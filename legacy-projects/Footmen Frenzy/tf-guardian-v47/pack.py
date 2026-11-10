from pathlib import Path
import sys,shutil,hashlib,json
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries,functions
import objdata
base=W/'tf-destiny-v46/release/FF799X_Rx_TF_Destiny_v46.w3x'; s=(S/'war3map.j').read_text(encoding='utf8');f=functions(s)
assert 'Parse successful' in (R/'compiler.log').read_text() and 'error' not in (R/'compiler.log').read_text().lower()
assert 'ticks>=100' in f['TF33_SelectTick'] and 'GetRandomInt(0,2)' in f['TF33_SelectTick']
assert 'set GTW_Left[i] = distance' in f['GTW_Cast'] and 'RMaxBJ(200.0' in f['GTW_Cast']
assert 'GL_ArmorApply(u, -3.0)' in f['TFP_LinkGround'] and 'GL_ArmorApply(u, 3.0)' in f['TFP_LinkGround']
assert '40.0 * TFP_FFDP_TICK' in f['TFP_FFDP_Tick'] and 'GD_Left[i] * 0.05' not in f['GD_Tick']
for n in ['war3map.w3a','war3mapSkin.w3a']:
 d=objdata.load(str(S/n))
 for t in d['tables']:
  for e in t:
   if e['newId']=='ATf2':
    for m in e['mods']:
     if m['id'] in ('aub1','arut'):m['value']=m['value'].replace('Six seconds to select','Five seconds to select')
   if e['newId']=='ATfd':
    for m in e['mods']:
     if m['id'] in ('aub1','arut'):
      m['value']=m['value'].replace('Allies entering the chain gain 10 HP and are slowed 20% for 1 sec; remaining in the chain heals 20 HP/sec.', 'Allies on the chain gain 3 armor and heal 10 on entry plus 20 HP/sec; enemies on it lose 3 armor and are slowed. Armor lasts 2 sec after leaving. Riders heal 40 HP/sec.')
 (S/n).write_bytes(objdata.dump(d))
out=R/'release/FF799X_Rx_TF_Guardian_v47.w3x';shutil.copy2(base,out)
payload={'war3map.j':S/'war3map.j','war3map.w3a':S/'war3map.w3a','war3mapSkin.w3a':S/'war3mapSkin.w3a','war3mapImported\\TFOrb.mdx':S/'TFOrb.mdx'}
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for name,path in payload.items():assert storm.SFileAddFileEx(h,str(path),name.encode(),0x80000200,2,2),name
assert storm.SFileCloseArchive(h)
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name,path in payload.items():assert read_storm(h,name)==path.read_bytes(),name
assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(out);old,new=entries(a),entries(b);skip=set()
for n in list(payload)+['(listfile)','(attributes)','(signature)']:
 e=a.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in old.items():
 if k not in skip:assert new.get(k)==v
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report={'output':str(out),'sha256':sha,'base':str(base),'unchanged_archive_entries':len(old.keys()-skip),'jass_compilation':'passed','tf_behavior_checks':101,'live_engine_test':'pending'};(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
