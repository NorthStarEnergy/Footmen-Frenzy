from pathlib import Path
import sys,shutil,re,copy,json,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
base=R/'base.w3x';source=W/'799x-backport/release/FF799X_Rx_GuardianChannel_v29.w3x'
if not base.exists():shutil.copy2(source,base)
O=R/'src';O.mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in ['war3map.j','war3map.w3a','war3map.wts']:(O/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
original=(O/'war3map.j').read_text(encoding='utf-8-sig');s=original
def edit(name,old,new):
 global s
 f=functions(s)[name];assert old in f,(name,old);s=s.replace(f,f.replace(old,new,1),1)
globals='''group array TFP_LinkInside
group array TFP_LanternInside
group array TFP_RideHit
group TFP_LinkEnum = CreateGroup()
group TFP_LinkNext = CreateGroup()
group TFP_LanternNext = CreateGroup()
'''
s=s.replace('group   array    TFP_FFDP_Track',globals+'group   array    TFP_FFDP_Track',1)
edit('TFP_FFDP_OnCast','    set TFP_FFDP_Track[i]   = CreateGroup()', '''    set TFP_FFDP_Track[i]   = CreateGroup()
    set TFP_LinkInside[i] = CreateGroup()
    set TFP_LanternInside[i] = CreateGroup()
    set TFP_RideHit[i] = CreateGroup()''')
edit('TFP_FFDP_Destroy','    call DestroyGroup(TFP_FFDP_Track[i])', '''    call DestroyGroup(TFP_LinkInside[i])
    call DestroyGroup(TFP_LanternInside[i])
    call DestroyGroup(TFP_RideHit[i])
    call DestroyGroup(TFP_FFDP_Track[i])''')
edit('TFP_FFDP_Destroy','        set TFP_FFDP_Track[i]   = TFP_FFDP_Track[last]', '''        set TFP_FFDP_Track[i]   = TFP_FFDP_Track[last]
        set TFP_LinkInside[i] = TFP_LinkInside[last]
        set TFP_LanternInside[i] = TFP_LanternInside[last]
        set TFP_RideHit[i] = TFP_RideHit[last]''')
edit('TFP_FFDP_Destroy','    set TFP_FFDP_Track[last]   = null', '''    set TFP_FFDP_Track[last]   = null
    set TFP_LinkInside[last] = null
    set TFP_LanternInside[last] = null
    set TFP_RideHit[last] = null''')
helper=r'''function TFP_LinkDistanceSquared takes real px, real py, real ax, real ay, real bx, real by returns real
    local real dx = bx - ax
    local real dy = by - ay
    local real len2 = dx * dx + dy * dy
    local real t = 0.0
    if len2 > 0.01 then
        set t = RMaxBJ(0.0, RMinBJ(1.0, ((px - ax) * dx + (py - ay) * dy) / len2))
    endif
    set dx = px - (ax + t * dx)
    set dy = py - (ay + t * dy)
    return dx * dx + dy * dy
endfunction

function TFP_LinkEnemy takes unit u, player owner returns boolean
    return u != null and GetUnitTypeId(u) != 0 and GetWidgetLife(u) > 0.405 and IsUnitEnemy(u, owner) and not IsUnitType(u, UNIT_TYPE_STRUCTURE) and not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) and GetUnitAbilityLevel(u, 'Aloc') == 0
endfunction

function TFP_LinkEffect takes integer i, unit target, boolean stun returns nothing
    local unit dummy = CreateUnit(TFP_FFDP_Owner[i], 'hor3', GetUnitX(target), GetUnitY(target), 0.0)
    if stun then
        call UnitAddAbility(dummy, 'AGtz')
        call SetUnitAbilityLevel(dummy, 'AGtz', 1)
        call IssueTargetOrder(dummy, "thunderbolt", target)
    else
        call UnitAddAbility(dummy, 'ALTc')
        call IssueTargetOrder(dummy, "slow", target)
    endif
    call UnitApplyTimedLife(dummy, 'BTLF', 1.0)
    set dummy = null
endfunction

function TFP_LinkGround takes integer i returns nothing
    local real ax = GetUnitX(TFP_FFDP_Caster[i])
    local real ay = GetUnitY(TFP_FFDP_Caster[i])
    local real bx = GetUnitX(TFP_FFDP_Lantern[i])
    local real by = GetUnitY(TFP_FFDP_Lantern[i])
    local real dx = bx - ax
    local real dy = by - ay
    local real ux
    local real uy
    local unit u
    call GroupClear(TFP_LinkNext)
    call GroupClear(TFP_LanternNext)
    call GroupEnumUnitsInRange(TFP_LinkEnum, (ax + bx) * 0.5, (ay + by) * 0.5, SquareRoot(dx * dx + dy * dy) * 0.5 + 150.0, null)
    loop
        set u = FirstOfGroup(TFP_LinkEnum)
        exitwhen u == null
        call GroupRemoveUnit(TFP_LinkEnum, u)
        set ux = GetUnitX(u)
        set uy = GetUnitY(u)
        if TFP_LinkEnemy(u, TFP_FFDP_Owner[i]) and (ux - bx) * (ux - bx) + (uy - by) * (uy - by) <= 130.0 * 130.0 then
            call GroupAddUnit(TFP_LanternNext, u)
            if not IsUnitInGroup(u, TFP_LanternInside[i]) then
                call TFP_LinkEffect(i, u, true)
            endif
        endif
        if u != TFP_FFDP_Caster[i] and GetWidgetLife(u) > 0.405 and IsUnitAlly(u, TFP_FFDP_Owner[i]) and not IsUnitType(u, UNIT_TYPE_STRUCTURE) and GetUnitAbilityLevel(u, 'Aloc') == 0 and TFP_LinkDistanceSquared(ux, uy, ax, ay, bx, by) <= 65.0 * 65.0 then
            call GroupAddUnit(TFP_LinkNext, u)
            if not IsUnitInGroup(u, TFP_LinkInside[i]) then
                call SetWidgetLife(u, RMinBJ(GetUnitState(u, UNIT_STATE_MAX_LIFE), GetWidgetLife(u) + 10.0))
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", u, "origin"))
                if not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) then
                    call TFP_LinkEffect(i, u, false)
                endif
            endif
            call SetWidgetLife(u, RMinBJ(GetUnitState(u, UNIT_STATE_MAX_LIFE), GetWidgetLife(u) + 20.0 * TFP_FFDP_TICK))
        endif
    endloop
    call GroupClear(TFP_LinkInside[i])
    call GroupAddGroup(TFP_LinkNext, TFP_LinkInside[i])
    call GroupClear(TFP_LanternInside[i])
    call GroupAddGroup(TFP_LanternNext, TFP_LanternInside[i])
    set u = null
endfunction

function TFP_LinkRide takes integer i, real ax, real ay, real bx, real by returns nothing
    local real dx = bx - ax
    local real dy = by - ay
    local unit u
    call GroupEnumUnitsInRange(TFP_LinkEnum, (ax + bx) * 0.5, (ay + by) * 0.5, SquareRoot(dx * dx + dy * dy) * 0.5 + 90.0, null)
    loop
        set u = FirstOfGroup(TFP_LinkEnum)
        exitwhen u == null
        call GroupRemoveUnit(TFP_LinkEnum, u)
        if TFP_LinkEnemy(u, TFP_FFDP_Owner[i]) and IsUnitType(u, UNIT_TYPE_HERO) and not IsUnitInGroup(u, TFP_RideHit[i]) and TFP_LinkDistanceSquared(GetUnitX(u), GetUnitY(u), ax, ay, bx, by) <= 90.0 * 90.0 then
            call GroupAddUnit(TFP_RideHit[i], u)
            call TFP_LinkEffect(i, u, true)
        endif
    endloop
    set u = null
endfunction
'''
s=s.replace('function TFP_FFDP_Tick takes',helper+'\nfunction TFP_FFDP_Tick takes',1)
edit('TFP_FFDP_Tick','                if TFP_FFDP_Next[i] <= 0.0 then', '''                if GetUnitTypeId(TFP_FFDP_Caster[i]) == 'H043' then
                    call TFP_LinkGround(i)
                endif
                if TFP_FFDP_Next[i] <= 0.0 then''')
edit('TFP_FFDP_Tick','                if d <= step then\n                    call SetUnitX(TFP_FFDP_Rider[i]', '''                if d <= step then
                    if GetUnitTypeId(TFP_FFDP_Caster[i]) == 'H043' then
                        call TFP_LinkRide(i, x, y, TFP_FFDP_ClampX(cx), TFP_FFDP_ClampY(cy))
                    endif
                    call SetUnitX(TFP_FFDP_Rider[i]''')
edit('TFP_FFDP_Tick','                    call SetUnitX(TFP_FFDP_Rider[i], TFP_FFDP_ClampX(x + step * dx / d))', '''                    if GetUnitTypeId(TFP_FFDP_Caster[i]) == 'H043' then
                        call TFP_LinkRide(i, x, y, TFP_FFDP_ClampX(x + step * dx / d), TFP_FFDP_ClampY(y + step * dy / d))
                    endif
                    call SetUnitX(TFP_FFDP_Rider[i], TFP_FFDP_ClampX(x + step * dx / d))''')
# ATfd is shared with Twisted Fate; add Guardian-specific details to the hero ability tooltip,
# without altering Twisted Fate's runtime research tooltip overrides.
d=objdata.load(str(O/'war3map.w3a'));es={e['newId']:e for t in d['tables'] for e in t}
slow=copy.deepcopy(es['AGbn']);slow['newId']='ALTc'
for m in slow['mods']:
 m['end']=b'ALTc'.hex()
 if m['id']=='anam':m['value']='Lantern chain slow'
 if m['id']=='atar':m['value']='friend,ground,air,organic,mechanical,vulnerable'
 if m['id']=='abuf':m['value']='Bslo'
 if m['id'] in ('adur','ahdu'):m['value']=1.0
 if m['id']=='Slo1':m['value']=0.2
assert not any(e['newId']=='ALTc' for t in d['tables'] for e in t);d['tables'][1].append(slow)
# Runtime updates the shared research text globally. Add the Guardian effects accurately
# to research text without claiming Twisted Fate also has them.
tooltip='|n|nGuardian only: enemies entering the lantern area are stunned 0.5 sec. Allies entering the chain gain 10 HP and are slowed 20% for 1 sec; remaining in the chain heals 20 HP/sec. A rescued ally stuns enemy heroes crossed for 0.5 sec.'
old=functions(s)['TFP_Init'];new=re.sub(r'^.*BlzSetAbilityResearchExtendedTooltip\(\x27ATfd\x27.*$',lambda m:m[0].replace('", ',tooltip+'", '),old,flags=re.M);assert new!=old;s=s.replace(old,new,1)
e=es['ATfd']
for m in e['mods']:
 if m['id'] in ['arut','aub1']:m['value']+=tooltip
(O/'war3map.w3a').write_bytes(objdata.dump(d))
s=s.replace('FF799X - Guardian Channel v29','FF799X - Guardian Lantern v30')
(O/'war3map.j').write_text(s,encoding='utf8')
p=O/'war3map.wts';raw=p.read_bytes();assert b'FF799X - Guardian Channel v29' in raw;p.write_bytes(raw.replace(b'FF799X - Guardian Channel v29',b'FF799X - Guardian Lantern v30'))
bf,sf=functions(original),functions(s);changed=[n for n in bf if bf[n]!=sf[n]]
assert set(changed)=={'TFP_FFDP_OnCast','TFP_FFDP_Destroy','TFP_FFDP_Tick','TFP_Init'},changed
(R/'changes.json').write_text(json.dumps(dict(base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),changed_functions=changed,added_functions=sorted(sf.keys()-bf.keys())),indent=2))
print('Guardian lantern effects prepared; other lantern users keep existing behavior.')
