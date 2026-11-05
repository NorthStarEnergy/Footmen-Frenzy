from pathlib import Path
import sys,json,hashlib,subprocess,shutil
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import archive,entries,storm,read_storm,c,functions,work
import objdata
O=R/'src';m=json.loads((R/'changes.json').read_text());base=Path(m['base']);assert hashlib.sha256(base.read_bytes()).hexdigest()==m['base_sha256']
exec(compile((R/'checks.py').read_text(),'checks.py','exec'),{'__file__':str(R/'checks.py'),'__name__':'__main__'})
s=(O/'war3map.j').read_text(encoding='utf8');f=functions(s)
run=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(O/'war3map.j')],capture_output=True,text=True)
(R/'audit/compiler.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
original=archive(base);h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
source=read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r\n','\n');bf=functions(source)
for name in bf:
 if name not in m['changed_functions']:assert bf[name]==f[name],name
restored=s.replace(f['FF_CompactHeroTooltips_Init']+'\n\n','',1).replace(f['InitTrig_FF_Runtime'],bf['InitTrig_FF_Runtime'],1).replace('FF799X - Hero Tooltips v31','FF799X - Guardian Lantern v30')
assert restored==source,'Script changes outside tooltip initialization'
names=['war3map.w3a','war3map.w3u','war3mapSkin.w3u']
for name in names:
 oldpath=R/'audit'/('base.'+name);oldpath.write_bytes(read_storm(h,name));olddata=objdata.load(str(oldpath));newdata=objdata.load(str(O/name));assert objdata.dump(newdata)==(O/name).read_bytes()
 key=lambda e:e['newId'] if e['newId']!='\0'*4 else e['oldId']
 old={key(e):e for t in olddata['tables'] for e in t};new={key(e):e for t in newdata['tables'] for e in t};assert old.keys()==new.keys()
 for uid in old:
  allowed={'aub1','atp1','arut','aret'} if name=='war3map.w3a' and uid in m['skills'] else {'aub1'} if name=='war3map.w3a' and uid=='AGr8' else {'utub'} if name!='war3map.w3a' and uid in {'H043','HOr1','HGr1'} else set()
  if not allowed:assert old[uid]==new[uid],(name,uid)
  else:
   before={(x['id'],x.get('level',0)):x for x in old[uid]['mods']};after={(x['id'],x.get('level',0)):x for x in new[uid]['mods']}
   for k,v in before.items():
    if k[0] not in allowed:assert after[k]==v,(name,uid,k)
   assert not any(k[0] not in allowed for k in after.keys()-before.keys()),(name,uid)
assert storm.SFileCloseArchive(h)
names=['war3map.j','war3map.w3a','war3map.w3u','war3mapSkin.w3u','war3map.wts'];out=R/'release/FF799X_Rx_HeroTooltips_v31.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(base,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for name in names:assert storm.SFileAddFileEx(h,str(O/name),name.encode(),0x80000200,2,2),name
assert storm.SFileCloseArchive(h)
result=archive(out);oldentries,newentries=entries(original),entries(result);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name in names:
 assert read_storm(h,name)==(O/name).read_bytes(),name
 e=original.get_hash_table_entry(name);skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert storm.SFileCloseArchive(h)
for name in ['(listfile)','(attributes)','(signature)']:
 e=original.get_hash_table_entry(name)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,value in oldentries.items():
 if k not in skip:assert newentries.get(k)==value,k
digest=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(digest+'  '+out.name+'\n')
report=dict(output=str(out),sha256=digest,changed_payloads=names,preserved_archive_entries=len(oldentries.keys()-skip),preserved_functions=len(bf)-len(m['changed_functions']),live_test='Pending')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
