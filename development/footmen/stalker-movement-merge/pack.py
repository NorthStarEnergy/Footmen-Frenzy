from pathlib import Path
import sys,json,hashlib,shutil,copy,struct
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
from validate_objdata import validate
import objdata
manifest=json.loads((R/'changes.json').read_text());base=Path(manifest['base'])
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(base)==manifest['base_sha256'],'Baseline changed during build'
checks=json.loads((R/'checks.json').read_text());assert checks['passed']==54
for n,d in json.loads((R/'compiled-hashes.json').read_text()).items():assert digest(R/n)==d,('Stale compiler output',n)
for n in ['compiler.log','editor-compiler.log']:assert 'Parse successful:' in (R/n).read_text() and 'Parse failed' not in (R/n).read_text()
assert 'Success!' in (R/'jasshelper.log').read_text()
stage=R/'stage.w3x';shutil.copy2(base,stage)
h=c.c_void_p();assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h))
changed=[]
for f in sorted((R/'src').rglob('*')):
    if not f.is_file():continue
    name=str(f.relative_to(R/'src')).replace('/','\\')
    assert storm.SFileAddFileEx(h,str(f),name.encode(),0x80000200,2,2),name
    changed.append(name)
assert storm.SFileCloseArchive(h)
out=R/'release/FF799X_Rx_UI_Mundo_Stalker_Fixed_Test.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(stage,out)
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint]
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
if archive(out).get_hash_table_entry('(attributes)'):assert storm.SFileRemoveFile(h,b'(attributes)',0)
assert storm.SFileCloseArchive(h)
ba=archive(base);aa=archive(out);before,after=entries(ba),entries(aa);allowed=set()
for name in changed+['(listfile)','(attributes)','(signature)']:
    for ar in [ba,aa]:
        e=ar.get_hash_table_entry(name)
        if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(after.get(k)==v for k,v in before.items() if k not in allowed),'Unrelated archive payload changed'
assert all(k in before or k in allowed for k in after),'Unexpected archive member'
bh=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,256,c.byref(bh))
assert storm.SFileOpenArchive(str(out),0,256,c.byref(h))
for name in changed:assert read_storm(h,name)==(R/'src'/name.replace('\\','/')).read_bytes(),name
baseline=read_storm(bh,'war3map.j').decode('utf-8-sig').replace('\r','');runtime=(R/'src/war3map.j').read_text(encoding='utf8')
oldfs=functions(baseline);newfs=functions(runtime)
assert set(oldfs)<=set(newfs)
assert {n for n in oldfs if oldfs[n]!=newfs[n]}==set(manifest['changed_functions'])
assert set(newfs)-set(oldfs)==set(manifest['new_functions'])
module=functions((R/'stalker.j').read_text())
for n,f in module.items():assert newfs[n]==f,n
assert read_storm(bh,'war3map.w3u')==(R/'before-war3map.w3u').read_bytes()
old=objdata.load(str(R/'before-war3map.w3u'));new=objdata.load(str(R/'src/war3map.w3u'))
expected=copy.deepcopy(old)
unit=next(e for t in expected['tables'] for e in t if e['newId']=='nStk')
next(m for m in unit['mods'] if m['id']=='ucol')['value']=16.0
assert new==expected,'Unexpected object change'
object_count=validate((R/'src/war3map.w3u').read_bytes(),False)
names=[v['path'] for v in json.loads((W/'size-audit-v50/archive-files.json').read_text())]
imp=read_storm(bh,'war3map.imp');pos=8
for _ in range(struct.unpack_from('<II',imp)[1]):
    flag=imp[pos];pos+=1;end=imp.index(0,pos);name=imp[pos:end].decode('latin1');pos=end+1
    names.append(name if flag in [10,13] else 'war3mapImported\\'+name)
names+=['war3map.j','war3map.wct','war3map.wts','war3map.w3a','war3map.w3u','war3map.w3h','war3map.imp','FF_MAINTENANCE.md']
known=sorted(set(names)-{'(listfile)','(attributes)','(signature)'})
known=[n for n in known if ba.get_hash_table_entry(n)]
changed_lower={n.lower() for n in changed};decoded=0
for name in known:
    prior=read_storm(bh,name);actual=read_storm(h,name);decoded+=1
    if name.lower() not in changed_lower:assert actual==prior,('Unrelated decoded payload changed',name)
ui=json.loads((W/'mundo-ui-merge/ui-preservation.json').read_text())['repaired_members_preserved']
for name,d in ui.items():assert hashlib.sha256(read_storm(h,name)).hexdigest()==d,('UI repair lost',name)
assert storm.SFileCloseArchive(bh);assert storm.SFileCloseArchive(h)
report=dict(output=str(out),sha256=digest(out),base=str(base),base_sha256=digest(base),changed_payloads=changed,changed_functions=manifest['changed_functions'],new_functions=manifest['new_functions'],changed_unit_fields=manifest['changed_unit_fields'],preserved_archive_entries=sum(k not in allowed for k in before),decoded_files=decoded,existing_unit_records=object_count,ui_members_verified=len(ui),all_non_stalker_functions_unchanged=True,runtime_editor_synchronized=True,runtime_compiler='passed',editor_compiler='passed',stalker_behavior_checks=checks['passed'],formation_cases=36,random_cases=checks['random_cases'],engine_playtested=False,installed_or_deployed=False)
(R/'verification.json').write_text(json.dumps(report,indent=2));out.with_suffix('.sha256').write_text(digest(out)+'  '+out.name+'\n')
delivery=W/'Transfer/UI_Mundo_Stalker_Fixed';delivery.mkdir(exist_ok=True)
for f in [out,out.with_suffix('.sha256'),R/'README.md',R/'verification.json',R/'checks.json',R/'changes.json']:shutil.copy2(f,delivery/f.name)
source=delivery/'developer-source';source.mkdir(exist_ok=True)
for name in ['stalker.j','prepare.py','checks.py','compile.py','pack.py']:shutil.copy2(R/name,source/name)
print(json.dumps(report,indent=2))
