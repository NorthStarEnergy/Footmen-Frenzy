from pathlib import Path
import sys,ast,struct,hashlib,shutil,json
from PIL import Image,ImageEnhance
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries
import objdata
source=W/'tf-destiny-v46/BTNLoadedDice.png'
im=Image.open(source).convert('RGBA');im.putalpha(255)
ns={'Image':Image,'struct':struct};tree=ast.parse((W/'799x-backport/make_magic_textures.py').read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='blp'],type_ignores=[]),'blp','exec'),ns)
assets={}
for disable in [False,True]:
 folder='CommandButtonsDisabled' if disable else 'CommandButtons'; name=('DISBTN' if disable else 'BTN')+'FFLoadedDice.blp';p=S/name
 p.write_bytes(ns['blp'](ImageEnhance.Brightness(im).enhance(.4) if disable else im))
 check=Image.open(p).convert('RGBA');assert check.size==(64,64) and p.read_bytes()[:4]==b'BLP1';check.save(S/(name+'.png'))
 assets['ReplaceableTextures\\'+folder+'\\'+name]=p
base=W/'tf-guardian-v47/release/FF799X_Rx_TF_Guardian_v47.w3x';h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in ['war3map.w3a','war3mapSkin.w3a','war3map.imp']:(S/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
found=0
for name in ['war3map.w3a','war3mapSkin.w3a']:
 o=objdata.load(str(S/name))
 for table in o['tables']:
  for e in table:
   if e['newId']=='ATfg':
    for m in e['mods']:
     if m['id'] in ('aart','arar'):m['value']='ReplaceableTextures\\CommandButtons\\BTNFFLoadedDice.blp';found+=1
 (S/name).write_bytes(objdata.dump(o))
assert found>=2
raw=(S/'war3map.imp').read_bytes();version,count=struct.unpack_from('<II',raw)
(S/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(assets))+raw[8:]+b''.join(b'\r'+n.encode()+b'\0' for n in assets))
payload={'war3map.w3a':S/'war3map.w3a','war3mapSkin.w3a':S/'war3mapSkin.w3a','war3map.imp':S/'war3map.imp',**assets}
out=R/'release/FF799X_Rx_TF_Guardian_Dice_v48.w3x';shutil.copy2(base,out);h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n,p in payload.items():assert storm.SFileAddFileEx(h,str(p),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h);h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n,p in payload.items():assert read_storm(h,n)==p.read_bytes(),n
assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(out);old,new=entries(a),entries(b);skip=set()
for n in list(payload)+['(listfile)','(attributes)','(signature)']:
 e=a.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in old.items():
 if k not in skip:assert new.get(k)==v
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n');rep={'output':str(out),'sha256':sha,'base':str(base),'untouched_entries':len(old.keys()-skip),'icon':'BLP1 active and disabled, 64x64 with mipmaps; archive readback passed','live_test':'pending'};(R/'verification.json').write_text(json.dumps(rep,indent=2));print(json.dumps(rep,indent=2))
