import json,numpy as np
def rot(q):
 x,y,z,w=q/np.linalg.norm(q)
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
from PIL import Image,ImageDraw
from pathlib import Path
m=json.load(open('799x-gragus-animation/model.json'))
def sample(track,t,default):
 if not track or not track.get('Keys'):return np.array(default,float)
 ks=track['Keys'];a=max([k for k in ks if k['Frame']<=t],key=lambda k:k['Frame'],default=ks[0]);b=min([k for k in ks if k['Frame']>=t],key=lambda k:k['Frame'],default=ks[-1]);f=0 if a['Frame']==b['Frame'] else (t-a['Frame'])/(b['Frame']-a['Frame'])
 if len(default)==4:
  if a==b:return np.array(a['Vector'])
  aa=np.array(a['Vector']);bb=np.array(b['Vector']);bb=bb if np.dot(aa,bb)>=0 else -bb;q=aa*(1-f)+bb*f;return q/np.linalg.norm(q)
 return np.array(a['Vector'])*(1-f)+np.array(b['Vector'])*f

def matrices(t,over={}):
 out={}
 def calc(i):
  if i in out:return out[i]
  n=m['Nodes'][i];p=np.array(n['PivotPoint']);r=sample(n.get('Rotation'),t,[0,0,0,1]);tr=sample(n.get('Translation'),t,[0,0,0]);sc=sample(n.get('Scaling'),t,[1,1,1])
  if i in over:r=over[i].get('r',r);tr=over[i].get('t',tr)
  M=np.eye(4);M[:3,:3]=rot(r)@np.diag(sc);M[:3,3]=p+tr-M[:3,:3]@p
  if n['Parent'] is not None:M=calc(n['Parent'])@M
  out[i]=M;return M
 for i,n in enumerate(m['Nodes']):
  if n:calc(i)
 return out


def vertices(t,over={}):
 mats=matrices(t,over);result=[]
 for gi in [0,3]:
  g=m['Geosets'][gi];v=np.array(g['Vertices']).reshape(-1,3);v=np.c_[v,np.ones(len(v))];vs=[]
  for k,vert in enumerate(v):
   group=g['Groups'][g['VertexGroup'][k]];vs.append((sum(mats[j] for j in group)/len(group)@vert)[:3])
  result.append((gi,np.array(vs),np.array(g['Faces']).reshape(-1,3)))
 return result

def render(t,over={},label=''):
 im=Image.new('RGB',(400,450),'#202832');d=ImageDraw.Draw(im);tri=[]
 for gi,v,faces in vertices(t,over):
  for f in faces:
   points=v[f];depth=np.mean(points[:,0]+points[:,1]);xy=[(200+(p[0]-p[1])*.9,410-p[2]*1.4+(p[0]+p[1])*.15) for p in points];tri.append((depth,xy,gi))
 for depth,xy,gi in sorted(tri):d.polygon(xy,fill=('#aa7658' if gi==0 else '#deb669'),outline=('#684532' if gi==0 else '#94733c'))
 d.text((10,10),label or str(t),fill='white');return im
if __name__=='__main__':
 canvas=Image.new('RGB',(1200,450))
 for i,t in enumerate([1833,36167,36433]):canvas.paste(render(t),(i*400,0))
 canvas.save('799x-gragus-animation/poses.png')
