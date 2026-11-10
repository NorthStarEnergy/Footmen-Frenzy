// Two-deck S17. BJ_state: 0 empty, 1 acting, 2 stood, 3 bust, 4 natural, 5 paid.
// BJ_phase: 0 idle, 1 betting, 2 player turns, 3 dealer, 4 results.
function BJ_Value takes integer card returns integer
    return IMinBJ(10,ModuloInteger(card,13)+2)
endfunction

function BJ_Recount takes integer h returns nothing
    local integer i = 0
    local integer c
    set BJ_total[h] = 0
    set BJ_aces[h] = 0
    loop
        exitwhen i >= BJ_count[h]
        set c = BJ_card[h*22+i]
        if ModuloInteger(c,13) == 12 then
            set BJ_total[h] = BJ_total[h]+11
            set BJ_aces[h] = BJ_aces[h]+1
        else
            set BJ_total[h] = BJ_total[h]+BJ_Value(c)
        endif
        set i = i+1
    endloop
    loop
        exitwhen BJ_total[h] <= 21 or BJ_aces[h] == 0
        set BJ_total[h] = BJ_total[h]-10
        set BJ_aces[h] = BJ_aces[h]-1
    endloop
endfunction

function BJ_Shuffle takes integer t returns nothing
    local integer i = 0
    local integer j
    local integer temp
    loop
        exitwhen i >= 104
        set BJ_shoe[t*104+i] = ModuloInteger(i,52)
        set i = i+1
    endloop
    set i = 103
    loop
        exitwhen i <= 0
        set j = CAS_Random(i+1)
        set temp = BJ_shoe[t*104+i]
        set BJ_shoe[t*104+i] = BJ_shoe[t*104+j]
        set BJ_shoe[t*104+j] = temp
        set i = i-1
    endloop
    set BJ_pos[t] = 0
    set BJ_error[t] = false
endfunction

function BJ_Draw takes integer t returns integer
    local integer card
    if BJ_pos[t] >= 104 then
        set BJ_error[t] = true
        return 0
    endif
    set card = BJ_shoe[t*104+BJ_pos[t]]
    set BJ_pos[t] = BJ_pos[t]+1
    return card
endfunction

function BJ_Hit takes integer t, integer h returns nothing
    if BJ_count[h] >= 22 then
        set BJ_error[t] = true
        return
    endif
    set BJ_card[h*22+BJ_count[h]] = BJ_Draw(t)
    set BJ_count[h] = BJ_count[h]+1
    call BJ_Recount(h)
    if BJ_total[h] > 21 then
        set BJ_state[h] = 3
    elseif BJ_total[h] == 21 then
        set BJ_state[h] = 2
    endif
endfunction

function BJ_DealerHit takes integer t returns nothing
    local integer card = BJ_Draw(t)
    set BJ_dealerCard[t*22+BJ_dealerCount[t]] = card
    set BJ_dealerCount[t] = BJ_dealerCount[t]+1
    if ModuloInteger(card,13) == 12 then
        set BJ_dealerTotal[t] = BJ_dealerTotal[t]+11
        set BJ_dealerAces[t] = BJ_dealerAces[t]+1
    else
        set BJ_dealerTotal[t] = BJ_dealerTotal[t]+BJ_Value(card)
    endif
    loop
        exitwhen BJ_dealerTotal[t] <= 21 or BJ_dealerAces[t] == 0
        set BJ_dealerTotal[t] = BJ_dealerTotal[t]-10
        set BJ_dealerAces[t] = BJ_dealerAces[t]-1
    endloop
endfunction

function BJ_Payout takes integer total, boolean natural, integer dealer, boolean dealerNatural, integer bet returns integer
    if total > 21 then
        return 0
    elseif dealerNatural then
        if natural then
            return bet
        endif
        return 0
    elseif natural then
        return bet*5/2
    elseif dealer > 21 or total > dealer then
        return bet*2
    elseif total == dealer then
        return bet
    endif
    return 0
endfunction

function BJ_Finish takes integer t, boolean refund returns nothing
    local integer h = t*12
    local integer s
    local integer payout
    local integer stake
    loop
        exitwhen h >= t*12+12
        if BJ_bet[h] > 0 and BJ_state[h] != 5 then
            set stake = BJ_bet[h]
            set s = BJ_owner[h/2]
            if refund then
                set payout = stake
            else
                set payout = BJ_Payout(BJ_total[h],BJ_state[h] == 4,BJ_dealerTotal[t],BJ_dealerCount[t] == 2 and BJ_dealerTotal[t] == 21,stake)
            endif
            // Mark paid before touching the wallet: duplicate finish calls are harmless.
            set BJ_state[h] = 5
            if s > 0 then
                call CAS_Settle(s,stake,payout,BJ_reserve[h])
                if refund then
                    set BJ_result[h] = "Round void / returned "+I2S(payout)
                elseif payout == stake then
                    set BJ_result[h] = "Push / returned "+I2S(payout)
                elseif payout > stake then
                    set BJ_result[h] = "Won +"+I2S(payout-stake)+" / return "+I2S(payout)
                else
                    set BJ_result[h] = "Lost "+I2S(stake)
                endif
                set CAS_note[s] = BJ_result[h]
            endif
        endif
        set h = h+1
    endloop
    set BJ_reveal[t] = true
    set BJ_phase[t] = 4
    set BJ_clock[t] = 5
    set BJ_turn[t] = 0
    call FGA_SaveLocal()
endfunction

function BJ_Next takes integer t returns nothing
    local integer h = t*12
    if BJ_error[t] then
        call BJ_Finish(t,true)
        return
    endif
    loop
        exitwhen h >= t*12+12
        if BJ_state[h] == 1 then
            set BJ_turn[t] = h+1
            set BJ_clock[t] = 20
            return
        endif
        set h = h+1
    endloop
    set BJ_turn[t] = 0
    set BJ_phase[t] = 3
    set BJ_reveal[t] = true
    set BJ_clock[t] = 2
endfunction

function BJ_Deal takes integer t returns nothing
    local integer h
    local integer dealPass = 0
    // The cut card triggers before the next round; live cards are never recycled.
    if BJ_pos[t] > 26 then
        call BJ_Shuffle(t)
    endif
    set BJ_round[t] = BJ_round[t]+1
    set BJ_dealerCount[t] = 0
    set BJ_dealerTotal[t] = 0
    set BJ_dealerAces[t] = 0
    set BJ_reveal[t] = false
    loop
        exitwhen dealPass >= 2
        set h = t*12
        loop
            exitwhen h >= t*12+12
            if BJ_bet[h] > 0 then
                set BJ_state[h] = 1
                call BJ_Hit(t,h)
            endif
            set h = h+2
        endloop
        call BJ_DealerHit(t)
        set dealPass = dealPass+1
    endloop
    set h = t*12
    loop
        exitwhen h >= t*12+12
        if BJ_bet[h] > 0 and BJ_total[h] == 21 then
            set BJ_state[h] = 4
        endif
        set h = h+2
    endloop
    set BJ_phase[t] = 2
    if BJ_error[t] then
        call BJ_Finish(t,true)
    elseif BJ_dealerTotal[t] == 21 then
        call BJ_Finish(t,false)
    else
        call BJ_Next(t)
    endif
endfunction

function BJ_Reset takes integer t returns nothing
    local integer h = t*12
    loop
        exitwhen h >= t*12+12
        set BJ_count[h] = 0
        set BJ_total[h] = 0
        set BJ_aces[h] = 0
        set BJ_state[h] = 0
        set BJ_bet[h] = 0
        set BJ_reserve[h] = 0
        set BJ_split[h] = false
        set BJ_result[h] = ""
        set h = h+1
    endloop
    set BJ_dealerCount[t] = 0
    set BJ_dealerTotal[t] = 0
    set BJ_reveal[t] = false
    set BJ_phase[t] = 0
endfunction

function BJ_Wager takes integer s returns nothing
    local integer t = BJ_table[s]
    local integer h = BJ_seat[s]*2
    local integer stake = CAS_amount[s]
    local integer i
    if BJ_phase[t] == 4 then
        call BJ_Reset(t)
    endif
    if BJ_phase[t] > 1 or BJ_bet[h] > 0 then
        set CAS_note[s] = "Your wager is already placed, or a round is in progress."
        return
    endif
    if not CAS_Reserve(s,stake,stake*3/2) then
        return
    endif
    set BJ_bet[h] = stake
    set BJ_reserve[h] = stake*3/2
    set BJ_state[h] = 1
    if BJ_phase[t] == 0 then
        set BJ_phase[t] = 1
        set BJ_clock[t] = 12
        if t > 0 then
            set BJ_clock[t] = 3
            set i = 1
            loop
                exitwhen i > 2
                set BJ_bet[(t*6+i)*2] = stake
                set BJ_state[(t*6+i)*2] = 1
                set i = i+1
            endloop
        endif
    endif
    set CAS_note[s] = "Wager locked: "+I2S(stake)+" account gold."
    call FGA_SaveLocal()
endfunction

function BJ_Action takes integer s, integer action returns nothing
    local integer t = BJ_table[s]
    local integer h = BJ_turn[t]-1
    local integer stake
    local integer card
    if BJ_phase[t] != 2 or h < 0 or BJ_owner[h/2] != s or BJ_state[h] != 1 then
        return
    endif
    if action == 1 then
        call BJ_Hit(t,h)
    elseif action == 2 then
        set BJ_state[h] = 2
    elseif action == 3 then
        if BJ_count[h] != 2 or BJ_bet[h] > 10000 or (BJ_split[h] and ModuloInteger(BJ_card[h*22],13) == 12) then
            return
        endif
        set stake = BJ_bet[h]
        if not CAS_Reserve(s,stake,stake*3/2) then
            return
        endif
        set BJ_bet[h] = stake*2
        set BJ_reserve[h] = BJ_reserve[h]+stake*3/2
        call BJ_Hit(t,h)
        if BJ_state[h] == 1 then
            set BJ_state[h] = 2
        endif
    elseif action == 4 then
        if BJ_count[h] != 2 or BJ_split[h] or ModuloInteger(h,2) != 0 or BJ_Value(BJ_card[h*22]) != BJ_Value(BJ_card[h*22+1]) or (ModuloInteger(BJ_card[h*22],13) == 12) != (ModuloInteger(BJ_card[h*22+1],13) == 12) then
            return
        endif
        set stake = BJ_bet[h]
        if not CAS_Reserve(s,stake,stake*3/2) then
            return
        endif
        set card = BJ_card[h*22+1]
        set BJ_count[h] = 1
        set BJ_count[h+1] = 1
        set BJ_card[(h+1)*22] = card
        set BJ_bet[h+1] = stake
        set BJ_reserve[h+1] = stake*3/2
        set BJ_split[h] = true
        set BJ_split[h+1] = true
        set BJ_state[h+1] = 1
        call BJ_Hit(t,h)
        call BJ_Hit(t,h+1)
        if ModuloInteger(card,13) == 12 then
            set BJ_state[h] = 2
            set BJ_state[h+1] = 2
        endif
    endif
    if BJ_error[t] then
        call BJ_Finish(t,true)
    elseif BJ_state[h] != 1 then
        call BJ_Next(t)
    endif
    call FGA_SaveLocal()
endfunction

function BJ_Move takes integer s, boolean community returns nothing
    local integer old = BJ_table[s]
    local integer seat = BJ_seat[s]
    local integer i = 0
    local integer t = s
    if BJ_bet[seat*2] > 0 and BJ_state[seat*2] != 5 then
        set CAS_note[s] = "Finish your current round before switching tables."
        return
    endif
    if community then
        set t = 0
        loop
            exitwhen i >= 6 or BJ_owner[i] == 0 or BJ_owner[i] == s
            set i = i+1
        endloop
        if i == 6 then
            set CAS_note[s] = "The community table is full (six seats)."
            return
        endif
    endif
    if old == t then
        return
    endif
    set BJ_owner[seat] = 0
    set BJ_table[s] = t
    set BJ_seat[s] = t*6+i
    set BJ_owner[t*6+i] = s
    set CAS_note[s] = "Seated. Choose your wager, then click Place wager."
endfunction

function BJ_Tick takes nothing returns nothing
    local integer t = 0
    local integer h
    local integer s
    loop
        exitwhen t > 24
        if BJ_phase[t] == 1 then
            set BJ_clock[t] = BJ_clock[t]-1
            if BJ_clock[t] <= 0 then
                call BJ_Deal(t)
            endif
        elseif BJ_phase[t] == 2 then
            set h = BJ_turn[t]-1
            set s = BJ_owner[h/2]
            set BJ_clock[t] = BJ_clock[t]-1
            if s < 0 then
                if BJ_total[h] < 17 then
                    call BJ_Hit(t,h)
                else
                    set BJ_state[h] = 2
                endif
                if BJ_state[h] != 1 then
                    call BJ_Next(t)
                elseif BJ_error[t] then
                    call BJ_Finish(t,true)
                endif
            elseif BJ_clock[t] <= 0 or not CAS_User(s) then
                set BJ_state[h] = 2
                call BJ_Next(t)
            endif
        elseif BJ_phase[t] == 3 then
            set BJ_clock[t] = BJ_clock[t]-1
            if BJ_clock[t] <= 0 then
                if BJ_dealerTotal[t] < 17 then
                    call BJ_DealerHit(t)
                    set BJ_clock[t] = 1
                    if BJ_error[t] then
                        call BJ_Finish(t,true)
                    endif
                else
                    call BJ_Finish(t,false)
                endif
            endif
        elseif BJ_phase[t] == 4 then
            set BJ_clock[t] = IMaxBJ(0,BJ_clock[t]-1)
        endif
        set t = t+1
    endloop
endfunction
