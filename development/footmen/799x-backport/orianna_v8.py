"""Quiet orb presentation, attack gesture, and +10% AoE at every rank."""
import re


def tooltip(text):
    return re.sub(r'Radius: ([0-9.]+)\.', lambda m: 'Radius: '+format(float(m[1])*1.1,'g')+'.', text)


def patch(script):
    def body(name):
        return re.search(r'^function '+name+r' takes .*?^endfunction',script,re.M|re.S)[0]
    def edit(name,old,new):
        nonlocal script
        before=body(name)
        assert old in before,(name,old)
        script=script.replace(before,before.replace(old,new),1)
    old=r'Abilities\\Weapons\\FarseerMissile\\FarseerMissile.mdl'
    new=r'Spells\\Orianna\\Feedback\\SoftOrb.mdx'
    for name in ('OM_UpdateBallVisual','OM_EmitTrail'):
        edit(name,old,new)
    edit('OM_UpdateBallVisual','    local real y = GetUnitY(OM_Ball[i])', '''    local real y = GetUnitY(OM_Ball[i])
    local real remaining = LoadReal(OM_Hash, key, -105) - OM_Now
    local real gesture = 0.0''')
    edit('OM_UpdateBallVisual','BlzSetSpecialEffectScale(fx, 2.0)','BlzSetSpecialEffectScale(fx, 1.0)')
    edit('OM_UpdateBallVisual','    call MoveLocation(OM_VisualGround, x, y)', '''    if remaining > 0.0 then
        set gesture = Sin((1.0 - remaining / 0.25) * 3.14159265)
    endif
    call BlzSetSpecialEffectScale(fx, 1.0 + 0.18 * gesture)
    call MoveLocation(OM_VisualGround, x, y)''')
    edit('OM_UpdateBallVisual','GetLocationZ(OM_VisualGround) + GetUnitFlyHeight(OM_Ball[i]))',
         'GetLocationZ(OM_VisualGround) + GetUnitFlyHeight(OM_Ball[i]) + 20.0 * gesture)')
    edit('OM_StartPulse','    call OM_CommandSound(OM_Ball[i], 2)', '''    call SaveReal(OM_Hash, GetHandleId(OM_Ball[i]), -105, OM_Now + 0.25)
    call OM_CommandSound(OM_Ball[i], 2)''')
    edit('OM_Home','    call OM_StopTravelFX(i)','    call RemoveSavedReal(OM_Hash, GetHandleId(OM_Ball[i]), -105)\n    call OM_StopTravelFX(i)')
    edit('OM_Unregister','    call OM_ClearBallVisual(i)','    call RemoveSavedReal(OM_Hash, GetHandleId(OM_Ball[i]), -105)\n    call OM_ClearBallVisual(i)')
    for name in ('OM_TrailTick','OM_EmitTrail'):
        edit(name,'0.7','0.32')
        edit(name,'160','75')
    edit('OM_AttackRadius',body('OM_AttackRadius'),re.sub(r'return ([0-9.]+)',lambda m:'return '+str(round(float(m[1])*1.1,4)),body('OM_AttackRadius')))
    edit('OM_OnCast','* 0.385','* 0.4235')
    name='FF_HeroTooltips_Init'
    edit(name,body(name),'\n'.join(tooltip(line) if "'AOz2'" in line or "'AOz4'" in line else line for line in body(name).splitlines()))
    return script
