from pathlib import Path
import json,math
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;d=json.loads((R/'geometry-preview.json').read_text())
im=Image.new('RGB',(1100,530),'#111822');draw=ImageDraw.Draw(im)
def proj(p,center,scale):
 x,y,z=p;a=-.7;u=x*math.cos(a)-y*math.sin(a);v=x*math.sin(a)+y*math.cos(a)
 return (center[0]+scale*u,center[1]+scale*(v*.45-z*.89))
for points in d['pentagons']:
 draw.line([proj(p,(285,380),.48) for p in points+[points[0]]],fill='#315368',width=1)
tri=[]
for mesh in d['pylon']:
 v=[mesh['v'][i:i+3] for i in range(0,len(mesh['v']),3)]
 for i in range(0,len(mesh['f']),3):
  pts=[v[j] for j in mesh['f'][i:i+3]];depth=sum(p[0]*math.sin(-.7)+p[1]*math.cos(-.7) for p in pts)
  tri.append((depth,pts,tuple(int(c*255) for c in mesh['color'])))
for _,pts,color in sorted(tri,reverse=True):draw.polygon([proj(p,(830,430),2) for p in pts],fill=color)
draw.text((130,30),'Dome: faint five-sided outlines',fill='white');draw.text((750,30),'Guardian pylon model',fill='white')
draw.text((340,500),'Geometry preview - not an in-game screenshot',fill='#aeb9c9');im.save(R/'model-preview.png')
