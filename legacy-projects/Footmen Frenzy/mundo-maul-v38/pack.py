from pathlib import Path
import sys,json,hashlib,shutil
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions,archive,entries
import objdata
m=json.loads((R/'changes.json').read_text());base=Path(m['base'])
assert hashlib.sha256(base.read_bytes()).hexdigest()==m['base_sha256']
checks=json.loads((R/'checks.json').read_text());assert checks['passed']>=136
log=(R/'compiler.log').read_text();assert 'Parse successful' in log and 'error' not in log.lower()
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
old=functions(read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r\n','\n'));new=functions((R/'src/war3map.j').read_text(encoding='utf8'))
assert not old.keys()-new.keys()
assert {n for n in old if old[n]!=new[n]}==set(m['changed_functions'])
for ext,changed,added in [('w3a',{'AMu3'},{'AMdv'}),('w3u',{'HMu1'},set())]:
    p=R/('base.'+ext);p.write_bytes(read_storm(h,'war3map.'+ext))
    key=lambda e:e['newId'] if e['newId']!='\0'*4 else e['oldId']
    a={key(e):e for t in objdata.load(str(p))['tables'] for e in t};d=objdata.load(str(R/'src'/('war3map.'+ext)));b={key(e):e for t in d['tables'] for e in t}
    assert objdata.dump(d)==(R/'src'/('war3map.'+ext)).read_bytes()
    assert b.keys()-a.keys()==added and not a.keys()-b.keys()
    for k in a:
        if k not in changed:assert a[k]==b[k],k
assert storm.SFileCloseArchive(h)
release=R/'release';release.mkdir(exist_ok=True);out=release/'FF799X_Rx_Consolidated_Maul_v38.w3x';shutil.copy2(base,out)
names=['war3map.j','war3map.w3a','war3map.w3u','war3map.wts']
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n in names:assert storm.SFileAddFileEx(h,str(R/'src'/n),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(out);ae,be=entries(a),entries(b);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in names:
    assert read_storm(h,n)==(R/'src'/n).read_bytes(),n
    e=a.get_hash_table_entry(n);skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert storm.SFileCloseArchive(h)
for n in ['(listfile)','(attributes)','(signature)']:
    e=a.get_hash_table_entry(n)
    if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in ae.items():
    if k not in skip:assert be.get(k)==v,k
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report=dict(output=str(out),sha256=sha,base=str(base),changed_functions=m['changed_functions'],preserved_functions=len(old)-len(m['changed_functions']),preserved_archive_entries=len(ae.keys()-skip),checks=checks['passed'],compiler='passed',live_test='Pending Warcraft III playtest')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
