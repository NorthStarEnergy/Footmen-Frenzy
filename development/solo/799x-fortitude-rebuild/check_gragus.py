"""Mocked Fortitude lifecycle plus native buff/armor object and icon checks."""
from pathlib import Path
from collections import defaultdict
import ast,re,math,sys,json,io
from PIL import Image
ROOT=Path(__file__).resolve().parent
source=(ROOT/'src/war3map.j').read_text()
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
tree=ast.parse((ROOT/'check_runtime.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('expression','translate')],type_ignores=[]),'<translator>','exec'))
functions['FS_ClearFortitude']=functions['FS_ClearFortitude'].replace("'BGf1'",str(int.from_bytes(b'BGf1','big')))
for n in ['FS_ClearFortitude','FS_OnCast']:functions[n]=functions[n].replace("'GF01'",str(int.from_bytes(b'GF01','big')))
env={};exec('\n\n'.join(translate(n) for n in ['FS_ClearFortitude','FS_OnCast','FS_Free','FS_Tick']),env)
sys.path.insert(0,str(ROOT.parent/'mini-foots/tools'));import objdata
abilities={e['newId']:e for t in objdata.load(str(ROOT/'src/war3map.w3a'))['tables'] for e in t}
mods={(m['id'],m.get('level',0)):m['value'] for m in abilities['AGf1']['mods']}
checks=[]
def check(name,ok):
    assert ok,name
    checks.append(name)
def setup(rank):
    global levels,effects,unit
    levels={};effects={};unit={'alive':True,'hp':200.}
    for typ,name in re.findall(r'^\s*(unit|player|group|effect|real|integer|boolean) array (FS_\w+)',source,re.M):env[name]=defaultdict(lambda:0)
    env['FS_U'][1]=1;env['FS_Kind'][1]=10;env['FS_FX'][1]=None;env['FS_DrinkFX'][1]=None
    def effect(*a):key=len(effects)+100;effects[key]={'path':a[0],'destroyed':False};return key
    def destroy(f):assert not effects[f]['destroyed'];effects[f]['destroyed']=True
    noop=lambda *a:None
    env.update(FS_Hash=99,FS_High=1,FS_Now=0.,FS_PERIOD=.03125,FS_LEE=False,FS_Q='AGr1',FS_W='AGr2',FS_E='AGr3',FS_R='AGr4',FS_DETONATE='AGr8',FS_FLURRY='AGr7',
        GetTriggerUnit=lambda:1,GetSpellTargetUnit=lambda:None,GetSpellAbilityId=lambda:'AGr2',GetUnitAbilityLevel=lambda *a:rank,GetSpellTargetX=lambda:0.,GetSpellTargetY=lambda:0.,GetUnitX=lambda u:0.,GetUnitY=lambda u:0.,SquareRoot=math.sqrt,GetOwningPlayer=lambda u:0,
        CreateUnit=lambda *a:2,IssueTargetOrder=lambda d,o,u:levels.update(display=levels.get('GFbf')),UnitApplyTimedLife=lambda *a:None,
        FS_Alive=lambda u:unit['alive'],FS_Buff=lambda u:1,UnitAddAbility=lambda u,a:levels.update({a:1}),SetUnitAbilityLevel=lambda u,a,l:levels.update({a:l}),UnitRemoveAbility=lambda u,a:levels.pop(a,None),BlzUnitHideAbility=noop,
        AddSpecialEffectTarget=effect,DestroyEffect=destroy,SetUnitAnimationByIndex=noop,QueueUnitAnimation=noop,GetHandleId=lambda u:u,RemoveSavedInteger=noop,LoadInteger=lambda *a:0,
        SetWidgetLife=lambda u,h:unit.update(hp=h),GetWidgetLife=lambda u:unit['hp'],BlzGetUnitMaxHP=lambda u:1000.,RMinBJ=min)
for rank in range(1,7):
    setup(rank);env['FS_OnCast']()
    check('Native armor modifier and rank buff '+str(rank),levels.get(int.from_bytes(b'GF01','big')+rank-1)==1 and levels.get('display')==rank and next(m['value'] for m in abilities['GF0'+str(rank)]['mods'] if m['id']=='Idef')==3+2*rank)
    env['FS_Tick']();check('Fortitude heal starts '+str(rank),unit['hp']>200.)
    env['FS_OnCast']();check('Recast replaces buff without stacking '+str(rank),{k:v for k,v in levels.items() if isinstance(k,int)}=={int.from_bytes(b'GF01','big')+rank-1:1} and sum(not v['destroyed'] for v in effects.values())==1)
    for _ in range(161):env['FS_Tick']()
    check('Expiry removes modifier and effect '+str(rank),not any(isinstance(k,int) for k in levels) and env['FS_Armor'][1]==0 and all(v['destroyed'] for v in effects.values()))
setup(6);env['FS_OnCast']();unit['alive']=False;env['FS_Tick']()
check('Death removes native armor modifier',not any(isinstance(k,int) for k in levels) and all(v['destroyed'] for v in effects.values()))
check('Armor does not use aura', "call UnitAddAbility(u, 'AGf1')" not in source and all(abilities['GF0'+str(r)]['oldId']=='AId1' for r in range(1,7)))
check('Fortitude uses no-target order',all(m['value']=='roar' for m in abilities['AGr2']['mods'] if m['id']=='Ncl6'))
for name in ['Barrel','Fortitude','Slam','Cask']:
    for disabled in [False,True]:
        p=ROOT/'src/ReplaceableTextures'/('CommandButtonsDisabled' if disabled else 'CommandButtons')/(('DISBTN' if disabled else 'BTN')+'RxGragas'+name+'.blp')
        data=p.read_bytes();im=Image.open(io.BytesIO(data)).convert('RGBA')
        check('Compatible icon '+p.name,data[:4]==b'BLP1' and im.size==(64,64) and im.getchannel('A').getextrema()==(255,255))
(ROOT/'audit/gragus-checks.json').write_text(json.dumps({'passed':True,'checks':checks,'engine_test':False},indent=2))
print(str(len(checks))+' Gragus lifecycle/object/icon checks passed')
