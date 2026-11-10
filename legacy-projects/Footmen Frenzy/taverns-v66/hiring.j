function FFHire_Prepare takes nothing returns nothing
    local integer pn = 1
    local integer team = 1
    local integer i
    local integer a
    local integer raw
    local integer idx
    local integer key
    local player p
    local unit shop
    local trigger chat
    if FFHire_Ready then
        return
    endif
    set FFHire_Ready = true
    loop
        exitwhen team > 4
        set T66_RandomLeft[team] = 3
        if CarryTav_shop[team] == null then
            set CarryTav_shop[team] = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'n66A', -2624, 160 - I2R(team-1)*288, 270)
        endif
        call GroupAddUnit(udg_realshops, CarryTav_shop[team])
        call RemoveUnitFromStock(CarryTav_shop[team], 'H0R0')
        call BlzSetUnitName(CarryTav_shop[team], "Team " + I2S(team) + " - Carry Altar / Random Hero")
        set T66_Offers[team] = "Available taverns:|nCarry Altar: Random Hero (3 shared uses)"
        if udg_selected_mode == 3 then
            call BlzSetUnitName(udg_real_shop[team], "Team " + I2S(team) + " - Hero Tavern")
            // Record the exact stock, including the older/mirror draft paths.
            set key = GetHandleId(udg_real_shop[team])
            set i = 1
            loop
                exitwhen i > LoadInteger(T66_StockHash, key, 0)
                set raw = LoadInteger(T66_StockHash, key, i)
                set idx = 1
                loop
                    exitwhen idx > udg_total_hero_count or udg_hero_type[idx] == raw
                    set idx = idx + 1
                endloop
                if idx <= udg_total_hero_count and udg_hero_category[idx] >= 12 then
                    call RemoveUnitFromStock(udg_real_shop[team], raw)
                    call MF_StockUnit(CarryTav_shop[team], raw, 1, 1)
                else
                    set T66_Offers[team] = T66_Offers[team] + "|nTavern: " + GetObjectName(raw)
                endif
                set i = i + 1
            endloop
            set key = GetHandleId(CarryTav_shop[team])
            set i = 1
            loop
                exitwhen i > LoadInteger(T66_StockHash, key, 0)
                set raw = LoadInteger(T66_StockHash, key, i)
                set T66_Offers[team] = T66_Offers[team] + "|nAltar: " + GetObjectName(raw)
                set i = i + 1
            endloop
        elseif udg_selected_mode == 2 then
            set T66_Offers[team] = T66_Offers[team] + "|nAll Pick: all nine western taverns, full enabled roster."
        else
            set T66_Offers[team] = T66_Offers[team] + "|nAll Random: automatic hero assignment. Random altar available for an eligible repick."
        endif
        set T66_RecordQuest[team] = CreateQuest()
        call QuestSetTitle(T66_RecordQuest[team], "Team " + I2S(team) + " - Draft Record (v66)")
        call QuestSetIconPath(T66_RecordQuest[team], "ReplaceableTextures\\CommandButtons\\BTNAltarOfKings.blp")
        call QuestSetRequired(T66_RecordQuest[team], false)
        call QuestSetDiscovered(T66_RecordQuest[team], true)
        call T66_Position(team, false)
        set team = team + 1
    endloop
    loop
        exitwhen pn > 12
        set p = ConvertedPlayer(pn)
        set team = udg_teamnumber[pn]
        if GetPlayerSlotState(p) == PLAYER_SLOT_STATE_PLAYING and team >= 1 and team <= 4 then
            if udg_selected_mode == 2 then
                call FFHire_CreateBuyer(p, -2688.0, -256.0)
                set T66_Buyer[pn] = T66_LastBuyer
            elseif udg_selected_mode == 3 then
                set shop = udg_real_shop[team]
                call FFHire_CreateBuyer(p, GetUnitX(shop), GetUnitY(shop))
                set T66_Buyer[pn] = T66_LastBuyer
            endif
            set shop = CarryTav_shop[team]
            call FFHire_CreateBuyer(p, GetUnitX(shop), GetUnitY(shop))
            set T66_CarryBuyer[pn] = T66_LastBuyer
        endif
        set pn = pn + 1
    endloop
    if udg_selected_mode != 2 then
        call T66_StopViews()
    endif
    set chat = CreateTrigger()
    set pn = 0
    loop
        exitwhen pn > 23
        call TriggerRegisterPlayerChatEvent(chat, Player(pn), "-draft", true)
        set pn = pn + 1
    endloop
    call TriggerAddAction(chat, function T66_ShowRecord)
    call TimerStart(CreateTimer(), 0.5, true, function T66_Record)
    call DisplayTextToForce(GetPlayersAll(), "v66: Team draft offers and picks are available to everyone in Quests (F9), or type -draft. Random Hero has 3 shared uses per team.")
    set chat = null
    set shop = null
    set p = null
endfunction
