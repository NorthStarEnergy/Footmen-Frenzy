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

function PK_Score takes integer seat returns integer
    local integer i = 0
    local integer a = 0
    local integer b = 0
    local integer c = 0
    local integer d = 0
    local integer e = 0
    local integer best = 0
    local integer value = 0
    local integer n = 7
    set PK_Eval[0] = PK_Cards[seat*2]
    set PK_Eval[1] = PK_Cards[seat*2+1]
    loop
        exitwhen i >= 5
        set PK_Eval[i+2] = OP_Board[i]
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

function PK_Pay takes integer x, integer amount returns nothing
    set PK_Stack[x] = PK_Stack[x]-amount
    set PK_Paid[x] = PK_Paid[x]+amount
    set PK_Total[x] = PK_Total[x]+amount
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
        set status = "Waiting for second admin"
        set note = "Solo test: cash out, then open Blackjack > House poker."
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
        call BlzFrameSetText(PK_Prompt[v],"Exact buy-in (press Enter)")
    endif
    if note == "" then
        set note = OP_Note
    endif
    call BlzFrameSetVisible(PK_Lower[v],not seated and not CAS_ended)
    call BlzFrameSetVisible(PK_Higher[v],not seated and not CAS_ended)
    call CUI_Paint(PK_Lower[v],0,PK_Default[v] > 100)
    call CUI_Paint(PK_Higher[v],0,PK_Default[v] < 1500)
    if not seated and not CAS_ended then
        if not CAS_ready[v+1] then
            set note = "Waiting for your wallet to load."
        elseif CAS_gold[v+1] < PK_Default[v] then
            set note = "Buy-in "+I2S(PK_Default[v])+"g / wallet "+I2S(CAS_gold[v+1])+"g. Choose a funded amount."
        endif
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
    call CUI_Text(PK_Next[v],"Buy in "+I2S(PK_Default[v])+"g")
    call CUI_Paint(PK_Next[v],4,CAS_ready[v+1] and CAS_gold[v+1] >= PK_Default[v])
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
    elseif f == OP_PageButton[v] then
        set OP_Page[v] = ModuloInteger(OP_Page[v]+1,IMaxBJ(1,(OP_RosterCount()+4)/5))
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
    elseif f == PK_Alternate[v] then
        set action = "l"
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
        if OP_Turn == v and OP_Phase == 1 then
            set action = "r"
        endif
    endif
    if action == "j" or action == "p" then
        call PK_Submit(v,action,I2S(PK_Default[v]))
        return
    endif
    if action != "" and GetLocalPlayer() == Player(v) then
        call BlzSendSyncData("FFPK40",I2S(PK_Version[v])+"/"+action+BlzFrameGetText(PK_Input[v]))
        call BlzFrameSetFocus(PK_Input[v],false)
    endif
    set f = null
endfunction

function PK_Chat takes nothing returns nothing
    local integer v = GetPlayerId(GetTriggerPlayer())
    local string line = GetEventPlayerChatString()
    if PK_Started[v] and PK_Eligible(v) then
        if line == "-poker" then
            set HousePK_Hidden[v] = true
            if GetLocalPlayer() == Player(v) and HousePK_Dialog[v] != null then
                call BlzFrameSetVisible(HousePK_Dialog[v],false)
            endif
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
    local integer v = 0
    if CAS_ended then
        return
    endif
    loop
        exitwhen v >= 24
        if PokerBuyIn[v] > 0 and not PK_Eligible(v) then
            call OP_Leave(v)
        endif
        set v = v+1
    endloop
    if OP_Phase == 0 then
        if OP_Seats >= 2 then
            set OP_Clock = OP_Clock-1
            if OP_Clock <= 0 then
                call OP_Deal()
            endif
        else
            set OP_Clock = 8
        endif
    elseif OP_Phase == 1 then
        set v = OP_Turn
        set OP_Clock = OP_Clock-1
        if OP_Leaving[v] then
            call OP_Action(v,"f",0)
        elseif OP_Clock <= 0 then
            // An absent player cannot keep posting blinds hand after hand.
            set OP_Leaving[v] = true
            if PK_Paid[v] == OP_Bet then
                call OP_Action(v,"c",0)
            else
                call OP_Action(v,"f",0)
            endif
        endif
    endif
    call OP_Refresh()
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
            set PK_Dialog[p] = BlzCreateFrameByType("BACKDROP","PokerTable",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),"",p)
            call BlzFrameSetSize(PK_Dialog[p],0.70,0.48)
            call BlzFrameSetAbsPoint(PK_Dialog[p],FRAMEPOINT_TOPLEFT,0.05,0.526)
            call BlzFrameSetTexture(PK_Dialog[p],"PokerUI\\table.blp",0,true)
            call BlzFrameSetLevel(PK_Dialog[p],50)
            call BlzFrameSetVisible(PK_Dialog[p],false)
            set PK_Title[p] = PK_Label(p,0.025,0.014,0.49,0.040,1.12)
            set PK_BotLabel[p] = PK_Label(p,0.025,0.064,0.270,0.024,1.00)
            set PK_BotStack[p] = PK_Label(p,0.025,0.090,0.405,0.100,0.98)
            set PK_HumanLabel[p] = PK_Label(p,0.025,0.308,0.231,0.023,0.91)
            set PK_HumanStack[p] = PK_Label(p,0.025,0.335,0.155,0.051,1.08)
            set PK_PotLabel[p] = PK_Label(p,0.537,0.197,0.139,0.048,1.24)
            set PK_Status[p] = PK_Label(p,0.454,0.312,0.215,0.024,1.05)
            set PK_CallLabel[p] = PK_Label(p,0.454,0.340,0.215,0.032,1.20)
            set PK_Text[p] = PK_Label(p,0.025,0.398,0.65,0.037,1.0)
            set PK_PotChips[p] = PK_Texture(p,"chips1",0.532,0.245,0.050,0.030)
            set PK_HumanDealer[p] = PK_Texture(p,"dealer",0.247,0.325,0.022,0.022)
            set PK_Face[p*9] = PK_Texture(p,"empty",0.286,0.293,0.060,0.086)
            set PK_Face[p*9+1] = PK_Texture(p,"empty",0.354,0.293,0.060,0.086)
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
            call BlzTriggerRegisterPlayerSyncEvent(sync,Player(p),"FFPK40",false)
            set OP_PageButton[p] = PK_Button(p,click,0.353,-0.060,0.074,"Seats >")
            set PK_Alternate[p] = PK_Button(p,click,0.455,-0.150,0.190,"Cash out")
            set PK_Lower[p] = PK_Button(p,click,0.454,-0.149,0.105,"-100g")
            set PK_Higher[p] = PK_Button(p,click,0.565,-0.149,0.110,"+100g")
            set PK_Fold[p] = PK_Button(p,click,0.025,-0.439,0.105,"Fold")
            set PK_Call[p] = PK_Button(p,click,0.135,-0.439,0.12,"Check / Call")
            set PK_Raise[p] = PK_Button(p,click,0.26,-0.439,0.12,"Raise to")
            set PK_Allin[p] = PK_Button(p,click,0.385,-0.439,0.13,"All-in")
            set PK_Next[p] = PK_Button(p,click,0.478,-0.439,0.197,"Join table")
            set PK_Hide[p] = PK_Button(p,click,0.565,-0.018,0.11,"Hide table")
            call TriggerAddAction(click,function PK_Click)
            call TriggerRegisterPlayerChatEvent(chat,Player(p),"-poker",true)
            call TriggerRegisterPlayerChatEvent(chat,Player(p),"-raise ",false)
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

function PK_PauseUnit takes nothing returns nothing
    call PauseUnit(GetEnumUnit(),true)
endfunction

function PK_Init takes nothing returns nothing
    set OP_ScoreTimer = CreateTimer()
    set PK_Seed = GetRandomInt(1,2147483646)
    call TimerStart(CreateTimer(),2,false,function PK_Start)
endfunction
