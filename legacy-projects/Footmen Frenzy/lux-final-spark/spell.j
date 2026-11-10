// Timer slots: caster 0, owner 1, x/y 2/3, direction 4/5, age 6,
// damage 7, length 8, fired 9, pause held 10, charge sound 11.
// Effects 100..139: guide/core, gold body, glow, left/right edge per segment.
function LX_Z takes real x, real y returns real
    local location p = Location(x, y)
    local real z = GetLocationZ(p)
    call RemoveLocation(p)
    set p = null
    return z
endfunction

function LX_Enemy takes unit u, player p returns boolean
    return u != null and GetUnitTypeId(u) != 0 and GetWidgetLife(u) > 0.405 and IsUnitEnemy(u, p) and not IsUnitType(u, UNIT_TYPE_STRUCTURE) and not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) and GetUnitAbilityLevel(u, 'Aloc') == 0
endfunction

function LX_InBeam takes real px, real py, real x, real y, real dx, real dy, real length returns boolean
    local real along = (px - x) * dx + (py - y) * dy
    local real across = (py - y) * dx - (px - x) * dy
    // A finite rectangle: no radial endpoint spill and no hits behind the caster.
    return along >= 0.0 and along <= length and across * across <= LX_HALF_WIDTH * LX_HALF_WIDTH
endfunction

function LX_Sound takes string path, real x, real y, real z, integer volume returns sound
    local sound s = CreateSound(path, false, true, true, 10, 10, "DefaultEAXON")
    call SetSoundChannel(s, 0)
    call SetSoundVolume(s, volume)
    call SetSoundDistances(s, 700.0, 4500.0)
    call SetSoundDistanceCutoff(s, 5000.0)
    call SetSoundPosition(s, x, y, z)
    call StartSound(s)
    return s
endfunction

function LX_Release takes integer h returns nothing
    local unit caster = LoadUnitHandle(LX_Hash, h, 0)
    if LoadBoolean(LX_Hash, h, 10) then
        call SaveBoolean(LX_Hash, h, 10, false)
        if GetUnitTypeId(caster) != 0 then
            // PauseUnitEx is reference counted; release only this spell's lock.
            call BlzPauseUnitEx(caster, false)
            call SetUnitAnimation(caster, "stand")
        endif
    endif
    if caster != null and GetHandleId(LoadTimerHandle(LX_Casters, GetHandleId(caster), 0)) == h then
        call RemoveSavedHandle(LX_Casters, GetHandleId(caster), 0)
    endif
    set caster = null
endfunction

function LX_Cleanup takes timer t returns nothing
    local integer h = GetHandleId(t)
    local integer i = 0
    local sound s = LoadSoundHandle(LX_Hash, h, 11)
    local fogmodifier vision
    call LX_Release(h)
    if s != null then
        call StopSound(s, true, true)
    endif
    loop
        exitwhen i >= LX_SEGMENTS * 5
        call DestroyEffect(LoadEffectHandle(LX_Hash, h, 100 + i))
        set i = i + 1
    endloop
    set i = 0
    loop
        exitwhen i >= LX_SEGMENTS
        set vision = LoadFogModifierHandle(LX_Hash, h, 400 + i)
        call FogModifierStop(vision)
        call DestroyFogModifier(vision)
        set i = i + 1
    endloop
    call DestroyEffect(LoadEffectHandle(LX_Hash, h, 200))
    call FlushChildHashtable(LX_Hash, h)
    call PauseTimer(t)
    call DestroyTimer(t)
    set s = null
    set vision = null
endfunction

function LX_Style takes effect fx, real length, real width, integer alpha, integer red, integer green, integer blue, real yaw, real pitch returns nothing
    // Reset first: repeated scaling must never accumulate from tick to tick.
    call BlzResetSpecialEffectMatrix(fx)
    call BlzSetSpecialEffectMatrixScale(fx, length, width, width)
    call BlzSetSpecialEffectOrientation(fx, yaw, pitch, 0.0)
    call BlzSetSpecialEffectAlpha(fx, alpha)
    call BlzSetSpecialEffectColor(fx, red, green, blue)
endfunction

function LX_Visual takes integer h, real age returns nothing
    local integer i = 0
    local real step = LoadReal(LX_Hash, h, 8) / I2R(LX_SEGMENTS)
    local real length
    local real yaw = Atan2(LoadReal(LX_Hash, h, 5), LoadReal(LX_Hash, h, 4))
    local real charge = RMinBJ(1.0, age / LX_CHARGE)
    local real pulse = 0.0
    local real fade = 1.0
    local real width = 4.0 + 9.0 * charge * charge
    local real pitch
    local effect fx
    if age >= LX_CHARGE then
        // Explode to full width immediately; settle the bloom over two ticks.
        set pulse = RMinBJ(1.0, (age - LX_CHARGE) / 0.0625)
        set width = 200.0 + 60.0 * (1.0 - pulse)
        set fade = RMinBJ(1.0, RMaxBJ(0.0, (1.4375 - age) / 0.25))
    endif
    loop
        exitwhen i >= LX_SEGMENTS
        set pitch = LoadReal(LX_Hash, h, 300 + i)
        set length = step / Cos(pitch)
        set fx = LoadEffectHandle(LX_Hash, h, 100 + i * 5)
        if age < LX_CHARGE then
            call LX_Style(fx, length, width, R2I(30.0 + 155.0 * charge * charge), 255, 125 + R2I(100.0 * charge), 65, yaw, pitch)
        else
            call LX_Style(fx, length, width * 0.48, R2I(255.0 * fade), 255, 255, 235, yaw, pitch)
        endif
        if age >= LX_CHARGE then
            call LX_Style(LoadEffectHandle(LX_Hash, h, 101 + i * 5), length, width, R2I(225.0 * fade), 255, 195, 55, yaw, pitch)
            call LX_Style(LoadEffectHandle(LX_Hash, h, 102 + i * 5), length, width * 1.65, R2I(100.0 * fade), 255, 105, 30, yaw, pitch)
        else
            call BlzSetSpecialEffectAlpha(LoadEffectHandle(LX_Hash, h, 101 + i * 5), 0)
            call BlzSetSpecialEffectAlpha(LoadEffectHandle(LX_Hash, h, 102 + i * 5), 0)
        endif
        if age < LX_CHARGE then
            call LX_Style(LoadEffectHandle(LX_Hash, h, 103 + i * 5), length, 3.0, R2I(12.0 + 45.0 * charge), 255, 165, 85, yaw, pitch)
            call LX_Style(LoadEffectHandle(LX_Hash, h, 104 + i * 5), length, 3.0, R2I(12.0 + 45.0 * charge), 255, 165, 85, yaw, pitch)
        else
            call BlzSetSpecialEffectAlpha(LoadEffectHandle(LX_Hash, h, 103 + i * 5), 0)
            call BlzSetSpecialEffectAlpha(LoadEffectHandle(LX_Hash, h, 104 + i * 5), 0)
        endif
        set i = i + 1
    endloop
    set fx = LoadEffectHandle(LX_Hash, h, 200)
    if age < LX_CHARGE then
        call BlzSetSpecialEffectScale(fx, 25.0 + 55.0 * charge * charge)
        call BlzSetSpecialEffectAlpha(fx, R2I(55.0 + 180.0 * charge))
    else
        call BlzSetSpecialEffectScale(fx, 150.0 + 90.0 * pulse)
        call BlzSetSpecialEffectAlpha(fx, R2I(240.0 * fade))
    endif
    set fx = null
endfunction

function LX_Damage takes integer h returns nothing
    local unit caster = LoadUnitHandle(LX_Hash, h, 0)
    local player owner = LoadPlayerHandle(LX_Hash, h, 1)
    local real x = LoadReal(LX_Hash, h, 2)
    local real y = LoadReal(LX_Hash, h, 3)
    local real dx = LoadReal(LX_Hash, h, 4)
    local real dy = LoadReal(LX_Hash, h, 5)
    local real length = LoadReal(LX_Hash, h, 8)
    local group g = CreateGroup()
    local unit u
    // One broad phase per cast; geometry below is the exact finite beam.
    call GroupEnumUnitsInRange(g, x + dx * length * 0.5, y + dy * length * 0.5, length * 0.5 + LX_HALF_WIDTH, null)
    loop
        set u = FirstOfGroup(g)
        exitwhen u == null
        call GroupRemoveUnit(g, u)
        if LX_Enemy(u, owner) and LX_InBeam(GetUnitX(u), GetUnitY(u), x, y, dx, dy, length) then
            call UnitDamageTarget(caster, u, LoadReal(LX_Hash, h, 7), false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    set u = null
    set caster = null
    set owner = null
endfunction

function LX_Tick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit caster = LoadUnitHandle(LX_Hash, h, 0)
    local real age = LoadReal(LX_Hash, h, 6) + LX_TICK
    local boolean fired = LoadBoolean(LX_Hash, h, 9)
    local sound s
    // Death, removal, or ownership transfer before firing cancels safely.
    if not fired and (GetUnitTypeId(caster) == 0 or GetWidgetLife(caster) <= 0.405 or GetOwningPlayer(caster) != LoadPlayerHandle(LX_Hash, h, 1)) then
        call LX_Cleanup(t)
    elseif age >= 1.4375 then
        call LX_Cleanup(t)
    else
        call SaveReal(LX_Hash, h, 6, age)
        if age >= LX_CHARGE and not fired then
            // Mark first, before damage can dispatch other map triggers.
            call SaveBoolean(LX_Hash, h, 9, true)
            call LX_Release(h)
            set s = LoadSoundHandle(LX_Hash, h, 11)
            call StopSound(s, true, true)
            call RemoveSavedHandle(LX_Hash, h, 11)
            set s = LX_Sound("Spells\\Lux\\FinalSparkBlast.wav", LoadReal(LX_Hash, h, 2), LoadReal(LX_Hash, h, 3), LX_Z(LoadReal(LX_Hash, h, 2), LoadReal(LX_Hash, h, 3)) + 85.0, 115)
            call KillSoundWhenDone(s)
            call LX_Damage(h)
        endif
        call LX_Visual(h, age)
    endif
    set s = null
    set caster = null
    set t = null
endfunction

function LX_Cast takes nothing returns nothing
    local unit caster = GetTriggerUnit()
    local integer rank = GetUnitAbilityLevel(caster, LX_ABILITY)
    local timer t
    local integer h
    local real x
    local real y
    local real angle
    local real dx
    local real dy
    local real length = LX_RANGE
    local real step
    local real sx
    local real sy
    local real ex
    local real ey
    local real z1
    local real z2
    local integer i = 0
    local integer j
    local effect fx
    local sound s
    local fogmodifier vision
    if GetSpellAbilityId() != LX_ABILITY or rank <= 0 or IsUnitIllusion(caster) or GetWidgetLife(caster) <= 0.405 or LoadTimerHandle(LX_Casters, GetHandleId(caster), 0) != null then
        set caster = null
        return
    endif
    set x = GetUnitX(caster)
    set y = GetUnitY(caster)
    if (GetSpellTargetX() - x) * (GetSpellTargetX() - x) + (GetSpellTargetY() - y) * (GetSpellTargetY() - y) < 1.0 then
        set angle = GetUnitFacing(caster) * bj_DEGTORAD
    else
        set angle = Atan2(GetSpellTargetY() - y, GetSpellTargetX() - x)
    endif
    set dx = Cos(angle)
    set dy = Sin(angle)
    // Clip at playable edges so effects never sample outside map terrain.
    if dx > 0.0001 then
        set length = RMinBJ(length, (GetRectMaxX(bj_mapInitialPlayableArea) - x) / dx)
    elseif dx < -0.0001 then
        set length = RMinBJ(length, (GetRectMinX(bj_mapInitialPlayableArea) - x) / dx)
    endif
    if dy > 0.0001 then
        set length = RMinBJ(length, (GetRectMaxY(bj_mapInitialPlayableArea) - y) / dy)
    elseif dy < -0.0001 then
        set length = RMinBJ(length, (GetRectMinY(bj_mapInitialPlayableArea) - y) / dy)
    endif
    set length = RMaxBJ(1.0, length)
    set t = CreateTimer()
    set h = GetHandleId(t)
    call SaveTimerHandle(LX_Casters, GetHandleId(caster), 0, t)
    call SaveUnitHandle(LX_Hash, h, 0, caster)
    call SavePlayerHandle(LX_Hash, h, 1, GetOwningPlayer(caster))
    call SaveReal(LX_Hash, h, 2, x)
    call SaveReal(LX_Hash, h, 3, y)
    call SaveReal(LX_Hash, h, 4, dx)
    call SaveReal(LX_Hash, h, 5, dy)
    call SaveReal(LX_Hash, h, 6, 0.0)
    call SaveReal(LX_Hash, h, 7, 150.0 + 250.0 * I2R(rank) + I2R(GetHeroInt(caster, true)))
    call SaveReal(LX_Hash, h, 8, length)
    call SaveBoolean(LX_Hash, h, 9, false)
    call SaveBoolean(LX_Hash, h, 10, true)
    call SetUnitFacing(caster, angle * bj_RADTODEG)
    call SetUnitAnimation(caster, "spell")
    call BlzPauseUnitEx(caster, true)
    set step = length / I2R(LX_SEGMENTS)
    loop
        exitwhen i >= LX_SEGMENTS
        set sx = x + dx * step * I2R(i)
        set sy = y + dy * step * I2R(i)
        set ex = sx + dx * step
        set ey = sy + dy * step
        set z1 = LX_Z(sx, sy) + 85.0
        set z2 = LX_Z(ex, ey) + 85.0
        set vision = CreateFogModifierRadius(GetOwningPlayer(caster), FOG_OF_WAR_VISIBLE, (sx + ex) * 0.5, (sy + ey) * 0.5, step * 0.65 + LX_HALF_WIDTH, true, false)
        call FogModifierStart(vision)
        call SaveFogModifierHandle(LX_Hash, h, 400 + i, vision)
        call SaveReal(LX_Hash, h, 300 + i, -Atan2(z2 - z1, step))
        set j = 0
        loop
            exitwhen j >= 5
            set fx = AddSpecialEffect("Spells\\Lux\\FinalSparkBeam.mdx", (sx + ex) * 0.5, (sy + ey) * 0.5)
            call BlzSetSpecialEffectZ(fx, (z1 + z2) * 0.5)
            if j == 3 then
                call BlzSetSpecialEffectPosition(fx, (sx + ex) * 0.5 - dy * LX_HALF_WIDTH, (sy + ey) * 0.5 + dx * LX_HALF_WIDTH, (z1 + z2) * 0.5)
            elseif j == 4 then
                call BlzSetSpecialEffectPosition(fx, (sx + ex) * 0.5 + dy * LX_HALF_WIDTH, (sy + ey) * 0.5 - dx * LX_HALF_WIDTH, (z1 + z2) * 0.5)
            endif
            call SaveEffectHandle(LX_Hash, h, 100 + i * 5 + j, fx)
            set j = j + 1
        endloop
        set i = i + 1
    endloop
    set fx = AddSpecialEffect("Spells\\Lux\\FinalSparkFlare.mdx", x + dx * 35.0, y + dy * 35.0)
    call BlzSetSpecialEffectZ(fx, LX_Z(x, y) + 95.0)
    call BlzSetSpecialEffectColor(fx, 255, 220, 110)
    call SaveEffectHandle(LX_Hash, h, 200, fx)
    call LX_Visual(h, 0.0)
    set s = LX_Sound("Spells\\Lux\\FinalSparkCharge.wav", x, y, LX_Z(x, y) + 85.0, 85)
    call SaveSoundHandle(LX_Hash, h, 11, s)
    call TimerStart(t, LX_TICK, true, function LX_Tick)
    set fx = null
    set s = null
    set t = null
    set caster = null
    set vision = null
endfunction

function LX_TestAllowed takes nothing returns boolean
    local integer i = 0
    local integer humans = 0
    loop
        exitwhen i >= 12
        if GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING and GetPlayerController(Player(i)) == MAP_CONTROL_USER then
            set humans = humans + 1
        endif
        set i = i + 1
    endloop
    return udg_mode_debugmode or humans == 1
endfunction

function LX_Summon takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer id = GetPlayerId(p)
    local unit u = LX_Hero[id]
    local integer rank = 1
    local string command = GetEventPlayerChatString()
    if not LX_TestAllowed() then
        call DisplayTimedTextToPlayer(p, 0.0, 0.0, 10.0, "Final Spark testing: use -lux in Debug mode or a solo game.")
    else
        if command == "-lux2" then
            set rank = 2
        elseif command == "-lux3" then
            set rank = 3
        endif
        if GetUnitTypeId(u) == 0 then
            set u = CreateUnit(p, 'HLx1', GetStartLocationX(GetPlayerStartLocation(p)), GetStartLocationY(GetPlayerStartLocation(p)), 270.0)
            set LX_Hero[id] = u
            // Track as a test extra: never overwrite the player's drafted hero.
            call GroupAddUnit(FF_TestRecruited, u)
            call SetHeroLevel(u, 6, false)
        elseif GetWidgetLife(u) <= 0.405 then
            call ReviveHero(u, GetStartLocationX(GetPlayerStartLocation(p)), GetStartLocationY(GetPlayerStartLocation(p)), true)
        endif
        if LoadTimerHandle(LX_Casters, GetHandleId(u), 0) == null then
            call SetUnitAbilityLevel(u, LX_ABILITY, rank)
            call BlzEndUnitAbilityCooldown(u, LX_ABILITY)
            call SetUnitState(u, UNIT_STATE_MANA, GetUnitState(u, UNIT_STATE_MAX_MANA))
        endif
        call SelectUnitForPlayerSingle(u, p)
        call DisplayTimedTextToPlayer(p, 0.0, 0.0, 14.0, "Lux test caster: V / Final Spark. Aim at a point; the beam always fires its full range. -lux / -lux2 / -lux3 select rank and refresh mana/cooldown.")
    endif
    set p = null
    set u = null
endfunction

function LX_Init takes nothing returns nothing
    local trigger cast = CreateTrigger()
    local trigger chat = CreateTrigger()
    local integer i = 0
    set LX_Hash = InitHashtable()
    set LX_Casters = InitHashtable()
    call TriggerRegisterAnyUnitEventBJ(cast, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddAction(cast, function LX_Cast)
    loop
        exitwhen i >= 12
        call TriggerRegisterPlayerChatEvent(chat, Player(i), "-lux", true)
        call TriggerRegisterPlayerChatEvent(chat, Player(i), "-lux2", true)
        call TriggerRegisterPlayerChatEvent(chat, Player(i), "-lux3", true)
        set i = i + 1
    endloop
    call TriggerAddAction(chat, function LX_Summon)
    set cast = null
    set chat = null
endfunction
