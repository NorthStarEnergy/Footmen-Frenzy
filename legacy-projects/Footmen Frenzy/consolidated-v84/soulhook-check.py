"""Execute selected packaged JASS bodies. Native mocks do not establish engine behavior."""
from pathlib import Path
from collections import defaultdict
import ast, math, re, json

R = Path(__file__).resolve().parent
source = (R/'src/war3map.j').read_text(encoding='utf-8-sig')
functions = {m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
for node in ast.parse((R.parent/'799x-backport/check_runtime.py').read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
names = ['FS_Alive','FS_Enemy','FS_Hit','FS_CanMove','DK_New','DK_Free','DK_Flash',
         'DK_PullStep','DK_AxeArea','DK_HookCast','DK_HookCatch','DK_HookChain','DK_HookStun','DK_Tick','DK_OnDeath']
code = '\n\n'.join(translate(n) for n in names)
# The source has comment-only branches; Python requires a statement in them.
code = re.sub(r'(?m)^(\s*)(if|elif) ([^\n]+):\n(?=\1(?:elif|else))',r'\1\2 \3:\n\1    pass\n',code)
compile(code,'translated JASS','exec')

def setup():
    e={}; units={100:dict(x=0.,y=0.,owner=0,alive=True),200:dict(x=300.,y=0.,owner=1,alive=True)}
    state=dict(target=(450.,0.),hits=[],stuns=[],groups={},fx={},lights={},next=1000,blocked=False)
    for typ,name in re.findall(r'^\s*(unit|player|group|effect|real|integer|boolean) array (DK_\w+)',source,re.M):
        e[name]=defaultdict((lambda:None) if typ in ['unit','player','group','effect'] else (lambda:0))
    e.update(DK_High=0,DK_Now=0.,DK_Hash={},FS_CodeDepth=0,FS_DUMMY='hgr1',bj_DEGTORAD=math.pi/180,
             bj_mapInitialPlayableArea=1,PATHING_TYPE_WALKABILITY=1,ATTACK_TYPE_NORMAL=0,DAMAGE_TYPE_MAGIC=0,
             UNIT_TYPE_DEAD='dead',UNIT_TYPE_STRUCTURE='structure',UNIT_TYPE_FLYING='flying',UNIT_TYPE_MAGIC_IMMUNE='immune')
    noop=lambda *a:None
    def alloc(store,value):
        state['next']+=1;store[state['next']]=value;return state['next']
    def destroy(store,h):
        assert h in store,('invalid/double free',h);del store[h]
    def enum(g,x,y,r,f):state['groups'][g][:]=[u for u,v in units.items() if math.hypot(v['x']-x,v['y']-y)<=r]
    def damage(c,v,amount,*args):
        state['hits'].append((c,v,amount))
        if state.get('on_damage'):state['on_damage'](c,v)
    def position(u,x,y):units[u].update(x=x+(20 if state['blocked'] else 0),y=y)
    e.update(RMinBJ=min,RMaxBJ=max,IMaxBJ=max,SquareRoot=math.sqrt,Pow=pow,Atan2=math.atan2,Cos=math.cos,Sin=math.sin,
        GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],GetOwningPlayer=lambda u:units.get(u,{}).get('owner'),
        GetUnitTypeId=lambda u:1 if u in units else 0,GetWidgetLife=lambda u:1000 if units.get(u,{}).get('alive') else 0,
        IsUnitType=lambda u,t:units.get(u,{}).get(t,False),IsUnitEnemy=lambda u,p:units[u]['owner']!=p,
        BlzIsUnitInvulnerable=lambda u:units[u].get('invulnerable',False),GetUnitAbilityLevel=lambda u,a:units[u].get(a,0),
        GetHandleId=lambda u:u or 0,GetUnitFacing=lambda u:0.,GetSpellTargetX=lambda:state['target'][0],GetSpellTargetY=lambda:state['target'][1],
        CreateGroup=lambda:alloc(state['groups'],[]),DestroyGroup=lambda g:destroy(state['groups'],g),
        GroupEnumUnitsInRange=enum,FirstOfGroup=lambda g:state['groups'][g][0] if state['groups'][g] else None,
        GroupRemoveUnit=lambda g,u:state['groups'][g].remove(u),GroupAddUnit=lambda g,u:state['groups'][g].append(u),
        IsUnitInGroup=lambda u,g:u in state['groups'][g],UnitDamageTarget=damage,
        AddSpecialEffect=lambda *a:alloc(state['fx'],a),DestroyEffect=lambda h:destroy(state['fx'],h),
        AddLightningEx=lambda *a:alloc(state['lights'],a),DestroyLightning=lambda h:destroy(state['lights'],h),
        MoveLightningEx=noop,SetLightningColor=noop,DK_GroundZ=lambda *a:0.,SetUnitAnimation=noop,
        SetUnitPosition=position,SetUnitX=lambda u,x:units[u].update(x=x),SetUnitY=lambda u,y:units[u].update(y=y),
        GetRectMinX=lambda r:-5000.,GetRectMaxX=lambda r:5000.,GetRectMinY=lambda r:-5000.,GetRectMaxY=lambda r:5000.,
        IsTerrainPathable=lambda *a:False,GetTerrainCliffLevel=lambda *a:0,
        CreateUnit=lambda p,k,x,y,f:alloc(units,dict(owner=p,x=x,y=y,alive=True,dummy=True)),
        UnitAddAbility=noop,SetUnitAbilityLevel=noop,IssueTargetOrder=lambda d,o,v:state['stuns'].append(v),UnitApplyTimedLife=noop,
        GetTriggerUnit=lambda:state['dead'],ResetUnitAnimation=noop,DR_Stop=noop)
    for n in ['Scale','Color','Height','X','Y','Yaw']:e['BlzSetSpecialEffect'+n]=noop
    e.update(DK_BloodHit=noop,DK_Strike=noop,DK_PullLimit=lambda rank:300.)
    for typ in ['Integer','Real','LightningHandle','TextTagHandle']:
        e['Load'+typ]=lambda h,p,k,typ=typ:h.get((p,k),None if typ.endswith('Handle') else 0)
        e['Save'+typ]=lambda h,p,k,v:h.__setitem__((p,k),v)
    e['RemoveSavedInteger']=e['RemoveSavedHandle']=lambda h,p,k:h.pop((p,k),None)
    e['FlushChildHashtable']=lambda h,p:[h.pop(key) for key in list(h) if key[0]==p]
    exec(code,e)
    return e,units,state

checks=[]
def check(name,condition):
    assert condition,name
    checks.append(name)
def tick(e,n=1):
    for _ in range(n):e['DK_Tick']()

for rank in range(1,7):
    e,u,s=setup();e['DK_HookCast'](100,rank);tick(e,64)
    check(f'rank {rank} hits once, pulls, releases all owned state',s['hits']==[(100,200,80+40*rank)] and u[200]['x']==150. and e['DK_High']==0 and not e['DK_Hash'] and not s['fx'] and not s['lights'] and not s['groups'])

e,u,s=setup();u[200]['y']=1000.;e['DK_HookCast'](100,1);tick(e,8)
check('turnaround reached',e['DK_Return'][1]);u[200].update(x=300.,y=0.);tick(e,8)
check('returning head does not catch newly arrived target',not s['hits'])
e,u,s=setup();u[200].update(x=84.375,y=149.);e['DK_HookCast'](100,1);tick(e,64)
check('swept corridor catches target between sampled positions',len(s['hits'])==1)
e,u,s=setup();u[200].update(x=84.375,y=151.);e['DK_HookCast'](100,1);tick(e,64)
check('swept corridor rejects target beyond 150',not s['hits'])

e,u,s=setup();e['DK_HookCast'](100,1);e['DK_X'][1]=300.;e['DK_HookCatch'](1,299.,0.)
first=e['DK_Hash'][200,-32];u[101]=dict(x=0.,y=0.,owner=0,alive=True)
e['DK_HookCast'](101,6);head=max(i for i in e['DK_Kind'] if e['DK_Kind'][i]==11)
e['DK_X'][head]=300.;e['DK_HookCatch'](head,299.,0.)
check('overlapping casts each deal their rank damage and apply stun',s['hits']==[(100,200,120.),(101,200,320.)] and s['stuns']==[200,200])
check('second hook replaces existing hook drag',e['DK_Source'][e['DK_Hash'][200,-32]]==101 and sum(e['DK_Kind'][i]==12 for i in e['DK_Kind'])==1)

e,u,s=setup();axe=e['DK_New'](1,100);e['DK_Return'][axe]=True;e['DK_X'][axe]=300.
pull=e['DK_New'](2,100);e['DK_Target'][pull]=200;e['DK_Parent'][pull]=axe;e['DK_Left'][pull]=300.;e['DK_Hash'][200,-3]=pull
e['DK_HookCast'](100,1);head=max(i for i in e['DK_Kind'] if e['DK_Kind'][i]==11);e['DK_X'][head]=300.;e['DK_HookCatch'](head,299.,0.)
check('hook replaces active axe drag',(200,-3) not in e['DK_Hash'] and e['DK_Kind'][e['DK_Hash'][200,-32]]==12)

e,u,s=setup();e['DK_HookCast'](100,1);e['DK_X'][1]=300.;e['DK_HookCatch'](1,299.,0.);hookpull=e['DK_Hash'][200,-32]
axe=e['DK_New'](1,100);e['DK_Return'][axe]=True;e['DK_X'][axe]=300.;e['DK_Y'][axe]=0.;e['DK_Stacks'][axe]=1
e['DK_Hit'][axe]=e['CreateGroup']();e['DK_Pulled'][axe]=e['CreateGroup']();e['DK_AxeArea'](axe,299.,0.)
check('returning axe replaces active hook drag',(200,-32) not in e['DK_Hash'] and e['DK_Kind'][e['DK_Hash'][200,-3]]==2)
tick(e);check('new pull alone moves victim once per tick',u[200]['x']==271.875)

e,u,s=setup();s['blocked']=True;e['DK_HookCast'](100,1);tick(e,64)
check('collision snap cancels drag and restores position',u[200]['x']==300. and e['DK_High']==0 and not e['DK_Hash'])
e,u,s=setup();e['DK_HookCast'](100,1);tick(e,3);u[100]['alive']=False;s['dead']=100;e['DK_OnDeath']();tick(e,64)
check('caster death releases claims and effects',e['DK_High']==0 and not s['fx'] and not s['lights'] and not s['groups'] and not e['DK_Hash'])
e,u,s=setup()
def reflected(c,v):
    u[c]['alive']=False;s['dead']=c;e['DK_OnDeath']()
s['on_damage']=reflected;e['DK_HookCast'](100,1);tick(e,64)
check('caster death during damage callback releases resources',e['DK_High']==0 and not s['fx'] and not s['lights'] and not s['groups'] and not e['DK_Hash'])
e,u,s=setup()
for _ in range(100):
    u[200]['x']=300.;e['DK_HookCast'](100,1);tick(e,64)
    assert e['DK_High']==0 and not s['fx'] and not s['lights'] and not s['groups'] and not e['DK_Hash']
check('100 sequential casts release all states and resources',len(s['hits'])==100)
(R/'checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'engine_tested':False},indent=2));print(f'{len(checks)} Soul Hook behavioral checks passed')

