"""Audit packaged command cards and execute JASS against deferred-sale native mocks.

This does not emulate Warcraft rendering. It specifically catches the old 13-button
card and a post-event stock decrement consuming a button restored inside the event.
"""
from pathlib import Path
import re,json,sys,collections
R=Path(__file__).resolve().parent;W=R.parent;B=R/'roundtrip'
sys.path.insert(0,str(W/'ffa-v4/tools'));from objectio import Obj
s=(B/'war3map.j').read_text()
helper=(W/'ffa-v4/verify_behavior.py').read_text();exec(helper[helper.index('def translate('):helper.index("translated='")])
pages=json.loads((R/'shop-pages.json').read_text())
u=Obj(B/'war3map.w3u');us=Obj(B/'war3mapSkin.w3u');it=Obj(B/'war3map.w3t');its=Obj(B/'war3mapSkin.w3t')
def props(table,kind):return {m[0].decode():m[4] for m in (table.find(kind) or {}).get('mods',[])}
def merged(table,skin,kind):return props(table,kind)|props(skin,kind)
for family,token,table,skin in [('creeps','h02U',u,us),('recipes','h037',it,its)]:
 p=merged(u,us,token)
 assert (p['ubpx'],p['ubpy'])==(2,2) and p['utip']=='Next page'
 assert p['usst']==0 and p['usma']==1 and p['usrg']==1
 assert all(p[k]==0 for k in ['ugol','ulum','ufoo']) and p['ureq']==''
 assert 'BTNReplay-SpeedUp' in p['uico']
 for page in pages[family]:
  positions=[(merged(table,skin,k)['ubpx'],merged(table,skin,k)['ubpy']) for k in page]+[(2,2),(3,2)]
  assert len(positions)<=12 and len(positions)==len(set(positions)),(family,page,positions)
 old=json.loads((W/'ffa-v8/shop-pages.json').read_text())[family]
 assert sum(pages[family],[])==sum(old,[]),'Stock lost or duplicated'
ability=merged(Obj(B/'war3map.w3a',True),Obj(B/'war3mapSkin.w3a',True),'Aneu')
assert (ability['abpx'],ability['abpy'])==(3,2)

names=['F8_RefreshShop','F8_FinishShopPage','F8_ShopSale','F8_KeepRecipeStock','F8_ShopInitEnum','F8_InitShops','Trig_Add_Creeps_To_Pub_Mode_Actions','Trig_limit_amount_of_creeps_Actions']
code='\n\n'.join(translate(n) if '\n' in translate(n) else translate(n)+'\n    pass' for n in names)
e={};timers=[];selections=[];units=[];registered=[];conditions=[]
def unit(kind,owner):
 x=dict(kind=kind,owner=owner,stock={},removed=False);units.append(x);return x
def add(shop,kind,current,maximum):shop['stock'][kind]=current
def remove(shop,kind):shop['stock'].pop(kind,None)
def save(h,k,c,v):h[k,c]=v
def flush(h,k):
 for key in list(h):
  if key[0]==k:del h[key]
def groupcall(group,fn):
 for unit in list(group):e['enum']=unit;fn()
e.update(GetUnitTypeId=lambda u:u['kind'],GetOwningPlayer=lambda u:u['owner'],GetHandleId=id,
 AddUnitToStock=add,AddItemToStock=add,RemoveUnitFromStock=remove,RemoveItemFromStock=remove,
 SaveInteger=save,LoadInteger=lambda h,k,c:h.get((k,c),0),SaveUnitHandle=save,LoadUnitHandle=lambda h,k,c:h.get((k,c)),
 SavePlayerHandle=save,LoadPlayerHandle=lambda h,k,c:h.get((k,c)),SaveTimerHandle=save,LoadTimerHandle=lambda h,k,c:h.get((k,c)),
 RemoveSavedHandle=lambda h,k,c:h.pop((k,c),None),FlushChildHashtable=flush,
 GetSellingUnit=lambda:e['shop'],GetSoldUnit=lambda:e['sold'],GetExpiredTimer=lambda:e['expired'],
 CreateTimer=lambda:object(),TimerStart=lambda t,d,r,fn:timers.append((t,fn)),DestroyTimer=lambda t:None,
 ModuloInteger=lambda x,y:x%y,RemoveUnit=lambda u:u.update(removed=True),SelectUnitForPlayerSingle=lambda u,p:selections.append((u,p)),
 InitHashtable=dict,CreateGroup=list,CreateTrigger=object,GroupEnumUnitsInRect=lambda g,*a:g.extend(units),
 GetPlayableMapRect=lambda:None,ForGroup=groupcall,GetEnumUnit=lambda:e['enum'],DestroyGroup=lambda g:None,
 TriggerRegisterAnyUnitEventBJ=lambda t,event:registered.append(event),EVENT_PLAYER_UNIT_SELL='sell',
 TriggerAddAction=lambda *a:None,TriggerAddCondition=lambda t,c:conditions.append(c),Condition=lambda f:f,bj_stockItemPurchased=object())
exec(code,e)
shops=[unit(kind,p) for p in [0,4,7,11,1,3,6,9] for kind in ['n00R','n01Y']]
e['F8_InitShops']();assert registered==['sell'] and len(conditions)==1
def finish():
 while timers:
  t,fn=timers.pop(0);e['expired']=t;fn()
for shop in shops:
 family,token=('creeps','h02U') if shop['kind']=='n00R' else ('recipes','h037')
 for cycle in range(12):
  page=cycle%len(pages[family]);assert set(shop['stock'])==set(pages[family][page]+[token])
  assert shop['stock'][token]==1
  e['shop']=shop;e['sold']=unit(token,shop['owner'])
  # Real units are passed through this earlier trigger; page controls must return before any cap/bounty work.
  e['Trig_limit_amount_of_creeps_Actions']();e['F8_ShopSale']()
  assert e['sold']['removed'] and len(timers)==1
  # Model consumption AFTER the sell event, which broke an immediate remove/add refresh.
  shop['stock'][token]-=1
  finish();assert shop['stock'][token]==1 and selections[-1]==(shop,shop['owner'])
  before=shop['stock'].copy();e['Trig_Add_Creeps_To_Pub_Mode_Actions']();assert shop['stock']==before
 assert not any(k[1]==1 for k in e['F8_Shops']),'Leaked timer handle'
# Two shop clicks can be pending independently, including different players.
for shop,token in [(shops[0],'h02U'),(shops[3],'h037')]:
 e['shop']=shop;e['sold']=unit(token,shop['owner']);e['F8_ShopSale']()
assert len(timers)==2;finish()
# Only recipe vendors bypass Blizzard marketplace removal; ordinary shops retain default behavior.
for kind,expected in [('n01Y',False),('n000',True),('n00R',True)]:
 e['shop']=unit(kind,27);assert conditions[0]()==expected
# Ordinary purchases are not swallowed by paging and do not refresh/reset stock.
for shop,token in [(shops[0],'hrdh'),(shops[1],'not-a-page')]:
 e['shop']=shop;e['sold']=unit(token,0);before=shop['stock'].copy();e['F8_ShopSale']()
 assert not e['sold']['removed'] and not timers and before==shop['stock']
init=re.search(r'^function SF_Initialize\b.*?^endfunction',s,re.M|re.S)[0]
start=re.search(r'^function F8_Start\b.*?^endfunction',s,re.M|re.S)[0]
assert 'call F8_InitShops()' in init and 'InitHashtable' not in start
# Changes are limited to shop code/object data and synchronized editor/title data.
allowed={'war3map.j','war3map.wct','war3map.w3i','war3map.w3u','war3mapSkin.w3u','war3map.w3t','war3mapSkin.w3t','(listfile)','(attributes)','(signature)'}
changed=[]
for file in B.rglob('*'):
 if file.is_file():
  rel=file.relative_to(B)
  if file.read_bytes()!=(R/'base'/rel).read_bytes():changed.append(str(rel));assert str(rel) in allowed,rel
# Object changes may only alter shop navigation or the position of sold stock icons.
for filename in ['war3map.w3u','war3mapSkin.w3u','war3map.w3t','war3mapSkin.w3t']:
 old=Obj(R/'base'/filename);new=Obj(B/filename)
 for table in new.tables:
  for obj in table:
   kind=(obj['new'] if obj['new']!=bytes(4) else obj['old']).decode()
   a=props(old,kind);b=props(new,kind)
   keys={k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
   if keys:
    if kind in ['h02U','h037']:
     assert keys<={'unam','utip','utub','uhot','ubpx','ubpy','uico','ugol','ulum','ufoo','usst','usrg','usma','ussc','ureq','urqa','upgr'}
    else:assert kind in sum(pages['creeps'],[])+sum(pages['recipes'],[]) and keys<={'ubpx','ubpy'}
print('PASS: packaged command cards have unique slots for all purchases, Next, and Select Buyer; free zero-delay navigation; all 16 shops cycle/wrap through all 21 creeps and 17 recipes; post-sale stock consumption, concurrent shops, pub timer, cleanup isolation and ordinary purchases checked. Terrain/placement/assets unchanged.')
