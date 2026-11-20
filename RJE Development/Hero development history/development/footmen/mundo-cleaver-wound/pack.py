from pathlib import Path
import hashlib,json,shutil,sys
R=Path(__file__).resolve().parent; W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
import objdata
manifest=json.loads((R/'changes.json').read_text()); base=Path(manifest['base'])
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(base)==manifest['base_sha256'],'Base changed during work'
checks=json.loads((R/'checks.json').read_text()); assert checks['passed']==40
for name in ['compiler.log','editor-compiler.log']:
    log=(R/name).read_text(); assert 'Parse successful:' in log and 'Parse failed' not in log
assert 'Success!' in (R/'jasshelper.log').read_text()
stage=R/'stage.w3x'; shutil.copy2(base,stage)
h=c.c_void_p(); assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h))
changed=[]
for f in sorted((R/'src').iterdir()):
    assert f.is_file()
    assert storm.SFileAddFileEx(h,str(f),f.name.encode(),0x80000200,2,2)
    changed.append(f.name)
assert storm.SFileCloseArchive(h)
out=R/'release/FF799X_Rx_Mundo_Cleaver_Wound_Test.w3x'; out.parent.mkdir(exist_ok=True)
# Preserve offsets of inherited encrypted members; do not manually compact.
shutil.copy2(stage,out)
ba=archive(base); before,after=entries(ba),entries(archive(out)); skip=set()
for n in changed+['(attributes)','(listfile)','(signature)']:
    e=ba.get_hash_table_entry(n)
    if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in before.items():
    if k not in skip:assert after.get(k)==v,('unexpected archive change',k)
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in changed:assert read_storm(h,n)==(R/'src'/n).read_bytes(),n
assert storm.SFileCloseArchive(h)
assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
oldfs=functions(read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r',''))
newfs=functions((R/'src/war3map.j').read_text(encoding='utf8'))
assert set(oldfs)<=set(newfs)
assert {n for n in oldfs if oldfs[n]!=newfs[n]}==set(manifest['changed_functions'])
assert set(newfs)-set(oldfs)==set(manifest['new_functions'])
for name,newids,allowed in [('war3map.w3a',manifest['new_abilities'],manifest['changed_abilities']),('war3map.w3h',manifest['new_buffs'],[])]:
    p=R/('before-'+name); assert p.read_bytes()==read_storm(h,name)
    old=objdata.load(str(p)); new=objdata.load(str(R/'src'/name))
    assert old['tables'][0]==new['tables'][0]
    assert len(new['tables'][1])==len(old['tables'][1])+len(newids)
    assert {e['newId'] for e in new['tables'][1][len(old['tables'][1]):]}==set(newids)
    for a,b in zip(old['tables'][1],new['tables'][1]):
        assert a['newId']==b['newId']
        if a['newId'] not in allowed:assert a==b,a['newId']
assert storm.SFileCloseArchive(h)
sha=digest(out); out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report=dict(output=str(out),sha256=sha,base=str(base),base_sha256=digest(base),changed_payloads=changed,preserved_archive_entries=len(before.keys()-skip),runtime_pjass='passed',editor_jasshelper_pjass='passed',behavior_object_checks=checks['passed'],engine_playtested=False,installed=False,includes_prior_mundo_health_kit=True,includes_parallel_lux_stalker_icon_work=False)
(R/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
