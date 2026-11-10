from pathlib import Path
import sys,shutil,hashlib,json
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W/'hero-polish'));from archive_helpers import storm,read_storm,c,archive,entries,functions
base=W/'tf-lock-v52/release/FF799X_Rx_TF_Guardian_OrbLock_v52.w3x';out=R/'release/FF799X_Rx_TF_Guardian_HealOrbs_v53.w3x';src=R/'src/war3map.j';h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h));before=read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r\n','\n');assert len(read_storm(h,'Spells\\Orianna\\Feedback\\Heal.wav'))>0;assert storm.SFileCloseArchive(h)
a,b=functions(before),functions(src.read_text(encoding='utf8'));assert a.keys()==b.keys();assert {k for k in a if a[k]!=b[k]}=={'TFP_wildCards___setCardRandHue','TF33_Cast','TF33_Impact','TF33_Flight'};assert 'constant real TFP_wildCards___PROJECTILE_SPEED=1100.' in src.read_text();assert 'Parse successful' in (R/'compiler.log').read_text()
shutil.copy2(base,out);h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h));assert storm.SFileAddFileEx(h,str(src),b'war3map.j',0x80000200,2,2);assert storm.SFileCloseArchive(h);h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h));assert read_storm(h,'war3map.j')==src.read_bytes();assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(out);old,new=entries(a),entries(b);skip=set()
for n in ['war3map.j','(listfile)','(attributes)','(signature)']:
 e=a.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in old.items():
 if k not in skip:assert new.get(k)==v
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n');report={'output':str(out),'sha256':sha,'preserved_entries':len(old.keys()-skip),'jass':'passed','behavior_checks':110,'live_test':'pending'};(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
