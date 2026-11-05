"""Execute changed JASS control flow and check packaged geometry/object data."""
from pathlib import Path
import re,math,json,collections,struct,sys
R=Path(__file__).resolve().parent
s=(R/'roundtrip/war3map.j').read_text()
helper=(R.parent/'ffa-v4/verify_behavior.py').read_text()
exec(helper[helper.index('def translate('):helper.index("translated='")])
names=['SF_Initialize','F8_RefreshShop','F8_ShopSale','F8_UpdateBoard','F8_InitVision','F8_VisionTick','Trig_Multiboard_Update_Actions','Trig_KD_Actions','Trig_colossal_stats_Actions','Trig_colossal_spawn_Actions','SoloFootsAltarStockAddPage']
translated='\n\n'.join(translate(n) for n in names).replace('offset/3','offset//3')
(R/'behavior-translated.py').write_text(translated)
e={};slots=[0,4,7,11,1,3,6,9];saved={};spawn=[];fog=[];messages=[];board=[]
glob=re.search(r'^globals\s*$(.*?)^endglobals',s,re.M|re.S)[1]
for typ,array,name in re.findall(r'^\s*(?:constant )?(\w+)\s+(?:(array)\s+)?(\w+)\s*(?:=|$)',glob,re.M):
 d=False if typ=='boolean' else '' if typ=='string' else 0 if typ in ['integer','real'] else None
 e[name]=collections.defaultdict(lambda d=d:d) if array else d
def unit(owner,kind):return dict(owner=owner,kind=kind,stock=set(),items=set(),removed=False)
def radius(p,state,x,y,r,*args):
 f=dict(p=p,x=x,y=y,r=r,stopped=False);fog.append(f);return f
e.update(Player=lambda p:p,GetPlayerId=lambda p:p,GetPlayerName=lambda p:'Player'+str(p),
 GetUnitTypeId=lambda u:u['kind'],GetOwningPlayer=lambda u:27 if u is None else u['owner'],
 GetSellingUnit=lambda:e['shop'],GetSoldUnit=lambda:e['sold'],GetTriggerUnit=lambda:e['victim'],GetKillingUnit=lambda:e['killer'],
 GetTriggerPlayer=lambda:12,IsUnitType=lambda u,t: u['kind'].startswith('H') if t==1 else u.get('structure',False),
 IsUnitEnemy=lambda u,p:u['owner']!=p,RemoveUnit=lambda u:u.update(removed=True),GetHandleId=id,
 SaveInteger=lambda h,k,c,v:saved.__setitem__((k,c),v),LoadInteger=lambda h,k,c:saved.get((k,c),0),
 AddUnitToStock=lambda u,k,a,b:u['stock'].add(k),RemoveUnitFromStock=lambda u,k:u['stock'].discard(k),
 AddUnitToStockBJ=lambda k,u,a,b:u['stock'].add(k),
 AddItemToStock=lambda u,k,a,b:u['items'].add(k),RemoveItemFromStock=lambda u,k:u['items'].discard(k),
 CreateForce=set,ForceAddPlayer=lambda f,p:f.add(p),Location=lambda x,y:(x,y),CreateTimer=object,
 Cos=math.cos,Sin=math.sin,I2R=float,I2S=str,ModuloInteger=lambda a,b:a%b,bj_PI=math.pi,
 MultiboardSetItemValueBJ=lambda *a:board.append(a),DisplayTimedTextToPlayer=lambda *a:messages.append(a[-1]),
 GetFloatGameState=lambda state:e['hour'],CreateFogModifierRadius=radius,
 CreateFogModifierRect=lambda p,*a:radius(p,0,0,0,99999),FogModifierStop=lambda f:f.update(stopped=True),
 F8_SpawnColo=lambda entry,x,y:spawn.append((entry,x,y)),
 UNIT_TYPE_HERO=1,UNIT_TYPE_STRUCTURE=2,FOG_OF_WAR_VISIBLE=0,GAME_STATE_TIME_OF_DAY=0,
 bj_ALLIANCE_UNALLIED=0,EVENT_PLAYER_UNIT_SELL=0,hour=12)
for called in set(re.findall(r'\b(\w+)\(',translated))|set(re.findall(r'\bfunction (\w+)',s)):
 if called not in e and called not in names:e[called]=lambda *a:None
exec(translated,e)
for p in slots:e['udg_player_active'][p+1]=True
e['SF_Initialize']()
assert [e['F8_Slot'][i] for i in range(1,9)]==slots
assert all(e['udg_team'][i]=={p} and e['udg_teamnumber'][p+1]==i for i,p in enumerate(slots,1))
assert e['udg_team'][9]==set(range(12,24))
pages=json.loads((R/'shop-pages.json').read_text())
for kind,token,key,stockfield in [('n00R','h02U','creeps','stock'),('n01Y','h037','recipes','items')]:
 shop=unit(27,kind);e['shop']=shop;e['F8_RefreshShop'](shop,0)
 for page in [0,1,0,1]:
  assert shop[stockfield]-{token}==set(pages[key][page])
  e['sold']=unit(0,token);e['F8_ShopSale']();assert e['sold']['removed']
assert len(set(sum(pages['creeps'],[])))==21
assert len(set(sum(pages['recipes'],[])))==17
for p in slots:
 altar=unit(p,'hhou');e['SF_HeroCount'][p+1]=1
 for i in range(1,12):saved[(id(altar),100+i)]=i;e['udg_hero_type'][i]='H'+str(i).zfill(3)
 e['SoloFootsAltarStockAddPage'](altar,1);assert len(altar['stock'])==12
 altar['stock'].clear();e['SF_HeroCount'][p+1]=2;e['SoloFootsAltarStockAddPage'](altar,1);assert not altar['stock']
for k,p in enumerate(slots):
 e['victim']=unit(p,'H000');e['killer']=unit(slots[(k+1)%8],'hfoo');e['Trig_Multiboard_Update_Actions']()
assert all(e['udg_hero_kills'][p+1]==1 and e['udg_hero_deaths'][p+1]==1 for p in slots)
e['victim']=unit(9,'H000');e['killer']=None;e['Trig_Multiboard_Update_Actions']();assert e['udg_hero_deaths'][10]==2
e['Trig_KD_Actions']();assert len(messages)==8
e['F8_InitVision']()
for p in slots:
 assert sorted(f['r'] for f in fog if f['p']==p and not f['stopped'])==[450.]*7+[1150.,2220.]
for p in range(12,24):assert any(f['p']==p and f['r']==99999 for f in fog)
e['hour']=0;e['F8_VisionTick']()
for p in slots:assert sorted(f['r'] for f in fog if f['p']==p and not f['stopped'])==[160.]*7+[1150.,2220.]
e['Trig_colossal_stats_Actions']()
data=(R/'roundtrip/war3map.wpm').read_bytes();w,h=struct.unpack_from('<II',data,8)
def cell(x,y):return int((x+5120)/32),int((y+5376)/32)
def walk(c):
 x,y=c;return 0<=x<w and 0<=y<h and not data[16+y*w+x]&2
seen={cell(0,-256)};queue=collections.deque(seen)
while queue:
 x,y=queue.popleft()
 for c in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
  if c not in seen and walk(c):seen.add(c);queue.append(c)
for wave in range(1,11):
 spawn.clear();e['udg_colossal_wave']=wave;e['udg_colossal_wave_id']=(wave-1)%5+1;e['Trig_colossal_spawn_Actions']()
 assert len([v for v in spawn if v[0] in [1,2]])==4
 bysector=collections.Counter()
 for entry,x,y in spawn:
  assert cell(x,y) in seen,('colossus unreachable',wave,entry,x,y)
  if entry>2:
   a=math.atan2(y+256,x);p=min(slots,key=lambda p:abs(math.atan2(math.sin(a-e['SF_Angle'][p+1]),math.cos(a-e['SF_Angle'][p+1]))));bysector[p]+=1
 assert len(bysector)==8 and len(set(bysector.values()))==1
 assert min(math.dist(a[1:],b[1:]) for i,a in enumerate(spawn) for b in spawn[i+1:])>100
layout=json.loads((R/'layout.json').read_text());terrain=(R/'roundtrip/war3map.w3e').read_bytes()
towers=[u for u in layout if u['kind']=='hwtw'];assert len(towers)==16
for p in slots:
 pair=[u for u in towers if u['owner']==p];assert len(pair)==2
 a=e['SF_Angle'][p+1];lateral=[]
 for u in pair:
  x,y=u['new'];assert abs(x*math.cos(a)+(y+256)*math.sin(a)-3640)<.01
  lateral.append(-x*math.sin(a)+(y+256)*math.cos(a))
  i=round((x+5120)/128);j=round((y+5376)/128)
  assert struct.unpack_from('<H',terrain,85+(j*81+i)*8+4)[0]&63==7
 assert abs(min(lateral)+640)<.01 and abs(max(lateral)-640)<.01
for u in layout:
 if u['kind'] in ['hwtw','n012','n007','n00R','n01T','n01Y','n02N','n045','n046','n01B','n004']:
  assert cell(*u['new']) in seen,('shop/tower unreachable',u)
assert not any(u['kind'] in ['n02U','n03L','n02Z'] for u in layout)
mid=[u['kind'] for u in layout if u['old'] is None];assert mid==['n01B','n004']*4
shops=[u for u in layout if u['kind'] in ['n012','n007','n00R','n01T','n01Y','n02N','n045','n046']]
assert len(shops)==64 and min(math.dist(a['new'],b['new']) for i,a in enumerate(shops) for b in shops[i+1:])>=191.99
sys.path.insert(0,str(R.parent/'ffa-v4/tools'));from objectio import Obj
objects=Obj(R/'roundtrip/war3map.w3u')
for table in [objects,Obj(R/'roundtrip/war3mapSkin.w3u')]:
 for kind,model in [('nFHT',r'buildings\other\Tavern\Tavern.mdl'),('hhou',r'buildings\human\AltarofKings\AltarofKings.mdl')]:
  mods={m[0].decode():m for m in table.find(kind)['mods']}
  assert mods['umdl'][4]==model and mods['usca'][1]==1 and mods['usca'][4]>.8
for kind in ['HGr1','HOr1']:assert objects.find(kind)
for name in ['war3mapMap.blp','war3mapMap_ingame.blp']:assert (R/'roundtrip'/name).read_bytes()[:4]==b'BLP1'
print('PASS: eight independent forces, all shop pages, altar stock/cap, eight-player K/D, observer/day/night vision, ten waves across all eight sectors, four central colossi, accessible camps/shops, 16 matched grass towers, explicit building art and BLP1 minimaps.')
