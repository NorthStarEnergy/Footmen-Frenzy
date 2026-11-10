"""Execute translated spell JASS against mocked natives; no engine playtest implied."""
from pathlib import Path
import re, math, json, ast
R=Path(__file__).resolve().parent
source=(R/'spells.j').read_text()
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
# Reuse only the established JASS translator, without running its prior tests.
tree=ast.parse((R.parent/'799x-backport/check_runtime.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ('expression','translate'):exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
checks=[]
def check(v,label):
 assert v,label
 checks.append(label)
def setup():
 units={1:dict(x=0.,y=0.,owner=0,life=1000.,kind='HVg1'),2:dict(x=0.,y=0.,owner=1,life=1000.,kind='hfoo')}
 state={'next':10,'timer':None,'spell':'AVge','damage':[],'stuns':[],'groups':{},'timers':{},'effects':{},'lightning':{}}
 def allocate(store,value):
  state['next']+=1;h=state['next'];store[h]=value;return h
 def group():return allocate(state['groups'],[])
 def kill(store,h):
  if h is not None:del store[h]
 env=dict(VG_Hash={},VG_PrevX={},VG_PrevY={},bj_PI=math.pi,bj_mapInitialPlayableArea=1,UNIT_TYPE_STRUCTURE='building',UNIT_TYPE_MAGIC_IMMUNE='immune',ATTACK_TYPE_NORMAL=1,DAMAGE_TYPE_MAGIC=2,WEAPON_TYPE_WHOKNOWS=0)
 noop=lambda *a:None
 env.update(RMaxBJ=max,RMinBJ=min,Cos=math.cos,Sin=math.sin,GetHandleId=lambda x:x,Location=lambda x,y:(x,y),GetLocationZ=lambda l:0.,RemoveLocation=noop,
 GetUnitTypeId=lambda u:units.get(u,{}).get('kind',0),GetWidgetLife=lambda u:units.get(u,{}).get('life',0.),IsUnitEnemy=lambda u,p:units[u]['owner']!=p,IsUnitType=lambda u,k:units[u].get(k,False),BlzIsUnitInvulnerable=lambda u:units[u].get('invulnerable',False),GetUnitAbilityLevel=lambda u,k:units[u].get(k,0),GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],GetOwningPlayer=lambda u:units[u]['owner'],
 GetTriggerUnit=lambda:1,GetSpellAbilityId=lambda:state['spell'],GetSpellTargetX=lambda:0.,GetSpellTargetY=lambda:0.,GetExpiredTimer=lambda:state['timer'],CreateTimer=lambda:allocate(state['timers'],{}),PauseTimer=noop,DestroyTimer=lambda h:kill(state['timers'],h),TimerStart=lambda *a:None,
 CreateGroup=group,DestroyGroup=lambda h:kill(state['groups'],h),FirstOfGroup=lambda g:next(iter(state['groups'][g]),None),GroupRemoveUnit=lambda g,u:state['groups'][g].remove(u),GroupAddUnit=lambda g,u:state['groups'][g].append(u),IsUnitInGroup=lambda u,g:u in state['groups'][g],
 GroupEnumUnitsInRect=lambda g,*a:state['groups'][g].__setitem__(slice(None),list(units)),GroupEnumUnitsInRange=lambda g,x,y,r,f:state['groups'][g].__setitem__(slice(None),[u for u,v in units.items() if math.hypot(v['x']-x,v['y']-y)<=r]),
 CreateUnit=lambda p,k,x,y,f:allocate(units,dict(owner=p,kind=k,x=x,y=y,life=1.,Aloc=1)),UnitAddAbility=noop,UnitApplyTimedLife=noop,IssueTargetOrder=lambda d,o,u:(state['stuns'].append(u) or True),UnitDamageTarget=lambda c,u,d,*a:state['damage'].append((u,d)),
 AddSpecialEffect=lambda *a:allocate(state['effects'],{}),DestroyEffect=lambda h:kill(state['effects'],h),BlzSetSpecialEffectScale=noop,BlzSetSpecialEffectZ=lambda h,z:state['effects'][h].update(z=z),
 AddLightningEx=lambda *a:allocate(state['lightning'],{}),SetLightningColor=noop,DestroyLightning=lambda h:kill(state['lightning'],h))
 for kind in ['UnitHandle','PlayerHandle','GroupHandle','EffectHandle','LightningHandle','Real','Integer']:
  env['Save'+kind]=lambda table,h,k,v:table.__setitem__((h,k),v)
  env['Load'+kind]=lambda table,h,k,kind=kind:table.get((h,k),0 if kind in ['Real','Integer'] else None)
 env['HaveSavedReal']=lambda table,h,k:(h,k) in table
 env['FlushChildHashtable']=lambda table,h:[table.pop(key) for key in list(table) if key[0]==h]
 for name in functions:
  if name not in ['VG_Init','VG_Summon']:
   exec(translate(name).replace('function VG_Tick','VG_Tick'),env)
 def cast(spell='AVge'):
  state['spell']=spell;env['VG_Cast']();state['timer']=max(state['timers']);return state['timer']
 def tick(n=1):
  for _ in range(n):env['VG_Tick']()
 return env,units,state,cast,tick

e,u,s,cast,tick=setup()
for args,want,label in [((0,0,100,100),False,'interior free'),((300,0,300,0),True,'spawn on rim'),((400,0,400,20),False,'outside free'),((250,0,350,0),True,'outward crossing'),((350,0,250,0),True,'inward crossing'),((-400,0,400,0),True,'fast crossing'),((-400,400,400,400),False,'distant segment'),((275,0,275,0),True,'inner boundary'),((325,0,325,0),True,'outer boundary')]:check(e['VG_Crosses'](*args)==want,label)
cast();tick();check(not s['stuns'],'interior not stunned');u[2]['x']=350.;tick();check(s['stuns']==[2],'crossing stunned');u[2]['x']=0.;tick();u[2]['x']=300.;tick();check(s['stuns']==[2],'once per cage');tick(92)
check(not s['timers'] and not s['groups'] and not s['lightning'],'cage expires and frees handles')
check(not e['VG_Hash'] and not e['VG_PrevX'] and not e['VG_PrevY'],'cage clears state')
e,u,s,cast,tick=setup();u[2]['x']=300.;cast();check(s['stuns']==[2],'edge stunned immediately');cast();check(s['stuns']==[2,2],'overlapping cage independent')
for prop in ['building','immune','invulnerable','Aloc']:
 e,u,s,cast,tick=setup();u[2].update(x=300.);u[2][prop]=True;cast();check(not s['stuns'],'cage excludes '+prop)
e,u,s,cast,tick=setup();u[2].update(owner=0,x=300.);cast();check(not s['stuns'],'allies safe')
e,u,s,cast,tick=setup();cast('AVgw');tick(39);check(not s['damage'],'no early damage');tick();check(s['damage']==[(2,300.)],'impact at 1.25 seconds');check(not s['effects'] and not s['timers'] and not s['groups'] and not s['lightning'],'strike cleans up')
e,u,s,cast,tick=setup();cast('AVgw');u[2]['x']=226.;tick(40);check(not s['damage'],'dodge outside radius')
e,u,s,cast,tick=setup();u[2]['x']=500.;cast('AVgw');u[2]['x']=225.;tick(40);check(s['damage']==[(2,300.)],'enter impact area and radius boundary')
e,u,s,cast,tick=setup();cast('AVgw');u[1]['life']=0.;tick(40);check(s['damage']==[(2,300.)],'launched strike survives caster death')
e,u,s,cast,tick=setup();cast();del u[1];tick();check(not s['timers'] and not s['groups'] and not s['lightning'],'removed caster cleans up')
report={'passed':len(checks),'checks':checks,'scope':'Translated actual JASS with mocked natives, not an in-game test'}
(R/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
