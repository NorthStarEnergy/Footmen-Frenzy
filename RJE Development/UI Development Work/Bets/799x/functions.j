function OP_NextLive takes integer after returns integer
    local integer n = 0
    loop
        exitwhen n >= 24
        set after = ModuloInteger(after+1,24)
        if OP_Live[after] then
            return after
        endif
        set n = n+1
    endloop
    return -1
endfunction

function OP_CashOut takes integer v returns nothing
    local integer buy = PokerBuyIn[v]
    local integer chips = PK_Stack[v]
    if buy <= 0 then
        return
    endif
    set PokerBuyIn[v] = 0
    set OP_Seats = OP_Seats-1
    set PK_Stack[v] = 0
    set OP_Leaving[v] = false
    set CAS_escrow[v+1] = CAS_escrow[v+1]-buy
    call CAS_Credit(0,v+1,IMinBJ(chips,buy),IMaxBJ(0,chips-buy))
    set PK_Version[v] = PK_Version[v]+1
    set PK_Feedback[v] = "Cashed out "+I2S(chips)+"g."
endfunction

function OP_Join takes integer v, integer amount returns nothing
    if PokerBuyIn[v] > 0 or CAS_ended or not PK_Eligible(v) then
        return
    endif
    if amount < 100 or amount > 1500 then
        set PK_Feedback[v] = "Choose a buy-in from 100 to 1,500g."
        return
    endif
    if not CAS_Reserve(0,v+1,amount,0) then
        set PK_Feedback[v] = CAS_note[v+1]
        return
    endif
    set PokerBuyIn[v] = amount
    set PK_Stack[v] = amount
    set PK_Default[v] = amount
    set OP_Seats = OP_Seats+1
    set PK_Version[v] = PK_Version[v]+1
    set PK_Feedback[v] = "Seated with "+I2S(amount)+"g for the next deal."
    if OP_Phase == 0 then
        set OP_Dealt[v] = false
        set OP_Live[v] = false
        set OP_Award[v] = 0
    endif
endfunction

function OP_AwardPots takes nothing returns nothing
    local integer floor = 0
    local integer cap
    local integer v
    local integer n
    local integer contributors
    local integer best
    local integer winners
    local integer chips
    local integer odd
    local integer sole
    local integer paid = 0
    loop
        set cap = 0
        set v = 0
        loop
            exitwhen v >= 24
            if PK_Total[v] > floor and (cap == 0 or PK_Total[v] < cap) then
                set cap = PK_Total[v]
            endif
            set v = v+1
        endloop
        exitwhen cap == 0
        set contributors = 0
        set winners = 0
        set best = -1
        set v = 0
        loop
            exitwhen v >= 24
            if PK_Total[v] >= cap then
                set contributors = contributors+1
                set sole = v
                if OP_Live[v] then
                    if OP_Score[v] > best then
                        set best = OP_Score[v]
                        set winners = 1
                    elseif OP_Score[v] == best then
                        set winners = winners+1
                    endif
                endif
            endif
            set v = v+1
        endloop
        set chips = contributors*(cap-floor)
        if contributors == 1 then
            set OP_Award[sole] = OP_Award[sole]+chips
        elseif winners == 0 then
            // All contenders for this excess left. Return their unmatched layer.
            set v = 0
            loop
                exitwhen v >= 24
                if PK_Total[v] >= cap then
                    set OP_Award[v] = OP_Award[v]+cap-floor
                endif
                set v = v+1
            endloop
        else
            set odd = ModuloInteger(chips,winners)
            set n = 1
            loop
                exitwhen n > 24
                set v = ModuloInteger(OP_Button+n,24)
                if PK_Total[v] >= cap and OP_Live[v] and OP_Score[v] == best then
                    set OP_Award[v] = OP_Award[v]+chips/winners
                    if odd > 0 then
                        set OP_Award[v] = OP_Award[v]+1
                        set odd = odd-1
                    endif
                endif
                set n = n+1
            endloop
            set paid = paid+chips
        endif
        set floor = cap
    endloop
    set OP_Pot = paid
endfunction

function OP_Finish takes nothing returns nothing
    local integer v = 0
    local integer sole = -1
    local integer winners = 0
    call OP_AwardPots()
    loop
        exitwhen v >= 24
        if OP_Dealt[v] then
            call CAS_ResultSound(v+1,OP_Award[v]-PK_Total[v])
            set PK_Stack[v] = PK_Stack[v]+OP_Award[v]
            set PK_Total[v] = 0
            set PK_Paid[v] = 0
            set PK_Version[v] = PK_Version[v]+1
            if OP_Award[v] > 0 and OP_Live[v] then
                set sole = v
                set winners = winners+1
            endif
            if OP_Leaving[v] or PK_Stack[v] == 0 or not PK_Eligible(v) then
                call OP_CashOut(v)
            endif
        endif
        set v = v+1
    endloop
    if winners == 1 then
        set OP_Note = GetPlayerName(Player(sole))+" wins the "+I2S(OP_Pot)+"g pot."
    else
        set OP_Note = "Pot settled. Seat results show each return, including side pots."
    endif
    set OP_Phase = 0
    set OP_Turn = -1
    set OP_Clock = 10
endfunction

function OP_ScoreTick takes nothing returns nothing
    loop
        exitwhen OP_ScoreCursor >= 24
        if OP_Live[OP_ScoreCursor] then
            set OP_Score[OP_ScoreCursor] = PK_Score(OP_ScoreCursor)
            set OP_ScoreCursor = OP_ScoreCursor+1
            return
        endif
        set OP_ScoreCursor = OP_ScoreCursor+1
    endloop
    call PauseTimer(OP_ScoreTimer)
    call OP_Finish()
endfunction

function OP_Showdown takes nothing returns nothing
    set OP_Phase = 2
    set OP_Street = 3
    set OP_Turn = -1
    set OP_Revealed = true
    set OP_Note = "Showdown"
    set OP_ScoreCursor = 0
    call TimerStart(OP_ScoreTimer,0.05,true,function OP_ScoreTick)
endfunction

function OP_Wager takes integer v, integer chips returns nothing
    call PK_Pay(v,chips)
    set OP_Pot = OP_Pot+chips
endfunction

function OP_Continue takes integer after returns nothing
    local integer v = 0
    local integer live = 0
    local integer able = 0
    local integer lone = -1
    local integer high = 0
    local integer n = 0
    loop
        exitwhen v >= 24
        if OP_Live[v] then
            set live = live+1
            set high = IMaxBJ(high,PK_Paid[v])
            if PK_Stack[v] > 0 then
                set able = able+1
                set lone = v
            endif
        endif
        set v = v+1
    endloop
    if live == 1 then
        call OP_Finish()
        return
    endif
    if able <= 1 then
        set OP_Bet = high
        if lone < 0 then
            call OP_Showdown()
            return
        elseif PK_Paid[lone] >= high then
            call OP_Showdown()
            return
        endif
    endif
    loop
        exitwhen n >= 24
        set after = ModuloInteger(after+1,24)
        if OP_Live[after] and PK_Stack[after] > 0 and (not PK_Acted[after] or PK_Paid[after] < OP_Bet) then
            set OP_Turn = after
            set OP_Clock = 30
            set PK_Version[after] = PK_Version[after]+1
            set PK_Feedback[after] = ""
            return
        endif
        set n = n+1
    endloop
    if OP_Street == 3 then
        call OP_Showdown()
        return
    endif
    set OP_Street = OP_Street+1
    set OP_Bet = 0
    set OP_MinRaise = 10
    set v = 0
    loop
        exitwhen v >= 24
        set PK_Paid[v] = 0
        set PK_Acted[v] = false
        set OP_Faced[v] = 0
        set v = v+1
    endloop
    set v = OP_Button
    loop
        set v = OP_NextLive(v)
        exitwhen PK_Stack[v] > 0
    endloop
    set OP_Turn = v
    set OP_Clock = 30
    set PK_Feedback[v] = ""
    set PK_Version[v] = PK_Version[v]+1
endfunction

function OP_Deal takes nothing returns nothing
    local integer v = 0
    local integer i = 0
    local integer j
    local integer swap
    local integer small
    local integer big
    local integer count = 0
    // A 52-card deck fits 23 pocket pairs plus a five-card board. If all 24
    // slots (including observers) buy in, rotate one seat out for each deal.
    if OP_Seats == 24 then
        set OP_Rest = ModuloInteger(OP_Rest+1,24)
    endif
    loop
        exitwhen i >= 52
        set PK_Deck[i] = i
        set i = i+1
    endloop
    set i = 51
    loop
        exitwhen i <= 0
        set j = PK_Random(i+1)
        set swap = PK_Deck[i]
        set PK_Deck[i] = PK_Deck[j]
        set PK_Deck[j] = swap
        set i = i-1
    endloop
    loop
        exitwhen v >= 24
        set OP_Dealt[v] = PokerBuyIn[v] > 0 and (OP_Seats < 24 or OP_Rest != v)
        set OP_Live[v] = OP_Dealt[v]
        if OP_Seats == 24 and v == OP_Rest then
            set PK_Feedback[v] = "Full deck this hand. Your seat plays the next deal."
        endif
        set PK_Acted[v] = false
        set OP_Faced[v] = 0
        set OP_Score[v] = 0
        set OP_Award[v] = 0
        set PK_Total[v] = 0
        set PK_Paid[v] = 0
        if OP_Dealt[v] then
            set PK_Cards[v*2] = PK_Deck[i]
            set PK_Cards[v*2+1] = PK_Deck[i+1]
            set i = i+2
            set count = count+1
            set PK_Feedback[v] = ""
            set PK_Version[v] = PK_Version[v]+1
        endif
        set v = v+1
    endloop
    set j = 0
    loop
        exitwhen j >= 5
        set OP_Board[j] = PK_Deck[i+j]
        set j = j+1
    endloop
    set OP_Hand = OP_Hand+1
    set OP_Button = OP_NextLive(OP_Button)
    set small = OP_NextLive(OP_Button)
    if count == 2 then
        set small = OP_Button
    endif
    set big = OP_NextLive(small)
    set OP_Phase = 1
    set OP_Revealed = false
    set OP_Street = 0
    set OP_Pot = 0
    set OP_Bet = 10
    set OP_MinRaise = 10
    call OP_Wager(small,IMinBJ(5,PK_Stack[small]))
    call OP_Wager(big,IMinBJ(10,PK_Stack[big]))
    set OP_Note = "Blinds  /  "+GetPlayerName(Player(small))+" "+I2S(PK_Paid[small])+"g  /  "+GetPlayerName(Player(big))+" "+I2S(PK_Paid[big])+"g"
    call OP_Continue(big)
endfunction

function OP_CanRaise takes integer v returns boolean
    local integer other = 0
    if OP_Turn != v or PK_Stack[v]+PK_Paid[v] <= OP_Bet or (PK_Acted[v] and OP_Faced[v] > 0 and OP_Bet-OP_Faced[v] < OP_MinRaise) then
        return false
    endif
    loop
        exitwhen other >= 24
        if other != v and OP_Live[other] and PK_Stack[other] > 0 then
            return true
        endif
        set other = other+1
    endloop
    return false
endfunction

function OP_Action takes integer v, string move, integer target returns nothing
    local integer due = IMinBJ(PK_Stack[v],OP_Bet-PK_Paid[v])
    local integer cap = PK_Stack[v]+PK_Paid[v]
    local integer raiseBy = target-OP_Bet
    local string name = GetPlayerName(Player(v))
    if OP_Phase != 1 or OP_Turn != v or CAS_ended then
        return
    endif
    if move == "f" then
        set OP_Live[v] = false
        set OP_Note = name+" folded."
    elseif move == "c" then
        call OP_Wager(v,due)
        if due == 0 then
            set OP_Note = name+" checked."
        else
            set OP_Note = name+" called "+I2S(due)+"g."
        endif
    elseif move == "r" then
        if not OP_CanRaise(v) or raiseBy <= 0 or target > cap or (raiseBy < OP_MinRaise and target != cap) then
            set PK_Feedback[v] = "Choose a legal raise or call. Minimum full raise to "+I2S(OP_Bet+OP_MinRaise)+"g."
            return
        endif
        call OP_Wager(v,target-PK_Paid[v])
        set OP_MinRaise = IMaxBJ(OP_MinRaise,raiseBy)
        set OP_Bet = target
        set OP_Note = name+" bet to "+I2S(target)+"g."
    else
        return
    endif
    if PK_Stack[v] == 0 and OP_Live[v] then
        set OP_Note = OP_Note+"  ALL-IN"
    endif
    set PK_Acted[v] = true
    set OP_Faced[v] = OP_Bet
    set PK_Version[v] = PK_Version[v]+1
    set PK_Feedback[v] = ""
    call OP_Continue(v)
endfunction

function OP_Leave takes integer v returns nothing
    if PokerBuyIn[v] == 0 or OP_Leaving[v] then
        return
    endif
    if OP_Phase == 0 or not OP_Dealt[v] then
        call OP_CashOut(v)
    else
        set OP_Leaving[v] = true
        set PK_Version[v] = PK_Version[v]+1
        set PK_Feedback[v] = "Leaving after this pot. Your remaining chips will return to your Wallet."
        if OP_Turn == v then
            call OP_Action(v,"f",0)
        endif
    endif
endfunction

function OP_EndMatch takes nothing returns nothing
    local integer v = 0
    call PauseTimer(OP_ScoreTimer)
    loop
        exitwhen v >= 24
        if PokerBuyIn[v] > 0 then
            set PK_Stack[v] = PK_Stack[v]+PK_Total[v]
            set PK_Total[v] = 0
            set PK_Paid[v] = 0
            call OP_CashOut(v)
        endif
        set v = v+1
    endloop
    set OP_Phase = 0
    set OP_Turn = -1
    set OP_Pot = 0
    set OP_Note = "Match ended. Open wagers returned."
endfunction

function OP_SeatLine takes integer v returns string
    local string name = SubString(GetPlayerName(Player(v)),0,18)
    local string line = name+"  "+I2S(PK_Stack[v])+"g"
    if OP_Turn == v then
        set line = "|cff8cf2ac> "+line+"|r"
    elseif OP_Button == v and OP_Dealt[v] then
        set line = "D  "+line
    endif
    if OP_Phase == 0 and OP_Award[v] > 0 then
        set line = line+"  /  returned "+I2S(OP_Award[v])+"g"
    elseif OP_Phase != 0 and not OP_Dealt[v] then
        set line = line+"  /  next deal"
    elseif OP_Dealt[v] and not OP_Live[v] then
        set line = line+"  /  folded"
    elseif OP_Phase != 0 and PK_Stack[v] == 0 then
        set line = line+"  /  all-in "+I2S(PK_Total[v])+"g"
    elseif OP_Phase == 1 then
        set line = line+"  /  bet "+I2S(PK_Paid[v])+"g"
    endif
    if OP_Revealed and OP_Live[v] then
        set line = line+"  "+PK_Card(PK_Cards[v*2])+PK_Card(PK_Cards[v*2+1])
    endif
    return line
endfunction

function OP_RosterCount takes nothing returns integer
    local integer v = 0
    local integer count = 0
    loop
        exitwhen v >= 24
        if PokerBuyIn[v] > 0 or OP_Dealt[v] then
            set count = count+1
        endif
        set v = v+1
    endloop
    return count
endfunction

function OP_Refresh takes nothing returns nothing
    local integer v = GetPlayerId(GetLocalPlayer())
    if v < 24 then
        call PK_Render(v)
    endif
endfunction

function BJ_Wager takes integer s returns nothing
    local integer t = BJ_table[s]
    local integer h = BJ_seat[s]*2
    local integer stake = CAS_amount[s]
    local integer i
    if stake < 10 or stake > 100 then
        set CAS_note[s] = "Blackjack opening bet: 10 to 100 gold."
        return
    endif
    if BJ_phase[t] == 4 then
        if t == 0 and BJ_clock[t] > 0 then
            set CAS_note[s] = "Next round opens in "+I2S(BJ_clock[t])+"s."
            return
        endif
        call BJ_Reset(t)
    endif
    if BJ_phase[t] > 1 or BJ_bet[h] > 0 then
        set CAS_note[s] = "Your wager is already placed, or a round is in progress."
        return
    endif
    if not CAS_Reserve(1,s,stake,stake*3/2) then
        return
    endif
    set BJWatchOlder[s] = ""
    set BJWatchPrevious[s] = ""
    set BJWatchLast[s] = "Bet "+I2S(stake)+"g"
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
    set CAS_note[s] = "Wager locked: "+I2S(stake)+" gold from your Wallet."
endfunction

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
    set MK_ffa = FFEnd_ParticipantCount() >= 2 and FFEnd_BlockCount() == 1
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
    if not CAS_Reserve(2,s,stake,payout-stake) then
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
    call CAS_Settle(2,s,MK_stake[ticket],payout,MK_reserve[ticket])
    call CAS_ResultSound(s,payout-MK_stake[ticket])
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
        call CAS_Announce("|cffe7cb88"+MK_Title(m)+"|r: "+MK_Label(m,target)+". Bets settled.")
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
    if AR_Fighter(GetTriggerUnit()) then
        return
    endif
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

function CAS_BetsView takes integer s returns nothing
    local integer m = MK_tab[s]
    local integer o
    local integer i = 0
    local integer k = 0
    local integer b = s*32
    local integer start = MK_page[s]*6
    local integer quote
    local integer volume
    local integer total = MK_volume[m]
    local integer tickets = 0
    local integer invested = 0
    local integer totalReturn = 0
    local string label
    call BlzFrameSetText(CAS_content[b+7],"|cffe7cb88"+MK_Title(m)+"|r  /  "+CUI_Value(I2S(total)+"g"))
    call BlzFrameSetVisible(CAS_content[b+7],true)
    call BlzFrameSetText(CAS_content[b+8],"OUTCOME")
    call BlzFrameSetVisible(CAS_content[b+8],true)
    call BlzFrameSetText(CAS_content[b+31],"POOL")
    call BlzFrameSetVisible(CAS_content[b+31],true)
    call BlzFrameSetPoint(CAS_content[b+6],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,CAS_SafeX(0.443),-0.168)
    call BlzFrameSetSize(CAS_content[b+6],CAS_SafeW(0.095),0.018)
    call BlzFrameSetTextAlignment(CAS_content[b+6],TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_RIGHT)
    call BlzFrameSetText(CAS_content[b+6],"ODDS")
    call BlzFrameSetVisible(CAS_content[b+6],true)
    set o = 1
    loop
        exitwhen o > 12
        if MK_Valid(m,o) then
            if k >= start and i < 6 then
                set volume = MK_pool[m*16+o]
                set label = MK_Label(m,o)
                if o == MK_pick[s] then
                    set label = "|cffe7cb88> "+label+"|r"
                endif
                call BlzFrameSetText(CAS_content[b+10+i*3],label)
                call BlzFrameSetText(CAS_content[b+11+i*3],CUI_Value(I2S(volume)+"g")+" / "+I2S(R2I(I2R(volume)*100.0/I2R(IMaxBJ(1,total))))+"%")
                set quote = MK_Quote(m,o,0)
                set label = CUI_Value(CAS_Odds(quote))
                if m == 2 and MK_baseScored[o] then
                    set label = "SCORED"
                elseif MK_done[m] then
                    set label = "SETTLED"
                    if m == 2 then
                        set label = "NO KILL"
                    elseif MK_winner[m] == o then
                        set label = "|cffe7cb88WINNER|r"
                    endif
                elseif CAS_closed or CAS_seconds >= 130 then
                    set label = "CLOSED"
                endif
                call BlzFrameSetText(CAS_content[b+12+i*3],label)
                call BlzFrameSetVisible(CAS_content[b+10+i*3],true)
                call BlzFrameSetVisible(CAS_content[b+11+i*3],true)
                call BlzFrameSetVisible(CAS_content[b+12+i*3],true)
                call BlzFrameSetVisible(CAS_track[s*6+i],true)
                call BlzFrameSetVisible(CAS_bar[s*6+i],volume > 0)
                call BlzFrameSetSize(CAS_bar[s*6+i],IMaxBJ(1,volume)*CAS_SafeW(0.140)/I2R(IMaxBJ(1,total)),0.003)
                call CAS_ShowButton(s,26+i,true)
                call CUI_Text(CAS_button[s*64+26+i],"PICK")
                if o == MK_pick[s] then
                    call CUI_Paint(CAS_button[s*64+26+i],5,true)
                endif
                set i = i+1
            endif
            set k = k+1
        endif
        set o = o+1
    endloop
    set invested = MK_ownedStake[s*96+m*16+MK_pick[s]]
    set totalReturn = MK_ownedReturn[s*96+m*16+MK_pick[s]]
    set label = "PICK AN OUTCOME"
    if MK_Valid(m,MK_pick[s]) then
        set quote = MK_Quote(m,MK_pick[s],CAS_amount[s])
        set label = MK_Label(m,MK_pick[s])+"  "+CUI_Value(CAS_Odds(quote))+"  /  RETURN "+CUI_Value(I2S(CAS_amount[s]*quote/100)+"g")
        if invested > 0 then
            if MK_done[m] or (m == 2 and MK_baseScored[MK_pick[s]]) then
                if m != 2 and MK_winner[m] == 0 then
                    set totalReturn = invested
                elseif (m == 2 and not MK_baseScored[MK_pick[s]]) or (m != 2 and MK_winner[m] != MK_pick[s]) then
                    set totalReturn = 0
                endif
                set label = MK_Label(m,MK_pick[s])+"|nSETTLED "+CUI_Value(I2S(invested)+"g")+"  /  RETURN "+CUI_Value(I2S(totalReturn)+"g")
            else
                set label = label+"|nLOCKED "+CUI_Value(I2S(invested)+"g")+"  /  RETURN "+CUI_Value(I2S(totalReturn)+"g")
            endif
        endif
    endif
    call BlzFrameSetText(CAS_content[b+9],label)
    call BlzFrameSetVisible(CAS_content[b+9],true)
    loop
        exitwhen i >= 6
        call BlzFrameSetVisible(CAS_button[s*64+26+i],false)
        set i = i+1
    endloop
    set i = 20
    loop
        exitwhen i > 24
        call CAS_ShowButton(s,i,true)
        if i-19 == m then
            call CUI_Paint(CAS_button[s*64+i],4,true)
        endif
        set i = i+1
    endloop
    call CAS_ShowButton(s,25,k > 6)
    call CAS_ShowButton(s,32,MK_IsOpen(m,MK_pick[s]))
endfunction
