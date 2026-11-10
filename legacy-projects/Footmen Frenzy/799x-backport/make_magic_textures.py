"""Procedural soft blue-green energy textures with mipmapped BLP1 alpha."""
from pathlib import Path
import struct
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'src/Spells/Orianna/Feedback'

def blp(image):
    width,height=image.size
    palette_image=image.convert('RGB').quantize(colors=256)
    colors=palette_image.getpalette();colors += [0]*(768-len(colors))
    palette=b''.join(bytes([colors[i+2],colors[i+1],colors[i],255]) for i in range(0,768,3))
    levels=[]
    while True:
        levels.append(image.convert('RGB').quantize(palette=palette_image,dither=Image.Dither.NONE).tobytes()+image.getchannel('A').tobytes())
        if image.size==(1,1):break
        image=image.resize((max(1,image.width//2),max(1,image.height//2)),Image.Resampling.LANCZOS)
    offsets=[];at=1180
    for level in levels:offsets.append(at);at+=len(level)
    return b'BLP1'+struct.pack('<6I',1,8,width,height,5,0)+struct.pack('<16I',*(offsets+[0]*(16-len(offsets))))+struct.pack('<16I',*([len(v) for v in levels]+[0]*(16-len(levels))))+palette+b''.join(levels)

y,x=np.mgrid[-1:1:512j,-1:1:512j]
r=np.sqrt(x*x+y*y);a=np.arctan2(y,x)
edge=np.clip((1-r)/.17,0,1);edge=edge*edge*(3-2*edge)
noise=.72+.16*np.sin(x*25+y*17+np.sin(y*13)*2)+.12*np.sin(x*47-y*29)
preview=Image.new('RGB',(1400,300),(20,31,30));draw=ImageDraw.Draw(preview)
for index,name in enumerate(['MoveGround','AttackGround','ProtectGround','ShockGround','ShockImpact']):
    if name=='MoveGround':
        density=np.exp(-((x+.12)/.68)**2-(y/.18)**2)
        density+=.65*np.exp(-((y-.16*np.sin(x*5))/.07)**2)*np.exp(-(x/.7)**2)
        density*=.65+.35*(x+1)/2
    elif name=='AttackGround':
        band=np.exp(-((r-.66-.045*np.sin(7*a+5*r))/.14)**2)
        density=band*(.6+.4*np.sin(6*a+5*r)**2)+.18*np.exp(-(r/.6)**2)
    elif name=='ProtectGround':
        density=.45*np.exp(-(r/.6)**2)+.6*np.exp(-((r-.47-.12*np.sin(3*a+4*r))/.16)**2)
    elif name=='ShockGround':
        arms=(.5+.5*np.cos(3*a+8*r))**5
        density=(.18+arms)*np.exp(-r*r/.9)+.8*np.exp(-(r/.17)**2)
    else:
        density=.8*np.exp(-((r-.73)/.16)**2)+.8*np.exp(-(r/.25)**2)+.55*(.5+.5*np.cos(a*8))**2*(r/.35)*np.exp(-(r/.65)**2)
    density=np.clip(density*noise*edge,0,1);bright=np.clip(density*.9,0,1)
    rgba=np.zeros((512,512,4),dtype=np.uint8)
    rgba[:,:,0]=(30+150*bright).astype('uint8');rgba[:,:,1]=(145+100*bright).astype('uint8');rgba[:,:,2]=(160+90*bright).astype('uint8');rgba[:,:,3]=(density*245).astype('uint8')
    im=Image.fromarray(rgba);(OUT/(name+'.blp')).write_bytes(blp(im))
    small=im.resize((260,260),Image.Resampling.LANCZOS);preview.paste(small,(index*280+10,35),small)
    draw.text((index*280+15,12),name,fill=(215,240,235))
    assert np.max(rgba[:,:,3])>=170 and np.all(rgba[[0,-1],:,3]==0)
preview.save(ROOT/'audit/magic-ground-preview.png')
print('Five soft energy textures generated with transparent edges and mipmaps.')
