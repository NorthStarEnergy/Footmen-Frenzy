"""Import only Veigar v69 artwork, preserving v80 gameplay and editor source."""
from pathlib import Path
import hashlib, json, re, shutil, struct, subprocess, sys
R=Path(__file__).resolve().parent; W=R.parent; O=R/'src'; O.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive, entries, functions, storm, read_storm, c
BASE=W/'fed-rewards-v80/release/FF799X_Rx_Fed_Rewards_v80_TEST.w3x'
digest=lambda b:hashlib.sha256(b).hexdigest()
assert digest(BASE.read_bytes())==json.loads((W/'fed-rewards-v80/verification.json').read_text())['sha256']
norm=lambda b:b.decode('utf-8-sig').replace('\r','')
h=c.c_void_p(); assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h))
original={n:read_storm(h,n) for n in ['war3map.j','war3map.wct','war3map.imp','FF_MAINTENANCE.md','FF_SOURCE_MANIFEST.json']}
assert storm.SFileCloseArchive(h)
helper=(R/'orb-impact.j').read_text().strip()
replacements={
 'VG_DarkImpact':[(r'war3mapImported\\DarkNova.mdx',r'Spells\\Veigar69\\MeteorImpact.mdx'),('BlzSetSpecialEffectColor(fx, 180, 95, 255)','BlzSetSpecialEffectColor(fx, 255, 255, 255)')],
 'VG_Tick':[(r'war3mapImported\\DarknessBomb.mdx',r'Spells\\Veigar69\\Meteor.mdx'),('BlzSetSpecialEffectColor(fx, 150, 65, 255)','BlzSetSpecialEffectColor(fx, 255, 255, 255)')],
 'VG_ClassicCast':[(r'call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilSpecialArt.mdl", target, "chest"))',r'call VG81_OrbImpact(target, "Spells\\Veigar69\\BalefulOrb.mdx")'),(r'call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DeathPact\\DeathPactTarget.mdl", target, "origin"))',r'call VG81_OrbImpact(target, "Spells\\Veigar69\\PrimordialOrb.mdx")')]
}
def patch(s):
 fs=functions(s)
 if 'VG_ClassicCast' not in fs:return s
 assert 'VG81_OrbImpact' not in fs
 for name,edits in replacements.items():
  old=fs[name]; new=old
  for a,b in edits:
   assert new.count(a)==1,(name,a)
   new=new.replace(a,b)
  s=s.replace(old,(helper+'\n\n' if name=='VG_ClassicCast' else '')+new,1)
 return s
# Patch the authoritative World Editor source before the compiled script.
w=original['war3map.wct']; p=w.index(0,8)+1; prefix=w[:p]; chunks=[]; edited=0
while p<len(w):
 n=struct.unpack_from('<I',w,p)[0]; p+=4; b=w[p:p+n]; p+=n
 s=norm(b.rstrip(b'\0')); updated=patch(s)
 if updated!=s:
  b=updated.encode()+(b'\0' if b.endswith(b'\0') else b''); edited+=1
 chunks.append(b)
assert p==len(w) and edited==1
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
runtime=patch(norm(original['war3map.j'])); (O/'war3map.j').write_text(runtime,encoding='utf8')
before=functions(norm(original['war3map.j'])); after=functions(runtime)
assert set(after)-set(before)=={'VG81_OrbImpact'} and not set(before)-set(after)
assert {n for n in before if before[n]!=after[n]}==set(replacements)
# Reversing exactly the approved visual edits must restore every original function.
for name,edits in replacements.items():
 restored=after[name]
 for a,b in edits:restored=restored.replace(b,a)
 assert restored==before[name],name
editor='\n'.join(norm(b.rstrip(b'\0')) for b in chunks); ef=functions(editor)
assert all(ef[n]==after[n] for n in list(replacements)+['VG81_OrbImpact'])
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1]
packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
names=lambda s:set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',s,re.M))
known=names(header); extras=[]
for line in packed.splitlines():
 m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
 if m and m[1] not in known and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:ef.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')
tool=Path('C:/Users/User/Documents/Codex/2026-10-28/thi/work')
def run(args,log,success):
 r=subprocess.run(list(map(str,args)),cwd=R,capture_output=True,text=True,errors='replace',timeout=90)
 output=r.stdout+r.stderr; (R/log).write_text(output); assert r.returncode==0 and success in output,output[-3000:]
run([tool/'jasshelper/pjass.exe',tool/'common.j',tool/'Blizzard.j',O/'war3map.j'],'compiler.log','Parse successful:')
run([tool/'jasshelper/clijasshelper.exe','--scriptonly',tool/'common.j',tool/'Blizzard.j',R/'editor-validation.j',R/'editor-compiled.j'],'jasshelper.log','Success!')
run([tool/'jasshelper/pjass.exe',tool/'common.j',tool/'Blizzard.j',R/'editor-compiled.j'],'editor-compiler.log','Parse successful:')
assert json.loads((R/'model-checks.json').read_text())['passed']
assets=[]
for name in ['BalefulOrb','PrimordialOrb','Meteor','MeteorImpact']:
 rel=Path('Spells/Veigar69')/(name+'.mdx'); dest=O/rel; dest.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(W/'Transfer/veigar-refine-v69-work/edited'/rel,dest); assets.append(str(rel).replace('/','\\'))
imp=original['war3map.imp']; version,count=struct.unpack_from('<II',imp); p=8; existing=[]
for _ in range(count):
 flag=imp[p]; p+=1; end=imp.index(0,p); name=imp[p:end].decode('latin1'); p=end+1
 existing.append(name if flag in [10,13] else 'war3mapImported\\'+name)
assert p==len(imp) and not set(assets)&set(existing)
(O/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(assets))+imp[8:]+b''.join(b'\x0d'+n.encode()+b'\0' for n in assets))
headers=[b.rstrip(b'\0') for b in chunks if re.search(rb'(?m)^globals\b',b)]
runtimes=[b.rstrip(b'\0') for b in chunks if b'function VG81_OrbImpact' in b]; assert len(headers)==len(runtimes)==1
sm=json.loads(norm(original['FF_SOURCE_MANIFEST.json'])); sm.update(compiled_source_sha256=digest((O/'war3map.j').read_bytes()),globals_sha256=digest(headers[0]),runtime_sha256=digest(runtimes[0]),runtime_functions=len(functions(norm(runtimes[0]))),source_map_sha256=digest(BASE.read_bytes()),revision='v81 Veigar visual-only asset integration',engine_playtest=False)
(O/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(sm,indent=2),encoding='utf8')
sd=O/'source_roundtrip'; sd.mkdir(exist_ok=True); (sd/'globals.j').write_bytes(headers[0]); (sd/'FF_Runtime.j').write_bytes(runtimes[0])
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\n\nv81: Four Veigar69 models imported. Q/R use 0.30-second target-attached orb flashes with the existing effect cleanup; damage remains immediate. Dark Matter uses the blue meteor and impact with neutral tint. No projectile gameplay, balance, hotkey, icon, cage, or TF changes. Engine visual verification pending.\n')
out=R/'release/FF799X_Rx_Veigar_Visuals_v81_TEST.w3x'; out.parent.mkdir(exist_ok=True); shutil.copy2(BASE,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
payloads={str(f.relative_to(O)).replace('/','\\'):f for f in O.rglob('*') if f.is_file()}
for n,f in payloads.items():assert storm.SFileAddFileEx(h,str(f),n.encode(),0x80000200,2,2),n
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint]
if archive(BASE).get_hash_table_entry('(attributes)'):assert storm.SFileRemoveFile(h,b'(attributes)',0)
assert storm.SFileCloseArchive(h)
ba,aa=archive(BASE),archive(out); be,ae=entries(ba),entries(aa); allowed=set()
for n in list(payloads)+['(listfile)','(attributes)','(signature)']:
 for ar in [ba,aa]:
  e=ar.get_hash_table_entry(n)
  if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(ae.get(k)==v for k,v in be.items() if k not in allowed)
assert all(k in be or k in allowed for k in ae)
assert storm.SFileOpenArchive(str(out),0,256,c.byref(h))
for n,f in payloads.items():assert read_storm(h,n)==f.read_bytes(),n
assert storm.SFileCloseArchive(h)
report=dict(output=str(out),sha256=digest(out.read_bytes()),base=str(BASE),base_sha256=digest(BASE.read_bytes()),changed_functions=list(replacements),added_functions=['VG81_OrbImpact'],assets=assets,unrelated_entries_preserved=sum(k not in allowed for k in be),gameplay_functions_restored_by_reversing_visual_edits=True,all_object_data_unchanged=True,runtime_compiler='passed',editor_compiler='passed',engine_playtested=False,installed_or_deployed=False)
(R/'verification.json').write_text(json.dumps(report,indent=2)); out.with_suffix('.sha256').write_text(report['sha256']+'  '+out.name+'\n'); print(json.dumps(report,indent=2))
