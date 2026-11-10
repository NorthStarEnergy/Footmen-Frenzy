function T66_Move takes unit u, real x, real y returns nothing
    if u != null then
        call SetUnitPathing(u, false)
        call SetUnitX(u, x)
        call SetUnitY(u, y)
    endif
endfunction

function T66_View takes player p, rect r returns nothing
    set T66_ViewCount = T66_ViewCount + 1
    set T66_Views[T66_ViewCount] = CreateFogModifierRect(p, FOG_OF_WAR_VISIBLE, r, true, false)
    call FogModifierStart(T66_Views[T66_ViewCount])
endfunction

function T66_StopViews takes nothing returns nothing
    local integer i = 1
    loop
        exitwhen i > T66_ViewCount
        call FogModifierStop(T66_Views[i])
        call DestroyFogModifier(T66_Views[i])
        set T66_Views[i] = null
        set i = i + 1
    endloop
    set T66_ViewCount = 0
    set i = 0
    loop
        exitwhen i > 23
        call SetFogStateRect(Player(i), FOG_OF_WAR_FOGGED, gg_rct_TAVERN_AREA, false)
        set i = i + 1
    endloop
endfunction

function T66_Position takes integer team, boolean archived returns nothing
    local real x
    local real y
    local real carryX
    local integer pn = 1
    if archived or udg_selected_mode == 2 then
        set x = -3008.0
        set y = 160.0 - I2R(team - 1) * 288.0
    else
        set x = -1600.0
        if team == 2 or team == 3 then
            set x = 1280.0
        endif
        set y = 1408.0
        if team >= 3 then
            set y = -1920.0
        endif
    endif
    set carryX = x + 384.0
    if archived or udg_selected_mode == 2 then
        set carryX = -2272.0
        if udg_selected_mode == 2 then
            set carryX = -3104.0
        endif
    endif
    if udg_selected_mode == 3 then
        call T66_Move(udg_real_shop[team], x, y)
    endif
    call T66_Move(CarryTav_shop[team], carryX, y)
    loop
        exitwhen pn > 12
        if udg_teamnumber[pn] == team then
            if udg_selected_mode == 2 and not archived and T66_Archived[team] then
                call T66_View(ConvertedPlayer(pn), gg_rct_TAVERN_AREA)
            endif
            if udg_selected_mode == 3 then
                call T66_Move(T66_Buyer[pn], x, y)
            endif
            call T66_Move(T66_CarryBuyer[pn], carryX, y)
        endif
        set pn = pn + 1
    endloop
    set T66_Archived[team] = archived
endfunction

function T66_Record takes nothing returns nothing
    local integer team = 1
    local integer pn
    local boolean complete
    local boolean allDone = true
    local string picks
    loop
        exitwhen team > 4
        set pn = 1
        set picks = ""
        set complete = true
        loop
            exitwhen pn > 12
            if udg_teamnumber[pn] == team and GetPlayerSlotState(ConvertedPlayer(pn)) == PLAYER_SLOT_STATE_PLAYING then
                if udg_herO[pn] != null and GetUnitTypeId(udg_herO[pn]) != 0 then
                    set picks = picks + "|n" + udg_orig_player_name[pn] + ": " + GetUnitName(udg_herO[pn])
                else
                    set picks = picks + "|n" + udg_orig_player_name[pn] + ": choosing"
                    set complete = false
                endif
            endif
            set pn = pn + 1
        endloop
        if T66_RecordQuest[team] != null then
            call QuestSetDescription(T66_RecordQuest[team], T66_Offers[team] + "|n|nPicks:" + picks + "|n|nRandom Hero uses remaining: " + I2S(T66_RandomLeft[team]) + "/3 (shared by team).|nRandom draws from the full eligible roster; team category limits still apply.")
        endif
        if complete != T66_Archived[team] then
            call T66_Position(team, complete)
        endif
        if not complete then
            set allDone = false
        endif
        set team = team + 1
    endloop
    if allDone and T66_ViewCount > 0 then
        call T66_StopViews()
    endif
endfunction

function T66_ShowRecord takes nothing returns nothing
    local integer team = 1
    loop
        exitwhen team > 4
        call DisplayTimedTextToPlayer(GetTriggerPlayer(), 0, 0, 30, "Team " + I2S(team) + ": " + QuestGetDescription(T66_RecordQuest[team]))
        set team = team + 1
    endloop
endfunction
