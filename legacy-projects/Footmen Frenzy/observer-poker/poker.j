// Observer Poker v1. All state changes run in synchronized trigger context.
// Each eligible observer owns an independent heads-up practice table.
function PK_Eligible takes integer p returns boolean
    return GetPlayerSlotState(Player(p)) == PLAYER_SLOT_STATE_PLAYING and GetPlayerController(Player(p)) == MAP_CONTROL_USER and (PK_SoloPlayer == p or GetPlayerTeam(Player(p)) == 4)
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
        call PK_End(p,1,"Computer wins: "+PK_Category(bot))
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
    set PK_LastRaise[p] = 10
    set PK_Turn[p] = 1-PK_Dealer[p]
    set PK_Actions[p] = 0
endfunction

function PK_Deal takes integer p returns nothing
    local integer i = 0
    local integer j = 0
    local integer tmp = 0
    local integer x = p*2
    set PK_Note[p] = "Blinds 5/10. Raise button adds one minimum raise."
    if PK_Stack[x] == 0 or PK_Stack[x+1] == 0 then
        set PK_Stack[x] = 500
        set PK_Stack[x+1] = 500
        set PK_Note[p] = "Practice reload: both stacks reset to 500."
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
    set PK_LastRaise[p] = 10
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
    call PK_Pay(x+PK_Dealer[p],IMinBJ(5,tmp))
    call PK_Pay(x+1-PK_Dealer[p],IMinBJ(10,tmp))
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
            call PK_End(p,1,"You fold. Computer wins")
        else
            call PK_End(p,0,"Computer folds. You win")
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

function PK_Render takes integer p returns nothing
    local integer x = p*2
    local integer b = p*9
    local integer i = 0
    local integer due = IMaxBJ(0,PK_Paid[x+1]-PK_Paid[x])
    local integer top = IMaxBJ(PK_Paid[x],PK_Paid[x+1])
    local string board = ""
    local string bot = "[hidden] [hidden]"
    local string phase = "Preflop"
    local string label = "Check"
    local string message = ""
    call BlzFrameSetEnable(PK_Fold[p],false)
    call BlzFrameSetEnable(PK_Call[p],false)
    call BlzFrameSetEnable(PK_Raise[p],false)
    call BlzFrameSetEnable(PK_Allin[p],false)
    call BlzFrameSetEnable(PK_Next[p],false)
    if PK_Street[p] == 1 then
        set phase = "Flop"
    elseif PK_Street[p] == 2 then
        set phase = "Turn"
    elseif PK_Street[p] == 3 then
        set phase = "River"
    endif
    loop
        exitwhen i >= PK_BoardCount(p)
        set board = board+PK_Card(PK_Cards[b+4+i])+"  "
        set i = i+1
    endloop
    if board == "" then
        set board = "(not dealt yet)"
    endif
    if PK_Reveal[p] then
        set bot = PK_Card(PK_Cards[b+2])+" "+PK_Card(PK_Cards[b+3])
    endif
    set message = "OBSERVER POKER - Hand "+I2S(PK_Hand[p])+" / "+phase+"|nComputer: "+I2S(PK_Stack[x+1])+" chips  "+bot+"|nBoard: "+board+"|nPot: "+I2S(PK_Total[x]+PK_Total[x+1])+"|nYou: "+I2S(PK_Stack[x])+" chips  "+PK_Card(PK_Cards[b])+" "+PK_Card(PK_Cards[b+1])+"|n"+PK_Note[p]
    if PK_Turn[p] == 0 then
        set message = message+"|nYour turn ("+I2S(PK_Clock[p])+" seconds)."
        call BlzFrameSetEnable(PK_Fold[p],true)
        call BlzFrameSetText(PK_Fold[p],"Fold")
        if due > 0 then
            set label = "Call "+I2S(due)
        endif
        call BlzFrameSetEnable(PK_Call[p],true)
        call BlzFrameSetText(PK_Call[p],label+"")
        if PK_Limit(p,0) > top and (not PK_Acted[x] or due >= PK_LastRaise[p]) then
            call BlzFrameSetEnable(PK_Raise[p],true)
        call BlzFrameSetText(PK_Raise[p],"Raise to "+I2S(IMinBJ(top+PK_LastRaise[p],PK_Limit(p,0)))+"")
            call BlzFrameSetEnable(PK_Allin[p],true)
        call BlzFrameSetText(PK_Allin[p],"All-in "+I2S(PK_Limit(p,0)))
        endif
    elseif PK_Turn[p] == 1 then
        set message = message+"|nComputer is thinking..."
    else
        call BlzFrameSetEnable(PK_Next[p],true)
        call BlzFrameSetText(PK_Next[p],"Next hand")
    endif
    call BlzFrameSetEnable(PK_Hide[p],true)
        call BlzFrameSetText(PK_Hide[p],"Hide table (-poker to reopen)")
    call BlzFrameSetText(PK_Text[p],message)
    if GetLocalPlayer() == Player(p) then
        call BlzFrameSetVisible(PK_Dialog[p],not PK_Hidden[p])
    endif
endfunction

function PK_Bot takes integer p returns nothing
    local integer x = p*2+1
    local integer due = IMaxBJ(0,PK_Paid[x-1]-PK_Paid[x])
    local integer r1 = ModuloInteger(PK_Cards[p*9+2],13)+2
    local integer r2 = ModuloInteger(PK_Cards[p*9+3],13)+2
    local integer strength = 0
    local integer roll = PK_Random(100)
    // Uses its own cards and the revealed board only, never human/future cards.
    if PK_Street[p] == 0 then
        if r1 == r2 then
            set strength = 3
        elseif r1 >= 11 and r2 >= 10 then
            set strength = 2
        elseif r1 >= 12 or r2 >= 12 then
            set strength = 1
        endif
    else
        set strength = PK_Score(p,1,PK_BoardCount(p))/759375
    endif
    if due > 0 and strength == 0 and due > 10 and roll < 65 then
        call PK_Action(p,1,0)
    elseif PK_Actions[p] < 4 and PK_Limit(p,1) > IMaxBJ(PK_Paid[x],PK_Paid[x-1]) and (not PK_Acted[x] or due >= PK_LastRaise[p]) and ((strength >= 2 and roll < 55) or roll < 8) then
        call PK_Action(p,1,2)
    else
        call PK_Action(p,1,1)
    endif
endfunction

function PK_Click takes nothing returns nothing
    local integer p = GetPlayerId(GetTriggerPlayer())
    local framehandle clicked = BlzGetTriggerFrame()
    if not PK_Eligible(p) then
        return
    endif
    if clicked == PK_Hide[p] then
        set PK_Hidden[p] = true
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
            endif
        endif
        set p = p+1
    endloop
endfunction

function PK_Button takes integer p, trigger t, real x, real y, real width, string label returns framehandle
    local framehandle f = BlzCreateFrame("ScriptDialogButton",PK_Dialog[p],0,p)
    call BlzFrameSetSize(f,width,0.035)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PK_Dialog[p],FRAMEPOINT_TOPLEFT,x,y)
    call BlzFrameSetText(f,label)
    call BlzTriggerRegisterFrameEvent(t,f,FRAMEEVENT_CONTROL_CLICK)
    return f
endfunction

function PK_Start takes nothing returns nothing
    local integer p = 0
    local trigger click = null
    local trigger chat = CreateTrigger()
    loop
        exitwhen p >= 24
        if PK_Eligible(p) then
            set PK_Started[p] = true
            set PK_Stack[p*2] = 500
            set PK_Stack[p*2+1] = 500
            set PK_Dialog[p] = BlzCreateFrame("EscMenuBackdrop",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),0,p)
            call BlzFrameSetSize(PK_Dialog[p],0.48,0.36)
            call BlzFrameSetAbsPoint(PK_Dialog[p],FRAMEPOINT_TOPLEFT,0.16,0.54)
            call BlzFrameSetLevel(PK_Dialog[p],50)
            call BlzFrameSetVisible(PK_Dialog[p],false)
            set PK_Text[p] = BlzCreateFrameByType("TEXT","PokerText",PK_Dialog[p],"",p)
            call BlzFrameSetPoint(PK_Text[p],FRAMEPOINT_TOPLEFT,PK_Dialog[p],FRAMEPOINT_TOPLEFT,0.025,-0.025)
            call BlzFrameSetSize(PK_Text[p],0.43,0.22)
            call BlzFrameSetTextAlignment(PK_Text[p],TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_LEFT)
            call BlzFrameSetScale(PK_Text[p],1.1)
            set click = CreateTrigger()
            set PK_Fold[p] = PK_Button(p,click,0.025,-0.25,0.09,"Fold")
            set PK_Call[p] = PK_Button(p,click,0.12,-0.25,0.11,"Check / Call")
            set PK_Raise[p] = PK_Button(p,click,0.235,-0.25,0.105,"Raise")
            set PK_Allin[p] = PK_Button(p,click,0.345,-0.25,0.11,"All-in")
            set PK_Next[p] = PK_Button(p,click,0.025,-0.30,0.13,"Next hand")
            set PK_Hide[p] = PK_Button(p,click,0.16,-0.30,0.295,"Hide table (-poker to reopen)")
            call TriggerAddAction(click,function PK_Click)
            call TriggerRegisterPlayerChatEvent(chat,Player(p),"-poker",true)
            call PK_Deal(p)
            call PK_Render(p)
            call DisplayTimedTextToPlayer(Player(p),0,0,20,"Observer Poker: automatically seated vs Computer. Play chips only. Type -poker to reopen. Solo practice pauses the battlefield.")
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
    local group g = null
    local rect bounds = null
    if PK_Solo then
        call SetPlayerTeam(Player(PK_SoloPlayer),4)
        call FogEnable(false)
        call FogMaskEnable(false)
        set g = CreateGroup()
        set bounds = GetWorldBounds()
        call GroupEnumUnitsInRect(g,bounds,null)
        call ForGroup(g,function PK_PauseUnit)
        call DestroyGroup(g)
        call RemoveRect(bounds)
    endif
    call TimerStart(CreateTimer(),2,false,function PK_Start)
    set g = null
    set bounds = null
endfunction
