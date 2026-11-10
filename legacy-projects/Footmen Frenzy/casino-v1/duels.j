// A challenge backs a named team/player to win versus that outcome not winning.
// Both sides explicitly accept the same target and equal stake; the pot backs itself.
function DU_Cancel takes integer id returns nothing
    local integer s = DU_from[id]
    if DU_state[id] != 1 then
        return
    endif
    set DU_state[id] = 4
    set DU_outgoing[s] = 0
    set DU_incoming[DU_to[id]] = 0
    set CAS_escrow[s] = CAS_escrow[s]-DU_stake[id]
    call CAS_Credit(s,DU_stake[id],0)
    set CAS_note[s] = "Challenge declined, cancelled, or expired. Gold returned."
endfunction

function DU_Offer takes integer s returns nothing
    local integer to = DU_opponent[s]
    local integer target = DU_pick[s]
    local integer stake = CAS_amount[s]
    if not CAS_User(to) or to == s or DU_outgoing[s] != 0 or DU_incoming[to] != 0 or DU_active[s] != 0 or DU_active[to] != 0 or not MK_Valid(5,target) or DU_n >= 511 then
        set CAS_note[s] = "Choose an available opponent and a valid winner. One active challenge per player."
        return
    endif
    if not CAS_Reserve(s,stake,0) then
        return
    endif
    set DU_n = DU_n+1
    set DU_from[DU_n] = s
    set DU_to[DU_n] = to
    set DU_target[DU_n] = target
    set DU_ffa[DU_n] = MK_FFA()
    set DU_stake[DU_n] = stake
    set DU_state[DU_n] = 1
    set DU_expire[DU_n] = CAS_seconds+30
    set DU_outgoing[s] = DU_n
    set DU_incoming[to] = DU_n
    set CAS_note[s] = "Challenge sent. Your "+I2S(stake)+" gold is held for 30 seconds."
    set CAS_note[to] = CAS_Name(s)+" challenges you: "+MK_Label(5,target)+" wins, "+I2S(stake)+" gold each. Open Casino / Challenges."
    call DisplayTimedTextToPlayer(Player(to-1),0,0,15,CAS_note[to])
    call FGA_SaveLocal()
endfunction

function DU_Accept takes integer s returns nothing
    local integer id = DU_incoming[s]
    local integer proposer
    if id == 0 or DU_state[id] != 1 then
        return
    endif
    set proposer = DU_from[id]
    if CAS_seconds >= DU_expire[id] or not CAS_User(proposer) or DU_active[s] != 0 or DU_active[proposer] != 0 or DU_ffa[id] != MK_FFA() or not MK_Valid(5,DU_target[id]) then
        call DU_Cancel(id)
        return
    endif
    if not CAS_Reserve(s,DU_stake[id],0) then
        return
    endif
    set DU_state[id] = 2
    set DU_incoming[s] = 0
    set DU_outgoing[proposer] = 0
    set DU_active[s] = id
    set DU_active[proposer] = id
    set CAS_note[s] = "Accepted: you win if "+MK_Label(5,DU_target[id])+" does NOT win. Pot "+I2S(DU_stake[id]*2)+"."
    set CAS_note[proposer] = "Accepted: you win if "+MK_Label(5,DU_target[id])+" wins. Pot "+I2S(DU_stake[id]*2)+"."
    call FGA_SaveLocal()
endfunction

function DU_Finish takes integer winner, boolean ffa returns nothing
    local integer id = 1
    local integer won
    local integer stake
    loop
        exitwhen id > DU_n
        if DU_state[id] == 1 then
            call DU_Cancel(id)
        elseif DU_state[id] == 2 then
            set DU_state[id] = 3
            set stake = DU_stake[id]
            set CAS_escrow[DU_from[id]] = CAS_escrow[DU_from[id]]-stake
            set CAS_escrow[DU_to[id]] = CAS_escrow[DU_to[id]]-stake
            set DU_active[DU_from[id]] = 0
            set DU_active[DU_to[id]] = 0
            if winner == 0 or DU_ffa[id] != ffa then
                call CAS_Credit(DU_from[id],stake,0)
                call CAS_Credit(DU_to[id],stake,0)
            else
                set won = DU_to[id]
                if DU_target[id] == winner then
                    set won = DU_from[id]
                endif
                call CAS_Credit(won,stake,stake)
                set CAS_note[won] = "Challenge won: return "+I2S(stake*2)+" gold."
            endif
        endif
        set id = id+1
    endloop
endfunction

function CAS_EndMatch takes nothing returns nothing
    local integer winner = CAS_winner
    local integer m = 1
    local integer i = 1
    local boolean ffa = winner < 0
    if CAS_ended then
        return
    endif
    set CAS_ended = true
    set CAS_closed = true
    if ffa then
        set winner = -winner
    endif
    // Each market that never had an event is void; any-base-kill is a yes proposition.
    loop
        exitwhen m > 4
        if m != 2 then
            call MK_Resolve(m,0)
        endif
        set m = m+1
    endloop
    set MK_done[2] = true
    call MK_Schedule()
    // Resolve the team/player winner using the map's canonical settlement result.
    if ffa != MK_FFA() then
        call MK_Resolve(5,0)
    else
        call MK_Resolve(5,winner)
    endif
    call DU_Finish(winner,ffa)
    set i = 0
    loop
        exitwhen i > 24
        if BJ_phase[i] >= 1 and BJ_phase[i] <= 3 then
            call BJ_Finish(i,true)
        endif
        set i = i+1
    endloop
    call FGA_SaveLocal()
endfunction
