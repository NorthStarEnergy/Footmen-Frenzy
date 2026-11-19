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

// Store numeric data once. The UI and file writer read this same ordered journal.
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
