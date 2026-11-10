from pathlib import Path
import sys,struct,re,json,ctypes as c,shutil,subprocess,hashlib,math
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive
B=R/'base';O=R/'src'
for d in [B,O,R/'release']:d.mkdir(exist_ok=True)
shutil.copyfile(W/'ffa-v14/release/Solo_Foots_8P_FFA_v14.w3x',R/'baseline.w3x');archive.extract(R/'baseline.w3x',B)
s=(B/'war3map.j').read_text();pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
source=(W/'ffa-v4/build.py').read_text();exec(source[source.index('class Reader:'):source.index('shop_types=')])
b=(B/'war3mapUnits.doo').read_bytes();units=placements(b);records=[];moves=[];roster=[0,4,7,11,1,3,6,9]
info=(B/'war3map.w3i').read_bytes();path=(B/'war3map.wpm').read_bytes();pw,ph=struct.unpack_from('<II',path,8)
shops=json.loads((W/'ffa-v11/shop-audit.json').read_text())
for u in units:
 rec=bytearray(b[u['start']:u['end']])
 if u['kind']=='sloc' and u['owner'] in roster:
  p=u['owner'];x,y=u['x'],u['y'];angle=math.atan2(y+256,x);nx=x+96*math.cos(angle);ny=y+96*math.sin(angle)
  for dx in range(-192,193,32):
   for dy in range(-192,193,32):
    i=int((nx+dx+5120)/32);j=int((ny+dy+5376)/32)
    assert 0<=i<pw and 0<=j<ph and not path[16+j*pw+i]&2,('Blocked base footprint',p,dx,dy)
  gap=min(math.dist((nx,ny),a['position']) for a in shops);assert gap>=384,(p,gap)
  struct.pack_into('<ff',rec,8,nx,ny)
  old=struct.pack('<ff',x,y);new=struct.pack('<ff',nx,ny);assert old in info,('Missing map info start',p);info=info.replace(old,new)
  for axis,val in [('X',nx),('Y',ny)]:s=re.sub(r'(set SF_Base'+axis+r'\['+str(p+1)+r'\]=)[^\n]+',lambda m:m[1]+f'{val:.3f}',s)
  row=roster.index(p);s=re.sub(r'call DefineStartLocation\('+str(row)+r',[^\n]+',f'call DefineStartLocation({row}, {nx:.3f}, {ny:.3f})',s)
  moves.append(dict(player=p+1,old=[x,y],new=[nx,ny],distance=96,nearest_shop=gap))
 records.append(rec)
assert len(moves)==8
(O/'war3mapUnits.doo').write_bytes(b[:16]+b''.join(records))
title='Solo Foots 8P FFA + King v15';s=re.sub(r'call SetMapName\("[^\"]+"\)',f'call SetMapName("{title}")',s)
end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):];tail=tail[:tail.index('# Terrain-derived BLP1 minimaps')]+tail[tail.index('work=Path('):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v15.w3x').replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','')
report={'base_moves':moves};exec(tail)
for name in ['war3map.w3e','war3map.wpm','war3map.w3u','war3map.w3a','war3map.w3t']:
 assert (R/'roundtrip'/name).read_bytes()==(B/name).read_bytes(),name
print('PASS: eight bases moved 96 outward; 384-wide footprint clear; shops >=384 away; runtime, editor starts and map info synchronized; balance and terrain unchanged.')
