from pathlib import Path
import sys,json,hashlib,shutil
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions,archive,entries
from validate_objdata import validate
import objdata
change=json.loads((R/'changes.json').read_text());base=Path(change['base'])
assert hashlib.sha256(base.read_bytes()).hexdigest()==change['base_sha256']
assert json.loads((R/'checks.json').read_text())['passed']>=204
assert json.loads((R/'tf-checks.json').read_text())['passed']>=92
log=(R/'compiler.log').read_text();assert 'Parse successful' in log and 'error' not in log.lower()
for n in ['war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3mapSkin.w3a']:validate((S/n).read_bytes(),n.endswith('.w3a'))
idx={e['newId']:e for t in objdata.load(str(S/'war3map.w3a'))['tables'] for e in t}
assert all(idx[f'mD{i:02X}']['flags']==1 for i in range(256))
assert idx['ATfg']['oldId']=='ANcl'
out=R/'release/FF799X_Rx_Mundo_TF_Polish_v45a.w3x';assert not out.exists()
shutil.copy2(base,out)
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n in change['payloads']:assert storm.SFileAddFileEx(h,str(S/n),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h)
old,new=archive(base),archive(out);oe,ne=entries(old),entries(new);skip=set()
for n in change['payloads']+['(listfile)','(attributes)','(signature)']:
 e=old.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in oe.items():
 if k not in skip:assert ne.get(k)==v,('Unrelated payload changed',k)
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in change['payloads']:assert read_storm(h,n)==(S/n).read_bytes(),n
for n in ['war3map.w3t','war3mapSkin.w3t']:validate(read_storm(h,n),False)
assert storm.SFileCloseArchive(h)
oldf=functions(old.read_file('war3map.j').decode('utf-8-sig'));newf=functions((S/'war3map.j').read_text())
allowed=set(change['changed_functions']+change['tf_functions'])
for n in oldf:
 if n not in allowed:assert oldf[n].replace('\r\n','\n')==newf[n],n
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report=dict(output=str(out),sha256=sha,base=str(base),preserved_payloads=len(oe.keys()-skip),checks=296,compiler='passed',live_test='pending',dice=change['dice'])
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


