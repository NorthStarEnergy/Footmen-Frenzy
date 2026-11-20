from pathlib import Path
import sys,re,struct,json
R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
BASE=W/'combined-v68/release/FF799X_Rx_Veigar_Classic_v68.w3x'; O=R/'src'; O.mkdir(exist_ok=True)
h=c.c_void_p(); assert storm.SFileOpenArchive(str(BASE),0,0x100,c.byref(h))
names=['war3map.j','war3map.wct','war3map.w3a','war3map.w3u','FF_MAINTENANCE.md']
orig={n:read_storm(h,n) for n in names};assert storm.SFileCloseArchive(h)

# Hidden negative attribute bonuses cancel item Intelligence without changing items.
resource='''// Mundo has no Intelligence or mana. Rebuild hidden offsets so item removal
// works even when the engine clamps the displayed total at zero.
function MU_ZeroResources takes unit u returns nothing
    local integer i = 0
    local integer id
    local integer amount
    local integer bit = 1
    loop
        exitwhen i == 20
        if i < 10 then
            set id = 'AMi0' + i
        else
            set id = 'AMj0' + i - 10
        endif
        call UnitRemoveAbility(u, id)
        set i = i + 1
    endloop
    call SetHeroInt(u, 0, true)
    set amount = GetHeroInt(u, true)
    set i = 0
    loop
        exitwhen i == 20
        if ModuloInteger(amount / bit, 2) == 1 then
            if i < 10 then
                set id = 'AMi0' + i
            else
                set id = 'AMj0' + i - 10
            endif
            call UnitAddAbility(u, id)
            call BlzUnitHideAbility(u, id, true)
        endif
        set bit = bit * 2
        set i = i + 1
    endloop
    if BlzGetUnitMaxMana(u) != 0 then
        call BlzSetUnitMaxMana(u, 0)
    endif
    call SetUnitState(u, UNIT_STATE_MANA, 0.0)
endfunction
'''
def patch(s):
 s=s.replace('\r','')
 assert 'function MU_ZeroResources ' not in s
 def edit(name,old,new):
  nonlocal s
  f=functions(s)[name];assert f.count(old)==1,(name,old)
  s=s.replace(f,f.replace(old,new,1),1)
 # An immediate first hit prevents half-second delay and ensures stationary enemies
 # are damaged even if a cloud and its first scan have just begun.
 edit('MU_GasExpire', '''                    call TimerStart(poison, 0.5, true, function MU_PoisonTick)
                endif
                call SaveInteger(MU_Hash, GetHandleId(poison), 42, 4)''','''                    call UnitDamageTarget(source, victim, (35.0 + 15.0 * (rank - 1)) * 0.5, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
                    call TimerStart(poison, 0.5, true, function MU_PoisonTick)
                endif
                call SaveInteger(MU_Hash, GetHandleId(poison), 42, 4)''')
 # 20 is the live cleaver's integer handle; use an independent cloud deadline.
 for fn in ['MU_OnCast','MU_TickHero']:
  f=functions(s)[fn];f2=f.replace('MU_Hash, h, 20, MU_Now + 0.5','MU_Hash, h, 23, MU_Now + 0.5').replace('LoadReal(MU_Hash, h, 20) <= MU_Now','LoadReal(MU_Hash, h, 23) <= MU_Now');assert f!=f2;s=s.replace(f,f2,1)
 edit('MU_Register',"        call UnitAddAbility(u, 'AMdc')","        call MU_ZeroResources(u)\n        call UnitAddAbility(u, 'AMdc')")
 edit('MU_TickHero','    if GetUnitTypeId(u) == 0 or IsUnitIllusion(u) then','    if GetUnitTypeId(u) != 0 and not IsUnitIllusion(u) then\n        call MU_ZeroResources(u)\n    endif\n    if GetUnitTypeId(u) == 0 or IsUnitIllusion(u) then')
 anchor='function MU_Register takes unit u returns nothing'; assert s.count(anchor)==1
 return s.replace(anchor,resource+'\n'+anchor,1)
runtime=patch(orig['war3map.j'].decode('utf-8-sig'));(O/'war3map.j').write_text(runtime,encoding='utf8')
w=orig['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[];count=0
while p<len(w):
 n=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+n];p+=n;t=b.rstrip(b'\0').decode('utf-8-sig').replace('\r','')
 if 'function MU_Register takes unit u returns nothing' in t:t=patch(t);count+=1
 chunks.append(t.encode('utf8')+(b'\0' if b.endswith(b'\0') else b''))
assert count==1 and p==len(w)
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(b.rstrip(b'\0').decode('utf8') for b in chunks);efs=functions(editor);rfs=functions(runtime)
changed=['MU_Register','MU_GasExpire','MU_OnCast','MU_TickHero','MU_ZeroResources']
for n in changed:assert efs[n]==rfs[n],n
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1];packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
def gnames(s):return set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',s,re.M))
source_names=gnames(header);extras=[]
for line in packed.splitlines():
 m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
 if m and m[1] not in source_names and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:efs.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')

def put(e,key,value,level=0,typ=0,ptr=0,lev=True):
 e['mods']=[m for m in e['mods'] if not(m['id']==key and m.get('level',0)==level)]
 m=dict(id=key,type=typ,value=value,end=e['newId'].encode().hex())
 if lev:m.update(level=level,ptr=ptr)
 e['mods'].append(m)
for name in ['war3map.w3a','war3map.w3u']:(O/name).write_bytes(orig[name])
d=objdata.load(str(O/'war3map.w3a'));assert objdata.dump(d)==orig['war3map.w3a'];ids={e['newId'] for t in d['tables'] for e in t}
for i in range(20):
 uid=('AMi'+str(i)) if i<10 else ('AMj'+str(i-10));assert uid not in ids
 e=dict(oldId='Aamk',newId=uid,flags=1,extra=0,mods=[])
 for key,val,typ in [('anam','Mundo hidden Intelligence offset',3),('alev',1,0),('aher',0,0),('aite',0,0),('aart','',3),('areq','',3)]:put(e,key,val,typ=typ)
 for key,val,ptr in [('Istr',0,1),('Iagi',0,2),('Iint',-(2**i),3),('Ihid',0,4)]:put(e,key,val,1,0,ptr)
 d['tables'][1].append(e)
(O/'war3map.w3a').write_bytes(objdata.dump(d))
u=objdata.load(str(O/'war3map.w3u'));assert objdata.dump(u)==orig['war3map.w3u']
e=next(e for t in u['tables'] for e in t if e['newId']=='HMu1')
for k,v,ty in [('uint',0,0),('uinp',0.,2),('umpm',0,0),('umpi',0,0),('umpr',0.,2)]:put(e,k,v,typ=ty,lev=False)
(O/'war3map.w3u').write_bytes(objdata.dump(u))
(O/'FF_MAINTENANCE.md').write_bytes(orig['FF_MAINTENANCE.md']+b'\n\nMundo health-kit test: AMu2 remains X click-to-toggle with 12/16/20/24/28/32 health per second. Disease clouds damage on first scan, use MU_Hash key 23 for cloud scheduling (20 belongs to cleaver). Hidden AMi0-AMi9 and AMj0-AMj9 cancel Intelligence bonuses; MU_ZeroResources recomputes on registration and each 0.25 sec, and sets max/current mana to zero. Hero object INT, INT growth, max mana, initial mana and mana regeneration are zero. Engine testing of negative stat bonus and zero max mana remains required.\n')
(R/'changes.json').write_text(json.dumps({'base':str(BASE),'changed_functions':changed,'runtime_editor_synchronized':True,'integration':'Apply prepare.py logic to latest combined baseline; do not replace whole map script when merging with other agents.'},indent=2))
print('Prepared Mundo resource and cloud changes against v68.')
