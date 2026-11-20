function FF_LearnTip_AVge takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'AVge')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('AVge', "Learn Event Horizon [E] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVge', "Requires hero level 1|nCreate a cage for 3s. Enemies that touch its edge are stunned for 1.5s.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('AVge', "Learn Event Horizon [E] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVge', "Requires hero level 4|nCreate a cage for 3s. Enemies that touch its edge are stunned for 1.75s.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('AVge', "Learn Event Horizon [E] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVge', "Requires hero level 7|nCreate a cage for 3s. Enemies that touch its edge are stunned for 2s.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('AVge', "Learn Event Horizon [E] - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVge', "Requires hero level 10|nCreate a cage for 3s. Enemies that touch its edge are stunned for 2.25s.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('AVge', "Learn Event Horizon [E] - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVge', "Requires hero level 13|nCreate a cage for 3s. Enemies that touch its edge are stunned for 2.5s.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('AVge', "Learn Event Horizon [E] - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVge', "Requires hero level 16|nCreate a cage for 3s. Enemies that touch its edge are stunned for 2.75s.", 0)
    endif
endfunction

function FF_LearnTip_AVgw takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'AVgw')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('AVgw', "Learn Dark Matter [W] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgw', "Requires hero level 1|nAfter 1.25s, a meteor deals |cffff8979190|r damage plus your Intelligence. Enemies at the center take |cffff897950%|r more.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('AVgw', "Learn Dark Matter [W] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgw', "Requires hero level 4|nAfter 1.25s, a meteor deals |cffff8979280|r damage plus your Intelligence. Enemies at the center take |cffff897950%|r more.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('AVgw', "Learn Dark Matter [W] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgw', "Requires hero level 7|nAfter 1.25s, a meteor deals |cffff8979370|r damage plus your Intelligence. Enemies at the center take |cffff897950%|r more.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('AVgw', "Learn Dark Matter [W] - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgw', "Requires hero level 10|nAfter 1.25s, a meteor deals |cffff8979460|r damage plus your Intelligence. Enemies at the center take |cffff897950%|r more.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('AVgw', "Learn Dark Matter [W] - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgw', "Requires hero level 13|nAfter 1.25s, a meteor deals |cffff8979550|r damage plus your Intelligence. Enemies at the center take |cffff897950%|r more.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('AVgw', "Learn Dark Matter [W] - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgw', "Requires hero level 16|nAfter 1.25s, a meteor deals |cffff8979640|r damage plus your Intelligence. Enemies at the center take |cffff897950%|r more.", 0)
    endif
endfunction

function FF_LearnTip_AVgq takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'AVgq')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('AVgq', "Learn Baleful Strike [Q] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgq', "Requires hero level 1|nDeals |cffff8979150 + 60% Intelligence + permanent stacks|r as damage. Every enemy unit killed by Veigar grants |cffff8979+1|r permanent Z damage; enemy heroes grant |cffff8979+5|r instead. Stacks survive death and do not reset. The live bonus appears on this ability.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('AVgq', "Learn Baleful Strike [Q] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgq', "Requires hero level 4|nDeals |cffff8979220 + 60% Intelligence + permanent stacks|r as damage. Every enemy unit killed by Veigar grants |cffff8979+1|r permanent Z damage; enemy heroes grant |cffff8979+5|r instead. Stacks survive death and do not reset. The live bonus appears on this ability.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('AVgq', "Learn Baleful Strike [Q] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgq', "Requires hero level 7|nDeals |cffff8979290 + 60% Intelligence + permanent stacks|r as damage. Every enemy unit killed by Veigar grants |cffff8979+1|r permanent Z damage; enemy heroes grant |cffff8979+5|r instead. Stacks survive death and do not reset. The live bonus appears on this ability.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('AVgq', "Learn Baleful Strike [Q] - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgq', "Requires hero level 10|nDeals |cffff8979360 + 60% Intelligence + permanent stacks|r as damage. Every enemy unit killed by Veigar grants |cffff8979+1|r permanent Z damage; enemy heroes grant |cffff8979+5|r instead. Stacks survive death and do not reset. The live bonus appears on this ability.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('AVgq', "Learn Baleful Strike [Q] - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgq', "Requires hero level 13|nDeals |cffff8979430 + 60% Intelligence + permanent stacks|r as damage. Every enemy unit killed by Veigar grants |cffff8979+1|r permanent Z damage; enemy heroes grant |cffff8979+5|r instead. Stacks survive death and do not reset. The live bonus appears on this ability.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('AVgq', "Learn Baleful Strike [Q] - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgq', "Requires hero level 16|nDeals |cffff8979500 + 60% Intelligence + permanent stacks|r as damage. Every enemy unit killed by Veigar grants |cffff8979+1|r permanent Z damage; enemy heroes grant |cffff8979+5|r instead. Stacks survive death and do not reset. The live bonus appears on this ability.", 0)
    endif
endfunction

function FF_LearnTip_AVgr takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'AVgr')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('AVgr', "Learn Primordial Burst [R] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgr', "Requires hero level 6|nBlasts an enemy hero for |cffff8979550 + 1.2 x your Intelligence + 0.8 x target Intelligence|r damage. Baleful Strike kills permanently strengthen this spell.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('AVgr', "Learn Primordial Burst [R] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgr', "Requires hero level 11|nBlasts an enemy hero for |cffff8979850 + 1.2 x your Intelligence + 0.8 x target Intelligence|r damage. Baleful Strike kills permanently strengthen this spell.", 0)
    elseif rank >= 2 then
        call BlzSetAbilityResearchTooltip('AVgr', "Learn Primordial Burst [R] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('AVgr', "Requires hero level 16|nBlasts an enemy hero for |cffff89791150 + 1.2 x your Intelligence + 0.8 x target Intelligence|r damage. Baleful Strike kills permanently strengthen this spell.", 0)
    endif
endfunction

function VG_Z takes real x, real y returns real
    local location l = Location(x, y)
    local real z = GetLocationZ(l)
    call RemoveLocation(l)
    set l = null
    return z
endfunction

function VG_BuildWalls takes integer h, real x, real y returns nothing
    local integer n = 0
    local real a
    local real b
    local real ax
    local real ay
    local real bx
    local real by
    local real yaw
    local real mx
    local real my
    // Guard's diagonal wall mesh: projected span 472.57431; pentagon edge 352.67115.
    local real scale = 0.7462766
    local effect wall
    local lightning beam
    local real za
    local real zb
    loop
        exitwhen n >= 5
        set a = bj_PI * 0.5 + 2.0 * bj_PI * I2R(n) / 5.0
        set b = bj_PI * 0.5 + 2.0 * bj_PI * I2R(n + 1) / 5.0
        set ax = x + 300.0 * Cos(a)
        set ay = y + 300.0 * Sin(a)
        set bx = x + 300.0 * Cos(b)
        set by = y + 300.0 * Sin(b)
        set yaw = Atan2(by - ay, bx - ax)
        // Center the asymmetric mesh on the collision edge.
        set mx = (ax + bx) * 0.5 - scale * (7.275773 * Cos(yaw) - 3.018424 * Sin(yaw))
        set my = (ay + by) * 0.5 - scale * (7.275773 * Sin(yaw) + 3.018424 * Cos(yaw))
        set wall = AddSpecialEffect("Doodads\\LordaeronSummer\\Terrain\\StoneWall45\\StoneWall452.mdl", mx, my)
        call BlzSetSpecialEffectScale(wall, scale)
        call BlzSetSpecialEffectYaw(wall, yaw - bj_PI * 0.25)
        call BlzSetSpecialEffectZ(wall, VG_Z((ax + bx) * 0.5, (ay + by) * 0.5))
        call BlzSetSpecialEffectColor(wall, 130, 55, 255)
        call BlzSetSpecialEffectAlpha(wall, 72)
        call SaveEffectHandle(VG_Hash, h, 200 + n, wall)
        set za = VG_Z(ax, ay)
        set zb = VG_Z(bx, by)
        call SaveReal(VG_Hash, h, 300 + n, za)
        call SaveReal(VG_Hash, h, 310 + n, zb)
        set beam = AddLightningEx("DRAL", true, ax, ay, za + 8.0, bx, by, zb + 8.0)
        call SetLightningColor(beam, 0.55, 0.12, 1.0, 0.8)
        call SaveLightningHandle(VG_Hash, h, 100 + n, beam)
        set beam = AddLightningEx("DRAL", true, ax, ay, za + 170.0, bx, by, zb + 170.0)
        call SetLightningColor(beam, 0.7, 0.3, 1.0, 0.85)
        call SaveLightningHandle(VG_Hash, h, 105 + n, beam)
        set beam = AddLightningEx("DRAL", true, ax, ay, za + 8.0, ax, ay, za + 195.0)
        call SetLightningColor(beam, 0.85, 0.55, 1.0, 0.95)
        call SaveLightningHandle(VG_Hash, h, 110 + n, beam)
        set n = n + 1
    endloop
    set wall = null
    set beam = null
endfunction

function VG_PointSegment2 takes real px, real py, real ax, real ay, real bx, real by returns real
    local real dx = bx - ax
    local real dy = by - ay
    local real len = dx * dx + dy * dy
    local real f = 0.0
    if len > 0.0001 then
        set f = RMaxBJ(0.0, RMinBJ(1.0, ((px - ax) * dx + (py - ay) * dy) / len))
    endif
    set dx = px - ax - f * dx
    set dy = py - ay - f * dy
    return dx * dx + dy * dy
endfunction

function VG_EdgeContact takes real ax, real ay, real bx, real by, real cx, real cy, real dx, real dy returns boolean
    local real rx = bx - ax
    local real ry = by - ay
    local real sx = dx - cx
    local real sy = dy - cy
    local real det = rx * sy - ry * sx
    local real t
    local real u
    if RAbsBJ(det) > 0.0001 then
        set t = ((cx - ax) * sy - (cy - ay) * sx) / det
        set u = ((cx - ax) * ry - (cy - ay) * rx) / det
        if t >= 0.0 and t <= 1.0 and u >= 0.0 and u <= 1.0 then
            return true
        endif
    endif
    return VG_PointSegment2(ax, ay, cx, cy, dx, dy) <= 1764.0 or VG_PointSegment2(bx, by, cx, cy, dx, dy) <= 1764.0 or VG_PointSegment2(cx, cy, ax, ay, bx, by) <= 1764.0 or VG_PointSegment2(dx, dy, ax, ay, bx, by) <= 1764.0
endfunction

function VG_Crosses takes real ax, real ay, real bx, real by returns boolean
    local integer n = 0
    local real a
    local real b
    loop
        exitwhen n >= 5
        set a = bj_PI * 0.5 + 2.0 * bj_PI * I2R(n) / 5.0
        set b = bj_PI * 0.5 + 2.0 * bj_PI * I2R(n + 1) / 5.0
        if VG_EdgeContact(ax, ay, bx, by, 300.0 * Cos(a), 300.0 * Sin(a), 300.0 * Cos(b), 300.0 * Sin(b)) then
            return true
        endif
        set n = n + 1
    endloop
    return false
endfunction

function VG_Enemy takes unit u, player p returns boolean
    return GetUnitTypeId(u) != 0 and GetWidgetLife(u) > 0.405 and IsUnitEnemy(u, p) and not IsUnitType(u, UNIT_TYPE_STRUCTURE) and not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) and GetUnitAbilityLevel(u, 'Aloc') == 0
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
    call GroupEnumUnitsInRange(g, x, y, 520.0, null)
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
            if HaveSavedReal(VG_PrevX, h, id) and LoadReal(VG_Hash, h, 3) - LoadReal(VG_Hash, h, -id) <= 0.04 then
                set px = LoadReal(VG_PrevX, h, id)
                set py = LoadReal(VG_PrevY, h, id)
            endif
            if VG_Crosses(px, py, ux, uy) then
                set dummy = CreateUnit(owner, 'hgr1', GetUnitX(u), GetUnitY(u), 0.0)
                call UnitAddAbility(dummy, 'AVgs')
                call SetUnitAbilityLevel(dummy, 'AVgs', LoadInteger(VG_Hash, h, 11))
                if IssueTargetOrder(dummy, "thunderbolt", u) then
                    call GroupAddUnit(hit, u)

                endif
                call UnitApplyTimedLife(dummy, 'BTLF', 1.0)
            endif
            call SaveReal(VG_Hash, h, -id, LoadReal(VG_Hash, h, 3))
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

function VG_AnimateWalls takes integer h, real age returns nothing
    local integer n = 0
    local real fade = RMinBJ(1.0, (3.0 - age) / 0.25)
    local real pulse = 0.85 + 0.15 * Sin(age * 5.0)
    local real x = LoadReal(VG_Hash, h, 1)
    local real y = LoadReal(VG_Hash, h, 2)
    local real a
    local real b
    local real ax
    local real ay
    local real bx
    local real by
    local real za
    local real zb
    local real height = 170.0 + 5.0 * Sin(age * 5.0)
    local lightning beam
    loop
        exitwhen n >= 5
        set a = bj_PI * 0.5 + 2.0 * bj_PI * I2R(n) / 5.0
        set b = bj_PI * 0.5 + 2.0 * bj_PI * I2R(n + 1) / 5.0
        set ax = x + 300.0 * Cos(a)
        set ay = y + 300.0 * Sin(a)
        set bx = x + 300.0 * Cos(b)
        set by = y + 300.0 * Sin(b)
        set za = LoadReal(VG_Hash, h, 300 + n)
        set zb = LoadReal(VG_Hash, h, 310 + n)
        call BlzSetSpecialEffectAlpha(LoadEffectHandle(VG_Hash, h, 200 + n), R2I((65.0 + 15.0 * pulse) * fade))
        call SetLightningColor(LoadLightningHandle(VG_Hash, h, 100 + n), 0.55, 0.12, 1.0, 0.8 * pulse * fade)
        set beam = LoadLightningHandle(VG_Hash, h, 105 + n)
        call MoveLightningEx(beam, true, ax, ay, za + height, bx, by, zb + height)
        call SetLightningColor(beam, 0.7, 0.3, 1.0, 0.85 * pulse * fade)
        set beam = LoadLightningHandle(VG_Hash, h, 110 + n)
        call MoveLightningEx(beam, true, ax, ay, za + 8.0, ax, ay, za + height + 25.0)
        call SetLightningColor(beam, 0.85, 0.55, 1.0, 0.95 * pulse * fade)
        set n = n + 1
    endloop
    set beam = null
endfunction

function VG_Cleanup takes timer t returns nothing
    local integer h = GetHandleId(t)
    local integer n = 0
    loop
        exitwhen n >= 40
        call DestroyLightning(LoadLightningHandle(VG_Hash, h, 100 + n))
        set n = n + 1
    endloop
    set n = 0
    loop
        exitwhen n >= 5
        call BlzSetSpecialEffectAlpha(LoadEffectHandle(VG_Hash, h, 200 + n), 0)
        call BlzSetSpecialEffectZ(LoadEffectHandle(VG_Hash, h, 200 + n), -10000.0)
        call DestroyEffect(LoadEffectHandle(VG_Hash, h, 200 + n))
        set n = n + 1
    endloop
    if LoadEffectHandle(VG_Hash, h, 7) != null then
        call BlzSetSpecialEffectZ(LoadEffectHandle(VG_Hash, h, 7), -10000.0)
        call DestroyEffect(LoadEffectHandle(VG_Hash, h, 7))
    endif
    call DestroyGroup(LoadGroupHandle(VG_Hash, h, 5))
    call DestroyGroup(LoadGroupHandle(VG_Hash, h, 6))
    call FlushChildHashtable(VG_Hash, h)
    call FlushChildHashtable(VG_PrevX, h)
    call FlushChildHashtable(VG_PrevY, h)
    call PauseTimer(t)
    call DestroyTimer(t)
endfunction

function VG_DarkImpact takes real x, real y returns effect
    local effect burst = AddSpecialEffect("Abilities\\Spells\\Orc\\WarStomp\\WarStompCaster.mdl", x, y)
    local effect wave = AddSpecialEffect("Spells\\Orianna\\Feedback\\ShockwaveRing.mdx", x, y)
    local sound hit = CreateSound("Spells\\Orianna\\Feedback\\Shockwave.wav", false, true, true, 0, 0, "SpellsEAX")
    local effect flash = AddSpecialEffect("BlinkTargetPurple.mdx", x, y)
    call BlzSetSpecialEffectZ(flash, VG_Z(x,y) + 12.0)
    call BlzSetSpecialEffectScale(flash, 2.0)
    call BlzPlaySpecialEffect(flash, ANIM_TYPE_BIRTH)
    call OM_KeepEffect(flash, 0.65)
    set flash = null
    call TerrainDeformCrater(x, y, 170.0, 54.0, 700, false)
    call BlzSetSpecialEffectScale(burst, 1.65)
    call DestroyEffect(burst)
    call BlzSetSpecialEffectZ(wave, VG_Z(x,y) + 12.0)
    call BlzSetSpecialEffectColor(wave, 153, 111, 255)
    call BlzPlaySpecialEffect(wave, ANIM_TYPE_STAND)
    call SetSoundChannel(hit, 0)
    call SetSoundVolume(hit, 127)
    call SetSoundPitch(hit, 0.78)
    call SetSoundDistances(hit, 350.0, 2200.0)
    call SetSoundPosition(hit, x, y, VG_Z(x,y))
    call StartSound(hit)
    call KillSoundWhenDone(hit)
    set hit = null
    set burst = null
    return wave
endfunction

function VG_Tick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local real age = LoadReal(VG_Hash, h, 3) + 0.03125
    local real x = LoadReal(VG_Hash, h, 1)
    local real y = LoadReal(VG_Hash, h, 2)
    local unit caster = LoadUnitHandle(VG_Hash, h, 0)
    local player owner = LoadPlayerHandle(VG_Hash, h, 9)
    local real radius
    local real distance
    local group hit = LoadGroupHandle(VG_Hash, h, 5)
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
            call VG_AnimateWalls(h, age)
            call VG_CageScan(h)
        endif
    else
        if age >= 0.45 and age < 1.25 then
            set fx = LoadEffectHandle(VG_Hash, h, 7)
            if fx == null then
                set fx = AddSpecialEffect("war3mapImported\\ShadowOrbMissile v1.2.mdx", x, y)
                call BlzSetSpecialEffectScale(fx, 2.4)
                call BlzSetSpecialEffectColor(fx, 159, 108, 255)
                call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
                call SaveEffectHandle(VG_Hash, h, 7, fx)
            endif
            // Accelerating descent; the original 1.25-second damage timing is unchanged.
            call BlzSetSpecialEffectZ(fx, VG_Z(x, y) + 35.0 + RMaxBJ(0.0, 1000.0 * (1.0 - ((age - 0.45) / 0.8) * ((age - 0.45) / 0.8))))
            call BlzSetSpecialEffectYaw(fx, age * 3.0)
        endif
        if age >= 1.25 then
            if age == 1.25 then
                set fx = LoadEffectHandle(VG_Hash, h, 7)
                call BlzSetSpecialEffectZ(fx, -10000.0)
                call DestroyEffect(fx)
                call SaveEffectHandle(VG_Hash, h, 7, VG_DarkImpact(x, y))
            endif
            set radius = RMinBJ(225.0, 65.0 + (age - 1.25)*640.0)
            call BlzSetSpecialEffectScale(LoadEffectHandle(VG_Hash,h,7), radius)
            set g = LoadGroupHandle(VG_Hash, h, 6)
            call GroupEnumUnitsInRange(g, x, y, radius, null)
            loop
                set u = FirstOfGroup(g)
                exitwhen u == null
                call GroupRemoveUnit(g, u)
                if VG_Enemy(u, owner) and not IsUnitInGroup(u, hit) then
                    call GroupAddUnit(hit, u)
                    set distance = SquareRoot((GetUnitX(u)-x)*(GetUnitX(u)-x) + (GetUnitY(u)-y)*(GetUnitY(u)-y))
                    call UnitDamageTarget(caster, u, LoadReal(VG_Hash, h, 10) * (1.0 + 0.5*RMaxBJ(0.0, 1.0-distance/225.0)), false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
                endif
            endloop
            if radius >= 225.0 then
                call VG_Cleanup(t)
            endif
        endif
    endif
    set fx = null
    set u = null
    set hit = null
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
    call SaveReal(VG_Hash, h, 10, 100.0 + 90.0 * GetUnitAbilityLevel(GetTriggerUnit(), 'AVgw') + GetHeroInt(GetTriggerUnit(), true))
    call SaveInteger(VG_Hash, h, 11, GetUnitAbilityLevel(GetTriggerUnit(), 'AVge'))
    call SaveGroupHandle(VG_Hash, h, 5, CreateGroup())
    call SaveGroupHandle(VG_Hash, h, 6, CreateGroup())
    if spell == 'AVge' then
        call SaveInteger(VG_Hash, h, 4, 1)
        call VG_BuildWalls(h, x, y)
        call VG_CageScan(h)
    else
    loop
        exitwhen n >= 40
        set a = 2.0 * bj_PI * n / 40.0
        set b = 2.0 * bj_PI * (n + 1) / 40.0
        set rim = AddLightningEx("DRAL", true, x + radius * Cos(a), y + radius * Sin(a), VG_Z(x + radius * Cos(a), y + radius * Sin(a)) + z, x + radius * Cos(b), y + radius * Sin(b), VG_Z(x + radius * Cos(b), y + radius * Sin(b)) + z)
        call SetLightningColor(rim, 0.65, 0.15, 1.0, 0.9)
        call SaveLightningHandle(VG_Hash, h, 100 + n, rim)
        set n = n + 1
    endloop
    endif
    call TimerStart(t, 0.03125, true, function VG_Tick)
    set rim = null
    set t = null
endfunction

function VG_ImpactCleanup takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local effect fx = LoadEffectHandle(VG_Hash, h, 20)
    call BlzSetSpecialEffectAlpha(fx, 0)
    call DestroyEffect(fx)
    call FlushChildHashtable(VG_Hash, h)
    call PauseTimer(t)
    call DestroyTimer(t)
    set fx = null
    set t = null
endfunction

function VG_PrimordialImpact takes real x, real y returns nothing
    local effect nova = AddSpecialEffect("war3mapImported\\DarkNova.mdx", x, y)
    local sound hit = CreateSound("Spells\\Orianna\\Feedback\\Shockwave.wav", false, true, true, 0, 0, "SpellsEAX")
    call BlzSetSpecialEffectScale(nova, 2.6)
    call BlzSetSpecialEffectZ(nova, VG_Z(x,y) + 45.0)
    call BlzPlaySpecialEffect(nova, ANIM_TYPE_BIRTH)
    call OM_KeepEffect(nova, 1.1)
    call SetSoundChannel(hit, 0)
    call SetSoundVolume(hit, 127)
    call SetSoundPitch(hit, 0.63)
    call SetSoundDistances(hit, 550.0, 2400.0)
    call SetSoundPosition(hit, x, y, VG_Z(x,y))
    call StartSound(hit)
    call KillSoundWhenDone(hit)
    set nova = null
    set hit = null
endfunction

function VG_BoltTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local effect fx = LoadEffectHandle(VG_Hash, h, 20)
    local unit target = LoadUnitHandle(VG_Hash, h, 21)
    local real x = LoadReal(VG_Hash, h, 22)
    local real y = LoadReal(VG_Hash, h, 23)
    local real dx = GetUnitX(target)-x
    local real dy = GetUnitY(target)-y
    local real dist = SquareRoot(dx*dx+dy*dy)
    local integer ticks = LoadInteger(VG_Hash, h, 24)+1
    if dist <= 27.0 or ticks >= 80 or GetUnitTypeId(target) == 0 then
        if LoadBoolean(VG_Hash, h, 25) and GetUnitTypeId(target) != 0 then
            call VG_PrimordialImpact(GetUnitX(target), GetUnitY(target))
        endif
        call VG_ImpactCleanup()
    else
        call BlzSetSpecialEffectYaw(fx, Atan2(dy,dx))
        set x = x+27.0*dx/dist
        set y = y+27.0*dy/dist
        call BlzSetSpecialEffectPosition(fx,x,y,VG_Z(x,y)+60.0+GetUnitFlyHeight(target))
        call SaveReal(VG_Hash,h,22,x)
        call SaveReal(VG_Hash,h,23,y)
        call SaveInteger(VG_Hash,h,24,ticks)
    endif
    set target=null
    set fx=null
    set t=null
endfunction

function VG81_OrbImpact takes unit caster, unit target, string model returns nothing
    local timer t=CreateTimer()
    local integer h=GetHandleId(t)
    local real x=GetUnitX(caster)
    local real y=GetUnitY(caster)
    local effect fx=AddSpecialEffect(model,x,y)
    if model == "war3mapImported\\ShadowOrbMissile v1.2.mdx" then
        call BlzSetSpecialEffectScale(fx, 3.1)
        call BlzSetSpecialEffectColor(fx, 195, 135, 255)
        call SaveBoolean(VG_Hash, h, 25, true)
    else
        call BlzSetSpecialEffectScale(fx, 1.7)
    endif
    call BlzSetSpecialEffectYaw(fx, Atan2(GetUnitY(target)-y, GetUnitX(target)-x))
    call BlzSetSpecialEffectZ(fx,VG_Z(x,y)+60.0)
    call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
    call SaveEffectHandle(VG_Hash,h,20,fx)
    call SaveUnitHandle(VG_Hash,h,21,target)
    call SaveReal(VG_Hash,h,22,x)
    call SaveReal(VG_Hash,h,23,y)
    call TimerStart(t,0.03125,true,function VG_BoltTick)
    set fx=null
    set t=null
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
            set damage = 80.0 + 70.0 * rank + 0.6 * GetHeroInt(caster, true) + I2R(LoadInteger(VG_Hash, GetHandleId(caster), 702))
            call VG81_OrbImpact(caster, target, "war3mapImported\\Void Arrow.mdx")
            call SaveUnitHandle(VG_Hash, GetHandleId(caster), 701, target)
            call UnitDamageTarget(caster, target, damage, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
            call RemoveSavedHandle(VG_Hash, GetHandleId(caster), 701)
        elseif IsUnitType(target, UNIT_TYPE_HERO) then
            set enemyInt = I2R(GetHeroInt(target, true))
            set damage = 250.0 + 300.0 * rank + 1.2 * GetHeroInt(caster, true) + 0.8 * enemyInt + I2R(LoadInteger(VG_Hash, GetHandleId(caster), 703))
            call VG81_OrbImpact(caster, target, "war3mapImported\\ShadowOrbMissile v1.2.mdx")
            call UnitDamageTarget(caster, target, damage, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
        endif
    endif
    set caster = null
    set target = null
endfunction

function VG82_UpdateCounter takes unit u returns nothing
    local ability a = BlzGetUnitAbility(u, 'AVgq')
    local integer stacks = LoadInteger(VG_Hash, GetHandleId(u), 702)
    local integer i = 0
    if a != null then
        loop
            exitwhen i >= 6
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL, i, "Baleful Strike [|cffffcc00Z|r] - |cff80dfff+" + I2S(stacks) + " damage|r")
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL_EXTENDED, i, "Deals " + I2S(150 + 70 * i) + " + 60% Intelligence + |cff80dfff" + I2S(stacks) + " permanent bonus|r magic damage.|n|nEvery enemy unit killed by Veigar grants +1 Z damage. Enemy heroes grant +5 instead. Attacks and all spells count. Illusions and structures do not count.|nStacks never reset, including on death.|n|nCurrent permanent bonus: |cff80dfff+" + I2S(stacks) + " damage|r")
            set i = i + 1
        endloop
    endif
    set a = BlzGetUnitAbility(u, 'AVgr')
    set stacks = LoadInteger(VG_Hash, GetHandleId(u), 703)
    set i = 0
    if a != null then
        loop
            exitwhen i >= 3
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL, i, "Primordial Burst [|cffffcc00V|r] - |cff80dfff+" + I2S(stacks) + " damage|r")
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL_EXTENDED, i, "Deals " + I2S(550 + 300 * i) + " + 120% Intelligence + 80% target Intelligence + |cff80dfff" + I2S(stacks) + " permanent bonus|r magic damage to an enemy hero.|n|nKills with Baleful Strike (Z) permanently grant +1 ultimate damage per enemy unit, or +5 per enemy hero. Other kill sources do not grant ultimate stacks. Illusions and structures do not count.|nStacks never reset, including on death.|n|nCurrent permanent bonus: |cff80dfff+" + I2S(stacks) + " damage|r")
            set i = i + 1
        endloop
    endif
    set a = null
endfunction

function VG_ClassicKill takes nothing returns nothing
    local unit u = GetKillingUnit()
    local unit victim = GetTriggerUnit()
    local integer gain = 1
    if GetUnitTypeId(u) == 'HVg1' and not IsUnitIllusion(u) and IsUnitEnemy(victim, GetOwningPlayer(u)) and not IsUnitIllusion(victim) and not IsUnitType(victim, UNIT_TYPE_STRUCTURE) then
        if IsUnitType(victim, UNIT_TYPE_HERO) then
            set gain = 5
        endif
        call SaveInteger(VG_Hash, GetHandleId(u), 702, LoadInteger(VG_Hash, GetHandleId(u), 702) + gain)
        if LoadUnitHandle(VG_Hash, GetHandleId(u), 701) == victim then
            call SaveInteger(VG_Hash, GetHandleId(u), 703, LoadInteger(VG_Hash, GetHandleId(u), 703) + gain)
        endif
        call VG82_UpdateCounter(u)
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
        if GetUnitTypeId(u) == 'HVg1' and not IsUnitIllusion(u) then
            call VG82_UpdateCounter(u)
        endif
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

function VG_Summon takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer id = GetPlayerId(p)
    local unit u = udg_herO[id + 1]
    if GetUnitTypeId(u) == 'HVg1' then
        call SelectUnitForPlayerSingle(u, p)
    elseif udg_mode_debugmode then
        set u = VG_Hero[id]
        if GetUnitTypeId(u) == 0 then
            set u = CreateUnit(p, 'HVg1', GetStartLocationX(GetPlayerStartLocation(p)), GetStartLocationY(GetPlayerStartLocation(p)), 270.0)
            set VG_Hero[id] = u
            call FF_TestExtraHero(u)
        elseif GetWidgetLife(u) <= 0.405 then
            call ReviveHero(u, GetStartLocationX(GetPlayerStartLocation(p)), GetStartLocationY(GetPlayerStartLocation(p)), true)
        endif
        call SelectUnitForPlayerSingle(u, p)
        call DisplayTimedTextToPlayer(p, 0.0, 0.0, 12.0, "Veigar: learn Q/W/E/R using hero skill points. Equilibrium is always active.")
    else
        call DisplayTimedTextToPlayer(p, 0.0, 0.0, 12.0, "Veigar is in the Hero Killer selection pool. In Debug, recruit him from All Heroes.")
    endif
    set p = null
    set u = null
endfunction

function VG_Init takes nothing returns nothing
    local trigger cast = CreateTrigger()
    local trigger chat = CreateTrigger()
    local trigger kills = CreateTrigger()
    local integer i = 0
    set VG_Hash = InitHashtable()
    set VG_PrevX = InitHashtable()
    set VG_PrevY = InitHashtable()
    call TriggerRegisterAnyUnitEventBJ(cast, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddAction(cast, function VG_Cast)
    call TriggerAddAction(cast, function VG_ClassicCast)
    call TriggerRegisterAnyUnitEventBJ(kills, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddAction(kills, function VG_ClassicKill)
    call TimerStart(CreateTimer(), 1.0, true, function VG_Equilibrium)
    set kills = null
    loop
        exitwhen i >= 12
        set i = i + 1
    endloop
    set cast = null
    set chat = null
endfunction

function VG_StunVisualTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit u = LoadUnitHandle(VG_Hash, h, 0)
    local real age = LoadReal(VG_Hash, h, 1) + 0.03125
    local boolean active = GetUnitAbilityLevel(u, 'BPSE') > 0
    local effect fx = LoadEffectHandle(VG_Hash, h, 2)
    local texttag label = LoadTextTagHandle(VG_Hash, h, 3)
    call SaveReal(VG_Hash, h, 1, age)
    if GetUnitTypeId(u) == 0 or GetWidgetLife(u) <= 0.405 or age >= 4.0 or (not active and (fx != null or age >= 0.25)) then
        if fx != null then
            call BlzSetSpecialEffectAlpha(fx, 0)
            call DestroyEffect(fx)
        endif
        if label != null then
            call DestroyTextTag(label)
        endif
        call FlushChildHashtable(VG_Hash, h)
        call PauseTimer(t)
        call DestroyTimer(t)
    elseif active then
        if fx == null then
            set fx = AddSpecialEffectTarget("Abilities\\Spells\\Human\\Thunderclap\\ThunderclapTarget.mdl", u, "overhead")
            call BlzSetSpecialEffectScale(fx, 1.8)
            call BlzSetSpecialEffectColor(fx, 210, 150, 255)
            call SaveEffectHandle(VG_Hash, h, 2, fx)
            set label = CreateTextTag()
            call SetTextTagText(label, "STUNNED", 0.022)
            call SetTextTagColor(label, 235, 185, 255, 255)
            call SetTextTagPermanent(label, false)
            call SetTextTagLifespan(label, 4.1)
            call SaveTextTagHandle(VG_Hash, h, 3, label)
        endif
        call SetTextTagPosUnit(label, u, 110.0)
    endif
    set label = null
    set fx = null
    set u = null
    set t = null
endfunction

function VG_StunFeedback takes unit u returns nothing
    local timer t = CreateTimer()
    call SaveUnitHandle(VG_Hash, GetHandleId(t), 0, u)
    call TimerStart(t, 0.03125, true, function VG_StunVisualTick)
    set t = null
endfunction
