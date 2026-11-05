from pathlib import Path
import sys,json,hashlib,shutil
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries,functions
import objdata
change=json.loads((R/'changes.json').read_text());base=Path(change['base']);names=change['payloads']
assert json.loads((R/'tf-checks.json').read_text())['passed']==92
log=(R/'compiler.log').read_text();assert 'Parse successful' in log and 'error' not in log.lower()
idx={(e['newId'] if e['newId']!='\0'*4 else e['oldId']):e for t in objdata.load(str(S/'war3map.w3a'))['tables'] for e in t}
for code in ['ATf6','ATf7','ATf8']:
 for lv,r in enumerate(change['ranges'],1):
  assert next(m['value'] for m in idx[code]['mods'] if m['id']=='aran' and m['level']==lv)==r
  assert next(m['value'] for m in idx[code]['mods'] if m['id']=='Ncl2' and m['level']==lv)==1
s=(S/'war3map.j').read_text();f=functions(s)
assert all('TextTag' not in f[n] for n in ['TF33_Cast','TF33_Show','TF33_Close'])
assert '+330.' in f['TF33_Show'] and 'TF33_Tint(orb,LoadInteger(TF33_H,h,4))' in f['TF33_Show']
out=R/'release/FF799X_Rx_TF_Orbs_v45c.w3x';out.parent.mkdir(exist_ok=True);assert not out.exists();shutil.copy2(base,out)
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n in names:assert storm.SFileAddFileEx(h,str(S/n),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h)
old,new=archive(base),archive(out);oe,ne=entries(old),entries(new);skip=set()
for n in names+['(listfile)','(attributes)','(signature)']:
 e=old.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in oe.items():
 if k not in skip:assert ne.get(k)==v,('Unrelated payload changed',k)
oldf=functions(old.read_file('war3map.j').decode('utf-8-sig').replace('\r\n','\n'))
for name in oldf:
 if name not in change['changed_functions']:assert oldf[name]==f[name],name
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in names:assert read_storm(h,n)==(S/n).read_bytes(),n
assert read_storm(h,'war3mapImported\\TFWhite.blp')
assert storm.SFileCloseArchive(h)
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report=dict(output=str(out),sha256=sha,base=str(base),preserved_payloads=len(oe.keys()-skip),tf_behavior_checks=92,range_checks=18,compiler='passed',live_test='pending')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
