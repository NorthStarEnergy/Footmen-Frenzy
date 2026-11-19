function PK_Tick takes nothing returns nothing
    local integer v = 0
    if CAS_ended then
        return
    endif
    loop
        exitwhen v >= 24
        if PokerBuyIn[v] > 0 and not PK_Eligible(v) then
            call OP_Leave(v)
        endif
        set v = v+1
    endloop
    if OP_Phase == 0 then
        if OP_Seats >= 2 then
            set OP_Clock = OP_Clock-1
            if OP_Clock <= 0 then
                call OP_Deal()
            endif
        else
            set OP_Clock = 8
        endif
    elseif OP_Phase == 1 then
        set v = OP_Turn
        set OP_Clock = OP_Clock-1
        if OP_Leaving[v] then
            call OP_Action(v,"f",0)
        elseif OP_Clock <= 0 then
            // An absent player cannot keep posting blinds hand after hand.
            set OP_Leaving[v] = true
            if PK_Paid[v] == OP_Bet then
                call OP_Action(v,"c",0)
            else
                call OP_Action(v,"f",0)
            endif
        endif
    endif
    call OP_Refresh()
endfunction
