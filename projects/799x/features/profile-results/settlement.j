function PF_NativeResult takes player p, boolean won, string message returns nothing
    local integer s = GetPlayerId(p)+1
    if not PF_frozen or GetPlayerController(p) != MAP_CONTROL_USER or GetPlayerSlotState(p) != PLAYER_SLOT_STATE_PLAYING or FF_IsBotName(GetPlayerName(p)) then
        if won then
            call CustomVictoryBJ(p,true,true)
        else
            call CustomDefeatBJ(p,message)
        endif
        return
    endif
    if PF_verdict[s] != 0 then
        return
    endif
    if won and AllowVictoryDefeat(PLAYER_GAME_RESULT_VICTORY) then
        set PF_verdict[s] = 1
    elseif not won and AllowVictoryDefeat(PLAYER_GAME_RESULT_DEFEAT) then
        set PF_verdict[s] = 2
        set PF_message[s] = message
    endif
    if GetLocalPlayer() == p and PF_visible and PF_results then
        call BlzFrameSetEnable(PF_continue,PF_verdict[s] > 0)
    endif
endfunction

function PF_Freeze takes nothing returns nothing
    local integer s = 1
    local integer k
    if PF_frozen then
        return
    endif
    loop
        exitwhen s > 24
        if s <= 4 then
            set PF_hillSeconds[s] = FF_us_kothHold[s]
        endif
        if s <= 12 then
            call PF_HeroExperience(s)
            call PF_ObserveBalance(s,GetPlayerState(Player(s-1),PLAYER_STATE_RESOURCE_GOLD))
        endif
        set k = 0
        if s > 12 then
            set k = PF_casinoFirst
        endif
        loop
            exitwhen k >= PF_metrics
            call SaveInteger(PF_final,s,k,PF_Live(s,k))
            set k = k+1
        endloop
        set s = s+1
    endloop
    set PF_frozen = true
endfunction
