"""Test packed JASS behavior with native mocks and validate actual object fields."""
from pathlib import Path
import ast, math, re, json, sys
R=Path(__file__).resolve().parent;W=R.parent
source=(R/'src/war3map.j').read_text(encoding='utf8')
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
for node in ast.parse((W/'799x-backport/check_runtime.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
selected=['VG_Enemy','VG_PointSegment2','VG_EdgeContact','VG_Crosses','VG_CageScan','VG_StunVisualTick']
code='\n\n'.join(translate(n) for n in selected)
checks=[]
def check(name,value):assert value,name;checks.append(name)
def setup():
 units={1:dict(x=0.,y=0.,owner=0,life=1000.),2:dict(x=0.,y=0.,owner=1,life=1000.)}
 state={'next':10,'groups':{},'units':units,'stuns':[],'fx':{},'tags':{},'timers':{},'timer':40,'order_ok':True,'feedback':[]}
 tables={'VG_Hash':{},'VG_PrevX':{},'VG_PrevY':{}}
 def alloc(store,value):state['next']+=1;store[state['next']]=value;return state['next']
 def createunit(p,k,x,y,f):return alloc(units,dict(x=x,y=y,owner=p,life=1.,kind=k,Aloc=1))
 def order(dummy,order,target):
  if state['order_ok']:state['stuns'].append((dummy,order,target));return True
  return False
 noop=lambda *a:None
 env=dict(**tables,bj_PI=math.pi,bj_mapInitialPlayableArea=0,UNIT_TYPE_STRUCTURE='structure',UNIT_TYPE_MAGIC_IMMUNE='immune',
  RMaxBJ=max,RMinBJ=min,RAbsBJ=abs,Cos=math.cos,Sin=math.sin,I2R=float,GetHandleId=lambda x:x,
  GetUnitTypeId=lambda u:1 if u in units else 0,GetWidgetLife=lambda u:units.get(u,{}).get('life',0),
  IsUnitEnemy=lambda u,p:units[u]['owner']!=p,IsUnitType=lambda u,t:units[u].get(t,False),BlzIsUnitInvulnerable=lambda u:units[u].get('invulnerable',False),
  GetUnitAbilityLevel=lambda u,k:units[u].get(k,0),GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],
  GroupEnumUnitsInRect=lambda g,*a:state['groups'][g].__setitem__(slice(None),list(units)),
  FirstOfGroup=lambda g:state['groups'][g][0] if state['groups'][g] else None,
  GroupRemoveUnit=lambda g,u:state['groups'][g].remove(u),GroupAddUnit=lambda g,u:state['groups'][g].append(u),
  IsUnitInGroup=lambda u,g:u in state['groups'][g],CreateUnit=createunit,UnitAddAbility=lambda d,a:units[d].update(ability=a),
  SetUnitAbilityLevel=lambda d,a,l:units[d].update(rank=l),IssueTargetOrder=order,UnitApplyTimedLife=noop,
  VG_StunFeedback=lambda u:state['feedback'].append(u),GetExpiredTimer=lambda:state['timer'],
  AddSpecialEffectTarget=lambda *a:alloc(state['fx'],{}),DestroyEffect=lambda x:state['fx'].pop(x),
  CreateTextTag=lambda:alloc(state['tags'],{}),DestroyTextTag=lambda x:state['tags'].pop(x),
  SetTextTagText=noop,SetTextTagColor=noop,SetTextTagPermanent=noop,SetTextTagLifespan=noop,SetTextTagPosUnit=noop,
  BlzSetSpecialEffectScale=noop,BlzSetSpecialEffectColor=noop,BlzSetSpecialEffectAlpha=noop,PauseTimer=noop,DestroyTimer=lambda t:state['timers'].pop(t,None))
 for typ in ['UnitHandle','PlayerHandle','GroupHandle','Real','Integer','EffectHandle','TextTagHandle']:
  env['Save'+typ]=lambda h,p,k,v:h.__setitem__((p,k),v)
  env['Load'+typ]=lambda h,p,k,typ=typ:h.get((p,k),0 if typ in ['Real','Integer'] else None)
 env['HaveSavedReal']=lambda h,p,k:(p,k) in h
 env['FlushChildHashtable']=lambda h,p:[h.pop(k) for k in list(h) if k[0]==p]
 exec(code,env)
 state['groups'][20]=[];state['groups'][21]=[]
 tables['VG_Hash'].update({(50,0):1,(50,9):0,(50,1):0.,(50,2):0.,(50,5):20,(50,6):21,(50,11):6})
 return env,units,state,tables

e,u,s,t=setup()
for pos,expected in [((0,0,0,0),False),((0,0,500,0),True),((500,0,0,0),True),((-500,0,500,0),True),((500,500,600,600),False)]:check('pentagon geometry '+str(pos),e['VG_Crosses'](*pos)==expected)
e['VG_CageScan'](50);check('inside cage remains free',not s['stuns']);u[2]['x']=500.;e['VG_CageScan'](50)
check('fast outward crossing receives rank 6 stun order',len(s['stuns'])==1 and s['stuns'][0][1:] == ('thunderbolt',2) and u[s['stuns'][0][0]]['rank']==6)
check('stun uses dedicated dummy and correct ability',u[s['stuns'][0][0]]['kind']=='hgr1' and u[s['stuns'][0][0]]['ability']=='AVgs')
u[2]['x']=0.;e['VG_CageScan'](50);check('one stun per target per cage',len(s['stuns'])==1)
for k in ['structure','immune','invulnerable','Aloc']:
 e,u,s,t=setup();u[2].update(x=285.);u[2][k]=True;e['VG_CageScan'](50);check('excludes '+k,not s['stuns'])
e,u,s,t=setup();u[2].update(x=285.,owner=0);e['VG_CageScan'](50);check('excludes allies',not s['stuns'])
e,u,s,t=setup();u[2]['x']=285.;s['order_ok']=False;e['VG_CageScan'](50);check('rejected order does not consume hit',not s['groups'][20])
s['order_ok']=True;e['VG_CageScan'](50);check('target is retried after rejected order',len(s['stuns'])==1)
e,u,s,t=setup();u[2]['BPSE']=1;t['VG_Hash'][40,0]=2;s['timers'][40]={}
for _ in range(88):e['VG_StunVisualTick']()
check('visual remains active beyond rank-six 2.75 second duration while buff exists',40 in s['timers'] and bool(s['fx']) and bool(s['tags']))
u[2]['BPSE']=0;e['VG_StunVisualTick']();check('stun visuals and timer clean after buff ends',40 not in s['timers'] and not s['fx'] and not s['tags'])

sys.path.insert(0,str(W/'mini-foots/tools'));import objdata
from game_data import game_read,slk
a=objdata.load(str(R/'src/war3map.w3a'));meta=slk(game_read(r'war3.w3mod:units\abilitymetadata.slk'))
expected={'int':0,'bool':0,'real':1,'unreal':2,'string':3}
for name,ranks,rng in [('AVgq',6,700),('AVgw',6,900),('AVge',6,900),('AVgr',3,650)]:
 ability=next(x for tab in a['tables'] for x in tab if x['newId']==name)
 for rank in range(1,ranks+1):
  v=next(m for m in ability['mods'] if m['id']=='aran' and m['level']==rank)
  check(f'{name} rank {rank} range and unsigned-real type',v['value']==rng and v['type']==2)
for name in ['AVgq','AVgw','AVge','AVgr','AVgs']:
 ability=next(x for tab in a['tables'] for x in tab if x['newId']==name)
 check(name+' fields match Warcraft metadata types',all(m['type']==expected.get(meta.get(m['id'],{}).get('type'),m['type']) for m in ability['mods']))
stun=next(x for tab in a['tables'] for x in tab if x['newId']=='AVgs')
speed=next(m for m in stun['mods'] if m['id']=='amsp')
check('stun projectile speed uses integer 10000',speed['type']==0 and speed['value']==10000)
for rank in range(1,7):
 for key in ['adur','ahdu']:
  v=next(m for m in stun['mods'] if m['id']==key and m['level']==rank)
  check(f'rank {rank} {key} stun duration',abs(v['value']-(1.5+0.25*(rank-1)))<0.001 and v['type']==2)
(R/'checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'scope':'Translated packaged JASS and object metadata, mocked native behavior; engine playtest pending.'},indent=2));print(len(checks),'Veigar checks passed')
