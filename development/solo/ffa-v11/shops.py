# Executed by build.py after UI integration; shares B/O/s/put/funcs.
import math
reader_source=(W/'ffa-v4/build.py').read_text()
exec(reader_source[reader_source.index('class Reader:'):reader_source.index('shop_types=')])
unitbytes=(B/'war3mapUnits.doo').read_bytes();units=placements(unitbytes)
path=(B/'war3map.wpm').read_bytes();pw,ph=struct.unpack_from('<II',path,8)
terrain=(B/'war3map.w3e').read_bytes()
roster=[0,4,7,11,1,3,6,9]
angles={p:float(re.search(r'set SF_Angle\['+str(p+1)+r'\]=([^\n]+)',s)[1].replace(' ','')) for p in roster}
def ground(x,y):
 i=int((x+5120)/32);j=int((y+5376)/32)
 ti=round((x+5120)/128);tj=round((y+5376)/128)
 return 0<=i<pw and 0<=j<ph and 0<=ti<=80 and 0<=tj<=80 and not path[16+j*pw+i]&2 and terrain[85+(tj*81+ti)*8+7]&15==9
def clear(x,y,r=64):return all(ground(x+dx,y+dy) for dx in [-r,0,r] for dy in [-r,0,r])
def rear_gap(x,y):
 a=math.atan2(y+256,x)
 for d in range(16,1025,16):
  if not ground(x+d*math.cos(a),y+d*math.sin(a)):return d
 return 9999
def front_clear(x,y):
 a=math.atan2(y+256,x)
 return all(clear(x-d*math.cos(a),y-d*math.sin(a),48) for d in [96,160,224])
def closest_sector(x,y):return min(roster,key=lambda p:abs(math.atan2(math.sin(math.atan2(y+256,x)-angles[p]),math.cos(math.atan2(y+256,x)-angles[p]))))
# Keep the authored stock-family order, adding the overlooked upgrades shop and reserving a tavern seat.
order=['nFHT','n012','n007','n00R','n01T','n01Y','n02N','n045','n046','n003']
rear={};audit=[]
for p in roster:
 a=angles[p]
 for index,kind in enumerate(order):
  lateral=(index-4.5)*192.
  choices=[]
  for radial in range(4096,5185,16):
   x=radial*math.cos(a)-lateral*math.sin(a);y=-256+radial*math.sin(a)+lateral*math.cos(a)
   if clear(x,y) and front_clear(x,y) and rear_gap(x,y)<=176:choices.append((x,y))
  assert choices,('No rear wall seat',p,kind)
  x,y=min(choices,key=lambda v:(abs(rear_gap(*v)-112),abs(math.hypot(v[0],v[1]+256)-4400)))
  rear[p,kind]=(x,y)
  audit.append(dict(kind=kind,sector=p,position=[x,y],wall_gap=rear_gap(x,y),runtime=kind=='nFHT'))
# All middle shops face mid with an actual wall behind their footprint.
middle=[];positions={}
for u in [u for u in units if u['kind'] in ['n01B','n004']]:
 choices=[]
 for dx in range(-256,257,16):
  for dy in range(-256,257,16):
   x=u['x']+dx;y=u['y']+dy
   if clear(x,y) and front_clear(x,y) and rear_gap(x,y)<=176:choices.append((x,y))
 assert choices,('No middle wall seat',u['kind'],u['x'],u['y'])
 x,y=min(choices,key=lambda v:math.dist(v,(u['x'],u['y']))+abs(rear_gap(*v)-112)*.25)
 positions[u['id']]=(x,y);middle.append((x,y))
 audit.append(dict(kind=u['kind'],position=[x,y],wall_gap=rear_gap(x,y),runtime=False))
# The Archvault was standing on the central objective; seat the single shop beside a wall tip.
vault=next(u for u in units if u['kind']=='n000');anchor=middle[0];choices=[]
for x in range(int(anchor[0])-768,int(anchor[0])+769,16):
 for y in range(int(anchor[1])-768,int(anchor[1])+769,16):
  if math.hypot(x,y+256)<2500 and clear(x,y,96) and front_clear(x,y) and rear_gap(x,y)<=288 and all(math.dist((x,y),v)>=240 for v in middle):choices.append((x,y))
assert choices,'No Archvault wall seat'
positions[vault['id']]=min(choices,key=lambda v:math.dist(v,anchor)+abs(rear_gap(*v)-144)*.3)
x,y=positions[vault['id']];audit.append(dict(kind='n000',position=[x,y],wall_gap=rear_gap(x,y),runtime=False))
records=[];changes=[];creation=funcs(s)['CreateAllUnits']
for u in units:
 x,y=u['x'],u['y'];kind=u['kind'];rec=bytearray(unitbytes[u['start']:u['end']])
 if kind in order:x,y=rear[closest_sector(x,y),kind]
 elif u['id'] in positions:x,y=positions[u['id']]
 if kind in order or u['id'] in positions:
  a=math.atan2(-256-y,-x)%(2*math.pi)
  struct.pack_into('<ff',rec,8,x,y);struct.pack_into('<f',rec,20,a)
  def repl(m):
   ox=float(m[2].replace(' ',''));oy=float(m[3].replace(' ',''))
   if math.dist((ox,oy),(u['x'],u['y']))>.03:return m[0]
   return m[1]+f'{x:.3f}, {y:.3f}, {math.degrees(a):.3f}'+m[5]
  creation=re.sub(r"(BlzCreateUnitWithSkin\(Player\(\d+\), '"+kind+r"', )([\d. -]+), ([\d. -]+), ([\d. -]+)(, '....'\))",repl,creation)
 records.append(rec);changes.append(dict(kind=kind,owner=u['owner'],old=[u['x'],u['y']],new=[x,y]))
(O/'war3mapUnits.doo').write_bytes(unitbytes[:16]+b''.join(records));put('CreateAllUnits',creation)
# Dynamic taverns use the reserved tenth rear-row seat, with the same direction as placed shops.
s=re.sub(r'^endglobals','real array SF_TavernX\nreal array SF_TavernY\nendglobals',s,count=1,flags=re.M)
init=funcs(s)['SF_Initialize'];anchor='    set SF_GameClock=CreateTimer()'
lines='\n'.join(f'    set SF_TavernX[{p+1}]={rear[p,"nFHT"][0]:.3f}\n    set SF_TavernY[{p+1}]={rear[p,"nFHT"][1]:.3f}' for p in roster)
put('SF_Initialize',init.replace(anchor,lines+'\n'+anchor))
f=funcs(s)['SF_OpenTaverns'];f=re.sub(r"^.*set SF_Tavern\[p\]=CreateUnit[^\n]*", "            set SF_Tavern[p]=CreateUnit(Player(p-1),'nFHT',SF_TavernX[p],SF_TavernY[p],Atan2(-256.-SF_TavernY[p],-SF_TavernX[p])*bj_RADTODEG)",f,flags=re.M);put('SF_OpenTaverns',f)
# The enlarged rear row remains visible to its player (and to their current kingdom).
put('F8_InitVision',funcs(s)['F8_InitVision'].replace('1150.','1500.'))
put('SKSync',funcs(s)['SKSync'].replace('1150.','1500.'))
f=funcs(s)['SoloFootsAltarStockPopulate'].replace('    call SetUnitScale(altar,.85,.85,.85)','    call SetUnitFacing(altar,Atan2(-256.-GetUnitY(altar),-GetUnitX(altar))*bj_RADTODEG)\n    call SetUnitScale(altar,.85,.85,.85)');put('SoloFootsAltarStockPopulate',f)
(R/'shop-audit.json').write_text(json.dumps(audit,indent=2));(R/'layout.json').write_text(json.dumps(changes,indent=2))
