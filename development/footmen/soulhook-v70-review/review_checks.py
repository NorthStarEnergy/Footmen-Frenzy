"""Execute selected packaged JASS bodies. Native mocks do not establish engine behavior."""
from pathlib import Path
from collections import defaultdict
import ast, math, re, json

R = Path(__file__).resolve().parent
source = (R/'actual/war3map.j').read_text(encoding='utf-8-sig')
functions = {m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
for node in ast.parse((R.parent/'799x-backport/check_runtime.py').read_text()).body:
    if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
names = ['FS_Alive','FS_Enemy','FS_Hit','FS_CanMove','DK_New','DK_Free','DK_Flash',
         'DK_PullStep','DK_HookCast','DK_HookCatch','DK_HookChain','DK_HookStun','DK_Tick','DK_OnDeath']
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
    e['DK_AxeArea']=noop
    for typ in ['Integer','Real','LightningHandle','TextTagHandle']:
        e['Load'+typ]=lambda h,p,k,typ=typ:h.get((p,k),None if typ.endswith('Handle') else 0)
        e['Save'+typ]=lambda h,p,k,v:h.__setitem__((p,k),v)
    e['RemoveSavedInteger']=e['RemoveSavedHandle']=lambda h,p,k:h.pop((p,k),None)
    e['FlushChildHashtable']=lambda h,p:[h.pop(key) for key in list(h) if key[0]==p]
    exec(code,e)
    return e,units,state

results=[]
def record(name,**details):results.append(dict(name=name,**details))
def tick(e,n=1):
    for _ in range(n):e['DK_Tick']()

# Normal rank damage, bounded drag, and owned handle cleanup.
for rank in range(1,7):
    e,u,s=setup();e['DK_HookCast'](100,rank);tick(e,64)
    assert s['hits']==[(100,200,80+40*rank)]
    assert u[200]['x']==150.
    assert not s['fx'] and not s['lights'] and not s['groups'] and not e['DK_Hash'] and e['DK_High']==0
record('All six ranks: one damage hit, 150-unit drag at initial distance 300, complete state/effect/group/tether cleanup',passed=True)

# Return path catch: introduce an enemy only after the head starts returning.
e,u,s=setup();u[200]['y']=1000.;e['DK_HookCast'](100,1);tick(e,8)
assert e['DK_Return'][1];u[200].update(x=300.,y=0.);tick(e)
assert len(s['hits'])==1
record('New target caught on return, despite outbound-only README description',reproduced=True)

# One drag claim wrongly gates all effects of a separate hook cast.
e,u,s=setup();e['DK_HookCast'](100,1);e['DK_X'][1]=300.;e['DK_HookCatch'](1)
u[101]=dict(x=0.,y=0.,owner=0,alive=True)
e['DK_HookCast'](101,6);head=max(i for i in e['DK_Kind'] if e['DK_Kind'][i]==11)
e['DK_X'][head]=300.;e['DK_HookCatch'](head)
assert s['hits']==[(100,200,120.)] and s['stuns']==[200]
record('Second caster rank-6 hook deals no damage and no stun to an already dragged target',reproduced=True,expected_second_damage=320,actual_second_damage=0)

# Reaping Axe and Soul Hook use distinct drag ownership keys.
e,u,s=setup();axe=e['DK_New'](1,100);e['DK_Return'][axe]=True;e['DK_X'][axe]=300.
pull=e['DK_New'](2,100);e['DK_Target'][pull]=200;e['DK_Parent'][pull]=axe;e['DK_Left'][pull]=300.
e['DK_Hash'][200,-3]=pull
e['DK_HookCast'](100,1);head=max(i for i in e['DK_Kind'] if e['DK_Kind'][i]==11)
e['DK_X'][head]=300.;e['DK_HookCatch'](head)
assert e['DK_Kind'][pull]==2 and e['DK_Hash'][200,-32]!=0
record('Reaping Axe pull and Soul Hook drag both own the same victim concurrently',reproduced=True)
tick(e)
assert u[200]['x']==231.875
record('Concurrent axe/hook pulls move victim 68.125 units in one 31.25ms tick, exceeding hook step 40',reproduced=True)

# Sampled circle misses a stationary target inside the nominal 150-wide corridor.
e,u,s=setup();u[200].update(x=84.375,y=149.);e['DK_HookCast'](100,1);tick(e,64)
assert not s['hits']
record('Stationary target at x=84.375, y=149 missed on both passes',reproduced=True,perpendicular_distance=149)

# Collision snap rollback and source death cleanup execute safely in mocks.
e,u,s=setup();s['blocked']=True;e['DK_HookCast'](100,1);tick(e,64)
assert u[200]['x']==300. and e['DK_High']==0 and not e['DK_Hash']
record('Collision snap over 8 units cancels drag and restores original position',passed=True)
e,u,s=setup();e['DK_HookCast'](100,1);tick(e,3);u[100]['alive']=False;s['dead']=100;e['DK_OnDeath']();tick(e,64)
assert e['DK_High']==0 and not s['fx'] and not s['lights'] and not s['groups'] and not e['DK_Hash']
record('Caster death during an active catch cleans drag/head/claim, flash expires',passed=True)

e,u,s=setup()
def reflected(c,v):
    u[c]['alive']=False;s['dead']=c;e['DK_OnDeath']()
s['on_damage']=reflected;e['DK_HookCast'](100,1);tick(e,64)
assert e['DK_High']==0 and not s['fx'] and not s['lights'] and not s['groups'] and not e['DK_Hash']
record('Synchronous reflected-damage caster death inside catch cleans owned resources',passed=True)
e,u,s=setup()
for n in range(100):
    u[200]['x']=300.;e['DK_HookCast'](100,1);tick(e,64)
    assert e['DK_High']==0 and not s['fx'] and not s['lights'] and not s['groups'] and not e['DK_Hash']
assert len(s['hits'])==100
record('100 sequential casts leave no active DK states, groups, effects, tethers or hash claims',passed=True)

(R/'review-checks.json').write_text(json.dumps(dict(engine_tested=False,results=results),indent=2))
print(json.dumps(results,indent=2))

