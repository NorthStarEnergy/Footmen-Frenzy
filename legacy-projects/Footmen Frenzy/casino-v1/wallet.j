// All gameplay state runs on every client. Local branches only show UI / save files.
function CAS_Random takes integer bound returns integer
    local integer hi = CAS_seed / 127773
    local integer lo = ModuloInteger(CAS_seed,127773)
    set CAS_seed = 16807*lo-2836*hi
    if CAS_seed <= 0 then
        set CAS_seed = CAS_seed+2147483647
    endif
    return ModuloInteger(CAS_seed,bound)
endfunction

function CAS_User takes integer s returns boolean
    return s >= 1 and s <= 24 and GetPlayerController(Player(s-1)) == MAP_CONTROL_USER and GetPlayerSlotState(Player(s-1)) == PLAYER_SLOT_STATE_PLAYING
endfunction

function CAS_Flush takes integer s returns nothing
    local integer amount
    if not FGA_ready[s] then
        return
    endif
    set amount = IMinBJ(CAS_returnDue[s],1000000000-FGA_gold[s])
    set FGA_gold[s] = FGA_gold[s]+amount
    set CAS_returnDue[s] = CAS_returnDue[s]-amount
    set amount = IMinBJ(CAS_profitDue[s],1000000000-FGA_gold[s])
    if FGA_pending[s] <= 1000000000-amount then
        call FGA_Award(s,amount)
        set CAS_profitDue[s] = CAS_profitDue[s]-amount
    endif
endfunction

function CAS_Credit takes integer s, integer principal, integer profit returns nothing
    set CAS_returnDue[s] = CAS_returnDue[s]+principal
    set CAS_profitDue[s] = CAS_profitDue[s]+profit
    call CAS_Flush(s)
endfunction

function CAS_Reserve takes integer s, integer stake, integer liability returns boolean
    if CAS_ended or not CAS_User(s) or not FGA_ready[s] then
        set CAS_note[s] = "Account gold unavailable, or this match has ended."
        return false
    endif
    if stake < 10 or stake > 10000 or ModuloInteger(stake,2) != 0 or FGA_gold[s] < stake then
        set CAS_note[s] = "Choose a wager of 10 to 10,000 gold within your balance."
        return false
    endif
    if liability < 0 or CAS_bank-CAS_liability < liability then
        set CAS_note[s] = "This wager exceeds the remaining house backing. Try a smaller amount."
        return false
    endif
    set FGA_gold[s] = FGA_gold[s]-stake
    set CAS_escrow[s] = CAS_escrow[s]+stake
    set CAS_liability = CAS_liability+liability
    call CAS_Flush(s)
    return true
endfunction

function CAS_Settle takes integer s, integer stake, integer payout, integer liability returns nothing
    set CAS_escrow[s] = CAS_escrow[s]-stake
    set CAS_liability = CAS_liability-liability
    set CAS_bank = CAS_bank+stake-payout
    call CAS_Credit(s,IMinBJ(stake,payout),IMaxBJ(0,payout-stake))
endfunction

function CAS_Odds takes integer value returns string
    return I2S(value/100)+"."+FF_Pad2(ModuloInteger(value,100))+"x"
endfunction

function CAS_Name takes integer s returns string
    if s < 1 then
        return "Computer"
    endif
    return GetPlayerName(Player(s-1))
endfunction
