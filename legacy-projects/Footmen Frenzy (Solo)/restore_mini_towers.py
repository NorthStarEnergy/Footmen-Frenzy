from pathlib import Path
import sys,re,json,struct
R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots')
O=Path(__file__).parent/'mini-tower-restore';O.mkdir(exist_ok=True)
sys.path.insert(0,str(Path(__file__).parent/'.audit-deps'))
import mpyq
def script(path):return mpyq.MPQArchive(str(path),listfile=False).read_file('war3map.j').decode('utf-8-sig')
old=script(R/'archive/final-v2-Mini Foots v2.w3x')
current=script(R/'release/Mini Foots v6.w3x')
assert current==(R/'src/war3map.j').read_text(encoding='utf-8-sig')
def towers(s):
    out=[]
    for i in range(12):
        body=re.search(r'function CreateBuildingsForPlayer'+str(i)+r' takes .*?\nendfunction',s,re.S).group()
        for m in re.finditer(r"BlzCreateUnitWithSkin\((p|Player\((\d+)\)), 'hwtw', ([^,]+), ([^,]+),",body):
            out.append({'owner':i if m[1]=='p' else int(m[2]),'x':float(m[3].replace(' ','')),'y':float(m[4].replace(' ',''))})
    return out
prior=towers(old);now=towers(current);assert len(prior)==len(now)==16
(O/'positions.json').write_text(json.dumps({'before':now,'restored':prior},indent=2))
# Render the actual terrain tiles and cliff heights with both tower layouts.
from PIL import Image,ImageDraw
d=(R/'base/files/war3map.w3e').read_bytes();off=13
n=struct.unpack_from('<i',d,off)[0];off+=4
tiles=[d[off+4*i:off+4*i+4].decode() for i in range(n)];off+=n*4
n=struct.unpack_from('<i',d,off)[0];off+=4+n*4
w,h,ox,oy=struct.unpack_from('<iiff',d,off);off+=16
im=Image.new('RGB',(w*12,h*12));draw=ImageDraw.Draw(im)
palette=['#6a7545','#8f825d','#abb085','#454b40','#92958b','#627e43','#ad9b78','#354f33','#c0ba95','#737b83','#8a654a','#c4b88c','#749076','#50585b','#96876b','#bdbbaa']
for y in range(h):
 for x in range(w):
  tile=d[off+(y*w+x)*((len(d)-off)//(w*h))+4]&15
  draw.rectangle((x*12,(h-1-y)*12,x*12+11,(h-1-y)*12+11),fill=palette[tile])
def pt(x,y):return ((x-ox)/128*12,(h-1-(y-oy)/128)*12)
for arr,col in [(now,'#ff5050'),(prior,'#00ffff')]:
 for t in arr:
  x,y=pt(t['x'],t['y']);draw.rectangle((x-5,y-5,x+5,y+5),outline=col,width=2)
draw.rectangle((0,0,410,32),fill='black');draw.text((7,8),'RED: current towers   CYAN: restored v2 edge pads',fill='white')
im.save(O/'terrain-positions.png')
print('Original edge positions:',prior)
print('Terrain tiles:',tiles)
patched=current
for i in range(12):
 pattern=r'function CreateBuildingsForPlayer'+str(i)+r' takes .*?\nendfunction'
 original=re.search(pattern,old,re.S).group()
 body=re.search(pattern,patched,re.S).group()
 coords=list(re.finditer(r"BlzCreateUnitWithSkin\((p|Player\((\d+)\)), 'hwtw', [^\n]+?\)",original))
 it=iter(coords)
 body=re.sub(r"BlzCreateUnitWithSkin\((p|Player\((\d+)\)), 'hwtw', [^\n]+?\)",lambda m:next(it).group(),body)
 patched=re.sub(pattern,lambda m:body,patched,count=1,flags=re.S)
assert towers(patched)==prior
patched=patched.replace('Mini Foots v6','Mini Foots v7')
(O/'war3map.j').write_text(patched,encoding='utf8',newline='\n')
for name in ['war3map.wts','war3map.w3i']:
 data=(R/'src'/name).read_bytes();assert b'Mini Foots v6' in data
 (O/name).write_bytes(data.replace(b'Mini Foots v6',b'Mini Foots v7'))
# Persist the edge coordinates in the source generator so later builds retain them.
builder=(R/'build_source.py').read_text()
start=builder.index('# Two equal tower pairs')
end=builder.index('towerused=',start)
mapping={slot:[(int(t['x']),int(t['y'])) for t in prior if t['owner']==slot] for slot in sorted({t['owner'] for t in prior})}
builder=builder[:start]+'# Restored original edge tower pads from Mini Foots v2.\ntowercoords='+repr(mapping)+'\n'+builder[end:]
(O/'build_source.py').write_text(builder.replace('Mini Foots v6','Mini Foots v7'),encoding='utf8')
for name in ['Pack-Map.ps1','verify.py','record_delivery.py','render_audit.py']:
 (O/name).write_text((R/name).read_text(encoding='utf-8-sig').replace('Mini Foots v6','Mini Foots v7'),encoding='utf8')

