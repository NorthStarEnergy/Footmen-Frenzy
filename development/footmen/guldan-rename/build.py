from pathlib import Path
import sys,shutil,json,hashlib,copy
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries
import objdata
base=W/'799x-backport/release/FF799X_Rx_OriannaGuldan_v34.w3x'
O=R/'src';O.mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
files={};changes=[]
for name in ['war3map.w3u','war3mapSkin.w3u']:
 raw=read_storm(h,name);p=O/name;p.write_bytes(raw);d=objdata.load(str(p));before=copy.deepcopy(d)
 for table in d['tables']:
  for e in table:
   if e['newId']=='HOr1':
    for m in e['mods']:
     old=m['value']
     if m['id']=='unam':m['value']="Gul'dan"
     elif m['id']=='upro':m['value']='The Warlock'
     elif m['id']=='utip':m['value']="Hire Gul'dan"
     elif m['id'] in ['uawt','utpr']:m['value']="Revive Gul'dan"
     elif m['id']=='utub':m['value']=m['value'].replace('Orianna',"Gul'dan")
     if old!=m['value']:changes.append([name,m['id'],old,m['value']])
 if d!=before:p.write_bytes(objdata.dump(d));files[name]=p
raw=read_storm(h,'war3map.wts');updated=raw.replace(b'FF799X - Orianna Guldan v34',b'FF799X - Guldan v35')
# WTS contains display text, never model or sound import paths.
updated=updated.replace(b'Orianna',b"Gul'dan").replace(b'Lady of Clockwork',b"Gul'dan")
if updated!=raw:
 p=O/'war3map.wts';p.write_bytes(updated);files['war3map.wts']=p
assert storm.SFileCloseArchive(h)
assert len(changes)>=5,changes
out=W/'799x-backport/release/FF799X_Rx_Guldan_v35.w3x';shutil.copy2(base,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for name,p in files.items():assert storm.SFileAddFileEx(h,str(p),name.encode(),0x80000200,2,2)
assert storm.SFileCloseArchive(h)
before=archive(base);after=archive(out);a,b=entries(before),entries(after);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name,p in files.items():
 assert read_storm(h,name)==p.read_bytes()
 e=before.get_hash_table_entry(name);skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert storm.SFileCloseArchive(h)
for name in ['(listfile)','(attributes)','(signature)']:
 e=before.get_hash_table_entry(name)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in a.items():
 if k not in skip:assert b.get(k)==v
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report=dict(output=str(out),changes=changes,preserved_archive_entries=len(a.keys()-skip),sha256=sha,verification='Archive roundtrip passed; gameplay script unchanged')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
