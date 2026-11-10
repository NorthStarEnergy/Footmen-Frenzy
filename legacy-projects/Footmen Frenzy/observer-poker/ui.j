// UI helpers are inserted before PK_Render; all frame handles created on all clients.
function PK_Texture takes integer p, string name, real x, real y, real w, real h returns framehandle
    local framehandle f = BlzCreateFrameByType("BACKDROP","PokerArtwork",PK_Dialog[p],"",p)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PK_Dialog[p],FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetTexture(f,"PokerUI\\"+name+".blp",0,true)
    return f
endfunction

function PK_Label takes integer p, real x, real y, real w, real h, real scale returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","PokerLabel",PK_Dialog[p],"",p)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PK_Dialog[p],FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetScale(f,scale)
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
    call BlzFrameSetEnable(PK_Fold[p],false)
    call BlzFrameSetEnable(PK_Call[p],false)
    call BlzFrameSetEnable(PK_Raise[p],false)
    call BlzFrameSetEnable(PK_Allin[p],false)
    call BlzFrameSetEnable(PK_Next[p],false)
    if PK_Street[p] == 1 then
        set phase = "FLOP"
    elseif PK_Street[p] == 2 then
        set phase = "TURN"
    elseif PK_Street[p] == 3 then
        set phase = "RIVER"
    endif
    call BlzFrameSetText(PK_Title[p],"|cffe7cb88FOOTMEN / OBSERVER POKER|r|n|cffabc1baHand "+I2S(PK_Hand[p])+"  /  "+phase+"  /  Blinds 5-10|r")
    call BlzFrameSetText(PK_HumanLabel[p],"|cffe7cb88YOU|r|n"+I2S(PK_Stack[x])+" chips")
    call BlzFrameSetText(PK_BotLabel[p],"COMPUTER|n"+I2S(PK_Stack[x+1])+" chips")
    call BlzFrameSetText(PK_PotLabel[p],"|cffffd579POT  "+I2S(pot)+"|r")
    call BlzFrameSetText(PK_Text[p],PK_Note[p])
    call BlzFrameSetText(PK_CallLabel[p],"To call: "+I2S(due))
    call PK_ChipArt(PK_HumanChips[p],PK_Stack[x])
    call PK_ChipArt(PK_BotChips[p],PK_Stack[x+1])
    call PK_ChipArt(PK_PotChips[p],pot)
    call BlzFrameSetVisible(PK_HumanDealer[p],PK_Dealer[p] == 0)
    call BlzFrameSetVisible(PK_BotDealer[p],PK_Dealer[p] == 1)
    loop
        exitwhen i >= 9
        if i < 2 then
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
        call BlzFrameSetText(PK_Status[p],"|cffffd579YOUR TURN / "+I2S(PK_Clock[p])+"s|r")
        call BlzFrameSetEnable(PK_Fold[p],true)
        if due > 0 then
            set label = "Call "+I2S(due)
        endif
        call BlzFrameSetEnable(PK_Call[p],true)
        call BlzFrameSetText(PK_Call[p],label)
        if PK_Limit(p,0) > top and (not PK_Acted[x] or due >= PK_LastRaise[p]) then
            call BlzFrameSetEnable(PK_Raise[p],true)
            call BlzFrameSetText(PK_Raise[p],"Raise to "+I2S(IMinBJ(top+PK_LastRaise[p],PK_Limit(p,0))))
            call BlzFrameSetEnable(PK_Allin[p],true)
            call BlzFrameSetText(PK_Allin[p],"All-in "+I2S(PK_Limit(p,0)))
        endif
    elseif PK_Turn[p] == 1 then
        call BlzFrameSetText(PK_Status[p],"Computer thinking...")
    else
        call BlzFrameSetText(PK_Status[p],"Hand complete")
        call BlzFrameSetEnable(PK_Next[p],true)
    endif
    if GetLocalPlayer() == Player(p) then
        call BlzFrameSetVisible(PK_Dialog[p],not PK_Hidden[p])
    endif
endfunction

function PK_Start takes nothing returns nothing
    local integer p = 0
    local integer i = 0
    local trigger click = null
    local trigger chat = CreateTrigger()
    loop
        exitwhen p >= 24
        if PK_Eligible(p) then
            set PK_Started[p] = true
            set PK_Stack[p*2] = 500
            set PK_Stack[p*2+1] = 500
            set PK_Dialog[p] = BlzCreateFrameByType("BACKDROP","PokerTable",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),"",p)
            call BlzFrameSetSize(PK_Dialog[p],0.70,0.48)
            call BlzFrameSetAbsPoint(PK_Dialog[p],FRAMEPOINT_TOPLEFT,0.05,0.57)
            call BlzFrameSetTexture(PK_Dialog[p],"PokerUI\\table.blp",0,true)
            call BlzFrameSetLevel(PK_Dialog[p],50)
            call BlzFrameSetVisible(PK_Dialog[p],false)
            set PK_Title[p] = PK_Label(p,0.025,0.018,0.50,0.05,1.15)
            set PK_BotLabel[p] = PK_Label(p,0.08,0.085,0.16,0.052,1.35)
            set PK_HumanLabel[p] = PK_Label(p,0.08,0.315,0.16,0.052,1.35)
            set PK_PotLabel[p] = PK_Label(p,0.34,0.16,0.16,0.027,1.25)
            set PK_Status[p] = PK_Label(p,0.46,0.298,0.19,0.027,1.0)
            set PK_CallLabel[p] = PK_Label(p,0.46,0.369,0.18,0.025,1.05)
            set PK_Text[p] = PK_Label(p,0.025,0.405,0.65,0.027,1.0)
            set PK_HumanChips[p] = PK_Texture(p,"chips4",0.46,0.325,0.075,0.045)
            set PK_BotChips[p] = PK_Texture(p,"chips4",0.46,0.09,0.075,0.045)
            set PK_PotChips[p] = PK_Texture(p,"chips1",0.275,0.158,0.052,0.026)
            set PK_HumanDealer[p] = PK_Texture(p,"dealer",0.245,0.335,0.022,0.022)
            set PK_BotDealer[p] = PK_Texture(p,"dealer",0.245,0.095,0.022,0.022)
            set PK_Face[p*9] = PK_Texture(p,"empty",0.285,0.305,0.06,0.087)
            set PK_Face[p*9+1] = PK_Texture(p,"empty",0.353,0.305,0.06,0.087)
            set PK_Face[p*9+2] = PK_Texture(p,"back",0.285,0.067,0.058,0.084)
            set PK_Face[p*9+3] = PK_Texture(p,"back",0.351,0.067,0.058,0.084)
            set i = 0
            loop
                exitwhen i >= 5
                set PK_Face[p*9+4+i] = PK_Texture(p,"empty",0.187+I2R(i)*0.066,0.196,0.06,0.086)
                set i = i+1
            endloop
            set click = CreateTrigger()
            set PK_Fold[p] = PK_Button(p,click,0.025,-0.439,0.105,"Fold")
            set PK_Call[p] = PK_Button(p,click,0.135,-0.439,0.12,"Check / Call")
            set PK_Raise[p] = PK_Button(p,click,0.26,-0.439,0.12,"Raise")
            set PK_Allin[p] = PK_Button(p,click,0.385,-0.439,0.13,"All-in")
            set PK_Next[p] = PK_Button(p,click,0.52,-0.439,0.155,"Next hand")
            set PK_Hide[p] = PK_Button(p,click,0.565,-0.018,0.11,"Hide table")
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
