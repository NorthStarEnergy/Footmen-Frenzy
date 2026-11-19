function BJ_SeatCount takes nothing returns integer
    local integer v = 0
    local integer count = 0
    loop
        exitwhen v >= 24
        if BJ_bet[v*2] > 0 then
            set count = count+1
        endif
        set v = v+1
    endloop
    return count
endfunction

function BJ_Roster takes integer s returns nothing
    local integer v = 0
    local integer seen = 0
    local integer row = 0
    local integer count = BJ_SeatCount()
    local integer pages = IMaxBJ(1,(count+5)/6)
    local integer page = ModuloInteger(BJ_Page[s],pages)
    local integer h
    local string name
    local string total
    loop
        exitwhen v >= 24
        set h = v*2
        if BJ_bet[h] > 0 then
            if seen/6 == page then
                set row = s*6+ModuloInteger(seen,6)
                set name = SubString(CAS_Name(v+1),0,16)
                if BJ_phase[0] == 2 and (BJ_turn[0]-1)/2 == v then
                    set name = "|cff8cf2ac> "+name+"|r"
                endif
                call BlzFrameSetVisible(CAS_row[row],true)
                call BlzFrameSetText(CAS_row[row],name)
                if BJ_phase[0] == 1 then
                    set total = I2S(BJ_bet[h])+"g"
                else
                    set total = BJ_SeatTotal(h)
                    if BJ_split[h] then
                        set total = total+"/"+BJ_SeatTotal(h+1)
                    endif
                endif
                call BlzFrameSetVisible(CAS_seatTotal[row],true)
                call BlzFrameSetText(CAS_seatTotal[row],total)
            endif
            set seen = seen+1
        endif
        set v = v+1
    endloop
    call CAS_ShowButton(s,16,pages > 1)
    call CUI_Text(CAS_button[s*64+16],"Seats "+I2S(page+1)+"/"+I2S(pages)+" >")
endfunction
