from pathlib import Path
import sys,re,ast,math,json,shutil,subprocess
from collections import defaultdict
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import functions as parse
s=(R/'src/war3map.j').read_text();functions=parse(s);checks=[]
def check(v,n):
    assert v,n
    checks.append(n)
# Execute existing behavior suites against the combined source, never their old source.
sources={
 'hero-rework':Path('C:/Users/User/Documents/Codex/2026-10-29/in-x20/work/hero-rework/checks.py'),
 'mundo-kit':Path('C:/Users/User/Documents/Codex/2026-10-29/in-x20/work/mundo-kit/checks.py'),
 'tf':Path('C:/Users/User/Documents/Codex/2026-10-29/i/work/check_tf.py'),
 'veigar':W/'veigar-prototype/checks.py'}
for label,source in sources.items():
    d=R/'tests'/label;(d/'src').mkdir(parents=True,exist_ok=True)
    for n in ['war3map.j','war3map.w3a']:shutil.copy2(R/'src'/n,d/'src'/n)
    code=source.read_text()
    if label=='veigar':
        code=code.replace("R.parent/'799x-backport/check_runtime.py'",repr(str(W/'799x-backport/check_runtime.py')))
        code=code.replace("("+repr(str(W/'799x-backport/check_runtime.py'))+").read_text()","Path("+repr(str(W/'799x-backport/check_runtime.py'))+").read_text()")
        (d/'spells.j').write_text('\n\n'.join(v for n,v in functions.items() if n.startswith('VG_')))
    (d/'checks.py').write_text(code)
reports={}
for label in ['mundo-kit','tf','veigar']:
    d=R/'tests'/label
    run=subprocess.run([sys.executable,str(d/'checks.py')],capture_output=True,text=True)
    (d/'run.log').write_text(run.stdout+run.stderr)
    assert run.returncode==0,(label,run.stdout[-500:],run.stderr[-1500:])
    reports[label]=json.loads((d/('checks.json' if label=='veigar' else 'behavior-checks.json')).read_text())['passed']
print('Hero regression checks:',reports)
# Translate actual merged mass functions; integer JASS division must stay integral.
tree=ast.parse((W/'799x-backport/check_runtime.py').read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ('expression','translate'):exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
def setup():
    units={};events=[];group=[]
    env=dict(udg_mode_pub=True,udg_mode_inhouse=False,udg_mode_no_mass=False,F35_MassReleased=False,F35_PlayerStaged=defaultdict(int),F35_MassPool=defaultdict(lambda:None),F35_MassPoolCount=0,ffgs_center_x=0.,ffgs_center_y=-256.,udg_player_active=defaultdict(lambda:True),udg_base={i:-i for i in range(1,13)},udg_autosend=defaultdict(lambda:True),udg_player_start={i:(-3000.,-3000.) for i in range(1,13)},ffgs_new_unit=defaultdict(lambda:None),udg_spawn_unit={0:'hfoo',1:'hrif'},bj_UNIT_FACING=270.,ffgs_count_group=group,filterLivingPlayerUnitsOfTypeId=0)
    def prop(u,k,v):units[u][k]=v
    def create(p,k,x,y,f):
        u=len(units)+1;units[u]=dict(owner=p,kind=k,x=x,y=y,life=420.,hidden=False,paused=False,food=True,path=True,invul=False,speed=0,stats=0);return u
    def apply(u,idx,pn):units[u]['stats']+=1;events.append(('stats',u))
    def speed(u):
        if not units[u]['hidden']:units[u]['speed']+=1
    env.update(ConvertedPlayer=lambda p:p-1,ModuloInteger=lambda a,b:a%b,I2R=float,
        GetUnitX=lambda u:0.,GetUnitY=lambda u:0.,CreateUnit=create,
        ShowUnit=lambda u,v:prop(u,'hidden',not v),PauseUnit=lambda u,v:prop(u,'paused',v),SetUnitInvulnerable=lambda u,v:prop(u,'invul',v),SetUnitUseFood=lambda u,v:prop(u,'food',v),SetUnitPathing=lambda u,v:prop(u,'path',v),SetUnitX=lambda u,v:prop(u,'x',v),SetUnitY=lambda u,v:prop(u,'y',v),
        GetUnitTypeId=lambda u:units.get(u,{}).get('kind',0),GetWidgetLife=lambda u:units.get(u,{}).get('life',0),GetOwningPlayer=lambda u:units.get(u,{}).get('owner',0),GetPlayerId=lambda p:p,IsUnitAliveBJ=lambda u:u not in env.get('dead_bases',[]),
        FFGS_ComputeStats=lambda *a:None,FFGS_ApplyUnit=apply,FFR7_ApplyMassSpeed=speed,UnitRemoveAbility=lambda *a:None,IssuePointOrder=lambda u,*a:events.append(('attack',u)),RemoveUnit=lambda u:units[u].update(kind=0),Location=lambda x,y:(x,y),GetLocationX=lambda p:p[0],GetLocationY=lambda p:p[1],
        GroupEnumUnitsOfPlayer=lambda g,p,f:g.__setitem__(slice(None),[u for u in units if units[u]['owner']==p and units[u]['kind']=='hfoo' and units[u]['life']>.405 and (env.get('include_hidden',False) or not units[u]['hidden'])]),BlzGroupGetSize=len,GroupClear=lambda g:g.clear(),IsUnitInGroup=lambda u,g:u in g)
    for n in ['F35_MassEnabled','F35_StageFootman','F35_ReleaseMass','F35_MassPoint','FFGS_SpawnForPlayer','FFGS_CountLivingOfType']:
        code=translate(n).replace('/ 3','// 3').replace('/ 7','// 7')
        exec(code,env)
    return env,units,events
e,u,events=setup()
for p in range(1,13):e['FFGS_SpawnForPlayer'](0,p,63)
check(len(u)==756,'12 players retain exactly 63 units each, no Mini Foots 50% multiplier')
check(all(v['hidden'] and v['paused'] and v['invul'] and not v['food'] and not v['path'] for v in u.values()),'Pre-mass units hidden, paused, invulnerable, food-free, pathing-free')
positions=[(v['x'],v['y']) for v in u.values()]
check(len(set(positions))==len(positions),'All 756 staged positions are unique')
check(all(-1472<=x<=1504 and -1888<=y<=1344 for x,y in positions),'All formation positions stay inside center rectangle')
check(min(math.dist(a,b) for i,a in enumerate(positions) for b in positions[i+1:])>=45.,'Formation spacing at least 45 units across teammates and teams')
for p in range(1,13):
    for hidden in [False,True]:
        e['include_hidden']=hidden
        check(e['FFGS_CountLivingOfType']('hfoo',p-1)==63,f'P{p} hidden unit cap counted exactly once (native includes hidden={hidden})')
e['F35_ReleaseMass']()
check(all(not v['hidden'] and not v['paused'] and not v['invul'] and v['food'] and v['path'] for v in u.values()),'Release restores visibility, movement, vulnerability, food and pathing')
check(all(v['speed']==1 and v['stats']==2 for v in u.values()),'Release refreshes current upgrades and applies speed once')
check(len([x for x in events if x[0]=='attack'])==756,'Every autosend-enabled unit attacks at release')
check(e['F35_MassPoolCount']==0 and all(x is None for x in e['F35_MassPool'].values()),'Pool releases all references')
before=len(events);e['F35_ReleaseMass']();check(len(events)==before,'Repeated mass-start does not duplicate release')
e['FFGS_SpawnForPlayer'](0,1,2);check(not u[757]['hidden'] and not u[758]['hidden'],'Post-mass waves spawn normally')
for flags in [dict(udg_mode_pub=False),dict(udg_mode_inhouse=True),dict(udg_mode_no_mass=True)]:
    e,u,events=setup();e.update(flags);e['FFGS_SpawnForPlayer'](0,1,3)
    check(e['F35_MassPoolCount']==0 and all(not v['hidden'] for v in u.values()),'Normal spawn retained for '+str(flags))
e,u,events=setup();e['FFGS_SpawnForPlayer'](1,1,2);check(e['F35_MassPoolCount']==0,'Tech units never enter footman pool')
e,u,events=setup()
for p in range(1,5):e['FFGS_SpawnForPlayer'](0,p,1)
e['udg_player_active'][1]=False;e['dead_bases']=[-2];u[3]['life']=0.;e['udg_autosend'][4]=False
e['F35_ReleaseMass']();check(all(u[n]['kind']==0 for n in [1,2,3]),'Inactive owners, destroyed bases and dead units discarded')
check(u[4]['kind']=='hfoo' and not u[4]['hidden'] and not any(x[0]=='attack' for x in events),'Autosend-off respected at release')
check('set ffgs_premass_seconds=90.00' in s,'90-second countdown preserved')
check(functions['Trig_Mass_START_Actions'].index('call F35_ReleaseMass()')<functions['Trig_Mass_START_Actions'].index('// AUTO BEASTSCROLL'),'Release precedes automatic roar')
check('or IsUnitHidden(u) then' in functions['FFR7_ApplyMassSpeed'],'Hidden units cannot receive duplicate mass speed')
check('F35_MassEnabled() and IsUnitHidden' in functions['Trig_keep_footy_in_base_Conditions'],'Base confinement cannot move hidden staged units')
(R/'checks.json').write_text(json.dumps(dict(hero_checks=reports,mass_checks=len(checks),checks=checks,scope='Actual translated JASS with mocked natives; not a live engine test'),indent=2))
print(len(checks),'mass checks passed.')
