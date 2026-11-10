from pathlib import Path
import math,struct
b=(Path(__file__).parent/'roundtrip/war3map.wpm').read_bytes()
w,h=struct.unpack_from('<II',b,8)
points=[]
for p in range(8):
 a=p*math.pi/4
 for i in range(86):
  r=560+(i//4)*64-((i//2)%2)*16
  t=(i%2*2-1)*(32+(i//4)*20+((i//2)%2)*48)
  x=r*math.cos(a)-t*math.sin(a);y=-256+r*math.sin(a)+t*math.cos(a)
  for dx,dy in [(0,0),(16,0),(-16,0),(0,16),(0,-16)]:
   col=int((x+dx+5120)/32);row=int((y+dy+5376)/32)
   assert 0<=col<w and 0<=row<h and not b[16+row*w+col]&2,(p,i,x,y)
  points.append((x,y,p))
minimum=min(math.hypot(x-u,y-v) for k,(x,y,p) in enumerate(points) for u,v,q in points[k+1:])
enemy=min(math.hypot(x-u,y-v) for k,(x,y,p) in enumerate(points) for u,v,q in points[k+1:] if p!=q)
assert minimum>=48
assert enemy<500
print(f'All 688 positions walkable with 16-unit clearance; minimum spacing {minimum:.1f}; closest opposing ranks {enemy:.1f}.')
