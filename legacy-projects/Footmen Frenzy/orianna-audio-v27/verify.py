"""Regression-check the actual Orianna functions, then verify an incremental MPQ update."""
from pathlib import Path
import sys,re,json,shutil,hashlib,subprocess
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import archive,entries,storm,read_storm,c,functions,work
import objdata
O=R/'src';m=json.loads((R/'changes.json').read_text());base=Path(m['base']);assert hashlib.sha256(base.read_bytes()).hexdigest()==m['base_sha256']
# Retain the previous gameplay regression suite, with the new speed and native label mocks.
code=(W/'hero-polish/checks.py').read_text();code=code[:code.index(" s=(V/'src/war3map.j').read_text()")]
code=code.replace("R=Path(__file__).resolve().parent;W=R.parent", "R=Path("+repr(str(W/'hero-polish'))+");W=R.parent")
code=code.replace("['check_runtime.py','check_gragus.py','check_guardian.py','check_guardian_bolts.py']", "['check_runtime.py']")
insert='''
   code=code.replace('OM_SPEED=1200.', 'OM_SPEED=1320.')
   code=code.replace('CreateSound=lambda path,*a:new(sounds,path=path,args=a),','CreateSound=lambda path,*a:new(sounds,path=path,args=a),CreateSoundFromLabel=lambda label,*a:new(sounds,path=label,args=a),')
   code=code.replace("v['path'].endswith(name+'.wav')", "v['path'].endswith(name+'.wav') or v['path']=={'Move':'FaerieDragonLaunch','Attack':'StasisTotemDeath'}.get(name)")
'''
code=code.replace("  if name=='check_runtime.py':", "  if name=='check_runtime.py':"+insert)
more='''
setup();cast('AOz1');ticks(1)
check('Move orb advances 10 percent faster on the first tick',abs(units[10]['x']-41.25)<.001)
check('Move cue follows the orb',any(v['path']=='FaerieDragonLaunch' and v.get('unit')==10 and v.get('started') for v in sounds.values()))
setup();cast('AOz3');ticks(1)
check('Protect orb advances 10 percent faster on the first tick',abs(units[10]['x']-41.25)<.001)
setup();cast('AOz2')
check('Stasis detonation cue follows the orb during Attack',any(v['path']=='StasisTotemDeath' and v.get('unit')==10 and v.get('started') for v in sounds.values()))
'''
code=code.replace('   code=code.replace("(ROOT/\'audit/runtime-checks.json\')",extra+', '   extra += '+repr(more)+'\n   code=code.replace("(ROOT/\'audit/runtime-checks.json\')",extra+')
g={'__file__':str(W/'hero-polish/checks.py')};exec(compile(code,'adapted-checks','exec'),g);g['run'](R,'799x')
s=(O/'war3map.j').read_text(encoding='utf8');f=functions(s)
assert 'constant real OM_SPEED = 1320.0' in s
assert 'OM_State[i] == 1 or OM_State[i] == 2' in f['OM_Tick'] and 'set step = OM_SPEED * OM_TICK' in f['OM_Tick']
assert 'CreateSoundFromLabel("StasisTotemDeath"' in f['OM_CommandSound'] and 'call OM_CommandSound(OM_Ball[i], 2)' in f['OM_StartPulse']
assert 'CreateSoundFromLabel("FaerieDragonLaunch"' in f['OM_CommandSound'] and 'call OM_CommandSound(OM_Ball[i], 1)' in f['OM_StartTravelFX']
assert s.count('set udg_hero_turnrate[93]=1.0')==1
run=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(O/'war3map.j')],capture_output=True,text=True)
(R/'audit/compiler.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
original=archive(base);h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
bf=functions(read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r\n','\n'))
for name in bf:
 if name not in m['changed_functions']:assert bf[name]==f[name],name
(R/'audit/base.w3a').write_bytes(read_storm(h,'war3map.w3a'));assert storm.SFileCloseArchive(h)
before=objdata.load(str(R/'audit/base.w3a'));after=objdata.load(str(O/'war3map.w3a'));assert objdata.dump(after)==(O/'war3map.w3a').read_bytes()
key=lambda e:e['newId'] if e['newId']!='\0'*4 else e['oldId']
old={key(e):e for t in before['tables'] for e in t};new={key(e):e for t in after['tables'] for e in t}
assert old.keys()==new.keys()
for uid in old:
 if uid!='AOz1':assert old[uid]==new[uid],uid
o=old['AOz1'];n=new['AOz1'];assert len(o['mods'])==len(n['mods'])
for a,b in zip(o['mods'],n['mods']):
 if a['id']=='acdn':assert b['value']==a['value']-2 and a['level']==b['level']
 elif a['id'] in ['arut','aub1']:assert b['value']==a['value'].replace('Cooldown: 8 seconds.','Cooldown: 6 seconds.')
 else:assert a==b
names=['war3map.j','war3map.w3a','war3map.wts'];out=R/'release/FF799X_Rx_OriannaAudio_v27.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(base,out)
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
