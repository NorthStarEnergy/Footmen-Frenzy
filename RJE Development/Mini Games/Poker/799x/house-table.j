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
