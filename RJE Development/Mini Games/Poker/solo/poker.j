function PK_Eligible takes integer p returns boolean
    return CasinoAdmin(p+1) and CAS_User(p+1)
endfunction

function PK_Random takes integer bound returns integer
    // Park-Miller/Schrage avoids signed overflow; separate from battle RNG.
    local integer hi = PK_Seed / 127773
    local integer lo = ModuloInteger(PK_Seed, 127773)
    set PK_Seed = 16807 * lo - 2836 * hi
    if PK_Seed <= 0 then
        set PK_Seed = PK_Seed + 2147483647
    endif
    return ModuloInteger(PK_Seed, bound)
endfunction

function PK_Card takes integer c returns string
    local integer r = ModuloInteger(c, 13)
    local integer s = c / 13
    local string ranks = "23456789TJQKA"
    local string suit = "C"
    local string color = "|cff8ad6ff"
    if s == 1 then
        set suit = "D"
        set color = "|cffffa757"
    elseif s == 2 then
        set suit = "H"
        set color = "|cffff7777"
    elseif s == 3 then
        set suit = "S"
        set color = "|cffffffff"
    endif
    return color + SubString(ranks, r, r + 1) + suit + "|r"
endfunction

function PK_Score5 takes integer a, integer b, integer c, integer d, integer e returns integer
    local integer i = 2
    local integer j = 0
    local integer r = 0
    local integer straight = 0
    local integer run = 0
    local integer four = 0
    local integer three = 0
    local integer pair1 = 0
    local integer pair2 = 0
    local integer kick = 0
    local integer packed = 0
    local boolean flush = a / 13 == b / 13 and a / 13 == c / 13 and a / 13 == d / 13 and a / 13 == e / 13
    loop
        exitwhen i > 14
        set PK_Count[i] = 0
        set i = i + 1
    endloop
    set PK_Count[ModuloInteger(a,13)+2] = PK_Count[ModuloInteger(a,13)+2]+1
    set PK_Count[ModuloInteger(b,13)+2] = PK_Count[ModuloInteger(b,13)+2]+1
    set PK_Count[ModuloInteger(c,13)+2] = PK_Count[ModuloInteger(c,13)+2]+1
    set PK_Count[ModuloInteger(d,13)+2] = PK_Count[ModuloInteger(d,13)+2]+1
    set PK_Count[ModuloInteger(e,13)+2] = PK_Count[ModuloInteger(e,13)+2]+1
    set i = 14
    loop
        exitwhen i < 2
        if PK_Count[i] == 4 then
            set four = i
        elseif PK_Count[i] == 3 then
            set three = i
        elseif PK_Count[i] == 2 then
            if pair1 == 0 then
                set pair1 = i
            else
                set pair2 = i
            endif
        endif
        set r = 0
        loop
            exitwhen r >= PK_Count[i]
            set PK_Sort[j] = i
            set j = j + 1
            set r = r + 1
        endloop
        if PK_Count[i] == 1 then
            set kick = kick * 15 + i
        endif
        set i = i - 1
    endloop
    set i = 2
    loop
        exitwhen i > 14
        if PK_Count[i] > 0 then
            set run = run + 1
            if run >= 5 then
                set straight = i
            endif
        else
            set run = 0
        endif
        set i = i + 1
    endloop
    if straight == 0 and PK_Count[14] > 0 and PK_Count[2] > 0 and PK_Count[3] > 0 and PK_Count[4] > 0 and PK_Count[5] > 0 then
        set straight = 5
    endif
    set i = 0
    loop
        exitwhen i >= 5
        set packed = packed * 15 + PK_Sort[i]
        set i = i + 1
    endloop
    if flush and straight > 0 then
        return 8 * 759375 + straight
    elseif four > 0 then
        return 7 * 759375 + four * 15 + kick
    elseif three > 0 and pair1 > 0 then
        return 6 * 759375 + three * 15 + pair1
    elseif flush then
        return 5 * 759375 + packed
    elseif straight > 0 then
        return 4 * 759375 + straight
    elseif three > 0 then
        return 3 * 759375 + three * 225 + kick
    elseif pair2 > 0 then
        return 2 * 759375 + pair1 * 225 + pair2 * 15 + kick
    elseif pair1 > 0 then
        return 759375 + pair1 * 3375 + kick
    endif
    return packed
endfunction

function PK_Score takes integer p, integer seat, integer board returns integer
    local integer base = p * 9
    local integer i = 0
    local integer a = 0
    local integer b = 0
    local integer c = 0
    local integer d = 0
    local integer e = 0
    local integer best = 0
    local integer value = 0
    local integer n = board + 2
    set PK_Eval[0] = PK_Cards[base + seat * 2]
    set PK_Eval[1] = PK_Cards[base + seat * 2 + 1]
    loop
        exitwhen i >= board
        set PK_Eval[i+2] = PK_Cards[base+4+i]
        set i = i + 1
    endloop
    loop
        exitwhen a >= n-4
        set b = a+1
        loop
            exitwhen b >= n-3
            set c = b+1
            loop
                exitwhen c >= n-2
                set d = c+1
                loop
                    exitwhen d >= n-1
                    set e = d+1
                    loop
                        exitwhen e >= n
                        set value = PK_Score5(PK_Eval[a],PK_Eval[b],PK_Eval[c],PK_Eval[d],PK_Eval[e])
                        set best = IMaxBJ(best,value)
                        set e = e+1
                    endloop
                    set d = d+1
                endloop
                set c = c+1
            endloop
            set b = b+1
        endloop
        set a = a+1
    endloop
    return best
endfunction

function PK_Category takes integer score returns string
    local integer c = score / 759375
    if c == 8 then
        return "straight flush"
    elseif c == 7 then
        return "four of a kind"
    elseif c == 6 then
        return "full house"
    elseif c == 5 then
        return "flush"
    elseif c == 4 then
        return "straight"
    elseif c == 3 then
        return "three of a kind"
    elseif c == 2 then
        return "two pair"
    elseif c == 1 then
        return "one pair"
    endif
    return "high card"
endfunction

function PK_BoardCount takes integer p returns integer
    if PK_Street[p] == 0 then
        return 0
    endif
    return IMinBJ(5,PK_Street[p]+2)
endfunction

function PK_Pay takes integer x, integer amount returns nothing
    set PK_Stack[x] = PK_Stack[x]-amount
    set PK_Paid[x] = PK_Paid[x]+amount
    set PK_Total[x] = PK_Total[x]+amount
endfunction

function PK_PlayerAt takes integer table, integer seat returns integer
    if seat == 0 then
        return table
    endif
    return PK_Guest[table]-1
endfunction

function PK_SeatName takes integer table, integer seat returns string
    local integer viewer = PK_PlayerAt(table,seat)
    if viewer < 0 then
        return NS_Name(NS_Dealt[table])
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
        call CAS_ResultSound(PK_PlayerAt(table,winner)+1,pot/2)
        call CAS_ResultSound(PK_PlayerAt(table,1-winner)+1,-(pot/2))
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
        set NS_Dealt[table] = NS_Selected[v]
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

function PK_Texture takes integer p, string name, real x, real y, real w, real h returns framehandle
    local framehandle f = BlzCreateFrameByType("BACKDROP","PokerArtwork",PK_Dialog[p],"",p)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PK_Dialog[p],FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetTexture(f,"PokerUI\\"+name+".blp",0,true)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function PK_Label takes integer p, real x, real y, real w, real h, real scale returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","PokerLabel",PK_Dialog[p],"",p)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PK_Dialog[p],FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetFont(f,"CasinoUI\\Bold.ttf",0.0115*scale,0)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function PK_ChipArt takes framehandle f, integer chips returns nothing
    local integer count = 1
    if chips >= 500 then
        set count = 4
    elseif chips >= 200 then
        set count = 3
    elseif chips >= 50 then
        set count = 2
    endif
    call BlzFrameSetVisible(f,chips > 0)
    call BlzFrameSetTexture(f,"PokerUI\\chips"+I2S(count)+".blp",0,true)
endfunction

function PK_Render takes integer v returns nothing
    local integer table = PK_Table[v]-1
    local integer seat = 0
    local integer x
    local integer y
    local integer i = 0
    local integer card
    local integer top
    local integer due
    local integer cap
    local integer amount = PK_Default[v]
    local boolean seated = table >= 0
    local boolean waiting = PK_Queue == v+1
    local boolean turn = false
    local boolean canRaise = false
    local boolean live = false
    local string phase = "PREFLOP"
    local string status = "Choose a buy-in"
    local string prompt = "Exact buy-in (press Enter)"
    local string note = PK_Feedback[v]
    local string face
    if not PK_Started[v] then
        return
    endif
    if GetLocalPlayer() == Player(v) then
        call BlzFrameSetVisible(PK_Dialog[v],not PK_Hidden[v])
    endif
    if PK_Hidden[v] then
        return
    endif
    if seated then
        if table != v then
            set seat = 1
        endif
        set x = table*2+seat
        set y = table*2+1-seat
        set live = PK_Turn[table] >= 0
        set turn = PK_Turn[table] == seat
        set top = PK_Top(table)
        set cap = PK_Paid[x]+PK_Stack[x]
        set due = IMinBJ(PK_Stack[x],top-PK_Paid[x])
        set canRaise = turn and cap > top and PK_Stack[y] > 0 and (not PK_Acted[x] or due >= PK_LastRaise[table])
        set amount = IMinBJ(cap,top+PK_LastRaise[table])
        if PK_Street[table] == 1 then
            set phase = "FLOP"
        elseif PK_Street[table] == 2 then
            set phase = "TURN"
        elseif PK_Street[table] == 3 then
            set phase = "RIVER"
        endif
        call BlzFrameSetText(PK_Title[v],"NO-LIMIT HOLD'EM  /  5-10g|n"+phase+"  /  Hand "+I2S(PK_Hand[table]))
        call BlzFrameSetText(PK_HumanLabel[v],"YOU")
        call BlzFrameSetText(PK_BotLabel[v],PK_SeatName(table,1-seat))
        call BlzFrameSetText(PK_HumanStack[v],"Stack  "+CUI_Value(I2S(PK_Stack[x]))+"|nBet     "+CUI_Value(I2S(PK_Paid[x])))
        call BlzFrameSetText(PK_BotStack[v],"Stack  "+CUI_Value(I2S(PK_Stack[y]))+"|nBet     "+CUI_Value(I2S(PK_Paid[y])))
        if live then
            call BlzFrameSetText(PK_PotLabel[v],"POT|n"+CUI_Value(I2S(PK_Total[x]+PK_Total[y])+"g"))
            if turn then
                set status = "|cff8cf2acYOUR TURN|r  /  "+I2S(PK_Clock[table])+"s"
            else
                set status = "Opponent's turn  /  "+I2S(PK_Clock[table])+"s"
            endif
        else
            call BlzFrameSetText(PK_PotLabel[v],"LAST POT|n"+CUI_Value(I2S(PK_LastPot[table])+"g"))
            set status = "Hand complete"
            if PK_Ready[x] then
                set status = "Waiting for opponent"
            elseif PK_Ready[y] and PK_Guest[table] != 0 then
                set status = "Opponent is ready"
            endif
        endif
        set prompt = "Raise to  /  Min "+I2S(amount)+"g"
        if due > 0 then
            call CUI_Text(PK_Call[v],"Call "+I2S(due)+"g")
        else
            call CUI_Text(PK_Call[v],"Check")
        endif
        call BlzFrameSetText(PK_CallLabel[v],"TO CALL   "+CUI_Value(I2S(due)+"g"))
        call BlzFrameSetVisible(PK_CallLabel[v],turn)
        call PK_ChipArt(PK_HumanChips[v],PK_Stack[x])
        call PK_ChipArt(PK_BotChips[v],PK_Stack[y])
        call PK_ChipArt(PK_PotChips[v],PK_Total[x]+PK_Total[y])
        call BlzFrameSetVisible(PK_HumanDealer[v],PK_Dealer[table] == seat)
        call BlzFrameSetVisible(PK_BotDealer[v],PK_Dealer[table] != seat)
        if note == "" then
            set note = PK_Note[table]
        endif
    else
        call BlzFrameSetText(PK_Title[v],"NO-LIMIT HOLD'EM  /  5-10g|nHeads-up table")
        if waiting then
            set status = "Waiting for a player"
            set note = "Seat reserved for "+I2S(PokerBuyIn[v])+"g. Cancel to return your buy-in."
        elseif CAS_ended then
            set status = "Match ended"
        endif
        call BlzFrameSetText(PK_HumanLabel[v],"YOUR WALLET")
        call BlzFrameSetText(PK_HumanStack[v],CUI_Value(I2S(CAS_gold[v+1])+"g"))
        call BlzFrameSetText(PK_BotLabel[v],"")
        call BlzFrameSetText(PK_BotStack[v],"")
        call BlzFrameSetText(PK_PotLabel[v],"")
        call BlzFrameSetVisible(PK_CallLabel[v],false)
        call BlzFrameSetVisible(PK_HumanChips[v],false)
        call BlzFrameSetVisible(PK_BotChips[v],false)
        call BlzFrameSetVisible(PK_PotChips[v],false)
        call BlzFrameSetVisible(PK_HumanDealer[v],false)
        call BlzFrameSetVisible(PK_BotDealer[v],false)
        if note == "" then
            set note = "Find player seats two humans. Practice deals against the computer."
        endif
    endif
    loop
        exitwhen i >= 9
        set face = "empty"
        if seated then
            if i < 2 then
                set card = PK_Cards[table*9+seat*2+i]
                set face = "card"+I2S(card)
            elseif i < 4 then
                set face = "back"
                if PK_Reveal[table] then
                    set face = "card"+I2S(PK_Cards[table*9+(1-seat)*2+i-2])
                endif
            elseif i-4 < PK_BoardCount(table) then
                set face = "card"+I2S(PK_Cards[table*9+i])
            endif
        endif
        call BlzFrameSetTexture(PK_Face[v*9+i],"PokerUI\\"+face+".blp",0,true)
        set i = i+1
    endloop
    call CUI_Text(NS_Selector[v],"Opponent > "+NS_Name(NS_Selected[v]))
    call BlzFrameSetVisible(NS_Selector[v],not seated and not waiting and not CAS_ended)
    call BlzFrameSetText(PK_Status[v],status)
    call BlzFrameSetVisible(PK_Lower[v],not seated and not CAS_ended and not waiting)
    call BlzFrameSetVisible(PK_Higher[v],not seated and not CAS_ended and not waiting)
    call CUI_Paint(PK_Lower[v],0,PK_Default[v] > 100)
    call CUI_Paint(PK_Higher[v],0,PK_Default[v] < 1500)
    if not seated and not CAS_ended and not waiting then
        if not CAS_ready[v+1] then
            set note = "Waiting for your wallet to load."
        elseif CAS_gold[v+1] < PK_Default[v] then
            set note = "Buy-in "+I2S(PK_Default[v])+"g / wallet "+I2S(CAS_gold[v+1])+"g. Choose a funded amount."
        endif
    endif
    call BlzFrameSetText(PK_Text[v],note)
    call BlzFrameSetText(PK_Prompt[v],prompt)
    call BlzFrameSetVisible(PK_Prompt[v],canRaise or (not seated and not waiting and not CAS_ended))
    call BlzFrameSetVisible(PK_Input[v],canRaise or (not seated and not waiting and not CAS_ended))
    if PK_InputVersion[v] != PK_Version[v] then
        set PK_InputVersion[v] = PK_Version[v]
        call BlzFrameSetText(PK_Input[v],I2S(amount))
    endif
    call BlzFrameSetVisible(PK_Fold[v],live)
    call BlzFrameSetVisible(PK_Call[v],live)
    call BlzFrameSetVisible(PK_Raise[v],live)
    call BlzFrameSetVisible(PK_Allin[v],live)
    call BlzFrameSetVisible(PK_Next[v],not live)
    call BlzFrameSetVisible(PK_Alternate[v],not live)
    call CUI_Paint(PK_Call[v],3,turn)
    call CUI_Paint(PK_Fold[v],1,turn)
    call CUI_Paint(PK_Raise[v],2,canRaise)
    call CUI_Paint(PK_Allin[v],2,canRaise)
    if seated and not live then
        call CUI_Text(PK_Next[v],"Next hand")
        call CUI_Text(PK_Alternate[v],"Cash out")
        call CUI_Paint(PK_Next[v],4,not PK_Ready[x] and PK_Stack[x] > 0 and PK_Stack[y] > 0)
    elseif waiting then
        call CUI_Text(PK_Next[v],"Finding player...")
        call CUI_Text(PK_Alternate[v],"Cancel search")
        call CUI_Paint(PK_Next[v],4,false)
    elseif not seated then
        call CUI_Text(PK_Next[v],"Find player "+I2S(PK_Default[v])+"g")
        call CUI_Text(PK_Alternate[v],"Practice "+I2S(PK_Default[v])+"g")
        call CUI_Paint(PK_Next[v],4,not CAS_ended and CAS_ready[v+1] and CAS_gold[v+1] >= PK_Default[v])
    endif
    call CUI_Paint(PK_Alternate[v],0,not CAS_ended and (seated or waiting or (CAS_ready[v+1] and CAS_gold[v+1] >= PK_Default[v])))
endfunction

function PK_Refresh takes integer v returns nothing
    local integer table = PK_Table[v]-1
    if table >= 0 then
        call PK_Render(table)
        if PK_Guest[table] > 0 then
            call PK_Render(PK_Guest[table]-1)
        endif
    else
        call PK_Render(v)
    endif
endfunction

function PK_Bot takes integer p returns nothing
    local integer x = p*2+1
    local integer top = IMaxBJ(PK_Paid[x],PK_Paid[x-1])
    local integer due = IMinBJ(PK_Stack[x],top-PK_Paid[x])
    local integer pot = PK_Total[x]+PK_Total[x-1]
    local integer move = NS_Move(p,due,pot,10,PK_Random(100))
    local integer target = top+IMaxBJ(PK_LastRaise[p],(pot+due)/2)
    if move == 2 and (PK_Actions[p] >= 4 or PK_Stack[x] <= due or PK_Stack[x-1] <= 0 or (PK_Acted[x] and due < PK_LastRaise[p])) then
        set move = 1
    endif
    call PK_Action(p,1,move,IMinBJ(target,PK_Paid[x]+PK_Stack[x]))
endfunction

function PK_Submit takes integer v, string action, string digits returns nothing
    local integer table = PK_Table[v]-1
    local integer seat = 0
    local integer x
    local integer other
    local integer amount = S2I(digits)
    if not PK_Started[v] or not PK_Eligible(v) or CAS_ended then
        return
    endif
    set PK_Feedback[v] = ""
    if (action == "j" or action == "p" or action == "r" or action == "b") and (I2S(amount) != digits or amount < 1) then
        set PK_Feedback[v] = "Enter a whole amount in gold."
    elseif table < 0 then
        if action == "o" and PK_Queue != v+1 then
            set NS_Selected[v] = ModuloInteger(NS_Selected[v]+1,5)
            set PK_Version[v] = PK_Version[v]+1
        elseif action == "j" or action == "p" then
            call PK_Join(v,amount,action == "p")
        elseif action == "l" then
            call PK_CancelQueue(v)
        elseif action == "b" and PK_Queue != v+1 then
            if amount >= 100 and amount <= 1500 then
                set PK_Default[v] = amount
                set PK_Version[v] = PK_Version[v]+1
                set PK_Feedback[v] = "Buy-in set to "+digits+"g."
            else
                set PK_Feedback[v] = "Buy-in must be 100 to 1,500g."
            endif
        endif
    else
        if table != v then
            set seat = 1
        endif
        set x = table*2+seat
        if PK_Turn[table] < 0 then
            if action == "l" then
                set other = PK_PlayerAt(table,1-seat)
                call PK_CloseTable(table,false)
                if other >= 0 then
                    call PK_Render(other)
                endif
            elseif action == "n" and PK_Stack[x] > 0 and PK_Stack[table*2+1-seat] > 0 and not PK_Ready[x] then
                set PK_Ready[x] = true
                if PK_Ready[table*2+1-seat] then
                    call PK_Deal(table)
                else
                    call PK_TableChanged(table)
                endif
            endif
        elseif PK_Turn[table] == seat then
            if action == "f" then
                call PK_Action(table,seat,0,0)
            elseif action == "c" then
                call PK_Action(table,seat,1,0)
            elseif action == "r" then
                call PK_Action(table,seat,2,amount)
            elseif action == "a" then
                call PK_Action(table,seat,2,PK_Stack[x]+PK_Paid[x])
            endif
        endif
    endif
    call PK_Refresh(v)
endfunction

function PK_Sync takes nothing returns nothing
    local integer v = GetPlayerId(GetTriggerPlayer())
    local string data = BlzGetTriggerSyncData()
    local string prefix = I2S(PK_Version[v])+"/"
    local integer n = StringLength(prefix)
    if SubString(data,0,n) == prefix then
        call PK_Submit(v,SubString(data,n,n+1),SubString(data,n+1,StringLength(data)))
    endif
endfunction

function PK_Click takes nothing returns nothing
    local integer v = GetPlayerId(GetTriggerPlayer())
    local framehandle f = BlzGetTriggerFrame()
    local string action = ""
    if not PK_Eligible(v) or PK_Hidden[v] then
        return
    endif
    if f == PK_Hide[v] then
        set PK_Hidden[v] = true
        call PK_Render(v)
        return
    elseif f == PK_Lower[v] or f == PK_Higher[v] then
        if f == PK_Lower[v] then
            call PK_Submit(v,"b",I2S(IMaxBJ(100,PK_Default[v]-100)))
        else
            call PK_Submit(v,"b",I2S(IMinBJ(1500,PK_Default[v]+100)))
        endif
        return
    elseif f == PK_Next[v] then
        set action = "j"
        if PK_Table[v] != 0 then
            set action = "n"
        endif
    elseif f == NS_Selector[v] then
        set action = "o"
    elseif f == PK_Alternate[v] then
        set action = "p"
        if PK_Table[v] != 0 or PK_Queue == v+1 then
            set action = "l"
        endif
    elseif f == PK_Call[v] then
        set action = "c"
    elseif f == PK_Fold[v] then
        set action = "f"
    elseif f == PK_Allin[v] then
        set action = "a"
    elseif f == PK_Raise[v] then
        set action = "r"
    elseif f == PK_Input[v] then
        set action = "b"
        if PK_Table[v] != 0 then
            set action = "r"
        endif
    endif
    if action == "j" or action == "p" then
        call PK_Submit(v,action,I2S(PK_Default[v]))
        return
    endif
    if action != "" and GetLocalPlayer() == Player(v) then
        call BlzSendSyncData("FFPK35",I2S(PK_Version[v])+"/"+action+BlzFrameGetText(PK_Input[v]))
        call BlzFrameSetFocus(PK_Input[v],false)
    endif
    set f = null
endfunction

function PK_Chat takes nothing returns nothing
    local integer v = GetPlayerId(GetTriggerPlayer())
    local string line = GetEventPlayerChatString()
    if PK_Started[v] and PK_Eligible(v) then
        if line == "-poker" then
            set CAS_view[v+1] = 0
            if GetLocalPlayer() == Player(v) and CAS_root[v+1] != null then
                call BlzFrameSetVisible(CAS_root[v+1],false)
            endif
            set PK_Hidden[v] = false
            call PK_Render(v)
        elseif SubString(line,0,7) == "-raise " then
            call PK_Submit(v,"r",SubString(line,7,StringLength(line)))
        endif
    endif
endfunction

function PK_Tick takes nothing returns nothing
    local integer table = 0
    local integer seat
    local integer other
    if PK_Queue > 0 and not PK_Eligible(PK_Queue-1) then
        call PK_CancelQueue(PK_Queue-1)
    endif
    loop
        exitwhen table >= 24
        if PK_Table[table] == table+1 then
            set seat = PK_Turn[table]
            if not PK_Eligible(table) or (PK_Guest[table] > 0 and not PK_Eligible(PK_Guest[table]-1)) then
                if seat >= 0 then
                    if not PK_Eligible(table) then
                        call PK_End(table,1,"Player left")
                    else
                        call PK_End(table,0,"Player left")
                    endif
                endif
                set other = PK_Guest[table]-1
                call PK_CloseTable(table,false)
                if other >= 0 then
                    call PK_Render(other)
                endif
            elseif seat >= 0 then
                set PK_Clock[table] = PK_Clock[table]-1
                if seat == 1 and PK_Guest[table] == 0 then
                    set PK_Wait[table] = PK_Wait[table]-1
                    if PK_Wait[table] <= 0 then
                        call PK_Bot(table)
                    endif
                elseif PK_Clock[table] <= 0 then
                    if PK_Paid[table*2+seat] == PK_Top(table) then
                        call PK_Action(table,seat,1,0)
                    else
                        call PK_Action(table,seat,0,0)
                    endif
                endif
            endif
            call PK_Refresh(table)
        elseif PK_Started[table] and not PK_Hidden[table] and PK_Table[table] == 0 then
            call PK_Render(table)
        endif
        set table = table+1
    endloop
endfunction

function PK_Button takes integer p, trigger t, real x, real y, real width, string label returns framehandle
    local framehandle f = CUI_Create(PK_Dialog[p],p,x,y,width,0.029,label,0)
    call BlzTriggerRegisterFrameEvent(t,f,FRAMEEVENT_CONTROL_CLICK)
    return f
endfunction

function PK_Start takes nothing returns nothing
    local integer p = 0
    local integer i = 0
    local trigger click = null
    local trigger chat = CreateTrigger()
    local trigger sync = CreateTrigger()
    call TriggerAddAction(sync,function PK_Sync)
    loop
        exitwhen p >= 24
        if CAS_User(p+1) then
            set PK_Hidden[p] = true
            set PK_Started[p] = true
            set PK_Stack[p*2] = 0
            set PK_Stack[p*2+1] = 0
            set PK_Dialog[p] = BlzCreateFrameByType("BACKDROP","PokerTable",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),"",p)
            call BlzFrameSetSize(PK_Dialog[p],0.70,0.48)
            call BlzFrameSetAbsPoint(PK_Dialog[p],FRAMEPOINT_TOPLEFT,0.05,0.57)
            call BlzFrameSetTexture(PK_Dialog[p],"PokerUI\\table.blp",0,true)
            call BlzFrameSetLevel(PK_Dialog[p],50)
            call BlzFrameSetVisible(PK_Dialog[p],false)
            set PK_Title[p] = PK_Label(p,0.025,0.014,0.49,0.040,1.12)
            set PK_BotLabel[p] = PK_Label(p,0.025,0.086,0.231,0.023,0.91)
            set PK_BotStack[p] = PK_Label(p,0.025,0.114,0.155,0.056,1.08)
            set PK_HumanLabel[p] = PK_Label(p,0.025,0.308,0.231,0.023,0.91)
            set PK_HumanStack[p] = PK_Label(p,0.025,0.335,0.155,0.051,1.08)
            set PK_PotLabel[p] = PK_Label(p,0.537,0.197,0.139,0.048,1.24)
            set PK_Status[p] = PK_Label(p,0.454,0.312,0.215,0.024,1.05)
            set PK_CallLabel[p] = PK_Label(p,0.454,0.340,0.215,0.032,1.20)
            set PK_Text[p] = PK_Label(p,0.025,0.398,0.65,0.037,1.0)
            set PK_HumanChips[p] = PK_Texture(p,"chips4",0.193,0.330,0.048,0.030)
            set PK_BotChips[p] = PK_Texture(p,"chips4",0.193,0.106,0.048,0.030)
            set PK_PotChips[p] = PK_Texture(p,"chips1",0.532,0.245,0.050,0.030)
            set PK_HumanDealer[p] = PK_Texture(p,"dealer",0.247,0.325,0.022,0.022)
            set PK_BotDealer[p] = PK_Texture(p,"dealer",0.247,0.113,0.022,0.022)
            set PK_Face[p*9] = PK_Texture(p,"empty",0.286,0.293,0.060,0.086)
            set PK_Face[p*9+1] = PK_Texture(p,"empty",0.354,0.293,0.060,0.086)
            set PK_Face[p*9+2] = PK_Texture(p,"back",0.286,0.081,0.060,0.086)
            set PK_Face[p*9+3] = PK_Texture(p,"back",0.354,0.081,0.060,0.086)
            set i = 0
            loop
                exitwhen i >= 5
                set PK_Face[p*9+4+i] = PK_Texture(p,"empty",0.184+I2R(i)*0.068,0.193,0.060,0.086)
                set i = i+1
            endloop
            set click = CreateTrigger()
            set PK_Default[p] = 100
            set PK_Version[p] = 1
            set PK_Feedback[p] = ""
            set PK_Prompt[p] = PK_Label(p,0.454,0.081,0.225,0.023,0.96)
            set PK_Input[p] = BlzCreateFrame("EscMenuEditBoxTemplate",PK_Dialog[p],0,p)
            call BlzFrameSetSize(PK_Input[p],0.168,0.033)
            call BlzFrameSetPoint(PK_Input[p],FRAMEPOINT_TOPLEFT,PK_Dialog[p],FRAMEPOINT_TOPLEFT,0.454,-0.107)
            call BlzFrameSetTextSizeLimit(PK_Input[p],6)
            call BlzTriggerRegisterFrameEvent(click,PK_Input[p],FRAMEEVENT_EDITBOX_ENTER)
            call BlzTriggerRegisterPlayerSyncEvent(sync,Player(p),"FFPK35",false)
            set PK_Alternate[p] = PK_Button(p,click,0.285,-0.439,0.180,"Practice")
            set PK_Lower[p] = PK_Button(p,click,0.454,-0.149,0.105,"-100g")
            set PK_Higher[p] = PK_Button(p,click,0.565,-0.149,0.110,"+100g")
            set PK_Fold[p] = PK_Button(p,click,0.025,-0.439,0.105,"Fold")
            set PK_Call[p] = PK_Button(p,click,0.135,-0.439,0.12,"Check / Call")
            set PK_Raise[p] = PK_Button(p,click,0.26,-0.439,0.12,"Raise to")
            set PK_Allin[p] = PK_Button(p,click,0.385,-0.439,0.13,"All-in")
            set PK_Next[p] = PK_Button(p,click,0.478,-0.439,0.197,"Find player")
            set NS_Selector[p] = PK_Button(p,click,0.307,-0.018,0.248,"Choose opponent")
            set PK_Hide[p] = PK_Button(p,click,0.565,-0.018,0.11,"Hide table")
            call TriggerAddAction(click,function PK_Click)
            call TriggerRegisterPlayerChatEvent(chat,Player(p),"-poker",true)
            call TriggerRegisterPlayerChatEvent(chat,Player(p),"-raise ",false)
            set PK_Turn[p] = -1
            set PK_Note[p] = ""
            call PK_Render(p)
        endif
        set p = p+1
    endloop
    call TriggerAddAction(chat,function PK_Chat)
    call TimerStart(CreateTimer(),1,true,function PK_Tick)
    call DestroyTimer(GetExpiredTimer())
    set click = null
    set chat = null
endfunction

function PK_Init takes nothing returns nothing
    set PK_Seed = GetRandomInt(1,2147483646)
    call TimerStart(CreateTimer(),2,false,function PK_Start)
endfunction
