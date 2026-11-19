// All accesses to PF_local are client-only. No local records are used by match logic.
function PF_CareerPath takes integer kind, integer page returns string
    return "FootmenFrenzy\\799X\\collection-"+I2S(StringHash(WalletAccount))+"-"+I2S(kind)+"-"+I2S(page)+".pld"
endfunction

function PF_CareerAdd takes integer kind, integer id returns nothing
    if not HaveSavedInteger(PF_local,kind,id) then
        call SaveInteger(PF_local,kind,id,0)
        call SaveInteger(PF_local,kind+10,PF_careerCount[kind],id)
        set PF_careerCount[kind] = PF_careerCount[kind]+1
    endif
endfunction

function PF_LoadCareer takes integer kind returns nothing
    local string data
    local integer page = 0
    local integer offset
    local integer id
    local integer n
    loop
        set data = s__File_readAndClose(s__File_open(PF_CareerPath(kind,page)))
        exitwhen SubString(data,0,2) != "C1"
        set n = StringLength(data)-2
        exitwhen n < 0 or n > 800 or ModuloInteger(n,20) != 0
        set offset = 2
        loop
            exitwhen offset > n
            set id = S2I(SubString(data,offset,offset+10))
            call PF_CareerAdd(kind,id)
            call SaveInteger(PF_local,kind,id,S2I(SubString(data,offset+10,offset+20)))
            set offset = offset+20
        endloop
        exitwhen n < 800
        set page = page+1
    endloop
endfunction

function PF_SaveCareer takes integer slot, integer kind returns nothing
    local integer k = slot*10+kind
    local integer i = 0
    local integer id
    local integer page = 0
    local integer total
    local string data = "C1"
    loop
        exitwhen i >= PF_counts[k]
        call PF_CareerAdd(kind,LoadInteger(PF_data,300+k,i))
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= PF_careerCount[kind]
        set id = LoadInteger(PF_local,kind+10,i)
        set total = LoadInteger(PF_local,kind,id)+LoadInteger(PF_data,k,id)
        set data = data+DPS_Field(id)+DPS_Field(total)
        set i = i+1
        if ModuloInteger(i,40) == 0 or i == PF_careerCount[kind] then
            if data != LoadStr(PF_local,kind+20,page) then
                call s__File_close(s__File_write(s__File_open(PF_CareerPath(kind,page)),data))
                call SaveStr(PF_local,kind+20,page,data)
            endif
            set data = "C1"
            set page = page+1
        endif
    endloop
endfunction

function PF_MySlot takes nothing returns integer
    local integer slot = GetPlayerId(GetLocalPlayer())+1
    if SoloSub_playerForObserver[slot-1] > 0 then
        return SoloSub_playerForObserver[slot-1]
    endif
    return slot
endfunction

function PF_UpdateCareer takes nothing returns nothing
    local integer kind = 1
    local integer s = PF_MySlot()
    if WalletAccount == null or WalletAccount == "" or FF_IsBotName(WalletAccount) then
        return
    endif
    loop
        exitwhen kind > 4
        if not PF_careerReady then
            call PF_LoadCareer(kind)
        endif
        call PF_SaveCareer(s,kind)
        set kind = kind+1
    endloop
    call PF_EconomyFile(s)
    set PF_careerReady = true
endfunction
