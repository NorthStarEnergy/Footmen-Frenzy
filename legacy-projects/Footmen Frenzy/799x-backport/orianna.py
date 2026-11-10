"""799X Orianna presentation and registration patch; no balance changes."""
import re


def patch(script):
    original = script
    def body(name):
        return re.search(r'^function ' + name + r' takes .*?^endfunction', script, re.M | re.S)[0]
    def edit(name, old, new):
        nonlocal script
        before = body(name)
        assert old in before, (name, old)
        script = script.replace(before, before.replace(old, new), 1)
    # Make timed feedback available to healing functions as well as attack functions.
    helpers = []
    for name in ['OM_CommandSound', 'OM_FeedbackCleanup', 'OM_KeepEffect']:
        helper = body(name)
        helpers.append(helper)
        script = script.replace(helper, '', 1)
    script = script.replace('function OM_PullRemove takes', '\n\n'.join(helpers) + '\n\nfunction OM_PullRemove takes', 1)
    edit('OM_CommandSound', '    endif\n    set s = CreateSound', '''    elseif kind == 4 then
        set path = "Spells\\\\Orianna\\\\Feedback\\\\Protect.wav"
        set duration = 600
    elseif kind == 5 then
        set path = "Spells\\\\Orianna\\\\Feedback\\\\Heal.wav"
        set duration = 700
    elseif kind == 6 then
        set path = "Spells\\\\Orianna\\\\Feedback\\\\Arrival.wav"
        set duration = 300
    elseif kind == 7 then
        set path = "Spells\\\\Orianna\\\\Feedback\\\\Windup.wav"
        set duration = 500
    elseif kind == 8 then
        set path = "Spells\\\\Orianna\\\\Feedback\\\\Return.wav"
        set duration = 400
    endif
    set s = CreateSound''')
    new_helpers = r'''
// Windup belongs to the ball and must disappear if the cast is cancelled.
function OM_StopWindupFX takes integer i returns nothing
    local integer key = GetHandleId(OM_Ball[i])
    local effect fx = LoadEffectHandle(OM_Hash, key, -101)
    if fx != null then
        call DestroyEffect(fx)
        call RemoveSavedHandle(OM_Hash, key, -101)
    endif
    set fx = null
endfunction

function OM_WindupFX takes integer i returns nothing
    local location ground = Location(OM_X[i], OM_Y[i])
    local effect fx
    call OM_StopWindupFX(i)
    set fx = AddSpecialEffect("Spells\\Orianna\\Feedback\\ShockwaveRing.mdx", OM_X[i], OM_Y[i])
    call BlzSetSpecialEffectZ(fx, GetLocationZ(ground) + 12.0)
    call BlzSetSpecialEffectScale(fx, OM_ShockRadius[i])
    call BlzSetSpecialEffectAlpha(fx, 110)
    call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
    call SaveEffectHandle(OM_Hash, GetHandleId(OM_Ball[i]), -101, fx)
    call OM_CommandSound(OM_Ball[i], 7)
    call RemoveLocation(ground)
    set ground = null
    set fx = null
endfunction

function OM_ArrivalFX takes integer i, boolean protect returns nothing
    local effect fx
    local location ground
    if protect then
        set ground = Location(GetUnitX(OM_Ball[i]), GetUnitY(OM_Ball[i]))
        set fx = AddSpecialEffect("Spells\\Orianna\\Feedback\\ProtectRing.mdx", GetUnitX(OM_Ball[i]), GetUnitY(OM_Ball[i]))
        call BlzSetSpecialEffectZ(fx, GetLocationZ(ground) + 12.0)
        call BlzSetSpecialEffectScale(fx, OM_HASTE_RADIUS)
        call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
        call OM_KeepEffect(fx, 1.5)
        call OM_CommandSound(OM_Ball[i], 5)
        call RemoveLocation(ground)
    else
        set fx = AddSpecialEffectTarget("Abilities\\Spells\\Human\\DispelMagic\\DispelMagicTarget.mdl", OM_Ball[i], "origin")
        call OM_KeepEffect(fx, 0.45)
        call OM_CommandSound(OM_Ball[i], 6)
    endif
    set fx = null
    set ground = null
endfunction

'''
    script = script.replace('function OM_PullRemove takes', new_helpers + 'function OM_PullRemove takes', 1)
    edit('OM_ProtectArrival', '    local unit u', '    local unit u\n    local effect fx')
    edit('OM_ProtectArrival', '            if u == carrier then', r'''            set fx = AddSpecialEffectTarget("Abilities\\Spells\\Human\\Heal\\HealTarget.mdl", u, "origin")
            call OM_KeepEffect(fx, 1.0)
            if u == carrier then''')
    edit('OM_ProtectArrival', '    set u = null', '    set u = null\n    set fx = null')
    edit('OM_LockBall', '    call SetUnitTimeScale(ball, 1.0)', '''    call SetUnitTimeScale(ball, 1.0)
    call SetUnitVertexColor(ball, 255, 255, 255, 255)
    call SetUnitScale(ball, 1.90, 1.90, 1.90)''')
    edit('OM_StartTravelFX', '    call OM_CommandSound(OM_Ball[i], 1)', '''    if protect then
        call OM_CommandSound(OM_Ball[i], 4)
    else
        call OM_CommandSound(OM_Ball[i], 1)
    endif''')
    edit('OM_Home', '    call OM_StopTravelFX(i)', '''    local boolean returning = OM_State[i] != 0 or OM_Carrier[i] != OM_Hero[i]
    call OM_StopTravelFX(i)
    call OM_StopWindupFX(i)''')
    edit('OM_Home', '    call GroupClear(OM_Hit[i])', r'''    call GroupClear(OM_Hit[i])
    if returning and OM_Alive(OM_Hero[i]) and not OM_WasDead[i] then
        call OM_KeepEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\DispelMagic\\DispelMagicTarget.mdl", OM_Ball[i], "origin"), 0.45)
        call OM_CommandSound(OM_Ball[i], 8)
    endif''')
    edit('OM_Home', '// Silent return: no damage, marks, heal, haste or pending ultimate.', '// Cosmetic return only: no damage, heal, haste or pending ultimate.')
    edit('OM_Register', ' or GetPlayerId(GetOwningPlayer(u)) >= 12 or GetPlayerId(GetOwningPlayer(u)) >= 12', ' or GetPlayerId(GetOwningPlayer(u)) >= 12')
    edit('OM_Register', '    set OM_Hit[i] = CreateGroup()', '    set OM_Carrier[i] = u\n    set OM_State[i] = 0\n    set OM_Hit[i] = CreateGroup()')
    edit('OM_Unregister', '    call OM_StopTravelFX(i)', '    call OM_StopTravelFX(i)\n    call OM_StopWindupFX(i)')
    edit('OM_Burst', '        call OM_GroundRing(x, y, radius, true)', '        call OM_StopWindupFX(i)\n        call OM_GroundRing(x, y, radius, true)')
    edit('OM_Burst', '        if OM_Enemy(OM_Hero[i], u) then', '        if OM_Enemy(OM_Hero[i], u) then\n            call OM_TravelImpact(u)')
    edit('OM_Tick', '                            call OM_StopTravelFX(i)', '                            call OM_StopTravelFX(i)\n                            call OM_ArrivalFX(i, OM_State[i] == 2)')
    edit('OM_OnCast', r'        call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl", GetUnitX(OM_Ball[i]), GetUnitY(OM_Ball[i])))', '        call OM_WindupFX(i)')
    script = script.replace('function OM_OnEnter takes', '''// Tavern sales can change owner after the enter-region event has already fired.
function OM_OnSold takes nothing returns nothing
    call OM_Register(GetSoldUnit())
endfunction

function OM_OnEnter takes''', 1)
    edit('OM_Init', '    set r = CreateRegion()', '''    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SELL)
    call TriggerAddAction(t, function OM_OnSold)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_CHANGE_OWNER)
    call TriggerAddAction(t, function OM_OnEnter)
    set r = CreateRegion()''')
    # The control unit works in Warcraft, but its imported unit model stays invisible.
    # Render a persistent native effect independently of dummy-unit skin/animation state.
    script = script.replace('    hashtable OM_Hash = InitHashtable()', '    location OM_VisualGround = Location(0.0, 0.0)\n    hashtable OM_Hash = InitHashtable()', 1)
    visual_helpers = r'''
function OM_ClearBallVisual takes integer i returns nothing
    local integer key = GetHandleId(OM_Ball[i])
    local effect fx = LoadEffectHandle(OM_Hash, key, -102)
    if fx != null then
        // Native missile death animations must not leave a second orb behind.
        call BlzSetSpecialEffectAlpha(fx, 0)
        call BlzSetSpecialEffectPosition(fx, 0.0, 0.0, -10000.0)
        call DestroyEffect(fx)
        call RemoveSavedHandle(OM_Hash, key, -102)
    endif
    set fx = null
endfunction

function OM_UpdateBallVisual takes integer i returns nothing
    local integer key = GetHandleId(OM_Ball[i])
    local effect fx = LoadEffectHandle(OM_Hash, key, -102)
    local string model = "Abilities\\Weapons\\FarseerMissile\\FarseerMissile.mdl"
    local real x = GetUnitX(OM_Ball[i])
    local real y = GetUnitY(OM_Ball[i])
    if not OM_Alive(OM_Hero[i]) or GetUnitTypeId(OM_Ball[i]) == 0 then
        call OM_ClearBallVisual(i)
        set fx = null
        return
    endif
    if fx == null then
        if LoadBoolean(OM_Hash, key, -103) then
            set model = "Abilities\\Weapons\\PriestMissile\\PriestMissile.mdl"
        endif
        set fx = AddSpecialEffect(model, x, y)
        call BlzSetSpecialEffectScale(fx, 2.0)
        call BlzSetSpecialEffectAlpha(fx, 255)
        call BlzSetSpecialEffectTimeScale(fx, 1.0)
        call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
        call SaveEffectHandle(OM_Hash, key, -102, fx)
    endif
    call MoveLocation(OM_VisualGround, x, y)
    call BlzSetSpecialEffectPosition(fx, x, y, GetLocationZ(OM_VisualGround) + GetUnitFlyHeight(OM_Ball[i]))
    set fx = null
endfunction

'''
    script = script.replace('function OM_BallLook takes', visual_helpers + 'function OM_BallLook takes', 1)
    before = body('OM_BallLook')
    script = script.replace(before, '''function OM_BallLook takes integer i, boolean protect returns nothing
    local integer key = GetHandleId(OM_Ball[i])
    if LoadBoolean(OM_Hash, key, -103) != protect then
        call OM_ClearBallVisual(i)
    endif
    call SaveBoolean(OM_Hash, key, -103, protect)
    call OM_LockBall(OM_Ball[i])
    call OM_UpdateBallVisual(i)
endfunction''', 1)
    edit('OM_LockBall', "    call UnitRemoveAbility(ball, 'Aloc')\n", '')
    edit('OM_LockBall', '    // Both packaged orb models have looping Stand - 1 at sequence index 3.\n    call SetUnitAnimationByIndex(ball, 3)', '    // The blank control unit has no model animation; its persistent effect is separate.')
    edit('OM_Home', '    call GroupClear(OM_Hit[i])', '    call GroupClear(OM_Hit[i])\n    call OM_UpdateBallVisual(i)')
    edit('OM_Unregister', '    call RemoveUnit(OM_Ball[i])', '    call OM_ClearBallVisual(i)\n    call RemoveSavedBoolean(OM_Hash, GetHandleId(OM_Ball[i]), -103)\n    call RemoveUnit(OM_Ball[i])')
    edit('OM_Tick', '                    call ShowUnit(OM_Ball[i], false)', '                    call OM_ClearBallVisual(i)\n                    call ShowUnit(OM_Ball[i], false)')
    edit('OM_Tick', '                    call OM_Burst(i, true, 0)\n                endif', '                    call OM_Burst(i, true, 0)\n                endif\n                call OM_UpdateBallVisual(i)')
    return script
