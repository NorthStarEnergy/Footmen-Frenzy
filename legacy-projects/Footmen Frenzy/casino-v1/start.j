function CAS_Tick takes nothing returns nothing
    local integer s = 1
    local integer id = 1
    set CAS_seconds = R2I(TimerGetElapsed(FF_gameTimer))
    call MK_Refresh()
    if CAS_seconds >= 120 and not CAS_warned then
        set CAS_warned = true
        call DisplayTimedTextToForce(GetPlayersAll(),10,"|cffe7cb88BETTING LAST CALL|r: all match markets close at 2:10. Open -bets for live odds.")
    endif
    if CAS_seconds >= 130 and not CAS_closed then
        set CAS_closed = true
        call DisplayTimedTextToForce(GetPlayersAll(),10,"|cffe7cb88MATCH BETTING CLOSED|r. Accepted odds are locked. Player challenges remain available.")
    endif
    call BJ_Tick()
    loop
        exitwhen id > DU_n
        if DU_state[id] == 1 and (CAS_seconds >= DU_expire[id] or not CAS_User(DU_from[id]) or not CAS_User(DU_to[id])) then
            call DU_Cancel(id)
            call FGA_SaveLocal()
        endif
        set id = id+1
    endloop
    loop
        exitwhen s > 24
        if FGA_ready[s] then
            call CAS_Flush(s)
        endif
        if CAS_root[s] != null and CAS_User(s) then
            call CAS_Render(s)
        endif
        set s = s+1
    endloop
endfunction

function CAS_BuildPlayer takes integer s returns nothing
    local integer i = 0
    local integer b = s*32
    local integer c = s*18
    local real x
    local real y
    local trigger click = CreateTrigger()
    set CAS_amount[s] = 50
    set CAS_note[s] = "Exact bet: -stake 250"
    set MK_tab[s] = 1
    set BJ_table[s] = s
    set BJ_seat[s] = s*6
    set BJ_owner[s*6] = s
    set BJ_owner[s*6+1] = -1
    set BJ_owner[s*6+2] = -1
    call BJ_Shuffle(s)
    set CAS_root[s] = BlzCreateFrameByType("BACKDROP","CasinoTable",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),"",s)
    call BlzFrameSetSize(CAS_root[s],0.70,0.48)
    call BlzFrameSetAbsPoint(CAS_root[s],FRAMEPOINT_TOPLEFT,0.05,0.57)
    call BlzFrameSetTexture(CAS_root[s],"PokerUI\\table.blp",0,true)
    call BlzFrameSetLevel(CAS_root[s],60)
    call BlzFrameSetVisible(CAS_root[s],false)
    set CAS_launch[s] = BlzCreateFrameByType("GLUETEXTBUTTON","CasinoOpen",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),"ScriptDialogButton",s)
    call BlzFrameSetSize(CAS_launch[s],0.065,0.025)
    call BlzFrameSetAbsPoint(CAS_launch[s],FRAMEPOINT_TOPLEFT,0.73,0.18)
    call BlzFrameSetText(CAS_launch[s],"Casino")
    call BlzFrameSetVisible(CAS_launch[s],GetLocalPlayer() == Player(s-1))
    call BlzTriggerRegisterFrameEvent(click,CAS_launch[s],FRAMEEVENT_CONTROL_CLICK)
    set CAS_title[s] = CAS_Label(s,0.025,0.016,0.53,0.027,1.15)
    set CAS_balance[s] = CAS_Label(s,0.025,0.043,0.65,0.024,1.0)
    set CAS_status[s] = CAS_Label(s,0.025,0.366,0.65,0.024,1.08)
    set CAS_footer[s] = CAS_Label(s,0.025,0.452,0.65,0.024,0.85)
    call CAS_Button(s,0,click,0.025,0.073,0.13,"Blackjack")
    call CAS_Button(s,1,click,0.16,0.073,0.12,"Match bets")
    call CAS_Button(s,2,click,0.285,0.073,0.13,"Duels")
    call CAS_Button(s,3,click,0.42,0.073,0.10,"Rules")
    call CAS_Button(s,4,click,0.575,0.014,0.10,"Hide")
    call CAS_Button(s,5,click,0.525,0.073,0.15,"Poker")
    call CAS_Button(s,6,click,0.025,0.394,0.075,"-10")
    call CAS_Button(s,7,click,0.105,0.394,0.075,"+10")
    call CAS_Button(s,8,click,0.185,0.394,0.075,"+50")
    call CAS_Button(s,9,click,0.265,0.394,0.075,"2x")
    call CAS_Button(s,10,click,0.345,0.394,0.075,"Half")
    call CAS_Button(s,11,click,0.43,0.394,0.245,"BET")
    call CAS_Button(s,12,click,0.025,0.423,0.10,"Hit")
    call CAS_Button(s,13,click,0.13,0.423,0.10,"Stand")
    call CAS_Button(s,14,click,0.235,0.423,0.12,"Double")
    call CAS_Button(s,15,click,0.36,0.423,0.10,"Split")
    call CAS_Button(s,16,click,0.465,0.423,0.21,"Community")
    call CAS_Button(s,20,click,0.025,0.110,0.125,"Hero kill")
    call CAS_Button(s,21,click,0.155,0.110,0.125,"Base kill")
    call CAS_Button(s,22,click,0.285,0.110,0.125,"Base lost")
    call CAS_Button(s,23,click,0.415,0.110,0.125,"Level 16")
    call CAS_Button(s,24,click,0.545,0.110,0.13,"Win match")
    call CAS_Button(s,25,click,0.555,0.336,0.12,"MORE")
    call CAS_Button(s,32,click,0.43,0.394,0.245,"BET")
    call CAS_Button(s,33,click,0.43,0.394,0.245,"CHALLENGE")
    call CAS_Button(s,34,click,0.025,0.298,0.20,"Opponent >")
    call CAS_Button(s,35,click,0.235,0.298,0.20,"Winner >")
    call CAS_Button(s,36,click,0.025,0.333,0.20,"Accept")
    call CAS_Button(s,37,click,0.235,0.333,0.20,"Decline")
    call CAS_Button(s,38,click,0.445,0.333,0.23,"Cancel")
    set CAS_content[b] = CAS_Label(s,0.025,0.109,0.65,0.023,0.90)
    set CAS_content[b+1] = CAS_Label(s,0.025,0.136,0.65,0.022,0.95)
    set CAS_content[b+2] = CAS_Label(s,0.195,0.140,0.48,0.023,0.90)
    set CAS_content[b+3] = CAS_Label(s,0.025,0.280,0.19,0.055,1.15)
    set CAS_content[b+4] = CAS_Label(s,0.025,0.190,0.16,0.040,0.85)
    set CAS_content[b+5] = CAS_Label(s,0.43,0.347,0.245,0.018,0.80)
    set CAS_content[b+6] = CAS_Label(s,0.19,0.252,0.48,0.020,0.80)
    set CAS_content[b+7] = CAS_Label(s,0.025,0.143,0.65,0.021,0.95)
    set CAS_content[b+8] = CAS_Label(s,0.035,0.169,0.64,0.018,0.80)
    set CAS_content[b+9] = CAS_Label(s,0.025,0.330,0.52,0.035,0.85)
    set CAS_content[b+28] = CAS_Label(s,0.04,0.125,0.62,0.115,1.0)
    set CAS_content[b+29] = CAS_Label(s,0.04,0.245,0.62,0.045,1.0)
    set CAS_content[b+30] = CAS_Label(s,0.04,0.112,0.62,0.25,0.86)
    // Unused label 31 is still created for a uniform visibility loop.
    set CAS_content[b+31] = CAS_Label(s,0.300,0.169,0.13,0.018,0.8)
    loop
        exitwhen i >= 6
        set y = 0.190+I2R(i)*0.023
        set CAS_content[b+10+i*3] = CAS_Label(s,0.035,y,0.255,0.021,0.90)
        set CAS_content[b+11+i*3] = CAS_Label(s,0.300,y,0.13,0.021,0.86)
        set CAS_content[b+12+i*3] = CAS_Label(s,0.445,y,0.10,0.021,0.93)
        set CAS_track[s*6+i] = CAS_Texture(s,"UI\\Widgets\\EscMenu\\Human\\blank-background.blp",CAS_SafeX(0.300),y+0.018,CAS_SafeW(0.115),0.003)
        call BlzFrameSetVertexColor(CAS_track[s*6+i],BlzConvertColor(255,30,55,49))
        set CAS_bar[s*6+i] = CAS_Texture(s,"UI\\Widgets\\EscMenu\\Human\\blank-background.blp",CAS_SafeX(0.300),y+0.018,CAS_SafeW(0.115),0.003)
        call BlzFrameSetVertexColor(CAS_bar[s*6+i],BlzConvertColor(255,214,184,106))
        call CAS_Button(s,26+i,click,0.555,y-0.003,0.12,"Select")
        call BlzFrameSetSize(CAS_button[s*40+26+i],CAS_SafeW(0.12),0.023)
        set x = 0.025
        if i >= 3 then
            set x = 0.355
        endif
        set CAS_row[s*6+i] = CAS_Label(s,x,0.245+I2R(ModuloInteger(i,3))*0.010,0.30,0.014,0.73)
        set CAS_card[c+i] = CAS_Texture(s,"PokerUI\\empty.blp",0.195+I2R(i)*0.067,0.178,0.054,0.060)
        set CAS_card[c+6+i] = CAS_Texture(s,"PokerUI\\empty.blp",0.205+I2R(i)*0.028,0.274,0.050,0.072)
        set CAS_card[c+12+i] = CAS_Texture(s,"PokerUI\\empty.blp",0.430+I2R(i)*0.028,0.274,0.050,0.060)
        set i = i+1
    endloop
    set CAS_chip[s] = CAS_Texture(s,"PokerUI\\chips1.blp",0.025,0.322,0.10,0.033)
    call TriggerAddAction(click,function CAS_Click)
    call CAS_Render(s)
    call DisplayTimedTextToPlayer(Player(s-1),0,0,15,"Casino ready: -blackjack / -bets / -challenges. Account gold wagers. Open Rules for table details.")
    set click = null
endfunction

function CAS_BuildNext takes nothing returns nothing
    set CAS_buildSlot = CAS_buildSlot+1
    if CAS_User(CAS_buildSlot) then
        call CAS_BuildPlayer(CAS_buildSlot)
    endif
    if CAS_buildSlot >= 24 then
        call DestroyTimer(GetExpiredTimer())
    endif
endfunction

function CAS_Init takes nothing returns nothing
    local trigger chat = CreateTrigger()
    local trigger death = CreateTrigger()
    local trigger level = CreateTrigger()
    local integer p = 0
    set CAS_seed = GetRandomInt(1,2147483646)
    set CAS_baseEvent = CreateTrigger()
    set CAS_matchEvent = CreateTrigger()
    set MK_payTimer = CreateTimer()
    call TriggerAddAction(CAS_baseEvent,function MK_BaseDeath)
    call TriggerAddAction(CAS_matchEvent,function CAS_EndMatch)
    loop
        exitwhen p >= 24
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-casino",true)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-blackjack",true)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-bets",true)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-challenges",true)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-stake ",false)
        set p = p+1
    endloop
    call TriggerRegisterAnyUnitEventBJ(death,EVENT_PLAYER_UNIT_DEATH)
    call TriggerRegisterAnyUnitEventBJ(level,EVENT_PLAYER_HERO_LEVEL)
    call TriggerAddAction(chat,function CAS_Chat)
    call TriggerAddAction(death,function MK_HeroDeath)
    call TriggerAddAction(level,function MK_Level)
    call BJ_Shuffle(0)
    call TimerStart(CreateTimer(),0.20,true,function CAS_BuildNext)
    call TimerStart(CreateTimer(),1.00,true,function CAS_Tick)
    set chat = null
    set death = null
    set level = null
endfunction
