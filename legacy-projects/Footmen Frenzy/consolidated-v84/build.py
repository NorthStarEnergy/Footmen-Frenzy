"""Consolidate verified latest 799X branches without dropping v83 content."""
from pathlib import Path
import hashlib, json, re, shutil, struct, subprocess, sys
R=Path(__file__).resolve().parent; W=R.parent; O=R/'src'; O.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive, entries, functions, storm, read_storm, c
BASE=W/'veigar-ultimate-v83/release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x'
digest=lambda b:hashlib.sha256(b).hexdigest()
assert digest(BASE.read_bytes())==json.loads((W/'veigar-ultimate-v83/verification.json').read_text())['sha256']
norm=lambda b:b.decode('utf-8-sig').replace('\r','')
h=c.c_void_p(); assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h))
original={n:read_storm(h,n) for n in ['war3map.j','war3map.wct','war3map.imp','FF_MAINTENANCE.md','FF_SOURCE_MANIFEST.json']}
assert storm.SFileCloseArchive(h)
DONOR=Path('C:/Users/User/Documents/Warcraft III/Maps/Test/FF799X_Rx_Ghoul_Grunt_Buff_v69.w3x')
GUARDIAN=W/'guardian-visuals-v68/FF799X_Rx_Veigar_GuardianVisuals_v68.w3x'
DARK=W/'dark-matter-icon-v68/FF799X_Rx_Veigar_Classic_v68_DarkMatterIcon.w3x'
def read_map(path,name):
 h=c.c_void_p(); assert storm.SFileOpenArchive(str(path),0,256,c.byref(h))
 data=read_storm(h,name); assert storm.SFileCloseArchive(h); return data
assert digest(DONOR.read_bytes())=='3a7fa707aacf1ccaee6e17683758f6a2f59cb5fa04c8baad39b9508c9e0363ca'
for folder,path in [('guardian-visuals-v68',GUARDIAN),('dark-matter-icon-v68',DARK)]:
 assert digest(path.read_bytes())==json.loads((W/folder/'verification.json').read_text())['sha256']
df=functions(norm(read_map(DONOR,'war3map.j'))); gf=functions(norm(read_map(GUARDIAN,'war3map.j')))
replacements={n:df[n] for n in ['FFGS_InitSettings','Trig_set_spawn_variables_Actions']}
replacements.update({n:gf[n] for n in ['TFP_FFDP_OnCast','GD_Cast']})
def patch(s):
 fs=functions(s)
 for name,new in replacements.items():
  if name in fs:s=s.replace(fs[name],new,1)
 return s
# Patch the authoritative World Editor source before the compiled script.
w=original['war3map.wct']; p=w.index(0,8)+1; prefix=w[:p]; chunks=[]; edited=0
while p<len(w):
 n=struct.unpack_from('<I',w,p)[0]; p+=4; b=w[p:p+n]; p+=n
 s=norm(b.rstrip(b'\0')); updated=patch(s)
 if updated!=s:
  b=updated.encode()+(b'\0' if b.endswith(b'\0') else b''); edited+=1
 chunks.append(b)
assert p==len(w) and edited>=1
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
runtime=patch(norm(original['war3map.j'])); (O/'war3map.j').write_text(runtime,encoding='utf8')
before=functions(norm(original['war3map.j'])); after=functions(runtime)
assert set(after)==set(before) and not set(before)-set(after)
assert {n for n in before if before[n]!=after[n]}==set(replacements)
editor='\n'.join(norm(b.rstrip(b'\0')) for b in chunks); ef=functions(editor)
assert all(ef[n]==after[n] for n in list(replacements))
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
# Merge the installed unit buff fields onto v83, preserving all newer objects.
import objdata, copy
for label,path in [('base',BASE),('installed',DONOR),('guardian',GUARDIAN)]:
 (R/(label+'.w3u')).write_bytes(read_map(path,'war3map.w3u'))
data=objdata.load(str(R/'base.w3u'));donor=objdata.load(str(R/'installed.w3u'));guard=objdata.load(str(R/'guardian.w3u'))
records=lambda d:{(e['oldId'],e['newId']):e for tab in d['tables'] for e in tab}
drec=records(donor); changes=[]
for key,e in records(data).items():
 if key[0] in ['ogru','ugho'] and key[1]=='\0'*4:
  dm={m['id']:m for m in drec[key]['mods']}
  for m in e['mods']:
   if m['id'] in ['udef','ua1b','uhpm']:
    changes.append([key[0],m['id'],m['value'],dm[m['id']]['value']]);m.update(copy.deepcopy(dm[m['id']]))
assert len(changes)==6
pylons=[e for tab in guard['tables'] for e in tab if e['newId']=='hGpy'];assert len(pylons)==1
assert not any(e['newId']=='hGpy' for tab in data['tables'] for e in tab)
data['tables'][1].append(copy.deepcopy(pylons[0]));(O/'war3map.w3u').write_bytes(objdata.dump(data))
assets=[]
for folder,path,key in [('guardian-visuals-v68',GUARDIAN,'changed_members'),('dark-matter-icon-v68',DARK,'replaced_members')]:
 for n in json.loads((W/folder/'verification.json').read_text())[key]:
  if n.endswith(('.blp','.mdx')):
   dest=O/n.replace('\\','/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(read_map(path,n));assets.append(n)
imp=original['war3map.imp'];version,count=struct.unpack_from('<II',imp);p=8;existing=[]
for _ in range(count):
 flag=imp[p];p+=1;end=imp.index(0,p);name=imp[p:end].decode('latin1');p=end+1
 existing.append(name if flag in [10,13] else 'war3mapImported\\'+name)
assert p==len(imp)
added=[n for n in assets if n not in existing]
(O/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(added))+imp[8:]+b''.join(b'\x0d'+n.encode()+b'\0' for n in added))
wts=read_map(BASE,'war3map.wts')
wts,n=re.subn(rb'(STRING 1\s*\{\s*)[^\r\n]+',lambda m:m[1]+b'Footmen Frenzy 799X v84 - Consolidated Test',wts,count=1);assert n==1
(O/'war3map.wts').write_bytes(wts)
(R/'merge-changes.json').write_text(json.dumps({'functions':list(replacements),'unit_fields':changes,'new_unit':'hGpy','assets':assets,'imports_added':added},indent=2))
headers=[b.rstrip(b'\0') for b in chunks if re.search(rb'(?m)^globals\b',b)]
runtimes=[b.rstrip(b'\0') for b in chunks if b'function VG82_UpdateCounter' in b]; assert len(headers)==len(runtimes)==1
sm=json.loads(norm(original['FF_SOURCE_MANIFEST.json'])); sm.update(compiled_source_sha256=digest((O/'war3map.j').read_bytes()),globals_sha256=digest(headers[0]),runtime_sha256=digest(runtimes[0]),runtime_functions=len(functions(norm(runtimes[0]))),source_map_sha256=digest(BASE.read_bytes()),revision='v84 consolidated latest 799X',engine_playtest=False)
(O/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(sm,indent=2),encoding='utf8')
sd=O/'source_roundtrip'; sd.mkdir(exist_ok=True); (sd/'globals.j').write_bytes(headers[0]); (sd/'FF_Runtime.j').write_bytes(runtimes[0])
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\n\nv84: Consolidated v83 with installed v68 spawn intervals/v69 Ghoul-Grunt buffs and completed Guardian dome/pylon/icon and Dark Matter icon branches. All v83 gameplay retained except the two explicitly merged spawn settings functions. Solo four-player variant and explicitly excluded casino/profile prototypes remain separate. Runtime/editor/archive checks passed; engine playtest pending.\n')
out=R/'release/FF799X_Rx_Consolidated_v84_TEST.w3x'; out.parent.mkdir(exist_ok=True); shutil.copy2(BASE,out)
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
report=dict(output=str(out),sha256=digest(out.read_bytes()),base=str(BASE),base_sha256=digest(BASE.read_bytes()),changed_functions=list(replacements),added_functions=[],unrelated_entries_preserved=sum(k not in allowed for k in be),per_hero_stacks=True,runtime_compiler='passed',editor_compiler='passed',engine_playtested=False,installed_or_deployed=False)
(R/'verification.json').write_text(json.dumps(report,indent=2)); out.with_suffix('.sha256').write_text(report['sha256']+'  '+out.name+'\n'); print(json.dumps(report,indent=2))


