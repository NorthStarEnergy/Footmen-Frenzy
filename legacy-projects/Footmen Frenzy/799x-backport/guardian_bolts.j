function GDB_Clear takes unit caster returns nothing
    local integer k = GetHandleId(caster)
    local integer n = 0
    loop
        exitwhen n == 2
        call DestroyLightning(LoadLightningHandle(GDV_Data, k, 50 + n))
        call RemoveSavedHandle(GDV_Data, k, 50 + n)
        call RemoveSavedHandle(GDV_Data, k, 52 + n)
        call RemoveSavedInteger(GDV_Data, k, 54 + n)
        set n = n + 1
    endloop
endfunction

function GDB_Visual takes unit caster returns nothing
    local integer k = GetHandleId(caster)
    local integer n = 0
    local unit target
    local lightning beam
    local real alpha
    loop
        exitwhen n == 2
        set beam = LoadLightningHandle(GDV_Data, k, 50 + n)
        if beam != null then
            set target = LoadUnitHandle(GDV_Data, k, 52 + n)
            if GDV_Step >= LoadInteger(GDV_Data, k, 54 + n) or GetUnitTypeId(target) == 0 or GetWidgetLife(target) <= 0.405 then
                call DestroyLightning(beam)
                call RemoveSavedHandle(GDV_Data, k, 50 + n)
                call RemoveSavedHandle(GDV_Data, k, 52 + n)
                call RemoveSavedInteger(GDV_Data, k, 54 + n)
            else
                call MoveLocation(GDB_Loc, GetUnitX(target), GetUnitY(target))
                call MoveLightningEx(beam, true, GetUnitX(caster), GetUnitY(caster), GetLocationZ(GD_Loc) + GetUnitFlyHeight(caster) + 100.0, GetUnitX(target), GetUnitY(target), GetLocationZ(GDB_Loc) + GetUnitFlyHeight(target) + 65.0)
                set alpha = 0.5 * I2R(LoadInteger(GDV_Data, k, 54 + n) - GDV_Step) / 7.0
                if n == 0 then
                    call SetLightningColor(beam, 0.3, 1.0, 0.8, alpha)
                else
                    call SetLightningColor(beam, 0.65, 0.4, 1.0, alpha)
                endif
            endif
        endif
        set n = n + 1
    endloop
    set target = null
    set beam = null
endfunction

function GDB_Hit takes unit caster, unit target, boolean ally returns nothing
    local integer k = GetHandleId(caster)
    local integer slot = 1
    local real amount = 20.0 + 5.0 * I2R(GetUnitAbilityLevel(caster, 'AZd1'))
    local unit dummy
    local lightning beam
    if target == null then
        return
    endif
    set dummy = CreateUnit(GetOwningPlayer(caster), 'hor3', GetUnitX(target), GetUnitY(target), 0.0)
    if ally then
        set slot = 0
        call SetWidgetLife(target, RMinBJ(GetUnitState(target, UNIT_STATE_MAX_LIFE), GetWidgetLife(target) + amount))
        call SetUnitState(target, UNIT_STATE_MANA, RMinBJ(GetUnitState(target, UNIT_STATE_MAX_MANA), GetUnitState(target, UNIT_STATE_MANA) + 10.0))
        call UnitAddAbility(dummy, 'AGbs')
        call IssueTargetOrder(dummy, "bloodlust", target)
    else
        call SetUnitState(target, UNIT_STATE_MANA, RMaxBJ(0.0, GetUnitState(target, UNIT_STATE_MANA) - 10.0))
        call UnitAddAbility(dummy, 'AGbn')
        call IssueTargetOrder(dummy, "slow", target)
        call UnitDamageTarget(caster, target, amount, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
    endif
    call UnitApplyTimedLife(dummy, 'BTLF', 1.0)
    call DestroyLightning(LoadLightningHandle(GDV_Data, k, 50 + slot))
    call MoveLocation(GDB_Loc, GetUnitX(target), GetUnitY(target))
    set beam = AddLightningEx("DRAM", true, GetUnitX(caster), GetUnitY(caster), GetLocationZ(GD_Loc) + GetUnitFlyHeight(caster) + 100.0, GetUnitX(target), GetUnitY(target), GetLocationZ(GDB_Loc) + GetUnitFlyHeight(target) + 65.0)
    call SaveLightningHandle(GDV_Data, k, 50 + slot, beam)
    call SaveUnitHandle(GDV_Data, k, 52 + slot, target)
    call SaveInteger(GDV_Data, k, 54 + slot, GDV_Step + 7)
    call GDB_Visual(caster)
    set dummy = null
    set beam = null
endfunction

function GDB_Strike takes unit caster, real x, real y returns nothing
    local unit u
    local unit friendly = null
    local unit enemy = null
    local integer allies = 0
    local integer enemies = 0
    call GroupEnumUnitsInRange(GDB_Enum, x, y, 600.0, null)
    loop
        set u = FirstOfGroup(GDB_Enum)
        exitwhen u == null
        call GroupRemoveUnit(GDB_Enum, u)
        if GetWidgetLife(u) > 0.405 and not IsUnitType(u, UNIT_TYPE_STRUCTURE) and GetUnitAbilityLevel(u, 'Aloc') == 0 and not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) then
            if IsUnitAlly(u, GetOwningPlayer(caster)) then
                set allies = allies + 1
                if GetRandomInt(1, allies) == 1 then
                    set friendly = u
                endif
            elseif IsUnitEnemy(u, GetOwningPlayer(caster)) then
                set enemies = enemies + 1
                if GetRandomInt(1, enemies) == 1 then
                    set enemy = u
                endif
            endif
        endif
    endloop
    call GDB_Hit(caster, friendly, true)
    call GDB_Hit(caster, enemy, false)
    set u = null
    set friendly = null
    set enemy = null
endfunction
