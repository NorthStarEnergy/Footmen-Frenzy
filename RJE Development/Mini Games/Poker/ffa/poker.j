function PK_Eligible takes integer p returns boolean
    return CasinoAdmin(p+1) and GetPlayerSlotState(Player(p)) == PLAYER_SLOT_STATE_PLAYING and GetPlayerController(Player(p)) == MAP_CONTROL_USER
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

function PK_Limit takes integer p, integer seat returns integer
    local integer x = p*2+seat
    local integer y = p*2+1-seat
    return IMinBJ(PK_Paid[x]+PK_Stack[x],PK_Paid[y]+PK_Stack[y])
endfunction

function PK_Pay takes integer x, integer amount returns nothing
    set PK_Stack[x] = PK_Stack[x]-amount
    set PK_Paid[x] = PK_Paid[x]+amount
    set PK_Total[x] = PK_Total[x]+amount
endfunction

function PK_End takes integer p, integer winner, string note returns nothing
    local integer x = p*2
    local integer pot = PK_Total[x]+PK_Total[x+1]
    if winner == 2 then
        set PK_Stack[x] = PK_Stack[x]+pot/2
        set PK_Stack[x+1] = PK_Stack[x+1]+pot/2
        set PK_Stack[x+1-PK_Dealer[p]] = PK_Stack[x+1-PK_Dealer[p]]+ModuloInteger(pot,2)
    else
        set PK_Stack[x+winner] = PK_Stack[x+winner]+pot
    endif
    if PokerBuyIn[p] > 0 then
        call CAS_Settle(p+1,PokerBuyIn[p],PK_Stack[x],PokerBuyIn[p])
        call CAS_ResultSound(p+1,PK_Stack[x]-PokerBuyIn[p])
        set PokerBuyIn[p] = 0
    endif
    set PK_Total[x] = 0
    set PK_Total[x+1] = 0
    set PK_Paid[x] = 0
    set PK_Paid[x+1] = 0
    set PK_Turn[p] = -1
    set PK_Note[p] = note+" (pot "+I2S(pot)+")"
endfunction

function PK_Showdown takes integer p returns nothing
    local integer human = PK_Score(p,0,5)
    local integer bot = PK_Score(p,1,5)
    set PK_Street[p] = 3
    set PK_Reveal[p] = true
    if human > bot then
        call PK_End(p,0,"You win: "+PK_Category(human))
    elseif bot > human then
        call PK_End(p,1,NS_Name(NS_Dealt[p])+" wins: "+PK_Category(bot))
    else
        call PK_End(p,2,"Split pot: "+PK_Category(human))
    endif
endfunction

function PK_Advance takes integer p returns nothing
    local integer x = p*2
    if PK_Stack[x] == 0 or PK_Stack[x+1] == 0 or PK_Street[p] == 3 then
        call PK_Showdown(p)
        return
    endif
    set PK_Street[p] = PK_Street[p]+1
    set PK_Paid[x] = 0
    set PK_Paid[x+1] = 0
    set PK_Acted[x] = false
    set PK_Acted[x+1] = false
    set PK_LastRaise[p] = 2
    set PK_Turn[p] = 1-PK_Dealer[p]
    set PK_Actions[p] = 0
endfunction

function PK_Deal takes integer p returns nothing
    local integer i = 0
    local integer j = 0
    local integer tmp = 0
    local integer x = p*2
    set PK_Note[p] = "Blinds 1/2. Raise button adds one minimum raise."
    if HouseStake[p] > 300 then
        set PK_Note[p] = "Maximum buy-in is 300 gold."
        return
    endif
    if not CAS_Reserve(p+1,HouseStake[p],HouseStake[p]) then
        set PK_Note[p] = CAS_note[p+1]
        return
    endif
    set NS_Dealt[p] = NS_Selected[p]
    set PokerBuyIn[p] = HouseStake[p]
    set PK_Stack[x] = PokerBuyIn[p]
    set PK_Stack[x+1] = PokerBuyIn[p]
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
    set i = 0
    loop
        exitwhen i >= 9
        set PK_Cards[p*9+i] = PK_Deck[i]
        set i = i+1
    endloop
    set PK_Hand[p] = PK_Hand[p]+1
    set PK_Dealer[p] = 1-PK_Dealer[p]
    set PK_Street[p] = 0
    set PK_Turn[p] = PK_Dealer[p]
    set PK_LastRaise[p] = 2
    set PK_Actions[p] = 0
    set PK_Clock[p] = 30
    set PK_Wait[p] = 2
    set PK_Reveal[p] = false
    set PK_Paid[x] = 0
    set PK_Paid[x+1] = 0
    set PK_Total[x] = 0
    set PK_Total[x+1] = 0
    set PK_Acted[x] = false
    set PK_Acted[x+1] = false
    set tmp = IMinBJ(PK_Stack[x],PK_Stack[x+1])
    call PK_Pay(x+PK_Dealer[p],IMinBJ(1,tmp))
    call PK_Pay(x+1-PK_Dealer[p],IMinBJ(2,tmp))
    if PK_Paid[x] == PK_Paid[x+1] and (PK_Stack[x] == 0 or PK_Stack[x+1] == 0) then
        call PK_Showdown(p)
    endif
endfunction

function PK_Action takes integer p, integer seat, integer action returns nothing
    local integer x = p*2+seat
    local integer y = p*2+1-seat
    local integer due = IMaxBJ(0,PK_Paid[y]-PK_Paid[x])
    local integer target = 0
    local integer raiseSize = 0
    if not PK_Eligible(p) or PK_Turn[p] != seat then
        return
    endif
    if action == 0 then
        if seat == 0 then
            call PK_End(p,1,"You fold. "+NS_Name(NS_Dealt[p])+" wins")
        else
            call PK_End(p,0,NS_Name(NS_Dealt[p])+" folds. You win")
        endif
        return
    elseif action == 1 then
        call PK_Pay(x,IMinBJ(due,PK_Stack[x]))
        if due == 0 then
            set PK_Note[p] = "Check."
        else
            set PK_Note[p] = "Call "+I2S(due)+"."
        endif
    else
        set target = IMaxBJ(PK_Paid[x],PK_Paid[y])+PK_LastRaise[p]
        if seat == 1 then
            set target = target-PK_LastRaise[p]+IMaxBJ(PK_LastRaise[p],(PK_Total[x]+PK_Total[y]+due)/2)
        endif
        if action == 3 then
            set target = PK_Limit(p,seat)
        endif
        set target = IMinBJ(target,PK_Limit(p,seat))
        set raiseSize = target-IMaxBJ(PK_Paid[x],PK_Paid[y])
        if raiseSize <= 0 or (PK_Acted[x] and due < PK_LastRaise[p]) then
            return
        endif
        call PK_Pay(x,target-PK_Paid[x])
        if raiseSize >= PK_LastRaise[p] then
            set PK_LastRaise[p] = raiseSize
            set PK_Acted[y] = false
        endif
        set PK_Note[p] = "Raise to "+I2S(target)+"."
    endif
    set PK_Acted[x] = true
    set PK_Actions[p] = PK_Actions[p]+1
    set PK_Turn[p] = 1-seat
    if PK_Paid[x] == PK_Paid[y] and PK_Acted[x] and PK_Acted[y] then
        call PK_Advance(p)
    elseif PK_Paid[x] == PK_Paid[y] and (PK_Stack[x] == 0 or PK_Stack[y] == 0) then
        call PK_Showdown(p)
    endif
    set PK_Clock[p] = 30
    set PK_Wait[p] = 2
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

function PK_Render takes integer p returns nothing
    local integer x = p*2
    local integer b = p*9
    local integer i = 0
    local integer due = IMaxBJ(0,PK_Paid[x+1]-PK_Paid[x])
    local integer top = IMaxBJ(PK_Paid[x],PK_Paid[x+1])
    local integer pot = PK_Total[x]+PK_Total[x+1]
    local string phase = "PREFLOP"
    local string label = "Check"
    local string path = ""
    local boolean raiseOK = false
    local integer callTone = 0
    if PK_Street[p] == 1 then
        set phase = "FLOP"
    elseif PK_Street[p] == 2 then
        set phase = "TURN"
    elseif PK_Street[p] == 3 then
        set phase = "RIVER"
    endif
    if PK_Hand[p] > 0 then
        call BlzFrameSetText(PK_Title[p],"POKER|n"+phase+" / #"+CUI_Value(I2S(PK_Hand[p])))
    else
        call BlzFrameSetText(PK_Title[p],"POKER")
    endif
    call BlzFrameSetText(PK_HumanLabel[p],"YOU")
    call BlzFrameSetText(PK_BotLabel[p],NS_Name(NS_Dealt[p]))
    if PK_Hand[p] == 0 then
        call BlzFrameSetText(PK_BotLabel[p],NS_Name(NS_Selected[p]))
    endif
    call CUI_Text(NS_Selector[p],"Opponent > "+NS_Name(NS_Selected[p]))
    call BlzFrameSetVisible(NS_Selector[p],PK_Turn[p] == -1 and not CAS_ended)
    call BlzFrameSetText(PK_HumanStack[p],CUI_Value(I2S(PK_Stack[x])))
    call BlzFrameSetText(PK_BotStack[p],CUI_Value(I2S(PK_Stack[x+1])))
    call BlzFrameSetText(PK_PotLabel[p],"POT  "+CUI_Value(I2S(pot)))
    if PK_Note[p] == "Blinds 1/2. Raise button adds one minimum raise." then
        call BlzFrameSetText(PK_Text[p],"BLINDS 1/2 / MAX BUY-IN 300g")
    else
        call BlzFrameSetText(PK_Text[p],PK_Note[p])
    endif
    call BlzFrameSetVisible(PK_CallLabel[p],PK_Turn[p] == 0)
    call BlzFrameSetText(PK_CallLabel[p],"TO CALL  "+CUI_Value(I2S(due)))
    call PK_ChipArt(PK_HumanChips[p],PK_Stack[x])
    call PK_ChipArt(PK_BotChips[p],PK_Stack[x+1])
    call PK_ChipArt(PK_PotChips[p],pot)
    call BlzFrameSetVisible(PK_HumanDealer[p],PK_Hand[p] > 0 and PK_Dealer[p] == 0)
    call BlzFrameSetVisible(PK_BotDealer[p],PK_Hand[p] > 0 and PK_Dealer[p] == 1)
    loop
        exitwhen i >= 9
        if PK_Hand[p] == 0 then
            set path = "empty"
        elseif i < 2 then
            set path = "card"+I2S(PK_Cards[b+i])
        elseif i < 4 then
            set path = "back"
            if PK_Reveal[p] then
                set path = "card"+I2S(PK_Cards[b+i])
            endif
        else
            set path = "empty"
            if i-4 < PK_BoardCount(p) then
                set path = "card"+I2S(PK_Cards[b+i])
            endif
        endif
        call BlzFrameSetTexture(PK_Face[b+i],"PokerUI\\"+path+".blp",0,true)
        set i = i+1
    endloop
    if PK_Turn[p] == 0 then
        call BlzFrameSetText(PK_Status[p],"YOUR TURN / "+CUI_Value(I2S(PK_Clock[p])+"s"))
            if due > 0 then
            set label = "Call "+I2S(due)
            set callTone = 3
        endif
            call CUI_Text(PK_Call[p],label)
        if PK_Limit(p,0) > top and (not PK_Acted[x] or due >= PK_LastRaise[p]) then
                    set raiseOK = true
            call CUI_Text(PK_Raise[p],"Raise "+I2S(IMinBJ(top+PK_LastRaise[p],PK_Limit(p,0))))
                    call CUI_Text(PK_Allin[p],"All-in "+I2S(PK_Limit(p,0)))
        endif
    elseif PK_Turn[p] == 1 then
        call BlzFrameSetText(PK_Status[p],"BOT'S TURN")
    else
        call BlzFrameSetText(PK_Status[p],"NEXT HAND")
        endif
    call CUI_Paint(PK_Fold[p],1,PK_Turn[p] == 0)
    call CUI_Paint(PK_Call[p],callTone,PK_Turn[p] == 0)
    call CUI_Paint(PK_Raise[p],2,raiseOK)
    call CUI_Paint(PK_Allin[p],2,raiseOK)
    call BlzFrameSetVisible(HouseLower[p],PK_Turn[p] == -1 and not CAS_ended)
    call BlzFrameSetVisible(HouseHigher[p],PK_Turn[p] == -1 and not CAS_ended)
    call CUI_Paint(HouseLower[p],0,HouseStake[p] > 10)
    call CUI_Paint(HouseHigher[p],0,HouseStake[p] < 300)
    call CUI_Text(PK_Next[p],"Buy in "+I2S(HouseStake[p])+"g")
    if PK_Turn[p] == -1 and not CAS_ended then
        call BlzFrameSetText(PK_HumanStack[p],CUI_Value(I2S(CAS_gold[p+1])+"g"))
        call BlzFrameSetText(PK_HumanLabel[p],"WALLET")
        if not CAS_ready[p+1] then
            call BlzFrameSetText(PK_Text[p],"Waiting for your wallet to load.")
        elseif CAS_gold[p+1] < HouseStake[p] then
            call BlzFrameSetText(PK_Text[p],"Your wallet needs "+I2S(HouseStake[p]-CAS_gold[p+1])+"g more for this buy-in.")
        endif
    endif
    call CUI_Paint(PK_Next[p],4,PK_Turn[p] == -1 and not CAS_ended and CAS_ready[p+1] and CAS_gold[p+1] >= HouseStake[p])
    call CUI_Paint(PK_Hide[p],0,true)
    if GetLocalPlayer() == Player(p) then
        call BlzFrameSetVisible(PK_Dialog[p],not PK_Hidden[p])
    endif
endfunction

function PK_Bot takes integer p returns nothing
    local integer x = p*2+1
    local integer top = IMaxBJ(PK_Paid[x],PK_Paid[x-1])
    local integer due = IMinBJ(PK_Stack[x],top-PK_Paid[x])
    local integer pot = PK_Total[x]+PK_Total[x-1]
    local integer move = NS_Move(p,due,pot,2,PK_Random(100))
    if move == 2 and (PK_Actions[p] >= 4 or PK_Stack[x] <= due or PK_Stack[x-1] <= 0 or (PK_Acted[x] and due < PK_LastRaise[p])) then
        set move = 1
    endif
    call PK_Action(p,1,move)
endfunction

function PK_Click takes nothing returns nothing
    local integer p = GetPlayerId(GetTriggerPlayer())
    local framehandle clicked = BlzGetTriggerFrame()
    if not PK_Eligible(p) then
        return
    endif
    if clicked == PK_Hide[p] then
        set PK_Hidden[p] = true
    elseif clicked == HouseLower[p] and PK_Turn[p] == -1 then
        set HouseStake[p] = IMaxBJ(10,HouseStake[p]-10)
    elseif clicked == HouseHigher[p] and PK_Turn[p] == -1 then
        set HouseStake[p] = IMinBJ(300,HouseStake[p]+10)
    elseif clicked == NS_Selector[p] and PK_Turn[p] == -1 and not CAS_ended then
        set NS_Selected[p] = ModuloInteger(NS_Selected[p]+1,5)
    elseif clicked == PK_Next[p] and PK_Turn[p] == -1 then
        call PK_Deal(p)
    elseif clicked == PK_Fold[p] then
        call PK_Action(p,0,0)
    elseif clicked == PK_Call[p] then
        call PK_Action(p,0,1)
    elseif clicked == PK_Raise[p] then
        call PK_Action(p,0,2)
    elseif clicked == PK_Allin[p] then
        call PK_Action(p,0,3)
    endif
    call PK_Render(p)
    set clicked = null
endfunction

function PK_Chat takes nothing returns nothing
    local integer p = GetPlayerId(GetTriggerPlayer())
    if PK_Started[p] and PK_Eligible(p) then
        set CAS_view[p+1] = 0
        if GetLocalPlayer() == Player(p) and CAS_root[p+1] != null then
            call BlzFrameSetVisible(CAS_root[p+1],false)
        endif
        set PK_Hidden[p] = false
        call PK_Render(p)
    endif
endfunction

function PK_Tick takes nothing returns nothing
    local integer p = 0
    loop
        exitwhen p >= 24
        if PK_Started[p] then
            if not PK_Eligible(p) then
                // Cash out the practice table before any return to active play.
                if PK_Turn[p] >= 0 then
                    set PK_Stack[p*2] = PK_Stack[p*2]+PK_Total[p*2]
                    set PK_Stack[p*2+1] = PK_Stack[p*2+1]+PK_Total[p*2+1]
                    set PK_Total[p*2] = 0
                    set PK_Total[p*2+1] = 0
                    call CAS_Settle(p+1,PokerBuyIn[p],PokerBuyIn[p],PokerBuyIn[p])
                    set PokerBuyIn[p] = 0
                    set PK_Turn[p] = -1
                endif
                call BlzFrameSetVisible(PK_Dialog[p],false)
            elseif PK_Turn[p] == 1 then
                set PK_Wait[p] = PK_Wait[p]-1
                if PK_Wait[p] <= 0 then
                    call PK_Bot(p)
                    call PK_Render(p)
                endif
            elseif PK_Turn[p] == 0 then
                set PK_Clock[p] = PK_Clock[p]-1
                if PK_Clock[p] <= 0 then
                    if PK_Paid[p*2] >= PK_Paid[p*2+1] then
                        call PK_Action(p,0,1)
                    else
                        call PK_Action(p,0,0)
                    endif
                endif
                call PK_Render(p)
            elseif not PK_Hidden[p] then
                call PK_Render(p)
            endif
        endif
        set p = p+1
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
    loop
        exitwhen p >= 24
        if GetPlayerSlotState(Player(p)) == PLAYER_SLOT_STATE_PLAYING and GetPlayerController(Player(p)) == MAP_CONTROL_USER then
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
            set PK_BotLabel[p] = PK_Label(p,0.035,0.087,0.215,0.022,0.91)
            set PK_BotStack[p] = PK_Label(p,0.105,0.109,0.085,0.032,1.48)
            set PK_HumanLabel[p] = PK_Label(p,0.105,0.314,0.085,0.017,0.91)
            set PK_HumanStack[p] = PK_Label(p,0.105,0.333,0.085,0.032,1.48)
            set PK_PotLabel[p] = PK_Label(p,0.532,0.205,0.134,0.038,1.24)
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
            set PK_Fold[p] = PK_Button(p,click,0.025,-0.439,0.105,"Fold")
            set PK_Call[p] = PK_Button(p,click,0.135,-0.439,0.12,"Check / Call")
            set PK_Raise[p] = PK_Button(p,click,0.26,-0.439,0.12,"Raise")
            set PK_Allin[p] = PK_Button(p,click,0.385,-0.439,0.13,"All-in")
            set PK_Next[p] = PK_Button(p,click,0.52,-0.439,0.155,"Next hand")
            set NS_Selector[p] = PK_Button(p,click,0.307,-0.018,0.248,"Choose opponent")
            set HouseStake[p] = 100
            set HouseLower[p] = PK_Button(p,click,0.454,-0.107,0.104,"-10g")
            set HouseHigher[p] = PK_Button(p,click,0.563,-0.107,0.112,"+10g")
            set PK_Hide[p] = PK_Button(p,click,0.565,-0.018,0.11,"Hide table")
            call TriggerAddAction(click,function PK_Click)
            call TriggerRegisterPlayerChatEvent(chat,Player(p),"-poker",true)
            set PK_Turn[p] = -1
            set PK_Note[p] = "Choose 10-300g, then click Buy in to deal. Blinds 1/2."
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

function PK_DetectSolo takes nothing returns nothing
    local integer p = 0
    local integer humans = 0
    loop
        exitwhen p >= 24
        if GetPlayerSlotState(Player(p)) == PLAYER_SLOT_STATE_PLAYING and GetPlayerController(Player(p)) == MAP_CONTROL_USER then
            set humans = humans+1
            set PK_SoloPlayer = p
        endif
        set p = p+1
    endloop
    set PK_Solo = humans == 1
    if not PK_Solo then
        set PK_SoloPlayer = -1
    endif
endfunction

function PK_Init takes nothing returns nothing
    set PK_Seed = GetRandomInt(1,2147483646)
    call PK_DetectSolo()
    call TimerStart(CreateTimer(),2,false,function PK_Start)
endfunction
