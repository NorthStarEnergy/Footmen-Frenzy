"""Enchantress hand attachment and cast-animation alignment."""
import re

def patch(script):
    def body(name):
        return re.search(r'^function '+name+r' takes .*?^endfunction',script,re.M|re.S)[0]
    def edit(name,old,new):
        nonlocal script
        before=body(name);assert old in before,(name,old)
        script=script.replace(before,before.replace(old,new),1)
    edit('OM_UpdateBallVisual',body('OM_UpdateBallVisual'),r'''function OM_UpdateBallVisual takes integer i returns nothing
    local integer key = GetHandleId(OM_Ball[i])
    local effect fx = LoadEffectHandle(OM_Hash, key, -102)
    local boolean attached = OM_State[i] == 0 and OM_Carrier[i] == OM_Hero[i]
    local string model = "Spells\\Orianna\\Feedback\\EnchantressOrb.mdx"
    local real x = GetUnitX(OM_Ball[i])
    local real y = GetUnitY(OM_Ball[i])
    local real remaining = LoadReal(OM_Hash, key, -105) - OM_Now
    local real gesture = 0.0
    if not OM_Alive(OM_Hero[i]) or GetUnitTypeId(OM_Ball[i]) == 0 then
        call OM_ClearBallVisual(i)
        set fx = null
        return
    endif
    if fx != null and LoadBoolean(OM_Hash, key, -106) != attached then
        call OM_ClearBallVisual(i)
        set fx = null
    endif
    if LoadBoolean(OM_Hash, key, -103) then
        set model = "Spells\\Orianna\\Feedback\\EnchantressOrbBlue.mdx"
    endif
    if fx == null then
        if attached then
            set fx = AddSpecialEffectTarget(model, OM_Hero[i], "hand,right")
        else
            set fx = AddSpecialEffect(model, x, y)
        endif
        call BlzSetSpecialEffectAlpha(fx, 200)
        call BlzSetSpecialEffectTimeScale(fx, 1.0)
        call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
        call SaveEffectHandle(OM_Hash, key, -102, fx)
        call SaveBoolean(OM_Hash, key, -106, attached)
    endif
    if LoadBoolean(OM_Hash, key, -103) then
        call BlzSetSpecialEffectColor(fx, 65, 145, 255)
    else
        call BlzSetSpecialEffectColor(fx, 255, 255, 255)
    endif
    if remaining > 0.0 then
        set gesture = Sin((1.0 - remaining / 0.25) * 3.14159265)
    endif
    call BlzSetSpecialEffectScale(fx, 0.65 * (1.0 + 0.18 * gesture))
    if not attached then
        call MoveLocation(OM_VisualGround, x, y)
        call BlzSetSpecialEffectPosition(fx, x, y, GetLocationZ(OM_VisualGround) + GetUnitFlyHeight(OM_Ball[i]) + 20.0 * gesture)
    endif
    set fx = null
endfunction''')
    edit('OM_ClearBallVisual','    set fx = null','    call RemoveSavedBoolean(OM_Hash, key, -106)\n    set fx = null')
    edit('OM_BallLook','    call SaveBoolean(OM_Hash, key, -103, protect)', '''    if LoadBoolean(OM_Hash, key, -103) != protect then
        call OM_ClearBallVisual(i)
    endif
    call SaveBoolean(OM_Hash, key, -103, protect)''')
    edit('OM_EmitTrail',r'Spells\\Orianna\\Feedback\\SoftOrb.mdx',r'Spells\\Orianna\\Feedback\\EnchantressTrail.mdx')
    for name in ('OM_EmitTrail','OM_TrailTick'):
        edit(name,'0.32','0.22')
        edit(name,'75','50')
    edit('OM_WindupFX','    call OM_StopWindupFX(i)', '''    // Native channel cast transitions into the pack's Spell Attack sequence.
    // Its release gesture lands 0.5 seconds later, exactly at Shockwave impact.
    call SetUnitAnimationByIndex(OM_Hero[i], 1)
    call QueueUnitAnimation(OM_Hero[i], "stand")
    call OM_StopWindupFX(i)''')
    # Channel can prefer its channel sequence despite the ability animation tags.
    # Start the chosen model sequence explicitly before the 0.5-second cast point;
    # no delayed action survives an interrupted cast or launches the ball early.
    script=script.replace('function OM_Init takes nothing returns nothing', '''function OM_OnCastAnimation takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local integer a = GetSpellAbilityId()
    if GetUnitTypeId(u) == OM_HERO and OM_Alive(u) then
        if a == OM_ATTACK or a == OM_PULSE or a == OM_PROTECT then
            call SetUnitAnimationByIndex(u, 1)
        elseif a == OM_SHOCK then
            call SetUnitAnimationByIndex(u, 9)
        endif
    endif
    set u = null
endfunction

function OM_Init takes nothing returns nothing''',1)
    edit('OM_Init','    call FF_HeroTooltips_Init()', '''    call FF_HeroTooltips_Init()
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_CHANNEL)
    call TriggerAddAction(t, function OM_OnCastAnimation)''')
    return script
