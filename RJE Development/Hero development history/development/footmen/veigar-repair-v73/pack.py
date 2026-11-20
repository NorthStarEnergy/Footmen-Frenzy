from pathlib import Path
import sys,json,hashlib,shutil,struct
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import archive,entries,functions,storm,read_storm,c
from validate_objdata import validate
import objdata
m=json.loads((R/'changes.json').read_text());base=Path(m['base']);digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(base)==m['base_sha256'];assert json.loads((R/'checks.json').read_text())['passed']==57
for n,d in json.loads((R/'compiled-hashes.json').read_text()).items():assert digest(R/n)==d,('Stale compiler output',n)
for n in ['compiler.log','editor-compiler.log']:assert 'Parse successful:' in (R/n).read_text() and 'Parse failed' not in (R/n).read_text()
assert 'Success!' in (R/'jasshelper.log').read_text()
stage=R/'stage.w3x';shutil.copy2(base,stage);h=c.c_void_p();assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h));changed=[]
for f in sorted((R/'src').rglob('*')):
 if f.is_file():
  n=str(f.relative_to(R/'src')).replace('/','\\');assert storm.SFileAddFileEx(h,str(f),n.encode(),0x80000200,2,2),n;changed.append(n)
assert storm.SFileCloseArchive(h)
out=R/'release/FF799X_Rx_Veigar_Cage_Range_v73_TEST.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(stage,out)
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint];assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
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
assert set(old)==set(new) and {n for n in old if old[n]!=new[n]}==set(m['changed_functions'])
oldobj=objdata.load(str(R/'before-war3map.w3a'));newobj=objdata.load(str(R/'src/war3map.w3a'))
assert [len(x) for x in oldobj['tables']]==[len(x) for x in newobj['tables']]
for a,b in zip(sum(oldobj['tables'],[]),sum(newobj['tables'],[])):
 if a['newId'] not in ['AVge','AVgw','AVgq','AVgr','AVgs']:assert a==b,a['newId']
validate(read_storm(h,'war3map.w3a'),True)
for n in ['war3map.imp','war3map.wts','war3map.w3h','war3map.w3u']+[f'Spells\\Mundo\\Cloud{i}.mdx' for i in range(21)]:assert read_storm(bh,n)==read_storm(h,n),n
imp=read_storm(h,'war3map.imp');pos=8;names=[v['path'] for v in json.loads((W/'size-audit-v50/archive-files.json').read_text())]
for _ in range(struct.unpack_from('<II',imp)[1]):
 flag=imp[pos];pos+=1;end=imp.index(0,pos);n=imp[pos:end].decode('latin1');pos=end+1;names.append(n if flag in [10,13] else 'war3mapImported\\'+n)
assert pos==len(imp);known=sorted(set(names)-{'(listfile)','(attributes)','(signature)'});known=[n for n in known if ba.get_hash_table_entry(n)]
for n in known:
 if n.lower() not in {x.lower() for x in changed}:assert read_storm(bh,n)==read_storm(h,n),n
for n,d in json.loads((W/'mundo-ui-merge/ui-preservation.json').read_text())['repaired_members_preserved'].items():assert hashlib.sha256(read_storm(h,n)).hexdigest()==d,n
assert storm.SFileCloseArchive(bh);assert storm.SFileCloseArchive(h)
report={'output':str(out),'sha256':digest(out),'base':str(base),'base_sha256':digest(base),'changed_payloads':changed,'changed_functions':m['changed_functions'],'verified_preserved_entries':sum(k not in allowed for k in before),'decoded_preserved_files':len(known),'veigar_checks':57,'runtime_compiler':'passed','editor_compiler':'passed','engine_playtested':False,'installed_or_deployed':False}
(R/'verification.json').write_text(json.dumps(report,indent=2));out.with_suffix('.sha256').write_text(digest(out)+'  '+out.name+'\n');print(json.dumps(report,indent=2))
