// Cosmetic coverage is refreshed by all domes before old effects are removed.
function GDV_Mark takes unit u, boolean positive returns nothing
    local integer k = GetHandleId(u)
    local integer kind = 4
    local effect fx
    if positive then
        set kind = 0
    endif
    if LoadEffectHandle(GDV_Data, k, kind) == null then
        if positive then
            set fx = AddSpecialEffectTarget("Abilities\\Spells\\Human\\InnerFire\\InnerFireTarget.mdl", u, "overhead")
            call BlzSetSpecialEffectColor(fx, 100, 210, 255)
        else
            set fx = AddSpecialEffectTarget("Abilities\\Spells\\Undead\\Curse\\CurseTarget.mdl", u, "overhead")
            call BlzSetSpecialEffectColor(fx, 190, 85, 255)
        endif
        call SaveEffectHandle(GDV_Data, k, kind, fx)
        call GroupAddUnit(GDV_Units, u)
    endif
    call SaveInteger(GDV_Data, k, kind + 2, GDV_Step)
    set fx = null
endfunction

function GDV_Pulse takes unit u, boolean positive returns nothing
    local integer k = GetHandleId(u)
    local integer slot = 7
    if positive then
        set slot = 3
    endif
    if LoadInteger(GDV_Data, k, slot) <= GDV_Step then
        if positive then
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", u, "origin"))
        else
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\ReplenishMana\\ReplenishManaCaster.mdl", u, "origin"))
        endif
        call SaveInteger(GDV_Data, k, slot, GDV_Step + 15)
    endif
endfunction

function GDV_CleanupUnit takes nothing returns nothing
    local unit u = GetEnumUnit()
    local integer k = GetHandleId(u)
    local integer kind = 0
    loop
        exitwhen kind > 4
        if GD_Count == 0 or GetUnitTypeId(u) == 0 or GetWidgetLife(u) <= 0.405 or LoadInteger(GDV_Data, k, kind + 2) != GDV_Step then
            call DestroyEffect(LoadEffectHandle(GDV_Data, k, kind))
            call RemoveSavedHandle(GDV_Data, k, kind)
            call RemoveSavedInteger(GDV_Data, k, kind + 2)
            call RemoveSavedInteger(GDV_Data, k, kind + 3)
        endif
        set kind = kind + 4
    endloop
    if LoadEffectHandle(GDV_Data, k, 0) == null and LoadEffectHandle(GDV_Data, k, 4) == null then
        call GroupRemoveUnit(GDV_Units, u)
    endif
    set u = null
endfunction

function GDV_Project takes unit caster, real x, real y returns nothing
    local integer k = GetHandleId(caster)
    local integer n = 0
    local real clock
    local integer cycle
    local real fade
    local real angle
    local real elevation
    local real radius
    local real z = GetLocationZ(GD_Loc)
    local lightning beam
    loop
        exitwhen n == 3
        set clock = I2R(GDV_Step) * GD_PERIOD / 1.2 + I2R(n) / 3.0
        set cycle = R2I(clock)
        set fade = Sin((clock - I2R(cycle)) * 3.14159265)
        set beam = LoadLightningHandle(GDV_Data, k, 20 + n)
        if beam == null or LoadInteger(GDV_Data, k, 40 + n) != cycle then
            // Irregular, synchronized endpoints without consuming gameplay RNG.
            set angle = 3.14159265 * (1.0 + Sin(I2R(cycle) * 12.9898 + I2R(n) * 78.233))
            set elevation = 0.12 + 1.25 * (0.5 + 0.5 * Sin(I2R(cycle) * 7.173 + I2R(n) * 29.417))
            call SaveReal(GDV_Data, k, 30 + n, angle)
            call SaveReal(GDV_Data, k, 35 + n, elevation)
            call SaveInteger(GDV_Data, k, 40 + n, cycle)
        endif
        set angle = LoadReal(GDV_Data, k, 30 + n)
        set elevation = LoadReal(GDV_Data, k, 35 + n)
        // Imported dome: approximately radius 600, sphere center 41 below ground.
        set radius = 600.0 * Sin(elevation)
        if beam == null then
            set beam = AddLightningEx("DRAM", true, x, y, z + GetUnitFlyHeight(caster) + 100.0, x + radius * Cos(angle), y + radius * Sin(angle), z - 41.0 + 600.0 * Cos(elevation))
            call SaveLightningHandle(GDV_Data, k, 20 + n, beam)
        else
            call MoveLightningEx(beam, true, x, y, z + GetUnitFlyHeight(caster) + 100.0, x + radius * Cos(angle), y + radius * Sin(angle), z - 41.0 + 600.0 * Cos(elevation))
        endif
        call SetLightningColor(beam, 0.35, 0.70, 1.0, 0.55 * fade * fade)
        set n = n + 1
    endloop
    set beam = null
endfunction

function GDV_Dome takes integer i, real x, real y returns nothing
    local real phase = I2R(GDV_Step) * GD_PERIOD
    local real angle
    local integer n = 0
    local integer k = GetHandleId(GD_Caster[i])
    local effect fx
    call GDV_Project(GD_Caster[i], x, y)
    call BlzSetSpecialEffectYaw(GD_Dome[i], phase * 0.22)
    call BlzSetSpecialEffectAlpha(GD_Dome[i], R2I(195.0 + 35.0 * Sin(phase * 2.0)))
    loop
        exitwhen n == 3
        set fx = LoadEffectHandle(GDV_Data, k, 10 + n)
        if fx == null then
            set fx = AddSpecialEffect("Abilities\\Weapons\\FaerieDragonMissile\\FaerieDragonMissile.mdl", x, y)
            call BlzSetSpecialEffectScale(fx, 1.3)
            call BlzSetSpecialEffectColor(fx, 90, 185, 255)
            call SaveEffectHandle(GDV_Data, k, 10 + n, fx)
        endif
        set angle = phase * 0.8 + I2R(n) * 2.0943951
        call BlzSetSpecialEffectPosition(fx, x + 420.0 * Cos(angle), y + 420.0 * Sin(angle), GetLocationZ(GD_Loc) + 230.0 + 65.0 * Sin(angle * 2.0))
        set n = n + 1
    endloop
    set fx = null
endfunction

function GDV_Stop takes unit caster returns nothing
    local integer k = GetHandleId(caster)
    local integer n = 0
    loop
        exitwhen n == 3
        call DestroyEffect(LoadEffectHandle(GDV_Data, k, 10 + n))
        call RemoveSavedHandle(GDV_Data, k, 10 + n)
        call DestroyLightning(LoadLightningHandle(GDV_Data, k, 20 + n))
        call RemoveSavedHandle(GDV_Data, k, 20 + n)
        call RemoveSavedReal(GDV_Data, k, 30 + n)
        call RemoveSavedReal(GDV_Data, k, 35 + n)
        call RemoveSavedInteger(GDV_Data, k, 40 + n)
        set n = n + 1
    endloop
endfunction
