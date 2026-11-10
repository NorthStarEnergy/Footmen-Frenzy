from pathlib import Path
import sys,struct,shutil,json,hashlib
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src';S.mkdir(exist_ok=True)
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries
from validate_objdata import validate
from game_data import game_read,chunks
import objdata
base=W/'mundo-polish-v45/release/FF799X_Rx_Mundo_TF_Polish_v45a.w3x'
names=['war3map.w3u','war3mapSkin.w3u','war3map.imp','war3map.wts']
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
original={n:read_storm(h,n) for n in names};assert storm.SFileCloseArchive(h)
for n,data in original.items():(S/n).write_bytes(data)
def put(e,key,value,typ):
 m=next((m for m in e['mods'] if m['id']==key),None)
 if m:m.update(value=value,type=typ)
 else:e['mods'].append(dict(id=key,type=typ,value=value,end='00000000'))
found=False
for n in names[:2]:
 o=objdata.load(str(S/n))
 for t in o['tables']:
  for e in t:
   if (e['newId'] if e['newId']!='\0'*4 else e['oldId'])=='HTf1':
    put(e,'umdl','war3mapImported\\FlamingRaven.mdx',3)
    put(e,'usca',1.,1);put(e,'ussc',1.3,1)
    put(e,'uwal',275.,1);put(e,'urun',275.,1);found=True
 data=objdata.dump(o);validate(data,False);(S/n).write_bytes(data)
assert found
assets={'war3mapImported\\FlamingRaven.mdx':'FlamingRaven.mdx','TBSFRaven.blp':'TBSFRaven.blp'}
for dest,source in assets.items():
 p=S/dest;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((R/'assets'/source).read_bytes())
model=chunks((R/'assets/FlamingRaven.mdx').read_bytes());assert struct.unpack('<I',model['VERS'])[0]==800
textures=[]
for at in range(0,len(model['TEXS']),268):
 name=model['TEXS'][at+4:at+264].split(b'\0')[0].decode()
 if name:
  assert name in assets or game_read('war3.w3mod:'+name) or game_read('war3.w3mod:'+name.rsplit('.',1)[0]+'.dds'),name
  textures.append(name)
imp=original['war3map.imp'];version,count=struct.unpack_from('<II',imp);body=imp[8:]
for name in assets:
 assert name.encode()+b'\0' not in body
 body+=b'\r'+name.encode()+b'\0'
(S/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(assets))+body)
assert b'Mundo and Twisted Fate v45a' in original['war3map.wts']
(S/'war3map.wts').write_bytes(original['war3map.wts'].replace(b'Mundo and Twisted Fate v45a',b'Mundo and Twisted Fate v45b'))
names+=list(assets)
out=R/'release/FF799X_Rx_Mundo_TF_Raven_v45b.w3x';out.parent.mkdir(exist_ok=True);assert not out.exists();shutil.copy2(base,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n in names:assert storm.SFileAddFileEx(h,str(S/n),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h)
old,new=archive(base),archive(out);oe,ne=entries(old),entries(new);skip=set()
for n in names+['(listfile)','(attributes)','(signature)']:
 e=old.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in oe.items():
 if k not in skip:assert ne.get(k)==v,('Unrelated payload changed',k)
assert old.read_file('war3map.j')==new.read_file('war3map.j')
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in names:assert read_storm(h,n)==(S/n).read_bytes(),n
for n in ['war3map.w3a','war3mapSkin.w3a']:validate(read_storm(h,n),True)
assert storm.SFileCloseArchive(h)
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report=dict(output=str(out),sha256=sha,base=str(base),model='Flaming Raven by UgoUgo',textures_verified=textures,preserved_payloads=len(oe.keys()-skip),script='identical to verified v45a',live_test='pending')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
