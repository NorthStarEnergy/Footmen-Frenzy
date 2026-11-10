from pathlib import Path
import sys,json,hashlib,shutil,struct
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import archive,entries,functions,storm,read_storm,c
from validate_objdata import validate
manifest=json.loads((R/'changes.json').read_text());base=Path(manifest['base'])
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(base)==manifest['base_sha256']
assert json.loads((R/'checks.json').read_text())['passed']==19
assert json.loads((R/'mundo-checks.json').read_text())['passed']==65
assert json.loads((R/'resource-checks.json').read_text())['passed']==10
assert json.loads((R/'model-checks.json').read_text())['models']==21
for n,d in json.loads((R/'compiled-hashes.json').read_text()).items():assert digest(R/n)==d,('Stale compiler output',n)
for n in ['compiler.log','editor-compiler.log']:assert 'Parse successful:' in (R/n).read_text() and 'Parse failed' not in (R/n).read_text()
assert 'Success!' in (R/'jasshelper.log').read_text()
stage=R/'stage.w3x';shutil.copy2(base,stage);h=c.c_void_p();assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h))
changed=[]
for f in sorted((R/'src').rglob('*')):
 if not f.is_file():continue
 n=str(f.relative_to(R/'src')).replace('/','\\');assert storm.SFileAddFileEx(h,str(f),n.encode(),0x80000200,2,2),n;changed.append(n)
assert storm.SFileCloseArchive(h)
out=R/'release/FF799X_Rx_SoulHook_Mundo_v72_TEST.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(stage,out)
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint]
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
if archive(out).get_hash_table_entry('(attributes)'):assert storm.SFileRemoveFile(h,b'(attributes)',0)
assert storm.SFileCloseArchive(h)
ba,aa=archive(base),archive(out);before,after=entries(ba),entries(aa);allowed=set()
for n in changed+['(listfile)','(attributes)','(signature)']:
 for ar in [ba,aa]:
  e=ar.get_hash_table_entry(n)
  if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(after.get(k)==v for k,v in before.items() if k not in allowed),'Unrelated archive payload changed'
assert all(k in before or k in allowed for k in after),'Unexpected archive member'
bh=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,256,c.byref(bh));assert storm.SFileOpenArchive(str(out),0,256,c.byref(h))
for n in changed:assert read_storm(h,n)==(R/'src'/n.replace('\\','/')).read_bytes(),n
old=functions(read_storm(bh,'war3map.j').decode('utf-8-sig').replace('\r',''));new=functions(read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r',''))
assert set(old)<=set(new)
assert {n for n in old if old[n]!=new[n]}==set(manifest['changed_functions'])
assert set(new)-set(old)==set(manifest['new_functions'])
for n in ['war3map.w3a','war3map.w3u']:validate(read_storm(h,n),n.endswith('.w3a'))
for n in ['war3map.imp','war3map.wts','war3map.w3h']+[f'Spells\\Mundo\\Cloud{i}.mdx' for i in range(21)]:
 assert read_storm(bh,n)==read_storm(h,n),('Gas/UI payload changed',n)
imp=read_storm(h,'war3map.imp');pos=8;names=[v['path'] for v in json.loads((W/'size-audit-v50/archive-files.json').read_text())]
for _ in range(struct.unpack_from('<II',imp)[1]):
 flag=imp[pos];pos+=1;end=imp.index(0,pos);name=imp[pos:end].decode('latin1');pos=end+1
 names.append(name if flag in [10,13] else 'war3mapImported\\'+name)
assert pos==len(imp)
known=sorted(set(names)-{'(listfile)','(attributes)','(signature)'});known=[n for n in known if ba.get_hash_table_entry(n)]
for n in known:
 if n.lower() not in {x.lower() for x in changed}:assert read_storm(bh,n)==read_storm(h,n),n
for n,d in json.loads((W/'mundo-ui-merge/ui-preservation.json').read_text())['repaired_members_preserved'].items():assert hashlib.sha256(read_storm(h,n)).hexdigest()==d,n
assert storm.SFileCloseArchive(bh);assert storm.SFileCloseArchive(h)
report={'output':str(out),'sha256':digest(out),'base':str(base),'base_sha256':digest(base),'changed_payloads':changed,'changed_functions':manifest['changed_functions'],'new_functions':manifest['new_functions'],'verified_preserved_entries':sum(k not in allowed for k in before),'decoded_preserved_files':len(known),'soulhook_checks':19,'mundo_cloud_checks':65,'mundo_resource_checks':10,'gas_particle_models':21,'runtime_compiler':'passed','editor_compiler':'passed','engine_playtested':False,'installed_or_deployed':False}
(R/'verification.json').write_text(json.dumps(report,indent=2));out.with_suffix('.sha256').write_text(digest(out)+'  '+out.name+'\n')
print(json.dumps(report,indent=2))
