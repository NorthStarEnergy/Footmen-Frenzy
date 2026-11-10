from pathlib import Path
import sys,copy,ast,struct
from PIL import Image
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src';sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
from validate_objdata import validate
import objdata
base=W/'tf-wc3-icons-v50/release/FF799X_Rx_TF_Guardian_WC3Icons_v50.w3x';h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for n in ['war3map.j','war3map.w3u','war3map.imp']:(S/n).write_bytes(read_storm(h,n))
assert storm.SFileCloseArchive(h)
s=(S/'war3map.j').read_text(encoding='utf-8-sig');f=functions(s)['TFP_wildCards___setCardRandHue'];new='''function TFP_wildCards___setCardRandHue takes unit u returns nothing
    call SetUnitScale(u,1.0,1.0,1.0)
    call SetUnitVertexColor(u,130,105,255,255)
endfunction''';s=s.replace(f,new,1)
f=functions(s)['TFP_wildCards___c'];assert f.count('TFP_tfConsts_CARD_DUMMY_ID')==3;s=s.replace(f,f.replace('TFP_tfConsts_CARD_DUMMY_ID',"'htz1'"),1)
(S/'war3map.j').write_text(s,encoding='utf8')
o=objdata.load(str(S/'war3map.w3u'));es={e['newId']:e for t in o['tables'] for e in t};assert 'htz1' not in es;u=copy.deepcopy(es['htf1']);u['newId']='htz1'
for m in u['mods']:
 m['end']='68747a31'
 if m['id']=='umdl':m['value']='war3mapImported\\TFWildOrb.mdx'
 if m['id']=='unam':m['value']='Wild Orb Projectile (Dummy)'
o['tables'][1].append(u);raw=objdata.dump(o);validate(raw,False);(S/'war3map.w3u').write_bytes(raw)
imp=(S/'war3map.imp').read_bytes();v,count=struct.unpack_from('<II',imp);newpath='war3mapImported\\TFWildOrb.mdx';(S/'war3map.imp').write_bytes(struct.pack('<II',v,count+1)+imp[8:]+b'\r'+newpath.encode()+b'\0')
tree=ast.parse((W/'799x-backport/make_magic_textures.py').read_text());ns={'Image':Image,'struct':struct};exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='blp'],type_ignores=[]),'blp','exec'),ns)
templates={False:Image.open(W/'799x-backport/tools/button-manager/Button Manager/standard/bm_btn.tga').convert('RGB'),True:Image.open(W/'799x-backport/tools/button-manager/Button Manager/standard/bm_disbtn.tga').convert('RGB')};preview=Image.new('RGB',(256,256))
for index,name in enumerate(['Fork','Choice']):
 im=Image.open(R/'art'/('Choice-light.png' if name=='Choice' else 'Fork.png')).convert('RGB');size=min(im.size);x=(im.width-size)//2;y=(im.height-size)//2;im=im.crop((x,y,x+size,y+size)).resize((64,64),Image.Resampling.LANCZOS)
 for disabled in [False,True]:
  filename=('DISBTN' if disabled else 'BTN')+'FFOrb'+name+'.blp';p=S/filename;out=Image.new('RGBA',(64,64));out.putdata([tuple(round(v*b[0]/255) for v in a)+(255,) if b[0]==b[1]==b[2] else b+(255,) for a,b in zip(im.getdata(),templates[disabled].getdata())]);p.write_bytes(ns['blp'](out));dec=Image.open(p).convert('RGBA');assert dec.size==(64,64) and dec.getchannel('A').getextrema()==(255,255);preview.paste(dec.convert('RGB').resize((128,128),Image.Resampling.NEAREST),(index*128,128 if disabled else 0))
preview.save(R/'preview.png');print('Prepared icons and dedicated Z projectile')

