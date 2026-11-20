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
    if not CasinoAdmin(s) then
        return
    endif
    if line == "-accept" then
        loop
            exitwhen id > 48
            if CreditOwner[id] != 0 and CreditTarget[id] == s then
                call CreditAccept(s,id)
                return
            endif
            set id = id+1
        endloop
    elseif CreditOpen(target) and target != s and FGA_Number(amount) and FGA_Number(fee) then
        call CreditPost(s,false,target,S2I(amount),0,0,0,S2I(fee))
        if CreditOwner[CreditSelected[s]] == s and CreditTarget[CreditSelected[s]] == target then
            call CreditTell(target,GetPlayerName(Player(s-1))+" offers "+amount+"g with a "+fee+"g fee. Review in Credit or type -accept.")
        endif
    else
        call CreditTell(s,"Use -loan slot amount fee, or open Casino > Credit.")
    endif
endfunction

function PK_Eligible takes integer p returns boolean
    return CasinoAdmin(p+1) and GetPlayerSlotState(Player(p)) == PLAYER_SLOT_STATE_PLAYING and GetPlayerController(Player(p)) == MAP_CONTROL_USER
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
    local integer first = PK_Cards[base+2]
    local integer second = PK_Cards[base+3]
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
    local integer score = PK_Score(p,1,n)
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
        set card = PK_Cards[base+4+i]
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
        if score == PK_Score5(PK_Cards[base+4],PK_Cards[base+5],PK_Cards[base+6],PK_Cards[base+7],PK_Cards[base+8]) then
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
    local integer n = PK_BoardCount(p)
    local integer price = 100*due/IMaxBJ(1,pot+due)
    local integer value
    local integer pressure
    local integer defend
    local integer caution = 0
    local integer first = PK_Cards[p*9+2]
    local integer second = PK_Cards[p*9+3]
    if n == 0 then
        set value = NS_Preflop(first,second)
        if PK_Dealer[p] == 1 then
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

function BJ_Value takes integer card returns integer
    return IMinBJ(10,ModuloInteger(card,13)+2)
endfunction

function BJ_Recount takes integer h returns nothing
    local integer i = 0
    local integer c
    set BJ_total[h] = 0
    set BJ_aces[h] = 0
    loop
        exitwhen i >= BJ_count[h]
        set c = BJ_card[h*22+i]
        if ModuloInteger(c,13) == 12 then
            set BJ_total[h] = BJ_total[h]+11
            set BJ_aces[h] = BJ_aces[h]+1
        else
            set BJ_total[h] = BJ_total[h]+BJ_Value(c)
        endif
        set i = i+1
    endloop
    loop
        exitwhen BJ_total[h] <= 21 or BJ_aces[h] == 0
        set BJ_total[h] = BJ_total[h]-10
        set BJ_aces[h] = BJ_aces[h]-1
    endloop
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
    local integer card = BJ_Draw(t)
    set BJ_dealerCard[t*22+BJ_dealerCount[t]] = card
    set BJ_dealerCount[t] = BJ_dealerCount[t]+1
    if ModuloInteger(card,13) == 12 then
        set BJ_dealerTotal[t] = BJ_dealerTotal[t]+11
        set BJ_dealerAces[t] = BJ_dealerAces[t]+1
    else
        set BJ_dealerTotal[t] = BJ_dealerTotal[t]+BJ_Value(card)
    endif
    loop
        exitwhen BJ_dealerTotal[t] <= 21 or BJ_dealerAces[t] == 0
        set BJ_dealerTotal[t] = BJ_dealerTotal[t]-10
        set BJ_dealerAces[t] = BJ_dealerAces[t]-1
    endloop
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
                call CAS_Settle(s,stake,payout,BJ_reserve[h])
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
                set CAS_note[s] = BJ_result[h]
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
    if BJ_error[t] then
        call BJ_Finish(t,true)
        return
    endif
    loop
        exitwhen h >= t*12+12
        if BJ_state[h] == 1 then
            set BJ_turn[t] = h+1
            set BJ_clock[t] = 20
            return
        endif
        set h = h+1
    endloop
    set BJ_turn[t] = 0
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
    if BJ_phase[t] != 2 or h < 0 or BJ_owner[h/2] != s or BJ_state[h] != 1 then
        return
    endif
    if action == 1 then
        call BJ_Hit(t,h)
    elseif action == 2 then
        set BJ_state[h] = 2
    elseif action == 3 then
        if BJ_count[h] != 2 or BJ_bet[h] > 10000 or (BJ_split[h] and ModuloInteger(BJ_card[h*22],13) == 12) then
            return
        endif
        set stake = BJ_bet[h]
        if not CAS_Reserve(s,stake,stake*3/2) then
            return
        endif
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
        if not CAS_Reserve(s,stake,stake*3/2) then
            return
        endif
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
            elseif BJ_clock[t] <= 0 or not CAS_User(s) then
                call BJWatchRecord(s,"Auto-stand")
                set BJ_state[h] = 2
                call BJ_Next(t)
            endif
        elseif BJ_phase[t] == 3 then
            set BJ_clock[t] = BJ_clock[t]-1
            if BJ_clock[t] <= 0 then
                if BJ_dealerTotal[t] < 17 then
                    call BJ_DealerHit(t)
                    set BJ_clock[t] = 1
                    if BJ_error[t] then
                        call BJ_Finish(t,true)
                    endif
                else
                    call BJ_Finish(t,false)
                endif
            endif
        elseif BJ_phase[t] == 4 then
            set BJ_clock[t] = IMaxBJ(0,BJ_clock[t]-1)
        endif
        set t = t+1
    endloop
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
    call CAS_Credit(s,DU_stake[id],0)
    set CAS_note[s] = "Challenge declined, cancelled, or expired. Gold returned."
endfunction

function DU_Offer takes integer s returns nothing
    local integer to = DU_opponent[s]
    local integer target = DU_pick[s]
    local integer stake = CAS_amount[s]
    if not CAS_User(to) or to == s or DU_outgoing[s] != 0 or DU_incoming[to] != 0 or DU_active[s] != 0 or DU_active[to] != 0 or not MK_Valid(5,target) or DU_n >= 511 then
        set CAS_note[s] = "Choose an available opponent and a valid winner. One active challenge per player."
        return
    endif
    if not CAS_Reserve(s,stake,0) then
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
    if CAS_seconds >= DU_expire[id] or not CAS_User(proposer) or DU_active[s] != 0 or DU_active[proposer] != 0 or DU_ffa[id] != MK_FFA() or not MK_Valid(5,DU_target[id]) then
        call DU_Cancel(id)
        return
    endif
    if not CAS_Reserve(s,DU_stake[id],0) then
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
                call CAS_Credit(DU_from[id],stake,0)
                call CAS_Credit(DU_to[id],stake,0)
            else
                set won = DU_to[id]
                if DU_target[id] == winner then
                    set won = DU_from[id]
                endif
                call CAS_Credit(won,stake,stake)
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

function BJ_CardStart takes real center, integer count, real width, real spacing returns real
    local integer visible = IMaxBJ(2,IMinBJ(6,count))
    return center-(width+I2R(visible-1)*spacing)*0.5
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
        set dealer = dealer+"  "+CUI_Value(I2S(BJ_dealerTotal[t]))
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
        call BlzFrameSetText(CAS_content[b+5],second+"  "+BJ_Summary(h+1)+"|nBET  "+CUI_Value(I2S(BJ_bet[h+1])+"g"))
        call BlzFrameSetVisible(CAS_content[b+5],true)
    else
        set handX = BJ_CardStart(0.445,BJ_count[h],cardWidth,spacing)
        call BlzFrameSetSize(CAS_content[b+3],0.460,0.040)
    endif
    call BlzFrameSetText(CAS_content[b+3],first+"  "+BJ_Summary(h)+"|nBET  "+CUI_Value(I2S(BJ_bet[h])+"g"))
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
    call CAS_ShowButton(s,11,not CAS_ended and CAS_ready[s] and CAS_gold[s] >= CAS_amount[s] and (BJ_phase[t] == 0 or BJ_phase[t] == 4 or (BJ_phase[t] == 1 and BJ_bet[h] == 0)))
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
