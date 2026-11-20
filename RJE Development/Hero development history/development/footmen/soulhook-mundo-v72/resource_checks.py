from pathlib import Path
import ast,re,json,math
R=Path(__file__).resolve().parent; source=(R/'src/war3map.j').read_text(encoding='utf8');functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
tree=ast.parse((R.parent/'799x-backport/check_runtime.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
selected=['MU_ZeroResources','MU_PoisonTick','MU_GasExpire','MU_GasSpawn','MU_BurnOff','MU_OnCast','MU_TickHero']
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
env.update(GetHandleId=lambda x:x or 0,GetUnitTypeId=lambda x:units.get(x,{}).get('kind',0),GetOwningPlayer=lambda x:units[x]['owner'],GetWidgetLife=lambda x:units[x]['life'],SetWidgetLife=lambda x,v:units[x].update(life=v),IsUnitEnemy=lambda x,p:units[x]['owner']!=p,IsUnitType=lambda x,t:units[x].get(t,False),IsUnitIllusion=lambda x:False,FS_Alive=lambda x:x in units and units[x]['life']>.405,GetUnitAbilityLevel=lambda u,a:units[u]['rank'] if a==raw('AMu2') else int(a in units[u]['abilities']),GetTriggerUnit=lambda:1,GetSpellAbilityId=lambda:state['spell'],GetUnitX=lambda u:units[u].get('x',0.),GetUnitY=lambda u:units[u].get('y',0.),GetUnitState=lambda u,s:1000.,GetPlayerId=lambda p:p,SetHeroInt=lambda u,v,b:units[u].update(intbase=v),GetHeroInt=lambda u,b:total(u),ModuloInteger=lambda a,b:a%b,UnitAddAbility=add,UnitRemoveAbility=remove,BlzUnitHideAbility=noop,BlzGetUnitMaxMana=lambda u:units[u]['maxmana'],BlzSetUnitMaxMana=lambda u,v:units[u].update(maxmana=v),SetUnitState=lambda u,s,v:units[u].update(mana=v),UnitDamageTarget=damage,CreateTimer=lambda:alloc(timers,{}),TimerStart=lambda t,d,r,fn:timers[t].update(callback=fn),GetExpiredTimer=lambda:state['timer'],DestroyTimer=lambda t:timers.pop(t),CreateGroup=lambda:alloc(groups,[]),DestroyGroup=lambda g:groups.pop(g),GroupEnumUnitsInRange=lambda g,x,y,r,f:groups[g].extend(u for u,v in units.items() if u!=1 and math.hypot(v.get('x',0)-x,v.get('y',0)-y)<=r),FirstOfGroup=lambda g:groups[g][0] if groups[g] else None,GroupRemoveUnit=lambda g,u:groups[g].remove(u),AddSpecialEffect=lambda *a:alloc(effects,{}),DestroyEffect=lambda h:effects.pop(h,None),BlzSetSpecialEffectScale=noop,BlzSetSpecialEffectColor=noop,SetUnitAbilityLevel=noop,MU_ClearFX=noop,MU_Register=noop,MU_Pay=lambda *a:False,MD_Tick=noop,MU_Heal=lambda u,h:None,HaveSavedReal=lambda h,k,n:(k,n) in h,HaveSavedInteger=lambda h,k,n:(k,n) in h,RMinBJ=min,RMaxBJ=max,RemoveSavedReal=lambda h,k,n:h.pop((k,n),None),RemoveSavedInteger=lambda h,k,n:h.pop((k,n),None),MU_Clear=noop,MU_ROff=noop,MU_EOff=noop,MU_RefreshE=noop)
for kind in ['UnitHandle','TimerHandle','EffectHandle','Real','Integer','Boolean']:
 env['Save'+kind]=lambda table,h,k,v:table.__setitem__((h,k),v)
 env['Load'+kind]=lambda table,h,k,kind=kind:table.get((h,k),False if kind=='Boolean' else 0 if kind in ['Real','Integer'] else None)
env['RemoveSavedHandle']=lambda h,k,n:h.pop((k,n),None);env['FlushChildHashtable']=lambda h,k:[h.pop(a) for a in list(h) if a[0]==k]
exec(code,env)
for n in [0,1,5,10,37,255,1024,65535]:
 units[1].update(intbase=7,itemint=n,maxmana=300,mana=200);env['MU_ZeroResources'](1)
 check(f'Item INT {n} canceled and mana zero',total(1)==0 and units[1]['intbase']==0 and units[1]['maxmana']==units[1]['mana']==0)
units[1]['itemint']=2;env['MU_ZeroResources'](1);check('Removing item bonus recalculates despite zero-clamped total',total(1)==0 and len(units[1]['abilities'])==1)
units[1]['itemint']=0;env['MU_ZeroResources'](1);check('Removing last INT item removes offsets',not units[1]['abilities'])
(R/'resource-checks.json').write_text(json.dumps(dict(passed=len(checks),checks=checks),indent=2));print(str(len(checks))+' resource checks passed')
