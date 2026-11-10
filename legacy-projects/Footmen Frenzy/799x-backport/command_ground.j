// Cosmetic ground glyphs have independent lifetimes; gameplay rings stay intact.
function OM_CommandGroundTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer key = GetHandleId(t)
    local effect fx = LoadEffectHandle(OM_Hash, key, 0)
    local real elapsed = LoadReal(OM_Hash, key, 1) + OM_TICK
    local real duration = LoadReal(OM_Hash, key, 2)
    local real size = LoadReal(OM_Hash, key, 3)
    local integer kind = LoadInteger(OM_Hash, key, 4)
    local real fade = RMaxBJ(0.0, 1.0 - elapsed / duration)
    if kind == 2 then
        call BlzSetSpecialEffectScale(fx, size * RMinBJ(1.0, elapsed / 0.25))
        set fade = RMinBJ(1.0, RMaxBJ(0.0, (duration - elapsed) / 0.125))
    elseif kind == 4 then
        call BlzSetSpecialEffectScale(fx, size * RMinBJ(1.0, elapsed / 0.18))
        set fade = RMinBJ(1.0, RMaxBJ(0.0, (duration - elapsed) / 0.45))
    elseif kind == 3 then
        call BlzSetSpecialEffectScale(fx, size * (0.94 + 0.06 * Sin(elapsed * 6.0)))
        set fade = RMinBJ(1.0, fade * 2.0)
    endif
    call BlzSetSpecialEffectAlpha(fx, R2I(180.0 * fade))
    if elapsed >= duration then
        call DestroyEffect(fx)
        call FlushChildHashtable(OM_Hash, key)
        call DestroyTimer(t)
    else
        call SaveReal(OM_Hash, key, 1, elapsed)
    endif
    set fx = null
    set t = null
endfunction

function OM_CommandGround takes integer kind, real x, real y, real size, real yaw returns nothing
    local string model = "Spells\\Orianna\\Feedback\\MoveGround.mdx"
    local real duration = 0.30
    local effect fx
    local timer t = CreateTimer()
    local integer key = GetHandleId(t)
    if kind == 2 then
        set model = "Spells\\Orianna\\Feedback\\AttackGround.mdx"
        set duration = 0.375
    elseif kind == 3 then
        set model = "Spells\\Orianna\\Feedback\\ProtectGround.mdx"
        set duration = 1.5
    elseif kind == 4 then
        set model = "Spells\\Orianna\\Feedback\\ShockImpact.mdx"
        set duration = 0.65
    endif
    set fx = AddSpecialEffect(model, x, y)
    call MoveLocation(OM_VisualGround, x, y)
    call BlzSetSpecialEffectZ(fx, GetLocationZ(OM_VisualGround) + 8.0)
    call BlzSetSpecialEffectYaw(fx, yaw)
    call BlzSetSpecialEffectAlpha(fx, 180)
    if kind == 2 or kind == 4 then
        call BlzSetSpecialEffectScale(fx, 0.01)
    else
        call BlzSetSpecialEffectScale(fx, size)
    endif
    call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
    call SaveEffectHandle(OM_Hash, key, 0, fx)
    call SaveReal(OM_Hash, key, 1, 0.0)
    call SaveReal(OM_Hash, key, 2, duration)
    call SaveReal(OM_Hash, key, 3, size)
    call SaveInteger(OM_Hash, key, 4, kind)
    call TimerStart(t, OM_TICK, true, function OM_CommandGroundTick)
    set fx = null
    set t = null
endfunction

function OM_UpdateShockGround takes integer i returns nothing
    local effect fx = LoadEffectHandle(OM_Hash, GetHandleId(OM_Ball[i]), -108)
    local real remaining = RMaxBJ(0.0, OM_ShockAt[i] - OM_Now)
    local real progress = RMinBJ(1.0, 1.0 - remaining / 0.5)
    if fx != null then
        call BlzSetSpecialEffectScale(fx, OM_ShockRadius[i] * (0.92 - 0.74 * progress))
        call BlzSetSpecialEffectYaw(fx, -2.5 * progress)
        call BlzSetSpecialEffectAlpha(fx, R2I(180.0 * (1.0 - 0.35 * progress)))
    endif
    set fx = null
endfunction
