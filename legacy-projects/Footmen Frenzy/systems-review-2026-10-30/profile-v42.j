// Player-local cumulative statistics. These values are presentation-only and
// must never affect synchronized gameplay or be presented as bot records.
function FFPS_Field takes string data, integer wanted returns string
    local integer i=0
    local integer start=0
    local integer field=0
    local integer n=StringLength(data)
    loop
        exitwhen i > n
        if i == n or SubString(data,i,i+1) == "|" then
            if field == wanted then
                return SubString(data,start,i)
            endif
            set field=field+1
            set start=i+1
        endif
        set i=i+1
    endloop
    return null
endfunction

function FFPS_Number takes string s returns integer
    local integer i=0
    local integer n
    local integer digit
    local integer value=0
    if s == null then
        set FFPS_valid=false
        return 0
    endif
    set n=StringLength(s)
    if n < 1 or n > 9 then
        set FFPS_valid=false
        return 0
    endif
    loop
        exitwhen i >= n
        set digit=S2I(SubString(s,i,i+1))
        if I2S(digit) != SubString(s,i,i+1) then
            set FFPS_valid=false
            return 0
        endif
        set value=value*10+digit
        set i=i+1
    endloop
    return value
endfunction

// Reversible name-bound obfuscation and a corruption check, not cryptographic
// authentication: the map code and its constants are available to players.
function FFPS_Rotate takes string input, integer amount returns string
    local integer i=0
    local integer digit
    local string result=""
    if input == null or StringLength(input) < 1 or StringLength(input) > 9 then
        set FFPS_valid=false
        return "0"
    endif
    loop
        exitwhen i >= StringLength(input)
        set digit=S2I(SubString(input,i,i+1))
        if I2S(digit) != SubString(input,i,i+1) then
            set FFPS_valid=false
            return "0"
        endif
        set result=result+I2S(ModuloInteger(digit+amount+10,10))
        set i=i+1
    endloop
    return result
endfunction

function FFPS_Load takes nothing returns nothing
    local string name=GetPlayerName(GetLocalPlayer())
    local integer file
    local integer i=0
    local string data
    local string oldData
    local string payload="FFPS2"
    local string encoded
    local boolean legacy=false
    // The name hash is a local filename key, not a verified account identity.
    set FFPS_file="FFPlayerStats_v2_"+I2S(StringHash(name))+".pld"
    set FFPS_key=ModuloInteger(ModuloInteger(StringHash("FFPS2:"+name),9)+9,9)+1
    set FFPS_valid=s__File_ReadEnabled
    set file=s__File_open(FFPS_file)
    set data=s__File_readAndClose(file)
    set file=s__File_open("FFPlayerStats_v1_"+I2S(StringHash(name))+".pld")
    set oldData=s__File_readAndClose(file)
    if data == null or data == "" then
        set data=oldData
        set legacy=true
    endif
    if data != null and data != "" then
        if legacy then
            if FFPS_Field(data,0) != "FFPS1" or FFPS_Field(data,9) != null then
                set FFPS_valid=false
            endif
            loop
                exitwhen i >= 8
                set FFPS_total[i]=FFPS_Number(FFPS_Field(data,i+1))
                set i=i+1
            endloop
        else
            if FFPS_Field(data,0) != "FFPS2" or FFPS_Field(data,9) == null or FFPS_Field(data,10) != null then
                set FFPS_valid=false
            endif
            loop
                exitwhen i >= 8
                set encoded=FFPS_Field(data,i+1)
                if encoded == null then
                    set FFPS_valid=false
                    set encoded=""
                endif
                set payload=payload+"|"+encoded
                set FFPS_total[i]=FFPS_Number(FFPS_Rotate(encoded,-FFPS_key))
                set i=i+1
            endloop
            if FFPS_Field(data,9) != I2S(StringHash(payload+"|"+name+"|FFPS2-check")) then
                set FFPS_valid=false
            endif
        endif
    endif
    set FFPS_loaded=true
endfunction

function FFPS_Current takes integer index,integer s returns integer
    if index == 0 then
        return udg_unit_kills[s]
    elseif index == 1 then
        return udg_unit_deaths[s]
    elseif index == 2 then
        return udg_hero_kills[s]
    elseif index == 3 then
        return udg_hero_deaths[s]
    elseif index == 4 then
        return DPS_Assists[s]
    elseif index == 5 then
        return DPS_Caps[s]
    elseif index == 6 then
        return DPS_Buildings[s]
    endif
    return FF_st_tmHits[s]
endfunction

function FFPS_Snapshot takes nothing returns nothing
    local integer s=GetPlayerId(GetLocalPlayer())+1
    local integer i=0
    local integer current
    local integer delta
    local integer file
    local string data="FFPS2"
    if not FFPS_loaded then
        call FFPS_Load()
    endif
    if not FFPS_valid or s < 1 or s > 12 then
        return
    endif
    if not FF_gr_participant[s] then
        return
    endif
    loop
        exitwhen i >= 8
        set current=FFPS_Current(i,s)
        set delta=current-FFPS_seen[i]
        if delta > 0 then
            if FFPS_total[i] > 999999999-delta then
                set FFPS_valid=false
                return
            endif
            set FFPS_total[i]=FFPS_total[i]+delta
        endif
        set FFPS_seen[i]=current
        set data=data+"|"+FFPS_Rotate(I2S(FFPS_total[i]),FFPS_key)
        set i=i+1
    endloop
    set data=data+"|"+I2S(StringHash(data+"|"+GetPlayerName(GetLocalPlayer())+"|FFPS2-check"))
    set file=s__File_open(FFPS_file)
    call s__File_close(s__File_write(file,data))
endfunction

function FFPS_Display takes nothing returns nothing
    local string s
    if not FFPS_loaded then
        call FFPS_Load()
    endif
    if FFPS_valid then
        set s="|cffffcc00Your saved totals|r  Units "+I2S(FFPS_total[0])+"/"+I2S(FFPS_total[1])+"   Heroes "+I2S(FFPS_total[2])+"/"+I2S(FFPS_total[3])+"   Assists "+I2S(FFPS_total[4])+"   Hills "+I2S(FFPS_total[5])+"   Buildings "+I2S(FFPS_total[6])+"   Xmutes "+I2S(FFPS_total[7])
    else
        set s="|cffff8080Local profile unavailable; existing data was not overwritten.|r"
    endif
    call BlzFrameSetText(FFPS_text,s)
endfunction
