// Test the entire footprint against the playable area, walls, and cliff tiers.
// No blanket exclusion behind bases: ordinary ground there remains eligible.
function MU_FlingSafe takes real x, real y, integer cliff, real radius returns boolean
    local integer i = 0
    local real px
    local real py
    if x-radius < GetRectMinX(bj_mapInitialPlayableArea) or x+radius > GetRectMaxX(bj_mapInitialPlayableArea) or y-radius < GetRectMinY(bj_mapInitialPlayableArea) or y+radius > GetRectMaxY(bj_mapInitialPlayableArea) then
        return false
    endif
    if GetTerrainCliffLevel(x, y) != cliff or IsTerrainPathable(x, y, PATHING_TYPE_WALKABILITY) then
        return false
    endif
    loop
        exitwhen i >= 8
        set px = x + radius*Cos(I2R(i)*bj_PI/4.0)
        set py = y + radius*Sin(I2R(i)*bj_PI/4.0)
        if GetTerrainCliffLevel(px, py) != cliff or IsTerrainPathable(px, py, PATHING_TYPE_WALKABILITY) then
            return false
        endif
        set i = i + 1
    endloop
    return true
endfunction

function MU_FlingTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit target = LoadUnitHandle(MU_Hash, h, 31)
    local unit caster = LoadUnitHandle(MU_Hash, h, 32)
    local real p = RMinBJ(1.0, LoadReal(MU_Hash, h, 33) + 0.0625)
    local real x = LoadReal(MU_Hash, h, 34) + p * LoadReal(MU_Hash, h, 36)
    local real y = LoadReal(MU_Hash, h, 35) + p * LoadReal(MU_Hash, h, 37)
    local boolean alive = FS_Alive(target) and FS_Alive(caster)
    local boolean safe = alive and MU_FlingSafe(x, y, LoadInteger(MU_Hash, h, 41), LoadReal(MU_Hash, h, 42))
    if safe then
        call SetUnitX(target, x)
        call SetUnitY(target, y)
        call SetUnitFlyHeight(target, LoadReal(MU_Hash, h, 38) + 840.0*p*(1.0-p), 0.0)
    endif
    if not alive or not safe or p >= 1.0 then
        if target != null and GetUnitTypeId(target) != 0 then
            call SetUnitFlyHeight(target, LoadReal(MU_Hash, h, 38), 0.0)
            call BlzPauseUnitEx(target, false)
            call RemoveSavedBoolean(MU_Hash, GetHandleId(target), 39)
            if alive then
                call FS_Hit(caster, target, LoadReal(MU_Hash, h, 40))
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Orc\\WarStomp\\WarStompTarget.mdl", target, "origin"))
                call DestroyEffect(AddSpecialEffectTarget("Objects\\Spawnmodels\\Human\\HumanBlood\\HumanBloodLarge0.mdl", target, "chest"))
            endif
        endif
        call FlushChildHashtable(MU_Hash, h)
        call DestroyTimer(t)
    else
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
    local real distance
    local real step
    local real progress
    local real safeProgress = 0.0
    local real radius
    local integer cliff
    local timer t
    local integer h
    if target == null or not FS_Enemy(target, GetOwningPlayer(caster)) or IsUnitType(target, UNIT_TYPE_FLYING) or IsUnitType(target, UNIT_TYPE_MECHANICAL) or LoadBoolean(MU_Hash, GetHandleId(target), 39) then
        return false
    endif
    set x = GetUnitX(target)
    set y = GetUnitY(target)
    set cliff = GetTerrainCliffLevel(x, y)
    set radius = RMaxBJ(16.0, BlzGetUnitCollisionSize(target))
    set angle = Atan2(y - GetUnitY(caster), x - GetUnitX(caster))
    set distance = 200.0 + 30.0*I2R(IMaxBJ(1, IMinBJ(6, rank))-1)
    set dx = GetUnitX(caster) - distance*Cos(angle) - x
    set dy = GetUnitY(caster) - distance*Sin(angle) - y
    set distance = SquareRoot(dx*dx+dy*dy)
    if distance < 1.0 or not MU_FlingSafe(x, y, cliff, radius) then
        return false
    endif
    // 16-unit sampling prevents skipping a 32-unit wall/pathing cell.
    set step = 16.0/distance
    set progress = RMinBJ(1.0, step)
    loop
        exitwhen not MU_FlingSafe(x+progress*dx, y+progress*dy, cliff, radius)
        set safeProgress = progress
        exitwhen progress >= 1.0
        set progress = RMinBJ(1.0, progress+step)
    endloop
    if safeProgress*distance < 16.0 then
        return false
    endif
    set t = CreateTimer()
    set h = GetHandleId(t)
    call SaveUnitHandle(MU_Hash, h, 31, target)
    call SaveUnitHandle(MU_Hash, h, 32, caster)
    call SaveReal(MU_Hash, h, 33, 0.0)
    call SaveReal(MU_Hash, h, 34, x)
    call SaveReal(MU_Hash, h, 35, y)
    call SaveReal(MU_Hash, h, 36, dx*safeProgress)
    call SaveReal(MU_Hash, h, 37, dy*safeProgress)
    call SaveReal(MU_Hash, h, 38, GetUnitFlyHeight(target))
    call SaveReal(MU_Hash, h, 40, 50.0+30.0*(rank-1))
    call SaveInteger(MU_Hash, h, 41, cliff)
    call SaveReal(MU_Hash, h, 42, radius)
    call SaveBoolean(MU_Hash, GetHandleId(target), 39, true)
    if GetUnitAbilityLevel(target, 'Amrf') == 0 then
        call UnitAddAbility(target, 'Amrf')
        call UnitRemoveAbility(target, 'Amrf')
    endif
    call BlzPauseUnitEx(target, true)
    call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilSpecialArt.mdl", target, "chest"))
    call TimerStart(t, 0.03125/1.05, true, function MU_FlingTick)
    set t = null
    return true
endfunction
