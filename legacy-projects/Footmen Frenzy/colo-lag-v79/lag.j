// Stock cumulative XP thresholds, verified against this map's gameplay constants.
function P79_LevelXP takes integer level returns integer
    if level <= 1 then
        return 0
    endif
    return 50 * level * (level + 1) - 100
endfunction

function P79_FractionalLevel takes unit u returns real
    local integer level = GetHeroLevel(u)
    local integer lower = P79_LevelXP(level)
    local integer upper = P79_LevelXP(level + 1)
    return I2R(level) + RMaxBJ(0.00, RMinBJ(1.00, I2R(GetHeroXP(u) - lower) / I2R(upper - lower)))
endfunction

function P79_NextTarget takes integer level returns integer
    if level < 10 then
        return 10
    endif
    if level < 13 then
        return 13
    endif
    if level < 16 then
        return 16
    endif
    return 0
endfunction

// A strict majority prevents one fed carry from qualifying an entire team.
function P79_TeamReached takes integer team, integer target returns boolean
    local integer pn = 1
    local integer count = 0
    local integer reached = 0
    local unit u
    if udg_force_defeat[team] then
        return false
    endif
    loop
        exitwhen pn > 12
        set u = udg_herO[pn]
        if udg_teamnumber[pn] == team and P67_ValidHero(u) then
            set count = count + 1
            if GetHeroLevel(u) >= target then
                set reached = reached + 1
            endif
        endif
        set pn = pn + 1
    endloop
    set u = null
    return count > 0 and reached * 2 > count
endfunction

function P79_TeamPresent takes integer team returns boolean
    local integer pn = 1
    if udg_force_defeat[team] then
        return false
    endif
    loop
        exitwhen pn > 12
        if udg_teamnumber[pn] == team and P67_ValidHero(udg_herO[pn]) then
            return true
        endif
        set pn = pn + 1
    endloop
    return false
endfunction

function P79_FieldAhead takes integer ownTeam, integer target returns boolean
    local integer team = 1
    local integer count = 0
    local integer opponents = 0
    loop
        exitwhen team > 4
        if team != ownTeam and P79_TeamPresent(team) then
            set opponents = opponents + 1
            if P79_TeamReached(team, target) then
                set count = count + 1
            endif
        endif
        set team = team + 1
    endloop
    return opponents > 0 and count * 2 > opponents
endfunction

function P79_Refresh takes nothing returns nothing
    local integer pn = 1
    local integer target
    local real now
    local real gap
    local unit u
    if not P67_Enabled() then
        return
    endif
    if P79_Clock == null then
        set P79_Clock = CreateTimer()
        call TimerStart(P79_Clock, 1000000.00, false, null)
    endif
    set now = TimerGetElapsed(P79_Clock)
    loop
        exitwhen pn > 12
        set u = udg_herO[pn]
        set target = 0
        if P67_ValidHero(u) and not udg_maphack[pn] and not udg_force_defeat[udg_teamnumber[pn]] then
            set target = P79_NextTarget(GetHeroLevel(u))
        endif
        if P79_Hero[pn] != u or P79_Target[pn] != target then
            set P79_Hero[pn] = u
            set P79_Target[pn] = target
            set P79_Active[pn] = false
            set P79_Waiting[pn] = false
        endif
        if target > 0 then
            set gap = I2R(target) - P79_FractionalLevel(u)
            if P79_FieldAhead(udg_teamnumber[pn], target) and (P79_Active[pn] or gap >= P79_MIN_GAP) then
                if not P79_Waiting[pn] then
                    set P79_Since[pn] = now
                    set P79_Waiting[pn] = true
                endif
                if now - P79_Since[pn] >= P79_LAG_SECONDS then
                    set P79_Active[pn] = true
                endif
            else
                set P79_Active[pn] = false
                set P79_Waiting[pn] = false
            endif
        else
            set P79_Active[pn] = false
            set P79_Waiting[pn] = false
        endif
        set pn = pn + 1
    endloop
    set u = null
endfunction

function P79_Extra takes integer baseXP, integer sharers, real gap, integer missing, integer allowance returns integer
    local real bonusRate
    if sharers <= 0 or missing <= 0 or allowance <= 0 then
        return 0
    endif
    set bonusRate = RMinBJ(P79_MAX_SHARE_BONUS, RMaxBJ(0.00, gap * P79_BONUS_PER_LEVEL))
    return IMinBJ(missing, IMinBJ(allowance, R2I(I2R(baseXP) * bonusRate / I2R(sharers))))
endfunction

// Run after normal death XP; only the extra grant is clamped to the milestone.
function P79_Pay takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer key = GetHandleId(t)
    local integer wave = LoadInteger(P79_Table, key, 0)
    local integer baseXP = LoadInteger(P79_Table, key, 1)
    local integer sharers = LoadInteger(P79_Table, key, 2)
    local integer pn = 1
    local integer target
    local integer budget
    local integer amount
    local integer level
    local unit u
    if P67_Enabled() then
        loop
            exitwhen pn > 12
            set u = LoadUnitHandle(P79_Table, key, 100 + pn)
            set target = LoadInteger(P79_Table, key, 200 + pn)
            if P67_ValidHero(u) and IsUnitAliveBJ(u) and P79_Active[pn] and P79_Target[pn] == target and not udg_maphack[pn] then
                set budget = wave * 16 + pn
                set level = GetHeroLevel(u)
                if P79_WaveCap[budget] == 0 then
                    set P79_WaveCap[budget] = R2I(I2R(P79_LevelXP(level + 1) - P79_LevelXP(level)) * P79_WAVE_LEVEL_CAP)
                endif
                set amount = P79_Extra(baseXP, sharers, I2R(target) - P79_FractionalLevel(u), P79_LevelXP(target) - GetHeroXP(u), P79_WaveCap[budget] - P79_WaveBonus[budget])
                if amount > 0 then
                    set P79_WaveBonus[budget] = P79_WaveBonus[budget] + amount
                    call SetHeroXP(u, GetHeroXP(u) + amount, true)
                endif
            endif
            set pn = pn + 1
        endloop
        call P67_Refresh()
    endif
    call FlushChildHashtable(P79_Table, key)
    call DestroyTimer(t)
    set u = null
    set t = null
endfunction

function P79_OnDeath takes nothing returns nothing
    local unit dying = GetTriggerUnit()
    local unit killer = GetKillingUnit()
    local integer key = GetHandleId(dying)
    local integer wave = LoadInteger(P79_Table, key, 0)
    local integer pn = 1
    local integer killerSlot
    local integer team
    local integer level
    local integer sharers = 0
    local integer timerKey
    local unit u
    local timer t
    if wave == 0 or LoadUnitHandle(P79_Table, key, 1) != dying then
        set dying = null
        set killer = null
        return
    endif
    // Consume the tag even if there is no eligible killer or this mode is disabled.
    call FlushChildHashtable(P79_Table, key)
    if not P67_Enabled() or killer == null then
        set dying = null
        set killer = null
        return
    endif
    set killerSlot = GetPlayerId(GetOwningPlayer(killer)) + 1
    if killerSlot < 1 or killerSlot > 12 or not udg_player_active[killerSlot] then
        set dying = null
        set killer = null
        return
    endif
    set team = udg_teamnumber[killerSlot]
    call P79_Refresh()
    set t = CreateTimer()
    set timerKey = GetHandleId(t)
    set level = GetUnitLevel(dying)
    call SaveInteger(P79_Table, timerKey, 0, wave)
    // The unchanged stock GrantNormalXP curve, before player XP handicaps.
    call SaveInteger(P79_Table, timerKey, 1, 5 * level * (level + 3) / 2 + 15)
    loop
        exitwhen pn > 12
        set u = udg_herO[pn]
        if udg_teamnumber[pn] == team and P67_ValidHero(u) and IsUnitAliveBJ(u) and IsUnitInRange(u, dying, 1200.00) then
            set sharers = sharers + 1
            if P79_Active[pn] then
                call SaveUnitHandle(P79_Table, timerKey, 100 + pn, u)
                call SaveInteger(P79_Table, timerKey, 200 + pn, P79_Target[pn])
            endif
        endif
        set pn = pn + 1
    endloop
    call SaveInteger(P79_Table, timerKey, 2, sharers)
    call TimerStart(t, 0.00, false, function P79_Pay)
    set dying = null
    set killer = null
    set u = null
    set t = null
endfunction

function P79_Tag takes unit u, integer wave returns nothing
    local trigger death
    local integer key
    if not P67_Enabled() or wave < 1 or wave > 10 then
        return
    endif
    if P79_Table == null then
        set P79_Table = InitHashtable()
        set death = CreateTrigger()
        call TriggerRegisterAnyUnitEventBJ(death, EVENT_PLAYER_UNIT_DEATH)
        call TriggerAddAction(death, function P79_OnDeath)
        set death = null
    endif
    set key = GetHandleId(u)
    call SaveInteger(P79_Table, key, 0, wave)
    call SaveUnitHandle(P79_Table, key, 1, u)
endfunction
