"""Mock the actual JASS frame renderer to verify card visibility and UI-only updates."""
import runpy,re,ast,copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
h=runpy.run_path(str(ROOT/'test_rules.py'))
ui=(ROOT/'ui.j').read_text();h['functions'].update({m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',ui)})
env=h['env'];textures={};visible={};labels={};enabled={}
env.update(BlzFrameSetTexture=lambda f,t,*_:textures.update({f:t}),BlzFrameSetVisible=lambda f,v:visible.update({f:v}),BlzFrameSetText=lambda f,t:labels.update({f:t}),BlzFrameSetEnable=lambda f,v:enabled.update({f:v}),GetLocalPlayer=lambda:0,Player=lambda p:p)
for name in ['PK_ChipArt','PK_Render']:
    tree=ast.fix_missing_locations(h['IntegerDiv']().visit(ast.parse(h['translate'](name))))
    exec(compile(tree,'UI '+name,'exec'),env)
for name in re.findall(r'framehandle array (\w+)',(ROOT/'poker-globals.j').read_text()):
    for i in range(216):env[name][i]=name+str(i)
checks=0
for p in [0,12]:
    h['reset'](p)
    b=p*9
    for street,count in [(0,0),(1,3),(2,4),(3,5)]:
        for reveal in [False,True]:
            env['PK_Street'][p]=street;env['PK_Reveal'][p]=reveal
            before={k:copy.deepcopy(env[k]) for k in ['PK_Stack','PK_Total','PK_Paid','PK_Cards','PK_Turn']}
            env['PK_Render'](p)
            for i in range(9):
                expected='card'+str(env['PK_Cards'][b+i])
                if 2<=i<4 and not reveal:expected='back'
                if i>=4 and i-4>=count:expected='empty'
                path=textures[env['PK_Face'][b+i]]
                assert path=='PokerUI\\'+expected+'.blp'
                assert (ROOT/'src'/path.replace('\\','/')).is_file()
                checks+=1
            assert all(env[k]==v for k,v in before.items()),'Renderer changed game state'
    if p!=0:assert env['PK_Dialog'][p] not in visible,'Foreign table made visible'
env['PK_Hidden'][0]=True;env['PK_Render'](0);assert visible[env['PK_Dialog'][0]] is False
env['PK_Hidden'][0]=False;env['PK_Render'](0);assert visible[env['PK_Dialog'][0]] is True
env['PK_ChipArt']('test',0);assert visible['test'] is False
for n,count in [(1,1),(50,2),(200,3),(500,4)]:
    env['PK_ChipArt']('test',n);assert textures['test']=='PokerUI\\chips'+str(count)+'.blp'
report=dict(card_visibility_checks=checks,hidden_opponent_and_future_cards=True,local_table_visibility=True,renderer_preserves_rules_state=True,zero_stack_and_chip_tiers=True,engine_tested=False)
(ROOT/'ui-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
