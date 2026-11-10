from pathlib import Path
import sys,shutil,re,copy,json,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
base=R/'base.w3x';source=W/'799x-backport/release/FF799X_Rx_Guardian_v28.w3x'
if not base.exists():shutil.copy2(source,base)
O=R/'src';O.mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in ['war3map.j','war3map.w3a','war3map.wts']:(O/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
original=(O/'war3map.j').read_text(encoding='utf-8-sig');s=original
def edit(name,old,new):
 global s
 f=functions(s)[name];assert old in f,(name,old);s=s.replace(f,f.replace(old,new,1),1)
def replace(name,body):
 global s
 f=functions(s)[name];s=s.replace(f,body.strip(),1)
s=s.replace('    effect array GTW_FX\n','    effect array GTW_FX\n    group array GTW_Hit\n    integer array GTW_Rank\n    hashtable GTW_Marks = InitHashtable()\n',1)
edit('GD_Stop','    call DestroyEffect(GD_Dome[i])','    call BlzSetSpecialEffectAlpha(GD_Dome[i], 0)\n    call DestroyEffect(GD_Dome[i])\n    call BlzStartUnitAbilityCooldown(GD_Caster[i], GD_ABILITY, 5.0)')
edit('GDV_Dome','    call GDV_Project(GD_Caster[i], x, y)\n','')
f=functions(s)['GDV_Dome'];start=f.index('    loop\n');end=f.index('    set fx = null',start)
f2=f[:start]+f[end:];s=s.replace(f,f2,1)
edit('GDB_Hit',"    local real amount = 20.0 + 5.0 * I2R(GetUnitAbilityLevel(caster, 'AZd1'))", "    local real power = 1.0 + RMinBJ(1.0, GD_Left[LoadInteger(GD_Data, GetHandleId(caster), 0)] * 0.05)\n    local real amount = (20.0 + 5.0 * I2R(GetUnitAbilityLevel(caster, 'AZd1'))) * power")
edit('GDB_Hit','UNIT_STATE_MANA) + 10.0','UNIT_STATE_MANA) + 10.0 * power')
edit('GDB_Hit','UNIT_STATE_MANA) - 10.0','UNIT_STATE_MANA) - 10.0 * power')
edit('GD_Tick','    local real burned','    local real burned\n    local real mana\n    local real power')
edit('GD_Tick','GetWidgetLife(caster) <= 0.405 or GD_Left[i] <= 0.00001','GetWidgetLife(caster) <= 0.405 or GetUnitState(caster, UNIT_STATE_MANA) <= 5.0')
edit('GD_Tick','        else\n            set x = GetUnitX(caster)', '''        else
            set mana = GetUnitState(caster, UNIT_STATE_MANA) - (30.0 + RMinBJ(100.0, 5.0 * GD_Left[i])) * GD_PERIOD
            call SetUnitState(caster, UNIT_STATE_MANA, RMaxBJ(0.0, mana))
            if mana <= 5.0 then
                call GD_Stop(i)
            else
            set power = 1.0 + RMinBJ(1.0, GD_Left[i] * 0.05)
            set x = GetUnitX(caster)''')
edit('GD_Tick','100.0 * GD_PERIOD','100.0 * power * GD_PERIOD')
edit('GD_Tick','10.0 * GD_PERIOD','10.0 * power * GD_PERIOD')
edit('GD_Tick','20.0 * GD_PERIOD','20.0 * power * GD_PERIOD')
edit('GD_Tick','            set GD_Left[i] = GD_Left[i] - GD_PERIOD','            set GD_Left[i] = GD_Left[i] + GD_PERIOD\n            endif')
cooldown_helper='''function GD_ClearActivationCooldown takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer key = GetHandleId(t)
    local unit caster = LoadUnitHandle(GD_Data, key, 100)
    if caster != null and LoadInteger(GD_Data, GetHandleId(caster), 0) != 0 then
        call BlzEndUnitAbilityCooldown(caster, GD_ABILITY)
    endif
    call FlushChildHashtable(GD_Data, key)
    call DestroyTimer(t)
    set caster = null
    set t = null
endfunction

function GD_ReadyActive takes unit caster returns nothing
    local timer t = CreateTimer()
    call SaveUnitHandle(GD_Data, GetHandleId(t), 100, caster)
    call TimerStart(t, 0.0, false, function GD_ClearActivationCooldown)
    set t = null
endfunction

'''
s=s.replace('function GD_Cast takes',cooldown_helper+'function GD_Cast takes',1)
edit('GD_Cast','    if i == 0 then\n        if GD_Count >= 8190 then', '''    if i != 0 then
        call GD_Stop(i)
        set caster = null
        return
    endif
    if GetUnitState(caster, UNIT_STATE_MANA) <= 5.0 then
        call BlzEndUnitAbilityCooldown(caster, GD_ABILITY)
        set caster = null
        return
    endif
    if i == 0 then
        if GD_Count >= 8190 then''')
edit('GD_Cast','    set GD_Left[i] = 15.0','    set GD_Left[i] = 0.0\n    // Clear the engine cooldown on the next tick so the active dome can be switched off.\n    call GD_ReadyActive(caster)')
edit('GTW_Remove','    call DestroyEffect(GTW_FX[i])', '''    local unit marked
    loop
        set marked = FirstOfGroup(GTW_Hit[i])
        exitwhen marked == null
        call GroupRemoveUnit(GTW_Hit[i], marked)
        call DestroyEffect(LoadEffectHandle(GTW_Marks, GetHandleId(GTW_Hit[i]), GetHandleId(marked)))
    endloop
    call FlushChildHashtable(GTW_Marks, GetHandleId(GTW_Hit[i]))
    set marked = null
    call DestroyEffect(GTW_FX[i])
    call DestroyGroup(GTW_Hit[i])''')
edit('GTW_Remove','    set GTW_FX[i] = GTW_FX[GTW_Count]','    set GTW_FX[i] = GTW_FX[GTW_Count]\n    set GTW_Hit[i] = GTW_Hit[GTW_Count]\n    set GTW_Rank[i] = GTW_Rank[GTW_Count]')
edit('GTW_Remove','    set GTW_FX[GTW_Count] = null','    set GTW_FX[GTW_Count] = null\n    set GTW_Hit[GTW_Count] = null')
insert=r'''function GTW_Eligible takes unit u, player owner returns boolean
    return u != null and GetUnitTypeId(u) != 0 and GetWidgetLife(u) > 0.405 and IsUnitEnemy(u, owner) and not IsUnitType(u, UNIT_TYPE_STRUCTURE) and not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) and GetUnitAbilityLevel(u, 'Aloc') == 0
endfunction

function GTW_Explode takes integer i returns nothing
    local unit caster = GTW_Caster[i]
    local unit target
    local unit dummy
    local effect fx = AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl", GTW_X[i], GTW_Y[i])
    call BlzSetSpecialEffectColor(fx, 80, 150, 255)
    call DestroyEffect(fx)
    loop
        set target = FirstOfGroup(GTW_Hit[i])
        exitwhen target == null
        call GroupRemoveUnit(GTW_Hit[i], target)
        call DestroyEffect(LoadEffectHandle(GTW_Marks, GetHandleId(GTW_Hit[i]), GetHandleId(target)))
        call RemoveSavedHandle(GTW_Marks, GetHandleId(GTW_Hit[i]), GetHandleId(target))
        if GTW_Eligible(target, GetOwningPlayer(caster)) then
            set dummy = CreateUnit(GetOwningPlayer(caster), 'hor3', GetUnitX(target), GetUnitY(target), 0.0)
            call UnitAddAbility(dummy, 'AGtz')
            call SetUnitAbilityLevel(dummy, 'AGtz', GTW_Rank[i])
            call IssueTargetOrder(dummy, "thunderbolt", target)
            call UnitApplyTimedLife(dummy, 'BTLF', 1.0)
        endif
    endloop
    set dummy = null
    set target = null
    set caster = null
    set fx = null
endfunction
'''
s=s.replace('function GTW_Tick takes',insert+'\nfunction GTW_Tick takes',1)
replace('GTW_Tick',r'''function GTW_Tick takes nothing returns nothing
    local integer i = GTW_Count
    local unit u
    local real step
    loop
        exitwhen i < 1
        if GetUnitTypeId(GTW_Caster[i]) == 0 then
            call GTW_Remove(i)
        else
            set step = RMinBJ(18.75, GTW_Left[i])
            set GTW_X[i] = GTW_X[i] + GTW_DX[i] * step
            set GTW_Y[i] = GTW_Y[i] + GTW_DY[i] * step
            set GTW_Left[i] = RMaxBJ(0.0, GTW_Left[i] - step)
            call BlzSetSpecialEffectX(GTW_FX[i], GTW_X[i])
            call BlzSetSpecialEffectY(GTW_FX[i], GTW_Y[i])
            call GroupEnumUnitsInRange(GTW_Enum, GTW_X[i], GTW_Y[i], 280.0, null)
            loop
                set u = FirstOfGroup(GTW_Enum)
                exitwhen u == null
                call GroupRemoveUnit(GTW_Enum, u)
                if GTW_Eligible(u, GetOwningPlayer(GTW_Caster[i])) and not IsUnitInGroup(u, GTW_Hit[i]) then
                    call GroupAddUnit(GTW_Hit[i], u)
                    call SaveEffectHandle(GTW_Marks, GetHandleId(GTW_Hit[i]), GetHandleId(u), AddSpecialEffectTarget("Abilities\\Spells\\Undead\\Curse\\CurseTarget.mdl", u, "overhead"))
                    call UnitDamageTarget(GTW_Caster[i], u, 20.0 + 10.0 * I2R(GTW_Rank[i]), false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
                endif
            endloop
            if GTW_Left[i] <= 0.0 then
                call GTW_Explode(i)
                call GTW_Remove(i)
            endif
        endif
        set i = i - 1
    endloop
    if GTW_Count == 0 then
        call PauseTimer(GTW_Timer)
    endif
    set u = null
endfunction''')
edit('GTW_Cast','    set GTW_Caster[i] = u','    set GTW_Caster[i] = u\n    set GTW_Hit[i] = CreateGroup()\n    set GTW_Rank[i] = GetUnitAbilityLevel(u, \'A0DL\')')
s=s.replace('FF799X - Guardian v28','FF799X - Guardian Channel v29')
(O/'war3map.j').write_text(s,encoding='utf8')
d=objdata.load(str(O/'war3map.w3a'));es={e['newId']:e for t in d['tables'] for e in t}
def put(e,k,v,level=0,ptr=0,typ=None):
 e['mods']=[m for m in e['mods'] if not (m['id']==k and m['level']==level)]
 e['mods'].append(dict(id=k,type=typ if typ is not None else (3 if isinstance(v,str) else 2 if isinstance(v,float) else 0),level=level,ptr=ptr,value=v,end=e['newId'].encode().hex()))
e=es['AZd1'];desc='Toggle Guardian Shield, radius 600. Allies gain 100 HP and 10 mana per second; enemies are slowed 60%, lose up to 20 mana per second and take equal magic damage. Every 0.75 seconds a random ally gains 25/30/35 HP, 10 mana and 10% speed for 1.5 seconds; a random enemy takes 25/30/35 damage, loses 10 mana and is slowed 15% for 1.5 seconds. Heal, mana restore, burn and damage grow 5% per second to double at 20 seconds. Guardian drains 30 mana/second, increasing 5 per second to 130 (his own regeneration and dome mana restore still apply). Stops at 5 mana or less. Toggle off anytime; 5-second cooldown after stopping.'
put(e,'arut',desc)
for level in range(1,4):
 put(e,'amcs',0,level);put(e,'acdn',5.0,level);put(e,'aub1',desc,level)
z=es['A0DL'];summary='Launch an orb in the chosen direction. It travels 700/800/900/1000/1100/1200 units at 600 speed, dealing 30/40/50/60/70/80 magic damage once to each enemy in 280 radius. At the end, all surviving marked enemies are stunned for 0.5/0.75/1/1.25/1.5/1.75 seconds. No displacement.'
put(z,'arut',summary)
for level in range(1,7):put(z,'aub1',summary,level)
stun=copy.deepcopy(es['AGr6']);stun['newId']='AGtz'
for m in stun['mods']:m['end']=b'AGtz'.hex()
put(stun,'anam','Time Warp stun');put(stun,'alev',6)
baselevel=[copy.deepcopy(m) for m in stun['mods'] if m['level']==1]
for level in range(2,7):
 for m in baselevel:
  m=copy.deepcopy(m);m['level']=level;stun['mods'].append(m)
for level in range(1,7):
 put(stun,'adur',0.25+0.25*level,level);put(stun,'ahdu',0.25+0.25*level,level);put(stun,'atar','ground,air,enemies,vulnerable',level)
assert not any(e['newId']=='AGtz' for t in d['tables'] for e in t)
d['tables'][1].append(stun);(O/'war3map.w3a').write_bytes(objdata.dump(d))
p=O/'war3map.wts';raw=p.read_bytes();assert b'FF799X - Guardian v28' in raw;p.write_bytes(raw.replace(b'FF799X - Guardian v28',b'FF799X - Guardian Channel v29'))
bf,sf=functions(original),functions(s);changed=[n for n in bf if bf[n]!=sf[n]]
(R/'changes.json').write_text(json.dumps(dict(base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),changed_functions=changed,added_functions=sorted(sf.keys()-bf.keys())),indent=2))
print('Prepared Guardian channel and Time Warp; changed',changed)
