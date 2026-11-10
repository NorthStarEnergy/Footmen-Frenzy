from pathlib import Path
import sys,io,json,re,struct,textwrap
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;W=R.parent;D=R/'icons'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c
from game_data import game_read
import objdata
strings=dict(re.findall(r'STRING (\d+)\s*\{\s*(.*?)\s*\}',(D/'war3map.wts').read_text(encoding='utf-8-sig'),re.S))
def fields(ext):
 out={}
 for t in objdata.load(str(D/('war3map.'+ext)))['tables']:
  for e in t:
   f={m['id']:m['value'] for m in e['mods'] if m.get('level',0)<=1}
   out[e['newId'] if e['newId']!='\0'*4 else e['oldId']]=f
 return out
units,abilities=fields('w3u'),fields('w3a')
def clean(v):
 v=strings.get(v[8:],v) if v.startswith('TRIGSTR_') else v
 return re.sub(r'\|c[0-9a-fA-F]{8}|\|r','',v)
h=c.c_void_p();assert storm.SFileOpenArchive(str(R/'release/FF799X_Rx_Veigar_Classic_v68.w3x'),0,0x100,c.byref(h))
def decode(raw):
 if raw[:4]==b'BLP1' and struct.unpack_from('<I',raw,4)[0]==1:
  _,depth,w,ht,enc,_=struct.unpack_from('<6I',raw,4);off=struct.unpack_from('<I',raw,28)[0];count=w*ht;idx=raw[off:off+count];alpha=raw[off+count:];pixels=[]
  for i,k in enumerate(idx):
   b,g,r,_=raw[156+k*4:160+k*4];a=255 if depth==0 else ((alpha[i*depth//8]>>(i*depth%8))&((1<<depth)-1))*255//((1<<depth)-1);pixels.append((r,g,b,a))
  im=Image.new('RGBA',(w,ht));im.putdata(pixels);return im
 return Image.open(io.BytesIO(raw)).convert('RGBA')
def extract(path):
 try:raw=read_storm(h,path);return decode(raw),'map'
 except (AssertionError,ValueError):pass
 for p in [path,path.rsplit('.',1)[0]+'.dds',path.rsplit('.',1)[0]+'.blp',path.rsplit('.',1)[0]+'.tga']:
  raw=game_read('war3.w3mod:'+p)
  if raw:
   try:return decode(raw),'Warcraft SD'
   except Exception:pass
 im=Image.new('RGBA',(64,64),'#333333');ImageDraw.Draw(im).text((6,24),'Missing',fill='white');return im,'Unresolved icon path'
groups=[('Guardian','H043',['A0DL','AFg1','ATfd','AZd1']),('Guldan','HOr1',['AOz1','AOz2','AOz3','AOz4']),('Gragas','HGr1',['AGr1','AGr2','AGr3','AGr4']),('Mundo','HMu1',['AMu2','AMu1','AMu3','AMu4','AMup']),('Twisted-Fate','HTf1',['ATf1','ATf2','ATf4','ATf5','ATf3','ATfg','ATfb','ATfc']),('Veigar','HVg1',['AVgq','AVgw','AVge','AVgr','AVgp']),('Demon-Knight','HDk1',['ADk1','ADk2','ADk3','ADk4'])]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',20)
manifest=[]
for group,hero,ids in groups:
 u=units[hero];rows=[]
 if u.get('uico'):rows.append((hero,'Hero portrait',u['uico']))
 else:
  rows.append((hero,'Hero portrait',units.get('Hblm',{}).get('uico',r'ReplaceableTextures\CommandButtons\BTNHeroBloodElfPrince.blp')))
 for aid in ids:
  f=abilities[aid];rows.append((aid,clean(f.get('anam',aid)),f['aart']))
 cols=min(6,len(rows));sheet=Image.new('RGB',(cols*172,52+((len(rows)+cols-1)//cols)*200),'#191c23');draw=ImageDraw.Draw(sheet)
 draw.text((12,12),group.replace('-',' ')+' - current v68'+(' (disabled hero)' if hero=='HDk1' else ''),font=title,fill='white')
 for i,(aid,label,path) in enumerate(rows):
  im,source=extract(path);im.save(D/(aid+'.png'));x=(i%cols)*172;y=52+(i//cols)*200
  sheet.paste(im.resize((128,128),Image.Resampling.NEAREST),(x+22,y),im.resize((128,128),Image.Resampling.NEAREST))
  for j,line in enumerate(textwrap.wrap(label,21)):draw.text((x+8,y+136+j*18),line,font=font,fill='white')
  manifest.append(dict(group=group,id=aid,label=label,icon=path,source=source,png=aid+'.png'))
 sheet.save(D/(group+'.png'))
assert storm.SFileCloseArchive(h)
(D/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'icons':len(manifest),'groups':[g[0] for g in groups]}))

