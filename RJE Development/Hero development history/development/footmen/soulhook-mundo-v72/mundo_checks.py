from pathlib import Path
import ast,re,json,math
R=Path(__file__).resolve().parent; source=(R/'src/war3map.j').read_text(encoding='utf8');functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
tree=ast.parse((R.parent/'799x-backport/check_runtime.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
selected=['MC_Now','MC_Heat','MC_Integral','MC_Drain','MC_Model','MU_ZeroResources','MU_PoisonTick','MU_GasExpire','MU_GasSpawn','MU_BurnOff','MU_OnCast','MU_TickHero']
code='\n\n'.join(translate(n) for n in selected);code=re.sub(r"'([A-Za-z0-9]{4})'",lambda m:str(int.from_bytes(m[1].encode(),'big')),code);code=code.replace('amount / bit','amount // bit');code=re.sub(r'\bfunction (MU_\w+)',r'\1',code)
raw=lambda s:int.from_bytes(s.encode(),'big')
checks=[]
def check(name,v):assert v,name;checks.append(name)
units={1:dict(owner=0,life=1000.,kind=raw('HMu1'),intbase=0,itemint=0,maxmana=0,mana=0,abilities=set(),rank=1),2:dict(owner=1,life=1000.,kind=1,x=20.,y=0.,abilities=set()),3:dict(owner=0,life=1000.,kind=1,x=20.,y=0.,abilities=set()),4:dict(owner=1,life=1000.,kind=1,x=20.,y=0.,mechanical=True,abilities=set())}
timers={};effects={};groups={};ht={};state=dict(next=1000,timer=0,damage=[],spell=raw('AMu2'))
def alloc(store,v):state['next']+=1;store[state['next']]=v;return state['next']
def add(u,id):units[u]['abilities'].add(id)
def remove(u,id):units[u]['abilities'].discard(id)
def total(u):
 v=units[u]['intbase']+units[u]['itemint']
 for i in range(20):
  if (raw('AMi0')+i if i<10 else raw('AMj0')+i-10) in units[u]['abilities']:v-=2**i
 return max(0,v)
def damage(a,b,d,*args):state['damage'].append((a,b,d));units[b]['life']-=d
noop=lambda *a:None
env=dict(MU_Hash=ht,MU_Now=0.,ATTACK_TYPE_NORMAL=0,DAMAGE_TYPE_MAGIC=1,WEAPON_TYPE_WHOKNOWS=0,UNIT_TYPE_FLYING='flying',UNIT_TYPE_MECHANICAL='mechanical',UNIT_TYPE_STRUCTURE='structure',UNIT_TYPE_MAGIC_IMMUNE='immune',UNIT_STATE_MANA=0,UNIT_STATE_MAX_LIFE=1)
env.update(GetHandleId=lambda x:x or 0,GetUnitTypeId=lambda x:units.get(x,{}).get('kind',0),GetOwningPlayer=lambda x:units[x]['owner'],GetWidgetLife=lambda x:units[x]['life'],SetWidgetLife=lambda x,v:units[x].update(life=v),IsUnitEnemy=lambda x,p:units[x]['owner']!=p,IsUnitType=lambda x,t:units[x].get(t,False),IsUnitIllusion=lambda x:False,FS_Alive=lambda x:x in units and units[x]['life']>.405,GetUnitAbilityLevel=lambda u,a:units[u]['rank'] if a==raw('AMu2') else int(a in units[u]['abilities']),GetTriggerUnit=lambda:1,GetSpellAbilityId=lambda:state['spell'],GetUnitX=lambda u:units[u].get('x',0.),GetUnitY=lambda u:units[u].get('y',0.),GetUnitState=lambda u,s:1000.,GetPlayerId=lambda p:p,SetHeroInt=lambda u,v,b:units[u].update(intbase=v),GetHeroInt=lambda u,b:total(u),ModuloInteger=lambda a,b:a%b,UnitAddAbility=add,UnitRemoveAbility=remove,BlzUnitHideAbility=noop,BlzGetUnitMaxMana=lambda u:units[u]['maxmana'],BlzSetUnitMaxMana=lambda u,v:units[u].update(maxmana=v),SetUnitState=lambda u,s,v:units[u].update(mana=v),UnitDamageTarget=damage,CreateTimer=lambda:alloc(timers,{}),TimerStart=lambda t,d,r,fn:timers[t].update(callback=fn),GetExpiredTimer=lambda:state['timer'],DestroyTimer=lambda t:timers.pop(t),CreateGroup=lambda:alloc(groups,[]),DestroyGroup=lambda g:groups.pop(g),GroupEnumUnitsInRange=lambda g,x,y,r,f:groups[g].extend(u for u,v in units.items() if u!=1 and math.hypot(v.get('x',0)-x,v.get('y',0)-y)<=r),FirstOfGroup=lambda g:groups[g][0] if groups[g] else None,GroupRemoveUnit=lambda g,u:groups[g].remove(u),AddSpecialEffect=lambda model,x,y:alloc(effects,dict(model=model,x=x,y=y)),DestroyEffect=lambda h:effects.pop(h,None),BlzSetSpecialEffectScale=noop,BlzSetSpecialEffectColor=noop,SetUnitAbilityLevel=noop,MU_ClearFX=noop,MU_Register=noop,MU_Pay=lambda *a:False,MD_Tick=noop,MU_Heal=lambda u,h:None,HaveSavedReal=lambda h,k,n:(k,n) in h,HaveSavedInteger=lambda h,k,n:(k,n) in h,RMinBJ=min,RMaxBJ=max,RemoveSavedReal=lambda h,k,n:h.pop((k,n),None),RemoveSavedInteger=lambda h,k,n:h.pop((k,n),None),MU_Clear=noop,MU_ROff=noop,MU_EOff=noop,MU_RefreshE=noop)
for kind in ['UnitHandle','TimerHandle','EffectHandle','Real','Integer','Boolean']:
 env['Save'+kind]=lambda table,h,k,v:table.__setitem__((h,k),v)
 env['Load'+kind]=lambda table,h,k,kind=kind:table.get((h,k),False if kind=='Boolean' else 0 if kind in ['Real','Integer'] else None)
env['RemoveSavedHandle']=lambda h,k,n:h.pop((k,n),None);env['FlushChildHashtable']=lambda h,k:[h.pop(a) for a in list(h) if a[0]==k]
env.update(MU_Timer=999,TimerGetElapsed=lambda t:state.get('elapsed',0.),R2I=int,I2S=str)
exec(code,env)
import copy,sys
initial=copy.deepcopy(units)
def reset(rank=1,start=0.):
 units.clear();units.update(copy.deepcopy(initial));units[1]['rank']=rank
 timers.clear();effects.clear();groups.clear();ht.clear();state.update(next=1000,timer=0,damage=[],spell=raw('AMu2'),elapsed=0.)
 env['MU_Now']=start
def now(t):env['MU_Now']=t;state['elapsed']=0.
def cast():env['MU_OnCast']()
def fire(t):state['timer']=t;timers[t]['callback']()
def latest_cloud():return max(t for t in timers if ht.get((t,46)) is not None)
def tickhero(t):now(t);env['MU_TickHero'](1)
def approx(a,b):return abs(a-b)<1e-7

reset();cast();startcloud=latest_cloud()
check('Activation begins at old base damage and pale model',ht[startcloud,46]==35. and all(v['model'].endswith('Cloud0.mdx') for v in effects.values()))
check('Activation stores separate start/payment clock',ht[1,24]==ht[1,25]==0. and ht[1,1])
for elapsed,expected in [(0,0),(.25,.025),(3.3,.33),(5,.5),(6.7,.67),(9.999,.9999),(10,1),(10.001,1),(90,1)]:
 now(elapsed);check(f'Heat at {elapsed}s is capped correctly',approx(env['MC_Heat'](1),expected))
now(9.75);state['elapsed']=.25
check('Sub-tick clock reaches full at exactly 10 seconds',env['MC_Heat'](1)==1.)
for age in [0.,2.5,5.,7.5,10.,20.]:
 now(age);env['MU_GasSpawn'](1,1);t=latest_cloud()
 check(f'Cloud at {age}s snapshots matching damage/model',approx(ht[t,46],35*(1+min(age/10,1))) and effects[ht[t,30]]['model'].endswith('Cloud'+str(int(min(age/10,1)*20))+'.mdx'))
now(25);cast();check('Toggle off resets clock and heat',not ht[1,1] and (1,24) not in ht and (1,25) not in ht and env['MC_Heat'](1)==0.)
cast();check('Reactivation starts fresh despite old clouds',ht[1,24]==25 and ht[latest_cloud(),46]==35. and env['MC_Heat'](1)==0.)
check('Emitted clouds keep their snapshot after toggle',ht[startcloud,46]==35.)

for rank in range(1,7):
 reset(rank);cast();units[1]['life']=100000.
 for i in range(1,41):tickhero(i*.25)
 expected=(8+4*rank)*15.
 check(f'Rank {rank} first 10 seconds integrates 1x-to-2x drain',approx(100000.-units[1]['life'],expected))
 hp=units[1]['life']
 for i in range(41,49):tickhero(i*.25)
 check(f'Rank {rank} full-strength drain remains capped',approx(hp-units[1]['life'],(8+4*rank)*4.))
 check(f'Rank {rank} damage caps at double',approx(ht[latest_cloud(),46],(35+15*(rank-1))*2.))
reset(start=.125);cast();tickhero(.25)
check('First partial heartbeat only charges actual elapsed time',approx(1000.-units[1]['life'],12*(.125+.125**2*.05)))
reset();cast();now(9.9);ht[1,25]=9.9;now(10.15)
check('Drain correctly integrates across the 10-second cap',approx(env['MC_Drain'](1,1),12*(.1*1.995+.15*2)))
reset();cast();ht[1,20]=123;tickhero(.5)
check('Ramp does not overwrite cleaver handle',ht[1,20]==123)
units[1]['life']=1.;tickhero(10.)
check('Low health shuts down and resets without killing Mundo',units[1]['life']==1. and not ht[1,1] and (1,24) not in ht and raw('AMur') not in units[1]['abilities'])
cast();check('Low health cannot reactivate',not ht[1,1])
reset();cast();units[1]['rank']=0;tickhero(.25)
check('Losing cloud ability resets ramp',not ht[1,1] and (1,24) not in ht)
for reason in ['death','owner','removed']:
 reset();cast();env['MU_Clear']=lambda u:env['MU_BurnOff'](u)
 if reason=='death':units[1]['life']=0
 elif reason=='owner':ht[1,9]=0;units[1]['owner']=1
 else:units[1]['kind']=0
 tickhero(5)
 check(reason+' cleanup resets ramp',not ht.get((1,1)) and (1,24) not in ht)

reset();cast();weak=latest_cloud();fire(weak);poison=ht[1,-2]
check('First exposure immediately damages eligible enemy only',state['damage']==[(1,2,17.5)])
now(10);env['MU_GasSpawn'](1,1);strong=latest_cloud();fire(strong);fire(weak)
check('Overlapping weak/strong clouds share one poison and do not add hits',ht[1,-2]==poison and len(state['damage'])==1 and all(ht[poison,k]==70 for k in range(50,54)))
fire(poison);check('Strongest exposure determines periodic damage',state['damage'][-1]==(1,2,35.))
for _ in range(3):fire(weak);fire(poison)
fire(weak);fire(poison)
check('Weaker exposure cannot extend strong damage beyond four ticks',state['damage'][-1]==(1,2,17.5))
for _ in range(6):
 if poison in timers:fire(poison)
check('Poison expires two seconds after final exposure and releases timer',poison not in timers and (1,-2) not in ht)
for _ in range(8):
 for t in list(timers):fire(t)
for _ in range(8):
 for t in list(timers):fire(t)
check('Cloud effects, poison timers and groups eventually clean',not timers and not effects and not groups)
check('Allied/mechanical targets remain unharmed',units[3]['life']==units[4]['life']==1000.)

reset();cast();t=latest_cloud();units[1]['kind']=0;fire(t)
check('Removing source cleans cloud effects and timer',t not in timers and not effects)
reset();cast();t=latest_cloud();fire(t);p=ht[1,-2];units[2]['life']=0;fire(p)
check('Dead victim releases poison timer',p not in timers and (1,-2) not in ht)

sys.path.insert(0,str(R.parent/'mini-foots/tools'));import objdata
a=objdata.load(str(R/'src/war3map.w3a'));cloud=next(e for table in a['tables'] for e in table if e['newId']=='AMu2')
for rank in range(1,7):
 tip=next(m['value'] for m in cloud['mods'] if m['id']=='aub1' and m['level']==rank)
 check(f'Rank {rank} tooltip matches damage, drain, ramp and reset',all(s in tip for s in ['10 seconds',f'{35+15*(rank-1)} to {(35+15*(rank-1))*2}/sec',f'{8+4*rank} to {(8+4*rank)*2}/sec','resets the ramp']))
asset=json.loads((R/'asset-checks.json').read_text())
check('All 21 heat models roundtrip with alpha blending',asset['roundtrip_passed'] and len(asset['models'])==21 and asset['blend']=='alpha')
check('Maximum cloud is near black, green start and purple middle',max(max(c) for c in asset['models'][-1]['rgb'])<=24 and asset['models'][0]['rgb'][0][1]>200 and asset['models'][13]['rgb'][0][2]>asset['models'][13]['rgb'][0][1])
(R/'mundo-checks.json').write_text(json.dumps(dict(passed=len(checks),checks=checks,scope='Actual translated JASS with mocked natives and model/object checks; native timing and visual appearance require in-game validation.'),indent=2))
print(f'{len(checks)} cloud ramp behavior/model/object checks passed.')

