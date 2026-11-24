function FF_PickTwistedFate takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer pn = GetConvertedPlayerId(p)
    local unit hero
    if not (DraftAllPick or udg_selected_mode == 2) or pn > 12 or not udg_player_active[pn] or udg_herO[pn] != null or not DraftPending[pn] or udg_altar_hero_purchases[pn] > 0 then
        return
    endif
    if GetUnitTypeId(FF_FatePick[pn-1]) != 0 then
        return
    endif
    set hero = CreateUnitAtLoc(p, 'HTf1', udg_loc_tavern, bj_UNIT_FACING)
    set FF_FatePick[pn-1] = hero
    set hero = null
    set p = null
endfunction

function FF_InitTwistedFatePick takes nothing returns nothing
    local trigger chat = CreateTrigger()
    local integer slot = 0
    loop
        exitwhen slot >= 12
        call TriggerRegisterPlayerChatEvent(chat, Player(slot), "-tf", true)
        set slot = slot + 1
    endloop
    call TriggerAddAction(chat, function FF_PickTwistedFate)
    set chat = null
endfunction
