"""Visible full-size orb hovering above its carrier in world space."""
import re


def patch(script):
    def edit(name, old, new):
        nonlocal script
        before = re.search(r'^function '+name+r' takes .*?^endfunction', script, re.M | re.S)[0]
        assert old in before, (name, old)
        script = script.replace(before, before.replace(old, new), 1)

    name = 'OM_UpdateBallVisual'
    edit(name, '    local boolean attached = OM_State[i] == 0 and OM_Carrier[i] == OM_Hero[i]\n', '')
    edit(name, '''    if fx != null and LoadBoolean(OM_Hash, key, -106) != attached then
        call OM_ClearBallVisual(i)
        set fx = null
    endif
''', '')
    edit(name, '''        if attached then
            set fx = AddSpecialEffectTarget(model, OM_Hero[i], "hand,right")
        else
            set fx = AddSpecialEffect(model, x, y)
        endif''', '        set fx = AddSpecialEffect(model, x, y)')
    edit(name, '        call SaveBoolean(OM_Hash, key, -106, attached)\n', '')
    edit(name, '0.65 * (1.0 + 0.18 * gesture)', '2.0 * (1.0 + 0.18 * gesture)')
    edit(name, '''    if not attached then
        call MoveLocation(OM_VisualGround, x, y)
        call BlzSetSpecialEffectPosition(fx, x, y, GetLocationZ(OM_VisualGround) + GetUnitFlyHeight(OM_Ball[i]) + 20.0 * gesture)
    endif''', '''    // The control ball follows either carrier at their fly height + 220 units.
    // World-space positioning avoids model attachment offsets and inherited scale.
    call MoveLocation(OM_VisualGround, x, y)
    call BlzSetSpecialEffectPosition(fx, x, y, GetLocationZ(OM_VisualGround) + GetUnitFlyHeight(OM_Ball[i]) + 20.0 * gesture)''')
    edit('OM_ClearBallVisual', '    call RemoveSavedBoolean(OM_Hash, key, -106)\n', '')
    for name in ('OM_EmitTrail', 'OM_TrailTick'):
        edit(name, '0.22', '0.68')
    return script
