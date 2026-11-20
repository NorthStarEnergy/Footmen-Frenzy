from pathlib import Path
import hashlib,json,shutil,struct,sys
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
import objdata
manifest=json.loads((R/'changes.json').read_text());base=Path(manifest['base']);checks=json.loads((R/'checks.json').read_text());assert checks['passed']==18
for log in ['compiler.log','editor-compiler.log']:
 assert 'Parse successful:' in (R/log).read_text() and 'Parse failed' not in (R/log).read_text()
assert 'Success!' in (R/'jasshelper.log').read_text()
stage=R/'stage.w3x';shutil.copy2(base,stage);h=c.c_void_p();assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h));changed=[]
for f in sorted((R/'src').iterdir()):
 assert f.is_file();assert storm.SFileAddFileEx(h,str(f),f.name.encode(),0x80000200,2,2);changed.append(f.name)
assert storm.SFileCloseArchive(h)
out=R/'release/FF799X_Rx_Mundo_HealthKit_Test.w3x';out.parent.mkdir(exist_ok=True)
shutil.copy2(stage,out)
beforearchive=archive(base);before,after=entries(beforearchive),entries(archive(out));skip=set()
for n in changed+['(attributes)','(listfile)','(signature)']:
 e=beforearchive.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in before.items():
 if k not in skip:assert after.get(k)==v,('changed unexpected payload',k)
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in changed:assert read_storm(h,n)==(R/'src'/n).read_bytes()
assert storm.SFileCloseArchive(h)
assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
oldfs=functions(read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r',''));newfs=functions((R/'src/war3map.j').read_text(encoding='utf8'))
assert {n for n in oldfs if oldfs[n]!=newfs[n]}==set(manifest['changed_functions'])-{'MU_ZeroResources'}
assert set(newfs)-set(oldfs)=={'MU_ZeroResources'}
for name in ['war3map.w3a','war3map.w3u']:
 p=R/('before-'+name);p.write_bytes(read_storm(h,name));old=objdata.load(str(p));new=objdata.load(str(R/'src'/name))
 assert old['tables'][0]==new['tables'][0]
 if name.endswith('w3a'):assert new['tables'][1][:len(old['tables'][1])]==old['tables'][1] and len(new['tables'][1])==len(old['tables'][1])+20
 else:
  for a,b in zip(old['tables'][1],new['tables'][1]):
   if a['newId']!='HMu1':assert a==b
assert storm.SFileCloseArchive(h)
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report={'output':str(out),'sha256':sha,'base':str(base),'changed_files':changed,'preserved_archive_entries':len(before.keys()-skip),'runtime_jass':'passed','editor_jasshelper_and_jass':'passed','mocked_jass_checks':checks['passed'],'engine_playtest':'pending','integration':'standalone test based on v68; not merged with parallel Lux or other work','installed':False};(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
