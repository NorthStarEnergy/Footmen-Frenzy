"""Extend Veigar's cast distances on the v73 combined test map."""
from pathlib import Path
import copy, hashlib, json, shutil, sys
R=Path(__file__).resolve().parent;W=R.parent;O=R/'src';O.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import archive,entries,storm,read_storm,c
from validate_objdata import validate
import objdata
BASE=W/'veigar-repair-v73/release/FF799X_Rx_Veigar_Cage_Range_v73_TEST.w3x'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='2b602b70eb95cd7d3b5549bf0f7b71256983c3171871642f871ed9bd60a61701'
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h))
original={n:read_storm(h,n) for n in ['war3map.w3a','FF_MAINTENANCE.md','war3map.j','war3map.wct']};assert storm.SFileCloseArchive(h)
(R/'before-war3map.w3a').write_bytes(original['war3map.w3a']);a=objdata.load(str(R/'before-war3map.w3a'));assert objdata.dump(a)==original['war3map.w3a']
edits=[];values={'AVgq':(700,900,6),'AVgw':(900,1100,6),'AVge':(900,1100,6),'AVgr':(650,850,3)}
for e in [e for t in a['tables'] for e in t if e['newId'] in values]:
 old,new,ranks=values[e['newId']];ranges=[m for m in e['mods'] if m['id']=='aran'];tips=[m for m in e['mods'] if m['id'] in ['aub1','arut']]
 assert len(ranges)==ranks and len(tips)==ranks+1
 for m in ranges:
  assert m['type']==2 and m['value']==old;m['value']=float(new);edits.append([e['newId'],'aran',m['level'],old,new])
 for m in tips:
  text=m['value'];expected=ranks if m['id']=='arut' else 1
  assert text.count('Range: '+str(old)+'.')==expected,(e['newId'],m['id'])
  m['value']=text.replace('Range: '+str(old)+'.','Range: '+str(new)+'.');edits.append([e['newId'],m['id'],m['level'],'updated'])
(O/'war3map.w3a').write_bytes(objdata.dump(a));validate((O/'war3map.w3a').read_bytes(),True)
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\n\nVeigar cast-distance test: Q 900, W 1100, E 1100, R 850; all ranks and displayed tooltips updated. Damage, target rules and cooldowns unchanged. Engine and balance testing pending.\n')
# Re-read the object and require all ranks and their normal and learn tooltips to agree.
outdata=objdata.load(str(O/'war3map.w3a'));baseobj=objdata.load(str(R/'before-war3map.w3a'))
assert [len(t) for t in outdata['tables']]==[len(t) for t in baseobj['tables']]
for a,b in zip(sum(baseobj['tables'],[]),sum(outdata['tables'],[])):
 if a['newId'] not in values:assert a==b,a['newId']
 else:
  assert [m for m in a['mods'] if m['id'] not in ['aran','aub1','arut']]==[m for m in b['mods'] if m['id'] not in ['aran','aub1','arut']]
  old,new,ranks=values[a['newId']]
  assert all(m['type']==2 and m['value']==new for m in b['mods'] if m['id']=='aran')
  assert all('Range: '+str(new)+'.' in m['value'] and 'Range: '+str(old)+'.' not in m['value'] for m in b['mods'] if m['id'] in ['aub1','arut'])
stage=R/'stage.w3x';shutil.copy2(BASE,stage);h=c.c_void_p();assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h))
for n in ['war3map.w3a','FF_MAINTENANCE.md']:assert storm.SFileAddFileEx(h,str(O/n),n.encode(),0x80000200,2,2)
assert storm.SFileCloseArchive(h)
out=R/'release/FF799X_Rx_Veigar_Range_v74_TEST.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(stage,out)
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint];assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
if archive(out).get_hash_table_entry('(attributes)'):assert storm.SFileRemoveFile(h,b'(attributes)',0)
assert storm.SFileCloseArchive(h)
ba,aa=archive(BASE),archive(out);before,after=entries(ba),entries(aa);allowed=set()
for n in ['war3map.w3a','FF_MAINTENANCE.md','(listfile)','(attributes)','(signature)']:
 for ar in [ba,aa]:
  e=ar.get_hash_table_entry(n)
  if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(after.get(k)==v for k,v in before.items() if k not in allowed)
assert all(k in before or k in allowed for k in after)
assert storm.SFileOpenArchive(str(out),0,256,c.byref(h))
for n in ['war3map.w3a','FF_MAINTENANCE.md']:assert read_storm(h,n)==(O/n).read_bytes()
for n in ['war3map.j','war3map.wct']:assert read_storm(h,n)==original[n]
assert storm.SFileCloseArchive(h)
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report={'output':str(out),'sha256':sha,'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'ranges':{k:v[1] for k,v in values.items()},'ranks_and_tooltips_checked':21,'unchanged_archive_entries':sum(k not in allowed for k in before),'script_and_editor_byte_identical':True,'engine_playtested':False,'installed':False,'edits':edits}
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='edits'},indent=2))
