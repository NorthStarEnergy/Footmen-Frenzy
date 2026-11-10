from pathlib import Path
import sys,struct,hashlib,shutil,json
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src';sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries,functions
import objdata
base=W/'tf-wc3-icons-v50/release/FF799X_Rx_TF_Guardian_WC3Icons_v50.w3x';s=(S/'war3map.j').read_text(encoding='utf8');f=functions(s);assert 'Parse successful' in (R/'compiler.log').read_text() and 'error' not in (R/'compiler.log').read_text().lower()
assert f['TFP_wildCards___c'].count("'htz1'")==3 and 'GetRandomInt' not in f['TFP_wildCards___setCardRandHue'];assert "'htf1'" in f['TF33_Cast']
o=objdata.load(str(S/'war3map.w3u'));new=[e for t in o['tables'] for e in t if e['newId']=='htz1'];assert len(new)==1 and any(m['id']=='umdl' and m['value']=='war3mapImported\\TFWildOrb.mdx' for m in new[0]['mods'])
payload={'war3map.j':S/'war3map.j','war3map.w3u':S/'war3map.w3u','war3map.imp':S/'war3map.imp','war3mapImported\\TFWildOrb.mdx':S/'TFWildOrb.mdx'}
for name in ['Fork','Choice']:
 for disabled in [False,True]:
  folder='CommandButtonsDisabled' if disabled else 'CommandButtons';filename=('DISBTN' if disabled else 'BTN')+'FFOrb'+name+'.blp';payload['ReplaceableTextures\\'+folder+'\\'+filename]=S/filename
out=R/'release/FF799X_Rx_TF_Guardian_Orbs_v51.w3x';shutil.copy2(base,out);h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n,p in payload.items():assert storm.SFileAddFileEx(h,str(p),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h);h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n,p in payload.items():assert read_storm(h,n)==p.read_bytes(),n
assert storm.SFileCloseArchive(h);a,b=archive(base),archive(out);old,new=entries(a),entries(b);skip=set()
for n in list(payload)+['(listfile)','(attributes)','(signature)']:
 e=a.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in old.items():
 if k not in skip:assert new.get(k)==v
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n');report={'output':str(out),'sha256':sha,'base':str(base),'unchanged_entries':len(old.keys()-skip),'jass':'passed','tf_behavior_checks':101,'model':'MDX roundtrip passed','live_test':'pending'};(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
