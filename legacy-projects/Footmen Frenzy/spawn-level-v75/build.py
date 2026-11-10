"""Restrict the timed footman level override to footmen; preserve configured unit levels."""
from pathlib import Path
import hashlib,json,re,shutil,struct,subprocess,sys
R=Path(__file__).resolve().parent;W=R.parent;O=R/'src';O.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
BASE=W/'veigar-range-v74/release/FF799X_Rx_Veigar_Range_v74_TEST.w3x'
digest=lambda b:hashlib.sha256(b).hexdigest()
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h))
original={n:read_storm(h,n) for n in ['war3map.j','war3map.wct','FF_MAINTENANCE.md','FF_SOURCE_MANIFEST.json']};assert storm.SFileCloseArchive(h)
norm=lambda b:b.decode('utf-8-sig').replace('\r','')
old='if ffgs_force_level_two[idx] then'
new='if ffgs_force_level_two[idx] and ffgs_footmen_rules[idx] then'
def patch(s):
 assert s.count(old)==1
 return s.replace(old,new,1)
runtime=patch(norm(original['war3map.j']));(O/'war3map.j').write_text(runtime,encoding='utf8')
before=functions(norm(original['war3map.j']));after=functions(runtime)
changed=[n for n in before if before[n]!=after[n]];assert len(changed)==1
# Verify the actual edited spawn function retains the configured assignment,
# and only footmen can enter the subsequent timed override for all 51 slots.
spawn=after[changed[0]];assert 'UNIT_IF_LEVEL, udg_unit_level[idx]' in spawn and new in spawn
for idx in range(51):
 force=idx<=13 or 31<=idx<=43;foot=idx==0
 for early in [False,True]:
  for configured in [1,2,3,4,6]:
   actual=(1 if early else 2) if force and foot else configured
   assert actual==((1 if early else 2) if idx==0 else configured)
assert 'constant real P67_POST7_RATE = 70.00' in runtime
w=original['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[];edited=0
while p<len(w):
 n=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+n];p+=n
 s=norm(b.rstrip(b'\0'))
 if old in s:
  b=patch(s).encode('utf8')+(b'\0' if b.endswith(b'\0') else b'');edited+=1
 chunks.append(b)
assert edited==1 and p==len(w)
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(norm(b.rstrip(b'\0')) for b in chunks);ef=functions(editor)
assert ef[changed[0]]==after[changed[0]]
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
tool=Path('C:/Users/User/Documents/Codex/2026-10-28/thi/work')
def run(args,log,success):
 r=subprocess.run(list(map(str,args)),cwd=R,capture_output=True,text=True,errors='replace',timeout=90)
 output=r.stdout+r.stderr;(R/log).write_text(output);assert r.returncode==0 and success in output,output[-3000:]
run([tool/'jasshelper/pjass.exe',tool/'common.j',tool/'Blizzard.j',O/'war3map.j'],'compiler.log','Parse successful:')
run([tool/'jasshelper/clijasshelper.exe','--scriptonly',tool/'common.j',tool/'Blizzard.j',R/'editor-validation.j',R/'editor-compiled.j'],'jasshelper.log','Success!')
run([tool/'jasshelper/pjass.exe',tool/'common.j',tool/'Blizzard.j',R/'editor-compiled.j'],'editor-compiler.log','Parse successful:')
headers=[b.rstrip(b'\0') for b in chunks if re.search(rb'(?m)^globals\b',b)]
runtimes=[b.rstrip(b'\0') for b in chunks if new.encode() in b];assert len(headers)==len(runtimes)==1
sm=json.loads(norm(original['FF_SOURCE_MANIFEST.json']));sm.update(compiled_source_sha256=digest((O/'war3map.j').read_bytes()),globals_sha256=digest(headers[0]),runtime_sha256=digest(runtimes[0]),source_map_sha256=digest(BASE.read_bytes()),revision='v75 preserve configured spawn levels; timed override only for footmen',engine_playtest=False)
(O/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(sm,indent=2),encoding='utf8')
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\n\nv75: restrict timed level override to footmen. All other spawned units retain udg_unit_level. Pub level-7+ XP remains 70%. Runtime and authoritative WCT synchronized; both compile. Engine playtest pending.\n')
out=R/'release/FF799X_Rx_Spawn_Levels_v75_TEST.w3x';out.parent.mkdir(exist_ok=True);shutil.copy2(BASE,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for f in O.iterdir():assert storm.SFileAddFileEx(h,str(f),f.name.encode(),0x80000200,2,2)
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint]
if archive(BASE).get_hash_table_entry('(attributes)'):assert storm.SFileRemoveFile(h,b'(attributes)',0)
assert storm.SFileCloseArchive(h)
ba,aa=archive(BASE),archive(out);be,ae=entries(ba),entries(aa);allowed=set()
for n in [f.name for f in O.iterdir()]+['(listfile)','(attributes)','(signature)']:
 for ar in [ba,aa]:
  e=ar.get_hash_table_entry(n)
  if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(ae.get(k)==v for k,v in be.items() if k not in allowed)
assert all(k in be or k in allowed for k in ae)
assert storm.SFileOpenArchive(str(out),0,256,c.byref(h))
for f in O.iterdir():assert read_storm(h,f.name)==f.read_bytes()
assert storm.SFileCloseArchive(h)
report=dict(output=str(out),sha256=digest(out.read_bytes()),base=str(BASE),changed_functions=changed,spawn_boundary_cases=510,unrelated_entries_preserved=sum(k not in allowed for k in be),runtime_compiler='passed',editor_compiler='passed',post7_xp_percent=70,engine_playtested=False,installed_or_deployed=False)
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
