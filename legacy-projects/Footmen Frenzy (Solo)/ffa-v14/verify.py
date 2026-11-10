from pathlib import Path
import sys,re,json,math
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'ffa-v4/tools'));from objectio import Obj
s=(R/'roundtrip/war3map.j').read_text();report=json.loads((R/'verification.json').read_text())
u=Obj(R/'roundtrip/war3map.w3u');it=Obj(R/'roundtrip/war3map.w3t')
def p(o,k):return {m[0].decode():m[4] for m in o.find(k)['mods']}
for id,old,new in report['prices']:
 assert old<=7000 and p(it,id)['igol']==new
 assert new==({'I004':1500,'I00H':1250}.get(id,math.floor(old*.9+.5)))
for id,old,new in report['health']:assert p(u,id)['uhpm']==round(old*1.1)==new
assert p(u,'hwtw')['ugol']==250 and p(u,'h000')['ubui']=='hhou,hwtw'
assert all(int(v)==200 for v in re.findall(r'set udg_startgold=(\d+)',s))
assert 'true, 6.666667' in s and 'true, 5.416667' in s
helper=(W/'ffa-v4/verify_behavior.py').read_text();exec(helper[helper.index('def translate('):helper.index("translated='")])
code='\n\n'.join(translate(n) for n in ['F14_IsTower','F14_Grass','F14_OwnBase','F14_Construct'])
e={};units=[];gold=[];tile='Yhdg'
slots=[0,4,7,11,1,3,6,9]
e.update(F8_Team={p:i+1 for i,p in enumerate(slots)},F8_Slot={i+1:p for i,p in enumerate(slots)},udg_player_active={p+1:True for p in slots})
for axis in ['X','Y']:e['SF_Base'+axis]={int(p):float(v) for p,v in re.findall(r'set SF_Base'+axis+r'\[(\d+)\]=([\d.-]+)',s)}
e.update(GetTerrainType=lambda x,y:tile,GetConstructingStructure=lambda:e['tower'],GetOwningPlayer=lambda u:u['owner'],GetPlayerId=lambda p:p,GetUnitTypeId=lambda u:u['kind'],GetUnitX=lambda u:u['x'],GetUnitY=lambda u:u['y'],CreateGroup=list,GroupEnumUnitsOfPlayer=lambda g,p,f:g.extend(x for x in units if x['owner']==p),FirstOfGroup=lambda g:g[0] if g else None,GroupRemoveUnit=lambda g,u:g.remove(u),DestroyGroup=lambda g:None,IsUnitType=lambda u,t:u.get('dead',False),UNIT_TYPE_DEAD=1,RemoveUnit=lambda u:u.update(removed=True),AdjustPlayerStateBJ=lambda n,p,s:gold.append(n),PLAYER_STATE_RESOURCE_GOLD=1,DisplayTextToPlayer=lambda *a:None)
exec(code,e)
for pn in [p+1 for p in slots]:
 x=e['SF_BaseX'][pn];y=e['SF_BaseY'][pn]
 assert e['F14_OwnBase'](pn,x,y)
 assert not e['F14_OwnBase'](pn,0,-256)
 other=next(q+1 for q in slots if q+1!=pn);assert not e['F14_OwnBase'](pn,e['SF_BaseX'][other],e['SF_BaseY'][other])
 tile='Ydrt';assert not e['F14_OwnBase'](pn,x,y);tile='Yhdg'
 for count in [1,4,5]:
  units[:]=[dict(kind='hgtw' if i%2 else 'hwtw',owner=pn-1,x=x,y=y) for i in range(count)]
  e['tower']=units[-1];e['tower']['kind']='hwtw';before=len(gold);e['F14_Construct']()
  assert e['tower'].get('removed',False)==(count>4) and len(gold)-before==int(count>4)
 # A dead tower frees a slot, including when four other structures are still alive/building.
 units[0]['dead']=True;e['tower'].pop('removed',None);e['F14_Construct']();assert not e['tower'].get('removed',False)
for name in ['war3mapUnits.doo','war3map.w3e','war3map.wpm','MiniFootsUI.fdf']:
 assert (R/'roundtrip'/name).read_bytes()==(R/'base'/name).read_bytes()
print('PASS: prices, HP, tier-one costs, 200 starting gold, faster production; all eight home regions reject mid/enemy/dirt; construction cap counts upgrades and frees dead slots; placement/terrain/UI preserved. Engine rendering pending.')
