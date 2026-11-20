function PF_Average takes integer gold, integer count returns integer
    if count == 0 then
        return 0
    endif
    return gold / count
endfunction

function PF_Use takes integer slot, integer kind, integer id, integer quantity returns nothing
    local integer key = slot * 10 + kind
    if PF_frozen or slot < 1 or slot > 12 or id == 0 or quantity <= 0 then
        return
    endif
    if not HaveSavedInteger(PF_data, key, id) then
        call SaveInteger(PF_data, 300 + key, PF_counts[key], id)
        set PF_counts[key] = PF_counts[key] + 1
    endif
    call SaveInteger(PF_data, key, id, LoadInteger(PF_data, key, id) + quantity)
    set PF_dirty = true
endfunction

function PF_Appearance takes integer slot, unit u, integer count returns nothing
    if u != null then
        call PF_Use(slot, 4, BlzGetUnitSkin(u), count)
    endif
endfunction

function PF_Hero takes integer slot, unit u returns nothing
    local integer id = GetUnitTypeId(u)
    if not PF_frozen and id != 0 and IsUnitType(u, UNIT_TYPE_HERO) and not IsUnitIllusion(u) and not HaveSavedHandle(PF_data, 900 + slot, GetHandleId(u)) then
        call SaveUnitHandle(PF_data, 900 + slot, GetHandleId(u), u)
        call SaveUnitHandle(PF_data, 950 + slot, PF_heroCount[slot], u)
        set PF_heroCount[slot] = PF_heroCount[slot]+1
        call PF_Use(slot, 1, id, 1)
        call PF_Appearance(slot, u, 1)
        set PF_lastHero[slot] = id
    endif
endfunction

function PF_HeroExperience takes integer s returns nothing
    local integer i = 0
    local integer xp
    local integer prev
    local unit hero
    loop
        exitwhen i >= PF_heroCount[s]
        set hero = LoadUnitHandle(PF_data,950+s,i)
        if GetUnitTypeId(hero) != 0 then
            set xp = GetHeroXP(hero)
            set prev = LoadInteger(PF_data,980+s,i)
            if xp > prev then
                set PF_heroXP[s] = PF_heroXP[s]+xp-prev
                call SaveInteger(PF_data,980+s,i,xp)
            endif
        endif
        set i = i+1
    endloop
    set hero = null
endfunction

function PF_Log takes integer slot, string actionName, integer id, integer gold, integer other returns nothing
    local integer n
    local integer key = 1000 + slot * 10
    if PF_frozen or slot < 1 or slot > 24 then
        return
    endif
    set n = PF_logCount[slot]
    call SaveStr(PF_data, key, n, actionName)
    call SaveInteger(PF_data, key+1, n, id)
    call SaveInteger(PF_data, key+2, n, gold)
    call SaveInteger(PF_data, key+3, n, other)
    call SaveInteger(PF_data, key+4, n, R2I(TimerGetElapsed(FF_gameTimer)))
    call SaveInteger(PF_data, key+5, n, GetPlayerState(Player(slot-1), PLAYER_STATE_RESOURCE_GOLD))
    set PF_logCount[slot] = n + 1
    set PF_dirty = true
endfunction

function PF_Price takes integer id, integer level returns integer
    if not HaveSavedInteger(PF_prices, 1, id) then
        return -1
    endif
    return LoadInteger(PF_prices, 1, id) + IMaxBJ(0, level-1) * LoadInteger(PF_prices, 2, id)
endfunction

function PF_Purchase takes integer slot, string kind, integer id, integer price returns nothing
    call PF_Log(slot, kind, id, price, 0)
endfunction

function PF_Transfer takes integer sender, integer target, integer amount returns nothing
    if PF_frozen then
        return
    endif
    set PF_sent[sender] = PF_sent[sender] + 1
    set PF_received[target] = PF_received[target] + 1
    call PF_Log(sender, "pool_sent", 0, amount, target)
    call PF_Log(target, "pool_received", 0, amount, sender)
endfunction

function PF_ArmGold takes integer slot returns trigger
    local trigger t = CreateTrigger()
    call TriggerRegisterPlayerStateEvent(t, Player(slot-1), PLAYER_STATE_RESOURCE_GOLD, NOT_EQUAL, I2R(GetPlayerState(Player(slot-1), PLAYER_STATE_RESOURCE_GOLD)))
    return t
endfunction

function PF_ObserveBalance takes integer slot, integer balance returns nothing
    local integer old = LoadInteger(PF_data, 800, slot)
    if not PF_frozen and HaveSavedInteger(PF_data,800,slot) then
        call SaveInteger(PF_data,800,slot,balance)
        if balance < old then
            set PF_recordedCost[slot] = PF_recordedCost[slot]+old-balance
            call PF_Log(slot,"gold_out",0,old-balance,0)
        endif
    endif
endfunction

function PF_GoldChanged takes nothing returns nothing
    local integer slot = GetPlayerId(GetTriggerPlayer()) + 1
    local trigger t
    call DestroyTrigger(GetTriggeringTrigger())
    if not PF_frozen then
        call PF_ObserveBalance(slot,GetPlayerState(GetTriggerPlayer(),PLAYER_STATE_RESOURCE_GOLD))
        set t = PF_ArmGold(slot)
        call TriggerAddAction(t, function PF_GoldChanged)
        set t = null
    endif
endfunction

function PF_InitGold takes nothing returns nothing
    local integer s = 1
    local trigger t
    loop
        exitwhen s > 12
        call SaveInteger(PF_data, 800, s, GetPlayerState(Player(s-1), PLAYER_STATE_RESOURCE_GOLD))
        set t = PF_ArmGold(s)
        call TriggerAddAction(t, function PF_GoldChanged)
        set s = s + 1
    endloop
    set t = null
endfunction

function FF_CloseProfilePanels takes nothing returns nothing
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

function PF_Schema takes nothing returns nothing
    set PF_casinoFirst = 60
    set PF_combatFirst = 26
    set PF_poolOutMetric = 38
    set PF_poolInMetric = 39
    set PF_sentMetric = 40
    set PF_receivedMetric = 41
    set PF_menuOrder[0] = 0
    set PF_sectionName[0] = "Overview"
    set PF_menuOrder[1] = 8
    set PF_sectionName[8] = "Combat"
    set PF_menuOrder[2] = 9
    set PF_sectionName[9] = "Economy"
    set PF_menuOrder[3] = 10
    set PF_sectionName[10] = "Army and tech"
    set PF_menuOrder[4] = 1
    set PF_sectionName[1] = "Heroes"
    set PF_menuOrder[5] = 2
    set PF_sectionName[2] = "Items"
    set PF_menuOrder[6] = 3
    set PF_sectionName[3] = "Units"
    set PF_menuOrder[7] = 4
    set PF_sectionName[4] = "Skins"
    set PF_menuOrder[8] = 5
    set PF_sectionName[5] = "Build order"
    set PF_menuOrder[9] = 7
    set PF_sectionName[7] = "Usage"
    set PF_menuOrder[10] = 6
    set PF_sectionName[6] = "Casino"
    set PF_sectionCount[0] = 9
    set PF_metricOrder[0] = 25
    set PF_metricOrder[1] = 29
    set PF_metricOrder[2] = 30
    set PF_metricOrder[3] = 28
    set PF_metricOrder[4] = 26
    set PF_metricOrder[5] = 27
    set PF_metricOrder[6] = 31
    set PF_metricOrder[7] = 34
    set PF_metricOrder[8] = 24
    set PF_sectionCount[8] = 17
    set PF_metricOrder[800] = 29
    set PF_metricOrder[801] = 30
    set PF_metricOrder[802] = 28
    set PF_metricOrder[803] = 26
    set PF_metricOrder[804] = 27
    set PF_metricOrder[805] = 31
    set PF_metricOrder[806] = 32
    set PF_metricOrder[807] = 33
    set PF_metricOrder[808] = 34
    set PF_metricOrder[809] = 35
    set PF_metricOrder[810] = 36
    set PF_metricOrder[811] = 47
    set PF_metricOrder[812] = 48
    set PF_metricOrder[813] = 49
    set PF_metricOrder[814] = 50
    set PF_metricOrder[815] = 51
    set PF_metricOrder[816] = 7
    set PF_sectionCount[9] = 27
    set PF_metricOrder[900] = 10
    set PF_metricOrder[901] = 37
    set PF_metricOrder[902] = 38
    set PF_metricOrder[903] = 39
    set PF_metricOrder[904] = 40
    set PF_metricOrder[905] = 41
    set PF_metricOrder[906] = 42
    set PF_metricOrder[907] = 43
    set PF_metricOrder[908] = 46
    set PF_metricOrder[909] = 11
    set PF_metricOrder[910] = 12
    set PF_metricOrder[911] = 13
    set PF_metricOrder[912] = 14
    set PF_metricOrder[913] = 15
    set PF_metricOrder[914] = 44
    set PF_metricOrder[915] = 45
    set PF_metricOrder[916] = 53
    set PF_metricOrder[917] = 16
    set PF_metricOrder[918] = 17
    set PF_metricOrder[919] = 18
    set PF_metricOrder[920] = 19
    set PF_metricOrder[921] = 20
    set PF_metricOrder[922] = 81
    set PF_metricOrder[923] = 82
    set PF_metricOrder[924] = 83
    set PF_metricOrder[925] = 84
    set PF_metricOrder[926] = 85
    set PF_sectionCount[10] = 19
    set PF_metricOrder[1000] = 0
    set PF_metricOrder[1001] = 1
    set PF_metricOrder[1002] = 2
    set PF_metricOrder[1003] = 3
    set PF_metricOrder[1004] = 4
    set PF_metricOrder[1005] = 5
    set PF_metricOrder[1006] = 6
    set PF_metricOrder[1007] = 8
    set PF_metricOrder[1008] = 9
    set PF_metricOrder[1009] = 52
    set PF_metricOrder[1010] = 54
    set PF_metricOrder[1011] = 55
    set PF_metricOrder[1012] = 56
    set PF_metricOrder[1013] = 57
    set PF_metricOrder[1014] = 58
    set PF_metricOrder[1015] = 59
    set PF_metricOrder[1016] = 21
    set PF_metricOrder[1017] = 22
    set PF_metricOrder[1018] = 23
    set PF_sectionCount[6] = 21
    set PF_metricOrder[600] = 64
    set PF_metricOrder[601] = 66
    set PF_metricOrder[602] = 65
    set PF_metricOrder[603] = 60
    set PF_metricOrder[604] = 61
    set PF_metricOrder[605] = 62
    set PF_metricOrder[606] = 63
    set PF_metricOrder[607] = 67
    set PF_metricOrder[608] = 68
    set PF_metricOrder[609] = 69
    set PF_metricOrder[610] = 70
    set PF_metricOrder[611] = 71
    set PF_metricOrder[612] = 72
    set PF_metricOrder[613] = 73
    set PF_metricOrder[614] = 74
    set PF_metricOrder[615] = 75
    set PF_metricOrder[616] = 76
    set PF_metricOrder[617] = 77
    set PF_metricOrder[618] = 78
    set PF_metricOrder[619] = 79
    set PF_metricOrder[620] = 80
    set PF_metrics = 81
    set PF_label[0] = "Units trained"
    set PF_key[0] = "trained"
    set PF_label[1] = "Units killed"
    set PF_key[1] = "killed"
    set PF_label[2] = "Structures built"
    set PF_key[2] = "built"
    set PF_label[3] = "Structures razed"
    set PF_key[3] = "razed"
    set PF_label[4] = "Tech percentage"
    set PF_key[4] = "tech"
    set PF_label[5] = "Peak food produced"
    set PF_key[5] = "food_cap"
    set PF_label[6] = "Peak food used"
    set PF_key[6] = "food_used"
    set PF_label[7] = "Heroes killed"
    set PF_key[7] = "hero_kills"
    set PF_label[8] = "Items gained"
    set PF_key[8] = "items"
    set PF_label[9] = "Mercenaries hired"
    set PF_key[9] = "mercs"
    set PF_label[10] = "Gold mined"
    set PF_key[10] = "mined"
    set PF_label[11] = "Gold mined with upkeep"
    set PF_key[11] = "gold_upkeep"
    set PF_label[12] = "Gold lost to upkeep"
    set PF_key[12] = "gold_lost"
    set PF_label[13] = "Gold lost to tax"
    set PF_key[13] = "gold_tax"
    set PF_label[14] = "Gold given (all trades)"
    set PF_key[14] = "given"
    set PF_label[15] = "Gold received (all trades)"
    set PF_key[15] = "received"
    set PF_label[16] = "Lumber harvested"
    set PF_key[16] = "lumber"
    set PF_label[17] = "Lumber lost to upkeep"
    set PF_key[17] = "lumber_lost"
    set PF_label[18] = "Lumber lost to tax"
    set PF_key[18] = "lumber_tax"
    set PF_label[19] = "Lumber given"
    set PF_key[19] = "lumber_given"
    set PF_label[20] = "Lumber received"
    set PF_key[20] = "lumber_received"
    set PF_label[21] = "Unit score"
    set PF_key[21] = "unit_score"
    set PF_label[22] = "Hero score"
    set PF_key[22] = "hero_score"
    set PF_label[23] = "Resource score"
    set PF_key[23] = "resource_score"
    set PF_label[24] = "Total score"
    set PF_key[24] = "score"
    set PF_label[25] = "Highest hero level"
    set PF_key[25] = "level"
    set PF_label[26] = "Unit kills"
    set PF_key[26] = "kills"
    set PF_label[27] = "Unit deaths"
    set PF_key[27] = "deaths"
    set PF_label[28] = "Assists"
    set PF_key[28] = "assists"
    set PF_label[29] = "Hero kills"
    set PF_key[29] = "h_kills"
    set PF_label[30] = "Hero deaths"
    set PF_key[30] = "h_deaths"
    set PF_label[31] = "Hill captures"
    set PF_key[31] = "caps"
    set PF_label[32] = "Buildings destroyed"
    set PF_key[32] = "buildings"
    set PF_label[33] = "Transmutes landed"
    set PF_key[33] = "transmutes"
    set PF_label[34] = "Damage dealt"
    set PF_key[34] = "damage"
    set PF_label[35] = "Structure damage"
    set PF_key[35] = "building_dmg"
    set PF_label[36] = "Damage taken"
    set PF_key[36] = "damage_in"
    set PF_label[37] = "Gold used (includes trades)"
    set PF_key[37] = "gold_out"
    set PF_label[38] = "Gold pooled"
    set PF_key[38] = "pool_out"
    set PF_label[39] = "Pooled gold received"
    set PF_key[39] = "pool_in"
    set PF_label[40] = "Transfers sent"
    set PF_key[40] = "sent_n"
    set PF_label[41] = "Transfers received"
    set PF_key[41] = "received_n"
    set PF_label[42] = "Average per transfer sent"
    set PF_key[42] = "avg_sent"
    set PF_label[43] = "Average per transfer received"
    set PF_key[43] = "avg_recv"
    set PF_label[44] = "Inheritance given"
    set PF_key[44] = "inherit_out"
    set PF_label[45] = "Inheritance received"
    set PF_key[45] = "inherit_in"
    set PF_label[46] = "Hill gold"
    set PF_key[46] = "hill_gold"
    set PF_label[47] = "Own units denied"
    set PF_key[47] = "denies"
    set PF_label[48] = "Allied units denied"
    set PF_key[48] = "ally_denies"
    set PF_label[49] = "Transmutes cast"
    set PF_key[49] = "tm_casts"
    set PF_label[50] = "Transmutes denied"
    set PF_key[50] = "tm_denied"
    set PF_label[51] = "Transmute saves"
    set PF_key[51] = "tm_saves"
    set PF_label[52] = "Creeps hired"
    set PF_key[52] = "creeps"
    set PF_label[53] = "Gold spent on creeps"
    set PF_key[53] = "creep_gold"
    set PF_label[54] = "Attack upgrade"
    set PF_key[54] = "atk"
    set PF_label[55] = "Defense upgrade"
    set PF_key[55] = "def"
    set PF_label[56] = "Race upgrade"
    set PF_key[56] = "race_level"
    set PF_label[57] = "Team research"
    set PF_key[57] = "team_research"
    set PF_label[58] = "Heroes fielded"
    set PF_key[58] = "heroes_used"
    set PF_label[59] = "Hero experience"
    set PF_key[59] = "hero_xp"
    set PF_label[60] = "Casino stakes placed"
    set PF_key[60] = "bets"
    set PF_label[61] = "Casino gold staked"
    set PF_key[61] = "staked"
    set PF_label[62] = "Casino gold returned"
    set PF_key[62] = "returns"
    set PF_label[63] = "Casino net (incl. open stakes)"
    set PF_key[63] = "net"
    set PF_label[64] = "Wallet"
    set PF_key[64] = "wallet"
    set PF_label[65] = "Match award (Wallet)"
    set PF_key[65] = "earned"
    set PF_label[66] = "Casino gold in play"
    set PF_key[66] = "escrow"
    set PF_label[67] = "Loan principal owed"
    set PF_key[67] = "loan"
    set PF_label[68] = "Loan fees owed"
    set PF_key[68] = "interest"
    set PF_label[69] = "Poker stakes"
    set PF_key[69] = "poker_stakes"
    set PF_label[70] = "Poker gold staked"
    set PF_key[70] = "poker_gold"
    set PF_label[71] = "Poker gold returned"
    set PF_key[71] = "poker_paid"
    set PF_label[72] = "Blackjack stakes"
    set PF_key[72] = "blackjack_stakes"
    set PF_label[73] = "Blackjack gold staked"
    set PF_key[73] = "blackjack_gold"
    set PF_label[74] = "Blackjack gold returned"
    set PF_key[74] = "blackjack_paid"
    set PF_label[75] = "Predictions stakes"
    set PF_key[75] = "predictions_stakes"
    set PF_label[76] = "Predictions gold staked"
    set PF_key[76] = "predictions_gold"
    set PF_label[77] = "Predictions gold returned"
    set PF_key[77] = "predictions_paid"
    set PF_label[78] = "Challenges stakes"
    set PF_key[78] = "challenges_stakes"
    set PF_label[79] = "Challenges gold staked"
    set PF_key[79] = "challenges_gold"
    set PF_label[80] = "Challenges gold returned"
    set PF_key[80] = "challenges_paid"
    set PF_columns[0] = 25
    set PF_columnTitle[0] = "Level"
    set PF_columns[1] = 24
    set PF_columnTitle[1] = "Score"
    set PF_columns[2] = 26
    set PF_columnTitle[2] = "Kills"
    set PF_columns[3] = 34
    set PF_columnTitle[3] = "Damage"
    set PF_columns[4] = 37
    set PF_columnTitle[4] = "Gold used"
    set PF_columns[5] = 21
    set PF_columnTitle[5] = "Unit score"
    set PF_columns[6] = 22
    set PF_columnTitle[6] = "Hero score"
    set PF_columns[7] = 23
    set PF_columnTitle[7] = "Resources"
    set PF_columns[8] = 24
    set PF_columnTitle[8] = "Total"
    set PF_columns[9] = 29
    set PF_columnTitle[9] = "Hero kills"
    set PF_columns[10] = 38
    set PF_columnTitle[10] = "Pooled"
    set PF_columns[11] = 39
    set PF_columnTitle[11] = "Received"
    set PF_columns[12] = 40
    set PF_columnTitle[12] = "Sends"
    set PF_columns[13] = 42
    set PF_columnTitle[13] = "Avg sent"
    set PF_columns[14] = 43
    set PF_columnTitle[14] = "Avg recv"
    set PF_columns[15] = 0
    set PF_columnTitle[15] = "Trained"
    set PF_columns[16] = 2
    set PF_columnTitle[16] = "Built"
    set PF_columns[17] = 3
    set PF_columnTitle[17] = "Razed"
    set PF_columns[18] = 8
    set PF_columnTitle[18] = "Items"
    set PF_columns[19] = 9
    set PF_columnTitle[19] = "Hired"
    set PF_columns[20] = 10
    set PF_columnTitle[20] = "Gold mined"
    set PF_columns[21] = 14
    set PF_columnTitle[21] = "Given"
    set PF_columns[22] = 15
    set PF_columnTitle[22] = "Received"
    set PF_columns[23] = 16
    set PF_columnTitle[23] = "Lumber"
    set PF_columns[24] = 12
    set PF_columnTitle[24] = "Upkeep"
    set PF_columns[25] = 27
    set PF_columnTitle[25] = "Deaths"
    set PF_columns[26] = 28
    set PF_columnTitle[26] = "Assists"
    set PF_columns[27] = 30
    set PF_columnTitle[27] = "Hero deaths"
    set PF_columns[28] = 31
    set PF_columnTitle[28] = "Hill caps"
    set PF_columns[29] = 36
    set PF_columnTitle[29] = "Dmg taken"
    set PF_columns[30] = 4
    set PF_columnTitle[30] = "Tech %"
    set PF_columns[31] = 5
    set PF_columnTitle[31] = "Peak supply"
    set PF_columns[32] = 6
    set PF_columnTitle[32] = "Food used"
    set PF_columns[33] = 1
    set PF_columnTitle[33] = "Units killed"
    set PF_columns[34] = 7
    set PF_columnTitle[34] = "Heroes killed"
    set PF_columns[35] = 11
    set PF_columnTitle[35] = "With upkeep"
    set PF_columns[36] = 13
    set PF_columnTitle[36] = "Gold tax"
    set PF_columns[37] = 17
    set PF_columnTitle[37] = "Wood upkeep"
    set PF_columns[38] = 18
    set PF_columnTitle[38] = "Wood tax"
    set PF_columns[39] = 19
    set PF_columnTitle[39] = "Wood given"
    set PF_columns[40] = 20
    set PF_columnTitle[40] = "Wood recv."
    set PF_columns[41] = 38
    set PF_columnTitle[41] = "Pooled"
    set PF_columns[42] = 39
    set PF_columnTitle[42] = "Received"
    set PF_columns[43] = 46
    set PF_columnTitle[43] = "Hill gold"
    set PF_columns[44] = 37
    set PF_columnTitle[44] = "Gold used"
    set PF_columns[45] = 58
    set PF_columnTitle[45] = "Heroes used"
    set PF_columns[46] = 59
    set PF_columnTitle[46] = "Hero XP"
    set PF_columns[47] = 25
    set PF_columnTitle[47] = "Level"
    set PF_columns[48] = 8
    set PF_columnTitle[48] = "Items gained"
    set PF_columns[49] = 9
    set PF_columnTitle[49] = "Mercenaries"
endfunction

function PF_Live takes integer s, integer k returns integer
    if k == 0 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_UNITS_TRAINED)
    elseif k == 1 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_UNITS_KILLED)
    elseif k == 2 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_STRUCT_BUILT)
    elseif k == 3 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_STRUCT_RAZED)
    elseif k == 4 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_TECH_PERCENT)
    elseif k == 5 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_FOOD_MAXPROD)
    elseif k == 6 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_FOOD_MAXUSED)
    elseif k == 7 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_HEROES_KILLED)
    elseif k == 8 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_ITEMS_GAINED)
    elseif k == 9 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_MERCS_HIRED)
    elseif k == 10 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_GOLD_MINED_TOTAL)
    elseif k == 11 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_GOLD_MINED_UPKEEP)
    elseif k == 12 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_GOLD_LOST_UPKEEP)
    elseif k == 13 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_GOLD_LOST_TAX)
    elseif k == 14 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_GOLD_GIVEN) + FF_st_poolOut[s]
    elseif k == 15 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_GOLD_RECEIVED) + FF_st_poolIn[s]
    elseif k == 16 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_LUMBER_TOTAL)
    elseif k == 17 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_LUMBER_LOST_UPKEEP)
    elseif k == 18 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_LUMBER_LOST_TAX)
    elseif k == 19 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_LUMBER_GIVEN)
    elseif k == 20 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_LUMBER_RECEIVED)
    elseif k == 21 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_UNIT_TOTAL)
    elseif k == 22 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_HERO_TOTAL)
    elseif k == 23 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_RESOURCE_TOTAL)
    elseif k == 24 then
        return GetPlayerScore(Player(s-1), PLAYER_SCORE_TOTAL)
    elseif k == 25 then
        return IMaxBJ(FF_st_heroLvl[s], GetHeroLevel(udg_herO[s]))
    elseif k == 26 then
        return udg_unit_kills[s]
    elseif k == 27 then
        return udg_unit_deaths[s]
    elseif k == 28 then
        return DPS_Assists[s]
    elseif k == 29 then
        return udg_hero_kills[s]
    elseif k == 30 then
        return udg_hero_deaths[s]
    elseif k == 31 then
        return DPS_Caps[s]
    elseif k == 32 then
        return DPS_Buildings[s]
    elseif k == 33 then
        return FF_st_tmHits[s]
    elseif k == 34 then
        return FF_st_dmg[s*3+FF_ST_DMG_OUT] + FF_st_dmg[s*3+FF_ST_DMG_BLD]
    elseif k == 35 then
        return FF_st_dmg[s*3+FF_ST_DMG_BLD]
    elseif k == 36 then
        return FF_st_dmg[s*3+FF_ST_DMG_IN]
    elseif k == 37 then
        return PF_recordedCost[s]
    elseif k == 38 then
        return FF_st_poolOut[s]
    elseif k == 39 then
        return FF_st_poolIn[s]
    elseif k == 40 then
        return PF_sent[s]
    elseif k == 41 then
        return PF_received[s]
    elseif k == 42 then
        return PF_Average(FF_st_poolOut[s], PF_sent[s])
    elseif k == 43 then
        return PF_Average(FF_st_poolIn[s], PF_received[s])
    elseif k == 44 then
        return FF_st_inhOut[s]
    elseif k == 45 then
        return FF_st_inhIn[s]
    elseif k == 46 then
        return FF_st_kothGold[s]
    elseif k == 47 then
        return FF_st_denyOwn[s]
    elseif k == 48 then
        return FF_st_denyAlly[s]
    elseif k == 49 then
        return FF_st_tmCasts[s]
    elseif k == 50 then
        return FF_st_tmDenied[s]
    elseif k == 51 then
        return FF_st_tmSaves[s]
    elseif k == 52 then
        return FF_st_creeps[s]
    elseif k == 53 then
        return FF_st_creepGold[s]
    elseif k == 54 then
        return FF_st_Tech(s, 'Rhme')
    elseif k == 55 then
        return FF_st_Tech(s, 'Rhar')
    elseif k == 56 then
        return FF_st_RaceLevel(s)
    elseif k == 57 then
        return FF_st_teamRes[s]
    elseif k == 58 then
        return PF_heroCount[s]
    elseif k == 59 then
        return PF_heroXP[s]
    elseif k == 60 then
        return PF_wagers[s]
    elseif k == 61 then
        return PF_staked[s]
    elseif k == 62 then
        return PF_returned[s]
    elseif k == 63 then
        return PF_returned[s]-PF_staked[s]
    elseif k == 64 then
        return WalletPublic[s-1]
    elseif k == 65 then
        return PF_rewards[s]
    elseif k == 66 then
        return CAS_escrow[s]
    elseif k == 67 then
        return LoanPrincipal[s]
    elseif k == 68 then
        return LoanFee[s]
    elseif k == 69 then
        return PF_gameBets[s*4+0]
    elseif k == 70 then
        return PF_gameStake[s*4+0]
    elseif k == 71 then
        return PF_gameReturn[s*4+0]
    elseif k == 72 then
        return PF_gameBets[s*4+1]
    elseif k == 73 then
        return PF_gameStake[s*4+1]
    elseif k == 74 then
        return PF_gameReturn[s*4+1]
    elseif k == 75 then
        return PF_gameBets[s*4+2]
    elseif k == 76 then
        return PF_gameStake[s*4+2]
    elseif k == 77 then
        return PF_gameReturn[s*4+2]
    elseif k == 78 then
        return PF_gameBets[s*4+3]
    elseif k == 79 then
        return PF_gameStake[s*4+3]
    elseif k == 80 then
        return PF_gameReturn[s*4+3]
    endif
    return 0
endfunction

function PF_Number takes integer s, integer k returns integer
    if PF_frozen then
        return LoadInteger(PF_final, s, k)
    endif
    return PF_Live(s,k)
endfunction

function PF_CasinoSlot takes integer s returns integer
    if s <= 12 and SoloSub_observerForPlayer[s] > 0 then
        return SoloSub_observerForPlayer[s]
    endif
    return s
endfunction

function PF_Category takes integer kind returns string
    if kind == 1 then
        return "hero"
    elseif kind == 2 then
        return "item"
    elseif kind == 3 then
        return "unit"
    endif
    return "skin"
endfunction

function PF_ExportJournal takes nothing returns nothing
    local integer s = PF_exportSlot
    local integer k = 1000+s*10
    local integer i = PF_exportStart
    local integer stop = IMinBJ(i+64,PF_logCount[s])
    loop
        exitwhen i >= stop
        call Preload("build,"+I2S(s)+","+I2S(i+1)+","+I2S(LoadInteger(PF_data,k+4,i))+","+LoadStr(PF_data,k,i)+","+I2S(LoadInteger(PF_data,k+1,i))+","+I2S(LoadInteger(PF_data,k+2,i))+","+I2S(LoadInteger(PF_data,k+3,i))+","+I2S(LoadInteger(PF_data,k+5,i)))
        set i = i+1
    endloop
endfunction

function PF_ExportSlot takes nothing returns nothing
    local integer s = PF_exportSlot
    local integer i = 0
    local integer kind = 1
    local integer k
    local integer id
    local string head = "profile,"+I2S(s)+","
    local string row = head
    local string field
    if not FF_gr_participant[s] then
        set i = PF_casinoFirst
    endif
    loop
        exitwhen i >= PF_metrics
        set field = PF_key[i]+"="+I2S(PF_Number(s,i))
        if StringLength(row)+StringLength(field)+1 > FF_PRELOAD_MAX then
            call Preload(row)
            set row = head
        endif
        if row != head then
            set row = row+","
        endif
        set row = row+field
        set i = i+1
    endloop
    call Preload(row)
    loop
        exitwhen kind > 4
        set k = s*10+kind
        set i = 0
        set head = "collection,"+I2S(s)+","+PF_Category(kind)+","
        set row = head
        loop
            exitwhen i >= PF_counts[k]
            set id = LoadInteger(PF_data,300+k,i)
            set field = FF_us_Id2S(id)+"="+I2S(LoadInteger(PF_data,k,id))
            if StringLength(row)+StringLength(field)+1 > FF_PRELOAD_MAX then
                call Preload(row)
                set row = head
            endif
            if row != head then
                set row = row+","
            endif
            set row = row+field
            set i = i+1
        endloop
        if row != head then
            call Preload(row)
        endif
        set kind = kind+1
    endloop
    set PF_exportStart = 0
    loop
        exitwhen PF_exportStart >= PF_logCount[s]
        call ExecuteFunc("PF_ExportJournal")
        set PF_exportStart = PF_exportStart+64
    endloop
endfunction

function PF_Export takes nothing returns nothing
    local integer account
    call Preload("casino,enabled=1,starting_wallet=1000")
    set PF_exportSlot = 1
    loop
        exitwhen PF_exportSlot > 24
        set account = PF_exportSlot-1
        if WalletKnown[account] or FF_gr_participant[PF_exportSlot] or PF_wagers[PF_exportSlot] > 0 or WalletPlayedSlot[account] > 0 then
            if WalletKnown[account] then
                call Preload("wallet,"+I2S(PF_exportSlot)+",known=1,opening="+I2S(WalletOpening[account])+",balance="+I2S(WalletPublic[account])+",starting_grant="+I2S(WalletStartingGrant[account]))
            else
                call Preload("wallet,"+I2S(PF_exportSlot)+",known=0")
            endif
            call Preload("profile_owner,"+I2S(PF_exportSlot)+","+FF_Sanitize(GetPlayerName(Player(PF_exportSlot-1)))+","+I2S(PF_CasinoSlot(PF_exportSlot)))
            call ExecuteFunc("PF_ExportSlot")
            call ExecuteFunc("PF_WriteCareer")
        endif
        set PF_exportSlot = PF_exportSlot+1
    endloop
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

function PF_OrderEvent takes nothing returns nothing
    local eventid e = GetTriggerEventId()
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local integer id
    local unit u
    if s > 12 then
        return
    endif
    if e == EVENT_PLAYER_UNIT_RESEARCH_START then
        set id = GetResearched()
        call PF_Purchase(s,"research_start",id,PF_Price(id,1+GetPlayerTechCount(Player(s-1),id,true)))
    elseif e == EVENT_PLAYER_UNIT_RESEARCH_CANCEL then
        call PF_Log(s,"research_cancel",GetResearched(),-1,0)
    elseif e == EVENT_PLAYER_UNIT_TRAIN_FINISH then
        set u = GetTrainedUnit()
        if IsUnitType(u,UNIT_TYPE_HERO) then
            call PF_Hero(s,u)
        else
            call PF_Use(s,3,GetUnitTypeId(u),1)
            call PF_Appearance(s,u,1)
        endif
        call PF_Log(s,"train",GetUnitTypeId(u),-1,0)
    elseif e == EVENT_PLAYER_UNIT_TRAIN_START then
        set id = GetTrainedUnitType()
        call PF_Purchase(s,"train_start",id,PF_Price(id,1))
    elseif e == EVENT_PLAYER_UNIT_TRAIN_CANCEL then
        call PF_Log(s,"train_cancel",GetTrainedUnitType(),-1,0)
    elseif e == EVENT_PLAYER_UNIT_CONSTRUCT_START then
        set id = GetUnitTypeId(GetConstructingStructure())
        call PF_Purchase(s,"construct_start",id,PF_Price(id,1))
    elseif e == EVENT_PLAYER_UNIT_CONSTRUCT_CANCEL then
        call PF_Log(s,"construct_cancel",GetUnitTypeId(GetCancelledStructure()),-1,0)
    else
        call PF_Log(s,"construct",GetUnitTypeId(GetConstructedStructure()),-1,0)
    endif
    set u = null
endfunction

function PF_InitOrders takes nothing returns nothing
    local trigger t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_RESEARCH_START)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_RESEARCH_CANCEL)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_TRAIN_START)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_TRAIN_FINISH)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_TRAIN_CANCEL)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_CONSTRUCT_START)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_CONSTRUCT_CANCEL)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_CONSTRUCT_FINISH)
    call TriggerAddAction(t,function PF_OrderEvent)
    set t = null
endfunction

function PF_ObjectData0 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'C049',100)
    call SaveInteger(PF_prices,1,'C050',300)
    call SaveInteger(PF_prices,1,'C051',325)
    call SaveInteger(PF_prices,1,'C052',325)
    call SaveInteger(PF_prices,1,'C053',350)
    call SaveInteger(PF_prices,1,'C054',350)
    call SaveInteger(PF_prices,1,'C055',350)
    call SaveInteger(PF_prices,1,'C056',325)
    call SaveInteger(PF_prices,1,'C057',100)
    call SaveInteger(PF_prices,1,'C058',275)
    call SaveInteger(PF_prices,1,'C059',250)
    call SaveInteger(PF_prices,1,'C060',300)
    call SaveInteger(PF_prices,1,'C061',325)
    call SaveInteger(PF_prices,1,'C062',250)
    call SaveInteger(PF_prices,1,'C063',225)
    call SaveInteger(PF_prices,1,'C064',275)
    call SaveInteger(PF_prices,1,'C065',275)
    call SaveInteger(PF_prices,1,'C066',300)
    call SaveInteger(PF_prices,1,'C067',350)
    call SaveInteger(PF_prices,1,'C068',325)
    call SaveInteger(PF_prices,1,'C069',375)
    call SaveInteger(PF_prices,1,'C070',375)
    call SaveInteger(PF_prices,1,'C071',300)
    call SaveInteger(PF_prices,1,'C072',300)
    call SaveInteger(PF_prices,1,'I000',150)
    call SaveInteger(PF_prices,1,'I001',0)
    call SaveStr(PF_prices,3,'I001',"ReplaceableTextures\\CommandButtons\\BTNHeartAmulet.blp")
    call SaveInteger(PF_prices,1,'I002',30000)
    call SaveInteger(PF_prices,1,'I003',2500)
    call SaveStr(PF_prices,3,'I003',"ReplaceableTextures\\CommandButtons\\BTNGoldClaw.blp")
    call SaveInteger(PF_prices,1,'I004',1500)
    call SaveStr(PF_prices,3,'I004',"ReplaceableTextures\\CommandButtons\\BTNRodofEnvy.blp")
    call SaveInteger(PF_prices,1,'I005',7500)
    call SaveStr(PF_prices,3,'I005',"ReplaceableTextures\\CommandButtons\\BTNStaffOfSanctuary.blp")
    call SaveInteger(PF_prices,1,'I006',1500)
    call SaveInteger(PF_prices,1,'I007',2500)
    call SaveInteger(PF_prices,1,'I008',1200)
    call SaveInteger(PF_prices,1,'I009',500)
    call SaveStr(PF_prices,3,'I009',"ReplaceableTextures\\CommandButtons\\BTNScepterOfMastery.blp")
    call SaveInteger(PF_prices,1,'I00A',2500)
    call SaveInteger(PF_prices,1,'I00B',1650)
    call SaveStr(PF_prices,3,'I00B',"ReplaceableTextures\\CommandButtons\\BTNImprovedUnholyStrength.blp")
    call SaveInteger(PF_prices,1,'I00C',500)
    call SaveStr(PF_prices,3,'I00C',"ReplaceableTextures\\CommandButtons\\BTNUsedSoulGem.blp")
    call SaveInteger(PF_prices,1,'I00D',600)
    call SaveStr(PF_prices,3,'I00D',"ReplaceableTextures\\CommandButtons\\BTNThoriumArmor.blp")
    call SaveInteger(PF_prices,1,'I00E',600)
    call SaveInteger(PF_prices,1,'I00F',650)
    call SaveInteger(PF_prices,1,'I00G',900)
    call SaveStr(PF_prices,3,'I00G',"ReplaceableTextures\\CommandButtons\\BTNSeigeEngineWithMissles.blp")
    call SaveInteger(PF_prices,1,'I00H',1250)
    call SaveStr(PF_prices,3,'I00H',"ReplaceableTextures\\CommandButtons\\BTNSkullWand.blp")
    call SaveInteger(PF_prices,1,'I00I',13000)
    call SaveInteger(PF_prices,1,'I00J',0)
    call SaveStr(PF_prices,3,'I00J',"ReplaceableTextures\\CommandButtons\\BTNEnergyPotion.blp")
    call SaveInteger(PF_prices,1,'I00K',950)
    call SaveStr(PF_prices,3,'I00K',"ReplaceableTextures\\CommandButtons\\BTNShamanMaster.blp")
    call SaveInteger(PF_prices,1,'I00L',1500)
    call SaveStr(PF_prices,3,'I00L',"ReplaceableTextures\\CommandButtons\\BTNGhostMage.blp")
    call SaveInteger(PF_prices,1,'I00M',1350)
    call SaveStr(PF_prices,3,'I00M',"ReplaceableTextures\\CommandButtons\\BTNWirtsLeg.blp")
    call SaveInteger(PF_prices,1,'I00N',600)
    call SaveStr(PF_prices,3,'I00N',"ReplaceableTextures\\CommandButtons\\BTNPriestAdept.blp")
    call SaveInteger(PF_prices,1,'I00O',1000)
    call SaveStr(PF_prices,3,'I00O',"ReplaceableTextures\\CommandButtons\\BTNGoldRing.blp")
    call SaveInteger(PF_prices,1,'I00P',2475)
    call SaveStr(PF_prices,3,'I00P',"ReplaceableTextures\\CommandButtons\\BTNAmuletOftheWild.blp")
    call SaveInteger(PF_prices,1,'I00Q',950)
    call SaveStr(PF_prices,3,'I00Q',"ReplaceableTextures\\PassiveButtons\\PASBTNElunesBlessing.blp")
    call SaveInteger(PF_prices,1,'I00R',5500)
    call SaveStr(PF_prices,3,'I00R',"ReplaceableTextures\\CommandButtons\\BTNAmuletOftheWild.blp")
    call SaveInteger(PF_prices,1,'I00S',950)
    call SaveStr(PF_prices,3,'I00S',"ReplaceableTextures\\CommandButtons\\BTNStaffOfPreservation.blp")
    call SaveInteger(PF_prices,1,'I00T',2750)
    call SaveStr(PF_prices,3,'I00T',"ReplaceableTextures\\PassiveButtons\\PASBTNElunesBlessing.blp")
    call SaveInteger(PF_prices,1,'I00U',2850)
    call SaveStr(PF_prices,3,'I00U',"ReplaceableTextures\\CommandButtons\\BTNWirtsLeg.blp")
    call SaveInteger(PF_prices,1,'I00V',2300)
    call SaveStr(PF_prices,3,'I00V',"ReplaceableTextures\\CommandButtons\\BTNGhostMage.blp")
    call SaveInteger(PF_prices,1,'I00W',4000)
    call SaveStr(PF_prices,3,'I00W',"ReplaceableTextures\\CommandButtons\\BTNShamanMaster.blp")
    call SaveInteger(PF_prices,1,'I00X',2500)
    call SaveStr(PF_prices,3,'I00X',"ReplaceableTextures\\CommandButtons\\BTNImprovedUnholyStrength.blp")
    call SaveInteger(PF_prices,1,'I00Y',1000)
    call SaveStr(PF_prices,3,'I00Y',"ReplaceableTextures\\CommandButtons\\BTNPriestAdept.blp")
    call SaveInteger(PF_prices,1,'I00Z',300)
    call SaveStr(PF_prices,3,'I00Z',"ReplaceableTextures\\CommandButtons\\BTNOrbOfDeath.blp")
    call SaveInteger(PF_prices,1,'I010',3000)
    call SaveStr(PF_prices,3,'I010',"ReplaceableTextures\\CommandButtons\\BTNStaffOfPreservation.blp")
    call SaveInteger(PF_prices,1,'I011',0)
    call SaveInteger(PF_prices,1,'I012',1050)
    call SaveStr(PF_prices,3,'I012',"ReplaceableTextures\\CommandButtons\\BTNOrbOfDeath.blp")
    call SaveInteger(PF_prices,1,'I013',0)
    call SaveStr(PF_prices,3,'I013',"ReplaceableTextures\\CommandButtons\\PASBTNEngineeringUpgrade.blp")
    call SaveInteger(PF_prices,1,'I014',0)
    call SaveStr(PF_prices,3,'I014',"ReplaceableTextures\\CommandButtons\\BTNMedalionOfCourage.blp")
    call SaveInteger(PF_prices,1,'I015',2500)
    call SaveStr(PF_prices,3,'I015',"ReplaceableTextures\\CommandButtons\\BTNRing_of_Roaring_Thunder.blp")
    call SaveInteger(PF_prices,1,'I016',0)
    call SaveStr(PF_prices,3,'I016',"ReplaceableTextures\\CommandButtons\\BTNMaskOfDeath.blp")
endfunction

function PF_ObjectData1 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'I017',500)
    call SaveInteger(PF_prices,1,'I018',0)
    call SaveInteger(PF_prices,1,'I019',0)
    call SaveInteger(PF_prices,1,'I01A',0)
    call SaveInteger(PF_prices,1,'I01B',0)
    call SaveInteger(PF_prices,1,'I01C',0)
    call SaveInteger(PF_prices,1,'I01D',10000)
    call SaveStr(PF_prices,3,'I01D',"ReplaceableTextures\\CommandButtons\\BTNOneRing.blp")
    call SaveInteger(PF_prices,1,'I01F',0)
    call SaveInteger(PF_prices,1,'I01G',75)
    call SaveStr(PF_prices,3,'I01G',"ReplaceableTextures\\CommandButtons\\BTNArcaniteArchitecture.blp")
    call SaveInteger(PF_prices,1,'I01H',2750)
    call SaveStr(PF_prices,3,'I01H',"ReplaceableTextures\\CommandButtons\\BTNfireStaff.blp")
    call SaveInteger(PF_prices,1,'I01I',1000)
    call SaveStr(PF_prices,3,'I01I',"ReplaceableTextures\\CommandButtons\\BTNfireStaff.blp")
    call SaveInteger(PF_prices,1,'I01J',0)
    call SaveInteger(PF_prices,1,'I01K',5000)
    call SaveStr(PF_prices,3,'I01K',"ReplaceableTextures\\CommandButtons\\BTNOneRing.blp")
    call SaveInteger(PF_prices,1,'I01L',0)
    call SaveStr(PF_prices,3,'I01L',"ReplaceableTextures\\CommandButtons\\BTNScrollOfTownPortal.blp")
    call SaveInteger(PF_prices,1,'I01M',0)
    call SaveStr(PF_prices,3,'I01M',"ReplaceableTextures\\CommandButtons\\BTNScrollOfTownPortal.blp")
    call SaveInteger(PF_prices,1,'I01N',0)
    call SaveStr(PF_prices,3,'I01N',"ReplaceableTextures\\CommandButtons\\BTNScrollOfTownPortal.blp")
    call SaveInteger(PF_prices,1,'I01O',15)
    call SaveStr(PF_prices,3,'I01O',"ReplaceableTextures\\CommandButtons\\BTNEnergyPotion.blp")
    call SaveInteger(PF_prices,1,'I01P',275)
    call SaveStr(PF_prices,3,'I01P',"ReplaceableTextures\\CommandButtons\\BTNGebo.BLP")
    call SaveInteger(PF_prices,1,'I01Q',1500)
    call SaveStr(PF_prices,3,'I01Q',"ReplaceableTextures\\CommandButtons\\BTNGlaringBeam.blp")
    call SaveInteger(PF_prices,1,'I01R',3500)
    call SaveStr(PF_prices,3,'I01R',"ReplaceableTextures\\CommandButtons\\BTNCoD.blp")
    call SaveInteger(PF_prices,1,'I01S',550)
    call SaveStr(PF_prices,3,'I01S',"ReplaceableTextures\\CommandButtons\\BTNCoD.blp")
    call SaveInteger(PF_prices,1,'I01T',0)
    call SaveStr(PF_prices,3,'I01T',"ReplaceableTextures\\CommandButtons\\BTNScrollOfTownPortal.blp")
    call SaveInteger(PF_prices,1,'I01U',0)
    call SaveStr(PF_prices,3,'I01U',"ReplaceableTextures\\CommandButtons\\BTNScrollOfTownPortal.blp")
    call SaveInteger(PF_prices,1,'I01V',0)
    call SaveStr(PF_prices,3,'I01V',"ReplaceableTextures\\CommandButtons\\BTNScrollOfTownPortal.blp")
    call SaveInteger(PF_prices,1,'I01W',0)
    call SaveStr(PF_prices,3,'I01W',"ReplaceableTextures\\CommandButtons\\BTNScrollOfTownPortal.blp")
    call SaveInteger(PF_prices,1,'I01X',0)
    call SaveStr(PF_prices,3,'I01X',"ReplaceableTextures\\CommandButtons\\BTNScrollOfTownPortal.blp")
    call SaveInteger(PF_prices,1,'I01Y',40)
    call SaveStr(PF_prices,3,'I01Y',"ReplaceableTextures\\CommandButtons\\BTNEnsnare.blp")
    call SaveInteger(PF_prices,1,'I01Z',10000)
    call SaveStr(PF_prices,3,'I01Z',"ReplaceableTextures\\CommandButtons\\BTNNobleSword.blp")
    call SaveInteger(PF_prices,1,'I020',200)
    call SaveStr(PF_prices,3,'I020',"ReplaceableTextures\\CommandButtons\\BTNMassTeleport.blp")
    call SaveInteger(PF_prices,1,'I021',200)
    call SaveStr(PF_prices,3,'I021',"ReplaceableTextures\\CommandButtons\\BTNScrollOfInferno.blp")
    call SaveInteger(PF_prices,1,'I022',450)
    call SaveStr(PF_prices,3,'I022',"ReplaceableTextures\\CommandButtons\\BTNPD3WizIllusion.BLP")
    call SaveInteger(PF_prices,1,'I023',0)
    call SaveInteger(PF_prices,1,'I024',1000)
    call SaveStr(PF_prices,3,'I024',"ReplaceableTextures\\CommandButtons\\BTN_CR_GREENstaf.blp")
    call SaveInteger(PF_prices,1,'I026',0)
    call SaveStr(PF_prices,3,'I026',"ReplaceableTextures\\CommandButtons\\BTNWarriorStrength.blp")
    call SaveInteger(PF_prices,1,'I027',0)
    call SaveInteger(PF_prices,1,'I028',0)
    call SaveInteger(PF_prices,1,'I029',0)
    call SaveInteger(PF_prices,1,'I02A',0)
    call SaveInteger(PF_prices,1,'I02B',0)
    call SaveInteger(PF_prices,1,'I02C',0)
    call SaveStr(PF_prices,3,'I02C',"ReplaceableTextures\\CommandButtons\\BTNStasisTrap.blp")
    call SaveInteger(PF_prices,1,'I02D',0)
    call SaveInteger(PF_prices,1,'I02E',0)
    call SaveInteger(PF_prices,1,'I02F',40)
    call SaveInteger(PF_prices,1,'I02G',0)
    call SaveInteger(PF_prices,1,'I02I',50)
    call SaveInteger(PF_prices,1,'I02J',400)
    call SaveStr(PF_prices,3,'I02J',"ReplaceableTextures\\CommandButtons\\BTNRing.blp")
    call SaveInteger(PF_prices,1,'I02K',0)
    call SaveStr(PF_prices,3,'I02K',"ReplaceableTextures\\CommandButtons\\BTNEnergyPotion.blp")
    call SaveInteger(PF_prices,1,'I02L',1100)
    call SaveStr(PF_prices,3,'I02L',"ReplaceableTextures\\CommandButtons\\BTNSpell_Nature_SpiritArmor.blp")
    call SaveInteger(PF_prices,1,'I02M',2100)
    call SaveStr(PF_prices,3,'I02M',"ReplaceableTextures\\CommandButtons\\BTNSpell_Nature_SpiritArmor.blp")
    call SaveInteger(PF_prices,1,'I02N',200)
    call SaveStr(PF_prices,3,'I02N',"ReplaceableTextures\\CommandButtons\\BTNSentryAmuletTier3.blp")
    call SaveInteger(PF_prices,1,'I02O',100)
    call SaveStr(PF_prices,3,'I02O',"ReplaceableTextures\\CommandButtons\\BTNAmulet.blp")
    call SaveInteger(PF_prices,1,'I02P',3000)
    call SaveStr(PF_prices,3,'I02P',"ReplaceableTextures\\CommandButtons\\BTNBerserkForTrolls.blp")
    call SaveInteger(PF_prices,1,'I02Q',0)
    call SaveInteger(PF_prices,1,'I02R',30)
    call SaveStr(PF_prices,3,'I02R',"ReplaceableTextures\\CommandButtons\\BTNGreaterInvisibility.blp")
    call SaveInteger(PF_prices,1,'I02S',600)
    call SaveInteger(PF_prices,1,'I02T',800)
    call SaveStr(PF_prices,3,'I02T',"ReplaceableTextures\\CommandButtons\\BTNPurify.blp")
    call SaveInteger(PF_prices,1,'I02U',950)
    call SaveStr(PF_prices,3,'I02U',"ReplaceableTextures\\CommandButtons\\BTNForkOfLightning.blp")
    call SaveInteger(PF_prices,1,'I02V',750)
    call SaveInteger(PF_prices,1,'I02W',350)
    call SaveStr(PF_prices,3,'I02W',"ReplaceableTextures\\CommandButtons\\BTNElemental Shield.blp")
    call SaveInteger(PF_prices,1,'I02X',100)
    call SaveStr(PF_prices,3,'I02X',"ReplaceableTextures\\CommandButtons\\BTNSentryAmuletTier3.blp")
    call SaveInteger(PF_prices,1,'I030',300)
    call SaveStr(PF_prices,3,'I030',"ReplaceableTextures\\CommandButtons\\BTNAmulet.blp")
endfunction

function PF_ObjectData2 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'I031',1000)
    call SaveStr(PF_prices,3,'I031',"ReplaceableTextures\\CommandButtons\\BTNElemental Shield.blp")
    call SaveInteger(PF_prices,1,'I033',5000)
    call SaveStr(PF_prices,3,'I033',"ReplaceableTextures\\CommandButtons\\BTNPenguin.blp")
    call SaveInteger(PF_prices,1,'I034',2000)
    call SaveInteger(PF_prices,1,'I03A',600)
    call SaveStr(PF_prices,3,'I03A',"ReplaceableTextures\\CommandButtons\\BTNCarrionSwarm1.blp")
    call SaveInteger(PF_prices,1,'I03C',250)
    call SaveInteger(PF_prices,1,'I03M',50)
    call SaveInteger(PF_prices,1,'I03N',1300)
    call SaveInteger(PF_prices,1,'I03P',200)
    call SaveInteger(PF_prices,1,'I03Q',0)
    call SaveStr(PF_prices,3,'I03Q',"ReplaceableTextures\\CommandButtons\\BTNBreathOfFrost.blp")
    call SaveInteger(PF_prices,1,'I03S',0)
    call SaveStr(PF_prices,3,'I03S',"ReplaceableTextures\\PassiveButtons\\PASBTNCriticalStrike.blp")
    call SaveInteger(PF_prices,1,'I03T',0)
    call SaveStr(PF_prices,3,'I03T',"ReplaceableTextures\\PassiveButtons\\PASBTNFeedBack.blp")
    call SaveInteger(PF_prices,1,'I03U',0)
    call SaveStr(PF_prices,3,'I03U',"ReplaceableTextures\\CommandButtons\\BTNWarStomp.blp")
    call SaveInteger(PF_prices,1,'I03X',300)
    call SaveInteger(PF_prices,1,'I03Y',500)
    call SaveStr(PF_prices,3,'I03Y',"ReplaceableTextures\\CommandButtons\\BTNMoonAmulet.blp")
    call SaveInteger(PF_prices,1,'I03Z',350)
    call SaveStr(PF_prices,3,'I03Z',"ReplaceableTextures\\CommandButtons\\BTNMoonAmulet.blp")
    call SaveInteger(PF_prices,1,'I040',300)
    call SaveInteger(PF_prices,1,'I042',1350)
    call SaveInteger(PF_prices,1,'I046',150)
    call SaveInteger(PF_prices,1,'I048',10000)
    call SaveStr(PF_prices,3,'I048',"ReplaceableTextures\\CommandButtons\\BTNNobleSword.blp")
    call SaveInteger(PF_prices,1,'I049',12000)
    call SaveInteger(PF_prices,1,'I04A',4000)
    call SaveStr(PF_prices,3,'I04A',"ReplaceableTextures\\CommandButtons\\BTNWindWalkOn.blp")
    call SaveInteger(PF_prices,1,'I04B',750)
    call SaveStr(PF_prices,3,'I04B',"ReplaceableTextures\\CommandButtons\\BTNWindWalkOn.blp")
    call SaveInteger(PF_prices,1,'ICPP',0)
    call SaveStr(PF_prices,3,'ICPP',"ReplaceableTextures\\WorldEditUI\\Editor-Ally-HighPriority.blp")
    call SaveInteger(PF_prices,1,'IGs1',6000)
    call SaveStr(PF_prices,3,'IGs1',"ReplaceableTextures\\CommandButtons\\BTNSilence.blp")
    call SaveInteger(PF_prices,1,'IRb0',42)
    call SaveInteger(PF_prices,1,'V073',750)
    call SaveInteger(PF_prices,1,'V074',700)
    call SaveInteger(PF_prices,1,'V075',700)
    call SaveInteger(PF_prices,1,'V076',700)
    call SaveInteger(PF_prices,1,'V077',750)
    call SaveInteger(PF_prices,1,'V078',650)
    call SaveInteger(PF_prices,1,'V079',650)
    call SaveInteger(PF_prices,1,'V080',800)
    call SaveInteger(PF_prices,1,'V081',800)
    call SaveInteger(PF_prices,1,'V082',800)
    call SaveInteger(PF_prices,1,'V083',850)
    call SaveInteger(PF_prices,1,'V084',650)
    call SaveInteger(PF_prices,1,'V085',650)
    call SaveInteger(PF_prices,1,'V086',700)
    call SaveInteger(PF_prices,1,'V087',800)
    call SaveInteger(PF_prices,1,'V088',750)
    call SaveInteger(PF_prices,1,'V089',800)
    call SaveInteger(PF_prices,1,'V090',800)
    call SaveInteger(PF_prices,1,'V091',700)
    call SaveInteger(PF_prices,1,'V092',750)
    call SaveInteger(PF_prices,1,'V093',750)
    call SaveInteger(PF_prices,1,'V094',700)
    call SaveInteger(PF_prices,1,'V095',750)
    call SaveInteger(PF_prices,1,'V096',850)
    call SaveInteger(PF_prices,1,'X025',325)
    call SaveInteger(PF_prices,1,'X026',350)
    call SaveInteger(PF_prices,1,'X027',275)
    call SaveInteger(PF_prices,1,'X028',300)
    call SaveInteger(PF_prices,1,'X029',325)
    call SaveInteger(PF_prices,1,'X030',250)
    call SaveInteger(PF_prices,1,'X031',350)
    call SaveInteger(PF_prices,1,'X032',250)
    call SaveInteger(PF_prices,1,'X033',300)
    call SaveInteger(PF_prices,1,'X034',300)
    call SaveInteger(PF_prices,1,'X035',350)
    call SaveInteger(PF_prices,1,'X036',275)
    call SaveInteger(PF_prices,1,'X037',300)
    call SaveInteger(PF_prices,1,'X038',350)
    call SaveInteger(PF_prices,1,'X039',325)
    call SaveInteger(PF_prices,1,'X040',100)
    call SaveInteger(PF_prices,1,'X041',325)
    call SaveInteger(PF_prices,1,'X042',350)
    call SaveInteger(PF_prices,1,'X043',350)
    call SaveInteger(PF_prices,1,'X044',375)
    call SaveInteger(PF_prices,1,'X045',275)
    call SaveInteger(PF_prices,1,'X046',300)
    call SaveInteger(PF_prices,1,'X047',275)
    call SaveInteger(PF_prices,1,'X048',350)
    call SaveInteger(PF_prices,1,'Z001',325)
    call SaveInteger(PF_prices,1,'Z002',300)
    call SaveInteger(PF_prices,1,'Z003',325)
    call SaveInteger(PF_prices,1,'Z004',375)
    call SaveInteger(PF_prices,1,'Z005',325)
    call SaveInteger(PF_prices,1,'Z006',300)
    call SaveInteger(PF_prices,1,'Z007',325)
    call SaveInteger(PF_prices,1,'Z008',275)
    call SaveInteger(PF_prices,1,'Z009',100)
    call SaveInteger(PF_prices,1,'Z010',500)
    call SaveInteger(PF_prices,1,'Z011',350)
    call SaveInteger(PF_prices,1,'Z012',300)
    call SaveInteger(PF_prices,1,'Z013',275)
endfunction

function PF_ObjectData3 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'Z014',325)
    call SaveInteger(PF_prices,1,'Z015',150)
    call SaveInteger(PF_prices,1,'Z016',100)
    call SaveInteger(PF_prices,1,'Z017',350)
    call SaveInteger(PF_prices,1,'Z018',100)
    call SaveInteger(PF_prices,1,'Z019',250)
    call SaveInteger(PF_prices,1,'Z020',250)
    call SaveInteger(PF_prices,1,'Z021',225)
    call SaveInteger(PF_prices,1,'Z022',300)
    call SaveInteger(PF_prices,1,'Z023',325)
    call SaveInteger(PF_prices,1,'Z024',225)
    call SaveStr(PF_prices,3,'amrc',"ReplaceableTextures\\CommandButtons\\BTNMassTeleport.blp")
    call SaveInteger(PF_prices,1,'ankh',700)
    call SaveInteger(PF_prices,1,'belv',300)
    call SaveInteger(PF_prices,1,'bgst',250)
    call SaveInteger(PF_prices,1,'brac',1000)
    call SaveInteger(PF_prices,1,'ches',0)
    call SaveInteger(PF_prices,1,'ciri',100)
    call SaveInteger(PF_prices,1,'ckng',500)
    call SaveInteger(PF_prices,1,'clfm',800)
    call SaveInteger(PF_prices,1,'clsd',25)
    call SaveInteger(PF_prices,1,'cnob',3250)
    call SaveInteger(PF_prices,1,'crys',200)
    call SaveInteger(PF_prices,1,'desc',1500)
    call SaveInteger(PF_prices,1,'dust',0)
    call SaveInteger(PF_prices,1,'evtl',350)
    call SaveInteger(PF_prices,1,'frhg',800)
    call SaveInteger(PF_prices,1,'gobm',125)
    call SaveStr(PF_prices,3,'gobm',"ReplaceableTextures\\CommandButtons\\BTNStasisTrap.blp")
    call SaveInteger(PF_prices,1,'gold',100)
    call SaveInteger(PF_prices,1,'hlst',150)
    call SaveInteger(PF_prices,1,'hslv',0)
    call SaveStr(PF_prices,3,'hslv',"ReplaceableTextures\\CommandButtons\\BTNEnergyPotion.blp")
    call SaveInteger(PF_prices,1,'hval',400)
    call SaveInteger(PF_prices,1,'infs',1000)
    call SaveInteger(PF_prices,1,'lgdh',450)
    call SaveInteger(PF_prices,1,'lhst',500)
    call SaveInteger(PF_prices,1,'lmbr',2000)
    call SaveInteger(PF_prices,1,'mcou',150)
    call SaveInteger(PF_prices,1,'mnst',150)
    call SaveInteger(PF_prices,1,'modt',300)
    call SaveInteger(PF_prices,1,'nams',50)
    call SaveInteger(PF_prices,1,'nspi',12000)
    call SaveInteger(PF_prices,1,'ofro',200)
    call SaveInteger(PF_prices,1,'olig',400)
    call SaveInteger(PF_prices,1,'oven',300)
    call SaveInteger(PF_prices,1,'pams',50)
    call SaveInteger(PF_prices,1,'pclr',50)
    call SaveStr(PF_prices,3,'pclr',"ReplaceableTextures\\CommandButtons\\BTNLesserClarityPotion.blp")
    call SaveInteger(PF_prices,1,'penr',350)
    call SaveInteger(PF_prices,1,'pghe',100)
    call SaveInteger(PF_prices,1,'pgma',100)
    call SaveInteger(PF_prices,1,'pinv',0)
    call SaveInteger(PF_prices,1,'pmna',300)
    call SaveInteger(PF_prices,1,'pnvl',150)
    call SaveInteger(PF_prices,1,'pnvu',250)
    call SaveInteger(PF_prices,1,'pres',200)
    call SaveInteger(PF_prices,1,'prvt',500)
    call SaveInteger(PF_prices,1,'rag1',2750)
    call SaveInteger(PF_prices,1,'rat6',1500)
    call SaveStr(PF_prices,3,'rat6',"ReplaceableTextures\\CommandButtons\\BTNForkOfLightning.blp")
    call SaveInteger(PF_prices,1,'rat9',800)
    call SaveStr(PF_prices,3,'rat9',"ReplaceableTextures\\CommandButtons\\BTNKatana.blp")
    call SaveInteger(PF_prices,1,'ratf',300)
    call SaveInteger(PF_prices,1,'rde3',200)
    call SaveInteger(PF_prices,1,'rhe2',0)
    call SaveInteger(PF_prices,1,'rhth',1200)
    call SaveInteger(PF_prices,1,'rin1',1200)
    call SaveInteger(PF_prices,1,'rlif',100)
    call SaveInteger(PF_prices,1,'rre2',0)
    call SaveInteger(PF_prices,1,'rst1',2000)
    call SaveInteger(PF_prices,1,'rwiz',100)
    call SaveInteger(PF_prices,1,'sand',2500)
    call SaveInteger(PF_prices,1,'sbch',500)
    call SaveInteger(PF_prices,1,'shas',50)
    call SaveInteger(PF_prices,1,'sman',75)
    call SaveInteger(PF_prices,1,'spre',900)
    call SaveInteger(PF_prices,1,'spro',400)
    call SaveInteger(PF_prices,1,'sreg',50)
    call SaveInteger(PF_prices,1,'sres',225)
    call SaveStr(PF_prices,3,'sres',"ReplaceableTextures\\CommandButtons\\BTNScrollOfTownPortal.blp")
    call SaveInteger(PF_prices,1,'sror',400)
    call SaveInteger(PF_prices,1,'srrc',2500)
    call SaveInteger(PF_prices,1,'ssil',75)
    call SaveInteger(PF_prices,1,'stel',250)
    call SaveInteger(PF_prices,1,'stwa',800)
    call SaveStr(PF_prices,3,'stwa',"ReplaceableTextures\\CommandButtons\\BTNHornedSword.blp")
    call SaveInteger(PF_prices,1,'stwp',0)
    call SaveInteger(PF_prices,1,'tcas',125)
    call SaveStr(PF_prices,3,'tcas',"ReplaceableTextures\\CommandButtons\\BTNRWall.blp")
    call SaveInteger(PF_prices,1,'tgrh',125)
    call SaveStr(PF_prices,3,'tgrh',"ReplaceableTextures\\CommandButtons\\BTNLWall.blp")
    call SaveInteger(PF_prices,1,'tgxp',1000)
    call SaveInteger(PF_prices,1,'tkno',1250)
    call SaveInteger(PF_prices,1,'tmmt',600)
    call SaveInteger(PF_prices,1,'tret',100)
    call SaveInteger(PF_prices,1,'ward',500)
    call SaveInteger(PF_prices,1,'whwd',250)
    call SaveInteger(PF_prices,1,'will',40)
    call SaveInteger(PF_prices,1,'wneg',450)
endfunction

function PF_ObjectData4 takes nothing returns nothing
    call SaveStr(PF_prices,3,'wneg',"ReplaceableTextures\\CommandButtons\\BTNRodOfNecromancy.blp")
    call SaveInteger(PF_prices,1,'wswd',75)
    call SaveInteger(PF_prices,1,'E002',0)
    call SaveInteger(PF_prices,1,'E003',0)
    call SaveInteger(PF_prices,1,'E005',0)
    call SaveInteger(PF_prices,1,'E007',0)
    call SaveInteger(PF_prices,1,'E008',0)
    call SaveStr(PF_prices,3,'E008',"ReplaceableTextures\\CommandButtons\\BTNPenguin.blp")
    call SaveInteger(PF_prices,1,'E00A',0)
    call SaveStr(PF_prices,3,'E00A',"ReplaceableTextures\\CommandButtons\\BTNFacelessOne.blp")
    call SaveInteger(PF_prices,1,'E00E',0)
    call SaveStr(PF_prices,3,'E00E',"ReplaceableTextures\\CommandButtons\\BTNHellScream.blp")
    call SaveInteger(PF_prices,1,'E00F',0)
    call SaveInteger(PF_prices,1,'E00O',0)
    call SaveStr(PF_prices,3,'E00O',"ReplaceableTextures\\CommandButtons\\BTNSatyr.blp")
    call SaveInteger(PF_prices,1,'E00P',0)
    call SaveStr(PF_prices,3,'E00P',"ReplaceableTextures\\CommandButtons\\BTNShips_Doctor_Kul-Tiras_HD.blp")
    call SaveInteger(PF_prices,1,'E00T',0)
    call SaveStr(PF_prices,3,'E00T',"ReplaceableTextures\\CommandButtons\\BTNBanditMage.blp")
    call SaveInteger(PF_prices,1,'E00U',0)
    call SaveStr(PF_prices,3,'E00U',"ReplaceableTextures\\CommandButtons\\BTNShandris.blp")
    call SaveInteger(PF_prices,1,'E00V',0)
    call SaveInteger(PF_prices,1,'E00Y',0)
    call SaveStr(PF_prices,3,'E00Y',"ReplaceableTextures\\CommandButtons\\BTNStormforgerIcon.blp")
    call SaveInteger(PF_prices,1,'E00Z',0)
    call SaveStr(PF_prices,3,'E00Z',"ReplaceableTextures\\CommandButtons\\BTNDranaiAkama.blp")
    call SaveInteger(PF_prices,1,'E010',0)
    call SaveStr(PF_prices,3,'E010',"ReplaceableTextures\\CommandButtons\\BTNBlackTemplar.blp")
    call SaveInteger(PF_prices,1,'E011',0)
    call SaveStr(PF_prices,3,'E011',"ReplaceableTextures\\CommandButtons\\BTNratling.blp")
    call SaveInteger(PF_prices,1,'E018',0)
    call SaveStr(PF_prices,3,'E018',"ReplaceableTextures\\CommandButtons\\BTNJunkGolem.blp")
    call SaveInteger(PF_prices,1,'E01G',0)
    call SaveStr(PF_prices,3,'E01G',"ReplaceableTextures\\CommandButtons\\BTNHellScream.blp")
    call SaveInteger(PF_prices,1,'H005',0)
    call SaveInteger(PF_prices,1,'H008',0)
    call SaveInteger(PF_prices,1,'H009',0)
    call SaveInteger(PF_prices,1,'H00A',0)
    call SaveInteger(PF_prices,1,'H00E',0)
    call SaveStr(PF_prices,3,'H00E',"ReplaceableTextures\\CommandButtons\\BTNSpiritWalker.blp")
    call SaveInteger(PF_prices,1,'H00K',0)
    call SaveStr(PF_prices,3,'H00K',"ReplaceableTextures\\CommandButtons\\BTNSpiritWalker.blp")
    call SaveInteger(PF_prices,1,'H00T',0)
    call SaveInteger(PF_prices,1,'H00U',0)
    call SaveStr(PF_prices,3,'H00U',"ReplaceableTextures\\CommandButtons\\BTNSheep.blp")
    call SaveInteger(PF_prices,1,'H015',0)
    call SaveStr(PF_prices,3,'H015',"ReplaceableTextures\\CommandButtons\\BTNPestilantPrince.blp")
    call SaveInteger(PF_prices,1,'H01B',0)
    call SaveStr(PF_prices,3,'H01B',"ReplaceableTextures\\CommandButtons\\BTNRevenant.blp")
    call SaveInteger(PF_prices,1,'H01F',0)
    call SaveStr(PF_prices,3,'H01F',"ReplaceableTextures\\CommandButtons\\BTNFemaleCaptain.blp")
    call SaveInteger(PF_prices,1,'H01H',0)
    call SaveStr(PF_prices,3,'H01H',"ReplaceableTextures\\CommandButtons\\BTNHydralisk.blp")
    call SaveInteger(PF_prices,1,'H01I',0)
    call SaveInteger(PF_prices,1,'H01R',0)
    call SaveStr(PF_prices,3,'H01R',"ReplaceableTextures\\CommandButtons\\BTNKelThuzad.blp")
    call SaveInteger(PF_prices,1,'H01U',0)
    call SaveStr(PF_prices,3,'H01U',"ReplaceableTextures\\CommandButtons\\BTNChaosGrunt.blp")
    call SaveInteger(PF_prices,1,'H02C',0)
    call SaveStr(PF_prices,3,'H02C',"ReplaceableTextures\\CommandButtons\\BTNthrall_foot.blp")
    call SaveInteger(PF_prices,1,'H02D',0)
    call SaveInteger(PF_prices,1,'H02E',0)
    call SaveInteger(PF_prices,1,'H02G',0)
    call SaveStr(PF_prices,3,'H02G',"ReplaceableTextures\\CommandButtons\\BTNProudMoore.blp")
    call SaveInteger(PF_prices,1,'H02I',0)
    call SaveStr(PF_prices,3,'H02I',"ReplaceableTextures\\CommandButtons\\BTNWendigo.blp")
    call SaveInteger(PF_prices,1,'H02J',0)
    call SaveStr(PF_prices,3,'H02J',"ReplaceableTextures\\CommandButtons\\BTNFelGuard.blp")
    call SaveInteger(PF_prices,1,'H02R',0)
    call SaveStr(PF_prices,3,'H02R',"ReplaceableTextures\\CommandButtons\\BTNCloak.blp")
    call SaveInteger(PF_prices,1,'H02W',0)
    call SaveStr(PF_prices,3,'H02W',"ReplaceableTextures\\CommandButtons\\BTNChaosSpaceOrc.blp")
    call SaveInteger(PF_prices,1,'H02Z',0)
    call SaveStr(PF_prices,3,'H02Z',"ReplaceableTextures\\CommandButtons\\BTNMarine.blp")
    call SaveInteger(PF_prices,1,'H036',0)
    call SaveStr(PF_prices,3,'H036',"ReplaceableTextures\\CommandButtons\\BTNRifleman Lordaeron.blp")
    call SaveInteger(PF_prices,1,'H03I',0)
    call SaveStr(PF_prices,3,'H03I',"ReplaceableTextures\\CommandButtons\\BTNdragonpriest.blp")
    call SaveInteger(PF_prices,1,'H03N',0)
    call SaveStr(PF_prices,3,'H03N',"ReplaceableTextures\\CommandButtons\\BTNBattlepriest.blp")
    call SaveInteger(PF_prices,1,'H03Q',0)
    call SaveStr(PF_prices,3,'H03Q',"ReplaceableTextures\\CommandButtons\\BTNWolf.blp")
    call SaveInteger(PF_prices,1,'H03U',0)
    call SaveStr(PF_prices,3,'H03U',"ReplaceableTextures\\CommandButtons\\BTNRayofHope.blp")
    call SaveInteger(PF_prices,1,'H043',0)
    call SaveStr(PF_prices,3,'H043',"ReplaceableTextures\\CommandButtons\\BTNGenericProtoss.blp")
    call SaveInteger(PF_prices,1,'H048',0)
    call SaveStr(PF_prices,3,'H048',"ReplaceableTextures\\CommandButtons\\BTNMountainKing.blp")
    call SaveInteger(PF_prices,1,'H04F',0)
    call SaveStr(PF_prices,3,'H04F',"ReplaceableTextures\\CommandButtons\\BTNdog.blp")
    call SaveInteger(PF_prices,1,'H04T',0)
    call SaveStr(PF_prices,3,'H04T',"ReplaceableTextures\\CommandButtons\\BTNHeroKingTerenas.blp")
    call SaveInteger(PF_prices,1,'H04U',0)
    call SaveStr(PF_prices,3,'H04U',"ReplaceableTextures\\CommandButtons\\BTNMedivh.blp")
    call SaveInteger(PF_prices,1,'H04W',0)
    call SaveStr(PF_prices,3,'H04W',"ReplaceableTextures\\CommandButtons\\BTNDeadeye.BLP")
    call SaveInteger(PF_prices,1,'H04X',0)
    call SaveStr(PF_prices,3,'H04X',"ReplaceableTextures\\CommandButtons\\BTNNerubianQueen.blp")
    call SaveInteger(PF_prices,1,'H04Y',0)
    call SaveStr(PF_prices,3,'H04Y',"ReplaceableTextures\\CommandButtons\\BTNWitchDoctor.blp")
endfunction

function PF_ObjectData5 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'H05E',0)
    call SaveStr(PF_prices,3,'H05E',"ReplaceableTextures\\CommandButtons\\BTNPestilantPrince.blp")
    call SaveInteger(PF_prices,1,'H05N',0)
    call SaveStr(PF_prices,3,'H05N',"ReplaceableTextures\\CommandButtons\\BTNWitchDoctor.blp")
    call SaveInteger(PF_prices,1,'H0R0',0)
    call SaveStr(PF_prices,3,'H0R0',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'HDk1',0)
    call SaveStr(PF_prices,3,'HDk1',"ReplaceableTextures\\CommandButtons\\BTNChaosGrom.blp")
    call SaveInteger(PF_prices,1,'HGr1',0)
    call SaveStr(PF_prices,3,'HGr1',"ReplaceableTextures\\CommandButtons\\BTNFireBrewmaster.tga")
    call SaveInteger(PF_prices,1,'HMu1',0)
    call SaveStr(PF_prices,3,'HMu1',"ReplaceableTextures\\CommandButtons\\BTNAbomination.blp")
    call SaveInteger(PF_prices,1,'HOr1',0)
    call SaveStr(PF_prices,3,'HOr1',"ReplaceableTextures\\CommandButtons\\BTNGuldan.blp")
    call SaveInteger(PF_prices,1,'HTf1',0)
    call SaveStr(PF_prices,3,'HTf1',"ReplaceableTextures\\CommandButtons\\BTNTwistedFate.tga")
    call SaveInteger(PF_prices,1,'HVg1',0)
    call SaveStr(PF_prices,3,'HVg1',"ReplaceableTextures\\CommandButtons\\BTNVeigarHero.blp")
    call SaveInteger(PF_prices,1,'N00C',0)
    call SaveInteger(PF_prices,1,'N00D',0)
    call SaveInteger(PF_prices,1,'N00H',0)
    call SaveStr(PF_prices,3,'N00H',"ReplaceableTextures\\CommandButtons\\BTNSylvanasWindrunner.blp")
    call SaveInteger(PF_prices,1,'N00I',0)
    call SaveInteger(PF_prices,1,'N00N',0)
    call SaveStr(PF_prices,3,'N00N',"ReplaceableTextures\\CommandButtons\\BTNArchimonde.blp")
    call SaveInteger(PF_prices,1,'N00O',0)
    call SaveStr(PF_prices,3,'N00O',"ReplaceableTextures\\CommandButtons\\BTNMountainGiant.blp")
    call SaveInteger(PF_prices,1,'N00P',0)
    call SaveInteger(PF_prices,1,'N00Z',0)
    call SaveInteger(PF_prices,1,'N015',0)
    call SaveStr(PF_prices,3,'N015',"ReplaceableTextures\\CommandButtons\\BTNHighElvenArcher.blp")
    call SaveInteger(PF_prices,1,'N01C',0)
    call SaveInteger(PF_prices,1,'N01D',0)
    call SaveInteger(PF_prices,1,'N01L',0)
    call SaveStr(PF_prices,3,'N01L',"ReplaceableTextures\\CommandButtons\\BTNSatyrTrickster.blp")
    call SaveInteger(PF_prices,1,'N027',0)
    call SaveStr(PF_prices,3,'N027',"ReplaceableTextures\\CommandButtons\\BTNGhostMage.blp")
    call SaveInteger(PF_prices,1,'N02O',0)
    call SaveStr(PF_prices,3,'N02O',"ReplaceableTextures\\CommandButtons\\BTNNagaMyrmidonRoyalGuard.blp")
    call SaveInteger(PF_prices,1,'N035',0)
    call SaveStr(PF_prices,3,'N035',"ReplaceableTextures\\CommandButtons\\BTNwarrior.blp")
    call SaveInteger(PF_prices,1,'N03B',0)
    call SaveStr(PF_prices,3,'N03B',"ReplaceableTextures\\CommandButtons\\BTNNecro.blp")
    call SaveInteger(PF_prices,1,'N03J',0)
    call SaveStr(PF_prices,3,'N03J',"ReplaceableTextures\\CommandButtons\\BTNEmberKnight.blp")
    call SaveInteger(PF_prices,1,'N05H',0)
    call SaveInteger(PF_prices,1,'O000',0)
    call SaveStr(PF_prices,3,'O000',"ReplaceableTextures\\CommandButtons\\BTNChaosWarlord.blp")
    call SaveInteger(PF_prices,1,'O003',0)
    call SaveInteger(PF_prices,1,'O004',0)
    call SaveInteger(PF_prices,1,'O005',0)
    call SaveInteger(PF_prices,1,'O006',0)
    call SaveInteger(PF_prices,1,'O008',0)
    call SaveStr(PF_prices,3,'O008',"ReplaceableTextures\\CommandButtons\\BTNDoomGuard.blp")
    call SaveInteger(PF_prices,1,'O00D',0)
    call SaveInteger(PF_prices,1,'O00G',0)
    call SaveStr(PF_prices,3,'O00G',"ReplaceableTextures\\CommandButtons\\BTNChaosBlademaster.blp")
    call SaveInteger(PF_prices,1,'O00I',0)
    call SaveStr(PF_prices,3,'O00I',"ReplaceableTextures\\CommandButtons\\BTNIceShard.blp")
    call SaveInteger(PF_prices,1,'O00O',0)
    call SaveStr(PF_prices,3,'O00O',"ReplaceableTextures\\CommandButtons\\BTNBaldie.blp")
    call SaveInteger(PF_prices,1,'O00T',0)
    call SaveStr(PF_prices,3,'O00T',"ReplaceableTextures\\CommandButtons\\BTNassasin_noob.blp")
    call SaveInteger(PF_prices,1,'O00X',0)
    call SaveStr(PF_prices,3,'O00X',"ReplaceableTextures\\CommandButtons\\BTNTigerLook.blp")
    call SaveInteger(PF_prices,1,'O010',0)
    call SaveStr(PF_prices,3,'O010',"ReplaceableTextures\\CommandButtons\\BTNHeroFemaleNecromancer.blp")
    call SaveInteger(PF_prices,1,'O016',0)
    call SaveStr(PF_prices,3,'O016',"ReplaceableTextures\\CommandButtons\\BTNTrollConjurer.blp")
    call SaveInteger(PF_prices,1,'O01B',0)
    call SaveStr(PF_prices,3,'O01B',"ReplaceableTextures\\CommandButtons\\BTNmonkeyking1.blp")
    call SaveInteger(PF_prices,1,'O01L',0)
    call SaveStr(PF_prices,3,'O01L',"ReplaceableTextures\\CommandButtons\\BTNSeaGiant.blp")
    call SaveInteger(PF_prices,1,'U002',0)
    call SaveInteger(PF_prices,1,'U003',0)
    call SaveInteger(PF_prices,1,'U004',0)
    call SaveInteger(PF_prices,1,'U005',0)
    call SaveInteger(PF_prices,1,'U00F',0)
    call SaveStr(PF_prices,3,'U00F',"ReplaceableTextures\\CommandButtons\\BTNSanta.blp")
    call SaveInteger(PF_prices,1,'U00R',0)
    call SaveStr(PF_prices,3,'U00R',"ReplaceableTextures\\CommandButtons\\BTNWight.blp")
    call SaveInteger(PF_prices,1,'abom',150)
    call SaveStr(PF_prices,3,'abom',"ReplaceableTextures\\CommandButtons\\BTNSkeletonWarrior.blp")
    call SaveStr(PF_prices,3,'dmmy',"ReplaceableTextures\\CommandButtons\\BTNMagicalSentry.blp")
    call SaveInteger(PF_prices,1,'e004',400)
    call SaveStr(PF_prices,3,'e004',"ReplaceableTextures\\CommandButtons\\BTNDryad.blp")
    call SaveInteger(PF_prices,1,'e00D',5)
    call SaveInteger(PF_prices,1,'e00G',2250)
    call SaveInteger(PF_prices,1,'e00H',250)
    call SaveStr(PF_prices,3,'e00H',"ReplaceableTextures\\CommandButtons\\BTNDruidOfTheTalon.blp")
    call SaveInteger(PF_prices,1,'e00I',300)
    call SaveStr(PF_prices,3,'e00I',"ReplaceableTextures\\CommandButtons\\BTNDryad.blp")
    call SaveStr(PF_prices,3,'e00Q',"ReplaceableTextures\\CommandButtons\\BTNdeathwing.blp")
    call SaveStr(PF_prices,3,'e00W',"ReplaceableTextures\\CommandButtons\\BTNdeathwing.blp")
    call SaveStr(PF_prices,3,'e00X',"ReplaceableTextures\\CommandButtons\\BTNdeathwing.blp")
    call SaveInteger(PF_prices,1,'e013',400)
    call SaveInteger(PF_prices,1,'earc',170)
    call SaveInteger(PF_prices,1,'emow',200)
    call SaveInteger(PF_prices,1,'esen',220)
    call SaveInteger(PF_prices,1,'etrp',400)
endfunction

function PF_ObjectData6 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'h000',225)
    call SaveInteger(PF_prices,1,'h002',500)
    call SaveStr(PF_prices,3,'h002',"ReplaceableTextures\\CommandButtons\\BTNTreeOfLife.blp")
    call SaveInteger(PF_prices,1,'h003',2250)
    call SaveStr(PF_prices,3,'h003',"ReplaceableTextures\\CommandButtons\\BTNBeastiary.blp")
    call SaveInteger(PF_prices,1,'h004',0)
    call SaveStr(PF_prices,3,'h004',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'h00B',1500)
    call SaveStr(PF_prices,3,'h00B',"ReplaceableTextures\\CommandButtons\\BTNCrypt.blp")
    call SaveInteger(PF_prices,1,'h00C',1500)
    call SaveStr(PF_prices,3,'h00C',"ReplaceableTextures\\CommandButtons\\BTNStronghold.blp")
    call SaveInteger(PF_prices,1,'h00D',1500)
    call SaveStr(PF_prices,3,'h00D',"ReplaceableTextures\\CommandButtons\\BTNTreeOfLife.blp")
    call SaveInteger(PF_prices,1,'h00F',1900)
    call SaveStr(PF_prices,3,'h00F',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'h00G',1500)
    call SaveStr(PF_prices,3,'h00G',"ReplaceableTextures\\CommandButtons\\BTNKeep.blp")
    call SaveInteger(PF_prices,1,'h00H',500)
    call SaveStr(PF_prices,3,'h00H',"ReplaceableTextures\\CommandButtons\\BTNGreatHall.blp")
    call SaveInteger(PF_prices,1,'h00I',2250)
    call SaveStr(PF_prices,3,'h00I',"ReplaceableTextures\\CommandButtons\\BTNGraveyard.blp")
    call SaveInteger(PF_prices,1,'h00J',2250)
    call SaveStr(PF_prices,3,'h00J',"ReplaceableTextures\\CommandButtons\\BTNTreeOfAges.blp")
    call SaveInteger(PF_prices,1,'h00L',3500)
    call SaveStr(PF_prices,3,'h00L',"ReplaceableTextures\\CommandButtons\\BTNTreeOfEternity.blp")
    call SaveInteger(PF_prices,1,'h00M',3500)
    call SaveStr(PF_prices,3,'h00M',"ReplaceableTextures\\CommandButtons\\BTNTaurenTotem.blp")
    call SaveInteger(PF_prices,1,'h00N',3500)
    call SaveStr(PF_prices,3,'h00N',"ReplaceableTextures\\CommandButtons\\BTNBlackCitadel.blp")
    call SaveInteger(PF_prices,1,'h00O',12500)
    call SaveStr(PF_prices,3,'h00O',"ReplaceableTextures\\CommandButtons\\BTNCastle.blp")
    call SaveInteger(PF_prices,1,'h00R',500)
    call SaveInteger(PF_prices,1,'h00S',10000)
    call SaveStr(PF_prices,3,'h00S',"ReplaceableTextures\\CommandButtons\\BTNElvenGuardTower.blp")
    call SaveInteger(PF_prices,1,'h00V',2250)
    call SaveStr(PF_prices,3,'h00V',"ReplaceableTextures\\CommandButtons\\BTNArcaneSanctum.blp")
    call SaveInteger(PF_prices,1,'h00W',500)
    call SaveStr(PF_prices,3,'h00W',"ReplaceableTextures\\CommandButtons\\BTNHumanBarracks.blp")
    call SaveInteger(PF_prices,1,'h00X',12500)
    call SaveStr(PF_prices,3,'h00X',"ReplaceableTextures\\CommandButtons\\BTNTreeOfEternity.blp")
    call SaveStr(PF_prices,3,'h00Y',"ReplaceableTextures\\CommandButtons\\BTNNetherDragon.blp")
    call SaveInteger(PF_prices,1,'h00Z',500)
    call SaveStr(PF_prices,3,'h00Z',"ReplaceableTextures\\CommandButtons\\BTNNecropolis.blp")
    call SaveInteger(PF_prices,1,'h010',400)
    call SaveStr(PF_prices,3,'h010',"ReplaceableTextures\\CommandButtons\\BTNHumanLumberMill.blp")
    call SaveInteger(PF_prices,1,'h011',12500)
    call SaveStr(PF_prices,3,'h011',"ReplaceableTextures\\CommandButtons\\BTNTaurenTotem.blp")
    call SaveInteger(PF_prices,1,'h012',12500)
    call SaveStr(PF_prices,3,'h012',"ReplaceableTextures\\CommandButtons\\BTNBlackCitadel.blp")
    call SaveInteger(PF_prices,1,'h013',3500)
    call SaveStr(PF_prices,3,'h013',"ReplaceableTextures\\CommandButtons\\BTNCastle.blp")
    call SaveInteger(PF_prices,1,'h014',400)
    call SaveInteger(PF_prices,1,'h016',3500)
    call SaveInteger(PF_prices,1,'h017',12500)
    call SaveInteger(PF_prices,1,'h018',400)
    call SaveStr(PF_prices,3,'h018',"ReplaceableTextures\\CommandButtons\\BTNMortarTeam.blp")
    call SaveStr(PF_prices,3,'h019',"ReplaceableTextures\\CommandButtons\\BTNChimaera.blp")
    call SaveStr(PF_prices,3,'h01A',"ReplaceableTextures\\CommandButtons\\BTNChimaera.blp")
    call SaveStr(PF_prices,3,'h01C',"ReplaceableTextures\\CommandButtons\\BTNChimaera.blp")
    call SaveInteger(PF_prices,1,'h01G',300)
    call SaveStr(PF_prices,3,'h01G',"ReplaceableTextures\\CommandButtons\\BTNTavern.blp")
    call SaveInteger(PF_prices,1,'h01J',140)
    call SaveStr(PF_prices,3,'h01J',"UI\\Minimap\\Minimap-Tower")
    call SaveInteger(PF_prices,1,'h01K',50)
    call SaveStr(PF_prices,3,'h01K',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h01L',50)
    call SaveStr(PF_prices,3,'h01L',"ReplaceableTextures\\CommandButtons\\BTNOrbOfFrost.blp")
    call SaveInteger(PF_prices,1,'h01M',50)
    call SaveStr(PF_prices,3,'h01M',"ReplaceableTextures\\CommandButtons\\BTNOrbOfFire.blp")
    call SaveInteger(PF_prices,1,'h01N',50)
    call SaveStr(PF_prices,3,'h01N',"ReplaceableTextures\\CommandButtons\\BTNOrbOfLightning.blp")
    call SaveInteger(PF_prices,1,'h01O',50)
    call SaveStr(PF_prices,3,'h01O',"ReplaceableTextures\\CommandButtons\\BTNFragmentationBombs.blp")
    call SaveInteger(PF_prices,1,'h01P',300)
    call SaveInteger(PF_prices,1,'h01S',0)
    call SaveStr(PF_prices,3,'h01S',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveStr(PF_prices,3,'h01T',"ReplaceableTextures\\CommandButtons\\BTNNetherDragon.blp")
    call SaveStr(PF_prices,3,'h01V',"ReplaceableTextures\\CommandButtons\\BTNNetherDragon.blp")
    call SaveStr(PF_prices,3,'h01W',"ReplaceableTextures\\CommandButtons\\BTNNetherDragon.blp")
    call SaveStr(PF_prices,3,'h01Y',"ReplaceableTextures\\CommandButtons\\BTNNetherDragon.blp")
    call SaveStr(PF_prices,3,'h01Z',"ReplaceableTextures\\CommandButtons\\BTNNetherDragon.blp")
    call SaveInteger(PF_prices,1,'h020',0)
    call SaveStr(PF_prices,3,'h020',"ReplaceableTextures\\CommandButtons\\BTNSpeedUp.blp")
    call SaveInteger(PF_prices,1,'h021',5)
    call SaveInteger(PF_prices,1,'h022',300)
    call SaveStr(PF_prices,3,'h022',"ReplaceableTextures\\CommandButtons\\BTNTreeOfLife.blp")
    call SaveInteger(PF_prices,1,'h023',250)
    call SaveStr(PF_prices,3,'h023',"ReplaceableTextures\\CommandButtons\\BTNGreatHall.blp")
    call SaveInteger(PF_prices,1,'h024',300)
    call SaveStr(PF_prices,3,'h024',"ReplaceableTextures\\CommandButtons\\BTNStronghold.blp")
    call SaveInteger(PF_prices,1,'h025',400)
    call SaveStr(PF_prices,3,'h025',"ReplaceableTextures\\CommandButtons\\BTNBeastiary.blp")
    call SaveInteger(PF_prices,1,'h026',500)
    call SaveStr(PF_prices,3,'h026',"ReplaceableTextures\\CommandButtons\\BTNTaurenTotem.blp")
    call SaveInteger(PF_prices,1,'h027',300)
    call SaveStr(PF_prices,3,'h027',"ReplaceableTextures\\CommandButtons\\BTNTreeOfLife.blp")
    call SaveInteger(PF_prices,1,'h028',400)
    call SaveStr(PF_prices,3,'h028',"ReplaceableTextures\\CommandButtons\\BTNTreeOfAges.blp")
    call SaveInteger(PF_prices,1,'h029',50)
    call SaveStr(PF_prices,3,'h029',"ReplaceableTextures\\CommandButtons\\BTNSummonWaterElemental.blp")
endfunction

function PF_ObjectData7 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'h02A',50)
    call SaveStr(PF_prices,3,'h02A',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h02B',50)
    call SaveStr(PF_prices,3,'h02B',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h02H',300)
    call SaveStr(PF_prices,3,'h02H',"ReplaceableTextures\\CommandButtons\\BTNTavern.blp")
    call SaveInteger(PF_prices,1,'h02K',500)
    call SaveStr(PF_prices,3,'h02K',"ReplaceableTextures\\CommandButtons\\BTNTreeOfEternity.blp")
    call SaveInteger(PF_prices,1,'h02L',1000)
    call SaveStr(PF_prices,3,'h02L',"ReplaceableTextures\\CommandButtons\\BTNTreeOfEternity.blp")
    call SaveInteger(PF_prices,1,'h02M',1000)
    call SaveStr(PF_prices,3,'h02M',"ReplaceableTextures\\CommandButtons\\BTNTaurenTotem.blp")
    call SaveInteger(PF_prices,1,'h02N',250)
    call SaveStr(PF_prices,3,'h02N',"ReplaceableTextures\\CommandButtons\\BTNHumanBarracks.blp")
    call SaveInteger(PF_prices,1,'h02O',250)
    call SaveStr(PF_prices,3,'h02O',"ReplaceableTextures\\CommandButtons\\BTNNecropolis.blp")
    call SaveInteger(PF_prices,1,'h02P',50)
    call SaveStr(PF_prices,3,'h02P',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h02Q',50)
    call SaveStr(PF_prices,3,'h02Q',"ReplaceableTextures\\CommandButtons\\BTNEarthquake.blp")
    call SaveInteger(PF_prices,1,'h02S',0)
    call SaveStr(PF_prices,3,'h02S',"ReplaceableTextures\\CommandButtons\\BTNArcaniteArchitecture.blp")
    call SaveInteger(PF_prices,1,'h02T',0)
    call SaveStr(PF_prices,3,'h02T',"ReplaceableTextures\\CommandButtons\\BTNArcaniteArchitecture.blp")
    call SaveInteger(PF_prices,1,'h02U',0)
    call SaveStr(PF_prices,3,'h02U',"ReplaceableTextures\\CommandButtons\\BTN_cr_RIGHTbooK.blp")
    call SaveInteger(PF_prices,1,'h02V',0)
    call SaveStr(PF_prices,3,'h02V',"ReplaceableTextures\\CommandButtons\\BTN_cr_LEFTbooK.blp")
    call SaveInteger(PF_prices,1,'h02X',0)
    call SaveStr(PF_prices,3,'h02X',"ReplaceableTextures\\CommandButtons\\BTN_cr_RIGHTbooK.blp")
    call SaveInteger(PF_prices,1,'h02Y',0)
    call SaveStr(PF_prices,3,'h02Y',"ReplaceableTextures\\CommandButtons\\BTN_cr_LEFTbooK.blp")
    call SaveStr(PF_prices,3,'h030',"ReplaceableTextures\\CommandButtons\\BTNHellSheep.blp")
    call SaveStr(PF_prices,3,'h031',"ReplaceableTextures\\CommandButtons\\BTNHellSheep.blp")
    call SaveStr(PF_prices,3,'h032',"ReplaceableTextures\\CommandButtons\\BTNHellSheep.blp")
    call SaveStr(PF_prices,3,'h033',"ReplaceableTextures\\CommandButtons\\BTNHellSheep.blp")
    call SaveStr(PF_prices,3,'h034',"ReplaceableTextures\\CommandButtons\\BTNHellSheep.blp")
    call SaveStr(PF_prices,3,'h035',"ReplaceableTextures\\CommandButtons\\BTNHellSheep.blp")
    call SaveInteger(PF_prices,1,'h037',0)
    call SaveStr(PF_prices,3,'h037',"ReplaceableTextures\\CommandButtons\\BTN_cr_RIGHTbooK.blp")
    call SaveInteger(PF_prices,1,'h038',0)
    call SaveStr(PF_prices,3,'h038',"ReplaceableTextures\\CommandButtons\\BTN_cr_LEFTbooK.blp")
    call SaveInteger(PF_prices,1,'h039',250)
    call SaveInteger(PF_prices,1,'h03A',50)
    call SaveStr(PF_prices,3,'h03A',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h03B',250)
    call SaveInteger(PF_prices,1,'h03C',0)
    call SaveStr(PF_prices,3,'h03C',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h03D',0)
    call SaveStr(PF_prices,3,'h03D',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h03E',0)
    call SaveStr(PF_prices,3,'h03E',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h03F',0)
    call SaveStr(PF_prices,3,'h03F',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h03G',0)
    call SaveStr(PF_prices,3,'h03G',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h03H',0)
    call SaveStr(PF_prices,3,'h03H',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h03J',300)
    call SaveStr(PF_prices,3,'h03J',"ReplaceableTextures\\CommandButtons\\BTNCrypt.blp")
    call SaveInteger(PF_prices,1,'h03K',400)
    call SaveStr(PF_prices,3,'h03K',"ReplaceableTextures\\CommandButtons\\BTNGraveyard.blp")
    call SaveInteger(PF_prices,1,'h03L',500)
    call SaveStr(PF_prices,3,'h03L',"ReplaceableTextures\\CommandButtons\\BTNBlackCitadel.blp")
    call SaveInteger(PF_prices,1,'h03O',0)
    call SaveStr(PF_prices,3,'h03O',"ReplaceableTextures\\CommandButtons\\BTN_cr_LEFTbooK.blp")
    call SaveInteger(PF_prices,1,'h03P',0)
    call SaveStr(PF_prices,3,'h03P',"ReplaceableTextures\\CommandButtons\\BTN_cr_RIGHTbooK.blp")
    call SaveInteger(PF_prices,1,'h03R',50)
    call SaveStr(PF_prices,3,'h03R',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h03S',0)
    call SaveStr(PF_prices,3,'h03S',"ReplaceableTextures\\CommandButtons\\BTN_cr_RIGHTbooK.blp")
    call SaveInteger(PF_prices,1,'h03T',0)
    call SaveStr(PF_prices,3,'h03T',"ReplaceableTextures\\CommandButtons\\BTN_cr_LEFTbooK.blp")
    call SaveInteger(PF_prices,1,'h03V',0)
    call SaveStr(PF_prices,3,'h03V',"ReplaceableTextures\\CommandButtons\\BTNNoTransmute.blp")
    call SaveInteger(PF_prices,1,'h03W',1000)
    call SaveStr(PF_prices,3,'h03W',"ReplaceableTextures\\CommandButtons\\BTNBlackCitadel.blp")
    call SaveInteger(PF_prices,1,'h03X',300)
    call SaveStr(PF_prices,3,'h03X',"ReplaceableTextures\\CommandButtons\\BTNKeep.blp")
    call SaveInteger(PF_prices,1,'h03Y',300)
    call SaveStr(PF_prices,3,'h03Y',"ReplaceableTextures\\CommandButtons\\BTNTavern.blp")
    call SaveInteger(PF_prices,1,'h03Z',0)
    call SaveStr(PF_prices,3,'h03Z',"ReplaceableTextures\\CommandButtons\\BTNChestOfGold.blp")
    call SaveInteger(PF_prices,1,'h040',400)
    call SaveStr(PF_prices,3,'h040',"ReplaceableTextures\\CommandButtons\\BTNArcaneSanctum.blp")
    call SaveInteger(PF_prices,1,'h041',500)
    call SaveStr(PF_prices,3,'h041',"ReplaceableTextures\\CommandButtons\\BTNCastle.blp")
    call SaveInteger(PF_prices,1,'h042',1000)
    call SaveStr(PF_prices,3,'h042',"ReplaceableTextures\\CommandButtons\\BTNCastle.blp")
    call SaveInteger(PF_prices,1,'h044',50)
    call SaveStr(PF_prices,3,'h044',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h045',50)
    call SaveStr(PF_prices,3,'h045',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h046',50)
    call SaveStr(PF_prices,3,'h046',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h047',50)
    call SaveStr(PF_prices,3,'h047',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h049',50)
    call SaveStr(PF_prices,3,'h049',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
endfunction

function PF_ObjectData8 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'h04A',50)
    call SaveStr(PF_prices,3,'h04A',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h04B',0)
    call SaveStr(PF_prices,3,'h04B',"ReplaceableTextures\\CommandButtons\\BTNNoTrading.tga")
    call SaveInteger(PF_prices,1,'h04C',500)
    call SaveInteger(PF_prices,1,'h04D',50)
    call SaveStr(PF_prices,3,'h04D',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h04E',50)
    call SaveStr(PF_prices,3,'h04E',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h04G',1000)
    call SaveInteger(PF_prices,1,'h04H',0)
    call SaveStr(PF_prices,3,'h04H',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h04I',0)
    call SaveStr(PF_prices,3,'h04I',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h04J',0)
    call SaveStr(PF_prices,3,'h04J',"ReplaceableTextures\\CommandButtons\\BTNDarknessVersusLight.blp")
    call SaveInteger(PF_prices,1,'h04K',50)
    call SaveStr(PF_prices,3,'h04K',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h04L',0)
    call SaveStr(PF_prices,3,'h04L',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h04M',0)
    call SaveStr(PF_prices,3,'h04M',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h04N',0)
    call SaveStr(PF_prices,3,'h04N',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h04O',0)
    call SaveStr(PF_prices,3,'h04O',"ReplaceableTextures\\CommandButtons\\BTNAdvancedFlameTower.blp")
    call SaveInteger(PF_prices,1,'h04P',0)
    call SaveStr(PF_prices,3,'h04P',"ReplaceableTextures\\CommandButtons\\BTNGoldMine.blp")
    call SaveInteger(PF_prices,1,'h04R',200)
    call SaveStr(PF_prices,3,'h04R',"ReplaceableTextures\\CommandButtons\\BTNHumanArcaneTower.blp")
    call SaveInteger(PF_prices,1,'h04V',50)
    call SaveStr(PF_prices,3,'h04V',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h050',50)
    call SaveStr(PF_prices,3,'h050',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h051',1000)
    call SaveStr(PF_prices,3,'h051',"ReplaceableTextures\\CommandButtons\\BTNTavern.blp")
    call SaveInteger(PF_prices,1,'h053',50)
    call SaveStr(PF_prices,3,'h053',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h054',0)
    call SaveStr(PF_prices,3,'h054',"war3mapImported\\BTNNoKOTH.blp")
    call SaveInteger(PF_prices,1,'h055',140)
    call SaveInteger(PF_prices,1,'h056',140)
    call SaveInteger(PF_prices,1,'h059',50)
    call SaveStr(PF_prices,3,'h059',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h05A',140)
    call SaveInteger(PF_prices,1,'h05C',170)
    call SaveInteger(PF_prices,1,'h05D',140)
    call SaveStr(PF_prices,3,'h05D',"UI\\Minimap\\Minimap-Tower")
    call SaveInteger(PF_prices,1,'h05F',0)
    call SaveStr(PF_prices,3,'h05F',"ReplaceableTextures\\CommandButtons\\BTNSorceressMaster.blp")
    call SaveInteger(PF_prices,1,'h05G',0)
    call SaveStr(PF_prices,3,'h05G',"ReplaceableTextures\\CommandButtons\\BTNTheCaptain.blp")
    call SaveInteger(PF_prices,1,'h05J',0)
    call SaveStr(PF_prices,3,'h05J',"ReplaceableTextures\\CommandButtons\\BTN_cr_RIGHTbooK.blp")
    call SaveInteger(PF_prices,1,'h05K',0)
    call SaveStr(PF_prices,3,'h05K',"ReplaceableTextures\\CommandButtons\\BTN_cr_LEFTbooK.blp")
    call SaveInteger(PF_prices,1,'h05L',0)
    call SaveStr(PF_prices,3,'h05L',"ReplaceableTextures\\CommandButtons\\BTNTheCaptain.blp")
    call SaveInteger(PF_prices,1,'h05M',50)
    call SaveStr(PF_prices,3,'h05M',"ReplaceableTextures\\WorldEditUI\\Editor-Force.blp")
    call SaveInteger(PF_prices,1,'h05Q',0)
    call SaveStr(PF_prices,3,'h05Q',"ReplaceableTextures\\CommandButtons\\BTNTheCaptain.blp")
    call SaveInteger(PF_prices,1,'h05S',0)
    call SaveStr(PF_prices,3,'h05S',"ReplaceableTextures\\CommandButtons\\BTNTheCaptain.blp")
    call SaveInteger(PF_prices,1,'h05T',0)
    call SaveStr(PF_prices,3,'h05T',"ReplaceableTextures\\CommandButtons\\BTNTavern.blp")
    call SaveInteger(PF_prices,1,'h05U',800)
    call SaveInteger(PF_prices,1,'h05V',140)
    call SaveInteger(PF_prices,1,'h05W',140)
    call SaveInteger(PF_prices,1,'h060',140)
    call SaveInteger(PF_prices,1,'hGpy',140)
    call SaveStr(PF_prices,3,'hGpy',"ReplaceableTextures\\CommandButtons\\BTNGuardianLantern.blp")
    call SaveInteger(PF_prices,1,'hGs1',0)
    call SaveInteger(PF_prices,1,'hSHC',0)
    call SaveStr(PF_prices,3,'hSHC',"ReplaceableTextures\\CommandButtons\\BTNDranaiAkama.blp")
    call SaveInteger(PF_prices,1,'hTNP',0)
    call SaveStr(PF_prices,3,'hTNP',"ReplaceableTextures\\CommandButtons\\BTN_cr_RIGHTbooK.blp")
    call SaveInteger(PF_prices,1,'hTRZ',0)
    call SaveStr(PF_prices,3,'hTRZ',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'hatw',500)
    call SaveInteger(PF_prices,1,'hbar',7500)
    call SaveInteger(PF_prices,1,'hctw',200)
    call SaveInteger(PF_prices,1,'hdhw',300)
    call SaveStr(PF_prices,3,'hdhw',"ReplaceableTextures\\CommandButtons\\BTNMortarTeam.blp")
    call SaveInteger(PF_prices,1,'hfoo',140)
    call SaveInteger(PF_prices,1,'hgr1',140)
    call SaveInteger(PF_prices,1,'hgtw',200)
    call SaveInteger(PF_prices,1,'hhou',300)
    call SaveStr(PF_prices,3,'hhou',"ReplaceableTextures\\CommandButtons\\BTNTavern.blp")
    call SaveInteger(PF_prices,1,'hkni',300)
    call SaveInteger(PF_prices,1,'hmil',220)
    call SaveInteger(PF_prices,1,'hor1',140)
    call SaveStr(PF_prices,3,'hor1',"ReplaceableTextures\\CommandButtons\\BTNPhoenixEgg.blp")
    call SaveInteger(PF_prices,1,'hor2',140)
    call SaveStr(PF_prices,3,'hor2',"ReplaceableTextures\\CommandButtons\\BTNPhoenixEgg.blp")
    call SaveInteger(PF_prices,1,'hor3',140)
    call SaveStr(PF_prices,3,'hor3',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'hrdh',400)
    call SaveInteger(PF_prices,1,'hrif',170)
    call SaveInteger(PF_prices,1,'hspt',250)
endfunction

function PF_ObjectData9 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'ht46',140)
    call SaveStr(PF_prices,3,'ht46',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'htf1',140)
    call SaveStr(PF_prices,3,'htf1',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'htf2',140)
    call SaveStr(PF_prices,3,'htf2',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'htf3',140)
    call SaveStr(PF_prices,3,'htf3',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'htf4',140)
    call SaveStr(PF_prices,3,'htf4',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveInteger(PF_prices,1,'htz1',140)
    call SaveStr(PF_prices,3,'htz1',"ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp")
    call SaveInteger(PF_prices,1,'hwtw',0)
    call SaveStr(PF_prices,3,'n000',"ReplaceableTextures\\CommandButtons\\BTNArcaneVault.blp")
    call SaveInteger(PF_prices,1,'n001',450)
    call SaveStr(PF_prices,3,'n002',"ReplaceableTextures\\CommandButtons\\BTNCancel.blp")
    call SaveStr(PF_prices,3,'n003',"ReplaceableTextures\\CommandButtons\\BTNDranaiHut.blp")
    call SaveInteger(PF_prices,1,'n005',400)
    call SaveInteger(PF_prices,1,'n006',200)
    call SaveInteger(PF_prices,1,'n00A',200)
    call SaveInteger(PF_prices,1,'n00Q',400)
    call SaveInteger(PF_prices,1,'n00S',500)
    call SaveInteger(PF_prices,1,'n00T',350)
    call SaveInteger(PF_prices,1,'n00U',5000)
    call SaveInteger(PF_prices,1,'n011',350)
    call SaveStr(PF_prices,3,'n012',"ReplaceableTextures\\CommandButtons\\BTNAltarOfKings.blp")
    call SaveInteger(PF_prices,1,'n014',400)
    call SaveStr(PF_prices,3,'n014',"ReplaceableTextures\\CommandButtons\\BTNSkink.blp")
    call SaveStr(PF_prices,3,'n019',"ReplaceableTextures\\CommandButtons\\BTNCancel.blp")
    call SaveInteger(PF_prices,1,'n01B',1000)
    call SaveInteger(PF_prices,1,'n01M',300)
    call SaveInteger(PF_prices,1,'n01N',1500)
    call SaveInteger(PF_prices,1,'n01P',12000)
    call SaveStr(PF_prices,3,'n01P',"ReplaceableTextures\\CommandButtons\\BTNnightterror.blp")
    call SaveStr(PF_prices,3,'n01Q',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveInteger(PF_prices,1,'n01R',200)
    call SaveStr(PF_prices,3,'n01R',"ReplaceableTextures\\CommandButtons\\BTNArmorGolem.blp")
    call SaveStr(PF_prices,3,'n01T',"ReplaceableTextures\\CommandButtons\\BTNGreenBook.blp")
    call SaveStr(PF_prices,3,'n01U',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n01V',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n01W',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n01X',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveInteger(PF_prices,1,'n01Y',8000)
    call SaveStr(PF_prices,3,'n01Y',"ReplaceableTextures\\CommandButtons\\BTNSpiritLodge.blp")
    call SaveStr(PF_prices,3,'n020',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n021',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n022',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n023',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n024',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n025',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n026',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n028',"ReplaceableTextures\\CommandButtons\\BTNCancel.blp")
    call SaveStr(PF_prices,3,'n029',"ReplaceableTextures\\CommandButtons\\BTNCancel.blp")
    call SaveStr(PF_prices,3,'n02A',"ReplaceableTextures\\CommandButtons\\BTNBlackMarket.blp")
    call SaveStr(PF_prices,3,'n02B',"ReplaceableTextures\\CommandButtons\\BTNArcaneVault.blp")
    call SaveStr(PF_prices,3,'n02C',"ReplaceableTextures\\CommandButtons\\BTNBlackMarket.blp")
    call SaveStr(PF_prices,3,'n02D',"ReplaceableTextures\\CommandButtons\\BTNCOP.blp")
    call SaveStr(PF_prices,3,'n02G',"ReplaceableTextures\\CommandButtons\\BTNExpandedView.blp")
    call SaveStr(PF_prices,3,'n02H',"ReplaceableTextures\\CommandButtons\\BTNCancel.blp")
    call SaveStr(PF_prices,3,'n02K',"ReplaceableTextures\\CommandButtons\\BTNArcaneVault.blp")
    call SaveInteger(PF_prices,1,'n02L',5)
    call SaveInteger(PF_prices,1,'n02M',50)
    call SaveStr(PF_prices,3,'n02N',"ReplaceableTextures\\CommandButtons\\BTNBlacksmith.blp")
    call SaveStr(PF_prices,3,'n02T',"ReplaceableTextures\\CommandButtons\\BTNChaosBlademaster.blp")
    call SaveStr(PF_prices,3,'n02V',"ReplaceableTextures\\CommandButtons\\BTNGoldMine.blp")
    call SaveStr(PF_prices,3,'n02W',"ReplaceableTextures\\CommandButtons\\BTNChestOfGold.blp")
    call SaveStr(PF_prices,3,'n02X',"ReplaceableTextures\\CommandButtons\\BTNChestOfGold.blp")
    call SaveStr(PF_prices,3,'n02Y',"ReplaceableTextures\\CommandButtons\\BTNChestOfGold.blp")
    call SaveStr(PF_prices,3,'n02Z',"ReplaceableTextures\\CommandButtons\\BTNSpiritLodge.blp")
    call SaveInteger(PF_prices,1,'n033',350)
    call SaveStr(PF_prices,3,'n033',"ReplaceableTextures\\CommandButtons\\BTNSonOfAnubis.blp")
    call SaveStr(PF_prices,3,'n034',"ReplaceableTextures\\CommandButtons\\BTNFarm.blp")
    call SaveStr(PF_prices,3,'n03C',"ReplaceableTextures\\CommandButtons\\BTNdeathwing.blp")
    call SaveStr(PF_prices,3,'n03D',"ReplaceableTextures\\CommandButtons\\BTNdeathwing.blp")
    call SaveStr(PF_prices,3,'n03E',"ReplaceableTextures\\CommandButtons\\BTNdeathwing.blp")
    call SaveInteger(PF_prices,1,'n03I',450)
    call SaveStr(PF_prices,3,'n03I',"ReplaceableTextures\\CommandButtons\\BTNAxeMaster.blp")
    call SaveStr(PF_prices,3,'n03K',"ReplaceableTextures\\CommandButtons\\BTNCancel.blp")
    call SaveInteger(PF_prices,1,'n03M',400)
    call SaveStr(PF_prices,3,'n03N',"ReplaceableTextures\\CommandButtons\\BTNSkeletonWarrior.blp")
    call SaveStr(PF_prices,3,'n03O',"ReplaceableTextures\\CommandButtons\\BTN_CW_Death_Guard.blp")
    call SaveStr(PF_prices,3,'n03P',"ReplaceableTextures\\CommandButtons\\BTN_CW_Death_Guard.blp")
    call SaveStr(PF_prices,3,'n03Q',"ReplaceableTextures\\CommandButtons\\BTN_CW_Death_Guard.blp")
    call SaveStr(PF_prices,3,'n03R',"ReplaceableTextures\\CommandButtons\\BTNSkeletonArcher.blp")
    call SaveStr(PF_prices,3,'n03S',"ReplaceableTextures\\CommandButtons\\BTNSkeletonArcher.blp")
    call SaveStr(PF_prices,3,'n03T',"ReplaceableTextures\\CommandButtons\\BTNSkeletonArcher.blp")
    call SaveStr(PF_prices,3,'n03U',"ReplaceableTextures\\CommandButtons\\BTNSkeletonArcher.blp")
    call SaveStr(PF_prices,3,'n03V',"ReplaceableTextures\\CommandButtons\\BTNSkeletonArcher.blp")
    call SaveStr(PF_prices,3,'n03W',"ReplaceableTextures\\CommandButtons\\BTN_CW_Death_Guard.blp")
    call SaveStr(PF_prices,3,'n03X',"ReplaceableTextures\\CommandButtons\\BTN_CW_Death_Guard.blp")
    call SaveStr(PF_prices,3,'n03Y',"ReplaceableTextures\\CommandButtons\\BTNSkeletonArcher.blp")
    call SaveStr(PF_prices,3,'n03Z',"ReplaceableTextures\\CommandButtons\\BTNGoldMine.blp")
    call SaveInteger(PF_prices,1,'n040',1300)
    call SaveInteger(PF_prices,1,'n042',0)
    call SaveStr(PF_prices,3,'n042',"ReplaceableTextures\\CommandButtons\\BTNTychusPortrait.blp")
    call SaveInteger(PF_prices,1,'n043',0)
    call SaveStr(PF_prices,3,'n043',"ReplaceableTextures\\CommandButtons\\BTNTychusPortrait.blp")
    call SaveInteger(PF_prices,1,'n044',0)
    call SaveStr(PF_prices,3,'n044',"ReplaceableTextures\\CommandButtons\\BTNTychusPortrait.blp")
    call SaveStr(PF_prices,3,'n045',"ReplaceableTextures\\CommandButtons\\BTNUndeadShrine.blp")
endfunction

function PF_ObjectData10 takes nothing returns nothing
    call SaveStr(PF_prices,3,'n046',"ReplaceableTextures\\CommandButtons\\BTNGoldMine.blp")
    call SaveStr(PF_prices,3,'n047',"ReplaceableTextures\\CommandButtons\\BTNOgronIconYellow.blp")
    call SaveInteger(PF_prices,1,'n048',450)
    call SaveStr(PF_prices,3,'n048',"ReplaceableTextures\\CommandButtons\\BTNForestTroll.blp")
    call SaveStr(PF_prices,3,'n049',"ReplaceableTextures\\CommandButtons\\BTNSumo.blp")
    call SaveStr(PF_prices,3,'n04C',"ReplaceableTextures\\CommandButtons\\BTNSkull.blp")
    call SaveStr(PF_prices,3,'n04K',"ReplaceableTextures\\CommandButtons\\BTNdeathwing.blp")
    call SaveInteger(PF_prices,1,'n04X',250)
    call SaveInteger(PF_prices,1,'n052',400)
    call SaveInteger(PF_prices,1,'n05F',0)
    call SaveInteger(PF_prices,1,'n05G',0)
    call SaveStr(PF_prices,3,'n05K',"ReplaceableTextures\\CommandButtons\\BTNDeathGrin.blp")
    call SaveStr(PF_prices,3,'n05N',"ReplaceableTextures\\CommandButtons\\BTNLobstrokkRed.blp")
    call SaveStr(PF_prices,3,'n05O',"ReplaceableTextures\\CommandButtons\\BTNLobstrokkRed.blp")
    call SaveStr(PF_prices,3,'n05S',"ReplaceableTextures\\CommandButtons\\BTNDeathGrin.blp")
    call SaveStr(PF_prices,3,'n05T',"ReplaceableTextures\\CommandButtons\\BTNDeathGrin.blp")
    call SaveStr(PF_prices,3,'n05U',"ReplaceableTextures\\CommandButtons\\BTNDeathGrin.blp")
    call SaveStr(PF_prices,3,'n05V',"ReplaceableTextures\\CommandButtons\\BTNDeathGrin.blp")
    call SaveStr(PF_prices,3,'n05W',"ReplaceableTextures\\CommandButtons\\BTNDeathGrin.blp")
    call SaveStr(PF_prices,3,'n05Z',"ReplaceableTextures\\CommandButtons\\BTNWarpPortal.blp")
    call SaveStr(PF_prices,3,'n060',"ReplaceableTextures\\CommandButtons\\BTNWarpPortal.blp")
    call SaveStr(PF_prices,3,'n061',"ReplaceableTextures\\CommandButtons\\BTNLobstrokkRed.blp")
    call SaveStr(PF_prices,3,'n064',"ReplaceableTextures\\CommandButtons\\BTNWarpPortal.blp")
    call SaveStr(PF_prices,3,'n06E',"ReplaceableTextures\\CommandButtons\\BTNBoneyard.blp")
    call SaveStr(PF_prices,3,'n06P',"ReplaceableTextures\\CommandButtons\\BTNdeathwing.blp")
    call SaveStr(PF_prices,3,'n66A',"ReplaceableTextures\\CommandButtons\\BTNAltarOfKings.blp")
    call SaveInteger(PF_prices,1,'ndr3',1900)
    call SaveInteger(PF_prices,1,'ngh2',220)
    call SaveInteger(PF_prices,1,'ngsp',300)
    call SaveStr(PF_prices,3,'nnrg',"ReplaceableTextures\\CommandButtons\\BTNNagaMyrmidon.blp")
    call SaveInteger(PF_prices,1,'nsce',190)
    call SaveInteger(PF_prices,1,'nsgt',200)
    call SaveInteger(PF_prices,1,'nske',0)
    call SaveInteger(PF_prices,1,'nskf',170)
    call SaveInteger(PF_prices,1,'nws1',450)
    call SaveStr(PF_prices,3,'o002',"ReplaceableTextures\\CommandButtons\\BTNStaffOfSanctuary.blp")
    call SaveInteger(PF_prices,1,'o009',400)
    call SaveInteger(PF_prices,1,'o00A',300)
    call SaveInteger(PF_prices,1,'o00B',16000)
    call SaveStr(PF_prices,3,'o00B',"ReplaceableTextures\\CommandButtons\\BTNAltarOfStorms.blp")
    call SaveInteger(PF_prices,1,'o00H',400)
    call SaveStr(PF_prices,3,'o00J',"ReplaceableTextures\\CommandButtons\\BTNTentacle.blp")
    call SaveInteger(PF_prices,1,'o00K',300)
    call SaveStr(PF_prices,3,'o00K',"ReplaceableTextures\\CommandButtons\\BTNBloodElfSorceress.blp")
    call SaveStr(PF_prices,3,'o00L',"ReplaceableTextures\\CommandButtons\\BTNWendigo_Custom.blp")
    call SaveStr(PF_prices,3,'o00M',"ReplaceableTextures\\CommandButtons\\BTNWendigo_Custom.blp")
    call SaveStr(PF_prices,3,'o00N',"ReplaceableTextures\\CommandButtons\\BTNWendigo_Custom.blp")
    call SaveStr(PF_prices,3,'o00P',"ReplaceableTextures\\CommandButtons\\BTNGreenBook.blp")
    call SaveStr(PF_prices,3,'o00Q',"ReplaceableTextures\\CommandButtons\\BTNGreenBook.blp")
    call SaveStr(PF_prices,3,'o00R',"ReplaceableTextures\\CommandButtons\\BTNGreenBook.blp")
    call SaveStr(PF_prices,3,'o00S',"ReplaceableTextures\\CommandButtons\\BTNGreenBook.blp")
    call SaveStr(PF_prices,3,'o00U',"ReplaceableTextures\\CommandButtons\\BTNOrcCaptureFlag.blp")
    call SaveStr(PF_prices,3,'o00V',"ReplaceableTextures\\CommandButtons\\BTNNecro.blp")
    call SaveInteger(PF_prices,1,'o00Y',0)
    call SaveStr(PF_prices,3,'o00Y',"ReplaceableTextures\\CommandButtons\\BTNForceField.blp")
    call SaveStr(PF_prices,3,'o011',"ReplaceableTextures\\CommandButtons\\BTNDeadProphetStaff.blp")
    call SaveInteger(PF_prices,1,'o012',150)
    call SaveStr(PF_prices,3,'o013',"ReplaceableTextures\\CommandButtonsDisabled\\DISBTNBoomBox.blp")
    call SaveStr(PF_prices,3,'o017',"ReplaceableTextures\\CommandButtons\\BTNTentacle.blp")
    call SaveStr(PF_prices,3,'o018',"ReplaceableTextures\\CommandButtons\\BTNTentacle.blp")
    call SaveInteger(PF_prices,1,'o019',230)
    call SaveStr(PF_prices,3,'o01E',"ReplaceableTextures\\CommandButtons\\BTNNeutralManaShieldOff.blp")
    call SaveStr(PF_prices,3,'o01F',"ReplaceableTextures\\CommandButtons\\BTNBearTrap.blp")
    call SaveInteger(PF_prices,1,'ogru',150)
    call SaveInteger(PF_prices,1,'ohun',170)
    call SaveInteger(PF_prices,1,'orai',250)
    call SaveInteger(PF_prices,1,'otau',300)
    call SaveInteger(PF_prices,1,'otbk',220)
    call SaveInteger(PF_prices,1,'otrb',200)
    call SaveInteger(PF_prices,1,'owtw',200)
    call SaveInteger(PF_prices,1,'u009',400)
    call SaveInteger(PF_prices,1,'u00B',500)
    call SaveInteger(PF_prices,1,'u00D',0)
    call SaveInteger(PF_prices,1,'u00E',150)
    call SaveInteger(PF_prices,1,'u00G',200)
    call SaveStr(PF_prices,3,'u00G',"ReplaceableTextures\\CommandButtons\\BTNSkeletonWarrior.blp")
    call SaveInteger(PF_prices,1,'u00H',250)
    call SaveInteger(PF_prices,1,'u00I',150)
    call SaveStr(PF_prices,3,'u00I',"ReplaceableTextures\\CommandButtons\\BTNSkeletonWarrior.blp")
    call SaveInteger(PF_prices,1,'u00K',175)
    call SaveStr(PF_prices,3,'u00K',"ReplaceableTextures\\CommandButtons\\BTNSkeletonWarrior.blp")
    call SaveInteger(PF_prices,1,'u00L',225)
    call SaveStr(PF_prices,3,'u00L',"ReplaceableTextures\\CommandButtons\\BTNSkeletonWarrior.blp")
    call SaveInteger(PF_prices,1,'u00O',0)
    call SaveInteger(PF_prices,1,'u00P',0)
    call SaveInteger(PF_prices,1,'u00Q',0)
    call SaveInteger(PF_prices,1,'u00S',150)
    call SaveInteger(PF_prices,1,'u00T',150)
    call SaveInteger(PF_prices,1,'u00U',150)
    call SaveInteger(PF_prices,1,'u00V',150)
    call SaveInteger(PF_prices,1,'u00W',150)
    call SaveInteger(PF_prices,1,'u00X',150)
    call SaveStr(PF_prices,3,'u00Y',"ReplaceableTextures\\CommandButtons\\BTNGargoyle.blp")
    call SaveStr(PF_prices,3,'u00Z',"ReplaceableTextures\\CommandButtons\\BTNGargoyle.blp")
    call SaveStr(PF_prices,3,'u010',"ReplaceableTextures\\CommandButtons\\BTNGargoyle.blp")
    call SaveInteger(PF_prices,1,'u011',250)
    call SaveInteger(PF_prices,1,'u012',150)
    call SaveStr(PF_prices,3,'u012',"ReplaceableTextures\\CommandButtons\\BTNSkeletonWarrior.blp")
    call SaveInteger(PF_prices,1,'u014',220)
    call SaveInteger(PF_prices,1,'u01A',300)
endfunction

function PF_ObjectData11 takes nothing returns nothing
    call SaveInteger(PF_prices,1,'u01B',5)
    call SaveInteger(PF_prices,1,'u01C',0)
    call SaveInteger(PF_prices,1,'u01F',0)
    call SaveStr(PF_prices,3,'u01F',"ReplaceableTextures\\CommandButtons\\BTNBookOfSummoning.blp")
    call SaveInteger(PF_prices,1,'uabo',300)
    call SaveInteger(PF_prices,1,'uban',170)
    call SaveInteger(PF_prices,1,'ucrm',220)
    call SaveInteger(PF_prices,1,'ucry',220)
    call SaveInteger(PF_prices,1,'ugho',150)
    call SaveStr(PF_prices,3,'umir',"ReplaceableTextures\\CommandButtons\\BTNMirrorImage.blp")
    call SaveInteger(PF_prices,1,'uobs',400)
    call SaveInteger(PF_prices,1,'ushd',300)
    call SaveInteger(PF_prices,1,'uskm',250)
    call SaveInteger(PF_prices,1,'z003',10)
    call SaveStr(PF_prices,3,'z003',"ReplaceableTextures\\CommandButtons\\BTNDarkTroll.blp")
    call SaveInteger(PF_prices,1,'z004',10)
    call SaveStr(PF_prices,3,'z004',"ReplaceableTextures\\CommandButtons\\BTNDarkTroll.blp")
    call SaveInteger(PF_prices,1,'z005',10)
    call SaveStr(PF_prices,3,'z005',"ReplaceableTextures\\CommandButtons\\BTNDarkTroll.blp")
    call SaveInteger(PF_prices,1,'R000',300)
    call SaveInteger(PF_prices,2,'R000',150)
    call SaveStr(PF_prices,3,'R000',"ReplaceableTextures\\PassiveButtons\\PASBTNDevotion.blp")
    call SaveInteger(PF_prices,1,'R001',100)
    call SaveInteger(PF_prices,2,'R001',50)
    call SaveInteger(PF_prices,2,'R002',50)
    call SaveStr(PF_prices,3,'R002',"ReplaceableTextures\\CommandButtons\\BTNPeriapt.blp")
    call SaveInteger(PF_prices,2,'R003',50)
    call SaveStr(PF_prices,3,'R003',"ReplaceableTextures\\CommandButtons\\BTNOrcMeleeUpOne.blp")
    call SaveInteger(PF_prices,1,'R004',150)
    call SaveInteger(PF_prices,2,'R004',150)
    call SaveInteger(PF_prices,2,'R005',50)
    call SaveStr(PF_prices,3,'R005',"ReplaceableTextures\\CommandButtons\\BTNPendantOfMana.blp")
    call SaveInteger(PF_prices,1,'R006',200)
    call SaveInteger(PF_prices,2,'R006',50)
    call SaveStr(PF_prices,3,'R006',"ReplaceableTextures\\CommandButtons\\BTNPotionGreen.blp")
    call SaveInteger(PF_prices,1,'R007',200)
    call SaveInteger(PF_prices,2,'R007',50)
    call SaveStr(PF_prices,3,'R007',"ReplaceableTextures\\CommandButtons\\BTNPotionBlue.blp")
    call SaveInteger(PF_prices,1,'R008',200)
    call SaveInteger(PF_prices,2,'R008',100)
    call SaveStr(PF_prices,3,'R008',"ReplaceableTextures\\PassiveButtons\\PASBTNDrum.blp")
    call SaveInteger(PF_prices,1,'R009',500)
    call SaveStr(PF_prices,3,'R009',"ReplaceableTextures\\CommandButtons\\BTNSpeedUp.blp")
    call SaveInteger(PF_prices,1,'R00A',400)
    call SaveInteger(PF_prices,2,'R00A',100)
    call SaveStr(PF_prices,3,'R00A',"ReplaceableTextures\\CommandButtons\\BTNFrostBolt.blp")
    call SaveStr(PF_prices,3,'R00B',"ReplaceableTextures\\WorldEditUI\\Editor-Random-Building.blp")
    call SaveInteger(PF_prices,1,'R00C',600)
    call SaveStr(PF_prices,3,'R00C',"ReplaceableTextures\\CommandButtons\\BTNResStone.blp")
    call SaveStr(PF_prices,3,'R00D',"ReplaceableTextures\\WorldEditUI\\Editor-Random-Building.blp")
    call SaveStr(PF_prices,3,'R00E',"ReplaceableTextures\\WorldEditUI\\Editor-Random-Building.blp")
    call SaveStr(PF_prices,3,'R00F',"ReplaceableTextures\\WorldEditUI\\Editor-Random-Building.blp")
    call SaveStr(PF_prices,3,'R00G',"ReplaceableTextures\\WorldEditUI\\Editor-Random-Building.blp")
    call SaveInteger(PF_prices,1,'R00H',500)
    call SaveStr(PF_prices,3,'R00H',"ReplaceableTextures\\CommandButtons\\BTNCallToArms.blp")
    call SaveInteger(PF_prices,1,'R00K',250)
    call SaveInteger(PF_prices,2,'R00K',25)
    call SaveStr(PF_prices,3,'R00K',"ReplaceableTextures\\CommandButtons\\BTNMarksmanship.blp")
    call SaveInteger(PF_prices,1,'R00L',200)
    call SaveInteger(PF_prices,1,'R00M',250)
    call SaveInteger(PF_prices,2,'R00M',25)
    call SaveStr(PF_prices,3,'R00M',"ReplaceableTextures\\CommandButtons\\BTNHealthStone.blp")
    call SaveInteger(PF_prices,1,'R00N',0)
    call SaveStr(PF_prices,3,'R00O',"ReplaceableTextures\\WorldEditUI\\Editor-Random-Building.blp")
    call SaveInteger(PF_prices,1,'R00P',500)
    call SaveInteger(PF_prices,2,'R00P',300)
    call SaveStr(PF_prices,3,'R00P',"ReplaceableTextures\\CommandButtons\\BTNSorceressAdept.blp")
    call SaveInteger(PF_prices,1,'R00Q',200)
    call SaveInteger(PF_prices,2,'R00Q',75)
    call SaveStr(PF_prices,3,'R00Q',"ReplaceableTextures\\CommandButtons\\BTNSoul Rune.blp")
    call SaveInteger(PF_prices,1,'R00T',0)
    call SaveStr(PF_prices,3,'R00T',"ReplaceableTextures\\CommandButtonsDisabled\\DISBTNCarrionSwarm1.blp")
    call SaveStr(PF_prices,3,'R00U',"ReplaceableTextures\\WorldEditUI\\Editor-Random-Building.blp")
    call SaveInteger(PF_prices,1,'R00V',10000)
    call SaveInteger(PF_prices,2,'R00V',50)
    call SaveStr(PF_prices,3,'R00V',"ReplaceableTextures\\CommandButtons\\BTNAzureDragon.blp")
    call SaveInteger(PF_prices,1,'Rhac',500)
    call SaveInteger(PF_prices,2,'Rhac',150)
    call SaveInteger(PF_prices,2,'Rhan',150)
    call SaveInteger(PF_prices,2,'Rhar',50)
    call SaveInteger(PF_prices,2,'Rhme',50)
    call SaveInteger(PF_prices,1,'Robs',150)
    call SaveInteger(PF_prices,2,'Robs',150)
    call SaveInteger(PF_prices,1,'Rorb',0)
    call SaveInteger(PF_prices,1,'Rugf',150)
    call SaveInteger(PF_prices,2,'Rugf',150)
    call SaveStr(PF_prices,4,StringHash("gold_out"),"Gold debit")
    call SaveStr(PF_prices,4,StringHash("pool_sent"),"Sent to")
    call SaveStr(PF_prices,4,StringHash("pool_received"),"Received from")
    call SaveStr(PF_prices,4,StringHash("item"),"Bought")
    call SaveStr(PF_prices,4,StringHash("hire"),"Hired")
    call SaveStr(PF_prices,4,StringHash("research"),"Research complete")
    call SaveStr(PF_prices,4,StringHash("upgrade"),"Upgraded")
    call SaveStr(PF_prices,4,StringHash("hero"),"Hero selected")
    call SaveStr(PF_prices,4,StringHash("train"),"Trained")
    call SaveStr(PF_prices,4,StringHash("construct"),"Built")
    call SaveStr(PF_prices,4,StringHash("stake"),"Casino stake")
    call SaveStr(PF_prices,4,StringHash("return"),"Casino return")
    call SaveStr(PF_prices,4,StringHash("research_start"),"Research started")
    call SaveStr(PF_prices,4,StringHash("research_cancel"),"Research cancelled")
endfunction

function PF_ObjectData12 takes nothing returns nothing
    call SaveStr(PF_prices,4,StringHash("train_start"),"Training started")
    call SaveStr(PF_prices,4,StringHash("train_cancel"),"Training cancelled")
    call SaveStr(PF_prices,4,StringHash("construct_start"),"Construction started")
    call SaveStr(PF_prices,4,StringHash("construct_cancel"),"Construction cancelled")
    call SaveStr(PF_prices,4,StringHash("skill"),"Learned")
    set PF_tabName[0] = "Stats"
    set PF_tabName[1] = "Heroes"
    set PF_tabName[2] = "Items"
    set PF_tabName[3] = "Units"
    set PF_tabName[4] = "Skins"
    set PF_tabName[5] = "Build order"
    set PF_tabName[6] = "Casino"
    set PF_tabName[7] = "Usage"
    set PF_tabName[8] = ""
    set PF_tabName[9] = ""
    set PF_tabName[10] = "Overview"
    set PF_tabName[11] = "Scores"
    set PF_tabName[12] = "Transfers"
    set PF_tabName[13] = "Army"
    set PF_tabName[14] = "Economy"
    set PF_tabName[15] = "Combat"
endfunction

function PF_LoadObjects takes nothing returns nothing
    call ExecuteFunc("PF_ObjectData0")
    call ExecuteFunc("PF_ObjectData1")
    call ExecuteFunc("PF_ObjectData2")
    call ExecuteFunc("PF_ObjectData3")
    call ExecuteFunc("PF_ObjectData4")
    call ExecuteFunc("PF_ObjectData5")
    call ExecuteFunc("PF_ObjectData6")
    call ExecuteFunc("PF_ObjectData7")
    call ExecuteFunc("PF_ObjectData8")
    call ExecuteFunc("PF_ObjectData9")
    call ExecuteFunc("PF_ObjectData10")
    call ExecuteFunc("PF_ObjectData11")
    call ExecuteFunc("PF_ObjectData12")
endfunction

function DPS_ProfileUpdate takes nothing returns nothing
    local integer slot = GetPlayerId(GetLocalPlayer()) + 1
    local integer i = 0
    local integer file
    local integer live
    local integer total
    local string payload = "P1"
    local string saved
    local string field
    local string label
    local string display = "|cffffcc00My Stats|r    This match / Lifetime|n|n"
    if slot > 12 or GetPlayerController(GetLocalPlayer()) != MAP_CONTROL_USER or IsPlayerObserver(GetLocalPlayer()) then
        if DPS_Personal then
            call BlzFrameSetText(DPS_ProfileText, "|cffffcc00My Stats|r|n|n" + WalletText())
        endif
        return
    endif
    if udg_orig_player_name[slot] == null or udg_orig_player_name[slot] == "" then
        return
    endif
    if not DPS_ProfileLoaded then
        set DPS_ProfileLoaded = true
        set DPS_ProfilePath = "FootmenFrenzy\\799X\\stats-" + I2S(StringHash(udg_orig_player_name[slot])) + ".pld"
        set file = s__File_open(DPS_ProfilePath)
        set saved = s__File_readAndClose(file)
        if SubString(saved, 0, 2) == "P1" and SubString(saved, 82, StringLength(saved)) == I2S(StringHash(SubString(saved, 0, 82) + DPS_ProfilePath)) then
            loop
                exitwhen i == 8
                set field = SubString(saved, 2 + 10*i, 12 + 10*i)
                set DPS_Prior[i] = BlzBitXor(S2I(field), DPS_Mask(i))
                set i = i + 1
            endloop
        endif
        set i = 0
    endif
    loop
        exitwhen i == 8
        set live = DPS_Current(slot, i)
        set total = DPS_Prior[i] + live
        set payload = payload + DPS_Field(BlzBitXor(total, DPS_Mask(i)))
        if DPS_Personal then
            if i == 0 then
                set label = "Unit kills"
            elseif i == 1 then
                set label = "Unit deaths"
            elseif i == 2 then
                set label = "Assists"
            elseif i == 3 then
                set label = "Hero kills"
            elseif i == 4 then
                set label = "Hero deaths"
            elseif i == 5 then
                set label = "Hill captures"
            elseif i == 6 then
                set label = "Buildings destroyed"
            elseif i == 7 then
                set label = "Transmutes landed"
            endif
            set display = display + label + "     " + I2S(live) + " / " + I2S(total) + "|n"
        endif
        set i = i + 1
    endloop
    if DPS_Personal then
        call BlzFrameSetText(DPS_ProfileText, display + "|n" + WalletText())
    endif
    if payload != DPS_LastPayload then
        set file = s__File_open(DPS_ProfilePath)
        call s__File_write(file, payload + I2S(StringHash(payload + DPS_ProfilePath)))
        call s__File_close(file)
        set DPS_LastPayload = payload
    endif
endfunction

function PF_CareerPath takes integer kind, integer page returns string
    return "FootmenFrenzy\\799X\\collection-"+I2S(StringHash(WalletAccount))+"-"+I2S(kind)+"-"+I2S(page)+".pld"
endfunction

function PF_CareerAdd takes integer kind, integer id returns nothing
    if not HaveSavedInteger(PF_local,kind,id) then
        call SaveInteger(PF_local,kind,id,0)
        call SaveInteger(PF_local,kind+10,PF_careerCount[kind],id)
        set PF_careerCount[kind] = PF_careerCount[kind]+1
    endif
endfunction

function PF_LoadCareer takes integer kind returns nothing
    local string data
    local integer page = 0
    local integer offset
    local integer id
    local integer n
    loop
        set data = s__File_readAndClose(s__File_open(PF_CareerPath(kind,page)))
        exitwhen SubString(data,0,2) != "C1"
        set n = StringLength(data)-2
        exitwhen n < 0 or n > 800 or ModuloInteger(n,20) != 0
        set offset = 2
        loop
            exitwhen offset > n
            set id = S2I(SubString(data,offset,offset+10))
            call PF_CareerAdd(kind,id)
            call SaveInteger(PF_local,kind,id,S2I(SubString(data,offset+10,offset+20)))
            set offset = offset+20
        endloop
        exitwhen n < 800
        set page = page+1
    endloop
endfunction

function PF_SaveCareer takes integer slot, integer kind returns nothing
    local integer k = slot*10+kind
    local integer i = 0
    local integer id
    local integer page = 0
    local integer total
    local string data = "C1"
    loop
        exitwhen i >= PF_counts[k]
        call PF_CareerAdd(kind,LoadInteger(PF_data,300+k,i))
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= PF_careerCount[kind]
        set id = LoadInteger(PF_local,kind+10,i)
        set total = LoadInteger(PF_local,kind,id)+LoadInteger(PF_data,k,id)
        set data = data+DPS_Field(id)+DPS_Field(total)
        set i = i+1
        if ModuloInteger(i,40) == 0 or i == PF_careerCount[kind] then
            if data != LoadStr(PF_local,kind+20,page) then
                call s__File_close(s__File_write(s__File_open(PF_CareerPath(kind,page)),data))
                call SaveStr(PF_local,kind+20,page,data)
            endif
            set data = "C1"
            set page = page+1
        endif
    endloop
endfunction

function PF_MySlot takes nothing returns integer
    local integer slot = GetPlayerId(GetLocalPlayer())+1
    if SoloSub_playerForObserver[slot-1] > 0 then
        return SoloSub_playerForObserver[slot-1]
    endif
    return slot
endfunction

function PF_Economy takes integer s, integer i returns integer
    if s > 12 or not FF_gr_participant[s] then
        return 0
    endif
    if i == 0 then
        return 1
    elseif i == 1 then
        if FFR4Pro then
            return 1
        endif
        return 0
    elseif i == 2 then
        return PF_Number(s,PF_poolOutMetric)
    elseif i == 3 then
        return PF_Number(s,PF_poolInMetric)
    elseif i == 4 then
        return PF_Number(s,PF_sentMetric)
    elseif i == 5 then
        return PF_Number(s,PF_receivedMetric)
    elseif FFR4Pro then
        if i == 6 then
            return PF_Number(s,PF_poolOutMetric)
        endif
        return PF_Number(s,PF_poolInMetric)
    endif
    return 0
endfunction

function PF_EconomyFile takes integer s returns nothing
    local string path = PF_CareerPath(0,0)
    local string data = "E1"
    local string saved
    local integer i = 0
    if not PF_careerReady then
        set saved = s__File_readAndClose(s__File_open(path))
        if StringLength(saved) == 82 and SubString(saved,0,2) == "E1" then
            loop
                exitwhen i == 8
                set PF_priorEco[i] = S2I(SubString(saved,2+i*10,12+i*10))
                set i = i+1
            endloop
        endif
    endif
    set i = 0
    loop
        exitwhen i == 8
        set data = data+DPS_Field(PF_priorEco[i]+PF_Economy(s,i))
        set i = i+1
    endloop
    if data != PF_lastEco then
        call s__File_close(s__File_write(s__File_open(path),data))
        set PF_lastEco = data
    endif
endfunction

function PF_ReceiveHistory takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local string data = BlzGetTriggerSyncData()
    local integer kind = S2I(SubString(data,0,1))
    local integer ix = 1
    local integer id
    local integer amount
    local integer key = 3000+s*10+kind
    if kind < 0 or kind > 4 or StringLength(data) > 201 or ModuloInteger(StringLength(data)-1,20) != 0 then
        return
    endif
    loop
        exitwhen ix+20 > StringLength(data)
        set id = S2I(SubString(data,ix,ix+10))
        set amount = S2I(SubString(data,ix+10,ix+20))
        if id >= 0 and amount >= 0 and DPS_Field(id)+DPS_Field(amount) == SubString(data,ix,ix+20) and not HaveSavedInteger(PF_history,key,id) and PF_historyN[s*5+kind] < 4096 then
            call SaveInteger(PF_history,key,id,amount)
            call SaveInteger(PF_history,key+500,PF_historyN[s*5+kind],id)
            set PF_historyN[s*5+kind] = PF_historyN[s*5+kind]+1
            set PF_dirty = true
        endif
        set ix = ix+20
    endloop
endfunction

function PF_SendHistory takes nothing returns nothing
    local string data
    local integer id
    local integer amount
    local integer n = 0
    local integer s = PF_MySlot()
    if not PF_careerReady or PF_sendKind > 4 or (GetPlayerId(GetLocalPlayer()) < 12 and not DPS_ProfileLoaded and not IsPlayerObserver(GetLocalPlayer()) and GetPlayerController(GetLocalPlayer()) == MAP_CONTROL_USER) then
        return
    endif
    set data = I2S(PF_sendKind)
    if PF_sendKind == 0 then
        loop
            exitwhen n == 8 or PF_sendIndex == 16
            set id = PF_sendIndex
            if id < 8 then
                set amount = PF_priorEco[id]
            else
                set amount = DPS_Prior[id-8]
            endif
            set data = data+DPS_Field(id)+DPS_Field(amount)
            set PF_sendIndex = PF_sendIndex+1
            set n = n+1
        endloop
        if PF_sendIndex == 16 then
            set PF_sendKind = 1
            set PF_sendIndex = 0
        endif
    else
        loop
            exitwhen n == 8 or PF_sendIndex >= PF_careerCount[PF_sendKind]
            set id = LoadInteger(PF_local,PF_sendKind+10,PF_sendIndex)
            set amount = LoadInteger(PF_local,PF_sendKind,id)
            if amount > 0 then
                set data = data+DPS_Field(id)+DPS_Field(amount)
                set n = n+1
            endif
            set PF_sendIndex = PF_sendIndex+1
        endloop
        if PF_sendIndex >= PF_careerCount[PF_sendKind] then
            set PF_sendKind = PF_sendKind+1
            set PF_sendIndex = 0
        endif
    endif
    if StringLength(data) > 1 then
        call BlzSendSyncData("FFCareer22",data)
    endif
endfunction

function PF_CareerRecords takes integer account returns nothing
    local integer kind = 0
    local integer i
    local integer id
    local integer base
    local integer total
    local integer s = account
    local integer k
    local integer key
    local string row
    local string head
    local string field
    if WalletPlayedSlot[account-1] > 0 then
        set s = WalletPlayedSlot[account-1]
    endif
    loop
        exitwhen kind > 4
        set k = s*10+kind
        set key = 3000+account*10+kind
        set head = "career,"+I2S(account)+","+I2S(kind)+","
        set row = head
        set i = 0
        loop
            exitwhen i >= PF_historyN[account*5+kind]
            set id = LoadInteger(PF_history,key+500,i)
            set base = LoadInteger(PF_history,key,id)
            if kind == 0 then
                if id < 8 then
                    set total = base+PF_Economy(s,id)
                elseif id < 16 then
                    set total = base+PF_Number(s,PF_combatFirst+id-8)
                else
                    set total = base
                endif
            else
                set total = base+LoadInteger(PF_data,k,id)
            endif
            set field = I2S(id)+"="+I2S(total)
            if StringLength(row)+StringLength(field)+1 > FF_PRELOAD_MAX then
                call Preload(row)
                set row = head
            endif
            if row != head then
                set row = row+","
            endif
            set row = row+field
            set i = i+1
        endloop
        if kind > 0 then
            set i = 0
            loop
                exitwhen i >= PF_counts[k]
                set id = LoadInteger(PF_data,300+k,i)
                if not HaveSavedInteger(PF_history,key,id) then
                    set field = I2S(id)+"="+I2S(LoadInteger(PF_data,k,id))
                    if StringLength(row)+StringLength(field)+1 > FF_PRELOAD_MAX then
                        call Preload(row)
                        set row = head
                    endif
                    if row != head then
                        set row = row+","
                    endif
                    set row = row+field
                endif
                set i = i+1
            endloop
        endif
        if row != head then
            call Preload(row)
        endif
        set kind = kind+1
    endloop
    if HaveSavedInteger(PF_history,3000+account*10,7) then
        set key = 3000+account*10
        set base = LoadInteger(PF_history,key,6)+PF_Economy(s,6)
        set total = LoadInteger(PF_history,key,1)+PF_Economy(s,1)
        call Preload("career_pool,"+I2S(account)+",avg_pro_sent="+I2S(PF_Average(base,total))+",avg_pro_received="+I2S(PF_Average(LoadInteger(PF_history,key,7)+PF_Economy(s,7),total)))
    endif
endfunction

function PF_WriteCareer takes nothing returns nothing
    call PF_CareerRecords(PF_exportSlot)
endfunction

function PF_UpdateCareer takes nothing returns nothing
    local integer kind = 1
    local integer s = PF_MySlot()
    if WalletAccount == null or WalletAccount == "" or FF_IsBotName(WalletAccount) then
        return
    endif
    loop
        exitwhen kind > 4
        if not PF_careerReady then
            call PF_LoadCareer(kind)
        endif
        call PF_SaveCareer(s,kind)
        set kind = kind+1
    endloop
    call PF_EconomyFile(s)
    set PF_careerReady = true
endfunction

function PF_Clock takes integer seconds returns string
    return I2S(seconds/60)+":"+FF_Pad2(ModuloInteger(seconds,60))
endfunction

function PF_Text takes real x, real y, real width, real height, real font returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","",PF_root,"",0)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,x,-y)
    call BlzFrameSetSize(f,width,height)
    call BlzFrameSetFont(f,"Fonts\\FRIZQT__.TTF",font,0)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function PF_Button takes trigger t, real x, real y, real width returns framehandle
    local framehandle f = BlzCreateFrame("ScriptDialogButton",PF_root,0,0)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,x,-y)
    call BlzFrameSetSize(f,width,0.031)
    call BlzFrameSetLevel(f,101)
    call BlzTriggerRegisterFrameEvent(t,f,FRAMEEVENT_CONTROL_CLICK)
    return f
endfunction

function PF_Art takes integer id returns string
    local string art = LoadStr(PF_prices,3,id)
    if art == null or art == "" then
        set art = BlzGetAbilityIcon(id)
    endif
    if art == null or art == "" then
        return "ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp"
    endif
    return art
endfunction

function PF_Name takes integer id returns string
    local string name = GetObjectName(id)
    if name == null or name == "" or name == "Default string" then
        return FF_us_Id2S(id)
    endif
    return name
endfunction

function PF_Row takes integer i, string title, string value, string extra, string art returns nothing
    local real x = -0.174
    local real y = 0.162+I2R(i)*0.042
    if art != "" and art != null then
        set x = -0.141
        call BlzFrameSetTexture(PF_icon[i],art,0,true)
        call BlzFrameSetVisible(PF_icon[i],true)
    endif
    call BlzFrameClearAllPoints(PF_line[i])
    call BlzFrameSetPoint(PF_line[i],FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,x,-y)
    call BlzFrameSetSize(PF_line[i],0.132-x,0.038)
    call BlzFrameSetText(PF_line[i],title)
    call BlzFrameSetText(PF_value[i],value)
    call BlzFrameSetText(PF_extra[i],extra)
    call BlzFrameSetVisible(PF_stripe[i],ModuloInteger(i,2) == 0)
endfunction

function PF_Columns takes string field, string value, string extra returns nothing
    call BlzFrameSetText(PF_col[0],field)
    call BlzFrameSetText(PF_col[1],value)
    call BlzFrameSetText(PF_col[2],extra)
endfunction

function PF_Activity takes integer s, integer r, integer ix returns nothing
    local integer k = 1000+s*10
    local integer id = LoadInteger(PF_data,k+1,ix)
    local integer gold = LoadInteger(PF_data,k+2,ix)
    local integer other = LoadInteger(PF_data,k+3,ix)
    local string name = LoadStr(PF_prices,4,StringHash(LoadStr(PF_data,k,ix)))
    local string debit = ""
    if id != 0 then
        set name = name+"  "+PF_Name(id)
    endif
    if other != 0 then
        set name = name+"  "+GetPlayerName(Player(other-1))
    endif
    if gold >= 0 then
        set debit = I2S(gold)
    endif
    call PF_Row(r,PF_Clock(LoadInteger(PF_data,k+4,ix))+"    "+name,debit,I2S(LoadInteger(PF_data,k+5,ix)),"")
endfunction

function PF_StatRow takes integer r, integer s, integer id returns nothing
    local integer amount
    local integer account = GetPlayerId(GetLocalPlayer())+1
    local string lifetime = ""
    if id >= PF_metrics then
        set amount = PF_priorEco[1]+PF_Economy(s,1)
        if id == PF_metrics then
            call PF_Row(r,"Pro matches played","",I2S(amount),"")
        elseif id == PF_metrics+1 then
            call PF_Row(r,"Average gold pooled per Pro match","",I2S(PF_Average(PF_priorEco[6]+PF_Economy(s,6),amount)),"")
        elseif id == PF_metrics+2 then
            call PF_Row(r,"Average gold received per Pro match","",I2S(PF_Average(PF_priorEco[7]+PF_Economy(s,7),amount)),"")
        elseif id == PF_metrics+3 then
            call PF_Row(r,"Total gold pooled","",I2S(PF_priorEco[2]+PF_Economy(s,2)),"")
        else
            call PF_Row(r,"Total pooled gold received","",I2S(PF_priorEco[3]+PF_Economy(s,3)),"")
        endif
    elseif id == 64 then
        call PF_Row(r,PF_label[id],HUD_WalletValue(),"","")
    else
        if id >= PF_casinoFirst then
            set s = account
        endif
        set amount = PF_Number(s,id)
        if id >= PF_combatFirst and id < PF_combatFirst+8 and DPS_ProfileLoaded and s == account then
            set lifetime = I2S(DPS_Prior[id-PF_combatFirst]+amount)
        endif
        call PF_Row(r,PF_label[id],I2S(amount),lifetime,"")
    endif
endfunction

function PF_UsageRow takes integer s, integer r, integer ix returns nothing
    local integer kind = FF_US_TECH
    local integer k
    local integer id
    local string uses
    loop
        set k = FF_us_CountKey(s,kind)
        exitwhen ix < FF_us_n[k] or kind == FF_US_TOWER
        set ix = ix-FF_us_n[k]
        if kind == FF_US_TECH then
            set kind = FF_US_SPELL
        elseif kind == FF_US_SPELL then
            set kind = FF_US_CMD
        else
            set kind = FF_US_TOWER
        endif
    endloop
    set id = LoadInteger(FF_us_ht,FF_us_OrderKey(s,kind),ix)
    set uses = I2S(LoadInteger(FF_us_ht,k,id))
    if kind == FF_US_CMD then
        call PF_Row(r,FF_us_cmd[id],FF_us_catName[kind],uses,"")
    else
        call PF_Row(r,PF_Name(id),FF_us_catName[kind],uses,PF_Art(id))
    endif
endfunction

function PF_ProfileView takes nothing returns nothing
    local integer s = PF_MySlot()
    local integer kind = PF_section
    local integer count = PF_sectionCount[kind]
    local integer i = 0
    local integer ix
    local integer id
    local integer amount
    local string empty = "No entries yet this match"
    call BlzFrameSetText(PF_title,GetPlayerName(GetLocalPlayer()))
    call BlzFrameSetText(PF_subtitle,"Player profile")
    call BlzFrameSetText(PF_sectionTitle,PF_sectionName[kind])
    call PF_Columns("Statistic","This match","Lifetime")
    if kind >= 1 and kind <= 4 then
        set count = PF_careerCount[kind]
        call PF_Columns(PF_sectionName[kind],"This match","Lifetime")
        set empty = "No entries recorded yet"
    elseif kind == 5 then
        set count = PF_logCount[s]
        call PF_Columns("Time     Action","Gold","Balance")
    elseif kind == 6 then
        call PF_Columns("Account activity","Amount","")
    elseif kind == 7 then
        set count = FF_us_n[FF_us_CountKey(s,FF_US_TECH)]+FF_us_n[FF_us_CountKey(s,FF_US_SPELL)]+FF_us_n[FF_us_CountKey(s,FF_US_CMD)]+FF_us_n[FF_us_CountKey(s,FF_US_TOWER)]
        call PF_Columns("Action","Type","Uses")
    elseif s > 12 then
        set count = 0
        set empty = "Match statistics appear when you control a player."
    elseif kind == 10 then
        call PF_Columns("Statistic","This match","")
    endif
    set PF_pages = IMaxBJ(1,(count+8)/9)
    set PF_page = IMinBJ(PF_page,PF_pages-1)
    loop
        set ix = PF_page*9+i
        exitwhen i >= 9 or ix >= count
        if kind >= 1 and kind <= 4 then
            set id = LoadInteger(PF_local,kind+10,ix)
            set amount = LoadInteger(PF_data,s*10+kind,id)
            call PF_Row(i,PF_Name(id),I2S(amount),I2S(amount+LoadInteger(PF_local,kind,id)),PF_Art(id))
        elseif kind == 5 then
            call PF_Activity(s,i,ix)
        elseif kind == 7 then
            call PF_UsageRow(s,i,ix)
        else
            call PF_StatRow(i,s,PF_metricOrder[kind*100+ix])
        endif
        set i = i+1
    endloop
    if count == 0 then
        call PF_Row(0,empty,"","","")
    endif
endfunction

function PF_TeamValue takes integer side, integer metric returns string
    local integer s = 1
    local integer total = 0
    local integer transfers = 0
    if PF_key[metric] == "level" or PF_key[metric] == "tech" then
        return ""
    endif
    loop
        exitwhen s > 12
        if FF_gr_participant[s] and FF_gr_IsMember(s,side) then
            if PF_key[metric] == "avg_sent" then
                set total = total+PF_Number(s,PF_poolOutMetric)
                set transfers = transfers+PF_Number(s,PF_sentMetric)
            elseif PF_key[metric] == "avg_recv" then
                set total = total+PF_Number(s,PF_poolInMetric)
                set transfers = transfers+PF_Number(s,PF_receivedMetric)
            else
                set total = total+PF_Number(s,metric)
            endif
        endif
        set s = s+1
    endloop
    if PF_key[metric] == "avg_sent" or PF_key[metric] == "avg_recv" then
        set total = PF_Average(total,transfers)
    endif
    return I2S(total)
endfunction

function PF_Color takes integer s returns string
    local integer id = GetHandleId(GetPlayerColor(Player(s-1)))
    if id < 10 then
        return "ReplaceableTextures\\TeamColor\\TeamColor0"+I2S(id)+".blp"
    endif
    return "ReplaceableTextures\\TeamColor\\TeamColor"+I2S(id)+".blp"
endfunction

function PF_ResultsView takes nothing returns nothing
    local integer side = 1
    local integer s
    local integer r = 1
    local integer c = 0
    local integer k
    local string title = "Match results"
    local string control = ""
    local string name
    local integer board = PF_section
    set PF_pages = 1
    if PF_section == 1 or PF_section == 3 then
        set PF_pages = 2
    elseif PF_section == 4 then
        set PF_pages = 3
    endif
    if PF_page > 0 then
        if PF_section == 1 then
            set board = 9
        elseif PF_section == 3 then
            set board = 6
        elseif PF_section == 4 then
            set board = 6+PF_page
        endif
    endif
    set s = PF_MySlot()
    if CAS_winner == 0 then
        set title = "Draw"
    elseif s <= 12 and FF_gr_participant[s] then
        if CAS_winner == -s or (CAS_winner > 0 and FF_gr_IsMember(s,CAS_winner)) then
            set title = "Victory"
        else
            set title = "Defeat"
        endif
    endif
    call BlzFrameSetText(PF_title,"|cffffcc68"+title+"|r     Footmen Frenzy")
    call BlzFrameSetText(PF_board[0],"Team  /  Player")
    loop
        exitwhen c >= 5
        call BlzFrameSetText(PF_board[c+1],PF_columnTitle[board*5+c])
        set c = c+1
    endloop
    loop
        exitwhen side > FF_gr_SideCount()
        if FF_gr_SideParticipated(side) then
            set name = FF_gr_SideLabel(side)+"   /   Total"
            if CAS_winner == side then
                set name = name+"   /   Winner"
            endif
            call BlzFrameSetText(PF_board[r*6],"|cffffcc68"+name+"|r")
            set c = 0
            loop
                exitwhen c >= 5
                call BlzFrameSetText(PF_board[r*6+c+1],"|cffffcc68"+PF_TeamValue(side,PF_columns[board*5+c])+"|r")
                set c = c+1
            endloop
            set r = r+1
            set s = 1
            loop
                exitwhen s > 12
                if FF_gr_participant[s] and FF_gr_IsMember(s,side) then
                    call BlzFrameSetVisible(PF_band[r],true)
                    call BlzFrameSetTexture(PF_band[r],PF_Color(s),0,true)
                    set name = udg_orig_player_name[s]
                    if name == null or name == "" then
                        set name = GetPlayerName(Player(s-1))
                    endif
                    if CAS_winner == -s then
                        set name = "|cffffcc68"+name+"   /   Winner|r"
                    endif
                    call BlzFrameSetText(PF_board[r*6],name)
                    if PF_lastHero[s] != 0 then
                        call BlzFrameSetTexture(PF_portrait[r],PF_Art(PF_lastHero[s]),0,true)
                        call BlzFrameSetVisible(PF_portrait[r],true)
                    endif
                    set c = 0
                    loop
                        exitwhen c >= 5
                        set k = PF_columns[board*5+c]
                        call BlzFrameSetText(PF_board[r*6+c+1],I2S(PF_Number(s,k)))
                        set c = c+1
                    endloop
                    set r = r+1
                endif
                set s = s+1
            endloop
            if PF_hillSeconds[side] > 0 then
                set control = control+"    "+FF_gr_SideLabel(side)+" "+PF_Clock(PF_hillSeconds[side])
            endif
        endif
        set side = side+1
    endloop
    if control != "" then
        set control = "     Hill control"+control
    endif
    call BlzFrameSetText(PF_subtitle,"Final standings    "+PF_Clock(PF_endSecond)+control+"    Wallet earnings   "+I2S(PF_rewards[GetPlayerId(GetLocalPlayer())+1]))
endfunction

function PF_AlignNumber takes framehandle f returns nothing
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_RIGHT)
    call BlzFrameSetFont(f,"CasinoUI\\Bold.ttf",0.013,0)
endfunction

function PF_CreateProfile takes trigger t returns nothing
    local integer i = 0
    local real y
    local framehandle f
    set PF_sectionTitle = PF_Text(-0.182,0.084,0.54,0.040,0.022)
    call BlzFrameSetFont(PF_sectionTitle,"CasinoUI\\Bold.ttf",0.021,0)
    set PF_col[0] = PF_Text(-0.174,0.131,0.306,0.023,0.011)
    set PF_col[1] = PF_Text(0.136,0.131,0.106,0.023,0.011)
    set PF_col[2] = PF_Text(0.249,0.131,0.108,0.023,0.011)
    loop
        exitwhen i >= 3
        call BlzFrameSetTextColor(PF_col[i],BlzConvertColor(255,232,202,146))
        if i > 0 then
            call BlzFrameSetTextAlignment(PF_col[i],TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_RIGHT)
        endif
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 11
        set PF_menu[i] = PF_Button(t,-0.366,0.091+I2R(i)*0.041,0.158)
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 9
        set y = 0.162+I2R(i)*0.042
        set f = BlzCreateFrameByType("BACKDROP","",PF_root,"",i)
        call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.182,-y)
        call BlzFrameSetSize(f,0.548,0.038)
        call BlzFrameSetTexture(f,"ReplaceableTextures\\TeamColor\\TeamColor08.blp",0,true)
        call BlzFrameSetVertexColor(f,BlzConvertColor(80,149,147,135))
        set PF_stripe[i] = f
        set PF_icon[i] = BlzCreateFrameByType("BACKDROP","",PF_root,"",i)
        call BlzFrameSetPoint(PF_icon[i],FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.174,-y-0.006)
        call BlzFrameSetSize(PF_icon[i],0.026,0.026)
        set PF_line[i] = PF_Text(-0.174,y,0.306,0.038,0.013)
        set PF_value[i] = PF_Text(0.136,y,0.106,0.038,0.013)
        set PF_extra[i] = PF_Text(0.249,y,0.108,0.038,0.013)
        call PF_AlignNumber(PF_value[i])
        call PF_AlignNumber(PF_extra[i])
        call BlzFrameSetTextColor(PF_extra[i],BlzConvertColor(255,232,218,190))
        set i = i+1
    endloop
    set f = null
endfunction

function PF_RenderNavigation takes nothing returns nothing
    local integer i = 0
    local integer section
    loop
        exitwhen i >= 6
        call BlzFrameSetVisible(PF_tab[i],PF_results)
        if PF_results then
            call BlzFrameSetText(PF_tab[i],PF_tabName[10+i])
            call BlzFrameSetEnable(PF_tab[i],i != PF_section)
        endif
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 11
        call BlzFrameSetVisible(PF_menu[i],not PF_results)
        if not PF_results then
            set section = PF_menuOrder[i]
            if section == PF_section then
                call BlzFrameSetText(PF_menu[i],"|cffffd784>  "+PF_sectionName[section]+"|r")
            else
                call BlzFrameSetText(PF_menu[i],PF_sectionName[section])
            endif
        endif
        set i = i+1
    endloop
    call BlzFrameSetVisible(PF_sectionTitle,not PF_results)
    set i = 0
    loop
        exitwhen i >= 3
        call BlzFrameSetVisible(PF_col[i],not PF_results)
        set i = i+1
    endloop
endfunction

function PF_Render takes nothing returns nothing
    local integer i = 0
    if not PF_visible then
        return
    endif
    loop
        exitwhen i >= 9
        call BlzFrameSetVisible(PF_stripe[i],false)
        call BlzFrameSetText(PF_extra[i],"")
        call BlzFrameSetText(PF_line[i],"")
        call BlzFrameSetText(PF_value[i],"")
        call BlzFrameSetVisible(PF_icon[i],false)
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 102
        call BlzFrameSetText(PF_board[i],"")
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 17
        call BlzFrameSetVisible(PF_band[i],false)
        call BlzFrameSetVisible(PF_portrait[i],false)
        set i = i+1
    endloop
    call PF_RenderNavigation()
    if PF_results then
        call PF_ResultsView()
    else
        call PF_ProfileView()
    endif
    call BlzFrameSetVisible(PF_prev,PF_page > 0)
    call BlzFrameSetVisible(PF_next,PF_page+1 < PF_pages)
    call BlzFrameSetText(PF_footer,"")
    if PF_pages > 1 then
        call BlzFrameSetText(PF_footer,I2S(PF_page+1)+" / "+I2S(PF_pages))
    endif
    call BlzFrameSetVisible(PF_back,not PF_results)
    call BlzFrameSetVisible(PF_continue,PF_results)
    if PF_results then
        call BlzFrameSetEnable(PF_continue,PF_verdict[GetPlayerId(GetLocalPlayer())+1] != 0 or IsPlayerObserver(GetLocalPlayer()) or not FF_gr_participant[GetPlayerId(GetLocalPlayer())+1])
    endif
endfunction

function PF_Open takes boolean results returns nothing
    local integer w = BlzGetLocalClientWidth()
    local integer h = BlzGetLocalClientHeight()
    set PF_visible = true
    set PF_results = results
    call BlzFrameClearAllPoints(PF_subtitle)
    if results then
        call BlzFrameSetPoint(PF_subtitle,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.365,-0.069)
        call BlzFrameSetSize(PF_subtitle,0.735,0.019)
    else
        call BlzFrameSetPoint(PF_subtitle,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.100,-0.051)
        call BlzFrameSetSize(PF_subtitle,0.370,0.019)
    endif
    set PF_section = 0
    set PF_page = 0
    if h > 0 then
        call BlzFrameSetSize(PF_root,RMaxBJ(0.8,0.6*I2R(w)/I2R(h)),0.6)
    endif
    call BlzFrameSetVisible(DPS_Panel,false)
    call BlzFrameSetVisible(PF_root,true)
    call PF_Render()
endfunction

function PF_Click takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local integer i = 0
    local framehandle f = BlzGetTriggerFrame()
    // Native dialogs allocate handles and must run on all clients.
    if f == PF_continue and PF_verdict[s] > 0 then
        if PF_verdict[s] == 1 then
            set PF_verdict[s] = -1
            call CustomVictoryBJ(GetTriggerPlayer(),true,true)
        else
            set PF_verdict[s] = -1
            call CustomDefeatBJ(GetTriggerPlayer(),PF_message[s])
        endif
    endif
    if GetLocalPlayer() == GetTriggerPlayer() then
        if f == PF_back or f == PF_continue then
            set PF_visible = false
            call BlzFrameSetVisible(PF_root,false)
            if not PF_results then
                call BlzFrameSetVisible(DPS_Panel,true)
            endif
        elseif f == PF_prev then
            set PF_page = IMaxBJ(0,PF_page-1)
        elseif f == PF_next then
            set PF_page = IMinBJ(PF_pages-1,PF_page+1)
        else
            loop
                exitwhen i >= 11
                if not PF_results and f == PF_menu[i] then
                    set PF_section = PF_menuOrder[i]
                    set PF_page = 0
                elseif PF_results and i < 6 and f == PF_tab[i] then
                    set PF_section = i
                    set PF_page = 0
                endif
                set i = i+1
            endloop
        endif
        call BlzFrameSetFocus(f,false)
        call PF_Render()
    endif
    set f = null
endfunction

function PF_Create takes nothing returns nothing
    local trigger t = CreateTrigger()
    local integer i = 0
    local integer c
    local real x
    local real y
    local real w
    set PF_root = BlzCreateFrame("EscMenuBackdrop",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),0,0)
    call BlzFrameSetLevel(PF_root,100)
    call BlzFrameSetAbsPoint(PF_root,FRAMEPOINT_TOP,0.4,0.6)
    call BlzFrameSetSize(PF_root,0.8,0.6)
    set PF_title = PF_Text(-0.100,0.018,0.370,0.035,0.020)
    call BlzFrameSetFont(PF_title,"CasinoUI\\Bold.ttf",0.020,0)
    set PF_subtitle = PF_Text(-0.365,0.069,0.735,0.019,0.010)
    set PF_back = PF_Button(t,0.284,0.021,0.081)
    call BlzFrameSetText(PF_back,"Back")
    set PF_continue = PF_Button(t,0.284,0.021,0.081)
    call BlzFrameSetText(PF_continue,"Continue")
    loop
        exitwhen i >= 6
        set PF_tab[i] = PF_Button(t,-0.366+I2R(i)*0.123,0.089,0.118)
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 17
        set y = 0.134+I2R(i)*0.024
        set PF_band[i] = BlzCreateFrameByType("BACKDROP","",PF_root,"",i)
        call BlzFrameSetPoint(PF_band[i],FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.364,-y)
        call BlzFrameSetSize(PF_band[i],0.728,0.022)
        call BlzFrameSetAlpha(PF_band[i],74)
        set PF_portrait[i] = BlzCreateFrameByType("BACKDROP","",PF_root,"",i)
        call BlzFrameSetPoint(PF_portrait[i],FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.361,-y)
        call BlzFrameSetSize(PF_portrait[i],0.022,0.022)
        set c = 0
        loop
            exitwhen c >= 6
            if c == 0 then
                set x = -0.333
                set w = 0.197
            else
                set x = -0.135+I2R(c-1)*0.100
                set w = 0.098
            endif
            set PF_board[i*6+c] = PF_Text(x,y,w,0.022,0.011)
            set c = c+1
        endloop
        set i = i+1
    endloop
    call PF_CreateProfile(t)
    set PF_prev = PF_Button(t,-0.170,0.548,0.085)
    set PF_next = PF_Button(t,0.084,0.548,0.085)
    call BlzFrameSetText(PF_prev,"Previous")
    call BlzFrameSetText(PF_next,"Next")
    set PF_footer = PF_Text(-0.030,0.548,0.070,0.031,0.012)
    call TriggerAddAction(t,function PF_Click)
    call BlzFrameSetVisible(PF_root,false)
    set t = null
endfunction
