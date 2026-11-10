"""Compose Cleaver Wound onto a chosen map without rewriting unrelated records."""
from pathlib import Path
import sys, re, struct, json, copy, hashlib
R = Path(__file__).resolve().parent
W = R.parent
sys.path[:0] = [str(W/'hero-polish'), str(W/'mini-foots/tools')]
from archive_helpers import storm, read_storm, c, functions
import objdata
BASE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else W/'mundo-health-kit/release/FF799X_Rx_Mundo_HealthKit_Test.w3x'
O = R/'src'
O.mkdir(exist_ok=True)
h = c.c_void_p()
assert storm.SFileOpenArchive(str(BASE), 0, 0x100, c.byref(h))
names = ['war3map.j','war3map.wct','war3map.w3a','war3map.w3h','FF_MAINTENANCE.md']
original = {n:read_storm(h,n) for n in names}
assert storm.SFileCloseArchive(h)
module = (R/'wound.j').read_text(encoding='utf8')
oldtip = 'Roots movement for 0.25 sec without stunning, then movement remains slowed 40% for 2 sec.'
newtip = 'Cleaver Wound: stops movement for 0.2 sec, then slows movement by 70% for 2 sec. Cancels Speed Scroll haste on this target and prevents it being reapplied during the wound. Can be dispelled.'

def patch(s):
    s = s.replace('\r','')
    assert 'function MW_Start ' not in s
    def edit(name, old, new):
        nonlocal s
        f = functions(s)[name]
        assert f.count(old)==1, (name,old)
        s = s.replace(f,f.replace(old,new,1),1)
    edit('MU_OnCleaverHit', '    call FS_Hit(source, target, damage)', '    call MW_Impact(target)\n    call FS_Hit(source, target, damage)')
    edit('MU_OnCleaverHit', '''        call MQ_Control(source, target, 'AMqr', "ensnare")
        call MQ_Control(source, target, 'AMus', "slow")''', '        call MW_Start(source, target)')
    edit('MU_Init', '    set MU_Hash = InitHashtable()', '    set MW_Hash = InitHashtable()\n    set MU_Hash = InitHashtable()')
    assert s.count(oldtip)==6
    s = s.replace(oldtip,newtip)
    anchor = 'function MU_OnCleaverHit takes nothing returns nothing'
    assert s.count(anchor)==1
    return s.replace(anchor,module+'\n'+anchor,1)

runtime = patch(original['war3map.j'].decode('utf-8-sig'))
runtime = runtime.replace('\nendglobals','\nhashtable MW_Hash = null\nendglobals',1)
(O/'war3map.j').write_text(runtime,encoding='utf8')
w=original['war3map.wct']; p=w.index(0,8)+1; prefix=w[:p]; chunks=[]; counts=[0,0]
while p<len(w):
    n=struct.unpack_from('<I',w,p)[0]; p+=4; b=w[p:p+n]; p+=n
    t=b.rstrip(b'\0').decode('utf-8-sig').replace('\r','')
    if 'function MU_OnCleaverHit takes nothing returns nothing' in t:
        t=patch(t); counts[0]+=1
    if re.search(r'^globals\b',t,re.M):
        t=t.replace('\nendglobals','\nhashtable MW_Hash = null\nendglobals',1); counts[1]+=1
    chunks.append(t.encode('utf8')+(b'\0' if b.endswith(b'\0') else b''))
assert counts==[1,1] and p==len(w),counts
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(b.rstrip(b'\0').decode('utf8') for b in chunks)
efs=functions(editor); rfs=functions(runtime)
changed=['MU_OnCleaverHit','MU_Init']; added=sorted(functions(module))
for n in changed+added: assert efs[n]==rfs[n],n
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1]
packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
def gnames(s): return set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',s,re.M))
source_names=gnames(header); extras=[]
for line in packed.splitlines():
    m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
    if m and m[1] not in source_names and not line.lstrip().startswith('//'): extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:efs.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')

def field(e,key,value,level=0,typ=3,ptr=0,lev=True):
    e['mods']=[m for m in e['mods'] if not(m['id']==key and m.get('level',0)==level)]
    m=dict(id=key,type=typ,value=value,end=e['newId'].encode().hex())
    if lev: m.update(level=level,ptr=ptr)
    e['mods'].append(m)

for n in ['war3map.w3a','war3map.w3h']:
    (R/('before-'+n)).write_bytes(original[n])
a=objdata.load(str(R/'before-war3map.w3a')); assert objdata.dump(a)==original['war3map.w3a']
es={e['newId']:e for t in a['tables'] for e in t}
assert not {'AMwR','AMwS'} & es.keys()
for original_id,uid,buff in [('AMqr','AMwR','BMwR'),('AMus','AMwS','BMwS')]:
    e=copy.deepcopy(es[original_id]); e['newId']=uid
    for m in e['mods']: m['end']=uid.encode().hex()
    field(e,'anam','Cleaver Wound - '+('movement lock' if uid=='AMwR' else 'slow'))
    for key in ['aart','acat','atat','amat','aeat','asat','alig','arac','areq','aefs','aefl']:
        field(e,key,'')
    field(e,'abuf',buff,1)
    field(e,'acas',0.,typ=1)
    # Native timed duration plus explicit timer cleanup, using private buff IDs.
    for key in ['adur','ahdu']: field(e,key,0.2 if uid=='AMwR' else 2.2,1,1)
    if uid=='AMwS':
        field(e,'Slo1',0.7,1,1,1); field(e,'Slo2',0.,1,1,2)
    a['tables'][1].append(e)
cleaver=es['AMu1']; tipcount=0
for m in cleaver['mods']:
    if m['type']==3 and oldtip in m['value']:
        m['value']=m['value'].replace(oldtip,newtip); tipcount+=1
assert tipcount>=6,tipcount
(O/'war3map.w3a').write_bytes(objdata.dump(a))
b=objdata.load(str(R/'before-war3map.w3h')); assert objdata.dump(b)==original['war3map.w3h']
assert not {'BMwR','BMwS'} & {e['newId'] for t in b['tables'] for e in t}
for parent,uid in [('Beng','BMwR'),('Bslo','BMwS')]:
    e=dict(oldId=parent,newId=uid,flags=1,extra=0,mods=[])
    for key,val in [('fnam','Cleaver Wound'),('ftip','Cleaver Wound'),('fube','Movement impaired. Speed Scroll cannot grant haste while wounded.'),('fart','ReplaceableTextures\\CommandButtons\\BTNMundoCleaver.blp'),('ftat',''),('feat',''),('fsat',''),('fmat',''),('flig','')]:
        field(e,key,val,lev=False)
    field(e,'ftac',0,typ=0,lev=False)
    b['tables'][1].append(e)
(O/'war3map.w3h').write_bytes(objdata.dump(b))
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\n\nMundo Cleaver Wound: new MW_ module and MW_Hash. AMwR/BMwR implement private art-free native movement root with 0.2 sec native duration and explicit cleanup; no shared Beng buff. AMwS/BMwS apply 70% move slow for 2.2 sec including root, no attack slow. Per-target 0.025 sec timer removes Bspe (also on impact), ending on 2.2 sec expiry, real dispel, death, removal, owner change, immunity, or replacement. Rehits refresh, not stack. Native root can interrupt channeling; no PauseUnit. Positional CreateSoundFromLabel MetalMediumChopFlesh and small blood burst play on contact including lethal hits. Engine testing pending.\n')
(R/'changes.json').write_text(json.dumps(dict(base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),changed_functions=changed,new_functions=added,changed_abilities=['AMu1'],new_abilities=['AMwR','AMwS'],new_buffs=['BMwR','BMwS'],runtime_editor_synchronized=True),indent=2))
print('Prepared Cleaver Wound: runtime, editor source, private control abilities/buffs and tooltips.')
