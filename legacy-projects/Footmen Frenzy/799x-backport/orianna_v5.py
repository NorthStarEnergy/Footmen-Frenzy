"""Travel wake, expanding attack pulse, native ally feedback and reduced AoE."""
from pathlib import Path
import re


def tooltip(text):
    text = re.sub(r'Radius: ([0-9.]+)\.',
                  lambda m: 'Radius: ' + format(float(m[1]) * .7, 'g') + '.', text)
    return text.replace('Release a red ground burst around the ball.',
                        'Release a fast outward pulse from the ball.').replace(
        'Instant burst; no lingering damage.',
        'Expands in 0.25 seconds; hits each enemy once as the pulse reaches them.')


def patch(script):
    def body(name):
        return re.search(r'^function ' + name + r' takes .*?^endfunction', script, re.M | re.S)[0]

    def replace(name, value):
        nonlocal script
        script = script.replace(body(name), value, 1)

    def edit(name, old, new):
        before = body(name)
        assert old in before, (name, old)
        replace(name, before.replace(old, new))

    # Keep one visible native orb, including when Protect changes its color.
    edit('OM_UpdateBallVisual', '''        if LoadBoolean(OM_Hash, key, -103) then
            set model = "Abilities\\\\Weapons\\\\PriestMissile\\\\PriestMissile.mdl"
        endif
''', '')
    edit('OM_UpdateBallVisual', '    call MoveLocation(OM_VisualGround, x, y)', '''    if LoadBoolean(OM_Hash, key, -103) then
        call BlzSetSpecialEffectColor(fx, 65, 145, 255)
    else
        call BlzSetSpecialEffectColor(fx, 255, 255, 255)
    endif
    call MoveLocation(OM_VisualGround, x, y)''')
    edit('OM_BallLook', '''    if LoadBoolean(OM_Hash, key, -103) != protect then
        call OM_ClearBallVisual(i)
    endif
''', '')
    edit('OM_OnCast', '''    elseif a == OM_PULSE then
        call OM_BallLook(i, false)''', '    elseif a == OM_PULSE then')
    replace('OM_StartTravelFX', '''function OM_StartTravelFX takes integer i, boolean protect returns nothing
    call OM_StopTravelFX(i)
    if protect then
        call OM_CommandSound(OM_Ball[i], 4)
    else
        call OM_CommandSound(OM_Ball[i], 1)
    endif
endfunction''')
    # Direct attachment starts immediately on a crossed ally, and uses the same
    # lifetime/refresh rules as haste. BOr4's automatic art is blank to avoid doubles.
    edit('OM_Haste', '        call UnitAddAbility(u, \'AOz7\')', r'''        if LoadEffectHandle(OM_Hash, GetHandleId(u), -104) == null then
            call SaveEffectHandle(OM_Hash, GetHandleId(u), -104, AddSpecialEffectTarget("Abilities\\Spells\\Items\\AIsp\\SpeedTarget.mdl", u, "origin"))
        endif
        call UnitAddAbility(u, 'AOz7')''')
    edit('OM_HasteRemove', "    call UnitRemoveAbility(OM_HUnit[i], 'AOz7')", '''    call DestroyEffect(LoadEffectHandle(OM_Hash, GetHandleId(OM_HUnit[i]), -104))
    call RemoveSavedHandle(OM_Hash, GetHandleId(OM_HUnit[i]), -104)
    call UnitRemoveAbility(OM_HUnit[i], 'AOz7')''')
    before = body('OM_AttackRadius')
    replace('OM_AttackRadius', re.sub(r'return ([0-9.]+)', lambda m: 'return ' + str(round(float(m[1]) * .7, 4)), before))
    edit('OM_OnCast', '(400.0 + 100.0 * level) * 0.55', '(400.0 + 100.0 * level) * 0.385')
    edit('OM_Tick', '''                        call OM_TravelHits(i)
                        call SetUnitX''', '''                        call OM_EmitTrail(i)
                        call OM_TravelHits(i)
                        call SetUnitX''')
    # Each cast owns its center, groups, timer and effect: moving/recasting the
    # ball cannot drag an already released pulse or mix two heroes' hit lists.
    extra = (Path(__file__).parent / 'orianna_v5.j').read_text()
    script = script.replace('function OM_Burst takes', extra + '\nfunction OM_Burst takes', 1)
    replace('OM_Burst', '''function OM_Burst takes integer i, boolean ultimate, integer level returns nothing
    local unit u
    local real x = GetUnitX(OM_Ball[i])
    local real y = GetUnitY(OM_Ball[i])
    if not ultimate then
        call OM_StartPulse(i, level)
        return
    endif
    call OM_StopWindupFX(i)
    call OM_GroundRing(x, y, OM_ShockRadius[i], true)
    call OM_CommandSound(OM_Ball[i], 3)
    call GroupEnumUnitsInRange(OM_Group, x, y, OM_ShockRadius[i], null)
    loop
        set u = FirstOfGroup(OM_Group)
        exitwhen u == null
        call GroupRemoveUnit(OM_Group, u)
        if OM_Enemy(OM_Hero[i], u) then
            call OM_TravelImpact(u)
            call OM_Deal(OM_Hero[i], u, OM_ShockDamage[i])
            if OM_Alive(u) then
                call OM_Pull(u, x, y)
            endif
        endif
    endloop
    set u = null
endfunction''')
    name = 'FF_HeroTooltips_Init'
    replace(name, '\n'.join(tooltip(line) if "'AOz2'" in line or "'AOz4'" in line else line
                            for line in body(name).splitlines()))
    return script
