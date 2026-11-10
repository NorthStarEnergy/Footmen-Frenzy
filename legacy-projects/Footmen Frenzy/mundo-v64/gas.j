function MU_PoisonTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit source = LoadUnitHandle(MU_Hash, h, 40)
    local unit victim = LoadUnitHandle(MU_Hash, h, 41)
    local integer left = LoadInteger(MU_Hash, h, 42)
    local integer rank = LoadInteger(MU_Hash, h, 43)
    if left > 0 and GetUnitTypeId(source) != 0 and FS_Alive(victim) and IsUnitEnemy(victim, GetOwningPlayer(source)) then
        call UnitDamageTarget(source, victim, (35.0 + 15.0 * (rank - 1)) * 0.5, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
        call SaveInteger(MU_Hash, h, 42, left - 1)
    else
        if LoadTimerHandle(MU_Hash, GetHandleId(source), -GetHandleId(victim)) == t then
            call RemoveSavedHandle(MU_Hash, GetHandleId(source), -GetHandleId(victim))
        endif
        call FlushChildHashtable(MU_Hash, h)
        call DestroyTimer(t)
    endif
    set source = null
    set victim = null
    set t = null
endfunction

function MU_GasExpire takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit source = LoadUnitHandle(MU_Hash, h, 40)
    local unit victim
    local timer poison
    local integer rank = LoadInteger(MU_Hash, h, 43)
    local integer left = LoadInteger(MU_Hash, h, 42)
    local group g = CreateGroup()
    if left > 0 and GetUnitTypeId(source) != 0 then
        call GroupEnumUnitsInRange(g, LoadReal(MU_Hash, h, 44), LoadReal(MU_Hash, h, 45), 250.0, null)
        loop
            set victim = FirstOfGroup(g)
            exitwhen victim == null
            call GroupRemoveUnit(g, victim)
            if FS_Alive(victim) and IsUnitEnemy(victim, GetOwningPlayer(source)) and not IsUnitType(victim, UNIT_TYPE_FLYING) and not IsUnitType(victim, UNIT_TYPE_MECHANICAL) and not IsUnitType(victim, UNIT_TYPE_STRUCTURE) and not IsUnitType(victim, UNIT_TYPE_MAGIC_IMMUNE) then
                set poison = LoadTimerHandle(MU_Hash, GetHandleId(source), -GetHandleId(victim))
                if poison == null then
                    set poison = CreateTimer()
                    call SaveTimerHandle(MU_Hash, GetHandleId(source), -GetHandleId(victim), poison)
                    call SaveUnitHandle(MU_Hash, GetHandleId(poison), 40, source)
                    call SaveUnitHandle(MU_Hash, GetHandleId(poison), 41, victim)
                    call TimerStart(poison, 0.5, true, function MU_PoisonTick)
                endif
                call SaveInteger(MU_Hash, GetHandleId(poison), 42, 4)
                call SaveInteger(MU_Hash, GetHandleId(poison), 43, rank)
            endif
        endloop
        call SaveInteger(MU_Hash, h, 42, left - 1)
    else
        call DestroyEffect(LoadEffectHandle(MU_Hash, h, 30))
        call DestroyEffect(LoadEffectHandle(MU_Hash, h, 31))
        call DestroyEffect(LoadEffectHandle(MU_Hash, h, 32))
        call FlushChildHashtable(MU_Hash, h)
        call DestroyTimer(t)
    endif
    call DestroyGroup(g)
    set g = null
    set source = null
    set victim = null
    set poison = null
    set t = null
endfunction

function MU_GasSpawn takes unit u, integer rank returns nothing
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    local timer t = CreateTimer()
    local integer h = GetHandleId(t)
    local effect fx = AddSpecialEffect("Abilities\\Spells\\Undead\\PlagueCloud\\PlagueCloudCaster.mdl", x, y)
    call BlzSetSpecialEffectScale(fx, 1.5)
    call BlzSetSpecialEffectColor(fx, 160 - 12 * rank, 190 + 8 * rank, 90 + 7 * rank)
    call SaveEffectHandle(MU_Hash, h, 30, fx)
    set fx = AddSpecialEffect("Abilities\\Spells\\Undead\\PlagueCloud\\PlagueCloudCaster.mdl", x + 70.0, y)
    call BlzSetSpecialEffectScale(fx, 1.3)
    call BlzSetSpecialEffectColor(fx, 160 - 12 * rank, 190 + 8 * rank, 90 + 7 * rank)
    call SaveEffectHandle(MU_Hash, h, 31, fx)
    set fx = AddSpecialEffect("Abilities\\Spells\\Undead\\PlagueCloud\\PlagueCloudCaster.mdl", x - 70.0, y)
    call BlzSetSpecialEffectScale(fx, 1.3)
    call BlzSetSpecialEffectColor(fx, 160 - 12 * rank, 190 + 8 * rank, 90 + 7 * rank)
    call SaveEffectHandle(MU_Hash, h, 32, fx)
    call SaveUnitHandle(MU_Hash, h, 40, u)
    call SaveInteger(MU_Hash, h, 42, 6)
    call SaveInteger(MU_Hash, h, 43, rank)
    call SaveReal(MU_Hash, h, 44, x)
    call SaveReal(MU_Hash, h, 45, y)
    call TimerStart(t, 0.5, true, function MU_GasExpire)
    set fx = null
    set t = null
endfunction