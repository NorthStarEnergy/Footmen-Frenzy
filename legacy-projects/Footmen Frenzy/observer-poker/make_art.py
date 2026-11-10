"""Deterministic original card/chip artwork, packaged as Warcraft BLP1 textures."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import struct,math,io,json
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'src/PokerUI';OUT.mkdir(parents=True,exist_ok=True)
FONT='C:/Windows/Fonts/segoeuib.ttf'
SYMBOL='C:/Windows/Fonts/seguisym.ttf'
def font(n,symbol=False):return ImageFont.truetype(SYMBOL if symbol else FONT,n)
def blp(image):
    width,height=image.size;image=image.convert('RGBA')
    pal=image.convert('RGB').quantize(colors=256);colors=pal.getpalette();colors += [0]*(768-len(colors))
    palette=b''.join(bytes([colors[i+2],colors[i+1],colors[i],255]) for i in range(0,768,3))
    levels=[]
    while True:
        levels.append(image.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).tobytes()+image.getchannel('A').tobytes())
        if image.size==(1,1):break
        image=image.resize((max(1,image.width//2),max(1,image.height//2)),Image.Resampling.LANCZOS)
    offsets=[];at=1180
    for level in levels:offsets.append(at);at+=len(level)
    return b'BLP1'+struct.pack('<6I',1,8,width,height,5,0)+struct.pack('<16I',*(offsets+[0]*(16-len(offsets))))+struct.pack('<16I',*([len(l) for l in levels]+[0]*(16-len(levels))))+palette+b''.join(levels)
art={}
def save(name,im):
    raw=blp(im);(OUT/(name+'.blp')).write_bytes(raw)
    # Pillow's BLP1 reader incorrectly reads palette alpha instead of the separate
    # alpha plane. Decode the actual BLP1 layout for preview/alpha verification.
    w,h=struct.unpack_from('<II',raw,12);offset=struct.unpack_from('<I',raw,28)[0]
    indices=raw[offset:offset+w*h];alpha=raw[offset+w*h:offset+2*w*h]
    palette=raw[156:1180]
    pixels=b''.join(bytes((palette[c*4+2],palette[c*4+1],palette[c*4],a)) for c,a in zip(indices,alpha))
    decoded=Image.frombytes('RGBA',(w,h),pixels)
    assert decoded.size==im.size and decoded.getchannel('A').tobytes()==im.getchannel('A').tobytes()
    art[name]=decoded
for suit,symbol in enumerate(['♣','♦','♥','♠']):
    for rank,label in enumerate(['2','3','4','5','6','7','8','9','10','J','Q','K','A']):
        im=Image.new('RGBA',(256,512));d=ImageDraw.Draw(im)
        d.rounded_rectangle((4,4,251,507),radius=22,fill='#fffdf6',outline='#c9bfa6',width=5)
        color='#bd2339' if suit in [1,2] else '#172738'
        d.text((20,5),label,font=font(88 if label!='10' else 76),fill=color)
        d.text((27,101),symbol,font=font(68,True),fill=color)
        d.text((128,255),symbol,font=font(163,True),fill=color,anchor='mm')
        # Opposite corner also reads correctly when viewed upside-down.
        corner=Image.new('RGBA',(115,185));cd=ImageDraw.Draw(corner)
        cd.text((5,0),label,font=font(76 if label!='10' else 65),fill=color)
        cd.text((10,87),symbol,font=font(62,True),fill=color)
        im.alpha_composite(corner.rotate(180),(133,315))
        save('card'+str(suit*13+rank),im)
im=Image.new('RGBA',(256,512));d=ImageDraw.Draw(im)
d.rounded_rectangle((4,4,251,507),22,fill='#f4eee0',outline='#c9bfa6',width=5)
d.rounded_rectangle((17,18,238,493),14,fill='#153f69',outline='#bd9c53',width=4)
for y in range(32,485,25):
    for x in range(30,235,25):d.polygon([(x,y-7),(x+7,y),(x,y+7),(x-7,y)],fill='#285780')
d.ellipse((69,197,187,315),fill='#103052',outline='#d8b968',width=5)
d.text((128,252),'♠',font=font(80,True),fill='#e7c875',anchor='mm')
save('back',im)
im=Image.new('RGBA',(256,512));d=ImageDraw.Draw(im)
d.rounded_rectangle((4,4,251,507),22,fill=(5,35,32,110),outline=(157,200,173,90),width=5)
save('empty',im)
for count in range(1,5):
    im=Image.new('RGBA',(256,128));d=ImageDraw.Draw(im)
    for col in range(count):
        x=12+col*45;y=82-col%2*12
        for layer in range(3+col):
            yy=y-layer*8
            d.ellipse((x,yy,x+85,yy+30),fill=['#be3444','#315db8','#35a07a','#aa7bba'][col],outline='#102332',width=3)
            for dx in [12,40,67]:d.line((x+dx,yy+3,x+dx+4,yy+9),fill='#fff2db',width=5)
            d.ellipse((x+19,yy+6,x+66,yy+24),outline='#eadab4',width=2)
    save('chips'+str(count),im)
im=Image.new('RGBA',(128,128));d=ImageDraw.Draw(im)
d.ellipse((5,5,123,123),fill='#fff3ce',outline='#b99950',width=6)
d.text((64,60),'D',font=font(72),fill='#27323e',anchor='mm');save('dealer',im)
im=Image.new('RGBA',(1024,1024));d=ImageDraw.Draw(im)
d.rounded_rectangle((4,4,1019,1019),40,fill='#101d29',outline='#b19b64',width=4)
d.rounded_rectangle((24,110,1000,840),290,fill='#302820',outline='#625442',width=12)
d.rounded_rectangle((49,140,975,809),260,fill='#123e36',outline='#9a8250',width=4)
d.rounded_rectangle((68,158,956,790),245,outline='#2c6456',width=3)
save('table',im)
# Offline composition from the exact shipped textures and runtime coordinates.
W,H=1400,960
preview=art['table'].resize((W,H),Image.Resampling.LANCZOS);draw=ImageDraw.Draw(preview)
def xy(x,y):return round(x/.70*W),round(y/.48*H)
def texture(name,x,y,w,h):preview.alpha_composite(art[name].resize(xy(w,h),Image.Resampling.LANCZOS),xy(x,y))
def text(t,x,y,size=23,color='#fff6dd'):draw.text(xy(x,y),t,font=font(size),fill=color)
text('FOOTMEN  /  OBSERVER POKER',.025,.018,29,'#e7cb88')
text('Hand 7  |  FLOP  |  Blinds 5 / 10',.025,.043,18,'#a8c1ba')
text('COMPUTER',.08,.085);text('480 chips',.08,.105,29)
texture('back',.285,.067,.058,.084);texture('back',.351,.067,.058,.084)
texture('chips3',.46,.09,.075,.045);texture('dealer',.245,.095,.022,.022)
texture('chips2',.275,.158,.052,.026);text('POT  60',.34,.16,25,'#f3d079')
for i,c in enumerate([25,36,9,None,None]):texture('empty' if c is None else 'card'+str(c),.187+i*.066,.196,.06,.086)
texture('card12',.285,.305,.06,.087);texture('card38',.353,.305,.06,.087)
text('YOU',.08,.315,24,'#f3d079');text('460 chips',.08,.335,29);texture('chips3',.46,.325,.075,.045)
text('YOUR TURN  •  24s',.46,.298,22,'#f3d079');text('To call: 20',.46,.369,21)
text('Computer raises to 40.',.025,.405,21)
for x,width,label in [(.025,.105,'Fold'),(.135,.12,'Call 20'),(.26,.12,'Raise to 60'),(.385,.13,'All-in 480'),(.52,.155,'Next hand')]:
    a,b=xy(x,.439);w,h=xy(width,.029);draw.rounded_rectangle((a,b,a+w,b+h),7,fill='#244b49',outline='#9d8e65',width=2);draw.text((a+w/2,b+h/2),label,font=font(22),anchor='mm',fill='#fff3d5')
preview.save(ROOT/'ui-preview.png')
# Deck contact sheet: visible typography/suit QA for every texture.
sheet=Image.new('RGB',(13*100,4*150),'#192833')
for i in range(52):sheet.paste(art['card'+str(i)].resize((96,144)),((i%13)*100,(i//13)*150),art['card'+str(i)].resize((96,144)))
sheet.save(ROOT/'deck-preview.png')
(ROOT/'art-verification.json').write_text(json.dumps(dict(textures=len(art),cards=52,format='BLP1 paletted with alpha and full mipmaps',decoded_all=True),indent=2))
print('Generated and decoded',len(art),'BLP textures plus offline previews.')
