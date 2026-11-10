from pathlib import Path
import sys,json,hashlib,subprocess,shutil
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import archive,entries,storm,read_storm,c,functions,work
import objdata
O=R/'src';m=json.loads((R/'changes.json').read_text());base=Path(m['base']);assert hashlib.sha256(base.read_bytes()).hexdigest()==m['base_sha256']
s=(O/'war3map.j').read_text(encoding='utf8');f=functions(s)
for name in ['Trig_Guardian_Force_Field_Learn_Actions','Trig_Guardian_Force_Field_Cast_Actions','Trig_Guardian_Force_Field_Loop_Actions']:
 assert 'AFFD' not in f[name] and 'udg_Guardian_FF_Detonate' not in f[name]
assert 'InitTrig_Guardian_Force_Field_Detonate()' not in f['FF_Editor_InitTriggers']
assert 'InitHashtableBJ()' in f['Trig_Guardian_Force_Field_Learn_Actions']
assert 'call GFW_Create' in f['Trig_Guardian_Force_Field_Cast_Actions'] and 'call GFB_Cast' in f['Trig_Guardian_Force_Field_Cast_Actions']
assert 'CPP_Remove_Pathing' in f['Trig_Guardian_Force_Field_Loop_Actions'] and 'udg_Guardian_FF_Index - 1' in f['Trig_Guardian_Force_Field_Loop_Actions']
# Execute the actual burst timeout/recast functions from the existing Guardian harness.
code=(W/'799x-backport/check_guardian.py').read_text();code=code[:code.index('def objects(ext):')]
code=code.replace('ROOT=Path(__file__).resolve().parent','ROOT=Path('+repr(str(R))+')').replace("(ROOT/'check_runtime.py')","(Path("+repr(str(W/'799x-backport'))+")/'check_runtime.py')")
exec(compile(code,'guardian-burst','exec'),{'__file__':str(W/'799x-backport/check_guardian.py')})
run=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(O/'war3map.j')],capture_output=True,text=True)
(R/'audit/compiler.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
original=archive(base);h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
bf=functions(read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r\n','\n'))
for name in bf:
 if name not in m['changed_functions']:assert bf[name]==f[name],name
(R/'audit/base.w3a').write_bytes(read_storm(h,'war3map.w3a'));assert storm.SFileCloseArchive(h)
before=objdata.load(str(R/'audit/base.w3a'));after=objdata.load(str(O/'war3map.w3a'));assert objdata.dump(after)==(O/'war3map.w3a').read_bytes()
key=lambda e:e['newId'] if e['newId']!='\0'*4 else e['oldId']
old={key(e):e for t in before['tables'] for e in t};new={key(e):e for t in after['tables'] for e in t};assert old.keys()==new.keys()
for uid in old:
 if uid!='AFg1':assert old[uid]==new[uid],uid
for a,b in zip(old['AFg1']['mods'],new['AFg1']['mods']):
 if a['id'] in ['arut','aub1']:assert b['value']==a['value'].replace('; use Detonate to clear it early',' and expires on its own')
 else:assert a==b
names=['war3map.j','war3map.w3a','war3map.wts'];out=R/'release/FF799X_Rx_Guardian_v28.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(base,out)
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
(R/'verification.json').write_text(json.dumps(report,indent=2));print('Burst tests passed; '+json.dumps(report,indent=2))
