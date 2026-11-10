function VG_ClassicKill takes nothing returns nothing
    local unit u = GetKillingUnit()
    local unit victim = GetTriggerUnit()
    local integer rank = GetUnitAbilityLevel(u, 'AVgq')
    local integer gain = 0
    if GetUnitTypeId(u) == 'HVg1' and rank > 0 and not IsUnitIllusion(u) and IsUnitEnemy(victim, GetOwningPlayer(u)) and not IsUnitIllusion(victim) and not IsUnitType(victim, UNIT_TYPE_SUMMONED) and not IsUnitType(victim, UNIT_TYPE_STRUCTURE) then
        if LoadUnitHandle(VG_Hash, GetHandleId(u), 701) == victim then
            set gain = 1
        endif
        if IsUnitType(victim, UNIT_TYPE_HERO) then
            set gain = gain + rank
        endif
        if gain > 0 then
            call SetHeroInt(u, GetHeroInt(u, false) + gain, true)
        endif
    endif
    set u = null
    set victim = null
endfunction

function VG_Equilibrium takes nothing returns nothing
    local group g = CreateGroup()
    local unit u
    local real maximum
    local real missing
    call GroupEnumUnitsInRect(g, bj_mapInitialPlayableArea, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if GetUnitTypeId(u) == 'HVg1' and GetWidgetLife(u) > 0.405 and not IsUnitIllusion(u) then
            set maximum = GetUnitState(u, UNIT_STATE_MAX_MANA)
            if maximum > 0.0 then
                set missing = RMaxBJ(0.0, 1.0 - GetUnitState(u, UNIT_STATE_MANA) / maximum)
                call SetUnitState(u, UNIT_STATE_MANA, RMinBJ(maximum, GetUnitState(u, UNIT_STATE_MANA) + 2.0 * missing))
            endif
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    set u = null
endfunction

function VG_ClassicCast takes nothing returns nothing
    local unit caster = GetTriggerUnit()
    local unit target = GetSpellTargetUnit()
    local integer spell = GetSpellAbilityId()
    local integer rank = GetUnitAbilityLevel(caster, spell)
    local real damage
    local real enemyInt = 0.0
    if (spell == 'AVgq' or spell == 'AVgr') and GetUnitTypeId(caster) == 'HVg1' and not IsUnitIllusion(caster) and VG_Enemy(target, GetOwningPlayer(caster)) then
        if spell == 'AVgq' then
            set damage = 80.0 + 70.0 * rank + 0.6 * GetHeroInt(caster, true)
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilSpecialArt.mdl", target, "chest"))
            call SaveUnitHandle(VG_Hash, GetHandleId(caster), 701, target)
            call UnitDamageTarget(caster, target, damage, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
            call RemoveSavedHandle(VG_Hash, GetHandleId(caster), 701)
        elseif IsUnitType(target, UNIT_TYPE_HERO) then
            set enemyInt = I2R(GetHeroInt(target, true))
            set damage = 250.0 + 300.0 * rank + 1.2 * GetHeroInt(caster, true) + 0.8 * enemyInt
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DeathPact\\DeathPactTarget.mdl", target, "origin"))
            call UnitDamageTarget(caster, target, damage, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
        endif
    endif
    set caster = null
    set target = null
endfunction
