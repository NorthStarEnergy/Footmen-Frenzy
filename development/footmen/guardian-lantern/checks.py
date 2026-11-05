"""Execute the actual lantern collision and entry behavior with simulated units."""
from pathlib import Path
from collections import defaultdict
import ast,re,sys,math
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'mini-foots/tools'));import objdata
s=(R/'src/war3map.j').read_text();functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
ns=dict(re=re,functions=functions)
for node in ast.parse((W/'799x-backport/check_runtime.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'),ns)
for name in ['TFP_LinkDistanceSquared','TFP_LinkEnemy','TFP_LinkEffect','TFP_LinkGround','TFP_LinkRide']:
 exec(ns['translate'](name).replace('function ',''),ns)
units={1:dict(x=0.,y=0.,hp=1000.,maxhp=1000.,owner=0,type='H043'),2:dict(x=1000.,y=0.,hp=1.,maxhp=1.,owner=0,type='lantern',locust=True),3:dict(x=500.,y=0.,hp=100.,maxhp=1000.,owner=0,type='ally'),4:dict(x=1000.,y=50.,hp=500.,maxhp=500.,owner=1,type='hero',hero=True),5:dict(x=500.,y=120.,hp=100.,maxhp=1000.,owner=0,type='ally'),6:dict(x=1000.,y=25.,hp=500.,maxhp=500.,owner=1,type='immune',hero=True,immune=True),7:dict(x=500.,y=0.,hp=500.,maxhp=500.,owner=1,type='creep'),8:dict(x=500.,y=0.,hp=500.,maxhp=500.,owner=1,type='hero',hero=True)}
hits=[];casts=[];effects=[];nextid=[20];enum=[];linknext=[];areanext=[]
def create(owner,kind,x,y,face):nextid[0]+=1;units[nextid[0]]=dict(x=x,y=y,hp=1,maxhp=1,owner=owner,type='dummy',locust=True,abilities=[]);return nextid[0]
def group_enum(g,x,y,r,f):g[:]=[u for u,v in units.items() if v['hp']>0 and math.hypot(v['x']-x,v['y']-y)<=r]
def add(g,u):
 if u not in g:g.append(u)
def merge(src,dest):
 for u in src:add(dest,u)
ns.update(TFP_FFDP_Caster=defaultdict(int,{1:1,2:1}),TFP_FFDP_Lantern=defaultdict(int,{1:2,2:2}),TFP_FFDP_Owner=defaultdict(int,{1:0,2:0}),TFP_LinkInside=defaultdict(list),TFP_LanternInside=defaultdict(list),TFP_RideHit=defaultdict(list),TFP_LinkEnum=enum,TFP_LinkNext=linknext,TFP_LanternNext=areanext,TFP_FFDP_TICK=.03,
 GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],GetUnitTypeId=lambda u:units[u]['type'] if u in units else 0,GetWidgetLife=lambda u:units[u]['hp'],SetWidgetLife=lambda u,v:units[u].__setitem__('hp',v),GetUnitState=lambda u,k:units[u][k],UNIT_STATE_MAX_LIFE='maxhp',
 IsUnitEnemy=lambda u,p:units[u]['owner']!=p,IsUnitAlly=lambda u,p:units[u]['owner']==p,IsUnitType=lambda u,k:units[u].get(k,False),UNIT_TYPE_STRUCTURE='structure',UNIT_TYPE_MAGIC_IMMUNE='immune',UNIT_TYPE_HERO='hero',BlzIsUnitInvulnerable=lambda u:units[u].get('invu',False),GetUnitAbilityLevel=lambda u,a:1 if units[u].get('locust') else 0,
 RMinBJ=min,RMaxBJ=max,SquareRoot=math.sqrt,GroupClear=lambda g:g.clear(),GroupEnumUnitsInRange=group_enum,FirstOfGroup=lambda g:g[0] if g else None,GroupRemoveUnit=lambda g,u:g.remove(u),GroupAddUnit=add,GroupAddGroup=merge,IsUnitInGroup=lambda u,g:u in g,
 CreateUnit=create,UnitAddAbility=lambda u,a:units[u]['abilities'].append(a),SetUnitAbilityLevel=lambda u,a,l:units[u].__setitem__('rank',l),IssueTargetOrder=lambda d,o,u:casts.append((o,u,tuple(units[d]['abilities']),units[d].get('rank'))),UnitApplyTimedLife=lambda *a:None,
 AddSpecialEffectTarget=lambda *a:effects.append(a) or len(effects),DestroyEffect=lambda *a:None)
assert ns['TFP_LinkDistanceSquared'](500.,100.,0.,0.,1000.,0.)==10000.
assert ns['TFP_LinkDistanceSquared'](1100.,0.,0.,0.,1000.,0.)==10000.
assert ns['TFP_LinkDistanceSquared'](2.,3.,0.,0.,0.,0.)==13.
ns['TFP_LinkGround'](1)
assert casts.count(('thunderbolt',4,('AGtz',),1))==1 and not any(c[1]==6 for c in casts)
assert casts.count(('slow',3,('ALTc',),None))==1 and abs(units[3]['hp']-110.6)<1e-6
assert units[1]['hp']==1000. and units[5]['hp']==100. and len(effects)==1
ns['TFP_LinkGround'](1);assert len(casts)==2 and abs(units[3]['hp']-111.2)<1e-6
# Exiting and re-entering are new crossings; staying never restuns/reapplies slow each tick.
units[4]['y']=300.;units[3]['y']=150.;ns['TFP_LinkGround'](1)
units[4]['y']=50.;units[3]['y']=0.;ns['TFP_LinkGround'](1)
assert casts.count(('thunderbolt',4,('AGtz',),1))==2 and casts.count(('slow',3,('ALTc',),None))==2
assert abs(units[3]['hp']-121.8)<1e-6
# Separate lanterns maintain independent entry histories.
ns['TFP_LinkGround'](2);assert casts.count(('thunderbolt',4,('AGtz',),1))==3
# Swept segments cover the whole movement step, even if neither endpoint touches the hero.
casts.clear();units[8]['x']=500.;units[8]['y']=75.;ns['TFP_LinkRide'](1,400.,0.,600.,0.)
assert casts==[('thunderbolt',8,('AGtz',),1)]
ns['TFP_LinkRide'](1,400.,0.,600.,0.);assert len(casts)==1
ns['TFP_LinkRide'](2,400.,0.,600.,0.);assert len(casts)==2
assert all(c[1] not in [3,6,7] for c in casts)
# Both end-of-trip and intermediate movement segments are checked, only for Guardian.
tick=functions['TFP_FFDP_Tick'];assert tick.count("GetUnitTypeId(TFP_FFDP_Caster[i]) == 'H043'")==3 and tick.count('call TFP_LinkRide(')==2 and tick.count('call TFP_LinkGround(')==1
destroy=functions['TFP_FFDP_Destroy'];start=functions['TFP_FFDP_OnCast']
for name in ['TFP_LinkInside','TFP_LanternInside','TFP_RideHit']:
 assert 'set '+name+'[i] = CreateGroup()' in start
 assert 'call DestroyGroup('+name+'[i])' in destroy and 'set '+name+'[i] = '+name+'[last]' in destroy and 'set '+name+'[last] = null' in destroy
a={e['newId']:e for t in objdata.load(str(R/'src/war3map.w3a'))['tables'] for e in t}
slow=a['ALTc']['mods'];get=lambda k:next(m['value'] for m in slow if m['id']==k)
assert abs(get('Slo1')-.2)<1e-6 and get('adur')==get('ahdu')==1. and 'friend' in get('atar')
stun=a['AGtz']['mods'];assert all(next(m['value'] for m in stun if m['id']==k and m['level']==1)==.5 for k in ['adur','ahdu'])
print('Lantern area entry/re-entry, ally chain healing and slow, swept rider collisions, immunity, concurrent lanterns and cleanup passed.')
