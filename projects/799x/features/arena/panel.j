function AR_View takes integer s returns nothing
    local integer b = s*32
    local integer target = AR_Target(s)
    local integer stake = AR_SelectedStake(s)
    local boolean canInvite = AR_state == 0 and target != 0 and AR_CanPlay(s) and not CAS_ended
    local string line = "Kill the opposing hero to win.|nEach side gets the same random hero, 40 footmen and one Scroll of the Beast."
    local string status
    if AR_state != 0 then
        set stake = AR_stake
    endif
    if CAS_ended then
        set status = "The arena is closed."
    elseif AR_state == 2 then
        set status = "Fighting: "+CAS_Name(AR_seat[0])+" vs "+CAS_Name(AR_seat[1])
    elseif AR_state == 1 then
        set status = CAS_Name(AR_seat[0])+" invited "+CAS_Name(AR_seat[1])+"  /  "+I2S(IMaxBJ(0,AR_until-CAS_seconds))+"s"
    elseif not AR_CanPlay(s) then
        set status = "A player slot with unit control is required."
    elseif target == 0 then
        set status = "Waiting for another player."
    else
        set status = "Opponent: "+CAS_Name(target)
    endif
    set line = line+"|n|nBoth Wallets pay on acceptance. The winner takes the pot."
    call BlzFrameSetText(CAS_content[b+28],line)
    call BlzFrameSetVisible(CAS_content[b+28],true)
    call BlzFrameSetText(CAS_content[b+29],status)
    call BlzFrameSetVisible(CAS_content[b+29],true)
    call CUI_Text(CAS_button[s*64+39],"Prediction duel")
    call CAS_ShowButton(s,39,true)
    call CAS_ShowButton(s,53,AR_state == 0 and target != 0 and AR_CanPlay(s) and not CAS_ended)
    call CAS_ShowButton(s,54,canInvite)
    call CUI_Text(CAS_button[s*64+19],"Invite for "+I2S(stake)+"g each")
    if AR_state == 0 then
        call CAS_ShowButton(s,19,canInvite and AR_CanFund(s,stake))
    elseif GetLocalPlayer() == Player(s-1) then
        call BlzFrameSetVisible(CAS_button[s*64+19],false)
    endif
    if stake == 0 then
        call CUI_Text(CAS_button[s*64+55],"Accept free duel")
    else
        call CUI_Text(CAS_button[s*64+55],"Accept for "+I2S(stake)+"g")
    endif
    if GetLocalPlayer() == Player(s-1) and AR_state == 1 and s == AR_seat[1] then
        set AR_shownOffer = AR_offer
    endif
    call CAS_ShowButton(s,55,AR_state == 1 and s == AR_seat[1] and not CAS_ended and (stake == 0 or AR_CanFund(s,stake)))
    if AR_state == 2 then
        call CUI_Text(CAS_button[s*64+56],"Forfeit")
    elseif AR_state == 1 and AR_seat[0] == s then
        call CUI_Text(CAS_button[s*64+56],"Cancel")
    else
        call CUI_Text(CAS_button[s*64+56],"Decline")
    endif
    call CAS_ShowButton(s,56,AR_state > 0 and (s == AR_seat[0] or s == AR_seat[1]))
endfunction
