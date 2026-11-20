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
out=R/'release/FF799X_Rx_Mundo_Cloud_Ramp_Test.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(stage,out)
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
assert read_storm(h,'war3map.w3a')==(R/'before-war3map.w3a').read_bytes()
oldimp=read_storm(h,'war3map.imp');newimp=(R/'src/war3map.imp').read_bytes()
assert newimp[8:8+len(oldimp)-8]==oldimp[8:]
assert struct.unpack_from('<II',newimp)==(struct.unpack_from('<II',oldimp)[0],struct.unpack_from('<II',oldimp)[1]+21)
assert storm.SFileCloseArchive(h)
oldobj=objdata.load(str(R/'before-war3map.w3a'));newobj=objdata.load(str(R/'src/war3map.w3a'))
assert oldobj['tables'][0]==newobj['tables'][0] and len(oldobj['tables'][1])==len(newobj['tables'][1])
for a,b in zip(oldobj['tables'][1],newobj['tables'][1]):
    assert a['newId']==b['newId']
    if a['newId']!='AMu2':assert a==b,a['newId']
    else:assert [m for m in a['mods'] if m['id'] not in ['aub1','arut']]==[m for m in b['mods'] if m['id'] not in ['aub1','arut']]
report=dict(output=str(out),sha256=digest(out),base=str(base),base_sha256=digest(base),changed_payloads=changed,preserved_archive_entries=sum(k not in allowed for k in before),runtime_compiler='passed',editor_compiler='passed',behavior_object_model_checks=checks['passed'],custom_models=21,engine_playtested=False,installed=False,includes_prior_mundo_health_kit_and_cleaver=True,includes_parallel_lux_stalker_icons=False)
(R/'verification.json').write_text(json.dumps(report,indent=2));out.with_suffix('.sha256').write_text(digest(out)+'  '+out.name+'\n')
print(json.dumps(report,indent=2))
