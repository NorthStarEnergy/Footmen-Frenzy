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

function PK_Render takes integer v returns nothing
    local integer i = 0
    local integer seen = 0
    local integer pages = IMaxBJ(1,(OP_RosterCount()+4)/5)
    local integer page = ModuloInteger(OP_Page[v],pages)
    local integer amount = PK_Default[v]
    local integer board = 0
    local integer due = 0
    local boolean seated = PokerBuyIn[v] > 0
    local boolean turn = OP_Turn == v and OP_Phase == 1 and not OP_Leaving[v]
    local boolean raiseOK = turn and OP_CanRaise(v)
    local string phase = "Taking seats"
    local string status = "Join for the next deal"
    local string roster = ""
    local string face
    local string note = PK_Feedback[v]
    if not PK_Started[v] or GetLocalPlayer() != Player(v) then
        return
    endif
    call BlzFrameSetVisible(PK_Dialog[v],not PK_Hidden[v])
    if PK_Hidden[v] then
        return
    endif
    loop
        exitwhen i >= 24
        if PokerBuyIn[i] > 0 or OP_Dealt[i] then
            if seen/5 == page then
                if roster != "" then
                    set roster = roster+"|n"
                endif
                set roster = roster+OP_SeatLine(i)
            endif
            set seen = seen+1
        endif
        set i = i+1
    endloop
    call BlzFrameSetText(PK_BotLabel[v],"TABLE SEATS   "+CUI_Value(I2S(OP_Seats)))
    call BlzFrameSetText(PK_BotStack[v],roster)
    call BlzFrameSetVisible(OP_PageButton[v],pages > 1)
    call CUI_Text(OP_PageButton[v],I2S(page+1)+"/"+I2S(pages)+" >")
    if OP_Phase == 1 or OP_Phase == 2 then
        set phase = "Preflop"
        if OP_Street == 1 then
            set phase = "Flop"
        elseif OP_Street == 2 then
            set phase = "Turn"
        elseif OP_Street == 3 then
            set phase = "River"
        endif
        if OP_Turn >= 0 then
            set status = GetPlayerName(Player(OP_Turn))+"'s turn  /  "+I2S(OP_Clock)+"s"
            if turn then
                set status = "|cff8cf2acYOUR TURN|r   "+I2S(OP_Clock)+"s"
            endif
        else
            set status = "Showdown"
        endif
    elseif CAS_ended then
        set status = "Match ended"
    elseif OP_Seats >= 2 then
        set status = "Next deal in "+I2S(OP_Clock)+"s"
    elseif seated then
        set status = "Waiting for another player"
    endif
    if OP_Street > 0 then
        set board = OP_Street+2
    endif
    call BlzFrameSetText(PK_Title[v],"OPEN HOLD'EM  /  NO LIMIT 5-10g|n"+phase+"  /  Hand "+I2S(OP_Hand))
    call BlzFrameSetText(PK_Status[v],status)
    if OP_Phase == 0 and OP_Hand > 0 then
        call BlzFrameSetText(PK_PotLabel[v],"LAST POT|n"+CUI_Value(I2S(OP_Pot)+"g"))
    else
        call BlzFrameSetText(PK_PotLabel[v],"POT|n"+CUI_Value(I2S(OP_Pot)+"g"))
    endif
    call PK_ChipArt(PK_PotChips[v],OP_Pot)
    if seated then
        call BlzFrameSetText(PK_HumanLabel[v],"YOUR SEAT")
        call BlzFrameSetText(PK_HumanStack[v],"Stack  "+CUI_Value(I2S(PK_Stack[v])+"g")+"|nBet     "+CUI_Value(I2S(PK_Paid[v])+"g"))
    else
        call BlzFrameSetText(PK_HumanLabel[v],"YOUR WALLET")
        call BlzFrameSetText(PK_HumanStack[v],CUI_Value(I2S(CAS_gold[v+1])+"g"))
    endif
    call BlzFrameSetVisible(PK_HumanDealer[v],OP_Dealt[v] and OP_Button == v)
    set i = 0
    loop
        exitwhen i >= 9
        if i < 2 or i >= 4 then
            set face = "empty"
            if i < 2 and OP_Dealt[v] then
                set face = "card"+I2S(PK_Cards[v*2+i])
            elseif i >= 4 and i < 4+board then
                set face = "card"+I2S(OP_Board[i-4])
            endif
            call BlzFrameSetTexture(PK_Face[v*9+i],"PokerUI\\"+face+".blp",0,true)
        endif
        set i = i+1
    endloop
    if turn then
        set due = IMinBJ(PK_Stack[v],OP_Bet-PK_Paid[v])
        set amount = IMinBJ(PK_Stack[v]+PK_Paid[v],OP_Bet+OP_MinRaise)
        call BlzFrameSetText(PK_Prompt[v],"Raise to  /  Min "+I2S(amount)+"g")
        call BlzFrameSetText(PK_CallLabel[v],"TO CALL   "+CUI_Value(I2S(due)+"g"))
        if due > 0 then
            call CUI_Text(PK_Call[v],"Call "+I2S(due)+"g")
        else
            call CUI_Text(PK_Call[v],"Check")
        endif
    else
        call BlzFrameSetText(PK_Prompt[v],"Buy-in  /  100 to 1,500g")
    endif
    if note == "" then
        set note = OP_Note
    endif
    call BlzFrameSetText(PK_Text[v],note)
    call BlzFrameSetVisible(PK_CallLabel[v],turn)
    call BlzFrameSetVisible(PK_Prompt[v],(not seated and not CAS_ended) or raiseOK)
    call BlzFrameSetVisible(PK_Input[v],(not seated and not CAS_ended) or raiseOK)
    if PK_InputVersion[v] != PK_Version[v] then
        set PK_InputVersion[v] = PK_Version[v]
        call BlzFrameSetText(PK_Input[v],I2S(amount))
    endif
    call BlzFrameSetVisible(PK_Next[v],not seated and not CAS_ended)
    call CUI_Paint(PK_Next[v],4,CAS_ready[v+1])
    call BlzFrameSetVisible(PK_Alternate[v],seated)
    if OP_Phase == 1 and OP_Live[v] and PK_Stack[v] > 0 then
        call CUI_Text(PK_Alternate[v],"Fold & leave")
    elseif OP_Phase != 0 and OP_Dealt[v] then
        call CUI_Text(PK_Alternate[v],"Leave after pot")
    else
        call CUI_Text(PK_Alternate[v],"Cash out")
    endif
    call CUI_Paint(PK_Alternate[v],1,not OP_Leaving[v])
    call BlzFrameSetVisible(PK_Fold[v],turn)
    call BlzFrameSetVisible(PK_Call[v],turn)
    call BlzFrameSetVisible(PK_Raise[v],turn)
    call BlzFrameSetVisible(PK_Allin[v],turn)
    call CUI_Paint(PK_Raise[v],2,raiseOK)
    call CUI_Paint(PK_Allin[v],2,raiseOK)
endfunction

function OP_Refresh takes nothing returns nothing
    local integer v = GetPlayerId(GetLocalPlayer())
    if v < 24 then
        call PK_Render(v)
    endif
endfunction

function PK_Submit takes integer v, string action, string digits returns nothing
    local integer number = S2I(digits)
    if not PK_Started[v] or not PK_Eligible(v) or CAS_ended then
        return
    endif
    if (action == "r" or action == "j" or action == "b") and (I2S(number) != digits or number <= 0) then
        set PK_Feedback[v] = "Enter a whole amount in gold."
    elseif action == "j" then
        call OP_Join(v,number)
    elseif action == "b" and PokerBuyIn[v] == 0 then
        if number < 100 or number > 1500 then
            set PK_Feedback[v] = "Buy-in is 100 to 1,500g."
        else
            set PK_Default[v] = number
            set PK_Feedback[v] = "Buy-in set to "+digits+"g."
            set PK_Version[v] = PK_Version[v]+1
        endif
    elseif action == "l" then
        call OP_Leave(v)
    elseif action == "a" then
        call OP_Action(v,"r",PK_Paid[v]+PK_Stack[v])
    else
        call OP_Action(v,action,number)
    endif
    call OP_Refresh()
endfunction
