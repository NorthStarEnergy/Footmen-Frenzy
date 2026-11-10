from pathlib import Path
import sys, subprocess, shutil, hashlib, json
R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries,functions
p=W/'tf-guardian-v47/src/war3map.j'; s=p.read_text(encoding='utf-8-sig'); before=s
def edit(n,a,b):
 global s
 f=functions(s)[n]; assert a in f,(n,a); s=s.replace(f,f.replace(a,b,1),1)
s=s.replace('group array TFP_LinkInside','hashtable GL_Armor = InitHashtable()\nlocation GTW_HeightLoc = Location(0.0, 0.0)\ngroup array TFP_LinkInside',1)
helper='''function GL_ArmorExpire takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer k = GetHandleId(t)
    local unit u = LoadUnitHandle(GL_Armor, k, 0)
    local real amount = LoadReal(GL_Armor, k, 1)
    if u != null and GetUnitTypeId(u) != 0 then
        call BlzSetUnitArmor(u, BlzGetUnitArmor(u) - amount)
        call RemoveSavedHandle(GL_Armor, GetHandleId(u), 0)
    endif
    call FlushChildHashtable(GL_Armor, k)
    call DestroyTimer(t)
    set u = null
    set t = null
endfunction

function GL_ArmorApply takes unit u, real amount returns nothing
    local integer k = GetHandleId(u)
    local timer t = LoadTimerHandle(GL_Armor, k, 0)
    local real old = 0.0
    if t == null then
        set t = CreateTimer()
        call SaveTimerHandle(GL_Armor, k, 0, t)
        call SaveUnitHandle(GL_Armor, GetHandleId(t), 0, u)
    else
        set old = LoadReal(GL_Armor, GetHandleId(t), 1)
    endif
    call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + amount - old)
    call SaveReal(GL_Armor, GetHandleId(t), 1, amount)
    call TimerStart(t, 2.0, false, function GL_ArmorExpire)
    set t = null
endfunction

'''
s=s.replace('function TFP_LinkGround takes',helper+'function TFP_LinkGround takes',1)
edit('TFP_LinkEffect',"'ALTc'","'AGbn'")
edit('TFP_LinkGround','        if u != TFP_FFDP_Caster[i] and GetWidgetLife(u)', '''        if TFP_LinkEnemy(u, TFP_FFDP_Owner[i]) and TFP_LinkDistanceSquared(ux, uy, ax, ay, bx, by) <= 65.0 * 65.0 then
            call GL_ArmorApply(u, -3.0)
            if not IsUnitInGroup(u, TFP_LinkInside[i]) then
                call TFP_LinkEffect(i, u, false)
            endif
            call GroupAddUnit(TFP_LinkNext, u)
        endif
        if u != TFP_FFDP_Caster[i] and GetWidgetLife(u)''')
edit('TFP_LinkGround','            call GroupAddUnit(TFP_LinkNext, u)\n            if not IsUnitInGroup(u, TFP_LinkInside[i]) then\n                call SetWidgetLife', '            call GroupAddUnit(TFP_LinkNext, u)\n            call GL_ArmorApply(u, 3.0)\n            if not IsUnitInGroup(u, TFP_LinkInside[i]) then\n                call SetWidgetLife')
edit('TFP_LinkGround','''                if not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) then
                    call TFP_LinkEffect(i, u, false)
                endif
''','')
edit('TFP_FFDP_Tick','''                set x = GetUnitX(TFP_FFDP_Rider[i])
                set y = GetUnitY(TFP_FFDP_Rider[i])''','''                if GetUnitTypeId(TFP_FFDP_Caster[i]) == 'H043' then
                    call GL_ArmorApply(TFP_FFDP_Rider[i], 3.0)
                    call SetWidgetLife(TFP_FFDP_Rider[i], RMinBJ(GetUnitState(TFP_FFDP_Rider[i], UNIT_STATE_MAX_LIFE), GetWidgetLife(TFP_FFDP_Rider[i]) + 40.0 * TFP_FFDP_TICK))
                endif
                set x = GetUnitX(TFP_FFDP_Rider[i])
                set y = GetUnitY(TFP_FFDP_Rider[i])''')
edit('GFW_Create','0.70875','1.25');edit('GFW_Create','55, 105, 255','120, 200, 255');edit('GFW_Create','3.0)','1.0)')
edit('GTW_Cast','    local real dy\n','    local real dy\n    local real distance\n')
edit('GTW_Cast','    set GTW_Count = GTW_Count + 1','    set distance = RMaxBJ(200.0, RMinBJ(600.0 + 100.0 * I2R(GetUnitAbilityLevel(u, \'A0DL\')), SquareRoot(dx * dx + dy * dy)))\n    set GTW_Count = GTW_Count + 1')
edit('GTW_Cast',"    set GTW_Left[i] = 600.0 + 100.0 * I2R(GetUnitAbilityLevel(u, 'A0DL'))",'    set GTW_Left[i] = distance')
edit('GTW_Cast','    call BlzSetSpecialEffectScale(GTW_FX[i], 4.0)','    call BlzSetSpecialEffectScale(GTW_FX[i], 4.0)\n    call MoveLocation(GTW_HeightLoc, GTW_X[i], GTW_Y[i])\n    call BlzSetSpecialEffectZ(GTW_FX[i], GetLocationZ(GTW_HeightLoc) + 200.0)')
edit('GTW_Tick','            call BlzSetSpecialEffectY(GTW_FX[i], GTW_Y[i])','            call BlzSetSpecialEffectY(GTW_FX[i], GTW_Y[i])\n            call MoveLocation(GTW_HeightLoc, GTW_X[i], GTW_Y[i])\n            call BlzSetSpecialEffectZ(GTW_FX[i], GetLocationZ(GTW_HeightLoc) + 200.0)')
edit('GTW_Explode','Abilities\\\\Spells\\\\Human\\\\Thunderclap\\\\ThunderClapCaster.mdl','Abilities\\\\Spells\\\\Other\\\\Doom\\\\DoomDeath.mdl')
edit('GDV_Dome','    call GDB_Visual(GD_Caster[i])','    call GDB_Visual(GD_Caster[i])\n    call GDV_Project(GD_Caster[i], x, y)')
edit('GDB_Hit','1.0 + RMinBJ(1.0, GD_Left[LoadInteger(GD_Data, GetHandleId(caster), 0)] * 0.05)','1.5')
edit('GD_Tick','(30.0 + RMinBJ(100.0, 5.0 * GD_Left[i]))','30.0');edit('GD_Tick','set power = 1.0 + RMinBJ(1.0, GD_Left[i] * 0.05)','set power = 1.5');edit('GD_Tick','set GD_Left[i] = GD_Left[i] + GD_PERIOD','set GD_Left[i] = 0.0')
s=s.replace('Allies entering the chain gain 10 HP and are slowed 20% for 1 sec; remaining in the chain heals 20 HP/sec.', 'Allies on the chain gain 3 armor and heal 10 on entry plus 20 HP/sec; enemies on it lose 3 armor and are slowed. Armor lasts 2 sec after leaving. Riders heal 40 HP/sec.')
s=s.replace('Other allies heal |cff80ff8010 + 20/sec|r and are slowed |cff80dfff20% for 1 sec|r on entry.', 'Allies gain |cff80ff803 armor|r and heal |cff80ff8010 + 20/sec|r; riders heal 40/sec. Enemies lose 3 armor and are slowed; armor effects last 2 sec after leaving.')
s=s.replace('Fire an orb that marks and damages enemies. Marked enemies are stunned when it bursts.', 'Fire an orb to the chosen point (minimum 200 range); it marks and damages enemies, then stuns them when it bursts at its destination.')
s=s.replace('|cffffcc00Ramp:|r |cff80dfff+5% power/sec, up to 2x|r|n','').replace('30 mana/sec, +5/sec over time (max 130)','30 mana/sec').replace('100 HP + 10 mana/sec','150 HP + 15 mana/sec').replace('up to 20 mana burn/sec','up to 30 mana burn/sec')
lines=s.splitlines()
for j,line in enumerate(lines):
 if "BlzSetAbilityResearchExtendedTooltip('AZd1'" in line:
  for a,b in [('25 heal','37.5 heal'),('25 damage','37.5 damage'),('30 heal','45 heal'),('30 damage','45 damage'),('35 heal','52.5 heal'),('35 damage','52.5 damage')]: line=line.replace(a,b)
  lines[j]=line
s='\n'.join(lines)+'\n'
s=s.replace('Six seconds to select, then ten seconds to throw.', 'Five seconds to select, then ten seconds to throw.')
p.write_text(s,encoding='utf8')
