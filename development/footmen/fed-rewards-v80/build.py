"""Capped rewards for fed heroes farming weaker teams."""
from pathlib import Path
import hashlib,json,re,shutil,struct,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;O=R/'src';O.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
BASE=W/'colo-lag-v79/release/FF799X_Rx_Colo_Lag_v79_TEST.w3x'
digest=lambda b:hashlib.sha256(b).hexdigest()
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h))
original={n:read_storm(h,n) for n in ['war3map.j','war3map.wct','FF_MAINTENANCE.md','FF_SOURCE_MANIFEST.json']};assert storm.SFileCloseArchive(h)
norm=lambda b:b.decode('utf-8-sig').replace('\r','')
old='function P80_Curve takes real ownLevel, real opposingLevel returns real'
helper=(R/'rewards.j').read_text(encoding='utf8')
extra_globals=(R/'globals.j').read_text(encoding='utf8').strip()
def patch(s):
 anchor='boolean P78_Reached10 = false'
 if anchor in s:
  assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n'+extra_globals,1)
 fs=functions(s)
 if 'P67_Refresh' not in fs:return s
 f=fs['P67_Refresh']
 s=s.replace(f,helper+'\n'+f.replace('    if not P67_Running or not P67_Enabled() then','    call P80_Sync()\n    if not P67_Running or not P67_Enabled() then').replace('call SetPlayerHandicapXPBJ(Player(pn - 1), P67_HeroRate(u))','call SetPlayerHandicapXPBJ(Player(pn - 1), 0.00)'),1)
 f=fs['InitTrig_FF_Runtime'];s=s.replace(f,f.replace('    call FFLoadTrace_Mark', '    call P80_Init()\n    call FFLoadTrace_Mark',1),1)
 f=fs['P67_Start'];s=s.replace(f,f.replace('    set P67_Running = true','    call P80_Start()\n    set P67_Running = true'),1)
 f=fs['P67_AddSupplement']
 s=s.replace(f,f.replace('real amount returns','real amount, unit victim returns').replace('amount * P67_HeroRate(u) * 0.01','amount * P67_HeroRate(u) * 0.01 * P80_Factor(u, victim)'),1)
 # Every supplement is called synchronously from a death event.
 import re
 s=re.sub(r'(call P67_AddSupplement\([^\n]+)\)',r'\1, GetDyingUnit())',s)
 f=fs['Trig_Multiboard_Update_Actions'];new=f
 for line in f.splitlines():
  if 'call AdjustPlayerStateBJ(R2I(' in line and 'PLAYER_STATE_RESOURCE_GOLD)' in line:
   lead,rest=line.split('call AdjustPlayerStateBJ(',1)
   amount,tail=rest.split(', ConvertedPlayer(udg_pn_killer)',1)
   new=new.replace(line,lead+'call AdjustPlayerStateBJ(P80_Gold(ConvertedPlayer(udg_pn_killer), udg_temp_dying_unit, '+amount+'), ConvertedPlayer(udg_pn_killer)'+tail)
 assert new.count('P80_Gold(')==4
 s=s.replace(f,new,1)
 f=fs['Trig_MH_shop_click_Actions']
 s=s.replace(f,f.replace('call SetPlayerHandicapXPBJ(GetTriggerPlayer(), 25.00)','if P80_Running and P67_Enabled() then\n            call SetPlayerHandicapXPBJ(GetTriggerPlayer(), 0.00)\n        else\n            call SetPlayerHandicapXPBJ(GetTriggerPlayer(), 25.00)\n        endif'),1)
 return s
runtime=patch(norm(original['war3map.j']));(O/'war3map.j').write_text(runtime,encoding='utf8')
before=functions(norm(original['war3map.j']));after=functions(runtime)
changed=[n for n in before if before[n]!=after[n]]
assert len(changed)==11,changed
added=sorted(set(after)-set(before));assert set(added)==set(functions(helper))
assert before['C77_ColoLevel']==after['C77_ColoLevel']
assert before['P78_Rate']==after['P78_Rate']
assert before['FFGS_ApplyUnit']==after['FFGS_ApplyUnit']
assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h))
misc=norm(read_storm(h,'war3mapMisc.txt'));assert storm.SFileCloseArchive(h)
assert not re.search(r'(?m)^(NeedHeroXP|GrantNormalXP)',misc)
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
sm=json.loads(norm(original['FF_SOURCE_MANIFEST.json']));sm.update(compiled_source_sha256=digest((O/'war3map.j').read_bytes()),globals_sha256=digest(headers[0]),runtime_sha256=digest(runtimes[0]),runtime_functions=len(functions(norm(runtimes[0]))),source_map_sha256=digest(BASE.read_bytes()),revision='v80 capped XP and gold reduction against weaker teams',engine_playtest=False)
(O/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(sm,indent=2),encoding='utf8')
sd=O/'source_roundtrip';sd.mkdir(exist_ok=True)
(sd/'globals.j').write_bytes(headers[0]);(sd/'FF_Runtime.j').write_bytes(runtimes[0])
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\n\nv80 normal Pub: per-recipient kill XP and killer-owner bounty scaled by fractional level lead over the victim team average. One level free, 15 percent reduction per additional level, capped at 60 percent; starts at level 7. Stronger hero victims raise the baseline. Structures and neutral colos exempt. Native player XP and player-victim bounty replaced by explicit kill payouts to avoid XP rollback; existing supplements and winning-factor bounty also scaled. Runtime engine playtest pending.\n')
out=R/'release/FF799X_Rx_Fed_Rewards_v80_TEST.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(BASE,out)
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
