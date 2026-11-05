from pathlib import Path
import sys,json,hashlib,shutil
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
import objdata
manifest=json.loads((R/'changes.json').read_text());base=Path(manifest['base'])
checks=json.loads((R/'checks.json').read_text());assert checks['passed']>=51
for n,digest in json.loads((R/'compiled-hashes.json').read_text()).items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==digest,('Stale compiler output',n)
for n in ['compiler.log','editor-compiler.log']:assert 'Parse successful:' in (R/n).read_text() and 'Parse failed' not in (R/n).read_text()
assert 'Success!' in (R/'jasshelper.log').read_text()
assert (R/'object-checks.json').exists() and (R/'native-checks.json').exists() and (R/'asset-validation.json').exists()
stage=R/'stage.w3x';shutil.copy2(base,stage)
h=c.c_void_p();assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h))
changed=[]
for f in sorted((R/'src').rglob('*')):
    if not f.is_file():continue
    name=str(f.relative_to(R/'src')).replace('/','\\')
    assert storm.SFileAddFileEx(h,str(f),name.encode(),0x80000200,2,2),name
    changed.append(name)
assert storm.SFileCloseArchive(h)
out=R/'release/FF799X_Rx_Stalker_v71.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(stage,out)
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint]
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
if archive(out).get_hash_table_entry('(attributes)'):assert storm.SFileRemoveFile(h,b'(attributes)',0)
assert storm.SFileCloseArchive(h)
before_archive=archive(base);after_archive=archive(out)
before,after=entries(before_archive),entries(after_archive);allowed=set()
for name in changed+['(listfile)','(attributes)','(signature)']:
    for ar in [before_archive,after_archive]:
        e=ar.get_hash_table_entry(name)
        if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(after.get(k)==v for k,v in before.items() if k not in allowed),'Unrelated archive payload changed'
assert all(k in before or k in allowed for k in after),'Unexpected new archive entry'
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name in changed:assert read_storm(h,name)==(R/'src'/name.replace('\\','/')).read_bytes(),name
for name in manifest['imports']:assert read_storm(h,name),name
assert storm.SFileCloseArchive(h)
assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
baseline={n:read_storm(h,n) for n in ['war3map.j','war3map.w3a','war3map.w3u']};assert storm.SFileCloseArchive(h)
oldfs=functions(baseline['war3map.j'].decode('utf-8-sig').replace('\r',''));newfs=functions((R/'src/war3map.j').read_text(encoding='utf8'))
assert set(oldfs)<=set(newfs)
assert {n for n in oldfs if oldfs[n]!=newfs[n]}==set(manifest['changed_functions'])
assert set(newfs)-set(oldfs)==set(manifest['new_functions'])
object_counts={}
for name,added in [('war3map.w3a',['AStB','AStS']),('war3map.w3u',['nStk'])]:
    old=objdata.load(str(R/('base-'+name)));new=objdata.load(str(R/'src'/name))
    assert new['tables'][0]==old['tables'][0]
    assert new['tables'][1][:-len(added)]==old['tables'][1]
    assert [e['newId'] for e in new['tables'][1][-len(added):]]==added
    object_counts[name]=sum(map(len,old['tables']))
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(output=str(out),sha256=digest(out),base=str(base),base_sha256=digest(base),changed_payloads=changed,preserved_archive_entries=sum(k not in allowed for k in before),existing_object_records_preserved=object_counts,changed_functions=manifest['changed_functions'],new_functions=manifest['new_functions'],runtime_compiler='passed',editor_compiler='passed',behavior_checks=checks['passed'],random_cases=checks['random_cases'],asset_bytes=sum(f.stat().st_size for f in (R/'src').rglob('*') if f.is_file() and f.suffix in ['.mdx','.blp']),engine_playtested=False,installed_or_deployed=False)
(R/'verification.json').write_text(json.dumps(report,indent=2));out.with_suffix('.sha256').write_text(digest(out)+'  '+out.name+'\n')
delivery=W/'Transfer/Stalker_v71';delivery.mkdir(exist_ok=True)
for f in [out,out.with_suffix('.sha256'),R/'verification.json',R/'checks.json',R/'asset-checks.json',R/'asset-validation.json',R/'native-checks.json',R/'object-checks.json',R/'model-inspection.json',R/'README.md',R/'Stalker-model-preview.png']:
    shutil.copy2(f,delivery/f.name)
source=delivery/'developer-source';source.mkdir(exist_ok=True)
for name in ['stalker.j','globals.j','prepare.py','assets.cjs','preview.cjs','preview.py','object_checks.py','native_checks.py','checks.py','compile.py','pack.py','validate_assets.cjs','changes.json']:
    shutil.copy2(R/name,source/name)
shutil.copytree(R/'src/Units',source/'Units',dirs_exist_ok=True)
shutil.copytree(R/'src/ReplaceableTextures',source/'ReplaceableTextures',dirs_exist_ok=True)
print(json.dumps(report,indent=2))
