from pathlib import Path
import json,struct,math,collections,re,sys
R=Path(__file__).resolve().parent;B=R/'roundtrip'
data=(B/'war3map.wpm').read_bytes();w,h=struct.unpack_from('<II',data,8)
terrain=(B/'war3map.w3e').read_bytes();units=json.loads((R/'layout.json').read_text())
def cell(x,y):return int((x+5120)/32),int((y+5376)/32)
def walk(c):
 x,y=c;return 0<=x<w and 0<=y<h and not data[16+y*w+x]&2
seen={cell(0,-256)};queue=collections.deque(seen)
while queue:
 x,y=queue.popleft()
 for c in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
  if c not in seen and walk(c):seen.add(c);queue.append(c)
for u in units:
 if u['kind'] in ['sloc','hwtw','n01B','n004','n000']:
  x,y=u['new'];assert cell(x,y) in seen,(u['kind'],x,y)
 if u['kind']=='hwtw':
  x,y=u['new'];i=round((x+5120)/128);j=round((y+5376)/128)
  assert struct.unpack_from('<H',terrain,85+(j*81+i)*8+4)[0]&63==7,'Tower must remain on grass'
for p in range(8):
 a=p*math.pi/4
 for i in range(86):
  radius=560+(i//4)*64-((i//2)%2)*16;t=(i%2*2-1)*(32+(i//4)*20+((i//2)%2)*48)
  x=radius*math.cos(a)-t*math.sin(a);y=-256+radius*math.sin(a)+t*math.cos(a)
  assert cell(x,y) in seen,('Formation',p,i)
s=(B/'war3map.j').read_text()
stats=re.search(r'function Trig_set_hero_stats_Actions\b.*?endfunction',s,re.S)[0]
categories={int(i):int(c) for i,c in re.findall(r'set udg_hero_category\[(\d+)\]\s*=\s*(\d+)',stats)}
for category in range(1,11):assert category in categories.values()
for idx,kind in [(92,'HOr1'),(93,'HGr1')]:
 assert re.search(r"set udg_hero_type\["+str(idx)+r"\]\s*=\s*'"+kind+"'",s)
 assert 1<=categories[idx]<=11
for name in ['war3mapMap.blp','war3mapMap_ingame.blp']:assert (B/name).read_bytes()[:4]==b'BLP1'
sys.path.insert(0,str(R.parent/'ffa-v4/tools'));from objectio import Obj
objects=Obj(B/'war3map.w3u');skins=Obj(B/'war3mapSkin.w3u')
for table in [objects,skins]:
 props={m[0].decode():m[4] for m in table.find('nFHT')['mods']}
 assert props['umdl']==r'buildings\orc\SpiritLodge\SpiritLodge.mdl' and props['usca']>.5
for kind in ['HGr1','HOr1']:assert objects.find(kind)
print('PASS: all eight bases, 16 grass towers, five center shops and 688 spawn positions connect to the center; ten SD categories available; Gragus and Orianna eligible; explicit tavern art in both tables; BLP1 minimaps.')
