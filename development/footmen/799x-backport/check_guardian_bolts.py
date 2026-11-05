"""Execute new random-bolt JASS with mocked engine state, plus native object checks."""
from pathlib import Path
import re,ast,sys,math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'mini-foots/tools'));import objdata
s=(ROOT/'src/war3map.j').read_text();functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
ns=dict(re=re,functions=functions)
for node in ast.parse((ROOT/'check_runtime.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'harness','exec'),ns)
units={1:dict(hp=100,mana=40,maxhp=200,maxmana=100,owner=0),2:dict(hp=100,mana=5,maxhp=200,maxmana=100,owner=1),3:dict(hp=100,mana=0,maxhp=200,maxmana=0,owner=0,structure=True),4:dict(hp=100,mana=100,maxhp=200,maxmana=100,owner=1,immune=True),5:dict(hp=0,mana=0,maxhp=100,maxmana=100,owner=1),6:dict(hp=100,mana=100,maxhp=200,maxmana=100,owner=1,invu=True)}
data={};bolts={};ids=[100];orders=[];added={};hits=[];rank=[1];group=[];chosen=[]
def newbeam(*args):ids[0]+=1;bolts[ids[0]]=args;return ids[0]
def save(h,k,c,v):h[k,c]=v
ns.update(GDV_Data=data,GDV_Step=15,GD_Loc=0,GDB_Loc=1,GDB_Enum=group,GetHandleId=lambda u:u,GetUnitAbilityLevel=lambda u,a:rank[0] if a=='AZd1' else 0,I2R=float,GetUnitX=lambda u:float(u*10),GetUnitY=lambda u:float(u*20),GetLocationZ=lambda p:0.,GetUnitFlyHeight=lambda u:0.,MoveLocation=lambda *a:None,GetOwningPlayer=lambda u:units[u]['owner'],CreateUnit=lambda *a:99,UnitAddAbility=lambda u,a:added.__setitem__(u,a),IssueTargetOrder=lambda d,o,t:orders.append((o,t,added[d])),UnitApplyTimedLife=lambda *a:None,GetWidgetLife=lambda u:units[u]['hp'],SetWidgetLife=lambda u,v:units[u].__setitem__('hp',v),GetUnitState=lambda u,k:units[u][k],SetUnitState=lambda u,k,v:units[u].__setitem__(k,v),RMinBJ=min,RMaxBJ=max,UNIT_STATE_MAX_LIFE='maxhp',UNIT_STATE_MAX_MANA='maxmana',UNIT_STATE_MANA='mana',ATTACK_TYPE_NORMAL=0,DAMAGE_TYPE_MAGIC=0,WEAPON_TYPE_WHOKNOWS=0,UnitDamageTarget=lambda c,u,d,*a:hits.append((c,u,d)),LoadLightningHandle=lambda h,k,c:h.get((k,c)),SaveLightningHandle=save,SaveUnitHandle=save,SaveInteger=save,LoadUnitHandle=lambda h,k,c:h.get((k,c)),LoadInteger=lambda h,k,c:h.get((k,c),0),DestroyLightning=lambda b:bolts.pop(b,None),RemoveSavedHandle=lambda h,k,c:h.pop((k,c),None),RemoveSavedInteger=lambda h,k,c:h.pop((k,c),None),AddLightningEx=newbeam,MoveLightningEx=lambda *a:None,SetLightningColor=lambda *a:None,GetUnitTypeId=lambda u:1 if u in units else 0,GroupEnumUnitsInRange=lambda g,x,y,r,f:g.extend(units),FirstOfGroup=lambda g:g[0] if g else None,GroupRemoveUnit=lambda g,u:g.remove(u),IsUnitType=lambda u,t:units[u].get(t,False),UNIT_TYPE_STRUCTURE='structure',UNIT_TYPE_MAGIC_IMMUNE='immune',BlzIsUnitInvulnerable=lambda u:units[u].get('invu',False),IsUnitAlly=lambda u,p:units[u]['owner']==p,IsUnitEnemy=lambda u,p:units[u]['owner']!=p,GetRandomInt=lambda lo,hi:1)
for n in ['GDB_Clear','GDB_Visual','GDB_Hit','GDB_Strike']:exec(ns['translate'](n).replace('function ',''),ns)
for r in range(1,4):
 rank[0]=r;units[1].update(hp=100,mana=40);units[2].update(mana=5);hits.clear();orders.clear()
 ns['GDB_Strike'](1,0,0)
 assert units[1]['hp']==120+5*r and units[1]['mana']==50
 assert units[2]['mana']==0 and hits==[(1,2,20+5*r)]
 assert orders==[('bloodlust',1,'AGbs'),('slow',2,'AGbn')]
 assert len(bolts)==2
 ns['GDV_Step']+=7;ns['GDB_Visual'](1);assert not bolts and not data
units[1].update(hp=199,mana=99);ns['GDB_Hit'](1,1,True);assert units[1]['hp']==200 and units[1]['mana']==100
ns['GDB_Clear'](1);assert not data and not bolts
ns['GDB_Hit'](1,None,True);assert not data
# No eligible targets: no mutation, casts, or bolts.
for u in units.values():u['invu']=True
hits.clear();orders.clear();ns['GDB_Strike'](1,0,0);assert not hits and not orders and not data
objects=lambda ext:{e['newId']:e for t in objdata.load(str(ROOT/'src'/('war3map.'+ext)))['tables'] for e in t}
a=objects('w3a');b=objects('w3h')
for uid,rng in [('A0DL',1200.),('AFg1',900.),('ATfd',1000.)]:
 for l in range(1,7):
  m=next(m for m in a[uid]['mods'] if m['id']=='aran' and m['level']==l)
  assert m['type']==2 and m['value']==rng
for uid,field,value in [('AGbs','Blo2',.1),('AGbn','Slo1',.15)]:
 e=a[uid];assert abs(next(m['value'] for m in e['mods'] if m['id']==field)-value)<1e-6
 assert next(m['value'] for m in e['mods'] if m['id']=='adur')==1.5
 assert next(m['value'] for m in e['mods'] if m['id']=='abuf') in b
from PIL import Image
for uid in ['A0DL','AFg1','ATfd','AZd1','AOz1','AOz2','AOz3','AOz4','AGr1','AGr2','AGr3','AGr4']:
 path=next(m['value'] for m in a[uid]['mods'] if m['id']=='aart')
 for p in [path,path.replace('CommandButtons\\BTN','CommandButtonsDisabled\\DISBTN')]:
  raw=(ROOT/'src'/p.replace('\\','/')).read_bytes();assert raw[:4]==b'BLP1'
  im=Image.open(ROOT/'src'/p.replace('\\','/'));assert im.size==(64,64)
print('Random dome bolts: all ranks, resource caps, eligibility, empty groups, buff orders, visual expiry/cleanup, all-rank typed cast ranges and 24 BTN/DISBTN assets passed')
