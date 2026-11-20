function FFA_CloseProfile takes nothing returns nothing
    local framehandle f = BlzGetTriggerFrame()
    if f != null then
        call BlzFrameSetFocus(f,false)
    endif
    set DPS_Open[GetPlayerId(GetLocalPlayer())] = false
    set spellKeysOpen = false
    set spellKeysEditing = -1
    if spellKeysPanel != null then
        call BlzFrameSetVisible(spellKeysPanel,false)
    endif
    call BlzFrameSetVisible(DPS_Panel,false)
    set f = null
endfunction

function FF_LinkProfile takes nothing returns nothing
    if DPS_Panel != null and spellKeysToggle != null then
        call BlzFrameSetParent(spellKeysToggle, DPS_Panel)
        call BlzFrameClearAllPoints(spellKeysToggle)
        call BlzFrameSetPoint(spellKeysToggle, FRAMEPOINT_TOPRIGHT, DPS_Panel, FRAMEPOINT_TOPRIGHT, -0.065, -0.012)
        call BlzFrameSetSize(spellKeysToggle, 0.065, 0.025)
    endif
endfunction
