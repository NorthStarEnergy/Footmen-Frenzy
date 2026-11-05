from pathlib import Path
import sys,ast,struct,hashlib,shutil,json
from PIL import Image,ImageEnhance,ImageDraw
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries
from validate_objdata import validate
import objdata
ns={'Image':Image,'struct':struct};tree=ast.parse((W/'799x-backport/make_magic_textures.py').read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='blp'],type_ignores=[]),'blp','exec'),ns)
assets={}; mappings={'ATf1':'Fork','ATf2':'Choice','ATf3':'Green','ATf4':'Red','ATf5':'Gold','ATf6':'Green','ATf7':'Red','ATf8':'Gold'}
for name in ['Fork','Choice','Red','Gold','Green']:
 im=Image.open(R/'art'/f'{name}.png').convert('RGB');size=min(im.size);x=(im.width-size)//2;y=(im.height-size)//2;im=im.crop((x,y,x+size,y+size)).resize((64,64),Image.Resampling.LANCZOS).convert('RGBA');draw=ImageDraw.Draw(im);draw.rectangle((0,0,63,63),outline=(12,12,17,255),width=2);draw.rectangle((2,2,61,61),outline=(125,112,84,255),width=1);im.putalpha(255)
 for disabled in [False,True]:
  folder='CommandButtonsDisabled' if disabled else 'CommandButtons';filename=('DISBTN' if disabled else 'BTN')+'FFOrb'+name+'.blp';p=S/filename
  p.write_bytes(ns['blp'](ImageEnhance.Brightness(im).enhance(.38) if disabled else im));check=Image.open(p).convert('RGBA');assert check.size==(64,64) and p.read_bytes()[:4]==b'BLP1';check.save(S/(filename+'.png'));assets['ReplaceableTextures\\'+folder+'\\'+filename]=p
base=W/'tf-dice-v48/release/FF799X_Rx_TF_Guardian_Dice_v48.w3x';h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in ['war3map.w3a','war3mapSkin.w3a','war3map.imp']:(S/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
seen={}
for name in ['war3map.w3a','war3mapSkin.w3a']:
 o=objdata.load(str(S/name))
 for table in o['tables']:
  for e in table:
   code=e['newId'] if e['newId']!='\0'*4 else e['oldId']
   if code in mappings:
    for m in e['mods']:
     if m['id'] in ('aart','arar'):
      m['value']='ReplaceableTextures\\CommandButtons\\BTNFFOrb'+mappings[code]+'.blp';seen.setdefault(code,set()).add(m['id'])
 data=objdata.dump(o);validate(data,True);(S/name).write_bytes(data)
assert all(seen.get(code)=={'aart','arar'} for code in mappings),seen
raw=(S/'war3map.imp').read_bytes();version,count=struct.unpack_from('<II',raw);(S/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(assets))+raw[8:]+b''.join(b'\r'+n.encode()+b'\0' for n in assets))
payload={'war3map.w3a':S/'war3map.w3a','war3mapSkin.w3a':S/'war3mapSkin.w3a','war3map.imp':S/'war3map.imp',**assets}
out=R/'release/FF799X_Rx_TF_Guardian_OrbIcons_v49.w3x';shutil.copy2(base,out);h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
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
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n');rep={'output':str(out),'sha256':sha,'base':str(base),'untouched_entries':len(old.keys()-skip),'ability_icon_mapping':mappings,'checks':'BLP1 active and disabled icons decoded, ability data validated, archive readback passed','live_test':'pending'};(R/'verification.json').write_text(json.dumps(rep,indent=2));print(json.dumps(rep,indent=2))
