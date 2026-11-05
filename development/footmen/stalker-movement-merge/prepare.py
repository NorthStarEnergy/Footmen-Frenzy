from pathlib import Path
import sys,re,struct,json,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
BASE=W/'mundo-ui-merge/release/FF799X_Rx_UI_Repair_Mundo_Combined_Test.w3x'
O=R/'src';O.mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,256,c.byref(h))
names=['war3map.j','war3map.wct','war3map.w3u','FF_MAINTENANCE.md']
original={n:read_storm(h,n) for n in names};storm.SFileCloseArchive(h)
old=functions((W/'stalker-v71/stalker.j').read_text());new=functions((R/'stalker.j').read_text())
changed=[n for n in old if old[n]!=new[n]];added=sorted(new.keys()-old.keys())
def patch(s):
    s=s.replace('\r','');fs=functions(s)
    for n in old:assert fs.get(n)==old[n],('Selected baseline has conflicting Stalker edits',n)
    for n in changed:s=s.replace(fs[n],new[n],1)
    anchor='function ST_Space takes'
    assert s.count(anchor)==1
    return s.replace(anchor,'\n\n'.join(new[n] for n in added)+'\n\n'+anchor,1)
runtime=patch(original['war3map.j'].decode('utf-8-sig'))
(O/'war3map.j').write_text(runtime,encoding='utf8')
w=original['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[];count=0
while p<len(w):
    n=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+n];p+=n
    t=b.rstrip(b'\0').decode('utf-8-sig').replace('\r','')
    if 'function ST_Init takes' in t:
        t=patch(t);count+=1;b=t.encode('utf8')+(b'\0' if b.endswith(b'\0') else b'')
    chunks.append(b)
assert p==len(w) and count==1
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(b.rstrip(b'\0').decode('utf8').replace('\r','') for b in chunks)
efs=functions(editor);rfs=functions(runtime)
for n in changed+added:assert efs[n]==rfs[n],n
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1];packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
source_names=set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',header,re.M));extras=[]
for line in packed.splitlines():
    m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
    if m and m[1] not in source_names and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:efs.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')
(R/'before-war3map.w3u').write_bytes(original['war3map.w3u']);(O/'war3map.w3u').write_bytes(original['war3map.w3u'])
u=objdata.load(str(O/'war3map.w3u'));assert objdata.dump(u)==original['war3map.w3u']
e=next(e for t in u['tables'] for e in t if e['newId']=='nStk')
col=next(m for m in e['mods'] if m['id']=='ucol');assert col['value']==32.0;col['value']=16.0
(O/'war3map.w3u').write_bytes(objdata.dump(u))
note='\n\nStalker movement/Blink patch on UI Repair + Mundo Combined: nStk collision 32 -> 16. ST_Cast processes selected ready units from leading edge to rear, allowing vacated squad slots. ST_Move uses validated SetUnitX/Y, avoids native Stop and removes the 2-unit placement rollback. ST_Space uses actual mover collision, tolerates 10-unit item probe deviation, and temporarily hides/restores loose items so loot does not block Blink. Ownership/selection/readiness, visibility, terrain, blockers, cooldown, shields and tether integration remain. Three existing ST_ functions changed; one item-enumeration helper added. No other runtime functions, abilities, string labels, art or Mundo behavior changed. Runtime/editor compilation and mocked-native regression checks required; engine playtest pending.\n'
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+note.encode())
(R/'changes.json').write_text(json.dumps(dict(base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),changed_functions=changed,new_functions=added,unit='nStk',changed_unit_fields={'ucol':{'before':32.0,'after':16.0}},runtime_editor_synchronized=True),indent=2))
print('Prepared narrow Stalker patch on exact user-selected combined baseline:',changed,added)
