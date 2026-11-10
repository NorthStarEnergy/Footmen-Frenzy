"""Add proportional catch-up to level 10 after the first active primary hero reaches 10."""
from pathlib import Path
import hashlib,json,re,shutil,struct,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;O=R/'src';O.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
BASE=W/'colo-curve-v77/release/FF799X_Rx_Colo_Curve_v77_TEST.w3x'
digest=lambda b:hashlib.sha256(b).hexdigest()
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h))
original={n:read_storm(h,n) for n in ['war3map.j','war3map.wct','FF_MAINTENANCE.md','FF_SOURCE_MANIFEST.json']};assert storm.SFileCloseArchive(h)
norm=lambda b:b.decode('utf-8-sig').replace('\r','')
old='function P67_HeroRate takes unit u returns real'
helper=(R/'catchup.j').read_text(encoding='utf8')
extra_globals=(R/'globals.j').read_text(encoding='utf8').strip()
def patch(s):
 if 'boolean P67_Reached6 = false' in s:
  assert s.count('boolean P67_Reached6 = false')==1
  s=s.replace('boolean P67_Reached6 = false','boolean P67_Reached6 = false\n'+extra_globals,1)
 fs=functions(s)
 if 'P67_HeroRate' not in fs:return s
 f=fs['P67_HeroRate']
 oldreturn='return P67_Rate(GetHeroLevel(u), P67_Reached4, P67_Reached6, P67_MassEnded, P67_FirstColo)'
 newreturn='return P78_Rate(GetHeroLevel(u), GetHeroXP(u), P78_Reached10, P67_Rate(GetHeroLevel(u), P67_Reached4, P67_Reached6, P67_MassEnded, P67_FirstColo))'
 assert f.count(oldreturn)==1
 s=s.replace(f,helper+'\n'+f.replace(oldreturn,newreturn),1)
 f=fs['P67_Refresh']
 anchor='            if GetHeroLevel(u) >= 6 then\n                set P67_Reached6 = true\n            endif'
 assert f.count(anchor)==1
 addition='\n            if GetHeroLevel(u) >= 10 and not P78_Reached10 then\n                set P78_Reached10 = true\n                call DisplayTextToForce(GetPlayersAll(), "|cff00ffffPub XP:|r Level 10 reached. Heroes below 10 now earn catch-up XP based on their own level progress.")\n            endif'
 s=s.replace(f,f.replace(anchor,anchor+addition).replace('Discover both milestones','Discover all milestones'),1)
 f=fs['P67_Start']
 oldmessage='From level 7 onward, kill XP is 70%.'
 assert f.count(oldmessage)==1
 s=s.replace(f,f.replace(oldmessage,'Level 7+ kill XP is 70%; once a hero reaches 10, heroes at levels 7-9 gain proportional catch-up until 10.'),1)
 return s
runtime=patch(norm(original['war3map.j']));(O/'war3map.j').write_text(runtime,encoding='utf8')
before=functions(norm(original['war3map.j']));after=functions(runtime)
changed=[n for n in before if before[n]!=after[n]]
assert set(changed)=={'P67_HeroRate','P67_Refresh','P67_Start'}
added=sorted(set(after)-set(before));assert added==['P78_Rate']
assert before['C77_ColoLevel']==after['C77_ColoLevel']
assert before['FFGS_ApplyUnit']==after['FFGS_ApplyUnit']
# The map inherits stock cumulative thresholds; reject silent changes to that assumption.
assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h))
misc=norm(read_storm(h,'war3mapMisc.txt'));assert storm.SFileCloseArchive(h)
assert not re.search(r'(?m)^NeedHeroXP',misc)
(R/'changes.json').write_text(json.dumps(dict(base=str(BASE),base_sha256=digest(BASE.read_bytes()),changed_functions=changed,added_functions=added),indent=2))
w=original['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[];edited=0
while p<len(w):
 n=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+n];p+=n
 s=norm(b.rstrip(b'\0'))
 patched=patch(s)
 if patched!=s:
  b=patched.encode('utf8')+(b'\0' if b.endswith(b'\0') else b'');edited+=1
 chunks.append(b)
assert edited==2 and p==len(w)
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(norm(b.rstrip(b'\0')) for b in chunks);ef=functions(editor)
assert all(ef[n]==after[n] for n in changed+added)
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1]
packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
names=lambda s:set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',s,re.M))
known=names(header);extras=[]
for line in packed.splitlines():
 m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
 if m and m[1] not in known and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:ef.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')
subprocess.run([sys.executable,str(R/'verify.py')],check=True,cwd=W)
cases=json.loads((R/'checks.json').read_text())
tool=Path('C:/Users/User/Documents/Codex/2026-10-28/thi/work')
def run(args,log,success):
 r=subprocess.run(list(map(str,args)),cwd=R,capture_output=True,text=True,errors='replace',timeout=90)
 output=r.stdout+r.stderr;(R/log).write_text(output);assert r.returncode==0 and success in output,output[-3000:]
run([tool/'jasshelper/pjass.exe',tool/'common.j',tool/'Blizzard.j',O/'war3map.j'],'compiler.log','Parse successful:')
run([tool/'jasshelper/clijasshelper.exe','--scriptonly',tool/'common.j',tool/'Blizzard.j',R/'editor-validation.j',R/'editor-compiled.j'],'jasshelper.log','Success!')
run([tool/'jasshelper/pjass.exe',tool/'common.j',tool/'Blizzard.j',R/'editor-compiled.j'],'editor-compiler.log','Parse successful:')
headers=[b.rstrip(b'\0') for b in chunks if re.search(rb'(?m)^globals\b',b)]
runtimes=[b.rstrip(b'\0') for b in chunks if old.encode() in b];assert len(headers)==len(runtimes)==1
sm=json.loads(norm(original['FF_SOURCE_MANIFEST.json']));sm.update(compiled_source_sha256=digest((O/'war3map.j').read_bytes()),globals_sha256=digest(headers[0]),runtime_sha256=digest(runtimes[0]),runtime_functions=len(functions(norm(runtimes[0]))),source_map_sha256=digest(BASE.read_bytes()),revision='v78 proportional individual level-10 catch-up after first level-10 hero',engine_playtest=False)
(O/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(sm,indent=2),encoding='utf8')
sd=O/'source_roundtrip';sd.mkdir(exist_ok=True)
(sd/'globals.j').write_bytes(headers[0]);(sd/'FF_Runtime.j').write_bytes(runtimes[0])
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\n\nv78 normal Pub: keep 70-percent kill XP at levels 7+ until first active registered primary hero reaches 10. Permanently unlock individual level-7-to-9 catch-up: rate = 70 + 40 * (10 - fractional hero level), based on actual cumulative XP thresholds 2700/3500/4400/5400. Ends individually at 10; below-7 rules preserved. Leader allies follow the same individual curve. All rewards still require kills. Native handicap refreshed every second and immediately on levels; scripted supplements calculate from current XP. Anti-cheat 25-percent override remains authoritative. Runtime and WCT synchronized. Engine playtest pending.\n')
out=R/'release/FF799X_Rx_Level10_Catchup_v78_TEST.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(BASE,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
payloads={str(f.relative_to(O)).replace('/','\\'):f for f in O.rglob('*') if f.is_file()}
for n,f in payloads.items():assert storm.SFileAddFileEx(h,str(f),n.encode(),0x80000200,2,2)
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint]
if archive(BASE).get_hash_table_entry('(attributes)'):assert storm.SFileRemoveFile(h,b'(attributes)',0)
assert storm.SFileCloseArchive(h)
ba,aa=archive(BASE),archive(out);be,ae=entries(ba),entries(aa);allowed=set()
for n in list(payloads)+['(listfile)','(attributes)','(signature)']:
 for ar in [ba,aa]:
  e=ar.get_hash_table_entry(n)
  if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(ae.get(k)==v for k,v in be.items() if k not in allowed)
assert all(k in be or k in allowed for k in ae)
assert storm.SFileOpenArchive(str(out),0,256,c.byref(h))
for n,f in payloads.items():assert read_storm(h,n)==f.read_bytes()
assert storm.SFileCloseArchive(h)
report=dict(output=str(out),sha256=digest(out.read_bytes()),base=str(BASE),changed_functions=changed,added_functions=added,checks=cases,unrelated_entries_preserved=sum(k not in allowed for k in be),runtime_compiler='passed',editor_compiler='passed',post7_xp_percent=70,engine_playtested=False,installed_or_deployed=False)
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
