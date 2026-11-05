from pathlib import Path
import sys, json, hashlib, shutil
R=Path(__file__).resolve().parent
W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive, entries, functions, storm, read_storm, c
base=W/'pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x'
source=W/'Transfer/Veigar_Classic_v68/FF799X_Rx_Veigar_Classic_v68.w3x'
manifest=json.loads((source.parent/'verification.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(base)==manifest['source_sha256']
assert sha(source)==manifest['output_sha256']
a,b=archive(base),archive(source)
old,new=entries(a),entries(b)
allowed=set()
for n in manifest['changed_members']+['(listfile)','(attributes)','(signature)']:
    for ar in [a,b]:
        e=ar.get_hash_table_entry(n)
        if e: allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(new.get(k)==v for k,v in old.items() if k not in allowed)
assert all(k in old or k in allowed for k in new)
handles=[]
for path in [base,source]:
    h=c.c_void_p()
    assert storm.SFileOpenArchive(str(path),0,0x100,c.byref(h))
    handles.append(h)
before=functions(read_storm(handles[0],'war3map.j').decode('utf-8-sig').replace('\r\n','\n'))
runtime=read_storm(handles[1],'war3map.j')
after=functions(runtime.decode('utf-8-sig').replace('\r\n','\n'))
changed=sorted(k for k in before if before[k]!=after.get(k))
assert set(changed)<=set(manifest['changed_functions']),changed
for n in manifest['changed_members']:
    expected=W/'hero-icons-simple/veigar-v68/edited'/n.replace('\\','/')
    assert read_storm(handles[1],n)==expected.read_bytes(),n
out=R/'release'/source.name
out.parent.mkdir(exist_ok=True)
shutil.copy2(source,out)
assert sha(out)==sha(source)
report={'base':str(base),'base_sha256':sha(base),'output':str(out),'output_sha256':sha(out),'already_combined':True,'unrelated_entries_preserved':sum(k not in allowed for k in old),'changed_functions':changed,'new_functions':sorted(set(after)-set(before)),'changed_members_verified':len(manifest['changed_members']),'new_icon_repaints_included':False,'unfinished_v69_included':False,'engine_tested':False}
(R/'verification.json').write_text(json.dumps(report,indent=2))
out.with_suffix('.sha256').write_text(sha(out)+'  '+out.name+'\n')
(R/'war3map.j').write_bytes(runtime)
for h in handles: assert storm.SFileCloseArchive(h)
print(json.dumps(report,indent=2))
