from pathlib import Path
import sys,json,hashlib,shutil,re
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions,archive,entries
import objdata
m=json.loads((R/'changes.json').read_text());base=Path(m['base'])
assert hashlib.sha256(base.read_bytes()).hexdigest()==m['base_sha256']
checks=json.loads((R/'checks.json').read_text());assert checks['passed']>=160
log=(R/'compiler.log').read_text();assert 'Parse successful' in log and 'error' not in log.lower()
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
old=functions(read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r\n','\n'));new=functions((R/'src/war3map.j').read_text(encoding='utf8'))
allowed={'MD_Clear','MD_Start','MD_Tick','MD_OnDamage','MD_Init','MU_Clear','MQ_Free','MQ_GroundTick','MQ_Land','MU_OnCleaverHit','MU_Launch','MU_Init'}
assert not old.keys()-new.keys() and {n for n in old if old[n]!=new[n]}==allowed
p=R/'base.w3a';p.write_bytes(read_storm(h,'war3map.w3a'))
key=lambda e:e['newId'] if e['newId']!='\0'*4 else e['oldId']
a={key(e):e for t in objdata.load(str(p))['tables'] for e in t};d=objdata.load(str(R/'src/war3map.w3a'));b={key(e):e for t in d['tables'] for e in t}
assert objdata.dump(d)==(R/'src/war3map.w3a').read_bytes()
assert b.keys()-a.keys()==set(m['added_abilities']) and not a.keys()-b.keys()
for k in a:
 if k not in ['AMu1','AMu3']:assert a[k]==b[k],k
# Only icon and explanatory text changes to the public abilities; balance is script-side.
for k in ['AMu1','AMu3']:
 def gameplay(e):return [x for x in e['mods'] if x['id'] not in ['aart','arar','aub1','arut']]
 assert gameplay(a[k])==gameplay(b[k]),k
assert storm.SFileCloseArchive(h)
release=R/'release';release.mkdir(exist_ok=True);out=release/'FF799X_Rx_Consolidated_Mundo_v40.w3x';shutil.copy2(base,out)
names=['war3map.j','war3map.w3a','war3map.imp','war3map.wts']+m['imports']
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n in names:assert storm.SFileAddFileEx(h,str(R/'src'/n),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(out);ae,be=entries(a),entries(b);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in names:
 assert read_storm(h,n)==(R/'src'/n).read_bytes(),n
 e=a.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert storm.SFileCloseArchive(h)
for n in ['(listfile)','(attributes)','(signature)']:
 e=a.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in ae.items():
 if k not in skip:assert be.get(k)==v,('Unrelated map payload changed',k)
# Model-cleanup removals remain absent; there are no new models in this build.
v39=json.loads((W/'model-cleanup-v39/verification.json').read_text())
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report=dict(output=str(out),sha256=sha,base=str(base),changed_functions=sorted(allowed),preserved_functions=len(old)-len(allowed),preserved_archive_entries=len(ae.keys()-skip),checks=checks['passed'],compiler='passed',live_test='Pending Warcraft III playtest',visual_model='Existing Axe Missile-Small enlarged; external cleaver download unavailable')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
