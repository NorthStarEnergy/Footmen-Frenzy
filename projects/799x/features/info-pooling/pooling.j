function FFPoolEligible takes integer slot, integer target returns boolean
    return target >= 1 and target <= 12 and target != slot and IsPlayerAlly(ConvertedPlayer(target), ConvertedPlayer(slot)) and SoloSub_CanReceiveGold(target)
endfunction

function FFPoolRefresh takes integer slot returns nothing
    local string recipient = "Off"
    if GetLocalPlayer() == ConvertedPlayer(slot) then
        if FFPoolTarget[slot] != 0 then
            set recipient = GetPlayerName(ConvertedPlayer(FFPoolTarget[slot]))
        endif
        call BlzFrameSetText(FFPoolRecipient, "Send to: " + recipient)
        call BlzFrameSetText(FFPoolReserveButton, "Keep: " + I2S(FFPoolReserve[slot]) + " gold")
        call BlzFrameSetEnable(FFPoolRecipient, FFR4_PoolingAllowed())
        call BlzFrameSetEnable(FFPoolReserveButton, FFR4_PoolingAllowed())
        if FFR4_PoolingAllowed() then
            call BlzFrameSetText(FFPoolTitle, "Pooling")
        else
            call BlzFrameSetText(FFPoolTitle, "Pooling (locked)")
        endif
        call BlzFrameSetVisible(FFPoolPanel, FFPoolOpen[slot])
    endif
endfunction

function FFPoolClose takes integer slot returns nothing
    if FFR4_PoolingAllowed() then
        if FFPoolTarget[slot] == 0 or FFPoolEligible(slot, FFPoolTarget[slot]) then
            set udg_autopoolto[slot] = FFPoolTarget[slot]
        else
            set udg_autopoolto[slot] = 0
        endif
        set udg_pool_threshold[slot] = FFPoolReserve[slot]
    endif
    set FFPoolOpen[slot] = false
    call FFPoolRefresh(slot)
endfunction

function FFPoolKey takes nothing returns nothing
    local integer slot = GetConvertedPlayerId(GetTriggerPlayer())
    if FFPoolOpen[slot] then
        call FFPoolClose(slot)
    elseif BlzGetTriggerPlayerKey() == OSKEY_F3 and slot <= 12 then
        set FFPoolTarget[slot] = udg_autopoolto[slot]
        set FFPoolReserve[slot] = udg_pool_threshold[slot]
        set FFPoolOpen[slot] = true
        call FFPoolRefresh(slot)
    elseif BlzGetTriggerPlayerKey() == OSKEY_F2 then
        call Uncle_ClearTextCommandsCallback()
    endif
endfunction

function FFPoolClick takes nothing returns nothing
    local integer slot = GetConvertedPlayerId(GetTriggerPlayer())
    local integer target = FFPoolTarget[slot]
    local framehandle clickedFrame = BlzGetTriggerFrame()
    if FFPoolOpen[slot] then
        if clickedFrame == FFPoolCloseButton then
            call FFPoolClose(slot)
        elseif FFR4_PoolingAllowed() then
            if clickedFrame == FFPoolRecipient then
                loop
                    set target = ModuloInteger(target + 1, 13)
                    exitwhen target == 0 or FFPoolEligible(slot, target)
                endloop
                set FFPoolTarget[slot] = target
            elseif FFPoolReserve[slot] == 0 then
                set FFPoolReserve[slot] = 50
            elseif FFPoolReserve[slot] == 50 then
                set FFPoolReserve[slot] = 150
            elseif FFPoolReserve[slot] == 150 then
                set FFPoolReserve[slot] = 250
            elseif FFPoolReserve[slot] == 250 then
                set FFPoolReserve[slot] = 500
            else
                set FFPoolReserve[slot] = 0
            endif
            call FFPoolRefresh(slot)
        endif
    endif
    if GetLocalPlayer() == GetTriggerPlayer() then
        call BlzFrameSetFocus(clickedFrame, false)
    endif
    set clickedFrame = null
endfunction

function FFPoolButton takes trigger click, string label, real x, real y, real width returns framehandle
    local framehandle b = BlzCreateFrame("ScriptDialogButton", FFPoolPanel, 0, 0)
    call BlzFrameSetPoint(b, FRAMEPOINT_TOPLEFT, FFPoolPanel, FRAMEPOINT_TOPLEFT, x, -y)
    call BlzFrameSetSize(b, width, 0.026)
    call BlzFrameSetText(b, label)
    call BlzTriggerRegisterFrameEvent(click, b, FRAMEEVENT_CONTROL_CLICK)
    return b
endfunction

function FFPoolInit takes nothing returns nothing
    local trigger keys = CreateTrigger()
    local trigger click = CreateTrigger()
    local integer i = 0
    set FFPoolPanel = BlzCreateFrame("EscMenuBackdrop", FFUI_GetRoot(), 0, 0)
    call BlzFrameSetAbsPoint(FFPoolPanel, FRAMEPOINT_TOPRIGHT, 0.785, 0.485)
    call BlzFrameSetSize(FFPoolPanel, 0.225, 0.122)
    call BlzFrameSetLevel(FFPoolPanel, 30)
    set FFPoolTitle = BlzCreateFrameByType("TEXT", "FFPoolTitle", FFPoolPanel, "", 0)
    call BlzFrameSetPoint(FFPoolTitle, FRAMEPOINT_TOPLEFT, FFPoolPanel, FRAMEPOINT_TOPLEFT, 0.018, -0.017)
    set FFPoolCloseButton = FFPoolButton(click, "X", 0.184, 0.009, 0.027)
    set FFPoolRecipient = FFPoolButton(click, "", 0.018, 0.040, 0.189)
    set FFPoolReserveButton = FFPoolButton(click, "", 0.018, 0.074, 0.189)
    call BlzFrameSetVisible(FFPoolPanel, false)
    loop
        exitwhen i >= bj_MAX_PLAYER_SLOTS
        call BlzTriggerRegisterPlayerKeyEvent(keys, Player(i), OSKEY_F2, 0, false)
        if i < 12 then
            call BlzTriggerRegisterPlayerKeyEvent(keys, Player(i), OSKEY_F3, 0, false)
        endif
        set i = i + 1
    endloop
    call TriggerAddAction(keys, function FFPoolKey)
    call TriggerAddAction(click, function FFPoolClick)
    set keys = null
    set click = null
endfunction


