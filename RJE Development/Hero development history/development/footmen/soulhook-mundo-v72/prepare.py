"""Merge and repair Soul Hook on the combined UI/Mundo/Stalker test map."""
from pathlib import Path
import copy, hashlib, json, re, struct, sys
R=Path(__file__).resolve().parent; W=R.parent; O=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
BASE=W/'Transfer/UI_Mundo_Stalker_Fixed/FF799X_Rx_UI_Mundo_Stalker_Fixed_Test.w3x'
ANCESTOR=W/'Transfer/Veigar_Classic_v68/FF799X_Rx_Veigar_Classic_v68.w3x'
DONOR=W/'soulhook-v70-review/actual/FF799X_Rx_DemonKnight_SoulHook_v70.w3x'
names=['war3map.j','war3map.wct','war3map.w3a','war3map.w3u','FF_MAINTENANCE.md']
def readmap(p):
 h=c.c_void_p();assert storm.SFileOpenArchive(str(p),0,0x100,c.byref(h))
 d={n:read_storm(h,n) for n in names};assert storm.SFileCloseArchive(h);return d
old,donor,base=map(readmap,[ANCESTOR,DONOR,BASE]); norm=lambda b:b.decode('utf-8-sig').replace('\r','')
af=functions(norm(old['war3map.j'])); df=functions(norm(donor['war3map.j']));bf=functions(norm(base['war3map.j']))
changed=[n for n in af if af[n]!=df[n]];added=[n for n in df if n not in af]
assert changed==['DK_Free','DK_Tick','DK_OnCast','DK_Init']
assert added==['DK_HookStun','DK_HookChain','DK_HookCatch','DK_HookCast']
assert all(bf[n]==af[n] for n in changed+['DK_AxeArea'])
hook=dict((n,df[n]) for n in added)
f=hook['DK_HookCatch']
f=f.replace('takes integer i returns nothing','takes integer i, real ox, real oy returns nothing',1)
f=f.replace('    local real dx\n','    local real dx\n    local real sx = DK_X[i]-ox\n    local real sy = DK_Y[i]-oy\n    local real length2 = sx*sx+sy*sy\n    local real projection\n    local real vx\n    local real vy\n',1)
f=f.replace('call GroupEnumUnitsInRange(g, DK_X[i], DK_Y[i], 150.0, null)', 'call GroupEnumUnitsInRange(g, (ox+DK_X[i])*0.5, (oy+DK_Y[i])*0.5, 150.0+SquareRoot(length2)*0.5, null)',1)
f=f.replace('        if FS_Enemy(v, DK_Owner[i]) and not IsUnitInGroup(v, DK_Hit[i]) and LoadInteger(DK_Hash, GetHandleId(v), -32) == 0 then', '''        set projection = 0.0
        if length2 > 0.01 then
            set projection = RMaxBJ(0.0, RMinBJ(1.0, ((GetUnitX(v)-ox)*sx+(GetUnitY(v)-oy)*sy)/length2))
        endif
        set vx = GetUnitX(v)-(ox+projection*sx)
        set vy = GetUnitY(v)-(oy+projection*sy)
        if vx*vx+vy*vy <= 22500.0 and FS_Enemy(v, DK_Owner[i]) and not IsUnitInGroup(v, DK_Hit[i]) then''',1)
f=f.replace('            if amount > 1.0 then\n                set pull = DK_New(12, DK_Source[i])', '''            if amount > 1.0 then
                // Most recent Demon Knight pull wins; each hook still deals its own hit.
                call DK_Free(LoadInteger(DK_Hash, GetHandleId(v), -3))
                call DK_Free(LoadInteger(DK_Hash, GetHandleId(v), -32))
                set pull = DK_New(12, DK_Source[i])''',1)
hook['DK_HookCatch']=f
tick=df['DK_Tick'];anchor='''                    set DK_X[i] = DK_X[i]+DK_DX[i]*step
                    set DK_Y[i] = DK_Y[i]+DK_DY[i]*step'''
assert tick.count(anchor)==1
tick=tick.replace(anchor,'''                    set ox = DK_X[i]
                    set oy = DK_Y[i]
                    set DK_X[i] = DK_X[i]+DK_DX[i]*step
                    set DK_Y[i] = DK_Y[i]+DK_DY[i]*step''')
assert tick.count('                    call DK_HookCatch(i)')==1
tick=tick.replace('                    call DK_HookCatch(i)','''                    if not DK_Return[i] then
                        call DK_HookCatch(i, ox, oy)
                    endif''')
axe=bf['DK_AxeArea'];needle='                call DK_Free(LoadInteger(DK_Hash, GetHandleId(v), -3))'
assert axe.count(needle)==1
axe=axe.replace(needle,needle+'\n                call DK_Free(LoadInteger(DK_Hash, GetHandleId(v), -32))')
replacements={n:df[n] for n in changed};replacements.update(DK_Tick=tick,DK_AxeArea=axe)
def patch(s):
 fs=functions(s)
 for n,new in replacements.items():
  if n in fs:
   assert fs[n]==af[n],('Conflicting script function',n)
   s=s.replace(fs[n],new,1)
 fs=functions(s)
 if 'DK_Tick' in fs:
  assert not any(n in fs for n in added)
  s=s.replace(fs['DK_Tick'],'\n\n'.join(hook[n] for n in added)+'\n\n'+fs['DK_Tick'],1)
 return s
runtime=patch(norm(base['war3map.j']));O.mkdir(exist_ok=True);(O/'war3map.j').write_text(runtime,encoding='utf8')
rf=functions(runtime);assert all(rf[n]==f for n,f in bf.items() if n not in replacements)
w=base['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[]
while p<len(w):
 size=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+size];p+=size
 s=norm(b.rstrip(b'\0'));patched=patch(s)
 chunks.append((patched.encode('utf8')+(b'\0' if b.endswith(b'\0') else b'')) if patched!=s else b)
assert p==len(w);(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(norm(b.rstrip(b'\0')) for b in chunks);ef=functions(editor)
for n in list(replacements)+added:assert ef[n]==rf[n],n
headers=[b.rstrip(b'\0') for b in chunks if re.search(rb'(?m)^globals\b',b)]
runtimes=[b.rstrip(b'\0') for b in chunks if b'function DK_HookCatch takes' in b]
assert len(headers)==len(runtimes)==1
# Refresh the archive's embedded source snapshots, which were stale in the inherited map.
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,0x100,c.byref(h))
source_manifest=json.loads(read_storm(h,'FF_SOURCE_MANIFEST.json').decode('utf-8-sig'));assert storm.SFileCloseArchive(h)
source_dir=O/'source_roundtrip';source_dir.mkdir(exist_ok=True)
(source_dir/'globals.j').write_bytes(headers[0]);(source_dir/'FF_Runtime.j').write_bytes(runtimes[0])
source_manifest.update(compiled_source_sha256=hashlib.sha256((O/'war3map.j').read_bytes()).hexdigest(),
 globals_sha256=hashlib.sha256(headers[0]).hexdigest(),runtime_sha256=hashlib.sha256(runtimes[0]).hexdigest(),
 runtime_functions=len(functions(norm(runtimes[0]))),source_map_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),
 revision='Soul Hook repair and combined Mundo/Stalker/UI test',engine_playtest=False)
(O/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(source_manifest,indent=2),encoding='utf8')
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1];packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
gnames=lambda s:set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',s,re.M))
source_names=gnames(header);extras=[]
for line in packed.splitlines():
 m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
 if m and m[1] not in source_names and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:ef.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')

audit={}
for name in ['war3map.w3a','war3map.w3u']:
 parsed=[]
 for label,data in [('ancestor',old),('donor',donor),('before',base)]:
  path=R/(label+'-'+name);path.write_bytes(data[name]);d=objdata.load(str(path));assert objdata.dump(d)==data[name];parsed.append(d)
 a,b,d=parsed;edits=[]
 for table in range(2):
  key=lambda e:(e['oldId'],e['newId'])
  am={key(e):e for e in a['tables'][table]};bm={key(e):e for e in b['tables'][table]};dm={key(e):e for e in d['tables'][table]}
  assert am.keys()<=bm.keys()
  for k,be in bm.items():
   if k not in am:
    assert be['newId'] in ['ADk5','ADk6'] and k not in dm,k
    d['tables'][table].append(copy.deepcopy(be));edits.append([*k,'added']);continue
   if am[k]==be:continue
   assert k in dm and be['newId'] in ['ADk1','ADk2','HDk1'],k
   ae,de=am[k],dm[k];mk=lambda m:(m['id'],m.get('level'),m.get('ptr'))
   av={mk(m):m for m in ae['mods']};bv={mk(m):m for m in be['mods']};dv={mk(m):m for m in de['mods']}
   for field in av.keys()|bv.keys():
    if av.get(field)==bv.get(field):continue
    assert dv.get(field) in [av.get(field),bv.get(field)],(k,field)
    de['mods']=[m for m in de['mods'] if mk(m)!=field]
    if field in bv:de['mods'].append(copy.deepcopy(bv[field]))
    edits.append([*k,*field])
 (O/name).write_bytes(objdata.dump(d));audit[name]=edits
(O/'FF_MAINTENANCE.md').write_bytes(base['FF_MAINTENANCE.md']+b'\n\nSoul Hook integrated and fixed: ADk5 C, ADk6 stun. Swept outbound collision, per-cast damage, most-recent Demon Knight displacement wins. Mundo ramp and authored cloud models retained. Runtime and WCT synchronized; engine testing pending.\n')
manifest={'base':str(BASE),'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'donor':str(DONOR),'donor_sha256':hashlib.sha256(DONOR.read_bytes()).hexdigest(),'changed_functions':list(replacements),'new_functions':added,'objects':audit}
(R/'changes.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
