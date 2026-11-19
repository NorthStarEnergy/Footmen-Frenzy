function PF_Number takes integer s, integer k returns integer
    if PF_frozen then
        return LoadInteger(PF_final, s, k)
    endif
    return PF_Live(s,k)
endfunction

function PF_CasinoSlot takes integer s returns integer
    if s <= 12 and SoloSub_observerForPlayer[s] > 0 then
        return SoloSub_observerForPlayer[s]
    endif
    return s
endfunction

function PF_Category takes integer kind returns string
    if kind == 1 then
        return "hero"
    elseif kind == 2 then
        return "item"
    elseif kind == 3 then
        return "unit"
    endif
    return "skin"
endfunction

function PF_ExportJournal takes nothing returns nothing
    local integer s = PF_exportSlot
    local integer k = 1000+s*10
    local integer i = PF_exportStart
    local integer stop = IMinBJ(i+64,PF_logCount[s])
    loop
        exitwhen i >= stop
        call Preload("build,"+I2S(s)+","+I2S(i+1)+","+I2S(LoadInteger(PF_data,k+4,i))+","+LoadStr(PF_data,k,i)+","+I2S(LoadInteger(PF_data,k+1,i))+","+I2S(LoadInteger(PF_data,k+2,i))+","+I2S(LoadInteger(PF_data,k+3,i))+","+I2S(LoadInteger(PF_data,k+5,i)))
        set i = i+1
    endloop
endfunction

function PF_ExportSlot takes nothing returns nothing
    local integer s = PF_exportSlot
    local integer i = 0
    local integer kind = 1
    local integer k
    local integer id
    local string head = "profile,"+I2S(s)+","
    local string row = head
    local string field
    if not FF_gr_participant[s] then
        set i = PF_casinoFirst
    endif
    loop
        exitwhen i >= PF_metrics
        set field = PF_key[i]+"="+I2S(PF_Number(s,i))
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
    call Preload(row)
    loop
        exitwhen kind > 4
        set k = s*10+kind
        set i = 0
        set head = "collection,"+I2S(s)+","+PF_Category(kind)+","
        set row = head
        loop
            exitwhen i >= PF_counts[k]
            set id = LoadInteger(PF_data,300+k,i)
            set field = FF_us_Id2S(id)+"="+I2S(LoadInteger(PF_data,k,id))
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
        if row != head then
            call Preload(row)
        endif
        set kind = kind+1
    endloop
    set PF_exportStart = 0
    loop
        exitwhen PF_exportStart >= PF_logCount[s]
        call ExecuteFunc("PF_ExportJournal")
        set PF_exportStart = PF_exportStart+64
    endloop
endfunction

function PF_Export takes nothing returns nothing
    set PF_exportSlot = 1
    loop
        exitwhen PF_exportSlot > 24
        if FF_gr_participant[PF_exportSlot] or PF_wagers[PF_exportSlot] > 0 or WalletPlayedSlot[PF_exportSlot-1] > 0 then
            call Preload("profile_owner,"+I2S(PF_exportSlot)+","+FF_Sanitize(GetPlayerName(Player(PF_exportSlot-1)))+","+I2S(PF_CasinoSlot(PF_exportSlot)))
            call ExecuteFunc("PF_ExportSlot")
            call ExecuteFunc("PF_WriteCareer")
        endif
        set PF_exportSlot = PF_exportSlot+1
    endloop
endfunction
