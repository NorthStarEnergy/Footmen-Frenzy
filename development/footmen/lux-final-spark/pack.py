from pathlib import Path
import sys, json, hashlib, shutil, struct
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive, entries, functions, storm, read_storm, c
import objdata
manifest=json.loads((R/'changes.json').read_text());base=Path(manifest['base'])
checks=json.loads((R/'checks.json').read_text());assert checks['passed']>=73
for n,digest in json.loads((R/'compiled-hashes.json').read_text()).items():
    assert hashlib.sha256((R/n).read_bytes()).hexdigest()==digest,('Stale compilation',n)
for n in ['compiler.log','editor-compiler.log']:
    log=(R/n).read_text();assert 'Parse successful:' in log and 'Parse failed' not in log
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

# Preserve inherited encrypted archive members at their original offsets.
# Replacing source adds only about 2 MB; no compaction is necessary.
out=R/'release/FF799X_Rx_Lux_FinalSpark_v70.w3x';out.parent.mkdir(exist_ok=True)
shutil.copy2(stage,out)
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint]
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
if archive(out).get_hash_table_entry('(attributes)'):
    assert storm.SFileRemoveFile(h,b'(attributes)',0)
assert storm.SFileCloseArchive(h)

before_archive=archive(base);after_archive=archive(out)
before,after=entries(before_archive),entries(after_archive);allowed=set()
for name in changed+['(listfile)','(attributes)','(signature)']:
    for ar in [before_archive,after_archive]:
        e=ar.get_hash_table_entry(name)
        if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(after.get(k)==v for k,v in before.items() if k not in allowed),'Unrelated archive entry changed'
assert all(k in before or k in allowed for k in after),'Unexpected new archive entry'
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name in changed:assert read_storm(h,name)==(R/'src'/name.replace('\\','/')).read_bytes(),name
assert storm.SFileCloseArchive(h)

assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
baseline={n:read_storm(h,n) for n in ['war3map.j','war3map.w3a','war3map.w3u']}
assert storm.SFileCloseArchive(h)
oldfs=functions(baseline['war3map.j'].decode('utf-8-sig').replace('\r',''))
newfs=functions((R/'src/war3map.j').read_text(encoding='utf8'))
assert set(oldfs)<=set(newfs)
assert {n for n in oldfs if oldfs[n]!=newfs[n]}==set(manifest['changed_functions'])
assert set(newfs)-set(oldfs)==set(manifest['new_functions'])
object_counts={}
for name,rawid in [('war3map.w3a','ALxR'),('war3map.w3u','HLx1')]:
    original=R/('base-'+name);original.write_bytes(baseline[name])
    old=objdata.load(str(original));new=objdata.load(str(R/'src'/name))
    assert new['tables'][0]==old['tables'][0]
    assert new['tables'][1][:-1]==old['tables'][1]
    assert new['tables'][1][-1]['newId']==rawid
    object_counts[name]=sum(map(len,old['tables']))
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(output=str(out),sha256=digest(out),base=str(base),base_sha256=digest(base),changed_payloads=changed,preserved_archive_entries=sum(k not in allowed for k in before),existing_object_records_preserved=object_counts,changed_functions=manifest['changed_functions'],new_functions=manifest['new_functions'],runtime_compiler='passed',editor_compiler='passed',behavior_checks=checks['passed'],random_geometry_cases=checks['random_geometry_cases'],new_asset_bytes=sum(f.stat().st_size for f in (R/'src/Spells/Lux').iterdir()),engine_playtested=False,installed_or_deployed=False)
(R/'verification.json').write_text(json.dumps(report,indent=2));out.with_suffix('.sha256').write_text(digest(out)+'  '+out.name+'\n')
# Deliver a reviewable package without changing any shared latest release.
delivery=W/'Transfer/Lux_FinalSpark_v70';delivery.mkdir(exist_ok=True)
for f in [out,out.with_suffix('.sha256'),R/'verification.json',R/'checks.json',R/'README.md']:
    shutil.copy2(f,delivery/f.name)
print(json.dumps(report,indent=2))
