// Per-cast state makes overlapping cages and strikes independent.
function VG_Enemy takes unit u, player p returns boolean
    return GetUnitTypeId(u) != 0 and GetWidgetLife(u) > 0.405 and IsUnitEnemy(u, p) and not IsUnitType(u, UNIT_TYPE_STRUCTURE) and not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) and GetUnitAbilityLevel(u, 'Aloc') == 0
endfunction

function VG_Z takes real x, real y returns real
    local location l = Location(x, y)
    local real z = GetLocationZ(l)
    call RemoveLocation(l)
    set l = null
    return z
endfunction

// Segment/annulus intersection: even a fast crossing cannot skip the rim.
function VG_Crosses takes real ax, real ay, real bx, real by returns boolean
    local real dx = bx - ax
    local real dy = by - ay
    local real len = dx * dx + dy * dy
    local real f = 0.0
    local real near2
    local real far2 = RMaxBJ(ax * ax + ay * ay, bx * bx + by * by)
    if len > 0.0001 then
        set f = RMaxBJ(0.0, RMinBJ(1.0, -(ax * dx + ay * dy) / len))
    endif
    set near2 = (ax + f * dx) * (ax + f * dx) + (ay + f * dy) * (ay + f * dy)
    return near2 <= 325.0 * 325.0 and far2 >= 275.0 * 275.0
endfunction

function VG_Cleanup takes timer t returns nothing
    local integer h = GetHandleId(t)
    local integer n = 0
    loop
        exitwhen n >= 40
        call DestroyLightning(LoadLightningHandle(VG_Hash, h, 100 + n))
        set n = n + 1
    endloop
    call DestroyEffect(LoadEffectHandle(VG_Hash, h, 7))
    call DestroyGroup(LoadGroupHandle(VG_Hash, h, 5))
    call DestroyGroup(LoadGroupHandle(VG_Hash, h, 6))
    call FlushChildHashtable(VG_Hash, h)
    call FlushChildHashtable(VG_PrevX, h)
    call FlushChildHashtable(VG_PrevY, h)
    call PauseTimer(t)
    call DestroyTimer(t)
endfunction

function VG_CageScan takes integer h returns nothing
    local group g = LoadGroupHandle(VG_Hash, h, 6)
    local group hit = LoadGroupHandle(VG_Hash, h, 5)
    local unit caster = LoadUnitHandle(VG_Hash, h, 0)
    local player owner = LoadPlayerHandle(VG_Hash, h, 9)
    local real x = LoadReal(VG_Hash, h, 1)
    local real y = LoadReal(VG_Hash, h, 2)
    local real ux
    local real uy
    local real px
    local real py
    local integer id
    local unit u
    local unit dummy
    // Track the whole playable area so fast movement retains its previous point.
    call GroupEnumUnitsInRect(g, bj_mapInitialPlayableArea, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if VG_Enemy(u, owner) and not IsUnitInGroup(u, hit) then
            set id = GetHandleId(u)
            set ux = GetUnitX(u) - x
            set uy = GetUnitY(u) - y
            set px = ux
            set py = uy
            if HaveSavedReal(VG_PrevX, h, id) then
                set px = LoadReal(VG_PrevX, h, id)
                set py = LoadReal(VG_PrevY, h, id)
            endif
            if VG_Crosses(px, py, ux, uy) then
                set dummy = CreateUnit(owner, 'hor3', GetUnitX(u), GetUnitY(u), 0.0)
                call UnitAddAbility(dummy, 'AVgs')
                if IssueTargetOrder(dummy, "thunderbolt", u) then
                    call GroupAddUnit(hit, u)
                endif
                call UnitApplyTimedLife(dummy, 'BTLF', 1.0)
            endif
            call SaveReal(VG_PrevX, h, id, ux)
            call SaveReal(VG_PrevY, h, id, uy)
        endif
    endloop
    set dummy = null
    set u = null
    set caster = null
    set owner = null
    set g = null
    set hit = null
endfunction

function VG_Tick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local real age = LoadReal(VG_Hash, h, 3) + 0.03125
    local real x = LoadReal(VG_Hash, h, 1)
    local real y = LoadReal(VG_Hash, h, 2)
    local unit caster = LoadUnitHandle(VG_Hash, h, 0)
    local player owner = LoadPlayerHandle(VG_Hash, h, 9)
    local group g
    local unit u
    local effect fx
    call SaveReal(VG_Hash, h, 3, age)
    if GetUnitTypeId(caster) == 0 then
        call VG_Cleanup(t)
    elseif LoadInteger(VG_Hash, h, 4) == 1 then
        if age >= 3.0 then
            call VG_Cleanup(t)
        else
            call VG_CageScan(h)
        endif
    else
        if age >= 0.75 then
            set fx = LoadEffectHandle(VG_Hash, h, 7)
            if fx == null then
                set fx = AddSpecialEffect("Abilities\\Spells\\Demon\\DarkPortal\\DarkPortalTarget.mdl", x, y)
                call BlzSetSpecialEffectScale(fx, 0.65)
                call SaveEffectHandle(VG_Hash, h, 7, fx)
            endif
            call BlzSetSpecialEffectZ(fx, VG_Z(x, y) + RMaxBJ(0.0, (1.25 - age) * 1400.0))
        endif
        if age >= 1.25 then
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Undead\\DeathAndDecay\\DeathAndDecayTarget.mdl", x, y))
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Undead\\FrostNova\\FrostNovaTarget.mdl", x, y))
            set g = LoadGroupHandle(VG_Hash, h, 6)
            call GroupEnumUnitsInRange(g, x, y, 225.0, null)
            loop
                set u = FirstOfGroup(g)
                exitwhen u == null
                call GroupRemoveUnit(g, u)
                if VG_Enemy(u, owner) then
                    call UnitDamageTarget(caster, u, 300.0, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
                endif
            endloop
            call VG_Cleanup(t)
        endif
    endif
    set fx = null
    set u = null
    set g = null
    set caster = null
    set owner = null
    set t = null
endfunction

function VG_Cast takes nothing returns nothing
    local integer spell = GetSpellAbilityId()
    local timer t
    local integer h
    local integer n = 0
    local real x = GetSpellTargetX()
    local real y = GetSpellTargetY()
    local real radius = 225.0
    local real z = 12.0
    local real a
    local real b
    local lightning rim
    if spell != 'AVge' and spell != 'AVgw' then
        return
    endif
    set t = CreateTimer()
    set h = GetHandleId(t)
    call SaveUnitHandle(VG_Hash, h, 0, GetTriggerUnit())
    call SavePlayerHandle(VG_Hash, h, 9, GetOwningPlayer(GetTriggerUnit()))
    call SaveReal(VG_Hash, h, 1, x)
    call SaveReal(VG_Hash, h, 2, y)
    call SaveReal(VG_Hash, h, 3, 0.0)
    call SaveGroupHandle(VG_Hash, h, 5, CreateGroup())
    call SaveGroupHandle(VG_Hash, h, 6, CreateGroup())
    if spell == 'AVge' then
        set radius = 300.0
        set z = 90.0
        call SaveInteger(VG_Hash, h, 4, 1)
        call VG_CageScan(h)
    endif
    loop
        exitwhen n >= 40
        set a = 2.0 * bj_PI * n / 40.0
        set b = 2.0 * bj_PI * (n + 1) / 40.0
        set rim = AddLightningEx("DRAL", true, x + radius * Cos(a), y + radius * Sin(a), VG_Z(x + radius * Cos(a), y + radius * Sin(a)) + z, x + radius * Cos(b), y + radius * Sin(b), VG_Z(x + radius * Cos(b), y + radius * Sin(b)) + z)
        call SetLightningColor(rim, 0.65, 0.15, 1.0, 0.9)
        call SaveLightningHandle(VG_Hash, h, 100 + n, rim)
        set n = n + 1
    endloop
    call TimerStart(t, 0.03125, true, function VG_Tick)
    set rim = null
    set t = null
endfunction

function VG_Summon takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer id = GetPlayerId(p)
    local unit u = VG_Hero[id]
    local real x = GetStartLocationX(GetPlayerStartLocation(p))
    local real y = GetStartLocationY(GetPlayerStartLocation(p))
    if GetUnitTypeId(u) == 0 then
        if GetUnitTypeId(udg_herO[id + 1]) != 0 then
            set x = GetUnitX(udg_herO[id + 1]) + 150.0
            set y = GetUnitY(udg_herO[id + 1])
        endif
        set u = CreateUnit(p, 'HVg1', x, y, 270.0)
        set VG_Hero[id] = u
        call SetUnitUseFood(u, false)
    elseif GetWidgetLife(u) <= 0.405 then
        call ReviveHero(u, x, y, true)
    endif
    call SelectUnitForPlayerSingle(u, p)
    call DisplayTimedTextToPlayer(p, 0.0, 0.0, 12.0, "Veigar prototype: E = Event Horizon, W = Dark Matter. Both spells are ready to use.")
    set p = null
    set u = null
endfunction

function VG_Init takes nothing returns nothing
    local trigger cast = CreateTrigger()
    local trigger chat = CreateTrigger()
    local integer i = 0
    set VG_Hash = InitHashtable()
    set VG_PrevX = InitHashtable()
    set VG_PrevY = InitHashtable()
    call TriggerRegisterAnyUnitEventBJ(cast, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddAction(cast, function VG_Cast)
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(chat, Player(i), "-veigar", true)
        set i = i + 1
    endloop
    call TriggerAddAction(chat, function VG_Summon)
    set cast = null
    set chat = null
endfunction
