function PF_Economy takes integer s, integer i returns integer
    if s > 12 or not FF_gr_participant[s] then
        return 0
    endif
    if i == 0 then
        return 1
    elseif i == 1 then
        if FFR4Pro then
            return 1
        endif
        return 0
    elseif i == 2 then
        return PF_Number(s,PF_poolOutMetric)
    elseif i == 3 then
        return PF_Number(s,PF_poolInMetric)
    elseif i == 4 then
        return PF_Number(s,PF_sentMetric)
    elseif i == 5 then
        return PF_Number(s,PF_receivedMetric)
    elseif FFR4Pro then
        if i == 6 then
            return PF_Number(s,PF_poolOutMetric)
        endif
        return PF_Number(s,PF_poolInMetric)
    endif
    return 0
endfunction

function PF_EconomyFile takes integer s returns nothing
    local string path = PF_CareerPath(0,0)
    local string data = "E1"
    local string saved
    local integer i = 0
    if not PF_careerReady then
        set saved = s__File_readAndClose(s__File_open(path))
        if StringLength(saved) == 82 and SubString(saved,0,2) == "E1" then
            loop
                exitwhen i == 8
                set PF_priorEco[i] = S2I(SubString(saved,2+i*10,12+i*10))
                set i = i+1
            endloop
        endif
    endif
    set i = 0
    loop
        exitwhen i == 8
        set data = data+DPS_Field(PF_priorEco[i]+PF_Economy(s,i))
        set i = i+1
    endloop
    if data != PF_lastEco then
        call s__File_close(s__File_write(s__File_open(path),data))
        set PF_lastEco = data
    endif
endfunction

// Share only numeric career baselines. The receiving client associates each message with
// its actual sender; match-authoritative statistics never consume these reported values.
function PF_ReceiveHistory takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local string data = BlzGetTriggerSyncData()
    local integer kind = S2I(SubString(data,0,1))
    local integer ix = 1
    local integer id
    local integer amount
    local integer key = 3000+s*10+kind
    if kind < 0 or kind > 4 or StringLength(data) > 201 or ModuloInteger(StringLength(data)-1,20) != 0 then
        return
    endif
    loop
        exitwhen ix+20 > StringLength(data)
        set id = S2I(SubString(data,ix,ix+10))
        set amount = S2I(SubString(data,ix+10,ix+20))
        if id >= 0 and amount >= 0 and DPS_Field(id)+DPS_Field(amount) == SubString(data,ix,ix+20) and not HaveSavedInteger(PF_history,key,id) and PF_historyN[s*5+kind] < 4096 then
            call SaveInteger(PF_history,key,id,amount)
            call SaveInteger(PF_history,key+500,PF_historyN[s*5+kind],id)
            set PF_historyN[s*5+kind] = PF_historyN[s*5+kind]+1
            set PF_dirty = true
        endif
        set ix = ix+20
    endloop
endfunction

function PF_SendHistory takes nothing returns nothing
    local string data
    local integer id
    local integer amount
    local integer n = 0
    local integer s = PF_MySlot()
    if not PF_careerReady or PF_sendKind > 4 or (GetPlayerId(GetLocalPlayer()) < 12 and not DPS_ProfileLoaded and not IsPlayerObserver(GetLocalPlayer()) and GetPlayerController(GetLocalPlayer()) == MAP_CONTROL_USER) then
        return
    endif
    set data = I2S(PF_sendKind)
    if PF_sendKind == 0 then
        loop
            exitwhen n == 8 or PF_sendIndex == 16
            set id = PF_sendIndex
            if id < 8 then
                set amount = PF_priorEco[id]
            else
                set amount = DPS_Prior[id-8]
            endif
            set data = data+DPS_Field(id)+DPS_Field(amount)
            set PF_sendIndex = PF_sendIndex+1
            set n = n+1
        endloop
        if PF_sendIndex == 16 then
            set PF_sendKind = 1
            set PF_sendIndex = 0
        endif
    else
        loop
            exitwhen n == 8 or PF_sendIndex >= PF_careerCount[PF_sendKind]
            set id = LoadInteger(PF_local,PF_sendKind+10,PF_sendIndex)
            set amount = LoadInteger(PF_local,PF_sendKind,id)
            if amount > 0 then
                set data = data+DPS_Field(id)+DPS_Field(amount)
                set n = n+1
            endif
            set PF_sendIndex = PF_sendIndex+1
        endloop
        if PF_sendIndex >= PF_careerCount[PF_sendKind] then
            set PF_sendKind = PF_sendKind+1
            set PF_sendIndex = 0
        endif
    endif
    if StringLength(data) > 1 then
        call BlzSendSyncData("FFCareer22",data)
    endif
endfunction

function PF_CareerRecords takes integer account returns nothing
    local integer kind = 0
    local integer i
    local integer id
    local integer base
    local integer total
    local integer s = account
    local integer k
    local integer key
    local string row
    local string head
    local string field
    if WalletPlayedSlot[account-1] > 0 then
        set s = WalletPlayedSlot[account-1]
    endif
    loop
        exitwhen kind > 4
        set k = s*10+kind
        set key = 3000+account*10+kind
        set head = "career,"+I2S(account)+","+I2S(kind)+","
        set row = head
        set i = 0
        loop
            exitwhen i >= PF_historyN[account*5+kind]
            set id = LoadInteger(PF_history,key+500,i)
            set base = LoadInteger(PF_history,key,id)
            if kind == 0 then
                if id < 8 then
                    set total = base+PF_Economy(s,id)
                elseif id < 16 then
                    set total = base+PF_Number(s,PF_combatFirst+id-8)
                else
                    set total = base
                endif
            else
                set total = base+LoadInteger(PF_data,k,id)
            endif
            set field = I2S(id)+"="+I2S(total)
            if StringLength(row)+StringLength(field)+1 > FF_PRELOAD_MAX then
                call Preload(row)
                set row = head
            endif
            if row != head then
                set row = row+","
            endif
            set row = row+field
            set i = i+1
        endloop
        if kind > 0 then
            set i = 0
            loop
                exitwhen i >= PF_counts[k]
                set id = LoadInteger(PF_data,300+k,i)
                if not HaveSavedInteger(PF_history,key,id) then
                    set field = I2S(id)+"="+I2S(LoadInteger(PF_data,k,id))
                    if StringLength(row)+StringLength(field)+1 > FF_PRELOAD_MAX then
                        call Preload(row)
                        set row = head
                    endif
                    if row != head then
                        set row = row+","
                    endif
                    set row = row+field
                endif
                set i = i+1
            endloop
        endif
        if row != head then
            call Preload(row)
        endif
        set kind = kind+1
    endloop
    if HaveSavedInteger(PF_history,3000+account*10,7) then
        set key = 3000+account*10
        set base = LoadInteger(PF_history,key,6)+PF_Economy(s,6)
        set total = LoadInteger(PF_history,key,1)+PF_Economy(s,1)
        call Preload("career_pool,"+I2S(account)+",avg_pro_sent="+I2S(PF_Average(base,total))+",avg_pro_received="+I2S(PF_Average(LoadInteger(PF_history,key,7)+PF_Economy(s,7),total)))
    endif
endfunction

function PF_WriteCareer takes nothing returns nothing
    call PF_CareerRecords(PF_exportSlot)
endfunction
