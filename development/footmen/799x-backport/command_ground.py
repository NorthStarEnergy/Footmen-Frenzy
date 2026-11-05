from pathlib import Path
import re


def patch(script):
    def edit(name,old,new):
        nonlocal script
        before=re.search(r'^function '+name+r' takes .*?^endfunction',script,re.M|re.S)[0]
        assert old in before,(name,old)
        script=script.replace(before,before.replace(old,new),1)
    script=script.replace('function OM_StopWindupFX takes',Path(__file__).with_suffix('.j').read_text()+'\nfunction OM_StopWindupFX takes',1)
    edit('OM_StopWindupFX','    set fx = null', '''    set fx = LoadEffectHandle(OM_Hash, key, -108)
    if fx != null then
        call BlzSetSpecialEffectAlpha(fx, 0)
        call DestroyEffect(fx)
        call RemoveSavedHandle(OM_Hash, key, -108)
    endif
    set fx = null''')
    edit('OM_WindupFX','    call OM_CommandSound(OM_Ball[i], 7)',r'''    set fx = AddSpecialEffect("Spells\\Orianna\\Feedback\\ShockGround.mdx", OM_X[i], OM_Y[i])
    call BlzSetSpecialEffectZ(fx, GetLocationZ(ground) + 8.0)
    call BlzSetSpecialEffectScale(fx, OM_ShockRadius[i] * 0.92)
    call BlzSetSpecialEffectAlpha(fx, 180)
    call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
    call SaveEffectHandle(OM_Hash, GetHandleId(OM_Ball[i]), -108, fx)
    call OM_CommandSound(OM_Ball[i], 7)''')
    edit('OM_UpdateBallVisual','    set fx = null\nendfunction','    call OM_UpdateShockGround(i)\n    set fx = null\nendfunction')
    edit('OM_StartPulse','    call OM_CommandSound(OM_Ball[i], 2)','    call OM_CommandGround(2, x, y, OM_AttackRadius(level) * 0.96, 0.0)\n    call OM_CommandSound(OM_Ball[i], 2)')
    edit('OM_ArrivalFX','    if protect then','    if protect then\n        call OM_CommandGround(3, GetUnitX(OM_Ball[i]), GetUnitY(OM_Ball[i]), OM_HASTE_RADIUS * 0.96, 0.0)')
    edit('OM_EmitTrail','    call MoveLocation(OM_VisualGround, x, y)', '''    if OM_State[i] == 1 and OM_Now >= LoadReal(OM_Hash, GetHandleId(OM_Ball[i]), -107) then
        call OM_CommandGround(1, x, y, 55.0, Atan2(OM_Y[i] - y, OM_X[i] - x))
        call SaveReal(OM_Hash, GetHandleId(OM_Ball[i]), -107, OM_Now + 0.09)
    endif
    call MoveLocation(OM_VisualGround, x, y)''')
    edit('OM_StartTravelFX','    call OM_StopTravelFX(i)','    call RemoveSavedReal(OM_Hash, GetHandleId(OM_Ball[i]), -107)\n    call OM_StopTravelFX(i)')
    edit('OM_Unregister','    call OM_ClearBallVisual(i)','    call RemoveSavedReal(OM_Hash, GetHandleId(OM_Ball[i]), -107)\n    call OM_ClearBallVisual(i)')
    return script
