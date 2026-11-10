"""Repair Veigar ability object field types and Event Horizon on the v72 test map."""
from pathlib import Path
import hashlib,json,re,struct,sys
R=Path(__file__).resolve().parent;W=R.parent;O=R/'src';O.mkdir(exist_ok=True)
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
from game_data import game_read,slk
BASE=W/'soulhook-mundo-v72/release/FF799X_Rx_SoulHook_Mundo_v72_TEST.w3x'
names=['war3map.j','war3map.wct','war3map.w3a','FF_MAINTENANCE.md','FF_SOURCE_MANIFEST.json']
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h));base={n:read_storm(h,n) for n in names};assert storm.SFileCloseArchive(h)
norm=lambda b:b.decode('utf-8-sig').replace('\r','')
before=functions(norm(base['war3map.j']))
def patch(s):
 fs=functions(s)
 for name in ['VG_CageScan','VG_StunVisualTick']:
  if name not in fs:continue
  f=fs[name]
  if name=='VG_CageScan':
   assert f.count("CreateUnit(owner, 'hor3'")==1
   g=f.replace("CreateUnit(owner, 'hor3'", "CreateUnit(owner, 'hgr1'")
  else:
   assert f.count('age >= 2.0')==1 and f.count('SetTextTagLifespan(label, 2.1)')==1
   g=f.replace('age >= 2.0','age >= 4.0').replace('SetTextTagLifespan(label, 2.1)','SetTextTagLifespan(label, 4.1)')
  s=s.replace(f,g,1)
 return s
runtime=patch(norm(base['war3map.j']));rf=functions(runtime)
changed=[n for n in before if before[n]!=rf[n]];assert changed==['VG_StunVisualTick','VG_CageScan']
(O/'war3map.j').write_text(runtime,encoding='utf8')
w=base['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[]
while p<len(w):
 n=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+n];p+=n;s=norm(b.rstrip(b'\0'));edited=patch(s)
 chunks.append(edited.encode('utf8')+(b'\0' if b.endswith(b'\0') else b'') if edited!=s else b)
assert p==len(w);(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(norm(b.rstrip(b'\0')) for b in chunks);ef=functions(editor)
for n in changed:assert ef[n]==rf[n],n
headers=[b.rstrip(b'\0') for b in chunks if re.search(rb'(?m)^globals\b',b)]
runtimes=[b.rstrip(b'\0') for b in chunks if b'function VG_CageScan takes' in b]
assert len(headers)==len(runtimes)==1
sd=O/'source_roundtrip';sd.mkdir(exist_ok=True);(sd/'globals.j').write_bytes(headers[0]);(sd/'FF_Runtime.j').write_bytes(runtimes[0])
sm=json.loads(base['FF_SOURCE_MANIFEST.json'].decode('utf-8-sig'));sm.update(
 compiled_source_sha256=hashlib.sha256((O/'war3map.j').read_bytes()).hexdigest(),globals_sha256=hashlib.sha256(headers[0]).hexdigest(),
 runtime_sha256=hashlib.sha256(runtimes[0]).hexdigest(),runtime_functions=len(functions(norm(runtimes[0]))),
 source_map_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),revision='Veigar casting and Event Horizon test',engine_playtest=False)
(O/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(sm,indent=2),encoding='utf8')
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1];packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
gnames=lambda x:set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',x,re.M))
known=gnames(header);extras=[]
for line in packed.splitlines():
 m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
 if m and m[1] not in known and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:ef.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')
(R/'before-war3map.w3a').write_bytes(base['war3map.w3a']);data=objdata.load(str(R/'before-war3map.w3a'));assert objdata.dump(data)==base['war3map.w3a']
metadata=slk(game_read(r'war3.w3mod:units\abilitymetadata.slk')); expected={'int':0,'bool':0,'real':1,'unreal':2,'string':3}
selected=['AVgq','AVgw','AVge','AVgr','AVgs'];edits=[]
for e in [e for tab in data['tables'] for e in tab if e['newId'] in selected]:
 for m in e['mods']:
  typ=expected.get(metadata.get(m['id'],{}).get('type'))
  if typ is not None and typ!=m['type']:
   assert (m['type'],typ) in [(1,2),(1,0)],(e['newId'],m)
   if typ==0:assert m['value']==0.0;m['value']=int(m['value'])
   edits.append([e['newId'],m['id'],m.get('level'),m['type'],typ]);m['type']=typ
  if e['newId']=='AVgs' and m['id']=='amsp':
   assert m['type']==0 and m['value']==0;m['value']=10000;edits.append(['AVgs','amsp',0,0,10000])
 assert all(m['type']==expected.get(metadata.get(m['id'],{}).get('type'),m['type']) for m in e['mods'])
(O/'war3map.w3a').write_bytes(objdata.dump(data))
(O/'FF_MAINTENANCE.md').write_bytes(base['FF_MAINTENANCE.md']+b'\n\nVeigar casting test: correct ability object field types using Warcraft metadata; preserve 700/900/900/650 cast ranges. AVgs stun missile speed 10000 with the standard spell dummy. Stun feedback supports rank 6. Editor and runtime synchronized. Engine playtest pending.\n')
report={'base':str(BASE),'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'changed_functions':changed,'new_functions':[],'ability_field_edits':edits,'intended_ranges':{'AVgq':700,'AVgw':900,'AVge':900,'AVgr':650}}
(R/'changes.json').write_text(json.dumps(report,indent=2));print('Prepared Veigar corrections:',len(edits),'ability field changes;',len(changed),'script functions.')
