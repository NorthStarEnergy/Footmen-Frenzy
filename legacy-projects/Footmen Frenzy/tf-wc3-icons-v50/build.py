from pathlib import Path
import sys,ast,struct,hashlib,shutil,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src';sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries
ns={'Image':Image,'struct':struct};tree=ast.parse((W/'799x-backport/make_magic_textures.py').read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='blp'],type_ignores=[]),'blp','exec'),ns)
standard=W/'799x-backport/tools/button-manager/Button Manager/standard';templates={False:Image.open(standard/'bm_btn.tga').convert('RGB'),True:Image.open(standard/'bm_disbtn.tga').convert('RGB')};assert all(im.size==(64,64) for im in templates.values())
assets={};preview=Image.new('RGB',(6*128,2*128),'#121212')
for i,name in enumerate(['Fork','Choice','Red','Gold','Green','Dice']):
 src=(W/'mundo-polish-v45/assets/loaded-dice.png') if name=='Dice' else (W/'tf-orb-icons-v49/art'/f'{name}.png')
 im=Image.open(src).convert('RGB');size=min(im.size);x=(im.width-size)//2;y=(im.height-size)//2;im=im.crop((x,y,x+size,y+size)).resize((64,64),Image.Resampling.LANCZOS)
 for disabled in [False,True]:
  folder='CommandButtonsDisabled' if disabled else 'CommandButtons'; suffix='FFLoadedDice' if name=='Dice' else 'FFOrb'+name;filename=('DISBTN' if disabled else 'BTN')+suffix+'.blp';p=S/filename
  out=Image.new('RGBA',(64,64));out.putdata([tuple(round(v*b[0]/255) for v in a)+(255,) if b[0]==b[1]==b[2] else b+(255,) for a,b in zip(im.getdata(),templates[disabled].getdata())]);p.write_bytes(ns['blp'](out));decoded=Image.open(p).convert('RGBA');assert decoded.size==(64,64) and decoded.getchannel('A').getextrema()==(255,255);decoded.save(S/(filename+'.png'));assets['ReplaceableTextures\\'+folder+'\\'+filename]=p;preview.paste(decoded.convert('RGB').resize((128,128),Image.Resampling.NEAREST),(i*128,128 if disabled else 0))
preview.save(R/'preview.png')
base=W/'tf-orb-icons-v49/release/FF799X_Rx_TF_Guardian_OrbIcons_v49.w3x';out=R/'release/FF799X_Rx_TF_Guardian_WC3Icons_v50.w3x';shutil.copy2(base,out);h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n,p in assets.items():assert storm.SFileAddFileEx(h,str(p),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h);h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n,p in assets.items():assert read_storm(h,n)==p.read_bytes(),n
assert storm.SFileCloseArchive(h);a,b=archive(base),archive(out);old,new=entries(a),entries(b);skip=set()
for n in list(assets)+['(listfile)','(attributes)','(signature)']:
 e=a.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in old.items():
 if k not in skip:assert new.get(k)==v
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n');report={'output':str(out),'sha256':sha,'base':str(base),'preserved_entries':len(old.keys()-skip),'buttons':'Standard Warcraft BTN and DISBTN templates; opaque BLP1 with mipmaps','live_test':'pending'};(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
