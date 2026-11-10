// Fixed-price tickets: the displayed quote includes the proposed stake.
// Every ticket reserves its maximum profit against the finite casino bank.
function MK_FFA takes nothing returns boolean
    return MK_ffa
endfunction

function MK_Valid takes integer m, integer o returns boolean
    if m == 5 and not MK_FFA() then
        return o >= 1 and o <= FF_gr_SideCount() and FF_gr_SideParticipated(o)
    endif
    return o >= 1 and o <= 12 and FF_gr_participant[o]
endfunction

function MK_Label takes integer m, integer o returns string
    if m == 5 and not MK_FFA() then
        return FF_gr_SideLabel(o)
    endif
    return CAS_Name(o)
endfunction

function MK_Title takes integer m returns string
    if m == 1 then
        return "FIRST HERO KILL"
    elseif m == 2 then
        return "SCORES A BASE KILL"
    elseif m == 3 then
        return "FIRST BASE LOST"
    elseif m == 4 then
        return "FIRST TO LEVEL 16"
    elseif MK_FFA() then
        return "PLAYER TO WIN"
    endif
    return "TEAM TO WIN"
endfunction

function MK_Contains takes string value, string needle returns boolean
    local integer i = 0
    local integer n = StringLength(needle)
    loop
        exitwhen i+n > StringLength(value)
        if SubString(value,i,i+n) == needle then
            return true
        endif
        set i = i+1
    endloop
    return false
endfunction

function MK_Prior takes integer m, integer o returns integer
    local string name
    if m == 1 and o >= 1 and o <= 12 and udg_herO[o] != null then
        set name = StringCase(GetUnitName(udg_herO[o]),false)
        if MK_Contains(name,"shadow") or MK_Contains(name,"cattle") then
            return 300
        endif
    endif
    return 100
endfunction

function MK_Quote takes integer m, integer o, integer stake returns integer
    local integer total = MK_quoteTotal[m]+stake
    local integer weight = MK_pool[m*16+o]+MK_prior[m*16+o]+stake
    if weight <= 0 then
        return 110
    endif
    return IMinBJ(2000,IMaxBJ(110,R2I(I2R(total)*100.00/I2R(weight))))
endfunction

function MK_Refresh takes nothing returns nothing
    local integer m = 1
    local integer i
    set MK_ffa = FFEnd_ParticipantCount() >= 2 and FFEnd_BlockCount() < 2
    loop
        exitwhen m > 5
        set i = 1
        set MK_quoteTotal[m] = 0
        loop
            exitwhen i > 12
            if MK_Valid(m,i) then
                set MK_prior[m*16+i] = MK_Prior(m,i)
                set MK_quoteTotal[m] = MK_quoteTotal[m]+MK_pool[m*16+i]+MK_prior[m*16+i]
            endif
            set i = i+1
        endloop
        set m = m+1
    endloop
endfunction

function MK_IsOpen takes integer m, integer o returns boolean
    return not CAS_closed and not CAS_ended and R2I(TimerGetElapsed(FF_gameTimer)) < 130 and not MK_done[m] and not (m == 2 and MK_baseScored[o]) and MK_Valid(m,o)
endfunction

function MK_Buy takes integer s, integer m, integer o returns nothing
    local integer stake = CAS_amount[s]
    local integer quote
    local integer payout
    call MK_Refresh()
    if not MK_IsOpen(m,o) or MK_n >= 4095 then
        set CAS_note[s] = "This market is closed or has no remaining tickets."
        return
    endif
    set quote = MK_Quote(m,o,stake)
    set payout = stake*quote/100
    if not CAS_Reserve(s,stake,payout-stake) then
        return
    endif
    set MK_n = MK_n+1
    set MK_player[MK_n] = s
    set MK_market[MK_n] = m
    set MK_target[MK_n] = o
    set MK_stake[MK_n] = stake
    set MK_return[MK_n] = payout
    set MK_reserve[MK_n] = payout-stake
    set MK_pool[m*16+o] = MK_pool[m*16+o]+stake
    set MK_volume[m] = MK_volume[m]+stake
    set MK_quoteTotal[m] = MK_quoteTotal[m]+stake
    set MK_ownedStake[s*96+m*16+o] = MK_ownedStake[s*96+m*16+o]+stake
    set MK_ownedReturn[s*96+m*16+o] = MK_ownedReturn[s*96+m*16+o]+payout
    set CAS_note[s] = "LOCKED "+CAS_Odds(quote)+" / "+I2S(stake)+" gold on "+MK_Label(m,o)+" / total return "+I2S(payout)
    call FGA_SaveLocal()
endfunction

function MK_Pay takes integer ticket, boolean win, boolean refund returns nothing
    local integer payout = 0
    local integer s = MK_player[ticket]
    if MK_paid[ticket] then
        return
    endif
    set MK_paid[ticket] = true
    if refund then
        set payout = MK_stake[ticket]
    elseif win then
        set payout = MK_return[ticket]
    endif
    call CAS_Settle(s,MK_stake[ticket],payout,MK_reserve[ticket])
    if payout > MK_stake[ticket] then
        set CAS_note[s] = MK_Title(MK_market[ticket])+": won +"+I2S(payout-MK_stake[ticket])+" gold."
    elseif refund then
        set CAS_note[s] = MK_Title(MK_market[ticket])+": void / wager returned."
    endif
endfunction

function MK_PayBatch takes nothing returns nothing
    local integer count = 0
    local integer m
    local integer target
    loop
        exitwhen MK_scan > MK_n or count >= 64
        set m = MK_market[MK_scan]
        set target = MK_target[MK_scan]
        if not MK_paid[MK_scan] then
            if m == 2 and (MK_baseScored[target] or MK_done[2]) then
                call MK_Pay(MK_scan,MK_baseScored[target],false)
            elseif m != 2 and MK_done[m] then
                call MK_Pay(MK_scan,MK_winner[m] == target,MK_winner[m] == 0)
            endif
        endif
        set MK_scan = MK_scan+1
        set count = count+1
    endloop
    if MK_scan > MK_n then
        call PauseTimer(MK_payTimer)
        call FGA_SaveLocal()
    endif
endfunction

function MK_Schedule takes nothing returns nothing
    set MK_scan = 1
    call TimerStart(MK_payTimer,0.01,true,function MK_PayBatch)
endfunction

function MK_Resolve takes integer m, integer target returns nothing
    if MK_done[m] then
        return
    endif
    set MK_done[m] = true
    set MK_winner[m] = target
    call MK_Schedule()
    if target > 0 then
        call DisplayTimedTextToForce(GetPlayersAll(),8,"|cffe7cb88"+MK_Title(m)+"|r: "+MK_Label(m,target)+". Bets settled.")
    endif
endfunction

function MK_BaseDeath takes nothing returns nothing
    local unit victim = CAS_baseVictim
    local unit killer = CAS_baseKiller
    local integer lost = GetPlayerId(GetOwningPlayer(victim))+1
    local integer won = 0
    if lost < 1 or lost > 12 or not FF_gr_participant[lost] then
        set victim = null
        set killer = null
        return
    endif
    // This callback is injected at the map's actual base-destruction trigger.
    call MK_Resolve(3,lost)
    if killer != null and IsPlayerEnemy(GetOwningPlayer(killer),GetOwningPlayer(victim)) then
        set won = GetPlayerId(GetOwningPlayer(killer))+1
    endif
    if won >= 1 and won <= 12 and FF_gr_participant[won] and not MK_baseScored[won] then
        set MK_baseScored[won] = true
        call MK_Schedule()
    endif
    set victim = null
    set killer = null
endfunction

function MK_HeroDeath takes nothing returns nothing
    local unit victim = GetTriggerUnit()
    local unit killer = GetKillingUnit()
    local integer s
    local integer v
    if not MK_done[1] and killer != null and IsUnitType(victim,UNIT_TYPE_HERO) and not IsUnitIllusion(victim) and IsPlayerEnemy(GetOwningPlayer(killer),GetOwningPlayer(victim)) then
        set s = GetPlayerId(GetOwningPlayer(killer))+1
        set v = GetPlayerId(GetOwningPlayer(victim))+1
        if s >= 1 and s <= 12 and v >= 1 and v <= 12 and FF_gr_participant[s] and FF_gr_participant[v] then
            call MK_Resolve(1,s)
        endif
    endif
    set victim = null
    set killer = null
endfunction

function MK_Level takes nothing returns nothing
    local unit hero = GetTriggerUnit()
    local integer s = GetPlayerId(GetOwningPlayer(hero))+1
    if not MK_done[4] and s >= 1 and s <= 12 and FF_gr_participant[s] and hero == udg_herO[s] and GetHeroLevel(hero) >= 16 then
        call MK_Resolve(4,s)
    endif
    set hero = null
endfunction
