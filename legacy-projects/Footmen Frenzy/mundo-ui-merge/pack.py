from pathlib import Path
import sys,json,hashlib,shutil,struct
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
import objdata
manifest=json.loads((R/'changes.json').read_text());base=Path(manifest['base'])
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(base)==manifest['base_sha256']
checks=json.loads((R/'checks.json').read_text());assert checks['passed']==65
assert json.loads((R/'cleaver-checks.json').read_text())['passed']==40
assert json.loads((R/'resource-checks.json').read_text())['passed']==10
for n,d in json.loads((R/'compiled-hashes.json').read_text()).items():assert digest(R/n)==d,('Stale compiler output',n)
for n in ['compiler.log','editor-compiler.log']:assert 'Parse successful:' in (R/n).read_text() and 'Parse failed' not in (R/n).read_text()
assert 'Success!' in (R/'jasshelper.log').read_text()
assets=json.loads((R/'asset-checks.json').read_text());assert assets['roundtrip_passed'] and len(assets['models'])==21
assert any(json.loads((R/'native-texture-check.json').read_text()).values())
stage=R/'stage.w3x';shutil.copy2(base,stage)
h=c.c_void_p();assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h))
changed=[]
for f in sorted((R/'src').rglob('*')):
    if not f.is_file():continue
    n=str(f.relative_to(R/'src')).replace('/','\\')
    assert storm.SFileAddFileEx(h,str(f),n.encode(),0x80000200,2,2),n
    changed.append(n)
assert storm.SFileCloseArchive(h)
out=R/'release/FF799X_Rx_UI_Repair_Mundo_Combined_Test.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(stage,out)
ba=archive(base);aa=archive(out);before,after=entries(ba),entries(aa);allowed=set()
for n in changed+['(listfile)','(attributes)','(signature)']:
    for ar in [ba,aa]:
        e=ar.get_hash_table_entry(n)
        if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(after.get(k)==v for k,v in before.items() if k not in allowed),'Unrelated archive payload changed'
assert all(k in before or k in allowed for k in after),'Unexpected archive member'
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in changed:assert read_storm(h,n)==(R/'src'/n.replace('\\','/')).read_bytes(),n
assert storm.SFileCloseArchive(h)
assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
old=functions(read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r',''));new=functions((R/'src/war3map.j').read_text(encoding='utf8'))
assert set(old)<=set(new)
assert {n for n in old if old[n]!=new[n]}==set(manifest['changed_functions'])
assert set(new)-set(old)==set(manifest['new_functions'])
for name,changes in manifest['object_changes'].items():
    assert read_storm(h,name)==(R/('before-'+name)).read_bytes()
    oldobj=objdata.load(str(R/('before-'+name)));newobj=objdata.load(str(R/'src'/name))
    added={tuple(c['object']) for c in changes if c.get('added')}
    changed_fields={}
    for change in changes:
        if 'field' in change:changed_fields.setdefault(tuple(change['object']),set()).add(tuple(change['field']))
    for ot,nt in zip(oldobj['tables'],newobj['tables']):
        om={(e['oldId'],e['newId']):e for e in ot};nm={(e['oldId'],e['newId']):e for e in nt}
        assert om.keys()<=nm.keys() and nm.keys()-om.keys()<=added
        for key,a in om.items():
            b=nm[key];skip=changed_fields.get(key,set())
            filtered=lambda e:{**e,'mods':[m for m in e['mods'] if (m['id'],m.get('level'),m.get('ptr')) not in skip]}
            assert filtered(a)==filtered(b),('Unexpected object change',name,key)
oldimp=read_storm(h,'war3map.imp');newimp=(R/'src/war3map.imp').read_bytes()
assert newimp[8:len(oldimp)]==oldimp[8:]
assert all(n.encode()+b'\0' in newimp for n in manifest['imports'])
# Full decode catches unreadable assets that raw encrypted-entry preservation cannot.
known_names=[v['path'] for v in json.loads((W/'size-audit-v50/archive-files.json').read_text())]
pos=8
for _ in range(struct.unpack_from('<II',oldimp)[1]):
    flag=oldimp[pos];pos+=1;end=oldimp.index(0,pos);name=oldimp[pos:end].decode('latin1');pos=end+1
    known_names.append(name if flag in [10,13] else 'war3mapImported\\'+name)
known_names+=['war3map.j','war3map.wct','war3map.wts','war3map.w3a','war3map.w3u','war3map.w3h','war3map.imp','FF_MAINTENANCE.md']
readable_names=sorted(set(known_names)-{'(attributes)','(signature)','(listfile)'})
readable_names=[n for n in readable_names if ba.get_hash_table_entry(n)]
for name in readable_names:read_storm(h,name)
assert storm.SFileCloseArchive(h)
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
baseline_handle=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(baseline_handle))
for name in readable_names:
    actual=read_storm(h,name)
    if name not in changed:
        # Check bytes against the selected repaired baseline, including WTS and icons.
        assert actual==read_storm(baseline_handle,name),name
assert storm.SFileCloseArchive(baseline_handle)
assert storm.SFileCloseArchive(h)
report=dict(output=str(out),sha256=digest(out),base=str(base),base_sha256=digest(base),changed_payloads=changed,preserved_archive_entries=sum(k not in allowed for k in before),runtime_compiler='passed',editor_compiler='passed',behavior_object_model_checks=115,fully_readable_preserved_files=len(readable_names),includes_ui_repair=True,custom_models=21,engine_playtested=False,installed=False,includes_prior_mundo_health_kit_and_cleaver=True,parallel_content='Inherited unchanged from UI agent selected baseline')
(R/'verification.json').write_text(json.dumps(report,indent=2));out.with_suffix('.sha256').write_text(digest(out)+'  '+out.name+'\n')
print(json.dumps(report,indent=2))
