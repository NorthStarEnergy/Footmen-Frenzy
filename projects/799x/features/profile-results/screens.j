function PF_Clock takes integer seconds returns string
    return I2S(seconds/60)+":"+FF_Pad2(ModuloInteger(seconds,60))
endfunction

function PF_Text takes real x, real y, real width, real height, real font returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","",PF_root,"",0)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,x,-y)
    call BlzFrameSetSize(f,width,height)
    call BlzFrameSetFont(f,"Fonts\\FRIZQT__.TTF",font,0)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function PF_Button takes trigger t, real x, real y, real width returns framehandle
    local framehandle f = BlzCreateFrame("ScriptDialogButton",PF_root,0,0)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,x,-y)
    call BlzFrameSetSize(f,width,0.031)
    call BlzFrameSetLevel(f,101)
    call BlzTriggerRegisterFrameEvent(t,f,FRAMEEVENT_CONTROL_CLICK)
    return f
endfunction

function PF_Art takes integer id returns string
    local string art = LoadStr(PF_prices,3,id)
    if art == null or art == "" then
        set art = BlzGetAbilityIcon(id)
    endif
    if art == null or art == "" then
        return "ReplaceableTextures\\CommandButtons\\BTNSelectHeroOn.blp"
    endif
    return art
endfunction

function PF_Name takes integer id returns string
    local string name = GetObjectName(id)
    if name == null or name == "" or name == "Default string" then
        return FF_us_Id2S(id)
    endif
    return name
endfunction

function PF_Card takes integer i, string title, string detail, string art returns nothing
    call BlzFrameSetText(PF_line[i],title)
    call BlzFrameSetText(PF_value[i],detail)
    if art != "" and art != null then
        call BlzFrameSetTexture(PF_icon[i],art,0,true)
        call BlzFrameSetVisible(PF_icon[i],true)
    endif
endfunction

function PF_Paginate takes integer n returns nothing
    set PF_pages = IMaxBJ(1,(n+13)/14)
    set PF_page = IMinBJ(PF_page,PF_pages-1)
endfunction

function PF_Activity takes integer s, integer r, integer ix returns nothing
    local integer k = 1000+s*10
    local integer id = LoadInteger(PF_data,k+1,ix)
    local integer gold = LoadInteger(PF_data,k+2,ix)
    local integer other = LoadInteger(PF_data,k+3,ix)
    local string kind = LoadStr(PF_data,k,ix)
    local string name = LoadStr(PF_prices,4,StringHash(kind))
    local string art = "UI\\Widgets\\ToolTips\\Human\\ToolTipGoldIcon.blp"
    local string detail = PF_Clock(LoadInteger(PF_data,k+4,ix))
    if id != 0 then
        set name = name+"  "+PF_Name(id)
        set art = PF_Art(id)
    endif
    if other != 0 then
        set name = name+"  "+GetPlayerName(Player(other-1))
    endif
    if gold >= 0 then
        set detail = detail+"    "+I2S(gold)+" gold"
    endif
    set detail = detail+"    Balance "+I2S(LoadInteger(PF_data,k+5,ix))
    call PF_Card(r,name,detail,art)
endfunction

function PF_ProfileView takes nothing returns nothing
    local integer s = PF_MySlot()
    local integer account = GetPlayerId(GetLocalPlayer())+1
    local integer kind = PF_section
    local integer k = s*10+kind
    local integer count
    local integer i = 0
    local integer ix
    local integer id
    local integer amount
    local integer start = 0
    local string detail
    local string art
    if kind == 0 then
        set count = PF_casinoFirst+4
        if s > 12 then
            set count = 0
        endif
    elseif kind <= 4 then
        set count = PF_careerCount[kind]
    elseif kind == 5 then
        set count = PF_logCount[s]
    elseif kind == 6 then
        set start = PF_casinoFirst
        set count = PF_metrics-start
    else
        set count = FF_us_n[FF_us_CountKey(s,FF_US_TECH)]+FF_us_n[FF_us_CountKey(s,FF_US_SPELL)]+FF_us_n[FF_us_CountKey(s,FF_US_CMD)]+FF_us_n[FF_us_CountKey(s,FF_US_TOWER)]
    endif
    call PF_Paginate(count)
    call BlzFrameSetText(PF_title,"|cffffcc68Player Profile|r    "+GetPlayerName(GetLocalPlayer()))
    call BlzFrameSetText(PF_subtitle,"This match")
    if kind >= 1 and kind <= 4 then
        call BlzFrameSetText(PF_subtitle,"This match  /  Lifetime on this computer")
        if kind == 4 then
            call BlzFrameSetText(PF_subtitle,"Appearances fielded, including default skins    |    This match  /  Lifetime")
        endif
    elseif kind == 5 then
        call BlzFrameSetText(PF_subtitle,"Build order   /   Oldest first. Gold debits include trades. Purchase lines show known prices.")
    elseif kind == 6 then
        call BlzFrameSetText(PF_subtitle,"Casino and credit   /   Account gold")
    endif
    loop
        set ix = PF_page*14+i
        exitwhen i >= 14 or ix >= count
        if kind == 0 or kind == 6 then
            set id = start+ix
            if kind == 0 and id >= PF_casinoFirst then
                set amount = PF_priorEco[1]+PF_Economy(s,1)
                if id == PF_casinoFirst then
                    call PF_Card(i,"Pro matches played",I2S(amount),"")
                elseif id == PF_casinoFirst+1 then
                    call PF_Card(i,"Average gold pooled / Pro match",I2S(PF_Average(PF_priorEco[6]+PF_Economy(s,6),amount)),"")
                elseif id == PF_casinoFirst+2 then
                    call PF_Card(i,"Average gold received / Pro match",I2S(PF_Average(PF_priorEco[7]+PF_Economy(s,7),amount)),"")
                else
                    call PF_Card(i,"Lifetime pooled / received",I2S(PF_priorEco[2]+PF_Economy(s,2))+" / "+I2S(PF_priorEco[3]+PF_Economy(s,3)),"")
                endif
            else
            if kind == 6 then
                set amount = PF_Number(account,id)
            else
                set amount = PF_Number(s,id)
            endif
            set detail = I2S(amount)
            if kind == 0 and id >= PF_combatFirst and id < PF_combatFirst+8 and DPS_ProfileLoaded and s == account then
                set detail = detail+" this match    /    "+I2S(DPS_Prior[id-PF_combatFirst]+amount)+" lifetime"
            endif
            call PF_Card(i,PF_label[id],detail,"")
            endif
        elseif kind <= 4 then
            set id = LoadInteger(PF_local,kind+10,ix)
            set amount = LoadInteger(PF_data,k,id)
            set detail = I2S(amount)+" this match    /    "+I2S(amount+LoadInteger(PF_local,kind,id))+" lifetime"
            call PF_Card(i,PF_Name(id),detail,PF_Art(id))
        elseif kind == 5 then
            call PF_Activity(s,i,ix)
        else
            set id = FF_US_TECH
            loop
                set k = FF_us_CountKey(s,id)
                exitwhen ix < FF_us_n[k] or id == FF_US_TOWER
                set ix = ix-FF_us_n[k]
                if id == FF_US_TECH then
                    set id = FF_US_SPELL
                elseif id == FF_US_SPELL then
                    set id = FF_US_CMD
                else
                    set id = FF_US_TOWER
                endif
            endloop
            set amount = LoadInteger(FF_us_ht,FF_us_OrderKey(s,id),ix)
            set detail = FF_us_catName[id]+"    "+I2S(LoadInteger(FF_us_ht,k,amount))
            if id == FF_US_CMD then
                call PF_Card(i,FF_us_cmd[amount],detail,"")
            else
                call PF_Card(i,PF_Name(amount),detail,PF_Art(amount))
            endif
        endif
        set i = i+1
    endloop
    if count == 0 then
        call BlzFrameSetText(PF_line[0],"No entries yet")
    endif
endfunction

function PF_TeamValue takes integer side, integer metric returns string
    local integer s = 1
    local integer total = 0
    local integer transfers = 0
    if PF_key[metric] == "level" or PF_key[metric] == "tech" then
        return ""
    endif
    loop
        exitwhen s > 12
        if FF_gr_participant[s] and FF_gr_IsMember(s,side) then
            if PF_key[metric] == "avg_sent" then
                set total = total+PF_Number(s,PF_poolOutMetric)
                set transfers = transfers+PF_Number(s,PF_sentMetric)
            elseif PF_key[metric] == "avg_recv" then
                set total = total+PF_Number(s,PF_poolInMetric)
                set transfers = transfers+PF_Number(s,PF_receivedMetric)
            else
                set total = total+PF_Number(s,metric)
            endif
        endif
        set s = s+1
    endloop
    if PF_key[metric] == "avg_sent" or PF_key[metric] == "avg_recv" then
        set total = PF_Average(total,transfers)
    endif
    return I2S(total)
endfunction

function PF_ResultsView takes nothing returns nothing
    local integer side = 1
    local integer s
    local integer r = 1
    local integer c = 0
    local integer k
    local string title = "Match results"
    local string control = ""
    local string name
    local integer board = PF_section
    set PF_pages = 1
    if PF_section == 1 or PF_section == 3 then
        set PF_pages = 2
    elseif PF_section == 4 then
        set PF_pages = 3
    endif
    if PF_page > 0 then
        if PF_section == 1 then
            set board = 9
        elseif PF_section == 3 then
            set board = 6
        elseif PF_section == 4 then
            set board = 6+PF_page
        endif
    endif
    set s = PF_MySlot()
    if CAS_winner == 0 then
        set title = "Draw"
    elseif s <= 12 and FF_gr_participant[s] then
        if CAS_winner == -s or (CAS_winner > 0 and FF_gr_IsMember(s,CAS_winner)) then
            set title = "Victory"
        else
            set title = "Defeat"
        endif
    endif
    call BlzFrameSetText(PF_title,"|cffffcc68"+title+"|r     Footmen Frenzy")
    call BlzFrameSetText(PF_board[0],"Team  /  Player")
    loop
        exitwhen c >= 5
        call BlzFrameSetText(PF_board[c+1],PF_columnTitle[board*5+c])
        set c = c+1
    endloop
    loop
        exitwhen side > FF_gr_SideCount()
        if FF_gr_SideParticipated(side) then
            set name = FF_gr_SideLabel(side)+"   /   Total"
            if CAS_winner == side then
                set name = name+"   /   Winner"
            endif
            call BlzFrameSetText(PF_board[r*6],"|cffffcc68"+name+"|r")
            set c = 0
            loop
                exitwhen c >= 5
                call BlzFrameSetText(PF_board[r*6+c+1],"|cffffcc68"+PF_TeamValue(side,PF_columns[board*5+c])+"|r")
                set c = c+1
            endloop
            set r = r+1
            set s = 1
            loop
                exitwhen s > 12
                if FF_gr_participant[s] and FF_gr_IsMember(s,side) then
                    call BlzFrameSetVisible(PF_band[r],true)
                    call BlzFrameSetTexture(PF_band[r],PF_Color(s),0,true)
                    set name = udg_orig_player_name[s]
                    if name == null or name == "" then
                        set name = GetPlayerName(Player(s-1))
                    endif
                    if CAS_winner == -s then
                        set name = "|cffffcc68"+name+"   /   Winner|r"
                    endif
                    call BlzFrameSetText(PF_board[r*6],name)
                    if PF_lastHero[s] != 0 then
                        call BlzFrameSetTexture(PF_portrait[r],PF_Art(PF_lastHero[s]),0,true)
                        call BlzFrameSetVisible(PF_portrait[r],true)
                    endif
                    set c = 0
                    loop
                        exitwhen c >= 5
                        set k = PF_columns[board*5+c]
                        call BlzFrameSetText(PF_board[r*6+c+1],I2S(PF_Number(s,k)))
                        set c = c+1
                    endloop
                    set r = r+1
                endif
                set s = s+1
            endloop
            if PF_hillSeconds[side] > 0 then
                set control = control+"    "+FF_gr_SideLabel(side)+" "+PF_Clock(PF_hillSeconds[side])
            endif
        endif
        set side = side+1
    endloop
    if control != "" then
        set control = "     Hill control"+control
    endif
    call BlzFrameSetText(PF_subtitle,"Final standings    "+PF_Clock(PF_endSecond)+control+"    Account gold earned   "+I2S(PF_rewards[GetPlayerId(GetLocalPlayer())+1]))
endfunction

function PF_Render takes nothing returns nothing
    local integer i = 0
    if not PF_visible then
        return
    endif
    loop
        exitwhen i >= 14
        call BlzFrameSetText(PF_line[i],"")
        call BlzFrameSetText(PF_value[i],"")
        call BlzFrameSetVisible(PF_icon[i],false)
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 102
        call BlzFrameSetText(PF_board[i],"")
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 17
        call BlzFrameSetVisible(PF_band[i],false)
        call BlzFrameSetVisible(PF_portrait[i],false)
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 8
        call BlzFrameSetVisible(PF_tab[i],not PF_results or i < 6)
        if PF_results then
            call BlzFrameSetText(PF_tab[i],PF_tabName[10+i])
        else
            call BlzFrameSetText(PF_tab[i],PF_tabName[i])
        endif
        call BlzFrameSetEnable(PF_tab[i],i != PF_section)
        set i = i+1
    endloop
    if PF_results then
        call PF_ResultsView()
    else
        call PF_ProfileView()
    endif
    call BlzFrameSetVisible(PF_prev,PF_page > 0)
    call BlzFrameSetVisible(PF_next,PF_page+1 < PF_pages)
    call BlzFrameSetText(PF_footer,"")
    if PF_pages > 1 then
        call BlzFrameSetText(PF_footer,I2S(PF_page+1)+" / "+I2S(PF_pages))
    endif
    call BlzFrameSetVisible(PF_back,not PF_results)
    call BlzFrameSetVisible(PF_continue,PF_results)
    if PF_results then
        call BlzFrameSetEnable(PF_continue,PF_verdict[GetPlayerId(GetLocalPlayer())+1] != 0 or IsPlayerObserver(GetLocalPlayer()) or not FF_gr_participant[GetPlayerId(GetLocalPlayer())+1])
    endif
endfunction

function PF_Open takes boolean results returns nothing
    local integer w = BlzGetLocalClientWidth()
    local integer h = BlzGetLocalClientHeight()
    set PF_visible = true
    set PF_results = results
    set PF_section = 0
    set PF_page = 0
    if h > 0 then
        call BlzFrameSetSize(PF_root,RMaxBJ(0.8,0.6*I2R(w)/I2R(h)),0.6)
    endif
    call BlzFrameSetVisible(DPS_Panel,false)
    call BlzFrameSetVisible(PF_root,true)
    call PF_Render()
endfunction

function PF_Click takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local integer i = 0
    local framehandle f = BlzGetTriggerFrame()
    // Native dialogs allocate handles and must run on all clients.
    if f == PF_continue and PF_verdict[s] > 0 then
        if PF_verdict[s] == 1 then
            set PF_verdict[s] = -1
            call CustomVictoryBJ(GetTriggerPlayer(),true,true)
        else
            set PF_verdict[s] = -1
            call CustomDefeatBJ(GetTriggerPlayer(),PF_message[s])
        endif
    endif
    if GetLocalPlayer() == GetTriggerPlayer() then
        if f == PF_back or f == PF_continue then
            set PF_visible = false
            call BlzFrameSetVisible(PF_root,false)
            if not PF_results then
                call BlzFrameSetVisible(DPS_Panel,true)
            endif
        elseif f == PF_prev then
            set PF_page = IMaxBJ(0,PF_page-1)
        elseif f == PF_next then
            set PF_page = IMinBJ(PF_pages-1,PF_page+1)
        else
            loop
                exitwhen i >= 8
                if f == PF_tab[i] then
                    set PF_section = i
                    set PF_page = 0
                endif
                set i = i+1
            endloop
        endif
        call BlzFrameSetFocus(f,false)
        call PF_Render()
    endif
    set f = null
endfunction

function PF_Create takes nothing returns nothing
    local trigger t = CreateTrigger()
    local integer i = 0
    local integer c
    local real x
    local real y
    local real w
    set PF_root = BlzCreateFrame("EscMenuBackdrop",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),0,0)
    call BlzFrameSetLevel(PF_root,100)
    call BlzFrameSetAbsPoint(PF_root,FRAMEPOINT_TOP,0.4,0.6)
    call BlzFrameSetSize(PF_root,0.8,0.6)
    set PF_title = PF_Text(-0.365,0.020,0.59,0.033,0.021)
    set PF_subtitle = PF_Text(-0.365,0.059,0.735,0.021,0.011)
    set PF_back = PF_Button(t,0.284,0.021,0.081)
    call BlzFrameSetText(PF_back,"Back")
    set PF_continue = PF_Button(t,0.284,0.021,0.081)
    call BlzFrameSetText(PF_continue,"Continue")
    loop
        exitwhen i >= 8
        set PF_tab[i] = PF_Button(t,-0.366+I2R(i)*0.092,0.089,0.091)
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 17
        set y = 0.134+I2R(i)*0.024
        set PF_band[i] = BlzCreateFrameByType("BACKDROP","",PF_root,"",i)
        call BlzFrameSetPoint(PF_band[i],FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.364,-y)
        call BlzFrameSetSize(PF_band[i],0.728,0.022)
        call BlzFrameSetAlpha(PF_band[i],74)
        set PF_portrait[i] = BlzCreateFrameByType("BACKDROP","",PF_root,"",i)
        call BlzFrameSetPoint(PF_portrait[i],FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.361,-y)
        call BlzFrameSetSize(PF_portrait[i],0.022,0.022)
        set c = 0
        loop
            exitwhen c >= 6
            if c == 0 then
                set x = -0.333
                set w = 0.197
            else
                set x = -0.135+I2R(c-1)*0.100
                set w = 0.098
            endif
            set PF_board[i*6+c] = PF_Text(x,y,w,0.022,0.011)
            set c = c+1
        endloop
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 14
        set x = -0.362+I2R(i/7)*0.369
        set y = 0.146+I2R(ModuloInteger(i,7))*0.057
        set PF_icon[i] = BlzCreateFrameByType("BACKDROP","",PF_root,"",i)
        call BlzFrameSetPoint(PF_icon[i],FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,x,-y)
        call BlzFrameSetSize(PF_icon[i],0.039,0.039)
        set PF_line[i] = PF_Text(x+0.045,y,0.315,0.022,0.013)
        set PF_value[i] = PF_Text(x+0.045,y+0.022,0.315,0.021,0.010)
        call BlzFrameSetTextColor(PF_value[i],BlzConvertColor(255,211,188,148))
        set i = i+1
    endloop
    set PF_prev = PF_Button(t,-0.170,0.548,0.085)
    set PF_next = PF_Button(t,0.084,0.548,0.085)
    call BlzFrameSetText(PF_prev,"Previous")
    call BlzFrameSetText(PF_next,"Next")
    set PF_footer = PF_Text(-0.030,0.548,0.070,0.031,0.012)
    call TriggerAddAction(t,function PF_Click)
    call BlzFrameSetVisible(PF_root,false)
    set t = null
endfunction
