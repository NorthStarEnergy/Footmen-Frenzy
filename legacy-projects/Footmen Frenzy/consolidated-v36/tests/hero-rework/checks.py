"""Execute changed JASS functions with mocked natives; no claim of engine playtesting."""
from pathlib import Path
from collections import defaultdict
import re,math,json
R=Path(__file__).resolve().parent
s=(R/'src/war3map.j').read_text()
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
# Reuse the project's JASS-to-Python translator, without running its old suite.
reference=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport\check_runtime.py').read_text()
exec(reference[reference.index('def expression('):reference.index('def setup():')])
old_expression=expression
def expression(line):return old_expression(line).replace('function ', '')
env={}
for name in ['MQ_Free','MQ_GroundTick','MQ_Land','MQ_Finish','MQ_Remove','MU_Launch','MU_OnCleaverHit','MU_Heal','MU_Pay','DR_Stop','DR_Start','DR_Damage','DK_New','DK_Free','DK_Tick','DK_AxeArea','DK_PullLimit','DK_PullStep']:
 code=translate(name)
 # Empty comment-only branch in pre-existing DK_Tick.
 code=re.sub(r'(?m)^(\s*)if DK_Kind \[ i \] != 1\s*:\n',lambda m:m[0]+m[1]+'    pass\n',code)
 exec(code,env)
results=[]
def check(ok,label):
 assert ok,label
 results.append(label)
def setup():
 global units,H,event,fx,timers,hits,controls,cooldowns,counter
 units={1:dict(x=0.,y=0.,hp=800.,maxhp=1000.,owner=0,alive=True,abilities=set()),2:dict(x=500.,y=0.,hp=1000.,maxhp=1000.,owner=1,alive=True,abilities=set()),3:dict(x=0.,y=0.,hp=800.,maxhp=1000.,owner=0,alive=True,abilities=set())}
 H={};event={};fx={};timers={};hits=[];controls=[];cooldowns=[];counter=[100]
 noop=lambda *a:None
 def create(store,**kw):counter[0]+=1;store[counter[0]]=kw;return counter[0]
 def enum(g,x,y,r,_):g[:]=[u for u in units if math.hypot(units[u]['x']-x,units[u]['y']-y)<=r]
 for name in re.findall(r'^\s*\w+\s+array\s+(DK_\w+)',s,re.M):env[name]=defaultdict(int)
 env.update(MQ_Hash=1,MU_Hash=2,DK_Hash=3,MU_Now=0.,DK_Now=0.,DK_High=0,UNIT_STATE_MAX_LIFE=1,bj_DEGTORAD=math.pi/180.,bj_mapInitialPlayableArea=0,
  MQ_FinishTrigger=90,MQ_RemoveTrigger=91,MU_CleaverHit=92,gg_trg_MissileCreate=93,
  GetHandleId=lambda u:u,GetExpiredTimer=lambda:event['timer'],GetTriggerUnit=lambda:event['unit'],GetEventDamage=lambda:event['damage'],BlzSetEventDamage=lambda d:event.update(damage=d),
  FS_Alive=lambda u:u in units and units[u]['alive'] and units[u]['hp']>.405,IsUnitIllusion=lambda u:False,GetUnitTypeId=lambda u:1 if u in units else 0,
  GetOwningPlayer=lambda u:units[u]['owner'],GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],GetUnitFacing=lambda u:0.,
  GetWidgetLife=lambda u:units[u]['hp'],GetUnitState=lambda u,k:units[u]['maxhp'],SetWidgetLife=lambda u,v:units[u].update(hp=v),
  UnitAddAbility=lambda u,a:units[u]['abilities'].add(a),UnitRemoveAbility=lambda u,a:units[u]['abilities'].discard(a),SetUnitAbilityLevel=noop,BlzUnitHideAbility=noop,
  SetUnitScale=lambda u,*v:units[u].update(scale=v[0]),SetUnitVertexColor=lambda u,*v:units[u].update(color=v),KillUnit=lambda u:units[u].update(alive=False),
  BlzEndUnitAbilityCooldown=lambda u,a:cooldowns.append((u,a)),DisplayTextToPlayer=noop,DK_Text=noop,
  CreateTimer=lambda:create(timers),PauseTimer=noop,DestroyTimer=lambda t:timers[t].update(destroyed=True),TimerStart=lambda t,d,r,c:timers[t].update(callback=c),
  AddSpecialEffect=lambda m,x,y:create(fx,x=x,y=y),AddSpecialEffectTarget=lambda *a:create(fx),DestroyEffect=lambda f:fx[f].update(destroyed=True) if f else None,
  BlzSetSpecialEffectScale=noop,BlzSetSpecialEffectZ=noop,BlzSetSpecialEffectTimeScale=noop,BlzSetSpecialEffectX=noop,BlzSetSpecialEffectY=noop,BlzSetSpecialEffectHeight=noop,BlzSetSpecialEffectYaw=noop,BlzSetSpecialEffectColor=noop,
  RMinBJ=min,RMaxBJ=max,IMaxBJ=max,Pow=pow,SquareRoot=math.sqrt,Atan2=math.atan2,Cos=math.cos,Sin=math.sin,DK_GroundZ=lambda x,y:0.,RAbsBJ=abs,
  Location=lambda x,y:(x,y),GetLocationX=lambda p:p[0],GetLocationY=lambda p:p[1],TriggerExecute=noop,
  FS_Hit=lambda u,v,d:hits.append((u,v,d)),MQ_Control=lambda u,v,a,o:controls.append((v,a,o)),
  CreateGroup=lambda:[],DestroyGroup=noop,GroupClear=lambda g:g.clear(),GroupEnumUnitsInRange=enum,FirstOfGroup=lambda g:g[0] if g else None,
  GroupRemoveUnit=lambda g,u:g.remove(u),GroupAddUnit=lambda g,u:g.append(u),IsUnitInGroup=lambda u,g:u in g,
  FS_Enemy=lambda u,p:u in units and units[u]['alive'] and units[u]['owner']!=p,DK_BloodHit=noop,DK_Strike=lambda u,v,d:hits.append((u,v,d)),
  GetRectMinX=lambda r:-5000.,GetRectMaxX=lambda r:5000.,GetRectMinY=lambda r:-5000.,GetRectMaxY=lambda r:5000.,
  FS_CanMove=lambda u,x,y:not event.get('blocked'),SetUnitPosition=lambda u,x,y:units[u].update(x=x,y=y),SetUnitX=lambda u,x:units[u].update(x=x),SetUnitY=lambda u,y:units[u].update(y=y))
 for typ in ['Integer','Real','Boolean','UnitHandle','TimerHandle','PlayerHandle','EffectHandle']:
  env['Save'+typ]=lambda h,i,k,v:H.update({(h,i,k):v})
  env['Load'+typ]=lambda h,i,k:H.get((h,i,k),0)
 for typ in ['Integer','Real','Handle']:env['RemoveSaved'+typ]=lambda h,i,k:H.pop((h,i,k),None)
 env['FlushChildHashtable']=lambda h,i:[H.pop(k) for k in list(H) if k[:2]==(h,i)]
def launch(u=1,rank=1,missing=.2):
 H[2,u,22]=missing;env['MU_Launch'](u,rank,1100.,0.);return env['udg_MissileData']
def land(i,x=500.,y=0.):
 env['MQ_Land'](i,x,y);env['udg_MissileData']=i;env['MQ_Remove']();event['timer']=i

setup();i=launch();check(env['udg_MissileSpeed']==1100. and env['udg_MissileCollision']==75.,'Troll flight properties retained')
env.update(udg_MissileHitUnit=2,udg_MissileTravelled=550.)
env['MU_OnCleaverHit']();check(abs(hits[-1][2]-144.)<1e-6,'Cast health and travelled distance both scale damage')
check(units[1]['hp']==850.,'Midrange hit refunds full health cost')
check(controls==[(2,'AMqr','ensnare'),(2,'AMus','slow')],'Movement root and slow applied, no stun order')
check(H[1,i,5]==500. and H[1,i,8],'Hit drops cleaver at target')
env['MQ_Remove']();event['timer']=i;units[1]['x']=500.;env['MQ_GroundTick']()
check(cooldowns==[(1,'AMu1')] and 'AMqh' in units[1]['abilities'] and H[2,1,21]==2.,'Pickup resets cooldown and grants timed haste/regen')
check(timers[i]['destroyed'] and not any(k[:2]==(1,i) for k in H),'Pickup releases timer and hashtable state')
setup();i=launch();env['udg_MissilePosition']=(1100.,0.);env['MQ_Finish']();env['MQ_Remove']();event['timer']=i
check(H[1,i,5]==1100.,'Miss lands at missile endpoint')
for _ in range(95):env['MQ_GroundTick']()
check(not timers[i].get('destroyed'),'Ground cleaver remains before 3 seconds')
env['MQ_GroundTick']();check(timers[i]['destroyed'] and not cooldowns,'Ground cleaver expires at 3 seconds without rewards')
setup();i=launch();land(i);j=launch();check(timers[i]['destroyed'] and H[2,1,20]==j,'Recast removes previous grounded cleaver')
setup();i=launch();j=launch();env['MQ_Land'](i,500.,0.);env['udg_MissileData']=i;env['MQ_Remove']();check(timers[i]['destroyed'] and H[2,1,20]==j,'Late old projectile cannot replace new cleaver')
setup();i=launch();land(i);units[1]['owner']=1;env['MQ_GroundTick']();check(timers[i]['destroyed'] and not cooldowns,'Ownership change removes pickup without reward')
setup();i=launch();land(i);units[1]['alive']=False;env['MQ_GroundTick']();check(timers[i]['destroyed'],'Death removes grounded cleaver')
setup();i=launch(1);j=launch(3);land(i);land(j,800.);check(H[2,1,20]==i and H[2,3,20]==j,'Same-player Mundos have independent projectiles')
for rank in range(1,7):
 vals=[]
 for distance,missing in [(0.,0.),(1100.,0.),(1100.,.9)]:
  setup();i=launch(rank=rank,missing=missing);env.update(udg_MissileHitUnit=2,udg_MissileTravelled=distance);env['MU_OnCleaverHit']();vals.append(hits[-1][2])
 check(vals[0]<vals[1]<vals[2],f'Rank {rank}: damage rises with distance and missing health')
setup();units[1]['hp']=50.;check(not env['MU_Pay'](1,50.,'AMu1') and units[1]['hp']==50.,'Insufficient health cannot kill caster')
setup();env['DR_Start'](1,2);i=H[3,1,-40];check({'ADri','ADrh','ADrc','ADrd'}<=units[1]['abilities'] and units[1]['scale']==1.4,'Ultimate adds immunity/speed/cleave/refusal and transformation')
event.update(unit=1,damage=100.);env['DR_Damage']();check(event['damage']==100. and env['DK_Stacks'][i]==0,'Nonlethal damage does not consume refusal')
event['damage']=900.;env['DR_Damage']();expiry=env['DK_End'][i];check(event['damage']==799. and expiry==10.,'Lethal damage leaves 1 HP and starts 10 seconds')
env['DK_Now']=3.;event['damage']=9999.;env['DR_Damage']();env['DR_Start'](1,3);check(env['DK_End'][i]==expiry,'Repeated lethal damage and recasting cannot extend refusal')
units[1]['hp']=1000.;env['DK_Now']=9.96875;env['DK_Tick']();check(not units[1]['alive'] and not units[1]['abilities'] and units[1]['scale']==1.,'Death occurs at 10 seconds even after healing; transformation cleaned')
setup();env['DR_Start'](1,1);env['DK_Now']=14.96875;env['DK_Tick']();check(units[1]['alive'] and not units[1]['abilities'],'Normal ultimate expiration does not kill')
setup();env['DR_Start'](1,3);units[1]['owner']=1;env['DK_Tick']();check(not units[1]['abilities'],'Ownership change cleans ultimate modifiers')
setup();i=env['DK_New'](1,1)
for key,val in [('X',450.),('Y',0.),('DX',1.),('DY',0.),('Left',50.),('Damage',110.),('Stacks',1),('Hit',[]),('Pulled',[])]:env['DK_'+key][i]=val
env['DK_FX'][i]=env['AddSpecialEffect']('axe',450.,0.)
env['DK_Tick']();check(len(hits)==1 and env['DK_Return'][i] and not env['DK_Hit'][i],'Outbound collision hits once and clears list on turn')
env['DK_Tick']();check(len(hits)==2,'Same enemy receives return damage')
env['DK_Tick']();check(len(hits)==2 and units[2]['x']<500.,'Return does not repeatedly damage and pulls toward caster')
event['blocked']=True;before=units[2]['x'];env['DK_Tick']();check(units[2]['x']==before,'Obstacles prevent pull displacement')
(R/'behavior-checks.json').write_text(json.dumps(dict(passed=len(results),checks=results,scope='Executed JASS with mocked engine natives; live Warcraft testing pending'),indent=2))
print(f'{len(results)} behavioral checks passed.')
