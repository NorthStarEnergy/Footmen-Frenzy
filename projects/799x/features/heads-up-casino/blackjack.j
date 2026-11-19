function BJ_Value takes integer card returns integer
    if ModuloInteger(card,13) == 12 then
        return 11
    endif
    return IMinBJ(10,ModuloInteger(card,13)+2)
endfunction

// Both seats score the physical cards from scratch, including every soft ace.
function BJ_CardSum takes integer groupId, integer count, boolean dealer returns integer
    local integer i = 0
    local integer aces = 0
    local integer total = 0
    local integer value
    loop
        exitwhen i >= count
        if dealer then
            set value = BJ_Value(BJ_dealerCard[groupId*22+i])
        else
            set value = BJ_Value(BJ_card[groupId*22+i])
        endif
        set total = total+value
        if value == 11 then
            set aces = aces+1
        endif
        set i = i+1
    endloop
    loop
        exitwhen total <= 21 or aces == 0
        set total = total-10
        set aces = aces-1
    endloop
    return total
endfunction

function BJ_Recount takes integer h returns nothing
    set BJ_total[h] = BJ_CardSum(h,BJ_count[h],false)
endfunction
