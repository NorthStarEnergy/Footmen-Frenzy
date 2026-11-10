import sys,math,numpy as np
sys.path.insert(0,'799x-gragus-animation');from preview import *
def mul(a,b):
 x,y,z,w=a;X,Y,Z,W=b;return np.array([w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z])
def axis(i,deg):
 a=np.zeros(4);a[i]=math.sin(math.radians(deg)/2);a[3]=math.cos(math.radians(deg)/2);return a
can=Image.new('RGB',(1200,450))
for k,angle in enumerate([-40,-70,-100]):
 q=mul(axis(0,angle),sample(m['Nodes'][35]['Rotation'],1833,[0,0,0,1]));over={35:{'r':q}};can.paste(render(1833,over,str(angle)),(400*k,0))
can.save('799x-gragus-animation/drink-study.png')
