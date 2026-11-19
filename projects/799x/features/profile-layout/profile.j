function PF_Row takes integer i, string title, string value, string extra, string art returns nothing
    local real x = -0.174
    local real y = 0.162+I2R(i)*0.042
    if art != "" and art != null then
        set x = -0.141
        call BlzFrameSetTexture(PF_icon[i],art,0,true)
        call BlzFrameSetVisible(PF_icon[i],true)
    endif
    call BlzFrameClearAllPoints(PF_line[i])
    call BlzFrameSetPoint(PF_line[i],FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,x,-y)
    call BlzFrameSetSize(PF_line[i],0.132-x,0.038)
    call BlzFrameSetText(PF_line[i],title)
    call BlzFrameSetText(PF_value[i],value)
    call BlzFrameSetText(PF_extra[i],extra)
    call BlzFrameSetVisible(PF_stripe[i],ModuloInteger(i,2) == 0)
endfunction

function PF_Columns takes string field, string value, string extra returns nothing
    call BlzFrameSetText(PF_col[0],field)
    call BlzFrameSetText(PF_col[1],value)
    call BlzFrameSetText(PF_col[2],extra)
endfunction

function PF_Activity takes integer s, integer r, integer ix returns nothing
    local integer k = 1000+s*10
    local integer id = LoadInteger(PF_data,k+1,ix)
    local integer gold = LoadInteger(PF_data,k+2,ix)
    local integer other = LoadInteger(PF_data,k+3,ix)
    local string name = LoadStr(PF_prices,4,StringHash(LoadStr(PF_data,k,ix)))
    local string debit = ""
    if id != 0 then
        set name = name+"  "+PF_Name(id)
    endif
    if other != 0 then
        set name = name+"  "+GetPlayerName(Player(other-1))
    endif
    if gold >= 0 then
        set debit = I2S(gold)
    endif
    call PF_Row(r,PF_Clock(LoadInteger(PF_data,k+4,ix))+"    "+name,debit,I2S(LoadInteger(PF_data,k+5,ix)),"")
endfunction

function PF_StatRow takes integer r, integer s, integer id returns nothing
    local integer amount
    local integer account = GetPlayerId(GetLocalPlayer())+1
    local string lifetime = ""
    if id >= PF_metrics then
        set amount = PF_priorEco[1]+PF_Economy(s,1)
        if id == PF_metrics then
            call PF_Row(r,"Pro matches played","",I2S(amount),"")
        elseif id == PF_metrics+1 then
            call PF_Row(r,"Average gold pooled per Pro match","",I2S(PF_Average(PF_priorEco[6]+PF_Economy(s,6),amount)),"")
        elseif id == PF_metrics+2 then
            call PF_Row(r,"Average gold received per Pro match","",I2S(PF_Average(PF_priorEco[7]+PF_Economy(s,7),amount)),"")
        elseif id == PF_metrics+3 then
            call PF_Row(r,"Total gold pooled","",I2S(PF_priorEco[2]+PF_Economy(s,2)),"")
        else
            call PF_Row(r,"Total pooled gold received","",I2S(PF_priorEco[3]+PF_Economy(s,3)),"")
        endif
    elseif id == 64 then
        call PF_Row(r,PF_label[id],HUD_WalletValue(),"","")
    else
        if id >= PF_casinoFirst then
            set s = account
        endif
        set amount = PF_Number(s,id)
        if id >= PF_combatFirst and id < PF_combatFirst+8 and DPS_ProfileLoaded and s == account then
            set lifetime = I2S(DPS_Prior[id-PF_combatFirst]+amount)
        endif
        call PF_Row(r,PF_label[id],I2S(amount),lifetime,"")
    endif
endfunction

function PF_UsageRow takes integer s, integer r, integer ix returns nothing
    local integer kind = FF_US_TECH
    local integer k
    local integer id
    local string uses
    loop
        set k = FF_us_CountKey(s,kind)
        exitwhen ix < FF_us_n[k] or kind == FF_US_TOWER
        set ix = ix-FF_us_n[k]
        if kind == FF_US_TECH then
            set kind = FF_US_SPELL
        elseif kind == FF_US_SPELL then
            set kind = FF_US_CMD
        else
            set kind = FF_US_TOWER
        endif
    endloop
    set id = LoadInteger(FF_us_ht,FF_us_OrderKey(s,kind),ix)
    set uses = I2S(LoadInteger(FF_us_ht,k,id))
    if kind == FF_US_CMD then
        call PF_Row(r,FF_us_cmd[id],FF_us_catName[kind],uses,"")
    else
        call PF_Row(r,PF_Name(id),FF_us_catName[kind],uses,PF_Art(id))
    endif
endfunction

function PF_ProfileView takes nothing returns nothing
    local integer s = PF_MySlot()
    local integer kind = PF_section
    local integer count = PF_sectionCount[kind]
    local integer i = 0
    local integer ix
    local integer id
    local integer amount
    local string empty = "No entries yet this match"
    call BlzFrameSetText(PF_title,GetPlayerName(GetLocalPlayer()))
    call BlzFrameSetText(PF_subtitle,"Player profile")
    call BlzFrameSetText(PF_sectionTitle,PF_sectionName[kind])
    call PF_Columns("Statistic","This match","Lifetime")
    if kind >= 1 and kind <= 4 then
        set count = PF_careerCount[kind]
        call PF_Columns(PF_sectionName[kind],"This match","Lifetime")
        set empty = "No entries recorded yet"
    elseif kind == 5 then
        set count = PF_logCount[s]
        call PF_Columns("Time     Action","Gold","Balance")
    elseif kind == 6 then
        call PF_Columns("Account activity","Amount","")
    elseif kind == 7 then
        set count = FF_us_n[FF_us_CountKey(s,FF_US_TECH)]+FF_us_n[FF_us_CountKey(s,FF_US_SPELL)]+FF_us_n[FF_us_CountKey(s,FF_US_CMD)]+FF_us_n[FF_us_CountKey(s,FF_US_TOWER)]
        call PF_Columns("Action","Type","Uses")
    elseif s > 12 then
        set count = 0
        set empty = "Match statistics appear when you control a player."
    elseif kind == 10 then
        call PF_Columns("Statistic","This match","")
    endif
    set PF_pages = IMaxBJ(1,(count+8)/9)
    set PF_page = IMinBJ(PF_page,PF_pages-1)
    loop
        set ix = PF_page*9+i
        exitwhen i >= 9 or ix >= count
        if kind >= 1 and kind <= 4 then
            set id = LoadInteger(PF_local,kind+10,ix)
            set amount = LoadInteger(PF_data,s*10+kind,id)
            call PF_Row(i,PF_Name(id),I2S(amount),I2S(amount+LoadInteger(PF_local,kind,id)),PF_Art(id))
        elseif kind == 5 then
            call PF_Activity(s,i,ix)
        elseif kind == 7 then
            call PF_UsageRow(s,i,ix)
        else
            call PF_StatRow(i,s,PF_metricOrder[kind*100+ix])
        endif
        set i = i+1
    endloop
    if count == 0 then
        call PF_Row(0,empty,"","","")
    endif
endfunction
