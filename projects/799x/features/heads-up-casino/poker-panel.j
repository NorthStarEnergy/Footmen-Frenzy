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
    local string prompt = "Buy-in  /  100 to 1,500g"
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
    call BlzFrameSetText(PK_Status[v],status)
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
        call CUI_Text(PK_Next[v],"Find player")
        call CUI_Text(PK_Alternate[v],"Practice")
        call CUI_Paint(PK_Next[v],4,not CAS_ended and CAS_ready[v+1])
    endif
    call CUI_Paint(PK_Alternate[v],0,not CAS_ended and CAS_ready[v+1])
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

function PK_Bot takes integer table returns nothing
    local integer x = table*2+1
    local integer due = PK_Top(table)-PK_Paid[x]
    local integer strength
    local integer roll = PK_Random(100)
    local integer rank = ModuloInteger(PK_Cards[table*9+2],13)
    local integer other = ModuloInteger(PK_Cards[table*9+3],13)
    local integer target = IMinBJ(PK_Paid[x]+PK_Stack[x],PK_Top(table)+PK_LastRaise[table])
    if PK_Street[table] == 0 then
        set strength = 0
        if rank == other or (rank >= 9 and other >= 8) then
            set strength = 2
        endif
    else
        set strength = PK_Score(table,1,PK_BoardCount(table))/759375
    endif
    if due > 10 and strength == 0 and roll < 55 then
        call PK_Action(table,1,0,0)
    elseif PK_Actions[table] < 4 and target > PK_Top(table) and PK_Stack[x-1] > 0 and (not PK_Acted[x] or due >= PK_LastRaise[table]) and (roll < 8 or (strength >= 2 and roll < 55)) then
        call PK_Action(table,1,2,target)
    else
        call PK_Action(table,1,1,0)
    endif
endfunction

// All amounts and actions are revalidated after synchronization. The version
// binds a click to the turn and hand the player actually saw.
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
        if action == "j" or action == "p" then
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
    elseif f == PK_Next[v] then
        set action = "j"
        if PK_Table[v] != 0 then
            set action = "n"
        endif
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
