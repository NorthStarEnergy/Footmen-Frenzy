"""Compose Disease Cloud ramp onto a baseline containing the prior Mundo kit."""
from pathlib import Path
import sys,re,struct,json,hashlib
R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
BASE=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else W/'mundo-cleaver-wound/release/FF799X_Rx_Mundo_Cleaver_Wound_Test.w3x'
O=R/'src';O.mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,0x100,c.byref(h))
original={n:read_storm(h,n) for n in ['war3map.j','war3map.wct','war3map.w3a','war3map.imp','FF_MAINTENANCE.md']}
assert storm.SFileCloseArchive(h)
module=(R/'ramp.j').read_text()

def tooltip(rank):
    damage=35+15*(rank-1);cost=8+4*rank;resist=6+4*rank
    return f'Toggle Disease Cloud. Over 10 seconds of continuous use, magic damage rises from {damage} to {damage*2}/sec and health drain rises from {cost} to {cost*2}/sec. Reaches full strength at 10 sec and stays there until stopped.|nLight green -> darker green -> purple/dark green -> near-black at full strength. Toggling off resets the ramp.|nAffects enemy ground organic units within 250 radius. Grants {resist}% spell damage resistance while active. Automatically stops before its health drain would kill Mundo.|nLeaves clouds for 3 sec; poison lingers for 2 sec. Each cloud keeps its emitted strength; overlapping clouds from Mundo do not stack.|nMana: 0. Toggle cooldown: 0.5 sec.'

def patch(s):
    s=s.replace('\r','');assert 'function MC_Heat ' not in s
    assert 'function MU_ZeroResources ' in s and 'function MW_Start ' in s
    def edit(name,old,new):
        nonlocal s
        f=functions(s)[name];assert f.count(old)==1,(name,old)
        s=s.replace(f,f.replace(old,new,1),1)
    s=s.replace('function MU_BurnOff takes',module+'\nfunction MU_BurnOff takes',1)
    edit('MU_BurnOff','    call SaveBoolean(MU_Hash, h, 1, false)',
         '    call SaveBoolean(MU_Hash, h, 1, false)\n    call RemoveSavedReal(MU_Hash, h, 24)\n    call RemoveSavedReal(MU_Hash, h, 25)\n    call RemoveSavedReal(MU_Hash, h, 23)')
    edit('MU_OnCast','            call SaveBoolean(MU_Hash, h, 1, true)',
         '            call SaveBoolean(MU_Hash, h, 1, true)\n            call SaveReal(MU_Hash, h, 24, MC_Now())\n            call SaveReal(MU_Hash, h, 25, MC_Now())')
    edit('MU_OnCast','MU_Hash, h, 23, MU_Now + 0.5','MU_Hash, h, 23, MC_Now() + 0.5')
    edit('MU_TickHero','            set cost = (8.0 + 4.0 * rank) * 0.25','            set cost = MC_Drain(u, rank)')
    edit('MU_TickHero','                call SetWidgetLife(u, GetWidgetLife(u) - cost)',
         '                call SetWidgetLife(u, GetWidgetLife(u) - cost)\n                call SaveReal(MU_Hash, h, 25, MC_Now())')
    edit('MU_TickHero','LoadReal(MU_Hash, h, 23) <= MU_Now','LoadReal(MU_Hash, h, 23) <= MC_Now()')
    edit('MU_TickHero','MU_Hash, h, 23, MU_Now + 0.5','MU_Hash, h, 23, MC_Now() + 0.5')
    edit('MU_GasSpawn','    local real x = GetUnitX(u)',
         '    local real heat = MC_Heat(u)\n    local string model = MC_Model(heat)\n    local real x = GetUnitX(u)')
    f=functions(s)['MU_GasSpawn'];n=f.replace('"Abilities\\\\Spells\\\\Undead\\\\PlagueCloud\\\\PlagueCloudCaster.mdl"','model')
    assert n.count('AddSpecialEffect(model,')==3
    n=re.sub(r'^    call BlzSetSpecialEffectColor.*\n','',n,flags=re.M)
    n=n.replace('    call SaveInteger(MU_Hash, h, 43, rank)','    call SaveInteger(MU_Hash, h, 43, rank)\n    call SaveReal(MU_Hash, h, 46, (35.0 + 15.0 * (rank - 1)) * (1.0 + heat))')
    s=s.replace(f,n,1)
    edit('MU_GasExpire','    local integer rank = LoadInteger(MU_Hash, h, 43)',
         '    local integer rank = LoadInteger(MU_Hash, h, 43)\n    local real damage = LoadReal(MU_Hash, h, 46)\n    local integer slot')
    old='(35.0 + 15.0 * (rank - 1)) * 0.5'
    edit('MU_GasExpire',old,'damage * 0.5')
    edit('MU_GasExpire','                call SaveInteger(MU_Hash, GetHandleId(poison), 43, rank)',
         '''                call SaveInteger(MU_Hash, GetHandleId(poison), 43, rank)
                // Four pending half-second doses: strongest exposure wins each slot.
                // Weaker old clouds cannot overwrite a stronger dose or extend it forever.
                set slot = 50
                loop
                    exitwhen slot > 53
                    call SaveReal(MU_Hash, GetHandleId(poison), slot, RMaxBJ(damage, LoadReal(MU_Hash, GetHandleId(poison), slot)))
                    set slot = slot + 1
                endloop''')
    edit('MU_PoisonTick',old,'LoadReal(MU_Hash, h, 50) * 0.5')
    edit('MU_PoisonTick','        call SaveInteger(MU_Hash, h, 42, left - 1)',
         '''        call SaveInteger(MU_Hash, h, 42, left - 1)
        call SaveReal(MU_Hash, h, 50, LoadReal(MU_Hash, h, 51))
        call SaveReal(MU_Hash, h, 51, LoadReal(MU_Hash, h, 52))
        call SaveReal(MU_Hash, h, 52, LoadReal(MU_Hash, h, 53))
        call SaveReal(MU_Hash, h, 53, 0.0)''')
    for rank in range(1,7):
        pattern=r'    call BlzSetAbilityResearchExtendedTooltip\(\x27AMu2\x27, ".*?", '+str(rank-1)+r'\)'
        s,count=re.subn(pattern,lambda _:f'    call BlzSetAbilityResearchExtendedTooltip(\'AMu2\', "{tooltip(rank)}", {rank-1})',s)
        assert count==1
    return s

runtime=patch(original['war3map.j'].decode('utf-8-sig'));(O/'war3map.j').write_text(runtime,encoding='utf8')
w=original['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[];count=0
while p<len(w):
    n=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+n];p+=n;t=b.rstrip(b'\0').decode('utf-8-sig').replace('\r','')
    if 'function MU_GasSpawn takes' in t:t=patch(t);count+=1
    chunks.append(t.encode('utf8')+(b'\0' if b.endswith(b'\0') else b''))
assert count==1 and p==len(w)
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(b.rstrip(b'\0').decode('utf8') for b in chunks);efs=functions(editor);rfs=functions(runtime)
changed=['MU_BurnOff','MU_OnCast','MU_TickHero','MU_GasSpawn','MU_GasExpire','MU_PoisonTick','MU_Init'];added=sorted(functions(module))
for n in changed+added:assert efs[n]==rfs[n],n
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1];packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
def gnames(s):return set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',s,re.M))
source_names=gnames(header);extras=[]
for line in packed.splitlines():
    m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
    if m and m[1] not in source_names and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:efs.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')
(R/'before-war3map.w3a').write_bytes(original['war3map.w3a'])
a=objdata.load(str(R/'before-war3map.w3a'));assert objdata.dump(a)==original['war3map.w3a']
e=next(e for t in a['tables'] for e in t if e['newId']=='AMu2')
for m in e['mods']:
    if m['id']=='aub1':m['value']=tooltip(m['level'])
    elif m['id']=='arut':m['value']=tooltip(1)
(O/'war3map.w3a').write_bytes(objdata.dump(a))
imports=[f'Spells\\Mundo\\Cloud{i}.mdx' for i in range(21)]
imp=original['war3map.imp'];version,count=struct.unpack_from('<II',imp)
assert all(n.encode()+b'\0' not in imp for n in imports)
(O/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(imports))+imp[8:]+b''.join(b'\r'+n.encode()+b'\0' for n in imports))
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\n\nMundo cloud ramp: MC_ helpers; continuous 10 sec 1x-to-2x damage/HP drain, off/death resets hero keys 24/25. Integrated elapsed-time drain, cap at 10 sec. Cloud key46 stores emitted DPS; poison keys50-53 preserve maximum overlapping dose for four half-second ticks without stacking. 21 alpha-blended custom particle models transition light green/dark green/purple+green/near-black, snapshots match emitted strength. Prior health-kit and cleaver preserved. Engine testing pending.\n')
(R/'changes.json').write_text(json.dumps(dict(base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),changed_functions=changed,new_functions=added,changed_abilities=['AMu2'],new_abilities=[],new_buffs=[],imports=imports,runtime_editor_synchronized=True),indent=2))
print('Prepared Disease Cloud ramp and tooltips; runtime/editor synchronized.')
