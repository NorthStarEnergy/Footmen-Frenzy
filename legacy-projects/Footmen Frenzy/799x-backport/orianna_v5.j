// Stationary afterimages fade behind the moving orb, never attached to it.
function OM_TrailTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer key = GetHandleId(t)
    local effect fx = LoadEffectHandle(OM_Hash, key, 0)
    local real life = LoadReal(OM_Hash, key, 1) - OM_TICK
    call BlzSetSpecialEffectAlpha(fx, R2I(160.0 * RMaxBJ(0.0, life) / 0.25))
    call BlzSetSpecialEffectScale(fx, 0.7 * RMaxBJ(0.0, life) / 0.25)
    if life <= 0.0 then
        call BlzSetSpecialEffectPosition(fx, 0.0, 0.0, -10000.0)
        call DestroyEffect(fx)
        call FlushChildHashtable(OM_Hash, key)
        call DestroyTimer(t)
    else
        call SaveReal(OM_Hash, key, 1, life)
    endif
    set fx = null
    set t = null
endfunction

function OM_EmitTrail takes integer i returns nothing
    local real x = GetUnitX(OM_Ball[i])
    local real y = GetUnitY(OM_Ball[i])
    local effect fx = AddSpecialEffect("Abilities\\Weapons\\FarseerMissile\\FarseerMissile.mdl", x, y)
    local timer t = CreateTimer()
    call MoveLocation(OM_VisualGround, x, y)
    call BlzSetSpecialEffectZ(fx, GetLocationZ(OM_VisualGround) + GetUnitFlyHeight(OM_Ball[i]))
    call BlzSetSpecialEffectColor(fx, 65, 145, 255)
    call BlzSetSpecialEffectScale(fx, 0.7)
    call BlzSetSpecialEffectAlpha(fx, 160)
    call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
    call SaveEffectHandle(OM_Hash, GetHandleId(t), 0, fx)
    call SaveReal(OM_Hash, GetHandleId(t), 1, 0.25)
    call TimerStart(t, OM_TICK, true, function OM_TrailTick)
    set fx = null
    set t = null
endfunction

function OM_PulseTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer key = GetHandleId(t)
    local unit caster = LoadUnitHandle(OM_Hash, key, 1)
    local effect fx = LoadEffectHandle(OM_Hash, key, 0)
    local group hit = LoadGroupHandle(OM_Hash, key, 2)
    local group candidates = LoadGroupHandle(OM_Hash, key, 3)
    local real elapsed = LoadReal(OM_Hash, key, 4) + OM_TICK
    local real radius = LoadReal(OM_Hash, key, 5) * RMinBJ(1.0, elapsed / 0.25)
    local real x = LoadReal(OM_Hash, key, 6)
    local real y = LoadReal(OM_Hash, key, 7)
    local real damage = LoadReal(OM_Hash, key, 8)
    local unit u
    call BlzSetSpecialEffectScale(fx, radius)
    if elapsed <= 0.25 and GetUnitTypeId(caster) != 0 then
        call GroupEnumUnitsInRange(candidates, x, y, radius, null)
        loop
            set u = FirstOfGroup(candidates)
            exitwhen u == null
            call GroupRemoveUnit(candidates, u)
            if OM_Enemy(caster, u) and not IsUnitInGroup(u, hit) then
                call GroupAddUnit(hit, u)
                call OM_TravelImpact(u)
                call OM_Deal(caster, u, damage)
                call OM_Slow(caster, u)
            endif
        endloop
    elseif elapsed > 0.25 then
        call BlzSetSpecialEffectAlpha(fx, R2I(255.0 * RMaxBJ(0.0, (0.375 - elapsed) / 0.125)))
    endif
    if elapsed >= 0.375 or GetUnitTypeId(caster) == 0 then
        call BlzSetSpecialEffectAlpha(fx, 0)
        call DestroyEffect(fx)
        call DestroyGroup(hit)
        call DestroyGroup(candidates)
        call FlushChildHashtable(OM_Hash, key)
        call DestroyTimer(t)
    else
        call SaveReal(OM_Hash, key, 4, elapsed)
    endif
    set u = null
    set caster = null
    set fx = null
    set hit = null
    set candidates = null
    set t = null
endfunction

function OM_StartPulse takes integer i, integer level returns nothing
    local timer t = CreateTimer()
    local integer key = GetHandleId(t)
    local real x = GetUnitX(OM_Ball[i])
    local real y = GetUnitY(OM_Ball[i])
    local effect fx = AddSpecialEffect("Spells\\Orianna\\Feedback\\AttackRing.mdx", x, y)
    call MoveLocation(OM_VisualGround, x, y)
    call BlzSetSpecialEffectZ(fx, GetLocationZ(OM_VisualGround) + 12.0)
    call BlzSetSpecialEffectScale(fx, 0.01)
    call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
    call SaveEffectHandle(OM_Hash, key, 0, fx)
    call SaveUnitHandle(OM_Hash, key, 1, OM_Hero[i])
    call SaveGroupHandle(OM_Hash, key, 2, CreateGroup())
    call SaveGroupHandle(OM_Hash, key, 3, CreateGroup())
    call SaveReal(OM_Hash, key, 4, 0.0)
    call SaveReal(OM_Hash, key, 5, OM_AttackRadius(level))
    call SaveReal(OM_Hash, key, 6, x)
    call SaveReal(OM_Hash, key, 7, y)
    call SaveReal(OM_Hash, key, 8, OM_AttackDamage(level))
    call OM_CommandSound(OM_Ball[i], 2)
    call TimerStart(t, OM_TICK, true, function OM_PulseTick)
    set fx = null
    set t = null
endfunction
