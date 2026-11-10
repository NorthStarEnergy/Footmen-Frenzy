function MU_GasExpire takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    call DestroyEffect(LoadEffectHandle(MU_Hash, h, 30))
    call FlushChildHashtable(MU_Hash, h)
    call DestroyTimer(t)
    set t = null
endfunction

function MU_GasSpawn takes unit u, integer rank returns nothing
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    local unit cloud = CreateUnit(GetOwningPlayer(u), 'hor3', x, y, 0.0)
    local effect fx = AddSpecialEffect("Abilities\\Spells\\Undead\\PlagueCloud\\PlagueCloudCaster.mdl", x, y)
    local timer t = CreateTimer()
    call UnitAddAbility(cloud, 'AMug')
    call SetUnitAbilityLevel(cloud, 'AMug', rank)
    call UnitApplyTimedLife(cloud, 'BTLF', 3.0)
    call BlzSetSpecialEffectColor(fx, 160 - 12 * rank, 190 + 8 * rank, 90 + 7 * rank)
    call SaveEffectHandle(MU_Hash, GetHandleId(t), 30, fx)
    call TimerStart(t, 3.0, false, function MU_GasExpire)
    set cloud = null
    set fx = null
    set t = null
endfunction

function MU_FlingTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit target = LoadUnitHandle(MU_Hash, h, 31)
    local unit caster = LoadUnitHandle(MU_Hash, h, 32)
    local real p = LoadReal(MU_Hash, h, 33) + 0.0625
    local real x = LoadReal(MU_Hash, h, 34) + p * LoadReal(MU_Hash, h, 36)
    local real y = LoadReal(MU_Hash, h, 35) + p * LoadReal(MU_Hash, h, 37)
    if target == null or not FS_Alive(target) or not FS_Alive(caster) or p >= 1.0 or IsTerrainPathable(x, y, PATHING_TYPE_WALKABILITY) then
        if target != null and GetUnitTypeId(target) != 0 then
            call SetUnitFlyHeight(target, LoadReal(MU_Hash, h, 38), 0.0)
            call BlzPauseUnitEx(target, false)
            call RemoveSavedBoolean(MU_Hash, GetHandleId(target), 39)
            if FS_Alive(target) and FS_Alive(caster) and p >= 1.0 and not IsTerrainPathable(x, y, PATHING_TYPE_WALKABILITY) then
                call SetUnitX(target, x)
                call SetUnitY(target, y)
                call FS_Hit(caster, target, LoadReal(MU_Hash, h, 40))
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Orc\\WarStomp\\WarStompTarget.mdl", target, "origin"))
            endif
        endif
        call FlushChildHashtable(MU_Hash, h)
        call DestroyTimer(t)
    else
        call SetUnitX(target, x)
        call SetUnitY(target, y)
        call SetUnitFlyHeight(target, LoadReal(MU_Hash, h, 38) + 600.0 * p * (1.0 - p), 0.0)
        call SaveReal(MU_Hash, h, 33, p)
    endif
    set target = null
    set caster = null
    set t = null
endfunction

function MU_Fling takes unit caster, unit target, integer rank returns boolean
    local real x
    local real y
    local real angle
    local real dx
    local real dy
    local timer t
    local integer h
    if target == null or not FS_Enemy(target, GetOwningPlayer(caster)) or IsUnitType(target, UNIT_TYPE_FLYING) or IsUnitType(target, UNIT_TYPE_MECHANICAL) or LoadBoolean(MU_Hash, GetHandleId(target), 39) then
        return false
    endif
    set x = GetUnitX(target)
    set y = GetUnitY(target)
    set angle = Atan2(y - GetUnitY(caster), x - GetUnitX(caster))
    set dx = GetUnitX(caster) - 200.0 * Cos(angle) - x
    set dy = GetUnitY(caster) - 200.0 * Sin(angle) - y
    if IsTerrainPathable(x + dx, y + dy, PATHING_TYPE_WALKABILITY) then
        return false
    endif
    set t = CreateTimer()
    set h = GetHandleId(t)
    call SaveUnitHandle(MU_Hash, h, 31, target)
    call SaveUnitHandle(MU_Hash, h, 32, caster)
    call SaveReal(MU_Hash, h, 33, 0.0)
    call SaveReal(MU_Hash, h, 34, x)
    call SaveReal(MU_Hash, h, 35, y)
    call SaveReal(MU_Hash, h, 36, dx)
    call SaveReal(MU_Hash, h, 37, dy)
    call SaveReal(MU_Hash, h, 38, GetUnitFlyHeight(target))
    call SaveReal(MU_Hash, h, 40, 50.0 + 30.0 * (rank - 1))
    call SaveBoolean(MU_Hash, GetHandleId(target), 39, true)
    if GetUnitAbilityLevel(target, 'Amrf') == 0 then
        call UnitAddAbility(target, 'Amrf')
        call UnitRemoveAbility(target, 'Amrf')
    endif
    call BlzPauseUnitEx(target, true)
    call TimerStart(t, 0.03125, true, function MU_FlingTick)
    set t = null
    return true
endfunction
