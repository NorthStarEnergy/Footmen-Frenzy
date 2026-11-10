// Keep labels and controls inside a shared horizontal safe area.
function CAS_SafeX takes real x returns real
    return 0.035+x*0.90
endfunction

function CAS_SafeW takes real width returns real
    return width*0.90
endfunction

function CAS_Label takes integer s, real x, real y, real w, real h, real scale returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","CasinoLabel",CAS_root[s],"",s)
    call BlzFrameSetSize(f,CAS_SafeW(w),h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,CAS_SafeX(x),-y)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetFont(f,"CasinoUI\\Bold.ttf",0.0135,0)
    call BlzFrameSetScale(f,scale)
    return f
endfunction

function CAS_Texture takes integer s, string path, real x, real y, real w, real h returns framehandle
    local framehandle f = BlzCreateFrameByType("BACKDROP","CasinoArt",CAS_root[s],"",s)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetTexture(f,path,0,true)
    return f
endfunction

function CAS_Tone takes integer id returns integer
    if id == 6 or id == 10 or id == 37 or id == 38 then
        return 1
    elseif id == 7 or id == 8 or id == 9 or id == 11 or id == 14 or id == 32 or id == 33 or id == 36 then
        return 2
    elseif id == 12 then
        return 3
    elseif id == 15 or id == 16 or id == 34 or id == 35 then
        return 4
    endif
    return 0
endfunction

function CAS_Button takes integer s, integer id, trigger click, real x, real y, real w, string label returns nothing
    local framehandle f = CUI_Create(CAS_root[s],s*40+id,CAS_SafeX(x),-y,CAS_SafeW(w),0.027,label,CAS_Tone(id))
    call BlzTriggerRegisterFrameEvent(click,f,FRAMEEVENT_CONTROL_CLICK)
    set CAS_button[s*40+id] = f
    set f = null
endfunction

function CAS_ShowButton takes integer s, integer id, boolean enabled returns nothing
    call BlzFrameSetVisible(CAS_button[s*40+id],true)
    call CUI_Paint(CAS_button[s*40+id],CAS_Tone(id),enabled)
endfunction

function CAS_CardFace takes framehandle f, integer card, boolean back returns nothing
    local string name = "empty"
    if back then
        set name = "back"
    elseif card >= 0 then
        set name = "card"+I2S(card)
    endif
    call BlzFrameSetVisible(f,true)
    call BlzFrameSetTexture(f,"PokerUI\\"+name+".blp",0,true)
endfunction

function BJ_Summary takes integer h returns string
    local string text = I2S(BJ_total[h])
    if BJ_total[h] > 21 then
        return "|cffff9090BUST "+text+"|r"
    elseif BJ_state[h] == 4 then
        return "|cffe7cb88BLACKJACK|r"
    elseif BJ_state[h] == 1 then
        return text
    elseif BJ_state[h] == 0 then
        return "--"
    endif
    return text
endfunction

function CAS_BlackjackView takes integer s returns nothing
    local integer t = BJ_table[s]
    local integer h = BJ_seat[s]*2
    local integer b = s*32
    local integer c = s*18
    local integer i = 0
    local integer j
    local integer own
    local integer card
    local real startX
    local real cardWidth = 0.060
    local real cardHeight = 0.082
    local real spacing = 0.067
    local boolean turn = BJ_phase[t] == 2 and BJ_turn[t]-1 >= h and BJ_turn[t]-1 <= h+1
    local string mode = "SOLO + BOTS"
    local string phase = "PLACE BET"
    local string dealer = "DEALER"
    if t == 0 then
        set mode = "COMMUNITY"
    endif
    if BJ_phase[t] == 1 then
        set phase = "DEAL IN "+I2S(BJ_clock[t])+"s"
    elseif BJ_phase[t] == 2 then
        set phase = CAS_Name(BJ_owner[(BJ_turn[t]-1)/2])+" / "+I2S(BJ_clock[t])+"s"
        if turn then
            set phase = "|cffe7cb88YOUR TURN / "+I2S(BJ_clock[t])+"s|r"
        endif
    elseif BJ_phase[t] == 3 then
        set phase = "DEALER'S TURN"
    elseif BJ_phase[t] == 4 then
        set phase = "NEXT ROUND"
    endif
    call BlzFrameSetText(CAS_content[b],mode+"  /  #"+I2S(BJ_round[t]))
    call BlzFrameSetVisible(CAS_content[b],true)
    call BlzFrameSetText(CAS_content[b+1],phase)
    call BlzFrameSetSize(CAS_content[b+1],CAS_SafeW(0.17),0.035)
    call BlzFrameSetVisible(CAS_content[b+1],true)
    if BJ_reveal[t] then
        set dealer = dealer+" / "+I2S(BJ_dealerTotal[t])
    endif
    call BlzFrameSetText(CAS_content[b+2],dealer)
    call BlzFrameSetVisible(CAS_content[b+2],true)
    call BlzFrameSetText(CAS_content[b+3],"|cffe7cb88YOU  "+BJ_Summary(h)+"|r|nBET "+I2S(BJ_bet[h]))
    call BlzFrameSetVisible(CAS_content[b+3],true)
    call BlzFrameSetText(CAS_content[b+4],"2 DECKS|nPAYS 3:2")
    call BlzFrameSetVisible(CAS_content[b+4],true)
    loop
        exitwhen i >= 6
        set startX = 0.435-I2R(IMaxBJ(2,IMinBJ(6,BJ_dealerCount[t])))*0.067/2.0
        call BlzFrameSetPoint(CAS_card[c+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,startX+I2R(i)*0.067,-0.164)
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
        set startX = 0.435-I2R(IMaxBJ(2,IMinBJ(6,BJ_count[h])))*0.067/2.0
        if BJ_split[h] then
            set startX = 0.205
            set cardWidth = 0.043
            set cardHeight = 0.062
            set spacing = 0.028
        endif
        call BlzFrameSetPoint(CAS_card[c+6+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,startX+I2R(i)*spacing,-0.280)
        call BlzFrameSetSize(CAS_card[c+6+i],cardWidth,cardHeight)
        call CAS_CardFace(CAS_card[c+6+i],card,false)
        call BlzFrameSetVisible(CAS_card[c+6+i],i < IMaxBJ(2,BJ_count[h]))
        if BJ_split[h] then
            set card = -1
            if i < BJ_count[h+1] then
                set card = BJ_card[(h+1)*22+i]
            endif
            call CAS_CardFace(CAS_card[c+12+i],card,false)
            call BlzFrameSetVisible(CAS_card[c+12+i],i < IMaxBJ(2,BJ_count[h+1]))
        endif
        set own = BJ_owner[t*6+i]
        set j = (t*6+i)*2
        if own == 0 then
            set phase = "OPEN"
        else
            set phase = CAS_Name(own)+" / "+BJ_Summary(j)
            if BJ_split[j] then
                set phase = phase+" + "+BJ_Summary(j+1)
            endif
        endif
        call BlzFrameSetVisible(CAS_row[s*6+i],true)
        call BlzFrameSetText(CAS_row[s*6+i],phase)
        set i = i+1
    endloop
    if BJ_split[h] then
        call BlzFrameSetText(CAS_content[b+5],"HAND 2 / "+BJ_Summary(h+1))
        call BlzFrameSetVisible(CAS_content[b+5],true)
    endif
    if BJ_count[h] > 6 or BJ_count[h+1] > 6 or BJ_dealerCount[t] > 6 then
        call BlzFrameSetPoint(CAS_content[b+6],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,CAS_SafeX(0.19),-0.252)
        call BlzFrameSetText(CAS_content[b+6],"6 cards shown / full total counted")
        call BlzFrameSetVisible(CAS_content[b+6],true)
    endif
    call BlzFrameSetVisible(CAS_chip[s],true)
    call PK_ChipArt(CAS_chip[s],BJ_bet[h]+BJ_bet[h+1])
    call CAS_ShowButton(s,11,BJ_phase[t] == 0 or BJ_phase[t] == 4 or (BJ_phase[t] == 1 and BJ_bet[h] == 0))
    call CAS_ShowButton(s,12,turn)
    call CAS_ShowButton(s,13,turn)
    call CAS_ShowButton(s,14,turn and BJ_count[BJ_turn[t]-1] == 2)
    call CAS_ShowButton(s,15,turn and not BJ_split[h] and BJ_count[h] == 2 and BJ_Value(BJ_card[h*22]) == BJ_Value(BJ_card[h*22+1]) and (ModuloInteger(BJ_card[h*22],13) == 12) == (ModuloInteger(BJ_card[h*22+1],13) == 12))
    call CAS_ShowButton(s,16,BJ_phase[t] == 0 or BJ_phase[t] == 4 or BJ_bet[h] == 0)
    if t == 0 then
        call CUI_Text(CAS_button[s*40+16],"Solo")
    else
        call CUI_Text(CAS_button[s*40+16],"Community")
    endif
endfunction

function CAS_BetsView takes integer s returns nothing
    local integer m = MK_tab[s]
    local integer o
    local integer i = 0
    local integer k = 0
    local integer b = s*32
    local integer start = MK_page[s]*6
    local integer quote
    local integer volume
    local integer total = MK_volume[m]
    local integer tickets = 0
    local integer invested = 0
    local integer totalReturn = 0
    local string label
    call BlzFrameSetText(CAS_content[b+7],"|cffe7cb88"+MK_Title(m)+"|r  /  "+I2S(total)+"g")
    call BlzFrameSetVisible(CAS_content[b+7],true)
    call BlzFrameSetText(CAS_content[b+8],"OUTCOME")
    call BlzFrameSetVisible(CAS_content[b+8],true)
    call BlzFrameSetText(CAS_content[b+31],"POOL")
    call BlzFrameSetVisible(CAS_content[b+31],true)
    call BlzFrameSetPoint(CAS_content[b+6],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,CAS_SafeX(0.445),-0.169)
    call BlzFrameSetSize(CAS_content[b+6],CAS_SafeW(0.10),0.018)
    call BlzFrameSetText(CAS_content[b+6],"ODDS")
    call BlzFrameSetVisible(CAS_content[b+6],true)
    set o = 1
    loop
        exitwhen o > 12
        if MK_Valid(m,o) then
            if k >= start and i < 6 then
                set volume = MK_pool[m*16+o]
                set label = MK_Label(m,o)
                if o == MK_pick[s] then
                    set label = "|cffe7cb88> "+label+"|r"
                endif
                call BlzFrameSetText(CAS_content[b+10+i*3],label)
                call BlzFrameSetText(CAS_content[b+11+i*3],I2S(volume)+"g / "+I2S(R2I(I2R(volume)*100.0/I2R(IMaxBJ(1,total))))+"%")
                set quote = MK_Quote(m,o,0)
                set label = CAS_Odds(quote)
                if m == 2 and MK_baseScored[o] then
                    set label = "SCORED"
                elseif MK_done[m] then
                    set label = "SETTLED"
                    if m == 2 then
                        set label = "NO KILL"
                    elseif MK_winner[m] == o then
                        set label = "|cffe7cb88WINNER|r"
                    endif
                elseif CAS_closed or CAS_seconds >= 130 then
                    set label = "CLOSED"
                endif
                call BlzFrameSetText(CAS_content[b+12+i*3],label)
                call BlzFrameSetVisible(CAS_content[b+10+i*3],true)
                call BlzFrameSetVisible(CAS_content[b+11+i*3],true)
                call BlzFrameSetVisible(CAS_content[b+12+i*3],true)
                call BlzFrameSetVisible(CAS_track[s*6+i],true)
                call BlzFrameSetVisible(CAS_bar[s*6+i],volume > 0)
                call BlzFrameSetSize(CAS_bar[s*6+i],IMaxBJ(1,volume)*CAS_SafeW(0.115)/I2R(IMaxBJ(1,total)),0.003)
                call CAS_ShowButton(s,26+i,true)
                call CUI_Text(CAS_button[s*40+26+i],"PICK")
                if o == MK_pick[s] then
                    call CUI_Paint(CAS_button[s*40+26+i],5,true)
                endif
                set i = i+1
            endif
            set k = k+1
        endif
        set o = o+1
    endloop
    set invested = MK_ownedStake[s*96+m*16+MK_pick[s]]
    set totalReturn = MK_ownedReturn[s*96+m*16+MK_pick[s]]
    set label = "PICK AN OUTCOME"
    if MK_Valid(m,MK_pick[s]) then
        set quote = MK_Quote(m,MK_pick[s],CAS_amount[s])
        set label = MK_Label(m,MK_pick[s])+"  "+CAS_Odds(quote)+"  /  RETURN "+I2S(CAS_amount[s]*quote/100)+"g"
        if invested > 0 then
            set label = label+"|nLOCKED "+I2S(invested)+"g  /  RETURN "+I2S(totalReturn)+"g"
        endif
    endif
    call BlzFrameSetText(CAS_content[b+9],label)
    call BlzFrameSetVisible(CAS_content[b+9],true)
    set i = 20
    loop
        exitwhen i > 24
        call CAS_ShowButton(s,i,true)
        if i-19 == m then
            call CUI_Paint(CAS_button[s*40+i],4,true)
        endif
        set i = i+1
    endloop
    call CAS_ShowButton(s,25,k > 6)
    call CAS_ShowButton(s,32,MK_IsOpen(m,MK_pick[s]))
endfunction

function CAS_DuelsView takes integer s returns nothing
    local integer b = s*32
    local integer id = DU_incoming[s]
    local string label = "PICK A PLAYER + WINNER|nEqual stakes. Both must accept."
    if DU_active[s] > 0 then
        set id = DU_active[s]
        set label = "|cffe7cb88LIVE / POT "+I2S(DU_stake[id]*2)+"g|r|n"+CAS_Name(DU_from[id])+": "+MK_Label(5,DU_target[id])+" WINS|n"+CAS_Name(DU_to[id])+": DOES NOT WIN"
    elseif id > 0 then
        set label = "|cffe7cb88FROM "+CAS_Name(DU_from[id])+"|r|nThey back "+MK_Label(5,DU_target[id])+" TO WIN.|nYou back DOES NOT WIN / "+I2S(DU_stake[id])+"g|nPOT "+I2S(DU_stake[id]*2)+"g / "+I2S(IMaxBJ(0,DU_expire[id]-CAS_seconds))+"s"
    elseif DU_outgoing[s] > 0 then
        set id = DU_outgoing[s]
        set label = "|cffe7cb88WAITING / "+I2S(IMaxBJ(0,DU_expire[id]-CAS_seconds))+"s|r|n"+CAS_Name(DU_to[id])+"|nYou back "+MK_Label(5,DU_target[id])+" TO WIN|nHELD "+I2S(DU_stake[id])+"g"
    endif
    call BlzFrameSetText(CAS_content[b+28],label)
    call BlzFrameSetVisible(CAS_content[b+28],true)
    call BlzFrameSetText(CAS_content[b+29],"VS "+CAS_Name(DU_opponent[s])+"  /  BACK "+MK_Label(5,DU_pick[s]))
    call BlzFrameSetVisible(CAS_content[b+29],true)
    call CAS_ShowButton(s,33,DU_active[s] == 0 and DU_outgoing[s] == 0 and CAS_User(DU_opponent[s]) and MK_Valid(5,DU_pick[s]) and not CAS_ended)
    call CAS_ShowButton(s,34,DU_active[s] == 0)
    call CAS_ShowButton(s,35,DU_active[s] == 0)
    call CAS_ShowButton(s,36,DU_incoming[s] > 0 and DU_active[s] == 0 and not CAS_ended)
    call CAS_ShowButton(s,37,DU_incoming[s] > 0)
    call CAS_ShowButton(s,38,DU_outgoing[s] > 0)
endfunction

function CAS_Render takes integer s returns nothing
    local integer i = 0
    local integer b = s*32
    local string label = "|cffe7cb88RULES|r"
    if CAS_root[s] == null then
        return
    endif
    if GetLocalPlayer() == Player(s-1) then
        call BlzFrameSetVisible(CAS_root[s],CAS_view[s] > 0)
    endif
    if CAS_view[s] == 0 then
        return
    endif
    set i = 0
    loop
        exitwhen i > 3
        if i+1 == CAS_view[s] then
            call CUI_Paint(CAS_button[s*40+i],5,true)
        else
            call CUI_Paint(CAS_button[s*40+i],0,true)
        endif
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 32
        if CAS_content[b+i] != null then
            call BlzFrameSetVisible(CAS_content[b+i],false)
        endif
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 18
        call BlzFrameSetVisible(CAS_card[s*18+i],false)
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 6
        call BlzFrameSetVisible(CAS_row[s*6+i],false)
        call BlzFrameSetVisible(CAS_track[s*6+i],false)
        call BlzFrameSetVisible(CAS_bar[s*6+i],false)
        set i = i+1
    endloop
    set i = 11
    loop
        exitwhen i >= 40
        if CAS_button[s*40+i] != null then
            call BlzFrameSetVisible(CAS_button[s*40+i],false)
        endif
        set i = i+1
    endloop
    call BlzFrameSetVisible(CAS_chip[s],false)
    if CAS_view[s] == 1 then
        call BlzFrameSetTexture(CAS_root[s],"PokerUI\\table.blp",0,true)
        set label = "|cffe7cb88BLACKJACK|r"
        call CAS_BlackjackView(s)
    elseif CAS_view[s] == 2 then
        call BlzFrameSetTexture(CAS_root[s],"CasinoUI\\panel.blp",0,true)
        set label = "|cffe7cb88MATCH BETS|r"
        call CAS_BetsView(s)
    elseif CAS_view[s] == 3 then
        call BlzFrameSetTexture(CAS_root[s],"CasinoUI\\panel.blp",0,true)
        set label = "|cffe7cb88CHALLENGES|r"
        call CAS_DuelsView(s)
    else
        call BlzFrameSetTexture(CAS_root[s],"CasinoUI\\panel.blp",0,true)
        call BlzFrameSetVisible(CAS_content[b+30],true)
        call BlzFrameSetText(CAS_content[b+30],"|cffe7cb88BLACKJACK|r|n2 decks / S17 / blackjack 3:2 / win 1:1 / ties push|nDouble first 2 cards. Split once. Split aces: 1 card.|nSplit 21 pays 1:1. Timeout stands. No insurance/surrender.|n|n|cffe7cb88MATCH BETS|r|nClose 2:10 / warning 2:00 / accepted odds stay locked|nBase kill: any enemy base. No first event or draw: refund.|n|n|cffe7cb88CHALLENGES|r|nEqual stakes. Accept to back the opposite result.|n|n|cffe7cb88GOLD|r|nStakes held. Profits repay debt. Local saves: quit/crash risk.")
    endif
    call BlzFrameSetText(CAS_title[s],label)
    set label = "LOADING GOLD"
    if FGA_ready[s] then
        set label = "GOLD "+I2S(FGA_gold[s])
        if CAS_escrow[s] > 0 then
            set label = label+"  /  HELD "+I2S(CAS_escrow[s])
        endif
        if FGA_debt[s] > 0 then
            set label = label+"  /  DEBT "+I2S(FGA_debt[s])
        endif
        if CAS_returnDue[s]+CAS_profitDue[s] > 0 then
            set label = label+"  /  CREDIT "+I2S(CAS_returnDue[s]+CAS_profitDue[s])
        endif
    endif
    call BlzFrameSetText(CAS_balance[s],label)
    set label = "BET "+I2S(CAS_amount[s])+"g"
    if CAS_ended then
        set label = label+"  /  SETTLED"
    elseif CAS_closed or CAS_seconds >= 130 then
        set label = label+"  /  BETS CLOSED"
    else
        set label = label+"  /  CLOSE "+I2S(130-CAS_seconds)+"s"
    endif
    call BlzFrameSetText(CAS_status[s],label)
    call BlzFrameSetText(CAS_footer[s],CAS_note[s])
endfunction

function CAS_CycleTarget takes integer current returns integer
    local integer i = 0
    loop
        exitwhen i >= 12
        set current = ModuloInteger(current,12)+1
        if MK_Valid(5,current) then
            return current
        endif
        set i = i+1
    endloop
    return 0
endfunction

function CAS_Click takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local framehandle f = BlzGetTriggerFrame()
    local integer id = 0
    local integer i
    local integer count
    local integer target
    loop
        exitwhen id >= 40 or CAS_button[s*40+id] == f
        set id = id+1
    endloop
    if f == CAS_launch[s] then
        set CAS_view[s] = 1
    elseif id <= 3 then
        set CAS_view[s] = id+1
    elseif id == 4 then
        set CAS_view[s] = 0
    elseif id == 5 then
        if PK_Started[s-1] then
            set CAS_view[s] = 0
            set PK_Hidden[s-1] = false
            call PK_Render(s-1)
        else
            set CAS_note[s] = "Poker practice is available in custom observer slots."
        endif
    elseif id == 6 then
        set CAS_amount[s] = IMaxBJ(10,CAS_amount[s]-10)
    elseif id == 7 then
        set CAS_amount[s] = IMinBJ(10000,CAS_amount[s]+10)
    elseif id == 8 then
        set CAS_amount[s] = IMinBJ(10000,CAS_amount[s]+50)
    elseif id == 9 then
        set CAS_amount[s] = IMinBJ(10000,CAS_amount[s]*2)
    elseif id == 10 then
        set CAS_amount[s] = IMaxBJ(10,CAS_amount[s]/20*10)
    elseif id == 11 then
        call BJ_Wager(s)
    elseif id >= 12 and id <= 15 then
        call BJ_Action(s,id-11)
    elseif id == 16 then
        call BJ_Move(s,BJ_table[s] != 0)
    elseif id >= 20 and id <= 24 then
        set MK_tab[s] = id-19
        set MK_page[s] = 0
        set MK_pick[s] = 0
    elseif id == 25 then
        set MK_page[s] = 1-MK_page[s]
    elseif id >= 26 and id <= 31 then
        set i = 1
        set count = 0
        set target = MK_page[s]*6+id-26
        loop
            exitwhen i > 12
            if MK_Valid(MK_tab[s],i) then
                if count == target then
                    set MK_pick[s] = i
                endif
                set count = count+1
            endif
            set i = i+1
        endloop
    elseif id == 32 then
        call MK_Buy(s,MK_tab[s],MK_pick[s])
    elseif id == 33 then
        call DU_Offer(s)
    elseif id == 34 then
        set i = 0
        loop
            exitwhen i >= 24
            set DU_opponent[s] = ModuloInteger(DU_opponent[s],24)+1
            exitwhen DU_opponent[s] != s and CAS_User(DU_opponent[s])
            set i = i+1
        endloop
    elseif id == 35 then
        set DU_pick[s] = CAS_CycleTarget(DU_pick[s])
    elseif id == 36 then
        call DU_Accept(s)
    elseif id == 37 then
        call DU_Cancel(DU_incoming[s])
    elseif id == 38 then
        call DU_Cancel(DU_outgoing[s])
    endif
    if CAS_view[s] > 0 and PK_Started[s-1] then
        set PK_Hidden[s-1] = true
        call PK_Render(s-1)
    endif
    call CAS_Render(s)
    set f = null
endfunction

function CAS_Chat takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local string line = GetEventPlayerChatString()
    local string amount
    local integer value
    if line == "-casino" or line == "-blackjack" then
        set CAS_view[s] = 1
    elseif line == "-bets" then
        set CAS_view[s] = 2
    elseif line == "-challenges" then
        set CAS_view[s] = 3
    elseif SubString(line,0,7) == "-stake " then
        set amount = SubString(line,7,StringLength(line))
        set value = S2I(amount)
        if FGA_Number(amount) and value >= 10 and value <= 10000 and ModuloInteger(value,2) == 0 then
            set CAS_amount[s] = value
            set CAS_note[s] = "Wager set to "+I2S(value)+" gold."
        else
            set CAS_note[s] = "Use -stake EVEN_AMOUNT, from 10 to 10000."
        endif
    endif
    if CAS_view[s] > 0 and PK_Started[s-1] then
        set PK_Hidden[s-1] = true
        call PK_Render(s-1)
    endif
    call CAS_Render(s)
endfunction
