from pathlib import Path
import sys,struct,math,re,json,ctypes as c,shutil,subprocess,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive
B=R/'base';O=R/'src'
for folder in [B,O,R/'release']:folder.mkdir(parents=True,exist_ok=True)
shutil.copyfile(W/'ffa-v8/release/Solo_Foots_8P_FFA_v8.w3x',R/'baseline.w3x')
archive.extract(R/'baseline.w3x',B)
s=(B/'war3map.j').read_text();pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
def put(n,t):
 global s
 s=s.replace(funcs(s)[n],t)
# Shrink the central circle 15%, tapering the displacement to zero before the towers.
def radius(r):
 if r<=2220:return r*.85
 if r<3300:return r-333*(3300-r)/1080
 return r
def inverse(r):
 if r<=1887:return r/.85
 if r<3300:return (r+333*3300/1080)/(1+333/1080)
 return r
def transform(x,y):
 r=math.hypot(x,y+256);q=radius(r)/r if r else 1
 return x*q,-256+(y+256)*q
terrain=(B/'war3map.w3e').read_bytes();N=81;ox=-5120;oy=-5376
def tile(x,y):
 i=max(0,min(80,round((x-ox)/128)));j=max(0,min(80,round((y-oy)/128)))
 return terrain[85+(j*N+i)*8:85+(j*N+i+1)*8]
raw=bytearray(terrain[:85]);levels=[]
for j in range(N):
 for i in range(N):
  x=ox+i*128;y=oy+j*128;r=math.hypot(x,y+256);q=inverse(r)/r if r else 1
  t=tile(x*q,-256+(y+256)*q);raw.extend(t);levels.append(t[7]&15)
(O/'war3map.w3e').write_bytes(raw)
pb=(B/'war3map.wpm').read_bytes();pw,ph=struct.unpack_from('<II',pb,8);path=bytearray(pb[:16])
for j in range(ph):
 for i in range(pw):
  x=ox+(i+.5)*32;y=oy+(j+.5)*32;r=math.hypot(x,y+256);q=inverse(r)/r if r else 1
  u=int((x*q-ox)/32);v=int((-256+(y+256)*q-oy)/32)
  value=pb[16+v*pw+u] if 0<=u<pw and 0<=v<ph else 254
  ti=i//4;tj=j//4;ls=[levels[(tj+dy)*N+ti+dx] for dx,dy in [(0,0),(1,0),(0,1),(1,1)]]
  if max(ls)!=min(ls):value|=2
  path.append(value)
(O/'war3map.wpm').write_bytes(path);(O/'war3map.shd').write_bytes(bytes(pw*ph))
source=(W/'ffa-v4/build.py').read_text();exec(source[source.index('class Reader:'):source.index('shop_types=')])
ub=(B/'war3mapUnits.doo').read_bytes();units=placements(ub);records=[];changes=[]
def walkable(x,y,clearance=64):
 for dx,dy in [(0,0),(clearance,0),(-clearance,0),(0,clearance),(0,-clearance)]:
  i=int((x+dx-ox)/32);j=int((y+dy-oy)/32)
  if not (0<=i<pw and 0<=j<ph) or path[16+j*pw+i]&2:return False
 return True
for u in units:
 x,y=u['x'],u['y'];kind=u['kind']
 if kind in ['n01B','n004']:
  x,y=transform(x,y)
  choices=[(x+dx,y+dy) for dx in range(-192,193,32) for dy in range(-192,193,32) if walkable(x+dx,y+dy)]
  assert choices,('no middle shop seat',kind,x,y)
  x,y=min(choices,key=lambda p:math.hypot(p[0]-x,p[1]-y))
 rec=bytearray(ub[u['start']:u['end']]);struct.pack_into('<ff',rec,8,x,y)
 if kind in ['n01B','n004']:struct.pack_into('<f',rec,20,math.atan2(-256-y,-x))
 records.append(rec);changes.append(dict(kind=kind,owner=u['owner'],old=[u['x'],u['y']],new=[x,y]))
(O/'war3mapUnits.doo').write_bytes(ub[:16]+b''.join(records))
creation=funcs(s)['CreateAllUnits']
for ch in changes:
 if ch['old']==ch['new']:continue
 def repl(m):
  x=float(m[2].replace(' ',''));y=float(m[3].replace(' ',''))
  if math.hypot(x-ch['old'][0],y-ch['old'][1])>.03:return m[0]
  nx,ny=ch['new'];return m[1]+f'{nx:.3f}, {ny:.3f}, {math.degrees(math.atan2(-256-ny,-nx)):.3f}'+m[5]
 creation=re.sub(r"(BlzCreateUnitWithSkin\(Player\(\d+\), '"+ch['kind']+r"', )([\d. -]+), ([\d. -]+), ([\d. -]+)(, '....'\))",repl,creation)
put('CreateAllUnits',creation)
# Move decorative/cliff blockers through the same transformation.
db=(B/'war3map.doo').read_bytes();reader=Reader(db);reader.o=12;count=reader.get('I');decor=[]
for _ in range(count):
 st=reader.o;kind=reader.get('4s');reader.skip(4);x,y,z=reader.get('3f');reader.skip(4+12+4+4+2+4)
 for _ in range(reader.get('I')):reader.skip(reader.get('I')*8)
 reader.skip(4+4+12);rec=bytearray(db[st:reader.o]);nx,ny=transform(x,y)
 struct.pack_into('<ff',rec,8,nx,ny);decor.append(rec)
assert db[reader.o:]==bytes(8)
(O/'war3map.doo').write_bytes(db[:16]+b''.join(decor)+bytes(8))
# Keep vision and the forward neutral camps aligned with the contracted entrances.
put('F8_InitVision',funcs(s)['F8_InitVision'].replace('2220.','1887.'))
put('F8_VisionTick',funcs(s)['F8_VisionTick'].replace('2320.',f'{radius(2320):.3f}'))
put('Trig_colossal_spawn_Actions',funcs(s)['Trig_colossal_spawn_Actions'].replace('2580.',f'{radius(2580):.3f}'))
title='Solo Foots 8 Player FFA v9';s=re.sub(r'call SetMapName\("[^\"]+"\)',f'call SetMapName("{title}")',s)
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
# Reuse the validated script/editor synchronization, BLP1 minimap and packaging pipeline.
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v9.w3x')
tail=tail.replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','middle_radius_scale=.85,nominal_middle_area_reduction=.2775,')
report={};exec(tail)
