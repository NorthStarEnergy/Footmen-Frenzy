from pathlib import Path
import json,math,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;d=json.loads((R/'assets/preview-mesh.json').read_text())
texture=np.frombuffer((R/'assets/texture.rgba').read_bytes(),dtype=np.uint8).reshape(d['height'],d['width'],4)
def render(angle,up=0.55,size=650,center=None,scale=3.5):
    a=math.radians(angle);right=np.array([-math.sin(a),math.cos(a),0.]);view=np.array([math.cos(a)*math.cos(up),math.sin(a)*math.cos(up),math.sin(up)]);vertical=np.cross(view,right)
    basis=np.array([right,vertical,view]);center=np.array([0.,0.,42.] if center is None else center)
    frame=np.zeros((size,size,3),dtype=float);frame[:]=[19,25,39];depth=np.full((size,size),-1e9)
    def project(points):
        q=(np.array(points)-center)@basis.T;q[:,0]=q[:,0]*scale+size/2;q[:,1]=size/2-q[:,1]*scale;return q
    for mesh in d['meshes']:
        if mesh['alpha']<.01:continue
        pts=np.array(mesh['positions']).reshape(-1,3);q=project(pts);uv=np.array(mesh['uv']).reshape(-1,2)
        for face in np.array(mesh['faces']).reshape(-1,3):
            tri=q[face];p=pts[face];normal=np.cross(p[1]-p[0],p[2]-p[0]);norm=np.linalg.norm(normal)
            if norm<1e-8:continue
            light=.6+.4*abs(np.dot(normal/norm,np.array([.3,-.5,.81])))
            x0=max(0,int(tri[:,0].min()));x1=min(size-1,int(tri[:,0].max())+1);y0=max(0,int(tri[:,1].min()));y1=min(size-1,int(tri[:,1].max())+1)
            if x1<x0 or y1<y0:continue
            x,y=np.meshgrid(np.arange(x0,x1+1),np.arange(y0,y1+1));v0,v1,v2=tri
            den=(v1[1]-v2[1])*(v0[0]-v2[0])+(v2[0]-v1[0])*(v0[1]-v2[1])
            if abs(den)<1e-8:continue
            b0=((v1[1]-v2[1])*(x-v2[0])+(v2[0]-v1[0])*(y-v2[1]))/den;b1=((v2[1]-v0[1])*(x-v2[0])+(v0[0]-v2[0])*(y-v2[1]))/den;b2=1-b0-b1
            z=b0*v0[2]+b1*v1[2]+b2*v2[2];mask=(b0>=0)&(b1>=0)&(b2>=0)&(z>=depth[y0:y1+1,x0:x1+1])
            if not mask.any():continue
            uvface=uv[face];tu=b0*uvface[0,0]+b1*uvface[1,0]+b2*uvface[2,0];tv=b0*uvface[0,1]+b1*uvface[1,1]+b2*uvface[2,1]
            for layer in mesh['layers']:
                if layer['texture']!=0:continue
                pixels=texture[np.clip((tv*d['height']).astype(int),0,d['height']-1),np.clip((tu*d['width']).astype(int),0,d['width']-1)]
                alpha=pixels[:,:,3]/255*mesh['alpha']*layer['alpha'];active=mask&(alpha>.02);dest=frame[y0:y1+1,x0:x1+1]
                if layer['filter']==3:dest[active]=np.minimum(255,dest[active]+pixels[:,:,:3][active]*alpha[active,None])
                else:
                    dest[active]=pixels[:,:,:3][active]*light*alpha[active,None]+dest[active]*(1-alpha[active,None]);depth[y0:y1+1,x0:x1+1][active]=z[active]
    return Image.fromarray(np.clip(frame,0,255).astype('uint8')),project
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
sheet=Image.new('RGB',(1300,750),(19,25,39));draw=ImageDraw.Draw(sheet)
for index,angle in enumerate([35,145]):
    im,proj=render(angle);sheet.paste(im,(index*650,70));draw.text((index*650+25,75),'Front / central weapon' if index==0 else 'Rear / walker geometry',font=font,fill=(190,208,235))
    if index==0:
        point=proj([d['muzzle']])[0];x=point[0];y=point[1]+70;draw.ellipse((x-8,y-8,x+8,y+8),outline=(100,190,255),width=2);draw.line((x+8,y,x+100,y-60),fill=(100,190,255),width=2);draw.text((x+100,y-85),'Launch point',font=small,fill=(150,210,255))
draw.text((25,15),'STALKER  /  Fingolfin model inspection',font=font,fill='white');draw.text((25,716),'Offline rendering of the imported MDX; not a Warcraft game capture.',font=small,fill=(160,175,198))
sheet.save(R/'Stalker-model-preview.png')
# Render command icons directly from the model's head geometry.
icon,_=render(25,up=.17,size=64,center=[8,0,72],scale=1.15)
def blp(im,path):
    im=im.convert('RGB');pal=im.quantize(colors=256);p=pal.getpalette();p=p+[0]*(768-len(p));palette=bytearray()
    for i in range(256):palette.extend([p[i*3+2],p[i*3+1],p[i*3],255])
    header=bytearray(156);header[:4]=b'BLP1';struct.pack_into('<6I',header,4,1,8,64,64,5,0)
    levels=[];offset=1180
    for level in range(7):
        size=64>>level;frame=im.resize((size,size)).quantize(palette=pal);raw=frame.tobytes()+b'\xff'*(size*size)
        struct.pack_into('<I',header,28+level*4,offset);struct.pack_into('<I',header,92+level*4,len(raw));levels.append(raw);offset+=len(raw)
    path.write_bytes(header+palette+b''.join(levels))
for disabled in [False,True]:
    card=icon.copy()
    if disabled:card=card.convert('L').convert('RGB').point(lambda p:round(p*.5))
    frame=ImageDraw.Draw(card);frame.rectangle((0,0,63,63),outline=(8,8,12),width=3);frame.rectangle((3,3,60,60),outline=(65,65,68) if disabled else (150,138,108),width=1)
    name=('DISBTN' if disabled else 'BTN')+'Stalker';card.save(R/'assets'/(name+'.png'))
    dest=R/('src/ReplaceableTextures/CommandButtonsDisabled' if disabled else 'src/Units/Stalker');dest.mkdir(parents=True,exist_ok=True);blp(card,dest/(name+'.blp'))
print('Saved model inspection preview and model-derived command icons.')
