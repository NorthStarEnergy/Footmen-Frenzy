function ST_Alive takes unit u returns boolean
    return GetUnitTypeId(u) == ST_UNIT and GetWidgetLife(u) > 0.405 and not IsUnitType(u, UNIT_TYPE_DEAD)
endfunction
function ST_Register takes unit u returns nothing
    local integer h = GetHandleId(u)
    if ST_Alive(u) and not IsUnitInGroup(u, ST_Units) then
        call GroupAddUnit(ST_Units, u)
        call SaveReal(ST_Hash, h, 0, ST_Now - ST_REGEN_DELAY)
        call SaveReal(ST_Hash, h, 1, 0.0)
        call SetUnitState(u, UNIT_STATE_MANA, ST_MAX_SHIELD)
    endif
endfunction
function ST_Enter takes nothing returns nothing
    call ST_Register(GetTriggerUnit())
endfunction
function ST_Selection takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local integer id = GetPlayerId(GetTriggerPlayer())
    if id < 12 then
        if GetTriggerEventId() == EVENT_PLAYER_UNIT_SELECTED then
            if GetUnitTypeId(u) == ST_UNIT then
                call GroupAddUnit(ST_Selected[id], u)
            endif
        else
            call GroupRemoveUnit(ST_Selected[id], u)
        endif
    endif
    set u = null
endfunction
function ST_Bonus takes nothing returns nothing
    local unit source = GetEventDamageSource()
    local unit target = GetTriggerUnit()
    local integer armor = BlzGetUnitIntegerField(target, UNIT_IF_DEFENSE_TYPE)
    // Warcraft heavy/fortified armor is the map's explicit Armored mapping.
    if GetUnitTypeId(source) == ST_UNIT and BlzGetEventIsAttack() and GetEventDamage() > 0.0 and (armor == 2 or armor == 3 or GetUnitTypeId(target) == ST_UNIT) then
        call BlzSetEventDamage(GetEventDamage() + 5.0)
    endif
    set source = null
    set target = null
endfunction
function ST_Damage takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local real damage = GetEventDamage()
    local real shield
    local real absorbed
    local effect fx
    if ST_Alive(u) and damage > 0.0 then
        call ST_Register(u)
        call SaveReal(ST_Hash, GetHandleId(u), 0, ST_Now)
        set shield = GetUnitState(u, UNIT_STATE_MANA)
        set absorbed = RMinBJ(shield, damage)
        if absorbed > 0.0 then
            call SetUnitState(u, UNIT_STATE_MANA, shield - absorbed)
            call BlzSetEventDamage(damage - absorbed)
            set fx = AddSpecialEffectTarget("Abilities\\Spells\\Items\\SpellShieldAmulet\\SpellShieldCaster.mdl", u, "chest")
            call BlzSetSpecialEffectScale(fx, 0.65)
            call DestroyEffect(fx)
            set fx = null
        endif
    endif
    set u = null
endfunction
function ST_Tick takes nothing returns nothing
    local integer i = 0
    local integer j
    local unit u
    local integer h
    set ST_Now = ST_Now + 0.25
    loop
        exitwhen i >= BlzGroupGetSize(ST_Units)
        set u = BlzGroupUnitAt(ST_Units, i)
        set h = GetHandleId(u)
        if not ST_Alive(u) then
            call GroupRemoveUnit(ST_Units, u)
            set j = 0
            loop
                exitwhen j >= 12
                call GroupRemoveUnit(ST_Selected[j], u)
                set j = j + 1
            endloop
            call FlushChildHashtable(ST_Hash, h)
        else
            if ST_Now - LoadReal(ST_Hash, h, 0) >= ST_REGEN_DELAY then
                call SetUnitState(u, UNIT_STATE_MANA, RMinBJ(ST_MAX_SHIELD, GetUnitState(u, UNIT_STATE_MANA) + 0.5))
            endif
            set i = i + 1
        endif
    endloop
    set u = null
endfunction
function ST_Ready takes unit u, player p returns boolean
    return ST_Alive(u) and GetOwningPlayer(u) == p and not IsUnitIllusion(u) and not IsUnitPaused(u) and not IsUnitHidden(u) and GetUnitAbilityLevel(u, 'Bstn') == 0 and GetUnitAbilityLevel(u, 'BPSE') == 0 and GetUnitAbilityLevel(u, 'Bens') == 0 and GetUnitAbilityLevel(u, 'Bena') == 0 and GetUnitAbilityLevel(u, 'Bsil') == 0 and GetUnitAbilityLevel(u, 'BNsi') == 0 and LoadReal(ST_Hash, GetHandleId(u), 1) <= ST_Now
endfunction
function ST_HideProbeItem takes nothing returns nothing
    local item ground = GetEnumItem()
    local integer h = GetHandleId(ST_Probe)
    local integer count
    if IsItemVisible(ground) then
        set count = LoadInteger(ST_Hash, h, 0) + 1
        call SaveInteger(ST_Hash, h, 0, count)
        call SaveItemHandle(ST_Hash, h, count, ground)
        call SetItemVisible(ground, false)
    endif
    set ground = null
endfunction
function ST_Space takes unit mover, player p, real x, real y returns boolean
    local group g
    local unit u
    local boolean ok = true
    local real dx
    local real dy
    local real radius = RMaxBJ(8.0, BlzGetUnitCollisionSize(mover))
    local rect scan
    local integer hidden
    local item ground
    if x < GetRectMinX(bj_mapInitialPlayableArea) + 40.0 or x > GetRectMaxX(bj_mapInitialPlayableArea) - 40.0 or y < GetRectMinY(bj_mapInitialPlayableArea) + 40.0 or y > GetRectMaxY(bj_mapInitialPlayableArea) - 40.0 or not IsVisibleToPlayer(x, y, p) then
        return false
    endif
    if IsTerrainPathable(x, y, PATHING_TYPE_WALKABILITY) or IsTerrainPathable(x + radius, y, PATHING_TYPE_WALKABILITY) or IsTerrainPathable(x - radius, y, PATHING_TYPE_WALKABILITY) or IsTerrainPathable(x, y + radius, PATHING_TYPE_WALKABILITY) or IsTerrainPathable(x, y - radius, PATHING_TYPE_WALKABILITY) then
        return false
    endif
    // Hidden item's actual placement also catches destructibles and buildings.
    // Loose loot blocks items, not walkers. Restore its visibility immediately.
    set scan = Rect(x - 64.0, y - 64.0, x + 64.0, y + 64.0)
    call EnumItemsInRect(scan, null, function ST_HideProbeItem)
    call RemoveRect(scan)
    set scan = null
    call SetItemPosition(ST_Probe, x, y)
    call SetItemVisible(ST_Probe, false)
    set dx = GetItemX(ST_Probe) - x
    set dy = GetItemY(ST_Probe) - y
    set hidden = LoadInteger(ST_Hash, GetHandleId(ST_Probe), 0)
    loop
        exitwhen hidden <= 0
        set ground = LoadItemHandle(ST_Hash, GetHandleId(ST_Probe), hidden)
        call SetItemVisible(ground, true)
        set hidden = hidden - 1
    endloop
    call FlushChildHashtable(ST_Hash, GetHandleId(ST_Probe))
    set ground = null
    if dx * dx + dy * dy > 100.0 then
        return false
    endif
    set g = CreateGroup()
    call GroupEnumUnitsInRange(g, x, y, 256.0, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if u != mover and GetWidgetLife(u) > 0.405 and not IsUnitType(u, UNIT_TYPE_DEAD) and not IsUnitType(u, UNIT_TYPE_FLYING) and not IsUnitHidden(u) and GetUnitAbilityLevel(u, 'Aloc') == 0 then
            set dx = GetUnitX(u) - x
            set dy = GetUnitY(u) - y
            if dx * dx + dy * dy < (BlzGetUnitCollisionSize(mover) + BlzGetUnitCollisionSize(u)) * (BlzGetUnitCollisionSize(mover) + BlzGetUnitCollisionSize(u)) then
                set ok = false
            endif
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    return ok
endfunction
function ST_FindLanding takes unit u, player p, real x, real y returns boolean
    local integer ring = 0
    local integer k
    local real a
    local real nx
    local real ny
    local real dx
    local real dy
    loop
        exitwhen ring > 3
        set k = 0
        loop
            exitwhen k >= 12
            set a = I2R(k) * bj_PI / 6.0
            set nx = x + I2R(ring) * 32.0 * Cos(a)
            set ny = y + I2R(ring) * 32.0 * Sin(a)
            set dx = nx - GetUnitX(u)
            set dy = ny - GetUnitY(u)
            if dx * dx + dy * dy <= ST_RANGE * ST_RANGE + 0.01 and ST_Space(u, p, nx, ny) then
                set ST_LandX = nx
                set ST_LandY = ny
                return true
            endif
            if ring == 0 then
                set k = 12
            else
                set k = k + 1
            endif
        endloop
        set ring = ring + 1
    endloop
    return false
endfunction
function ST_Move takes unit u, player p, real dx, real dy returns boolean
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    local real facing = GetUnitFacing(u)
    local effect fx
    if not ST_FindLanding(u, p, x + dx, y + dy) then
        return false
    endif
    // Placement was validated for terrain, visibility, collision, and range.
    set fx = AddSpecialEffect("Abilities\\Spells\\NightElf\\Blink\\BlinkCaster.mdl", x, y)
    call BlzSetSpecialEffectColor(fx, 110, 130, 255)
    call DestroyEffect(fx)
    // Landing has already been checked. Coordinate setters avoid a second
    // placement search and do not issue SetUnitPosition's implicit Stop order.
    call SetUnitX(u, ST_LandX)
    call SetUnitY(u, ST_LandY)
    call SetUnitFacing(u, facing)
    call SaveReal(ST_Hash, GetHandleId(u), 1, ST_Now + ST_COOLDOWN)
    call BlzStartUnitAbilityCooldown(u, ST_BLINK, ST_COOLDOWN)
    set fx = AddSpecialEffect("Abilities\\Spells\\NightElf\\Blink\\BlinkTarget.mdl", GetUnitX(u), GetUnitY(u))
    call BlzSetSpecialEffectColor(fx, 110, 130, 255)
    call DestroyEffect(fx)
    // Preserve the map's lantern/tether teleport handling.
    call TFP_FFDP_NotifyTeleport(u, true)
    set fx = null
    return true
endfunction
function ST_Cast takes nothing returns nothing
    local unit caster = GetTriggerUnit()
    local player p = GetOwningPlayer(caster)
    local integer id = GetPlayerId(p)
    local real x = GetUnitX(caster)
    local real y = GetUnitY(caster)
    local real dx = GetSpellTargetX() - x
    local real dy = GetSpellTargetY() - y
    local real distance = SquareRoot(dx * dx + dy * dy)
    local integer i = 0
    local unit u
    local real ux
    local real uy
    local boolean moved = false
    local group pending = null
    local integer j
    local unit next = null
    local real projection
    local real best
    if GetSpellAbilityId() == ST_BLINK and id < 12 and ST_Ready(caster, p) then
        if distance > ST_RANGE then
            set dx = dx * ST_RANGE / distance
            set dy = dy * ST_RANGE / distance
        endif
        if distance > 1.0 then
            set pending = CreateGroup()
            call GroupAddUnit(pending, caster)
            loop
                exitwhen i >= BlzGroupGetSize(ST_Units)
                set u = BlzGroupUnitAt(ST_Units, i)
                set ux = GetUnitX(u) - x
                set uy = GetUnitY(u) - y
                if u != caster and ST_Ready(u, p) and IsUnitInGroup(u, ST_Selected[id]) and ux * ux + uy * uy <= 1440000.0 and BlzGetUnitAbilityCooldownRemaining(u, ST_BLINK) <= 0.0 then
                    call GroupAddUnit(pending, u)
                endif
                set i = i + 1
            endloop
            // Move the leading edge first. Rear units can use the space their
            // selected squadmates vacated; blocked front units still obstruct.
            loop
                exitwhen BlzGroupGetSize(pending) == 0
                set j = 0
                set best = -1000000000.0
                set next = null
                loop
                    exitwhen j >= BlzGroupGetSize(pending)
                    set u = BlzGroupUnitAt(pending, j)
                    set projection = GetUnitX(u) * dx + GetUnitY(u) * dy
                    if next == null or projection > best then
                        set next = u
                        set best = projection
                    endif
                    set j = j + 1
                endloop
                call GroupRemoveUnit(pending, next)
                if ST_Ready(next, p) then
                    if next == caster then
                        set moved = ST_Move(next, p, dx, dy)
                    else
                        call ST_Move(next, p, dx, dy)
                    endif
                endif
            endloop
            call DestroyGroup(pending)
        endif
        if not moved then
            call BlzEndUnitAbilityCooldown(caster, ST_BLINK)
        endif
    endif
    set caster = null
    set p = null
    set u = null
    set next = null
    set pending = null
endfunction
function ST_Summon takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local group g = CreateGroup()
    local unit u
    local integer i = 0
    local integer count = 0
    local real x = GetStartLocationX(GetPlayerStartLocation(p))
    local real y = GetStartLocationY(GetPlayerStartLocation(p))
    if LX_TestAllowed() and GetPlayerId(p) < 12 then
        loop
            exitwhen i >= BlzGroupGetSize(ST_Units)
            set u = BlzGroupUnitAt(ST_Units, i)
            if ST_Alive(u) and GetOwningPlayer(u) == p then
                call GroupAddUnit(g, u)
                set count = count + 1
            endif
            set i = i + 1
        endloop
        if count == 0 then
            set i = 0
            loop
                exitwhen i >= 8
                set u = CreateUnit(p, ST_UNIT, x + I2R(ModuloInteger(i, 4)) * 100.0 - 150.0, y + I2R(i / 4) * 100.0 + 200.0, 270.0)
                call ST_Register(u)
                call GroupAddUnit(FF_TestRecruited, u)
                call GroupAddUnit(g, u)
                set i = i + 1
            endloop
        endif
        call SelectGroupForPlayerBJ(g, p)
        call DisplayTimedTextToPlayer(p, 0.0, 0.0, 15.0, "Stalkers: select the squad, then B + click to Blink together. 800 range / 7 sec per unit. Blue mana bar = 80 shields; regenerates 2/sec after 7 sec without damage. Heavy/fortified targets take +5 attack damage.")
    else
        call DisplayTimedTextToPlayer(p, 0.0, 0.0, 10.0, "Stalker test: use -stalkers in Debug mode or a solo game.")
    endif
    call DestroyGroup(g)
    set g = null
    set u = null
    set p = null
endfunction
function ST_Init takes nothing returns nothing
    local trigger cast = CreateTrigger()
    local trigger damage = CreateTrigger()
    local trigger bonus = CreateTrigger()
    local trigger select = CreateTrigger()
    local trigger chat = CreateTrigger()
    local trigger enter = CreateTrigger()
    local region world = CreateRegion()
    local group g = CreateGroup()
    local unit u
    local timer tick = CreateTimer()
    local integer i = 0
    set ST_Hash = InitHashtable()
    set ST_Units = CreateGroup()
    set ST_Probe = CreateItem('wolg', 0.0, 0.0)
    call SetItemVisible(ST_Probe, false)
    call SetItemInvulnerable(ST_Probe, true)
    loop
        exitwhen i >= bj_MAX_PLAYER_SLOTS
        call TriggerRegisterPlayerUnitEvent(damage, Player(i), EVENT_PLAYER_UNIT_DAMAGED, null)
        call TriggerRegisterPlayerUnitEvent(bonus, Player(i), EVENT_PLAYER_UNIT_DAMAGING, null)
        if i < 12 then
            set ST_Selected[i] = CreateGroup()
            call TriggerRegisterPlayerUnitEvent(select, Player(i), EVENT_PLAYER_UNIT_SELECTED, null)
            call TriggerRegisterPlayerUnitEvent(select, Player(i), EVENT_PLAYER_UNIT_DESELECTED, null)
            call TriggerRegisterPlayerChatEvent(chat, Player(i), "-stalker", true)
            call TriggerRegisterPlayerChatEvent(chat, Player(i), "-stalkers", true)
        endif
        set i = i + 1
    endloop
    call TriggerAddAction(damage, function ST_Damage)
    call TriggerAddAction(bonus, function ST_Bonus)
    call TriggerAddAction(select, function ST_Selection)
    call TriggerAddAction(chat, function ST_Summon)
    call TriggerRegisterAnyUnitEventBJ(cast, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddAction(cast, function ST_Cast)
    call RegionAddRect(world, GetWorldBounds())
    call TriggerRegisterEnterRegion(enter, world, null)
    call TriggerAddAction(enter, function ST_Enter)
    call GroupEnumUnitsInRect(g, bj_mapInitialPlayableArea, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        call ST_Register(u)
    endloop
    call DestroyGroup(g)
    call TimerStart(tick, 0.25, true, function ST_Tick)
    set cast = null
    set damage = null
    set bonus = null
    set select = null
    set chat = null
    set enter = null
    set world = null
    set tick = null
    set g = null
    set u = null
endfunction