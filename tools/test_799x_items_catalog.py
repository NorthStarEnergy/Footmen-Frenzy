"""Execute the catalog's JASS UI control flow with mocked engine primitives.

These are behavior tests, not Warcraft rendering or multiplayer verification.
"""
import argparse
import ast
import collections
import json
from pathlib import Path
import re


def translate(script, name):
    block=re.search(r'^function '+name+r'\b.*?^endfunction',script,re.M|re.S)[0].splitlines()
    sig=re.match(r'function \w+ takes (.*?) returns',block[0])[1]
    args=[] if sig=='nothing' else [v.strip().split()[-1] for v in sig.split(',')]
    local=args+[re.match(r'\s*local \w+ (\w+)',line)[1] for line in block if re.match(r'\s*local \w+ (\w+)',line)]
    assigned=set(re.findall(r'^\s*set (\w+)\s*=', '\n'.join(block),re.M))-set(local)
    out=['def '+name+'('+','.join(args)+'):']
    if assigned:
        out.append('    global '+','.join(sorted(assigned)))
    level=1
    for line in block[1:-1]:
        line=line.strip()
        if not line or line.startswith('//'):
            continue
        line=re.sub(r'\b(true|false|null)\b',lambda m:{'true':'True','false':'False','null':'None'}[m[1]],line)
        line=re.sub(r'\bfunction (\w+)',r'\1',line)
        if line.startswith('local '):
            line=re.sub(r'^local \w+ ','',line)
            if '=' not in line:
                line+='=None'
        elif line.startswith('set '):line=line[4:]
        elif line.startswith('call '):line=line[5:]
        elif line=='loop':line='while True:'
        elif line.startswith('exitwhen '):line='if '+line[9:]+': break'
        elif line.startswith('if '):line=line[:-5]+':'
        elif line.startswith('elseif '):level-=1;line='elif '+line[7:-5]+':'
        elif line=='else':level-=1;line='else:'
        elif line in ('endif','endloop'):level-=1;continue
        out.append('    '*level+line)
        if line.endswith(':'):level+=1
    return '\n'.join(out)


class JassDivision(ast.NodeTransformer):
    def visit_BinOp(self,node):
        self.generic_visit(node)
        if isinstance(node.op,ast.Div):
            return ast.copy_location(ast.Call(ast.Name('jdiv',ast.Load()),[node.left,node.right],[]),node)
        return node


def environment(script):
    env={}
    declarations=re.search(r'^globals\s*$(.*?)^endglobals',script,re.M|re.S)[1]
    for typ,array,name in re.findall(r'^\s*(?:constant )?(\w+)\s+(?:(array)\s+)?(\w+)\s*(?:=|$)',declarations,re.M):
        default=False if typ=='boolean' else '' if typ=='string' else 0 if typ in ('integer','real') else None
        env[name]=collections.defaultdict(lambda d=default:d) if array else default
    frames={}
    handles=[]
    samples=[]
    def create(*args):
        result=len(handles)+1
        handles.append(result)
        frames[result]=dict(visible=True,enabled=True,text='')
        return result
    def setfield(field):
        return lambda f,value:frames[f].update({field:value})
    def save(table,parent,key,value):
        table[parent,key]=value
    def load(default):
        return lambda table,parent,key:table.get((parent,key),default)
    def sample(uid,*args):
        value={'id':uid,'removed':False}
        samples.append(value)
        return value
    env.update(jdiv=lambda a,b:a//b if isinstance(a,int) and isinstance(b,int) else a/b,
               IMaxBJ=max,IMinBJ=min,I2S=str,I2R=float,R2I=int,R2SW=lambda v,w,p:f'{v:.{p}f}',
               StringLength=lambda s:len(s or ''),SubString=lambda s,a,b:s[a:b],StringCase=lambda s,up:s.upper() if up else s.lower(),
               ModuloInteger=lambda a,b:a%b,GetPlayerId=lambda p:p,GetLocalPlayer=lambda:env['local_player'],
               GetTriggerPlayer=lambda:env['trigger_player'],BlzGetTriggerFrame=lambda:env['clicked'],
               BlzCreateFrame=create,BlzCreateFrameByType=create,CreateTrigger=create,CreateTimer=create,
               BlzFrameSetText=setfield('text'),BlzFrameSetVisible=setfield('visible'),BlzFrameSetEnable=setfield('enabled'),
               BlzFrameGetText=lambda f:frames[f]['text'],BlzFrameSetTexture=lambda f,texture,*args:frames[f].update(texture=texture),
               SaveInteger=save,SaveStr=save,SaveBoolean=save,LoadInteger=load(0),LoadStr=load(''),LoadBoolean=load(False),
               ExecuteFunc=lambda name:env[name](),IC_Data={},local_player=0,trigger_player=0,clicked=None,
               SpellKeysRefresh=lambda:None,BlzGetAbilityId=lambda a:a['id'],GetObjectName=lambda id:id,
               ConvertAbilityIntegerLevelField=lambda field:field,ConvertAbilityRealLevelField=lambda field:field,
               BlzGetAbilityIntegerLevelField=lambda a,field,level:int(a.get(field,0)),
               BlzGetAbilityRealLevelField=lambda a,field,level:float(a.get(field,0)),BlzGetAbilityExtendedTooltip=lambda id,level:'Ability '+id,
               CreateItem=sample,RemoveItem=lambda sample:sample.update(removed=True),
               GetItemName=lambda sample:'Native '+sample['id'],BlzGetItemIconPath=lambda sample:'native/'+sample['id'],
               BlzGetItemExtendedTooltip=lambda sample:'Current tooltip '+sample['id'],BlzGetItemDescription=lambda sample:'Description',
               BlzGetItemAbilityByIndex=lambda sample,i:None)
    names=re.findall(r'^function (IC_\w+|FFUI_Click) takes',script,re.M)
    code='\n\n'.join(translate(script,name) for name in names)
    tree=JassDivision().visit(ast.parse(code))
    ast.fix_missing_locations(tree)
    for name in set(re.findall(r'\b([A-Za-z_]\w*)\(',code)):
        if name not in env and name not in names:
            env[name]=lambda *args:None
    for name in set(re.findall(r'\b(?:FRAMEPOINT|FRAMEEVENT|TEXT_JUSTIFY)_[A-Z_]+\b',code)):
        env[name]=name
    exec(compile(tree,'catalog-jass-simulation','exec'),env)
    for name in ('FFUI_Root','FFUI_Items','FFUI_Toggle','FFUI_ItemsButton','DPS_Panel','spellKeysPanel'):
        env[name]=create()
    env['IC_LoadIndex']=1
    env['IC_TextPages']=1
    env['spellKeysEditing']=-1
    env['IC_Init']()
    return env,frames,handles,samples


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('workspace',type=Path)
    args=parser.parse_args()
    project=args.workspace/'projects/799x'
    script=(project/'src/war3map.j').read_text(encoding='utf-8')
    data=json.loads((project/'catalog-data.json').read_text())
    e,frames,handles,samples=environment(script)
    ids={row['id']:i for i,row in enumerate(data['items'],1)}
    def click(frame,player=0):
        e['trigger_player']=player;e['clicked']=frame
        e['IC_Click']()
    e['IC_Ready']=True
    assert e['IC_Count']==225 and e['IC_Sections']==23
    # Every catalog item is reachable through normal page browsing or a recipe link.
    visited=set()
    for page in range((e['IC_Sections']+1)//2):
        e['IC_Page']=page;e['IC_Render']()
        visited.update(v for v in e['IC_TileItem'].values() if v)
    assert visited==set(range(1,e['IC_Count']+1)),set(range(1,e['IC_Count']+1))-visited
    assert not frames[e['IC_Next']]['enabled']
    before=len(handles)
    frames[e['IC_Search']]['text']='soldier'
    click(e['IC_SearchButton'])
    assert e['IC_TileItem'][0]==ids['hval']
    click(e['IC_Tile'][0])
    assert e['IC_Selected']==ids['hval'] and frames[e['IC_Detail']]['visible']
    selected=e['IC_Selected'];click(e['IC_Back'],player=1)
    assert e['IC_Selected']==selected,'Remote click changed local UI'
    click(e['IC_Back'])
    assert e['IC_Selected']==0 and e['IC_Query']=='soldier'
    click(e['IC_Back'])
    assert e['IC_Query']=='' and frames[e['IC_Search']]['text']==''
    frames[e['IC_Search']]['text']='no such item zz'
    click(e['IC_Search'])
    assert not any(e['IC_TileItem'].values())
    assert not frames[e['IC_Next']]['enabled']
    click(e['IC_Back'])
    # Recipe links keep back navigation and display all ingredients plus the result.
    e['IC_Select'](ids['I00K']);e['IC_Render']();click(e['IC_TabButton'][2])
    assert set(v for v in e['IC_LinkItem'].values() if v)=={ids[i] for i in ['I00K','I003','ratf','I03C','I00W']}
    result_slot=next(i for i,v in e['IC_LinkItem'].items() if v==ids['I00W'])
    click(e['IC_Link'][result_slot]);assert e['IC_Selected']==ids['I00W']
    click(e['IC_Back']);assert e['IC_Selected']==ids['I00K']
    # Long text is split losslessly at word/line boundaries and pages are bounded.
    text=' '.join('word'+str(i) for i in range(650))
    e['IC_TextPage']=0;e['IC_Paginate'](text);pages=e['IC_TextPages'];chunks=[]
    for page in range(pages):
        e['IC_TextPage']=page;chunks.append(e['IC_Paginate'](text))
    assert ' '.join(' '.join(chunks).split())==text
    assert all(len(c.strip().splitlines())<=12 for c in chunks)
    # Global hide keeps the toggle accessible and restores the selected page state.
    e['clicked']=e['FFUI_Toggle'];e['FFUI_ItemsOpen']=True;e['FFUI_Click']()
    assert e['FFUI_Hidden'] and not frames[e['FFUI_Root']]['visible']
    assert frames[e['FFUI_Toggle']]['visible'] and '00ff00' in frames[e['FFUI_Toggle']]['text']
    e['FFUI_Click']()
    assert not e['FFUI_Hidden'] and frames[e['FFUI_Root']]['visible']
    assert e['IC_Selected']==ids['I00K'] and 'ff0000' in frames[e['FFUI_Toggle']]['text']
    assert len(handles)==before,'Local interactions allocated engine handles'
    # Native stat reads format fractions as percentages without changing flat armor.
    stats=e['IC_ReadAbility']({'id':'AFv1','Uav1':0.5,'acdn':30})
    assert '50%' in stats and '30' in stats
    # Hydration is synchronized, bounded to two samples/tick, and removes every sample.
    e['FFUI_ItemsOpen']=False;e['IC_Ready']=False;e['IC_LoadIndex']=1
    while not e['IC_Ready']:
        previous=len(samples);e['IC_Hydrate']();assert len(samples)-previous<=2
    assert len(samples)==e['IC_Count'] and all(s['removed'] for s in samples)
    assert e['IC_LoadTimer'] is None
    assert e['IC_Icon'][ids['hval']]=='native/hval'
    assert e['IC_Description'][ids['hval']]=='Current tooltip hval'
    # Keep resolved build-time text when the native tooltip still contains editor tokens.
    e['IC_LoadIndex']=ids['rwiz'];e['IC_Ready']=False
    e['BlzGetItemExtendedTooltip']=lambda sample:'Mana regen <AIrn,DataA1,%>%'
    expected=e['IC_Description'][ids['rwiz']]
    e['IC_Hydrate']()
    assert e['IC_Description'][ids['rwiz']]==expected
    assert all('<' not in row['description'] for row in data['items'])
    assert 'not FFUI_ItemsOpen or FFUI_Hidden' in re.search(r'^function SpellKeysInput\b.*?^endfunction',script,re.M|re.S)[0]
    report=dict(catalog_items_reachable=len(visited),search_and_empty_results=True,detail_and_recipe_navigation=True,
                local_player_isolation=True,clicks_allocate_no_handles=True,hide_show_preserves_page=True,
                long_text_paginated_without_loss=True,native_stats_format=True,hydration_samples_removed=len(samples),
                live_warcraft_test=False)
    (project/'catalog-behavior-tests.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
