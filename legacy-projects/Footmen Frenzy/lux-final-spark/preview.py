"""Offline top-down asset preview using the real JASS visual state and BLPs."""
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageChops
from checks import setup
R=Path(__file__).resolve().parent
S=2;W=980;H=360;scale=.225
fontpath='C:/Windows/Fonts/segoeui.ttf'
font=ImageFont.truetype(fontpath,13*S);title=ImageFont.truetype(fontpath,22*S)
textures={k:Image.open(R/f'src/Spells/Lux/FinalSpark{k}.blp').convert('L') for k in ['Beam','Flare']}
def project(x,y):return round((85+x*scale)*S),round((205-y*scale)*S)
def render(state,age):
    scene=Image.new('RGB',(W*S,H*S),(13,25,24));d=ImageDraw.Draw(scene)
    for x in range(45,W,36):d.line((x*S,95*S,x*S,300*S),fill=(20,36,32),width=1)
    for y in range(95,301,36):d.line((45*S,y*S,935*S,y*S),fill=(20,36,32),width=1)
    d.text((30*S,18*S),'FINAL SPARK',font=title,fill=(247,231,192))
    d.text((30*S,51*S),'Offline effect preview - generated textures and actual JASS visual state',font=font,fill=(145,168,161))
    targets=[(1000,0),(2100,75),(2800,180)]
    for x,y in targets:
        cx,cy=project(x,y);r=8*S
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(125,59,55),outline=(232,132,104),width=S)
    cx,cy=project(0,0);d.ellipse((cx-10*S,cy-10*S,cx+10*S,cy+10*S),fill=(63,110,135),outline=(150,205,226),width=S)
    # Join coplanar strips before rasterizing, avoiding independent pixel-rounding
    # cracks at mesh boundaries in this offline 2-D renderer.
    groups=[[] for _ in range(5)];flares=[]
    ordinal=0
    for handle,fx in state['effects'].items():
        if 'Flare' in fx['model']:flares.append(fx)
        else:
            if fx.get('alpha',255):groups[ordinal%5].append(fx)
            ordinal+=1
    visuals=list(flares)
    for group in groups:
        if not group:continue
        merged=dict(group[0]);left=min(v['x']-v['matrix'][0]/2 for v in group);right=max(v['x']+v['matrix'][0]/2 for v in group)
        merged['x']=(left+right)/2;merged['matrix']=(right-left,*merged['matrix'][1:]);visuals.append(merged)
    for fx in visuals:
        alpha=fx.get('alpha',255)
        if not alpha:continue
        flare='Flare' in fx['model'];tex=textures['Flare' if flare else 'Beam']
        a,b,c=fx.get('matrix',(fx.get('scale',1),)*3)
        width=max(1,round(a*scale*S));height=max(1,round(b*scale*S))
        mask=tex.resize((width,height),Image.Resampling.BILINEAR)
        rgb=fx.get('color',(255,255,255))
        layer=Image.merge('RGB',tuple(mask.point([round(v*channel*alpha/(255*255)) for v in range(256)]) for channel in rgb))
        px,py=project(fx['x'],fx['y']);canvas=Image.new('RGB',scene.size);canvas.paste(layer,(px-width//2,py-height//2))
        scene=ImageChops.add(scene,canvas)
    d=ImageDraw.Draw(scene)
    phase='CHARGING' if age<1 else 'BLAST' if age<1.15 else 'AFTERGLOW' if age<1.4375 else 'READY'
    d.text((30*S,315*S),f'{phase}   {min(age,1.4375):.2f} sec',font=font,fill=(247,210,130))
    d.text((360*S,315*S),'3400 range   /   200 damage width   /   one impact',font=font,fill=(145,168,161))
    return scene.resize((W,H),Image.Resampling.LANCZOS)
e,u,state,cast,tick,clean=setup();cast();frames=[];stills={}
for i in range(47):
    age=i*.03125;frame=render(state,age);frames.append(frame)
    if i in [0,24,32,40]:stills[i]=frame.copy()
    tick()
frames+=([frames[-1]]*20)
frames[0].save(R/'FinalSpark-preview.gif',save_all=True,append_images=frames[1:],duration=32,loop=0,optimize=True)
contact=Image.new('RGB',(W*2,H*2))
for j,frame in enumerate(stills.values()):contact.paste(frame,((j%2)*W,(j//2)*H))
contact.save(R/'FinalSpark-preview.png')
delivery=R.parent/'Transfer/Lux_FinalSpark_v70';delivery.mkdir(exist_ok=True)
for name in ['FinalSpark-preview.gif','FinalSpark-preview.png']:shutil.copy2(R/name,delivery/name)
print('Saved offline animated sequence and contact sheet.')
