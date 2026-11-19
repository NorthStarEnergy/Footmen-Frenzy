// A table is keyed by its first player. Seat 1 is another player, or the house in practice.
function PK_PlayerAt takes integer table, integer seat returns integer
    if seat == 0 then
        return table
    endif
    return PK_Guest[table]-1
endfunction

function PK_SeatName takes integer table, integer seat returns string
    local integer viewer = PK_PlayerAt(table,seat)
    if viewer < 0 then
        return "Computer"
    endif
    return GetPlayerName(Player(viewer))
endfunction

function PK_TableChanged takes integer table returns nothing
    set PK_Feedback[table] = ""
    set PK_Version[table] = PK_Version[table]+1
    if PK_Guest[table] > 0 then
        set PK_Feedback[PK_Guest[table]-1] = ""
        set PK_Version[PK_Guest[table]-1] = PK_Version[PK_Guest[table]-1]+1
    endif
endfunction

function PK_Top takes integer table returns integer
    return IMaxBJ(PK_Paid[table*2],PK_Paid[table*2+1])
endfunction

function PK_End takes integer table, integer winner, string note returns nothing
    local integer first = table*2
    local integer larger = first
    local integer excess
    local integer pot
    if PK_Turn[table] < 0 then
        return
    endif
    if PK_Total[first+1] > PK_Total[first] then
        set larger = first+1
    endif
    set excess = IAbsBJ(PK_Total[first]-PK_Total[first+1])
    set PK_Stack[larger] = PK_Stack[larger]+excess
    set pot = PK_Total[first]+PK_Total[first+1]-excess
    if winner == 2 then
        set PK_Stack[first] = PK_Stack[first]+pot/2
        set PK_Stack[first+1] = PK_Stack[first+1]+pot/2
        set PK_Note[table] = note+"  /  Split "+I2S(pot)+"g"
    else
        set PK_Stack[first+winner] = PK_Stack[first+winner]+pot
        set PK_Note[table] = note+"  /  "+PK_SeatName(table,winner)+" wins "+I2S(pot)+"g"
    endif
    if excess > 0 then
        set PK_Note[table] = PK_Note[table]+"  /  "+I2S(excess)+"g uncalled"
    endif
    set PK_LastPot[table] = pot
    set PK_Turn[table] = -1
    set PK_Total[first] = 0
    set PK_Total[first+1] = 0
    set PK_Paid[first] = 0
    set PK_Paid[first+1] = 0
    set PK_Ready[first] = false
    set PK_Ready[first+1] = PK_Guest[table] == 0
    call PK_TableChanged(table)
endfunction

function PK_Showdown takes integer table returns nothing
    local integer left = PK_Score(table,0,5)
    local integer right = PK_Score(table,1,5)
    set PK_Street[table] = 3
    set PK_Reveal[table] = true
    if left > right then
        call PK_End(table,0,PK_Category(left))
    elseif right > left then
        call PK_End(table,1,PK_Category(right))
    else
        call PK_End(table,2,PK_Category(left))
    endif
endfunction

function PK_Advance takes integer table returns nothing
    local integer x = table*2
    if PK_Stack[x] == 0 or PK_Stack[x+1] == 0 or PK_Street[table] == 3 then
        call PK_Showdown(table)
        return
    endif
    set PK_Street[table] = PK_Street[table]+1
    set PK_Paid[x] = 0
    set PK_Paid[x+1] = 0
    set PK_Acted[x] = false
    set PK_Acted[x+1] = false
    set PK_LastRaise[table] = 10
    set PK_Turn[table] = 1-PK_Dealer[table]
    set PK_Actions[table] = 0
endfunction

function PK_Deal takes integer table returns nothing
    local integer x = table*2
    local integer i = 0
    local integer j
    local integer tmp
    local integer small
    local integer big
    loop
        exitwhen i >= 52
        set PK_Deck[i] = i
        set i = i+1
    endloop
    set i = 51
    loop
        exitwhen i <= 0
        set j = PK_Random(i+1)
        set tmp = PK_Deck[i]
        set PK_Deck[i] = PK_Deck[j]
        set PK_Deck[j] = tmp
        set i = i-1
    endloop
    loop
        exitwhen i >= 9
        set PK_Cards[table*9+i] = PK_Deck[i]
        set i = i+1
    endloop
    set PK_Hand[table] = PK_Hand[table]+1
    set PK_Dealer[table] = 1-PK_Dealer[table]
    set small = x+PK_Dealer[table]
    set big = x+1-PK_Dealer[table]
    set PK_Street[table] = 0
    set PK_Turn[table] = PK_Dealer[table]
    set PK_LastRaise[table] = 10
    set PK_Actions[table] = 0
    set PK_Clock[table] = 30
    set PK_Wait[table] = 2
    set PK_Reveal[table] = false
    set PK_Acted[x] = false
    set PK_Acted[x+1] = false
    call PK_Pay(small,IMinBJ(5,PK_Stack[small]))
    call PK_Pay(big,IMinBJ(10,PK_Stack[big]))
    set PK_Note[table] = "Blinds posted  /  "+PK_SeatName(table,PK_Dealer[table])+" "+I2S(PK_Paid[small])+"g  /  "+PK_SeatName(table,1-PK_Dealer[table])+" "+I2S(PK_Paid[big])+"g"
    if PK_Stack[small] == 0 or (PK_Stack[big] == 0 and PK_Paid[small] >= PK_Paid[big]) then
        call PK_Showdown(table)
    endif
    call PK_TableChanged(table)
endfunction

function PK_Action takes integer table, integer seat, integer action, integer target returns nothing
    local integer x = table*2+seat
    local integer y = table*2+1-seat
    local integer top = PK_Top(table)
    local integer due = IMinBJ(PK_Stack[x],top-PK_Paid[x])
    local integer cap = PK_Paid[x]+PK_Stack[x]
    local integer size = target-top
    local string name = PK_SeatName(table,seat)
    local integer viewer = PK_PlayerAt(table,seat)
    if CAS_ended or PK_Turn[table] != seat then
        return
    endif
    if action == 0 then
        call PK_End(table,1-seat,name+" folded")
        return
    elseif action == 1 then
        call PK_Pay(x,due)
        if due > 0 then
            set PK_Note[table] = name+" called "+I2S(due)+"g"
        else
            set PK_Note[table] = name+" checked"
        endif
    else
        if size <= 0 or target > cap or PK_Stack[y] == 0 or (size < PK_LastRaise[table] and target != cap) or (PK_Acted[x] and due < PK_LastRaise[table]) then
            if viewer >= 0 then
                set PK_Feedback[viewer] = "Raise to "+I2S(top+PK_LastRaise[table])+"g or more, or go all-in within your stack."
            endif
            return
        endif
        call PK_Pay(x,target-PK_Paid[x])
        if size >= PK_LastRaise[table] then
            set PK_LastRaise[table] = size
            set PK_Acted[y] = false
        endif
        if top == 0 then
            set PK_Note[table] = name+" bet "+I2S(target)+"g"
        else
            set PK_Note[table] = name+" raised to "+I2S(target)+"g"
        endif
        if PK_Stack[x] == 0 then
            set PK_Note[table] = PK_Note[table]+"  /  ALL-IN"
        endif
    endif
    set PK_Acted[x] = true
    set PK_Actions[table] = PK_Actions[table]+1
    set PK_Turn[table] = 1-seat
    set PK_Clock[table] = 30
    set PK_Wait[table] = 2
    if action == 1 and (PK_Stack[x] == 0 or PK_Stack[y] == 0) then
        call PK_Showdown(table)
    elseif PK_Paid[x] == PK_Paid[y] and PK_Acted[x] and PK_Acted[y] then
        call PK_Advance(table)
    endif
    call PK_TableChanged(table)
endfunction

function PK_Return takes integer v, integer chips, boolean practice returns nothing
    local integer stake = PokerBuyIn[v]
    if stake <= 0 then
        return
    endif
    set PokerBuyIn[v] = 0
    if practice then
        call CAS_Settle(0,v+1,stake,chips,stake)
    else
        set CAS_escrow[v+1] = CAS_escrow[v+1]-stake
        call CAS_Credit(0,v+1,IMinBJ(stake,chips),IMaxBJ(0,chips-stake))
    endif
    set PK_Table[v] = 0
    set PK_Version[v] = PK_Version[v]+1
    set PK_Feedback[v] = "Wallet credited "+I2S(chips)+"g."
endfunction

function PK_CloseTable takes integer table, boolean refundHand returns nothing
    local integer x = table*2
    local integer guest = PK_Guest[table]-1
    if refundHand then
        set PK_Stack[x] = PK_Stack[x]+PK_Total[x]
        set PK_Stack[x+1] = PK_Stack[x+1]+PK_Total[x+1]
        set PK_Note[table] = "Match ended. Unsettled hand refunded."
    endif
    call PK_Return(table,PK_Stack[x],guest < 0)
    set PK_Feedback[table] = PK_Note[table]+"  /  "+PK_Feedback[table]
    if guest >= 0 then
        call PK_Return(guest,PK_Stack[x+1],false)
        set PK_Feedback[guest] = PK_Note[table]+"  /  "+PK_Feedback[guest]
    endif
    set PK_Guest[table] = 0
    set PK_Turn[table] = -1
    set PK_Hand[table] = 0
    set PK_Total[x] = 0
    set PK_Total[x+1] = 0
    set PK_Paid[x] = 0
    set PK_Paid[x+1] = 0
endfunction

function PK_CancelQueue takes integer v returns nothing
    if PK_Queue == v+1 then
        set PK_Queue = 0
        call PK_Return(v,PokerBuyIn[v],false)
    endif
endfunction

function PK_Join takes integer v, integer amount, boolean practice returns nothing
    local integer table = PK_Queue-1
    local integer backing = 0
    if PK_Table[v] != 0 or PK_Queue == v+1 or CAS_ended or not PK_Eligible(v) then
        return
    endif
    if amount < 100 or amount > 1500 then
        set PK_Feedback[v] = "Choose a buy-in from 100 to 1,500 gold."
        return
    endif
    if practice then
        set backing = amount
    endif
    if not CAS_Reserve(0,v+1,amount,backing) then
        set PK_Feedback[v] = CAS_note[v+1]
        return
    endif
    set PokerBuyIn[v] = amount
    set PK_Default[v] = amount
    set PK_Feedback[v] = ""
    set PK_Version[v] = PK_Version[v]+1
    if not practice and table >= 0 and not PK_Eligible(table) then
        call PK_CancelQueue(table)
        set table = -1
    endif
    if practice then
        set table = v
        set PK_Guest[table] = 0
    elseif table < 0 then
        set PK_Queue = v+1
        return
    else
        set PK_Queue = 0
        set PK_Guest[table] = v+1
        set PK_Table[v] = table+1
        set PK_Feedback[table] = ""
        call DisplayTimedTextToPlayer(Player(table),0,0,6,"Poker opponent found. Open -poker to play.")
    endif
    set PK_Table[table] = table+1
    set PK_Stack[table*2] = PokerBuyIn[table]
    set PK_Stack[table*2+1] = amount
    call PK_Deal(table)
endfunction
