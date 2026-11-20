function CAS_DuelsView takes integer s returns nothing
    local integer b = s*32
    local integer id = DU_incoming[s]
    local string label = "PICK A PLAYER + WINNER|nEqual stakes. Both must accept."
    if DU_active[s] > 0 then
        set id = DU_active[s]
        set label = "LIVE / POT "+CUI_Value(I2S(DU_stake[id]*2)+"g")+"|n"+CAS_Name(DU_from[id])+": "+MK_Label(5,DU_target[id])+" WINS|n"+CAS_Name(DU_to[id])+": DOES NOT WIN"
    elseif id > 0 then
        set label = "|cffe7cb88FROM "+CAS_Name(DU_from[id])+"|r|nThey back "+MK_Label(5,DU_target[id])+" TO WIN.|nYou back DOES NOT WIN / "+CUI_Value(I2S(DU_stake[id])+"g")+"|nPOT "+CUI_Value(I2S(DU_stake[id]*2)+"g")+" / "+CUI_Value(I2S(IMaxBJ(0,DU_expire[id]-CAS_seconds))+"s")
    elseif DU_outgoing[s] > 0 then
        set id = DU_outgoing[s]
        set label = "WAITING / "+CUI_Value(I2S(IMaxBJ(0,DU_expire[id]-CAS_seconds))+"s")+"|n"+CAS_Name(DU_to[id])+"|nYou back "+MK_Label(5,DU_target[id])+" TO WIN|nHELD "+CUI_Value(I2S(DU_stake[id])+"g")
    endif
    call BlzFrameSetSize(CAS_content[b+28],0.650,0.115)
    call BlzFrameSetText(CAS_content[b+28],label)
    call BlzFrameSetVisible(CAS_content[b+28],true)
    call BlzFrameSetText(CAS_content[b+29],"VS "+CAS_Name(DU_opponent[s])+"  /  BACK "+MK_Label(5,DU_pick[s]))
    call BlzFrameSetVisible(CAS_content[b+29],true)
    call CAS_ShowButton(s,33,DU_active[s] == 0 and DU_outgoing[s] == 0 and CAS_User(DU_opponent[s]) and MK_Valid(5,DU_pick[s]) and not CAS_ended)
    call CAS_ShowButton(s,34,DU_active[s] == 0)
    call CAS_ShowButton(s,35,DU_active[s] == 0)
    call CAS_ShowButton(s,36,DU_incoming[s] > 0 and DU_active[s] == 0 and not CAS_ended)
    call CAS_ShowButton(s,37,DU_incoming[s] > 0)
    call CAS_ShowButton(s,38,DU_outgoing[s] > 0)
endfunction

function CAS_CycleTarget takes integer current returns integer
    local integer i = 0
    loop
        exitwhen i >= 12
        set current = ModuloInteger(current,12)+1
        if MK_Valid(5,current) then
            return current
        endif
        set i = i+1
    endloop
    return 0
endfunction

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
                call CAS_ResultSound(won,stake)
                if won == DU_from[id] then
                    call CAS_ResultSound(DU_to[id],-stake)
                else
                    call CAS_ResultSound(DU_from[id],-stake)
                endif
                set CAS_note[won] = "Challenge won: return "+I2S(stake*2)+" gold."
            endif
        endif
        set id = id+1
    endloop
endfunction
