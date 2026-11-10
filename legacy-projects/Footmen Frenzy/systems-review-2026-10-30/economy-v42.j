// EXPERIMENTAL player-local account gold. Not authoritative or crash-safe.
function FGA_Number takes string x returns boolean
    if x == null or x == "" or StringLength(x) > 11 then
        return false
    endif
    return I2S(S2I(x)) == x
endfunction

function FGA_Record takes integer s returns string
    local string payload="FGA1|"+I2S(FGA_gold[s])+"|"+I2S(FGA_lender[s])+"|"+I2S(FGA_debt[s])+"|"+I2S(FGA_pending[s])
    return payload+"|"+I2S(StringHash(payload+"|"+GetPlayerName(Player(s-1))+"|FGA1"))
endfunction

function FGA_SaveLocal takes nothing returns nothing
    local integer s=GetPlayerId(GetLocalPlayer())+1
    if s >= 1 and s <= 24 and FGA_ready[s] then
        call FileIO_Write("FFAccountGold_v1_"+I2S(StringHash(GetPlayerName(GetLocalPlayer())))+".pld",FGA_Record(s))
    endif
endfunction

function FGA_SendLocal takes nothing returns nothing
    local string name=GetPlayerName(GetLocalPlayer())
    local string data=FileIO_Read("FFAccountGold_v1_"+I2S(StringHash(name))+".pld")
    local string payload
    if not s__File_ReadEnabled then
        set data="INVALID"
    elseif data == null or data == "" then
        set payload="FGA1|1000|0|0|0"
        set data=payload+"|"+I2S(StringHash(payload+"|"+name+"|FGA1"))
    endif
    call BlzSendSyncData("FGA1",data)
endfunction

function FGA_Find takes integer identity returns integer
    local integer s=1
    local integer found=0
    if identity == 0 then
        return 0
    endif
    loop
        exitwhen s > 24
        if FGA_ready[s] and GetPlayerSlotState(Player(s-1)) == PLAYER_SLOT_STATE_PLAYING and StringHash(GetPlayerName(Player(s-1))) == identity then
            if found != 0 then
                return 0
            endif
            set found=s
        endif
        set s=s+1
    endloop
    return found
endfunction

function FGA_Reconcile takes nothing returns nothing
    local integer s=1
    local integer lender
    loop
        exitwhen s > 24
        if FGA_ready[s] and FGA_pending[s] > 0 then
            set lender=FGA_Find(FGA_lender[s])
            if lender > 0 and lender != s and FGA_gold[lender] <= 1000000000-FGA_pending[s] then
                set FGA_gold[lender]=FGA_gold[lender]+FGA_pending[s]
                set FGA_pending[s]=0
                if FGA_debt[s] == 0 then
                    set FGA_lender[s]=0
                endif
            endif
        endif
        set s=s+1
    endloop
endfunction

function FGA_OnSync takes nothing returns nothing
    local integer s=GetPlayerId(GetTriggerPlayer())+1
    local string data=BlzGetTriggerSyncData()
    local string a=FFPS_Field(data,1)
    local string b=FFPS_Field(data,2)
    local string c=FFPS_Field(data,3)
    local string d=FFPS_Field(data,4)
    local string check=FFPS_Field(data,5)
    local string payload
    if s < 1 or s > 24 or FGA_ready[s] then
        return
    endif
    if FFPS_Field(data,0) != "FGA1" or not FGA_Number(a) or not FGA_Number(b) or not FGA_Number(c) or not FGA_Number(d) or FFPS_Field(data,6) != null then
        return
    endif
    set payload="FGA1|"+a+"|"+b+"|"+c+"|"+d
    if check != I2S(StringHash(payload+"|"+GetPlayerName(Player(s-1))+"|FGA1")) then
        return
    endif
    if S2I(a) < 0 or S2I(a) > 1000000000 or S2I(c) < 0 or S2I(c) > 1000000000 or S2I(d) < 0 or S2I(d) > 1000000000 then
        return
    endif
    if (S2I(c) > 0 or S2I(d) > 0) and S2I(b) == 0 then
        return
    endif
    set FGA_gold[s]=S2I(a)
    set FGA_lender[s]=S2I(b)
    set FGA_debt[s]=S2I(c)
    set FGA_pending[s]=S2I(d)
    set FGA_ready[s]=true
    call FGA_Reconcile()
    call FGA_SaveLocal()
endfunction

function FGA_Token takes string line, integer which returns string
    local integer i=0
    local string converted=""
    loop
        exitwhen i >= StringLength(line)
        if SubString(line,i,i+1) == " " then
            set converted=converted+"|"
        else
            set converted=converted+SubString(line,i,i+1)
        endif
        set i=i+1
    endloop
    return FFPS_Field(converted,which)
endfunction

function FGA_OnCommand takes nothing returns nothing
    local integer s=GetPlayerId(GetTriggerPlayer())+1
    local string line=GetEventPlayerChatString()
    local string target=FGA_Token(line,1)
    local string principal=FGA_Token(line,2)
    local string vig=FGA_Token(line,3)
    local integer b
    local integer p
    local integer v
    local integer lender
    if not FGA_ready[s] then
        call DisplayTextToPlayer(GetTriggerPlayer(),0,0,"Account gold is not loaded.")
        return
    endif
    if SubString(line,0,6) == "-loan " then
        if not FGA_Number(target) or not FGA_Number(principal) or not FGA_Number(vig) or FGA_Token(line,4) != null then
            call DisplayTextToPlayer(GetTriggerPlayer(),0,0,"Use -loan slot amount vig, for example -loan 2 500 50")
            return
        endif
        set b=S2I(target)
        set p=S2I(principal)
        set v=S2I(vig)
        if b < 1 or b > 24 or b == s or not FGA_ready[b] or p <= 0 or p > 1000000 or v < 0 or v > 1000000 or FGA_gold[s] < p or FGA_lender[b] != 0 then
            call DisplayTextToPlayer(GetTriggerPlayer(),0,0,"Loan unavailable: check slot, balance and existing debt.")
            return
        endif
        set FGA_offerLender[b]=s
        set FGA_offerAmount[b]=p
        set FGA_offerVig[b]=v
        call DisplayTextToPlayer(Player(b-1),0,0,GetPlayerName(GetTriggerPlayer())+" offers "+I2S(p)+" account gold; repay "+I2S(p+v)+". Type -accept to accept.")
    elseif line == "-accept" then
        set lender=FGA_offerLender[s]
        if lender < 1 or lender > 24 then
            return
        endif
        set p=FGA_offerAmount[s]
        set v=FGA_offerVig[s]
        if not FGA_ready[lender] or GetPlayerSlotState(Player(lender-1)) != PLAYER_SLOT_STATE_PLAYING or FGA_lender[s] != 0 or FGA_gold[lender] < p or FGA_gold[s] > 1000000000-p or StringHash(GetPlayerName(Player(lender-1))) == 0 or FGA_Find(StringHash(GetPlayerName(Player(lender-1)))) != lender then
            call DisplayTextToPlayer(GetTriggerPlayer(),0,0,"Loan can no longer be accepted.")
            set FGA_offerLender[s]=0
            return
        endif
        set FGA_gold[lender]=FGA_gold[lender]-p
        set FGA_gold[s]=FGA_gold[s]+p
        set FGA_lender[s]=StringHash(GetPlayerName(Player(lender-1)))
        set FGA_debt[s]=p+v
        set FGA_offerLender[s]=0
        call DisplayTextToPlayer(GetTriggerPlayer(),0,0,"Loan accepted. Future account earnings repay "+I2S(p+v)+" gold first.")
        call FGA_SaveLocal()
    endif
endfunction

function FGA_Award takes integer s, integer amount returns nothing
    local integer paid=0
    local integer lender
    if not FGA_ready[s] or amount < 0 then
        return
    endif
    if FGA_debt[s] > 0 then
        set paid=IMinBJ(amount,FGA_debt[s])
        set lender=FGA_Find(FGA_lender[s])
        if lender > 0 and lender != s and FGA_gold[lender] <= 1000000000-paid then
            set FGA_gold[lender]=FGA_gold[lender]+paid
        elseif FGA_pending[s] <= 1000000000-paid then
            set FGA_pending[s]=FGA_pending[s]+paid
        else
            return
        endif
        set FGA_debt[s]=FGA_debt[s]-paid
        set amount=amount-paid
        if FGA_debt[s] == 0 and FGA_pending[s] == 0 then
            set FGA_lender[s]=0
        endif
    endif
    if FGA_gold[s] <= 1000000000-amount then
        set FGA_gold[s]=FGA_gold[s]+amount
    endif
endfunction

// Positive winner = side; negative winner = one player slot.
function FGA_Settle takes integer winner returns nothing
    local integer s=1
    local integer award
    local player p
    if FGA_settled then
        return
    endif
    set FGA_settled=true
    loop
        exitwhen s > 24
        set p=Player(s-1)
        set award=0
        if GetPlayerSlotState(p) == PLAYER_SLOT_STATE_PLAYING and GetPlayerController(p) == MAP_CONTROL_USER and not FF_IsBotName(GetPlayerName(p)) then
            if s <= 12 and FF_gr_participant[s] then
                set award=150
                if (winner > 0 and FF_gr_IsMember(s,winner)) or (winner < 0 and s == -winner) then
                    set award=650
                endif
            elseif GetPlayerTeam(p) == 4 then
                set award=25
            endif
        endif
        call FGA_Award(s,award)
        set s=s+1
    endloop
    call FGA_SaveLocal()
    set p=null
endfunction

function FGA_Display takes nothing returns nothing
    local integer s=GetPlayerId(GetLocalPlayer())+1
    if FGA_text == null then
        return
    endif
    if s >= 1 and s <= 24 and FGA_ready[s] then
        call BlzFrameSetText(FGA_text,"|cffffcc00Account gold:|r "+I2S(FGA_gold[s])+"   Debt: "+I2S(FGA_debt[s])+"   Pending lender credit: "+I2S(FGA_pending[s])+"   |cffaaaaaa-loan slot amount vig / -accept|r")
    else
        call BlzFrameSetText(FGA_text,"|cffff8080Account gold unavailable; do not use loans.|r")
    endif
endfunction

function FGA_Init takes nothing returns nothing
    local trigger sync=CreateTrigger()
    local trigger command=CreateTrigger()
    local integer i=0
    loop
        exitwhen i >= 24
        call BlzTriggerRegisterPlayerSyncEvent(sync,Player(i),"FGA1",false)
        call TriggerRegisterPlayerChatEvent(command,Player(i),"-loan ",false)
        call TriggerRegisterPlayerChatEvent(command,Player(i),"-accept",true)
        set i=i+1
    endloop
    call TriggerAddAction(sync,function FGA_OnSync)
    call TriggerAddAction(command,function FGA_OnCommand)
    call TimerStart(CreateTimer(),3.00,false,function FGA_SendLocal)
    set sync=null
    set command=null
endfunction
