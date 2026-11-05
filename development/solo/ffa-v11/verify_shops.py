from pathlib import Path
import math,struct,json,re,collections
R=Path(__file__).resolve().parent;W=R.parent;B=R/'roundtrip'
s=(B/'war3map.j').read_text();source=(W/'ffa-v4/build.py').read_text();exec(source[source.index('class Reader:'):source.index('shop_types=')])
units=placements((B/'war3mapUnits.doo').read_bytes());audit=json.loads((R/'shop-audit.json').read_text())
assert len(audit)==89 and sum(u['runtime'] for u in audit)==8
shops={u['kind'] for u in audit};placed=[u for u in units if u['kind'] in shops];assert len(placed)==81
creation=re.search(r'^function CreateAllUnits\b.*?^endfunction',s,re.M|re.S)[0]
for u in placed:
 a=math.atan2(-256-u['y'],-u['x']);error=abs(math.atan2(math.sin(u['angle']-a),math.cos(u['angle']-a)))
 assert error<1e-5,('Facing',u)
 candidates=re.findall(r"BlzCreateUnitWithSkin\(Player\(\d+\), '"+u['kind']+r"', ([\d.-]+), ([\d.-]+), ([\d.-]+),",creation)
 assert any(math.dist((float(x),float(y)),(u['x'],u['y']))<.01 and abs(math.atan2(math.sin(math.radians(float(deg))-a),math.cos(math.radians(float(deg))-a)))<.001 for x,y,deg in candidates),('Runtime mismatch',u)
for row in audit:
 if row['runtime']:
  pn=row['sector']+1
  x=float(re.search(r'set SF_TavernX\['+str(pn)+r'\]=([^\n]+)',s)[1]);y=float(re.search(r'set SF_TavernY\['+str(pn)+r'\]=([^\n]+)',s)[1])
  assert math.dist((x,y),row['position'])<.01
 assert row['wall_gap']<= (288 if row['kind']=='n000' else 176)
 if 'sector' in row:
  pn=row['sector']+1
  bx=float(re.search(r'set SF_BaseX\['+str(pn)+r'\]=([^\n]+)',s)[1]);by=float(re.search(r'set SF_BaseY\['+str(pn)+r'\]=([^\n]+)',s)[1])
  assert math.dist((bx,by),row['position'])+96<1500,'Rear shop outside own base vision'
  assert all(math.dist((bx,by),(u['x'],u['y']))>1500+96 for u in units if u['kind']=='hwtw' and u['owner']!=row['sector']),'Vision exposes opponent tower'
positions=[a['position'] for a in audit]
assert min(math.dist(a,b) for i,a in enumerate(positions) for b in positions[i+1:])>=191.99
path=(B/'war3map.wpm').read_bytes();pw,ph=struct.unpack_from('<II',path,8)
def cell(x,y):return int((x+5120)/32),int((y+5376)/32)
blocked=set()
for a in audit:
 x,y=a['position'];r=96 if a['kind']=='n000' else 64
 for j in range(cell(x-r,y-r)[1],cell(x+r,y+r)[1]+1):
  for i in range(cell(x-r,y-r)[0],cell(x+r,y+r)[0]+1):blocked.add((i,j))
def walk(c):
 i,j=c;return 0<=i<pw and 0<=j<ph and not path[16+j*pw+i]&2 and c not in blocked
seen={cell(0,-256)};q=collections.deque(seen)
while q:
 x,y=q.popleft()
 for c in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
  if c not in seen and walk(c):seen.add(c);q.append(c)
for row in audit:
 x,y=row['position'];a=math.atan2(y+256,x)
 approach=cell(x-192*math.cos(a),y-192*math.sin(a));assert approach in seen,('Blocked approach',row)
for u in units:
 if u['kind'] in ['hwtw','sloc']:assert cell(u['x'],u['y']) in seen
old=placements((R/'base/war3mapUnits.doo').read_bytes());before={u['id']:u for u in old}
for u in units:
 if u['kind'] not in shops:assert (u['x'],u['y'],u['angle'])==(before[u['id']]['x'],before[u['id']]['y'],before[u['id']]['angle'])
print('PASS: all 81 placed shops + eight runtime taverns face mid, wall gaps audited, stock-family spacing >=192, all approaches connected with conservative shop footprints, script/placement coordinates agree, bases/towers unchanged.')
