function FFRandom_Stock takes nothing returns nothing
    local integer team = 1
    loop
        exitwhen team > 4
        if CarryTav_shop[team] != null then
            call RemoveUnitFromStock(CarryTav_shop[team], 'h004')
            if T66_RandomLeft[team] > 0 then
                call MF_StockUnit(CarryTav_shop[team], 'h004', T66_RandomLeft[team], 3)
            endif
        endif
        set team = team + 1
    endloop
endfunction

function FFRandom_Sold takes nothing returns nothing
    local unit sold = GetSoldUnit()
    local unit shop = GetSellingUnit()
    local player p
    local integer pn
    local integer team
    local integer index
    local integer i = 1
    local integer count = 0
    if GetUnitTypeId(sold) != 'h004' then
        set sold = null
        set shop = null
        return
    endif
    call SoloSub_ReownToSlot(sold)
    set p = GetOwningPlayer(sold)
    set pn = GetConvertedPlayerId(p)
    set team = udg_teamnumber[pn]
    call RemoveUnit(sold)
    if pn >= 1 and pn <= 12 and team >= 1 and team <= 4 and shop == CarryTav_shop[team] and T66_RandomLeft[team] > 0 and GetPlayerSlotState(p) == PLAYER_SLOT_STATE_PLAYING and (udg_herO[pn] == null or udg_mode_debugmode) then
        set index = 0
        loop
            exitwhen i > udg_total_hero_count
            if udg_hero_type[i] != 0 and not MF_HeroDisabled(udg_hero_type[i]) and (udg_selected_mode != 3 or FFR_Allowed(team, i)) and (udg_hero_category[i] < 12 or not CarryTav_locked[team]) then
                set count = count + 1
                if GetRandomInt(1, count) == 1 then
                    set index = i
                endif
            endif
            set i = i + 1
        endloop
        if index > 0 then
            set T66_RandomLeft[team] = T66_RandomLeft[team] - 1
            call CreateNUnitsAtLoc(1, udg_hero_type[index], p, udg_loc_tavern, bj_UNIT_FACING)
            if udg_selected_mode == 3 then
                call UnitAddItemByIdSwapped('bspd', GetLastCreatedUnit())
            endif
            if udg_hero_category[index] >= 12 then
                call CarryTav_LockTeam(team)
            endif
        else
            call DisplayTextToPlayer(p, 0, 0, "No eligible heroes remain; your Random use was not consumed.")
        endif
    else
        call DisplayTextToPlayer(p, 0, 0, "Use your own team's Carry Altar while eligible to choose a hero. Each team has 3 shared Random uses.")
    endif
    call FFRandom_Stock()
    set sold = null
    set shop = null
    set p = null
endfunction
