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
