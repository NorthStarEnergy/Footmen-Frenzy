function AR_Fighter takes unit u returns boolean
    if AR_state != 2 or u == null then
        return false
    endif
    return GetOwningPlayer(u) == AR_owner[0] or GetOwningPlayer(u) == AR_owner[1]
endfunction

function AR_BarDamage takes nothing returns nothing
    if AR_Fighter(GetEventDamageSource()) != AR_Fighter(GetTriggerUnit()) then
        call BlzSetEventDamage(0)
    endif
endfunction

function AR_BarOrder takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local boolean fighter = AR_Fighter(u)
    local boolean outside
    if GetTriggerEventId() == EVENT_PLAYER_UNIT_ISSUED_POINT_ORDER then
        set outside = fighter != RectContainsCoords(AR_floor,GetOrderPointX(),GetOrderPointY())
    else
        set outside = fighter != AR_Fighter(GetOrderTargetUnit())
        if GetOrderTargetUnit() == null then
            set outside = fighter != RectContainsCoords(AR_floor,GetWidgetX(GetOrderTarget()),GetWidgetY(GetOrderTarget()))
        endif
    endif
    if outside then
        call PauseUnit(u,true)
        call IssueImmediateOrder(u,"stop")
        call PauseUnit(u,false)
    endif
    set u = null
endfunction

function AR_BarEntry takes nothing returns nothing
    local unit u = GetEnteringUnit()
    local player p = GetOwningPlayer(u)
    if not AR_Fighter(u) then
        if GetPlayerId(p) < 12 then
            call SetUnitPosition(u,GetPlayerStartLocationX(p),GetPlayerStartLocationY(p))
        else
            call SetUnitPosition(u,0,-256)
        endif
        call IssueImmediateOrder(u,"stop")
    endif
    set u = null
endfunction

function AR_Init takes nothing returns nothing
    local trigger entry = CreateTrigger()
    set AR_floor = Rect(-1024,5376,1024,6912)
    set AR_clock = CreateTimer()
    set AR_damage = CreateTrigger()
    set AR_orders = CreateTrigger()
    call TriggerRegisterEnterRectSimple(entry,AR_floor)
    call TriggerAddAction(entry,function AR_BarEntry)
    call TriggerRegisterAnyUnitEventBJ(AR_damage,EVENT_PLAYER_UNIT_DAMAGING)
    call TriggerAddAction(AR_damage,function AR_BarDamage)
    call TriggerRegisterAnyUnitEventBJ(AR_orders,EVENT_PLAYER_UNIT_ISSUED_POINT_ORDER)
    call TriggerRegisterAnyUnitEventBJ(AR_orders,EVENT_PLAYER_UNIT_ISSUED_TARGET_ORDER)
    call TriggerAddAction(AR_orders,function AR_BarOrder)
    call DisableTrigger(AR_damage)
    call DisableTrigger(AR_orders)
    // Level-one arena pool. Each hero has a native combat skill and no spawned army.
    set AR_roster[0] = 'H00A'
    set AR_skill[0] = 'AHtb'
    set AR_roster[1] = 'E002'
    set AR_skill[1] = 'AEer'
    set AR_roster[2] = 'U003'
    set AR_skill[2] = 'A00P'
    set AR_roster[3] = 'U004'
    set AR_skill[3] = 'AUcs'
    set AR_roster[4] = 'E005'
    set AR_skill[4] = 'AEfk'
    set AR_roster[5] = 'O004'
    set AR_skill[5] = 'AOcl'
    set entry = null
endfunction

function PK_Eligible takes integer p returns boolean
    return CasinoAdmin(p+1) and CAS_User(p+1)
endfunction

function FGA_Number takes string x returns boolean
    if x == null or x == "" or StringLength(x) > 11 then
        return false
    endif
    return I2S(S2I(x)) == x
endfunction

function FGA_Token takes string line, integer which returns string
    local integer i=0
    local string converted=""
    loop
        exitwhen i >= StringLength(line)
        if SubString(line,i,i+1) == " " then
            set converted=converted+"|"
        else
            set converted=converted+SubString(line,i,i+1)
        endif
        set i=i+1
    endloop
    return FFPS_Field(converted,which)
endfunction

function FGA_Find takes integer identity returns integer
    local integer s=1
    local integer found=0
    if identity == 0 then
        return 0
    endif
    loop
        exitwhen s > 24
        if CAS_ready[s] and GetPlayerSlotState(Player(s-1)) == PLAYER_SLOT_STATE_PLAYING and LoanIdentity[s] == identity then
            if found != 0 then
                return 0
            endif
            set found=s
        endif
        set s=s+1
    endloop
    return found
endfunction

function FGA_OnCommand takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local string line = GetEventPlayerChatString()
    local integer target = S2I(FGA_Token(line,1))
    local string amount = FGA_Token(line,2)
    local string fee = FGA_Token(line,3)
    local integer id = 1
    local integer match = 0
    if not PK_Eligible(s-1) then
        return
    endif
    if line == "-accept" then
        loop
            exitwhen id > 48
            if CreditOwner[id] != 0 and CreditTarget[id] == s then
                if match != 0 then
                    call CreditTell(s,"Multiple offers. Select the one you want in Credit.")
                    return
                endif
                set match = id
            endif
            set id = id+1
        endloop
    if match != 0 then
        call CreditAccept(s,match)
    endif
    elseif PK_Eligible(target-1) and CreditOpen(target) and target != s and FGA_Number(amount) and FGA_Number(fee) then
        call CreditPost(s,false,target,S2I(amount),0,0,0,S2I(fee))
        if CreditOwner[CreditSelected[s]] == s and CreditTarget[CreditSelected[s]] == target then
            call CreditTell(target,GetPlayerName(Player(s-1))+" offers "+amount+"g with a "+fee+"g fee. Review in Credit or type -accept.")
        endif
    else
        call CreditTell(s,"Use -loan slot amount fee, or open Casino > Credit.")
    endif
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

function BJ_Value takes integer card returns integer
    if ModuloInteger(card,13) == 12 then
        return 11
    endif
    return IMinBJ(10,ModuloInteger(card,13)+2)
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

function NS_Name takes integer id returns string
    if id == 0 then
        return "Maya Chen II"
    elseif id == 1 then
        return "Elise Park"
    elseif id == 2 then
        return "Alex Morgan"
    elseif id == 3 then
        return "Miles Bennett"
    endif
    return "Ethan Cole"
endfunction

function HousePK_Random takes integer bound returns integer
    // Park-Miller/Schrage avoids signed overflow; separate from battle RNG.
    local integer hi = HousePK_Seed / 127773
    local integer lo = ModuloInteger(HousePK_Seed, 127773)
    set HousePK_Seed = 16807 * lo - 2836 * hi
    if HousePK_Seed <= 0 then
        set HousePK_Seed = HousePK_Seed + 2147483647
    endif
    return ModuloInteger(HousePK_Seed, bound)
endfunction

function HousePK_Score takes integer p, integer seat, integer board returns integer
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
    set HousePK_Eval[0] = HousePK_Cards[base + seat * 2]
    set HousePK_Eval[1] = HousePK_Cards[base + seat * 2 + 1]
    loop
        exitwhen i >= board
        set HousePK_Eval[i+2] = HousePK_Cards[base+4+i]
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
                        set value = PK_Score5(HousePK_Eval[a],HousePK_Eval[b],HousePK_Eval[c],HousePK_Eval[d],HousePK_Eval[e])
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

function HousePK_BoardCount takes integer p returns integer
    if HousePK_Street[p] == 0 then
        return 0
    endif
    return IMinBJ(5,HousePK_Street[p]+2)
endfunction

function HousePK_Limit takes integer p, integer seat returns integer
    local integer x = p*2+seat
    local integer y = p*2+1-seat
    return IMinBJ(HousePK_Paid[x]+HousePK_Stack[x],HousePK_Paid[y]+HousePK_Stack[y])
endfunction

function HousePK_Pay takes integer x, integer amount returns nothing
    set HousePK_Stack[x] = HousePK_Stack[x]-amount
    set HousePK_Paid[x] = HousePK_Paid[x]+amount
    set HousePK_Total[x] = HousePK_Total[x]+amount
endfunction

function HousePK_End takes integer p, integer winner, string note returns nothing
    local integer x = p*2
    local integer pot = HousePK_Total[x]+HousePK_Total[x+1]
    if winner == 2 then
        set HousePK_Stack[x] = HousePK_Stack[x]+pot/2
        set HousePK_Stack[x+1] = HousePK_Stack[x+1]+pot/2
        set HousePK_Stack[x+1-HousePK_Dealer[p]] = HousePK_Stack[x+1-HousePK_Dealer[p]]+ModuloInteger(pot,2)
    else
        set HousePK_Stack[x+winner] = HousePK_Stack[x+winner]+pot
    endif
    if HousePokerBuyIn[p] > 0 then
        call CAS_Settle(0,p+1,HousePokerBuyIn[p],HousePK_Stack[x],HousePokerBuyIn[p])
        call CAS_ResultSound(p+1,HousePK_Stack[x]-HousePokerBuyIn[p])
        set HousePokerBuyIn[p] = 0
    endif
    set HousePK_Total[x] = 0
    set HousePK_Total[x+1] = 0
    set HousePK_Paid[x] = 0
    set HousePK_Paid[x+1] = 0
    set HousePK_Turn[p] = -1
    set HousePK_Note[p] = note+" (pot "+I2S(pot)+")"
endfunction

function HousePK_Showdown takes integer p returns nothing
    local integer human = HousePK_Score(p,0,5)
    local integer bot = HousePK_Score(p,1,5)
    set HousePK_Street[p] = 3
    set HousePK_Reveal[p] = true
    if human > bot then
        call HousePK_End(p,0,"You win: "+PK_Category(human))
    elseif bot > human then
        call HousePK_End(p,1,NS_Name(NS_Dealt[p])+" wins: "+PK_Category(bot))
    else
        call HousePK_End(p,2,"Split pot: "+PK_Category(human))
    endif
endfunction

function HousePK_Advance takes integer p returns nothing
    local integer x = p*2
    if HousePK_Stack[x] == 0 or HousePK_Stack[x+1] == 0 or HousePK_Street[p] == 3 then
        call HousePK_Showdown(p)
        return
    endif
    set HousePK_Street[p] = HousePK_Street[p]+1
    set HousePK_Paid[x] = 0
    set HousePK_Paid[x+1] = 0
    set HousePK_Acted[x] = false
    set HousePK_Acted[x+1] = false
    set HousePK_LastRaise[p] = 2
    set HousePK_Turn[p] = 1-HousePK_Dealer[p]
    set HousePK_Actions[p] = 0
endfunction

function HousePK_Deal takes integer p returns nothing
    local integer i = 0
    local integer j = 0
    local integer tmp = 0
    local integer x = p*2
    set HousePK_Note[p] = "Blinds 1/2. Raise button adds one minimum raise."
    if HouseStake[p] > 300 then
        set HousePK_Note[p] = "Maximum buy-in is 300 gold."
        return
    endif
    if not CAS_Reserve(0,p+1,HouseStake[p],HouseStake[p]) then
        set HousePK_Note[p] = CAS_note[p+1]
        return
    endif
    set NS_Dealt[p] = NS_Selected[p]
    set HousePokerBuyIn[p] = HouseStake[p]
    set HousePK_Stack[x] = HousePokerBuyIn[p]
    set HousePK_Stack[x+1] = HousePokerBuyIn[p]
    loop
        exitwhen i >= 52
        set HousePK_Deck[i] = i
        set i = i+1
    endloop
    set i = 51
    loop
        exitwhen i <= 0
        set j = HousePK_Random(i+1)
        set tmp = HousePK_Deck[i]
        set HousePK_Deck[i] = HousePK_Deck[j]
        set HousePK_Deck[j] = tmp
        set i = i-1
    endloop
    set i = 0
    loop
        exitwhen i >= 9
        set HousePK_Cards[p*9+i] = HousePK_Deck[i]
        set i = i+1
    endloop
    set HousePK_Hand[p] = HousePK_Hand[p]+1
    set HousePK_Dealer[p] = 1-HousePK_Dealer[p]
    set HousePK_Street[p] = 0
    set HousePK_Turn[p] = HousePK_Dealer[p]
    set HousePK_LastRaise[p] = 2
    set HousePK_Actions[p] = 0
    set HousePK_Clock[p] = 30
    set HousePK_Wait[p] = 2
    set HousePK_Reveal[p] = false
    set HousePK_Paid[x] = 0
    set HousePK_Paid[x+1] = 0
    set HousePK_Total[x] = 0
    set HousePK_Total[x+1] = 0
    set HousePK_Acted[x] = false
    set HousePK_Acted[x+1] = false
    set tmp = IMinBJ(HousePK_Stack[x],HousePK_Stack[x+1])
    call HousePK_Pay(x+HousePK_Dealer[p],IMinBJ(1,tmp))
    call HousePK_Pay(x+1-HousePK_Dealer[p],IMinBJ(2,tmp))
    if HousePK_Paid[x] == HousePK_Paid[x+1] and (HousePK_Stack[x] == 0 or HousePK_Stack[x+1] == 0) then
        call HousePK_Showdown(p)
    endif
endfunction

function HousePK_Action takes integer p, integer seat, integer action returns nothing
    local integer x = p*2+seat
    local integer y = p*2+1-seat
    local integer due = IMaxBJ(0,HousePK_Paid[y]-HousePK_Paid[x])
    local integer target = 0
    local integer raiseSize = 0
    if not PK_Eligible(p) or HousePK_Turn[p] != seat then
        return
    endif
    if action == 0 then
        if seat == 0 then
            call HousePK_End(p,1,"You fold. "+NS_Name(NS_Dealt[p])+" wins")
        else
            call HousePK_End(p,0,NS_Name(NS_Dealt[p])+" folds. You win")
        endif
        return
    elseif action == 1 then
        call HousePK_Pay(x,IMinBJ(due,HousePK_Stack[x]))
        if due == 0 then
            set HousePK_Note[p] = "Check."
        else
            set HousePK_Note[p] = "Call "+I2S(due)+"."
        endif
    else
        set target = IMaxBJ(HousePK_Paid[x],HousePK_Paid[y])+HousePK_LastRaise[p]
        if seat == 1 then
            set target = target-HousePK_LastRaise[p]+IMaxBJ(HousePK_LastRaise[p],(HousePK_Total[x]+HousePK_Total[y]+due)/2)
        endif
        if action == 3 then
            set target = HousePK_Limit(p,seat)
        endif
        set target = IMinBJ(target,HousePK_Limit(p,seat))
        set raiseSize = target-IMaxBJ(HousePK_Paid[x],HousePK_Paid[y])
        if raiseSize <= 0 or (HousePK_Acted[x] and due < HousePK_LastRaise[p]) then
            return
        endif
        call HousePK_Pay(x,target-HousePK_Paid[x])
        if raiseSize >= HousePK_LastRaise[p] then
            set HousePK_LastRaise[p] = raiseSize
            set HousePK_Acted[y] = false
        endif
        set HousePK_Note[p] = "Raise to "+I2S(target)+"."
    endif
    set HousePK_Acted[x] = true
    set HousePK_Actions[p] = HousePK_Actions[p]+1
    set HousePK_Turn[p] = 1-seat
    if HousePK_Paid[x] == HousePK_Paid[y] and HousePK_Acted[x] and HousePK_Acted[y] then
        call HousePK_Advance(p)
    elseif HousePK_Paid[x] == HousePK_Paid[y] and (HousePK_Stack[x] == 0 or HousePK_Stack[y] == 0) then
        call HousePK_Showdown(p)
    endif
    set HousePK_Clock[p] = 30
    set HousePK_Wait[p] = 2
endfunction

function HousePK_Texture takes integer p, string name, real x, real y, real w, real h returns framehandle
    local framehandle f = BlzCreateFrameByType("BACKDROP","PokerArtwork",HousePK_Dialog[p],"",p)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,HousePK_Dialog[p],FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetTexture(f,"PokerUI\\"+name+".blp",0,true)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function HousePK_Label takes integer p, real x, real y, real w, real h, real scale returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","PokerLabel",HousePK_Dialog[p],"",p)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,HousePK_Dialog[p],FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetFont(f,"CasinoUI\\Bold.ttf",0.0115*scale,0)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function HousePK_Render takes integer p returns nothing
    local integer x = p*2
    local integer b = p*9
    local integer i = 0
    local integer due = IMaxBJ(0,HousePK_Paid[x+1]-HousePK_Paid[x])
    local integer top = IMaxBJ(HousePK_Paid[x],HousePK_Paid[x+1])
    local integer pot = HousePK_Total[x]+HousePK_Total[x+1]
    local string phase = "PREFLOP"
    local string label = "Check"
    local string path = ""
    local boolean raiseOK = false
    local integer callTone = 0
    if HousePK_Street[p] == 1 then
        set phase = "FLOP"
    elseif HousePK_Street[p] == 2 then
        set phase = "TURN"
    elseif HousePK_Street[p] == 3 then
        set phase = "RIVER"
    endif
    if HousePK_Hand[p] > 0 then
        call BlzFrameSetText(HousePK_Title[p],"POKER|n"+phase+" / #"+CUI_Value(I2S(HousePK_Hand[p])))
    else
        call BlzFrameSetText(HousePK_Title[p],"POKER")
    endif
    call BlzFrameSetText(HousePK_HumanLabel[p],"YOU")
    call BlzFrameSetText(HousePK_BotLabel[p],NS_Name(NS_Dealt[p]))
    if HousePK_Hand[p] == 0 then
        call BlzFrameSetText(HousePK_BotLabel[p],NS_Name(NS_Selected[p]))
    endif
    call CUI_Text(NS_Selector[p],"Opponent > "+NS_Name(NS_Selected[p]))
    call BlzFrameSetVisible(NS_Selector[p],HousePK_Turn[p] == -1 and not CAS_ended)
    call BlzFrameSetText(HousePK_HumanStack[p],CUI_Value(I2S(HousePK_Stack[x])))
    call BlzFrameSetText(HousePK_BotStack[p],CUI_Value(I2S(HousePK_Stack[x+1])))
    call BlzFrameSetText(HousePK_PotLabel[p],"POT  "+CUI_Value(I2S(pot)))
    if HousePK_Note[p] == "Blinds 1/2. Raise button adds one minimum raise." then
        call BlzFrameSetText(HousePK_Text[p],"BLINDS 1/2 / MAX BUY-IN 300g")
    else
        call BlzFrameSetText(HousePK_Text[p],HousePK_Note[p])
    endif
    call BlzFrameSetVisible(HousePK_CallLabel[p],HousePK_Turn[p] == 0)
    call BlzFrameSetText(HousePK_CallLabel[p],"TO CALL  "+CUI_Value(I2S(due)))
    call PK_ChipArt(HousePK_HumanChips[p],HousePK_Stack[x])
    call PK_ChipArt(HousePK_BotChips[p],HousePK_Stack[x+1])
    call PK_ChipArt(HousePK_PotChips[p],pot)
    call BlzFrameSetVisible(HousePK_HumanDealer[p],HousePK_Hand[p] > 0 and HousePK_Dealer[p] == 0)
    call BlzFrameSetVisible(HousePK_BotDealer[p],HousePK_Hand[p] > 0 and HousePK_Dealer[p] == 1)
    loop
        exitwhen i >= 9
        if HousePK_Hand[p] == 0 then
            set path = "empty"
        elseif i < 2 then
            set path = "card"+I2S(HousePK_Cards[b+i])
        elseif i < 4 then
            set path = "back"
            if HousePK_Reveal[p] then
                set path = "card"+I2S(HousePK_Cards[b+i])
            endif
        else
            set path = "empty"
            if i-4 < HousePK_BoardCount(p) then
                set path = "card"+I2S(HousePK_Cards[b+i])
            endif
        endif
        call BlzFrameSetTexture(HousePK_Face[b+i],"PokerUI\\"+path+".blp",0,true)
        set i = i+1
    endloop
    if HousePK_Turn[p] == 0 then
        call BlzFrameSetText(HousePK_Status[p],"YOUR TURN / "+CUI_Value(I2S(HousePK_Clock[p])+"s"))
            if due > 0 then
            set label = "Call "+I2S(due)
            set callTone = 3
        endif
            call CUI_Text(HousePK_Call[p],label)
        if HousePK_Limit(p,0) > top and (not HousePK_Acted[x] or due >= HousePK_LastRaise[p]) then
                    set raiseOK = true
            call CUI_Text(HousePK_Raise[p],"Raise "+I2S(IMinBJ(top+HousePK_LastRaise[p],HousePK_Limit(p,0))))
                    call CUI_Text(HousePK_Allin[p],"All-in "+I2S(HousePK_Limit(p,0)))
        endif
    elseif HousePK_Turn[p] == 1 then
        call BlzFrameSetText(HousePK_Status[p],"BOT'S TURN")
    else
        call BlzFrameSetText(HousePK_Status[p],"NEXT HAND")
        endif
    call CUI_Paint(HousePK_Fold[p],1,HousePK_Turn[p] == 0)
    call CUI_Paint(HousePK_Call[p],callTone,HousePK_Turn[p] == 0)
    call CUI_Paint(HousePK_Raise[p],2,raiseOK)
    call CUI_Paint(HousePK_Allin[p],2,raiseOK)
    call BlzFrameSetVisible(HouseLower[p],HousePK_Turn[p] == -1 and not CAS_ended)
    call BlzFrameSetVisible(HouseHigher[p],HousePK_Turn[p] == -1 and not CAS_ended)
    call CUI_Paint(HouseLower[p],0,HouseStake[p] > 10)
    call CUI_Paint(HouseHigher[p],0,HouseStake[p] < 300)
    call CUI_Text(HousePK_Next[p],"Buy in "+I2S(HouseStake[p])+"g")
    if HousePK_Turn[p] == -1 and not CAS_ended then
        call BlzFrameSetText(HousePK_HumanStack[p],CUI_Value(I2S(CAS_gold[p+1])+"g"))
        call BlzFrameSetText(HousePK_HumanLabel[p],"WALLET")
        if not CAS_ready[p+1] then
            call BlzFrameSetText(HousePK_Text[p],"Waiting for your wallet to load.")
        elseif CAS_gold[p+1] < HouseStake[p] then
            call BlzFrameSetText(HousePK_Text[p],"Your wallet needs "+I2S(HouseStake[p]-CAS_gold[p+1])+"g more for this buy-in.")
        endif
    endif
    call CUI_Paint(HousePK_Next[p],4,HousePK_Turn[p] == -1 and not CAS_ended and CAS_ready[p+1] and CAS_gold[p+1] >= HouseStake[p])
    call CUI_Paint(HousePK_Hide[p],0,true)
    if GetLocalPlayer() == Player(p) then
        call BlzFrameSetVisible(HousePK_Dialog[p],not HousePK_Hidden[p])
    endif
endfunction

function NS_Equity takes integer n, integer bucket returns integer
    local string row
    if n == 3 then
        set row = "027043041054037037037037037037037037037037037037031051045063060066066076073081072082059059059059077077077077070076071071078085082082077077077077037058048048092096092092093093093093088088088088090090089091090090090090090090090090090090090090093095094096094094094094094094094094094094094094097097097097093095094094097099098098097097097097100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100"
    elseif n == 4 then
        set row = "018034028042030030030030030030030030030030030030023045032051057063061067073080075081052052052052028056034056068072066078078084073084072072072072030053036056092093092096091093094092082082082082089082089089082074081086080079076083088088088088088093088094084096082093080089086084089089089089093093093093090092090090095098096096093093093093081083087087100100100100100100100100098098098098100100100100100100100100100100100100100100100100"
    else
        set row = "011025017017017017017017017017017017004004004004015037026026052059054054072079078078009009009009026056043043066070067067078084083083021030022022020048034034091093091091088092091091016024018018091091091091086087086086086087087087042041043043086092089089084094087087084090089089038035039039090090090090090091090090096097097097044044046046052073071071100100099099097100098098046059063063100100099099099099098098097097097097075084085085"
    endif
    return S2I(SubString(row,bucket*3,bucket*3+3))
endfunction

function NS_Preflop takes integer first, integer second returns integer
    local integer a = ModuloInteger(first,13)+2
    local integer b = ModuloInteger(second,13)+2
    local integer value = (a+b-10)*100/24
    if a == b then
        return 48+(a-2)*43/10
    endif
    if first/13 == second/13 then
        set value = value+7
    endif
    if IAbsBJ(a-b) == 1 then
        set value = value+4
    endif
    if a == 14 or b == 14 then
        set value = value+4
    endif
    return IMinBJ(96,value)
endfunction

function NS_Postflop takes integer p, integer n returns integer
    local integer base = p*9
    local integer first = HousePK_Cards[base+2]
    local integer second = HousePK_Cards[base+3]
    local integer a = ModuloInteger(first,13)+2
    local integer b = ModuloInteger(second,13)+2
    local integer top = 0
    local integer matched = 0
    local integer pairGroup = 0
    local integer suitA = 1
    local integer suitB = 1
    local integer i = 1
    local integer j
    local integer card
    local integer r
    local integer boardIn
    local integer allInWindow
    local integer draw = 0
    local integer high = 0
    local integer score = HousePK_Score(p,1,n)
    loop
        exitwhen i > 14
        set NS_BoardRank[i] = false
        set i = i+1
    endloop
    if first/13 == second/13 then
        set suitA = 2
        set suitB = 2
    endif
    set i = 0
    loop
        exitwhen i >= n
        set card = HousePK_Cards[base+4+i]
        set r = ModuloInteger(card,13)+2
        set top = IMaxBJ(top,r)
        set NS_BoardRank[r] = true
        if card/13 == first/13 then
            set suitA = suitA+1
        endif
        if card/13 == second/13 then
            set suitB = suitB+1
        endif
        set i = i+1
    endloop
    if a == b or NS_BoardRank[a] then
        set matched = a
    endif
    if NS_BoardRank[b] then
        set matched = IMaxBJ(matched,b)
    endif
    if matched >= top then
        set pairGroup = 2
    elseif matched > 0 then
        set pairGroup = 1
    endif
    if n == 5 then
        if score == PK_Score5(HousePK_Cards[base+4],HousePK_Cards[base+5],HousePK_Cards[base+6],HousePK_Cards[base+7],HousePK_Cards[base+8]) then
            set pairGroup = 3
        endif
    elseif suitA == 4 or suitB == 4 then
        set draw = 1
    else
        set i = 1
        loop
            exitwhen i > 10 or draw == 1
            set j = i
            set boardIn = 0
            set allInWindow = 0
            loop
                exitwhen j >= i+5
                set r = j
                if j == 1 then
                    set r = 14
                endif
                if NS_BoardRank[r] then
                    set boardIn = boardIn+1
                    set allInWindow = allInWindow+1
                elseif a == r or b == r then
                    set allInWindow = allInWindow+1
                endif
                set j = j+1
            endloop
            if allInWindow == 4 and boardIn < 4 then
                set draw = 1
            endif
            set i = i+1
        endloop
    endif
    if IMaxBJ(a,b) >= 12 then
        set high = 1
    endif
    return NS_Equity(n,(score/759375)*16+pairGroup*4+draw*2+high)
endfunction

function NS_Move takes integer p, integer due, integer pot, integer blind, integer roll returns integer
    local integer id = NS_Dealt[p]
    local integer n = HousePK_BoardCount(p)
    local integer price = 100*due/IMaxBJ(1,pot+due)
    local integer value
    local integer pressure
    local integer defend
    local integer caution = 0
    local integer first = HousePK_Cards[p*9+2]
    local integer second = HousePK_Cards[p*9+3]
    if n == 0 then
        set value = NS_Preflop(first,second)
        if HousePK_Dealer[p] == 1 then
            set value = value+5
        endif
        set pressure = IMinBJ(88,IMaxBJ(0,(value-25)*2))
        set defend = 19+price/2
        if due > blind then
            set pressure = IMaxBJ(0,value-53)
            set defend = 25+price/2+IMinBJ(28,2*due/blind)
        endif
    else
        set value = NS_Postflop(p,n)
        set defend = price+6
        // A large bet represents a stronger range than a random pair of cards.
        if due > 0 then
            set defend = defend+price/3
        endif
        set pressure = IMinBJ(91,IMaxBJ(3,(value-39)*2))
        if due > 0 then
            set pressure = IMaxBJ(2,(value-56)*2)
        endif
    endif
    if id == 0 then
        // Maya flats more, including with some hands strong enough to reraise.
        set pressure = pressure-9
        set defend = defend-3
    elseif id == 1 then
        // Elise gives up marginal bluff catchers, particularly on the river.
        set caution = 3
        if n == 5 then
            set caution = 9
        endif
        set defend = defend+caution
    elseif id == 2 then
        // Alex pushes early edges and removes some speculative river bluffs.
        if n < 4 then
            set pressure = pressure+8
        elseif n == 5 and value < 50 then
            set pressure = 0
        endif
    elseif id == 3 then
        // Miles checks some big hands and rarely fires an empty bluff.
        if value >= 65 then
            set pressure = pressure-16
        elseif value < 45 then
            set pressure = 1
        endif
        set defend = defend-2
    else
        // Ethan's easier heads-up adaptation opens wide and overdefends small bets.
        if n == 0 then
            set pressure = pressure+17
            set defend = defend-13
        elseif price <= 28 then
            set defend = defend-10
        endif
    endif
    if due > 0 and value < defend and roll >= IMaxBJ(0,18-3*(defend-value)) then
        return 0
    endif
    if roll < pressure then
        return 2
    endif
    return 1
endfunction

function HousePK_Bot takes integer p returns nothing
    local integer x = p*2+1
    local integer top = IMaxBJ(HousePK_Paid[x],HousePK_Paid[x-1])
    local integer due = IMinBJ(HousePK_Stack[x],top-HousePK_Paid[x])
    local integer pot = HousePK_Total[x]+HousePK_Total[x-1]
    local integer move = NS_Move(p,due,pot,2,HousePK_Random(100))
    if move == 2 and (HousePK_Actions[p] >= 4 or HousePK_Stack[x] <= due or HousePK_Stack[x-1] <= 0 or (HousePK_Acted[x] and due < HousePK_LastRaise[p])) then
        set move = 1
    endif
    call HousePK_Action(p,1,move)
endfunction

function HousePK_Click takes nothing returns nothing
    local integer p = GetPlayerId(GetTriggerPlayer())
    local framehandle clicked = BlzGetTriggerFrame()
    if not PK_Eligible(p) then
        return
    endif
    if clicked == HousePK_Hide[p] then
        set HousePK_Hidden[p] = true
    elseif clicked == HouseLower[p] and HousePK_Turn[p] == -1 then
        set HouseStake[p] = IMaxBJ(10,HouseStake[p]-10)
    elseif clicked == HouseHigher[p] and HousePK_Turn[p] == -1 then
        set HouseStake[p] = IMinBJ(300,HouseStake[p]+10)
    elseif clicked == NS_Selector[p] and HousePK_Turn[p] == -1 and not CAS_ended then
        set NS_Selected[p] = ModuloInteger(NS_Selected[p]+1,5)
    elseif clicked == HousePK_Next[p] and HousePK_Turn[p] == -1 then
        call HousePK_Deal(p)
    elseif clicked == HousePK_Fold[p] then
        call HousePK_Action(p,0,0)
    elseif clicked == HousePK_Call[p] then
        call HousePK_Action(p,0,1)
    elseif clicked == HousePK_Raise[p] then
        call HousePK_Action(p,0,2)
    elseif clicked == HousePK_Allin[p] then
        call HousePK_Action(p,0,3)
    endif
    call HousePK_Render(p)
    set clicked = null
endfunction

function HousePK_Refund takes integer p returns nothing
    if HousePokerBuyIn[p] > 0 then
        call CAS_Settle(0,p+1,HousePokerBuyIn[p],HousePokerBuyIn[p],HousePokerBuyIn[p])
        set HousePokerBuyIn[p] = 0
        set HousePK_Turn[p] = -1
    endif
endfunction

function HousePK_Tick takes nothing returns nothing
    local integer p = 0
    loop
        exitwhen p >= 24
        if HousePK_Started[p] then
            if not PK_Eligible(p) then
                // Cash out the practice table before any return to active play.
                if HousePK_Turn[p] >= 0 then
                    set HousePK_Stack[p*2] = HousePK_Stack[p*2]+HousePK_Total[p*2]
                    set HousePK_Stack[p*2+1] = HousePK_Stack[p*2+1]+HousePK_Total[p*2+1]
                    set HousePK_Total[p*2] = 0
                    set HousePK_Total[p*2+1] = 0
                    set HousePK_Turn[p] = -1
                endif
                call HousePK_Refund(p)
                call BlzFrameSetVisible(HousePK_Dialog[p],false)
            elseif HousePK_Turn[p] == 1 then
                set HousePK_Wait[p] = HousePK_Wait[p]-1
                if HousePK_Wait[p] <= 0 then
                    call HousePK_Bot(p)
                    call HousePK_Render(p)
                endif
            elseif HousePK_Turn[p] == 0 then
                set HousePK_Clock[p] = HousePK_Clock[p]-1
                if HousePK_Clock[p] <= 0 then
                    if HousePK_Paid[p*2] >= HousePK_Paid[p*2+1] then
                        call HousePK_Action(p,0,1)
                    else
                        call HousePK_Action(p,0,0)
                    endif
                endif
                call HousePK_Render(p)
            elseif not HousePK_Hidden[p] then
                call HousePK_Render(p)
            endif
        endif
        set p = p+1
    endloop
endfunction

function HousePK_Button takes integer p, trigger t, real x, real y, real width, string label returns framehandle
    local framehandle f = CUI_Create(HousePK_Dialog[p],p,x,y,width,0.029,label,0)
    call BlzTriggerRegisterFrameEvent(t,f,FRAMEEVENT_CONTROL_CLICK)
    return f
endfunction

function HousePK_Start takes integer p returns nothing
    local integer i = 0
    local trigger click = null
    if not HousePK_Started[p] then
        set HousePK_Hidden[p] = true
        set HousePK_Started[p] = true
        set HousePK_Stack[p*2] = 0
        set HousePK_Stack[p*2+1] = 0
        set HousePK_Dialog[p] = BlzCreateFrameByType("BACKDROP","PokerTable",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),"",p)
        call BlzFrameSetSize(HousePK_Dialog[p],0.70,0.48)
        call BlzFrameSetAbsPoint(HousePK_Dialog[p],FRAMEPOINT_TOPLEFT,0.05,0.57)
        call BlzFrameSetTexture(HousePK_Dialog[p],"PokerUI\\table.blp",0,true)
        call BlzFrameSetLevel(HousePK_Dialog[p],50)
        call BlzFrameSetVisible(HousePK_Dialog[p],false)
        set HousePK_Title[p] = HousePK_Label(p,0.025,0.014,0.49,0.040,1.12)
        set HousePK_BotLabel[p] = HousePK_Label(p,0.035,0.087,0.215,0.022,0.91)
        set HousePK_BotStack[p] = HousePK_Label(p,0.105,0.109,0.085,0.032,1.48)
        set HousePK_HumanLabel[p] = HousePK_Label(p,0.105,0.314,0.085,0.017,0.91)
        set HousePK_HumanStack[p] = HousePK_Label(p,0.105,0.333,0.085,0.032,1.48)
        set HousePK_PotLabel[p] = HousePK_Label(p,0.532,0.205,0.134,0.038,1.24)
        set HousePK_Status[p] = HousePK_Label(p,0.454,0.312,0.215,0.024,1.05)
        set HousePK_CallLabel[p] = HousePK_Label(p,0.454,0.340,0.215,0.032,1.20)
        set HousePK_Text[p] = HousePK_Label(p,0.025,0.398,0.65,0.037,1.0)
        set HousePK_HumanChips[p] = HousePK_Texture(p,"chips4",0.193,0.330,0.048,0.030)
        set HousePK_BotChips[p] = HousePK_Texture(p,"chips4",0.193,0.106,0.048,0.030)
        set HousePK_PotChips[p] = HousePK_Texture(p,"chips1",0.532,0.245,0.050,0.030)
        set HousePK_HumanDealer[p] = HousePK_Texture(p,"dealer",0.247,0.325,0.022,0.022)
        set HousePK_BotDealer[p] = HousePK_Texture(p,"dealer",0.247,0.113,0.022,0.022)
        set HousePK_Face[p*9] = HousePK_Texture(p,"empty",0.286,0.293,0.060,0.086)
        set HousePK_Face[p*9+1] = HousePK_Texture(p,"empty",0.354,0.293,0.060,0.086)
        set HousePK_Face[p*9+2] = HousePK_Texture(p,"back",0.286,0.081,0.060,0.086)
        set HousePK_Face[p*9+3] = HousePK_Texture(p,"back",0.354,0.081,0.060,0.086)
        set i = 0
        loop
            exitwhen i >= 5
            set HousePK_Face[p*9+4+i] = HousePK_Texture(p,"empty",0.184+I2R(i)*0.068,0.193,0.060,0.086)
            set i = i+1
        endloop
        set click = CreateTrigger()
        set HousePK_Fold[p] = HousePK_Button(p,click,0.025,-0.439,0.105,"Fold")
        set HousePK_Call[p] = HousePK_Button(p,click,0.135,-0.439,0.12,"Check / Call")
        set HousePK_Raise[p] = HousePK_Button(p,click,0.26,-0.439,0.12,"Raise")
        set HousePK_Allin[p] = HousePK_Button(p,click,0.385,-0.439,0.13,"All-in")
        set HousePK_Next[p] = HousePK_Button(p,click,0.52,-0.439,0.155,"Next hand")
        set NS_Selector[p] = HousePK_Button(p,click,0.307,-0.018,0.248,"Choose opponent")
        set HouseStake[p] = 100
        set HouseLower[p] = HousePK_Button(p,click,0.454,-0.107,0.104,"-10g")
        set HouseHigher[p] = HousePK_Button(p,click,0.563,-0.107,0.112,"+10g")
        set HousePK_Hide[p] = HousePK_Button(p,click,0.565,-0.018,0.11,"Hide table")
        call TriggerAddAction(click,function HousePK_Click)
        set HousePK_Turn[p] = -1
        set HousePK_Note[p] = "Choose 10-300g, then click Buy in to deal. Blinds 1/2."
    endif
    set HousePK_Hidden[p] = false
    call HousePK_Render(p)
    set click = null
endfunction

function BJ_CardSum takes integer groupId, integer count, boolean dealer returns integer
    local integer i = 0
    local integer aces = 0
    local integer total = 0
    local integer value
    loop
        exitwhen i >= count
        if dealer then
            set value = BJ_Value(BJ_dealerCard[groupId*22+i])
        else
            set value = BJ_Value(BJ_card[groupId*22+i])
        endif
        set total = total+value
        if value == 11 then
            set aces = aces+1
        endif
        set i = i+1
    endloop
    loop
        exitwhen total <= 21 or aces == 0
        set total = total-10
        set aces = aces-1
    endloop
    return total
endfunction

function BJ_Recount takes integer h returns nothing
    set BJ_total[h] = BJ_CardSum(h,BJ_count[h],false)
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
    local integer count = BJ_dealerCount[t]
    local integer before = BJ_CardSum(t,count,true)
    set BJ_dealerTotal[t] = before
    if count >= 2 and before >= 17 then
        return
    endif
    set BJ_dealerCard[t*22+count] = BJ_Draw(t)
    set BJ_dealerCount[t] = count+1
    set BJ_dealerTotal[t] = BJ_CardSum(t,count+1,true)
    if count >= 2 then
        set BJ_dealerAction[t] = "Hit on "+I2S(before)+"  /  now "+I2S(BJ_dealerTotal[t])
    endif
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
                call CAS_Settle(1,s,stake,payout,BJ_reserve[h])
                call CAS_ResultSound(s,payout-stake)
                if refund then
                    set BJ_result[h] = "Round void / returned "+I2S(payout)
                elseif payout == stake then
                    set BJ_result[h] = "Push / returned "+I2S(payout)
                elseif payout > stake then
                    set BJ_result[h] = "Won +"+I2S(payout-stake)+" / return "+I2S(payout)
                else
                    set BJ_result[h] = "Lost "+I2S(stake)
                endif
                if ModuloInteger(h,2) == 1 then
                    set CAS_note[s] = "Hand 1: "+BJ_result[h-1]+"  /  Hand 2: "+BJ_result[h]
                else
                    set CAS_note[s] = BJ_result[h]
                endif
            endif
        endif
        set h = h+1
    endloop
    set BJ_reveal[t] = true
    set BJ_phase[t] = 4
    set BJ_clock[t] = 5
    set BJ_turn[t] = 0
endfunction

function BJ_Next takes integer t returns nothing
    local integer h = t*12
    local boolean compare = false
    if BJ_error[t] then
        call BJ_Finish(t,true)
        return
    endif
    loop
        exitwhen h >= t*12+12
        if BJ_state[h] == 2 and BJ_bet[h] > 0 then
            set compare = true
        endif
        if BJ_state[h] == 1 then
            set BJ_turn[t] = h+1
            set BJ_clock[t] = 20
            return
        endif
        set h = h+1
    endloop
    set BJ_turn[t] = 0
    if not compare then
        set BJ_dealerAction[t] = "No hands left to compare"
        call BJ_Finish(t,false)
        return
    endif
    set BJ_dealerAction[t] = "Hole card revealed"
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
    set BJ_dealerAction[t] = ""
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
        set BJ_dealerAction[t] = "Blackjack"
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

function BJWatchActive takes integer host returns boolean
    return host > 0 and PK_Eligible(host-1) and not CAS_ended and BJ_phase[host] >= 1 and (BJ_phase[host] <= 3 or (BJ_phase[host] == 4 and BJ_clock[host] > 0))
endfunction

function BJWatchRecord takes integer host, string action returns nothing
    set BJWatchOlder[host] = BJWatchPrevious[host]
    set BJWatchPrevious[host] = BJWatchLast[host]
    set BJWatchLast[host] = action
endfunction

function BJWatchAction takes integer s, integer hand, integer action returns nothing
    local string detail
    if action == 1 then
        set detail = "Hit"
    elseif action == 2 then
        set detail = "Stand"
    elseif action == 3 then
        set detail = "Double"
    else
        set detail = "Split"
    endif
    if BJ_split[hand] and action != 4 then
        set detail = detail+" (hand "+I2S(ModuloInteger(hand,2)+1)+")"
    endif
    call BJWatchRecord(s,detail)
endfunction

function BJ_Action takes integer s, integer action returns nothing
    local integer t = BJ_table[s]
    local integer h = BJ_turn[t]-1
    local integer stake
    local integer card
    if not PK_Eligible(s-1) or BJ_phase[t] != 2 or h < 0 or BJ_owner[h/2] != s or BJ_state[h] != 1 then
        return
    endif
    if action == 1 then
        call BJ_Hit(t,h)
        set BJ_clock[t] = 20
        set CAS_note[s] = "Hit  /  drew "+PK_Card(BJ_card[h*22+BJ_count[h]-1])+"  /  total "+I2S(BJ_total[h])
    elseif action == 2 then
        set CAS_note[s] = "Standing on "+I2S(BJ_total[h])
        set BJ_state[h] = 2
    elseif action == 3 then
        if BJ_count[h] != 2 or BJ_bet[h] > 10000 or (BJ_split[h] and ModuloInteger(BJ_card[h*22],13) == 12) then
            return
        endif
        set stake = BJ_bet[h]
        if not CAS_Reserve(1,s,stake,stake*3/2) then
            return
        endif
        set CAS_note[s] = "Doubled  /  wager now "+I2S(stake*2)+"g"
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
        if not CAS_Reserve(1,s,stake,stake*3/2) then
            return
        endif
        set CAS_note[s] = "Split  /  "+I2S(stake)+"g on each hand"
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
    call BJWatchAction(s,h,action)
    if BJ_error[t] then
        call BJ_Finish(t,true)
    elseif BJ_state[h] != 1 then
        call BJ_Next(t)
    endif
endfunction

function BJ_Tick takes nothing returns nothing
    local integer t = 1
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
            elseif BJ_clock[t] <= 0 or not PK_Eligible(s-1) then
                call BJWatchRecord(s,"Auto-stand")
                set BJ_state[h] = 2
                call BJ_Next(t)
            endif
        elseif BJ_phase[t] == 3 then
            set BJ_clock[t] = BJ_clock[t]-1
            if BJ_clock[t] <= 0 then
                if BJ_CardSum(t,BJ_dealerCount[t],true) < 17 then
                    call BJ_DealerHit(t)
                    set BJ_clock[t] = 1
                    if BJ_error[t] then
                        call BJ_Finish(t,true)
                    endif
                else
                    if BJ_dealerTotal[t] > 21 then
                        set BJ_dealerAction[t] = "Bust on "+I2S(BJ_dealerTotal[t])
                    else
                        set BJ_dealerAction[t] = "Stands on "+I2S(BJ_dealerTotal[t])
                    endif
                    call BJ_Finish(t,false)
                endif
            endif
        elseif BJ_phase[t] == 4 then
            set BJ_clock[t] = IMaxBJ(0,BJ_clock[t]-1)
        endif
        set t = t+1
    endloop
endfunction

function BJ_Summary takes integer h returns string
    local string text = I2S(BJ_total[h])
    if BJ_total[h] > 21 then
        return "|cffff9090BUST "+text+"|r"
    elseif BJ_state[h] == 4 then
        return "|cffe7cb88BLACKJACK 21|r"
    elseif BJ_state[h] == 1 then
        return CUI_Value(text)
    elseif BJ_state[h] == 0 then
        return "--"
    endif
    return CUI_Value(text)
endfunction

function BJ_SeatTotal takes integer hand returns string
    if BJ_state[hand] == 0 then
        return "--"
    elseif BJ_total[hand] > 21 then
        return "|cffff9090"+I2S(BJ_total[hand])+"|r"
    endif
    return CUI_Value(I2S(BJ_total[hand]))
endfunction

function AR_CanPlay takes integer s returns boolean
    if not PK_Eligible(s-1) then
        return false
    endif
    return GetPlayerController(Player(s-1)) == MAP_CONTROL_USER and not IsPlayerObserver(Player(s-1))
endfunction

function AR_Next takes integer s, integer fromSlot returns integer
    local integer i = 0
    loop
        exitwhen i >= 24
        set fromSlot = ModuloInteger(fromSlot,24)+1
        if fromSlot != s and AR_CanPlay(fromSlot) then
            return fromSlot
        endif
        set i = i+1
    endloop
    return 0
endfunction

function AR_Tell takes integer s, string msg returns nothing
    set CAS_note[s] = msg
    call DisplayTimedTextToPlayer(Player(s-1),0,0,12,msg)
endfunction

function AR_Target takes integer s returns integer
    if AR_pick[s] != s and AR_CanPlay(AR_pick[s]) then
        return AR_pick[s]
    endif
    return AR_Next(s,0)
endfunction

function AR_SelectedStake takes integer s returns integer
    return IMaxBJ(10,IMinBJ(10000,CAS_amount[s])/2*2)
endfunction

function AR_Terms takes integer stake returns string
    if stake == 0 then
        return "Free duel"
    endif
    return I2S(stake)+"g each  /  "+I2S(stake*2)+"g pot"
endfunction

function AR_CanFund takes integer s, integer stake returns boolean
    return CAS_ready[s] and CAS_gold[s] >= stake
endfunction

function AR_Invite takes integer s, integer stake returns nothing
    local integer other = AR_Target(s)
    if AR_state != 0 or CAS_ended or not AR_CanPlay(s) or not AR_CanPlay(other) or s == other then
        call AR_Tell(s,"Choose an available player when the arena is free.")
        return
    endif
    if stake != 0 and (stake != AR_SelectedStake(s) or not AR_CanFund(s,stake)) then
        call AR_Tell(s,"Your Wallet must cover the selected stake.")
        return
    endif
    set AR_offer = AR_offer+1
    set AR_stake = stake
    set AR_seat[0] = s
    set AR_seat[1] = other
    set AR_state = 1
    set AR_until = R2I(TimerGetElapsed(FF_gameTimer))+30
    call AR_Tell(s,"Arena invitation sent to "+CAS_Name(other)+". "+AR_Terms(stake)+".")
    call AR_Tell(other,CAS_Name(s)+" invites you to the arena. "+AR_Terms(stake)+". Type -arena and click Accept within 30 seconds.")
endfunction

function AR_EmptyOwner takes player p, player exclude, group scratch returns boolean
    if p == exclude then
        return false
    endif
    call GroupEnumUnitsOfPlayer(scratch,p,null)
    return FirstOfGroup(scratch) == null
endfunction

function AR_FindOwner takes player exclude returns player
    local group g = CreateGroup()
    local player p = Player(bj_PLAYER_NEUTRAL_EXTRA)
    local integer i = 12
    if not AR_EmptyOwner(p,exclude,g) then
        set p = Player(bj_PLAYER_NEUTRAL_VICTIM)
        if not AR_EmptyOwner(p,exclude,g) then
            set p = null
            loop
                exitwhen i >= 24 or p != null
                if GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_EMPTY and AR_EmptyOwner(Player(i),exclude,g) then
                    set p = Player(i)
                endif
                set i = i+1
            endloop
        endif
    endif
    call DestroyGroup(g)
    set g = null
    return p
endfunction

function AR_Flag takes player a, player b, alliancetype flag, boolean value returns nothing
    if GetPlayerAlliance(a,b,flag) != value then
        set AR_flagFrom[AR_flagCount] = a
        set AR_flagTo[AR_flagCount] = b
        set AR_flagType[AR_flagCount] = flag
        set AR_flagBefore[AR_flagCount] = not value
        set AR_flagCount = AR_flagCount+1
        call SetPlayerAlliance(a,b,flag,value)
    endif
endfunction

function AR_Control takes integer side returns nothing
    local player p = AR_owner[side]
    local player human = Player(AR_seat[side]-1)
    local integer i = 0
    loop
        exitwhen i >= 24
        if Player(i) != p and Player(i) != AR_owner[1-side] then
            call AR_Flag(p,Player(i),ALLIANCE_PASSIVE,i != AR_seat[1-side]-1)
            call AR_Flag(Player(i),p,ALLIANCE_PASSIVE,i != AR_seat[1-side]-1)
            call AR_Flag(p,Player(i),ALLIANCE_SHARED_CONTROL,Player(i) == human)
            call AR_Flag(p,Player(i),ALLIANCE_SHARED_ADVANCED_CONTROL,Player(i) == human)
            call AR_Flag(p,Player(i),ALLIANCE_SHARED_XP,false)
        endif
        set i = i+1
    endloop
    call AR_Flag(p,AR_owner[1-side],ALLIANCE_PASSIVE,false)
    call AR_Flag(p,human,ALLIANCE_SHARED_VISION,true)
endfunction

function AR_EnterCamera takes integer side returns nothing
    local integer s = AR_seat[side]
    local player p = Player(s-1)
    set AR_vision[side] = CreateFogModifierRect(p,FOG_OF_WAR_VISIBLE,AR_floor,false,false)
    call FogModifierStart(AR_vision[side])
    set CAS_view[s] = 0
    set PK_Hidden[s-1] = true
    set HousePK_Hidden[s-1] = true
    if GetLocalPlayer() == Player(s-1) and HousePK_Dialog[s-1] != null then
        call BlzFrameSetVisible(HousePK_Dialog[s-1],false)
    endif
    if GetLocalPlayer() == p then
        set AR_oldLeft = GetCameraBoundMinX()
        set AR_oldBottom = GetCameraBoundMinY()
        set AR_oldRight = GetCameraBoundMaxX()
        set AR_oldTop = GetCameraBoundMaxY()
        set AR_oldX = GetCameraTargetPositionX()
        set AR_oldY = GetCameraTargetPositionY()
        set AR_oldZoom = GetCameraField(CAMERA_FIELD_TARGET_DISTANCE)
        call BlzFrameSetVisible(CAS_root[s],false)
        if PK_Dialog[s-1] != null then
            call BlzFrameSetVisible(PK_Dialog[s-1],false)
        endif
        call ResetToGameCamera(0)
        call SetCameraField(CAMERA_FIELD_TARGET_DISTANCE,AR_oldZoom,0)
        call SetCameraBoundsToRect(AR_floor)
        call SetCameraPosition(GetUnitX(AR_hero[side]),GetUnitY(AR_hero[side]))
        call ClearSelection()
        call SelectUnit(AR_hero[side],true)
    endif
endfunction

function AR_End takes integer winner, string message returns nothing
    local integer side = 0
    local integer i = 0
    local integer s
    local boolean fighting = AR_state == 2
    if AR_state == 0 then
        return
    endif
    set AR_state = 0
    call PauseTimer(AR_clock)
    if AR_held[0]+AR_held[1] > 0 then
        if winner != 0 then
            set message = message+" Pot won: "+I2S(AR_held[0]+AR_held[1])+" Wallet gold."
        else
            set message = message+" Reserved gold returned."
        endif
    endif
    if AR_deaths != null then
        call DestroyTrigger(AR_deaths)
        set AR_deaths = null
    endif
    loop
        exitwhen side > 1
        set s = AR_seat[side]
        if AR_held[side] > 0 then
            set CAS_escrow[s] = CAS_escrow[s]-AR_held[side]
            if winner == 0 then
                call CAS_Credit(3,s,AR_held[side],0)
            elseif winner == s then
                call CAS_Credit(3,s,AR_held[side],AR_stake)
                call CAS_ResultSound(s,AR_stake)
            else
                call CAS_ResultSound(s,-AR_held[side])
            endif
            set AR_held[side] = 0
        endif
        if fighting then
            if AR_vision[side] != null then
                call FogModifierStop(AR_vision[side])
                call DestroyFogModifier(AR_vision[side])
                set AR_vision[side] = null
                if GetLocalPlayer() == Player(s-1) then
                    call SetCameraBounds(AR_oldLeft,AR_oldBottom,AR_oldLeft,AR_oldTop,AR_oldRight,AR_oldTop,AR_oldRight,AR_oldBottom)
                    call SetCameraField(CAMERA_FIELD_TARGET_DISTANCE,AR_oldZoom,0)
                    call SetCameraPosition(AR_oldX,AR_oldY)
                    call ClearSelection()
                    if udg_herO[s] != null then
                        call SelectUnit(udg_herO[s],true)
                    endif
                endif
                set FF_oc_followed[s-1] = null
            endif
            if AR_scroll[side] != null then
                call RemoveItem(AR_scroll[side])
                set AR_scroll[side] = null
            endif
            call RemoveUnit(AR_hero[side])
            set AR_hero[side] = null
        endif
        call AR_Tell(s,message)
        set AR_seat[side] = 0
        set AR_owner[side] = null
        set side = side+1
    endloop
    set AR_stake = 0
    if fighting then
        call DisableTrigger(AR_damage)
        call DisableTrigger(AR_orders)
        loop
            exitwhen i >= 80
            call RemoveUnit(AR_foot[i])
            set AR_foot[i] = null
            set i = i+1
        endloop
        loop
            exitwhen AR_flagCount == 0
            set AR_flagCount = AR_flagCount-1
            call SetPlayerAlliance(AR_flagFrom[AR_flagCount],AR_flagTo[AR_flagCount],AR_flagType[AR_flagCount],AR_flagBefore[AR_flagCount])
        endloop
    endif
endfunction

function AR_Withdraw takes integer s returns nothing
    if s != AR_seat[0] and s != AR_seat[1] then
        return
    endif
    if AR_state == 1 then
        call AR_End(0,CAS_Name(s)+" closed the arena invitation.")
    elseif AR_state == 2 then
        if s == AR_seat[0] then
            call AR_End(AR_seat[1],CAS_Name(AR_seat[1])+" wins the duel by forfeit.")
        else
            call AR_End(AR_seat[0],CAS_Name(AR_seat[0])+" wins the duel by forfeit.")
        endif
    endif
endfunction

function AR_Alive takes unit u returns boolean
    return GetUnitTypeId(u) != 0 and GetWidgetLife(u) > 0.405 and not IsUnitType(u,UNIT_TYPE_DEAD)
endfunction

function AR_Contain takes unit u returns nothing
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    if not RectContainsCoords(AR_floor,x,y) and AR_Alive(u) then
        call SetUnitPosition(u,RMaxBJ(-976,RMinBJ(976,x)),RMaxBJ(5424,RMinBJ(6864,y)))
        call IssueImmediateOrder(u,"stop")
    endif
endfunction

function AR_Tick takes nothing returns nothing
    local integer i = 0
    local boolean left
    local boolean right
    if CAS_ended then
        call AR_End(0,"The main match ended. The arena is closed.")
    elseif AR_state == 1 then
        if R2I(TimerGetElapsed(FF_gameTimer)) >= AR_until or not AR_CanPlay(AR_seat[0]) or not AR_CanPlay(AR_seat[1]) then
            call AR_End(0,"Arena invitation expired.")
        endif
    elseif AR_state == 2 then
        set left = AR_Alive(AR_hero[0]) and AR_CanPlay(AR_seat[0])
        set right = AR_Alive(AR_hero[1]) and AR_CanPlay(AR_seat[1])
        if not left and not right then
            call AR_End(0,"Arena duel drawn. Both sides were eliminated.")
        elseif not left then
            call AR_End(AR_seat[1],CAS_Name(AR_seat[1])+" wins the arena duel!")
        elseif not right then
            call AR_End(AR_seat[0],CAS_Name(AR_seat[0])+" wins the arena duel!")
        else
            // Global Silence uses a native map-wide buff in addition to the match spell guard.
            call UnitRemoveAbility(AR_hero[0],'BGs1')
            call UnitRemoveAbility(AR_hero[0],'BGs2')
            call UnitRemoveAbility(AR_hero[1],'BGs1')
            call UnitRemoveAbility(AR_hero[1],'BGs2')
            call AR_Contain(AR_hero[0])
            call AR_Contain(AR_hero[1])
            loop
                exitwhen i >= 80
                call AR_Contain(AR_foot[i])
                set i = i+1
            endloop
        endif
    endif
endfunction

function AR_HeroDied takes nothing returns nothing
    // Let the native death event finish so all match event guards still see the arena owners.
    call TimerStart(AR_clock,0,false,function AR_Tick)
endfunction

function AR_Army takes integer side, integer roll returns boolean
    local integer i = 0
    local integer index
    local real sign = -1
    local real facing = 0
    local unit u
    local player p = AR_owner[side]
    local playercolor color = GetPlayerColor(Player(AR_seat[side]-1))
    if side == 1 then
        set sign = 1
        set facing = 180
    endif
    set u = CreateUnit(p,AR_roster[roll],sign*880,6144,facing)
    set AR_hero[side] = u
    if u == null then
        return false
    endif
    call SetUnitColor(u,color)
    call RemoveGuardPosition(u)
    call SuspendHeroXP(u,true)
    call SelectHeroSkill(u,AR_skill[roll])
    set AR_scroll[side] = CreateItem('sror',GetUnitX(u),GetUnitY(u))
    if AR_scroll[side] == null or not UnitAddItem(u,AR_scroll[side]) then
        set u = null
        return false
    endif
    call SetItemDroppable(AR_scroll[side],false)
    call SetItemPawnable(AR_scroll[side],false)
    call SetItemDropOnDeath(AR_scroll[side],false)
    loop
        exitwhen i >= 40
        set index = side*40+i
        set u = CreateUnit(p,'hfoo',sign*(464+80*(i/8)),6144+80*(ModuloInteger(i,8)-3.5),facing)
        set AR_foot[index] = u
        if u == null then
            return false
        endif
        call SetUnitColor(u,color)
        call SetUnitUseFood(u,false)
        call RemoveGuardPosition(u)
        set i = i+1
    endloop
    set u = null
    return true
endfunction

function AR_Accept takes integer s, integer offer returns nothing
    local integer roll
    local integer i = 0
    if AR_state != 1 or s != AR_seat[1] or offer != AR_offer then
        return
    endif
    call AR_Tick()
    if AR_state != 1 then
        return
    endif
    set AR_owner[0] = AR_FindOwner(null)
    set AR_owner[1] = AR_FindOwner(AR_owner[0])
    if AR_owner[0] == null or AR_owner[1] == null then
        call AR_End(0,"The arena could not reserve two empty army slots.")
        return
    endif
    if AR_stake > 0 then
        if not AR_CanFund(AR_seat[0],AR_stake) then
            call AR_End(0,"Invitation closed. The challenger can no longer cover the stake.")
            return
        endif
        if not AR_CanFund(s,AR_stake) then
            call AR_Tell(s,"You need "+I2S(AR_stake)+" Wallet gold to accept.")
            return
        endif
        if not CAS_Reserve(3,AR_seat[0],AR_stake,0) then
            call AR_End(0,"Invitation closed. The challenger's stake was unavailable.")
            return
        endif
        set AR_held[0] = AR_stake
        if not CAS_Reserve(3,s,AR_stake,0) then
            call AR_End(0,"Invitation closed. The matching stake was unavailable.")
            return
        endif
        set AR_held[1] = AR_stake
    endif
    set AR_state = 2
    call EnableTrigger(AR_damage)
    call EnableTrigger(AR_orders)
    call AR_Control(0)
    call AR_Control(1)
    set roll = GetRandomInt(0,5)
    if not AR_Army(0,roll) or not AR_Army(1,roll) then
        call AR_End(0,"Arena setup failed. The invitation has been cleared.")
        return
    endif
    set AR_deaths = CreateTrigger()
    call TriggerRegisterUnitEvent(AR_deaths,AR_hero[0],EVENT_UNIT_DEATH)
    call TriggerRegisterUnitEvent(AR_deaths,AR_hero[1],EVENT_UNIT_DEATH)
    call TriggerAddAction(AR_deaths,function AR_HeroDied)
    call AR_EnterCamera(0)
    call AR_EnterCamera(1)
    loop
        exitwhen i >= 80
        call IssuePointOrder(AR_foot[i],"attack",GetUnitX(AR_hero[1-i/40]),6144)
        set i = i+1
    endloop
    call AR_Tell(AR_seat[0],"Arena duel! Protect your "+GetUnitName(AR_hero[0])+" and kill the opposing hero.")
    call AR_Tell(AR_seat[1],"Arena duel! Protect your "+GetUnitName(AR_hero[1])+" and kill the opposing hero.")
    call TimerStart(AR_clock,0.125,true,function AR_Tick)
endfunction

function AR_ReceiveAccept takes nothing returns nothing
    call AR_Accept(GetPlayerId(GetTriggerPlayer())+1,S2I(BlzGetTriggerSyncData()))
endfunction

function DU_Cancel takes integer id returns nothing
    local integer s = DU_from[id]
    if DU_state[id] != 1 then
        return
    endif
    set DU_state[id] = 4
    set DU_outgoing[s] = 0
    set DU_incoming[DU_to[id]] = 0
    set CAS_escrow[s] = CAS_escrow[s]-DU_stake[id]
    call CAS_Credit(3,s,DU_stake[id],0)
    set CAS_note[s] = "Challenge declined, cancelled, or expired. Gold returned."
endfunction

function DU_Offer takes integer s returns nothing
    local integer to = DU_opponent[s]
    local integer target = DU_pick[s]
    local integer stake = CAS_amount[s]
    if not PK_Eligible(to-1) or to == s or DU_outgoing[s] != 0 or DU_incoming[to] != 0 or DU_active[s] != 0 or DU_active[to] != 0 or not MK_Valid(5,target) or DU_n >= 511 then
        set CAS_note[s] = "Choose an available opponent and a valid winner. One active challenge per player."
        return
    endif
    if not CAS_Reserve(3,s,stake,0) then
        return
    endif
    set DU_n = DU_n+1
    set DU_from[DU_n] = s
    set DU_to[DU_n] = to
    set DU_target[DU_n] = target
    set DU_ffa[DU_n] = MK_FFA()
    set DU_stake[DU_n] = stake
    set DU_state[DU_n] = 1
    set DU_expire[DU_n] = CAS_seconds+30
    set DU_outgoing[s] = DU_n
    set DU_incoming[to] = DU_n
    set CAS_note[s] = "Challenge sent. Your "+I2S(stake)+" gold is held for 30 seconds."
    set CAS_note[to] = CAS_Name(s)+" challenges you: "+MK_Label(5,target)+" wins, "+I2S(stake)+" gold each. Open Casino / Challenges."
    call DisplayTimedTextToPlayer(Player(to-1),0,0,15,CAS_note[to])
endfunction

function DU_Accept takes integer s returns nothing
    local integer id = DU_incoming[s]
    local integer proposer
    if id == 0 or DU_state[id] != 1 then
        return
    endif
    set proposer = DU_from[id]
    if CAS_seconds >= DU_expire[id] or not PK_Eligible(proposer-1) or DU_active[s] != 0 or DU_active[proposer] != 0 or DU_ffa[id] != MK_FFA() or not MK_Valid(5,DU_target[id]) then
        call DU_Cancel(id)
        return
    endif
    if not CAS_Reserve(3,s,DU_stake[id],0) then
        return
    endif
    set DU_state[id] = 2
    set DU_incoming[s] = 0
    set DU_outgoing[proposer] = 0
    set DU_active[s] = id
    set DU_active[proposer] = id
    set CAS_note[s] = "Accepted: you win if "+MK_Label(5,DU_target[id])+" does NOT win. Pot "+I2S(DU_stake[id]*2)+"."
    set CAS_note[proposer] = "Accepted: you win if "+MK_Label(5,DU_target[id])+" wins. Pot "+I2S(DU_stake[id]*2)+"."
endfunction

function DU_Finish takes integer winner, boolean ffa returns nothing
    local integer id = 1
    local integer won
    local integer stake
    loop
        exitwhen id > DU_n
        if DU_state[id] == 1 then
            call DU_Cancel(id)
        elseif DU_state[id] == 2 then
            set DU_state[id] = 3
            set stake = DU_stake[id]
            set CAS_escrow[DU_from[id]] = CAS_escrow[DU_from[id]]-stake
            set CAS_escrow[DU_to[id]] = CAS_escrow[DU_to[id]]-stake
            set DU_active[DU_from[id]] = 0
            set DU_active[DU_to[id]] = 0
            if winner == 0 or DU_ffa[id] != ffa then
                call CAS_Credit(3,DU_from[id],stake,0)
                call CAS_Credit(3,DU_to[id],stake,0)
            else
                set won = DU_to[id]
                if DU_target[id] == winner then
                    set won = DU_from[id]
                endif
                call CAS_Credit(3,won,stake,stake)
                call CAS_ResultSound(won,stake)
                if won == DU_from[id] then
                    call CAS_ResultSound(DU_to[id],-stake)
                else
                    call CAS_ResultSound(DU_from[id],-stake)
                endif
                set CAS_note[won] = "Challenge won: return "+I2S(stake*2)+" gold."
            endif
        endif
        set id = id+1
    endloop
endfunction

function BJ_CardStart takes real center, integer count, real width, real spacing returns real
    local integer visible = IMaxBJ(2,IMinBJ(6,count))
    return center-(width+I2R(visible-1)*spacing)*0.5
endfunction

function AR_View takes integer s returns nothing
    local integer b = s*32
    local integer target = AR_Target(s)
    local integer stake = AR_SelectedStake(s)
    local boolean canInvite = AR_state == 0 and target != 0 and AR_CanPlay(s) and not CAS_ended
    local string line = "Kill the opposing hero to win.|nEach side gets the same random hero, 40 footmen and one Scroll of the Beast."
    local string status
    if AR_state != 0 then
        set stake = AR_stake
    endif
    if CAS_ended then
        set status = "The arena is closed."
    elseif AR_state == 2 then
        set status = "Fighting: "+CAS_Name(AR_seat[0])+" vs "+CAS_Name(AR_seat[1])
    elseif AR_state == 1 then
        set status = CAS_Name(AR_seat[0])+" invited "+CAS_Name(AR_seat[1])+"  /  "+I2S(IMaxBJ(0,AR_until-CAS_seconds))+"s"
    elseif not AR_CanPlay(s) then
        set status = "A player slot with unit control is required."
    elseif target == 0 then
        set status = "Waiting for another player."
    else
        set status = "Opponent: "+CAS_Name(target)
    endif
    set line = line+"|n|nBoth Wallets pay on acceptance. The winner takes the pot."
    call BlzFrameSetText(CAS_content[b+28],line)
    call BlzFrameSetVisible(CAS_content[b+28],true)
    call BlzFrameSetText(CAS_content[b+29],status)
    call BlzFrameSetVisible(CAS_content[b+29],true)
    call CUI_Text(CAS_button[s*64+39],"Prediction duel")
    call CAS_ShowButton(s,39,true)
    call CAS_ShowButton(s,53,AR_state == 0 and target != 0 and AR_CanPlay(s) and not CAS_ended)
    call CAS_ShowButton(s,54,canInvite)
    call CUI_Text(CAS_button[s*64+19],"Invite for "+I2S(stake)+"g each")
    if AR_state == 0 then
        call CAS_ShowButton(s,19,canInvite and AR_CanFund(s,stake))
    elseif GetLocalPlayer() == Player(s-1) then
        call BlzFrameSetVisible(CAS_button[s*64+19],false)
    endif
    if stake == 0 then
        call CUI_Text(CAS_button[s*64+55],"Accept free duel")
    else
        call CUI_Text(CAS_button[s*64+55],"Accept for "+I2S(stake)+"g")
    endif
    if GetLocalPlayer() == Player(s-1) and AR_state == 1 and s == AR_seat[1] then
        set AR_shownOffer = AR_offer
    endif
    call CAS_ShowButton(s,55,AR_state == 1 and s == AR_seat[1] and not CAS_ended and (stake == 0 or AR_CanFund(s,stake)))
    if AR_state == 2 then
        call CUI_Text(CAS_button[s*64+56],"Forfeit")
    elseif AR_state == 1 and AR_seat[0] == s then
        call CUI_Text(CAS_button[s*64+56],"Cancel")
    else
        call CUI_Text(CAS_button[s*64+56],"Decline")
    endif
    call CAS_ShowButton(s,56,AR_state > 0 and (s == AR_seat[0] or s == AR_seat[1]))
endfunction

function BJWatchList takes integer s returns nothing
    local integer host = 1
    local integer count = 0
    local integer index = 0
    local integer row
    local integer key
    local integer pages
    local integer hand
    local boolean show
    local framehandle eye
    local string name
    loop
        exitwhen host > 24
        if host != s and BJWatchActive(host) then
            set count = count+1
        endif
        set host = host+1
    endloop
    set pages = IMaxBJ(1,(count+3)/4)
    set BJWatchPage[s] = ModuloInteger(BJWatchPage[s],pages)
    set host = 1
    loop
        exitwhen host > 24
        set key = s*25+host
        set eye = BJWatchEye[key]
        if eye != null then
            set show = false
            if BJWatchActive(host) then
                set show = CAS_view[s] == 1 and index/4 == BJWatchPage[s]
                if show then
                    set row = ModuloInteger(index,4)
                    set hand = BJ_seat[host]*2
                    set name = CAS_Name(host)
                    if StringLength(name) > 14 then
                        set name = SubString(name,0,14)+"..."
                    endif
                    call BlzFrameSetText(CAS_row[s*6+row],name+"|n"+CUI_Value(I2S(BJ_bet[hand]+BJ_bet[hand+1])+"g"))
                    call BlzFrameSetVisible(CAS_row[s*6+row],true)
                    call BlzFrameSetPoint(eye,FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,0.159,-0.174-0.039*I2R(row))
                endif
                set index = index+1
            endif
            call BlzFrameSetVisible(eye,show)
        endif
        set host = host+1
    endloop
    call BlzFrameSetVisible(CAS_button[s*64+16],CAS_view[s] == 1 and pages > 1)
    call CUI_Text(CAS_button[s*64+16],"Games "+I2S(BJWatchPage[s]+1)+"/"+I2S(pages)+" >")
    call BlzFrameSetVisible(CAS_button[s*64+61],CAS_view[s] == 1 and BJWatchHost[s] > 0)
    if CAS_view[s] == 1 then
        call BlzFrameSetText(CAS_content[s*32],"LIVE GAMES  "+I2S(count))
        call BlzFrameSetVisible(CAS_content[s*32],true)
        if count == 0 then
            call BlzFrameSetText(CAS_row[s*6],"No other games")
            call BlzFrameSetVisible(CAS_row[s*6],true)
        endif
    endif
    set eye = null
endfunction

function CAS_BlackjackView takes integer s, integer host returns nothing
    local integer t = BJ_table[host]
    local integer h = BJ_seat[host]*2
    local integer b = s*32
    local integer c = s*18
    local integer i = 0
    local integer card
    local real dealerX
    local real handX
    local real splitX = 0.0
    local real cardWidth = 0.060
    local real cardHeight = 0.082
    local real spacing = 0.067
    local boolean turn = BJ_phase[t] == 2 and BJ_turn[t]-1 >= h and BJ_turn[t]-1 <= h+1
    local boolean ownTable = host == s
    local boolean betting = ownTable and not CAS_ended and (BJ_phase[t] == 0 or BJ_phase[t] == 4)
    local string history = BJWatchOlder[host]
    local string phase = "PLACE BET"
    local string dealer = "DEALER"
    local string first = "YOU"
    local string second = "HAND 2"
    if not ownTable then
        set first = SubString(CAS_Name(host),0,16)
    endif
    if BJ_phase[t] == 1 then
        set phase = "DEAL IN "+CUI_Value(I2S(BJ_clock[t])+"s")
    elseif BJ_phase[t] == 2 then
        set phase = CAS_Name(BJ_owner[(BJ_turn[t]-1)/2])+" / "+CUI_Value(I2S(BJ_clock[t])+"s")
        if turn and ownTable then
            set phase = "YOUR TURN / "+CUI_Value(I2S(BJ_clock[t])+"s")
        endif
    elseif BJ_phase[t] == 3 then
        set phase = "DEALER'S TURN"
    elseif BJ_phase[t] == 4 then
        set phase = "NEXT ROUND"
    endif
    call BlzFrameSetText(CAS_content[b+1],phase)
    call BlzFrameSetVisible(CAS_content[b+1],true)
    if BJ_reveal[t] then
        set dealer = dealer+"  "+CUI_Value(I2S(BJ_dealerTotal[t]))+"   /   "+BJ_dealerAction[t]
    elseif BJ_dealerCount[t] > 0 then
        set dealer = dealer+"   /   Shows "+PK_Card(BJ_dealerCard[t*22])+"   /   Hole card down"
    endif
    call BlzFrameSetText(CAS_content[b+2],dealer)
    call BlzFrameSetVisible(CAS_content[b+2],true)
    set dealerX = BJ_CardStart(0.445,BJ_dealerCount[t],0.054,0.067)
    if BJ_split[h] then
        set first = "HAND 1"
        if turn then
            if BJ_turn[t]-1 == h then
                set first = "> HAND 1"
            else
                set second = "> HAND 2"
            endif
        endif
        set cardWidth = 0.043
        set cardHeight = 0.062
        set spacing = 0.028
        set handX = BJ_CardStart(0.330,BJ_count[h],cardWidth,spacing)
        set splitX = BJ_CardStart(0.560,BJ_count[h+1],cardWidth,spacing)
        call BlzFrameSetSize(CAS_content[b+3],0.230,0.040)
        call BlzFrameSetText(CAS_content[b+5],second+"  "+BJ_Summary(h+1)+"  /  "+I2S(BJ_bet[h+1])+"g")
        call BlzFrameSetVisible(CAS_content[b+5],true)
    else
        set handX = BJ_CardStart(0.445,BJ_count[h],cardWidth,spacing)
        call BlzFrameSetSize(CAS_content[b+3],0.460,0.040)
    endif
    call BlzFrameSetText(CAS_content[b+3],first+"  "+BJ_Summary(h)+"  /  "+I2S(BJ_bet[h])+"g")
    call BlzFrameSetVisible(CAS_content[b+3],true)
    loop
        exitwhen i >= 6
        call BlzFrameSetPoint(CAS_card[c+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,dealerX+I2R(i)*0.067,-0.140)
        call BlzFrameSetSize(CAS_card[c+i],0.054,0.078)
        set card = -1
        if i < BJ_dealerCount[t] then
            set card = BJ_dealerCard[t*22+i]
        endif
        call CAS_CardFace(CAS_card[c+i],card,i == 1 and BJ_dealerCount[t] > 1 and not BJ_reveal[t])
        call BlzFrameSetVisible(CAS_card[c+i],i < IMaxBJ(2,BJ_dealerCount[t]))
        set card = -1
        if i < BJ_count[h] then
            set card = BJ_card[h*22+i]
        endif
        call BlzFrameSetPoint(CAS_card[c+6+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,handX+I2R(i)*spacing,-0.268)
        call BlzFrameSetSize(CAS_card[c+6+i],cardWidth,cardHeight)
        call CAS_CardFace(CAS_card[c+6+i],card,false)
        call BlzFrameSetVisible(CAS_card[c+6+i],i < IMaxBJ(2,BJ_count[h]))
        if BJ_split[h] then
            set card = -1
            if i < BJ_count[h+1] then
                set card = BJ_card[(h+1)*22+i]
            endif
            call BlzFrameSetPoint(CAS_card[c+12+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,splitX+I2R(i)*spacing,-0.268)
            call BlzFrameSetSize(CAS_card[c+12+i],cardWidth,cardHeight)
            call CAS_CardFace(CAS_card[c+12+i],card,false)
            call BlzFrameSetVisible(CAS_card[c+12+i],i < IMaxBJ(2,BJ_count[h+1]))
        endif
        set i = i+1
    endloop
    if BJ_count[h] > 6 or BJ_count[h+1] > 6 or BJ_dealerCount[t] > 6 then
        call BlzFrameSetText(CAS_content[b+4],"First 6 cards shown")
    elseif BJ_phase[t] >= 2 then
        call BlzFrameSetText(CAS_content[b+4],"Bots   "+BJ_SeatTotal(h+2)+" / "+BJ_SeatTotal(h+4))
    else
        call BlzFrameSetText(CAS_content[b+4],"Private table + 2 bots")
    endif
    call BlzFrameSetVisible(CAS_content[b+4],true)
    call BlzFrameSetVisible(CAS_chip[s],true)
    if betting then
        call PK_ChipArt(CAS_chip[s],CAS_amount[s])
    else
        call PK_ChipArt(CAS_chip[s],BJ_bet[h]+BJ_bet[h+1])
    endif
    if betting then
        call BlzFrameSetText(BJ_wagerLabel[s],"NEXT BET   "+CUI_Value(I2S(CAS_amount[s])+"g"))
    else
        call BlzFrameSetText(BJ_wagerLabel[s],"WAGER   "+CUI_Value(I2S(BJ_bet[h]+BJ_bet[h+1])+"g"))
    endif
    set i = 6
    loop
        exitwhen i > 10
        call BlzFrameSetVisible(CAS_button[s*64+i],betting)
        set i = i+1
    endloop
    call CAS_ShowButton(s,11,not CAS_ended and CAS_ready[s] and CAS_gold[s] >= CAS_amount[s] and (BJ_phase[t] == 0 or (BJ_phase[t] == 4 and (t != 0 or BJ_clock[t] == 0)) or (BJ_phase[t] == 1 and BJ_bet[h] == 0)))
    call CAS_ShowButton(s,12,turn)
    call CAS_ShowButton(s,13,turn)
    call CAS_ShowButton(s,14,turn and CAS_gold[s] >= BJ_bet[BJ_turn[t]-1] and BJ_count[BJ_turn[t]-1] == 2)
    call CAS_ShowButton(s,15,turn and CAS_gold[s] >= BJ_bet[BJ_turn[t]-1] and not BJ_split[h] and BJ_count[h] == 2 and BJ_Value(BJ_card[h*22]) == BJ_Value(BJ_card[h*22+1]) and (ModuloInteger(BJ_card[h*22],13) == 12) == (ModuloInteger(BJ_card[h*22+1],13) == 12))
    call BlzFrameSetVisible(CAS_button[s*64+11],betting)
    set i = 12
    loop
        exitwhen i > 15
        call BlzFrameSetVisible(CAS_button[s*64+i],ownTable and turn)
        set i = i+1
    endloop
    if BJWatchPrevious[host] != "" then
        if history != "" then
            set history = history+"  >  "
        endif
        set history = history+BJWatchPrevious[host]
    endif
    if BJWatchLast[host] != "" then
        if history != "" then
            set history = history+"  >  "
        endif
        set history = history+BJWatchLast[host]
    endif
    call BlzFrameSetText(BJWatchHistory[s],history)
    call BlzFrameSetVisible(BJWatchHistory[s],not betting and (not ownTable or not turn))
endfunction
