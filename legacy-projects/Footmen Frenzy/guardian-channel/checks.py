"""Run the changed JASS branches with simulated units, timers, groups and mana."""
from pathlib import Path
from collections import defaultdict
import sys,re,ast,math
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'mini-foots/tools'));import objdata
s=(R/'src/war3map.j').read_text();functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
ns=dict(re=re,functions=functions)
for node in ast.parse((W/'799x-backport/check_runtime.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'),ns)
for name in ['GD_Stop','GD_Tick','GD_Cast','GD_ClearActivationCooldown','GD_ReadyActive','GTW_Eligible','GTW_Remove','GTW_Explode','GTW_Tick','GTW_Cast','GDB_Hit']:
 exec(ns['translate'](name).replace('function ',''),ns)
units={1:dict(type='H043',hp=1000.,maxhp=1000.,mana=2000.,maxmana=2000.,owner=0,x=0.,y=0.,rank=1),2:dict(type='enemy',hp=1000.,maxhp=1000.,mana=500.,maxmana=500.,owner=1,x=100.,y=0.,rank=0),3:dict(type='ally',hp=500.,maxhp=1000.,mana=100.,maxmana=500.,owner=0,x=120.,y=0.,rank=0),4:dict(type='immune',hp=1000.,maxhp=1000.,mana=500.,maxmana=500.,owner=1,x=100.,y=0.,rank=0,immune=True)}
data={};effects={};nextid=[10];casts=[];damage=[];cooldowns=[];timer=[];events=[];target=[(1000.,0.)]
def fresh():nextid[0]+=1;return nextid[0]
def fx(*a):i=fresh();effects[i]=True;return i
def destroy(i):
 if i is not None:effects[i]=False
def load(h,k,c):return h.get((k,c),0)
def save(h,k,c,v):h[k,c]=v
def flush(h,k):
 for a in list(h):
  if a[0]==k:del h[a]
def enum(g,x,y,r,*a):g[:]=[u for u,v in units.items() if v['type']!='dummy' and v['hp']>0 and math.hypot(v['x']-x,v['y']-y)<=r]
def issue(dummy,order,target):casts.append((dummy,order,target,units[dummy].get('rank',0)))
def create(owner,kind,x,y,face):
 i=fresh();units[i]=dict(type='dummy',hp=1,owner=owner,x=x,y=y,rank=0,mana=0,maxmana=0,maxhp=1);return i
def deal(c,u,n,*args):damage.append((c,u,n));units[u]['hp']-=n
noop=lambda *a:None
ns.update(GD_Count=0,GD_Caster=defaultdict(lambda:0),GD_Dome=defaultdict(lambda:None),GD_Left=defaultdict(float),GD_Data={},GD_Enum=[],GD_Timer=1,GD_PERIOD=.05,GDV_Step=0,GDV_Units=[],GD_ABILITY='AZd1',GD_SLOW='AZd2',GD_Loc=0,
 GTW_Count=0,GTW_Caster=defaultdict(lambda:0),GTW_X=defaultdict(float),GTW_Y=defaultdict(float),GTW_DX=defaultdict(float),GTW_DY=defaultdict(float),GTW_Left=defaultdict(float),GTW_FX=defaultdict(lambda:None),GTW_Hit=defaultdict(list),GTW_Rank=defaultdict(int),GTW_Marks={},GTW_Enum=[],GTW_Timer=2,
 GetTriggerUnit=lambda:1,GetSpellAbilityId=lambda:'AZd1',GetUnitTypeId=lambda u:units[u]['type'] if u in units else 0,GetWidgetLife=lambda u:units[u]['hp'] if u in units else 0,GetUnitState=lambda u,k:units[u][k],SetUnitState=lambda u,k,v:units[u].__setitem__(k,v),UNIT_STATE_MANA='mana',UNIT_STATE_LIFE='hp',UNIT_STATE_MAX_LIFE='maxhp',UNIT_STATE_MAX_MANA='maxmana',
 GetOwningPlayer=lambda u:units[u]['owner'],GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],GetUnitAbilityLevel=lambda u,a:0 if a=='Aloc' else units[u]['rank'],GetHandleId=lambda u:id(u) if isinstance(u,list) else u,GetSpellTargetX=lambda:target[0][0],GetSpellTargetY=lambda:target[0][1],GetUnitFacing=lambda u:0.,
 LoadInteger=load,SaveInteger=save,RemoveSavedInteger=lambda h,k,c:h.pop((k,c),None),SaveEffectHandle=save,LoadEffectHandle=lambda h,k,c:h.get((k,c)),RemoveSavedHandle=lambda h,k,c:h.pop((k,c),None),FlushChildHashtable=flush,
 AddSpecialEffect=fx,AddSpecialEffectTarget=fx,DestroyEffect=destroy,BlzSetSpecialEffectAlpha=noop,BlzSetSpecialEffectScale=noop,BlzSetSpecialEffectColor=noop,BlzSetSpecialEffectColorByPlayer=noop,BlzSetSpecialEffectPosition=noop,BlzSetSpecialEffectX=noop,BlzSetSpecialEffectY=noop,BlzPlaySpecialEffect=noop,ANIM_TYPE_STAND=0,
 CreateGroup=lambda:[],DestroyGroup=noop,GroupEnumUnitsInRange=enum,FirstOfGroup=lambda g:g[0] if g else None,GroupRemoveUnit=lambda g,u:g.remove(u),GroupAddUnit=lambda g,u:g.append(u),IsUnitInGroup=lambda u,g:u in g,ForGroup=lambda g,f:None,
 TimerStart=lambda *a:timer.append(a),PauseTimer=noop,BlzEndUnitAbilityCooldown=lambda *a:events.append(('ready',a)),BlzStartUnitAbilityCooldown=lambda u,a,d:cooldowns.append((u,a,d)),UnitAddAbility=noop,UnitRemoveAbility=noop,
 IsUnitType=lambda u,k:units[u].get(k,False),UNIT_TYPE_STRUCTURE='structure',UNIT_TYPE_MAGIC_IMMUNE='immune',IsUnitEnemy=lambda u,p:units[u]['owner']!=p,IsUnitAlly=lambda u,p:units[u]['owner']==p,BlzIsUnitInvulnerable=lambda u:units[u].get('invu',False),
 UnitDamageTarget=deal,ATTACK_TYPE_NORMAL=0,DAMAGE_TYPE_MAGIC=0,WEAPON_TYPE_WHOKNOWS=0,CreateUnit=create,SetUnitAbilityLevel=lambda u,a,l:units[u].__setitem__('rank',l),IssueTargetOrder=issue,UnitApplyTimedLife=noop,
 GD_ReadyActive=lambda u:events.append(('ready',u)),GDV_Stop=noop,GDV_Dome=noop,GDV_Mark=noop,GDV_Pulse=noop,GDV_CleanupUnit=noop,MoveLocation=noop,GetLocationZ=lambda *a:0.,Player=lambda n:n,RMinBJ=min,RMaxBJ=max,I2R=float,SquareRoot=math.sqrt,Atan2=math.atan2,Cos=math.cos,Sin=math.sin,bj_DEGTORAD=math.pi/180)
# Immediate recast switches off, consumes no upfront mana, then starts five seconds cooldown.
ns['GD_Cast']();assert ns['GD_Count']==1 and units[1]['mana']==2000 and events[-1][0]=='ready'
ns['GD_Cast']();assert ns['GD_Count']==0 and cooldowns[-1]==(1,'AZd1',5.0)
units[1]['mana']=5.;ns['GD_Cast']();assert ns['GD_Count']==0
units[1]['mana']=2000.;ns['GD_Cast']();units[2]['x']=100.;units[3]['x']=120.
ns['GD_Tick']();assert ns['GD_Count']==1 and abs(units[1]['mana']-1999.)<.0001 and abs(units[3]['hp']-505.)<.0001
assert abs(units[2]['mana']-499.)<.0001 and damage[-1]==(1,2,1.0)
# Ramp values, excluding the caster from enumeration so restoration does not mask drain.
ns['GD_Left'][1]=20.;units[1]['mana']=1000.;units[3]['hp']=500.;units[2]['mana']=500.
ns['GD_Tick']();assert abs(units[1]['mana']-994.5)<.0001 and abs(units[3]['hp']-510.)<.0001 and abs(units[2]['mana']-498.)<.0001
units[1]['mana']=6.;ns['GD_Tick']();assert ns['GD_Count']==0 and cooldowns[-1]==(1,'AZd1',5.0)
units[1]['mana']=100.;ns['GD_Cast']();units[1]['hp']=0.;ns['GD_Tick']();assert ns['GD_Count']==0;units[1]['hp']=1000.
# Each orb owns a hit group, deals damage once and stuns every surviving marked target at its endpoint.
ns['GetSpellAbilityId']=lambda:'A0DL';units[1]['rank']=2;units[1]['mana']=1000.;units[2]['hp']=1000.;units[2]['x']=100.;units[4]['hp']=1000.;damage.clear();casts.clear()
ns['GTW_Cast']();assert ns['GTW_Count']==1 and ns['GTW_Rank'][1]==2
for _ in range(10):ns['GTW_Tick']()
assert [d for d in damage if d[1]==2]==[(1,2,40.)] and all(d[1]!=4 and d[1]!=3 for d in damage)
units[2]['x']=2000.
for _ in range(40):ns['GTW_Tick']()
assert ns['GTW_Count']==0 and len(casts)==1 and casts[0][1:] == ('thunderbolt',2,2) and not ns['GTW_Marks']
assert not any(effects.values())
# Deferred activation clears the engine cooldown only if this caster still has an active dome.
deferred={};deadlines={};expired=[0];ready=[]
ns.update(GD_Data=deferred,CreateTimer=fresh,GetExpiredTimer=lambda:expired[0],LoadUnitHandle=lambda h,k,c:h.get((k,c)),SaveUnitHandle=save,TimerStart=lambda t,d,r,cb:deadlines.__setitem__(t,cb),DestroyTimer=lambda t:deadlines.pop(t),BlzEndUnitAbilityCooldown=lambda u,a:ready.append((u,a)))
exec(ns['translate']('GD_ReadyActive').replace('function ',''),ns)
deferred[1,0]=1;ns['GD_ReadyActive'](1);expired[0]=next(iter(deadlines));deadlines[expired[0]]();assert ready==[(1,'AZd1')] and not deadlines
ns['GD_ReadyActive'](1);expired[0]=next(iter(deadlines));deferred.pop((1,0));deadlines[expired[0]]();assert len(ready)==1 and not deadlines
# Random strike damage, healing and mana transfer all scale with the same uptime factor.
beams={};ns.update(GD_Data={(1,0):1},GD_Left=defaultdict(float,{1:20.}),GDV_Data={},GDV_Step=20,GDB_Loc=0,SetWidgetLife=lambda u,v:units[u].__setitem__('hp',v),GetUnitFlyHeight=lambda u:0.,LoadLightningHandle=lambda h,k,c:h.get((k,c)),SaveLightningHandle=save,DestroyLightning=noop,AddLightningEx=lambda *a:fresh(),SaveUnitHandle=save,GDB_Visual=noop)
units[1]['rank']=3;units[3]['hp']=500.;units[3]['mana']=100.;units[2]['hp']=1000.;units[2]['mana']=500.;damage.clear()
ns['GDB_Hit'](1,3,True);assert units[3]['hp']==570. and units[3]['mana']==120.
ns['GDB_Hit'](1,2,False);assert units[2]['mana']==480. and damage[-1]==(1,2,70.)
abilities={e['newId']:e for t in objdata.load(str(R/'src/war3map.w3a'))['tables'] for e in t}
for rank in range(1,7):
 for field in ['adur','ahdu']:
  assert abs(next(m['value'] for m in abilities['AGtz']['mods'] if m['id']==field and m['level']==rank)-(.25+.25*rank))<1e-6
for rank in range(1,4):
 assert next(m['value'] for m in abilities['AZd1']['mods'] if m['id']=='acdn' and m['level']==rank)==5.
 assert next(m['value'] for m in abilities['AZd1']['mods'] if m['id']=='amcs' and m['level']==rank)==0
assert 'GDV_Project(' not in functions['GDV_Dome'] and 'FaerieDragonMissile' not in functions['GDV_Dome']
print('Guardian toggle, 5-mana cutoff, 5-second cooldown, uptime ramp, per-projectile mark/damage/stun, immunity and cleanup checks passed.')
