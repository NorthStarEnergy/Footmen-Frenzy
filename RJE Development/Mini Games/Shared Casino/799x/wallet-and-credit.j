function LoanLegacyRecord takes integer s returns string
    local string payload = "L1"
    set payload = payload+"|"+I2S(LoanLent[s])
    set payload = payload+"|"+I2S(LoanOutstanding[s])
    set payload = payload+"|"+I2S(LoanInterest[s])
    set payload = payload+"|"+I2S(LoanLender[s])
    set payload = payload+"|"+I2S(LoanPrincipal[s])
    set payload = payload+"|"+I2S(LoanFee[s])
    set payload = payload+"|"+I2S(LoanPendingPrincipal[s])
    set payload = payload+"|"+I2S(LoanPendingFee[s])
    return payload+"|"+I2S(StringHash(payload+"|"+I2S(LoanIdentity[s])))
endfunction

function LoanRecord takes integer s returns string
    local string legacy = LoanLegacyRecord(s)
    local string payload = "L2|"+legacy+"|"+I2S(CreditMode[s])+"|"+I2S(CreditRate[s])+"|"+I2S(CreditPeriod[s])+"|"+I2S(CreditElapsed[s])+"|"+I2S(CreditFraction[s])
    return payload+"|"+I2S(StringHash(payload+"|"+I2S(LoanIdentity[s])))
endfunction

function LoanSave takes integer s returns nothing
    if Player(s-1) == GetLocalPlayer() then
        call s__File_close(s__File_write(s__File_open(WalletPath+".loans.pld"), LoanRecord(s)))
    endif
endfunction

function WalletSave takes nothing returns nothing
    local integer file = s__File_open(WalletPath)
    local string field = I2S(BlzBitXor(WalletBalance+CreditHold[GetPlayerId(GetLocalPlayer())+1], StringHash(WalletAccount + "/wallet/v1")))
    call s__File_write(file, field + ":" + I2S(StringHash(WalletAccount + ":" + field)))
    call s__File_close(file)
endfunction

function WalletBroadcast takes nothing returns nothing
    if WalletBalance >= 0 then
        call BlzSendSyncData(WalletSyncPrefix, I2S(WalletBalance)+"|"+LoanLocalRecord)
    endif
endfunction

function WalletLoad takes nothing returns nothing
    local player client = GetLocalPlayer()
    local string saved
    local string field
    local integer i = 0
    set HUD_walletRead = true
    call DestroyTimer(GetExpiredTimer())
    if WalletAccount == null or WalletAccount == "" or FF_IsBotName(WalletAccount) then
        call HUD_ShowWallet()
        return
    endif
    if not IsPlayerObserver(client) and (GetPlayerController(client) != MAP_CONTROL_USER or GetPlayerSlotState(client) != PLAYER_SLOT_STATE_PLAYING) then
        call HUD_ShowWallet()
        return
    endif
    set WalletPath = "FootmenFrenzy\\799X\\wallet-" + I2S(StringHash(WalletAccount)) + ".pld"
    set saved = s__File_readAndClose(s__File_open(WalletPath))
    if saved == null or saved == "" then
        set WalletSyncPrefix = "FFWalletNew"
        set WalletBalance = 1000
        call WalletSave()
    else
        loop
            exitwhen i >= StringLength(saved) or SubString(saved, i, i+1) == ":"
            set i = i + 1
        endloop
        set field = SubString(saved, 0, i)
        if saved == field + ":" + I2S(StringHash(WalletAccount + ":" + field)) and field == I2S(S2I(field)) then
            set WalletBalance = BlzBitXor(S2I(field), StringHash(WalletAccount + "/wallet/v1"))
        endif
    endif
    set LoanLocalRecord = s__File_readAndClose(s__File_open(WalletPath+".loans.pld"))
    if LoanLocalRecord == null or LoanLocalRecord == "" then
        set LoanLocalRecord = LoanRecord(GetPlayerId(client)+1)
    endif
    call HUD_ShowWallet()
    call WalletBroadcast()
endfunction

function CasinoWalletDelta takes integer s, integer delta returns nothing
    set CAS_gold[s] = CAS_gold[s] + delta
    set WalletPublic[s-1] = CAS_gold[s]
    if GetLocalPlayer() == Player(s-1) and WalletBalance >= 0 then
        set WalletBalance = CAS_gold[s]
        call HUD_ShowWallet()
        call WalletSave()
    endif
endfunction

function LoanCollect takes integer borrower returns nothing
    local integer lender = FGA_Find(LoanLender[borrower])
    local integer principal = LoanPendingPrincipal[borrower]
    local integer fee = LoanPendingFee[borrower]
    if lender == 0 or principal+fee == 0 or principal > LoanOutstanding[lender] or fee > 2147483647-LoanInterest[lender] or CAS_gold[lender] > 2147483647-principal-fee then
        return
    endif
    set LoanPendingPrincipal[borrower] = 0
    set LoanPendingFee[borrower] = 0
    if LoanPrincipal[borrower]+LoanFee[borrower] == 0 then
        set LoanLender[borrower] = 0
    endif
    set LoanOutstanding[lender] = LoanOutstanding[lender]-principal
    set LoanInterest[lender] = LoanInterest[lender]+fee
    call CasinoWalletDelta(lender,principal+fee)
    call LoanSave(lender)
    call LoanSave(borrower)
endfunction

function LoanAward takes integer s, integer amount returns nothing
    local integer principal = IMinBJ(amount,LoanPrincipal[s])
    local integer fee = IMinBJ(amount-principal,LoanFee[s])
    if CreditMode[s] == 1 then
        call CasinoWalletDelta(s,amount)
        return
    endif
    call CasinoWalletDelta(s,amount-principal-fee)
    if principal+fee > 0 then
        set LoanPrincipal[s] = LoanPrincipal[s]-principal
        set LoanFee[s] = LoanFee[s]-fee
        set LoanPendingPrincipal[s] = LoanPendingPrincipal[s]+principal
        set LoanPendingFee[s] = LoanPendingFee[s]+fee
        call LoanSave(s)
        call LoanCollect(s)
    endif
endfunction

function WalletReceive takes nothing returns nothing
    local integer id = GetPlayerId(GetTriggerPlayer())
    local string data = BlzGetTriggerSyncData()
    local integer slot = id+1
    local string balance = FFPS_Field(data,0)
    local integer amount = S2I(balance)
    local string ledger = SubString(data,StringLength(balance)+1,StringLength(data))
    local string field
    local integer i = 1
    local string full = ledger
    local boolean updated = FFPS_Field(full,0) == "L2"
    if updated then
        set ledger = SubString(full,3,StringLength(full))
    endif
    if WalletKnown[id] or not FGA_Number(balance) or amount < 0 or FFPS_Field(ledger,0) != "L1" then
        return
    endif
    loop
        exitwhen i > 8
        set field = FFPS_Field(ledger,i)
        if not FGA_Number(field) or (i != 4 and S2I(field) < 0) then
            return
        endif
        set i = i+1
    endloop
    set LoanLent[slot] = S2I(FFPS_Field(ledger,1))
    set LoanOutstanding[slot] = S2I(FFPS_Field(ledger,2))
    set LoanInterest[slot] = S2I(FFPS_Field(ledger,3))
    set LoanLender[slot] = S2I(FFPS_Field(ledger,4))
    set LoanPrincipal[slot] = S2I(FFPS_Field(ledger,5))
    set LoanFee[slot] = S2I(FFPS_Field(ledger,6))
    set LoanPendingPrincipal[slot] = S2I(FFPS_Field(ledger,7))
    set LoanPendingFee[slot] = S2I(FFPS_Field(ledger,8))
    if updated then
        set CreditMode[slot] = S2I(FFPS_Field(full,11))
        set CreditRate[slot] = S2I(FFPS_Field(full,12))
        set CreditPeriod[slot] = S2I(FFPS_Field(full,13))
        set CreditElapsed[slot] = S2I(FFPS_Field(full,14))
        set CreditFraction[slot] = S2I(FFPS_Field(full,15))
    endif
    if ((updated and full == LoanRecord(slot)) or (not updated and full == LoanLegacyRecord(slot))) and LoanOutstanding[slot] <= LoanLent[slot] then
        set WalletKnown[id] = true
        set WalletOpening[id] = amount
        if BlzGetTriggerSyncPrefix() == "FFWalletNew" and amount == 1000 then
            set WalletStartingGrant[id] = amount
        endif
        set PF_dirty = true
        set WalletPublic[id] = amount
        set CAS_gold[slot] = amount
        set CAS_ready[slot] = true
        set i = 1
        loop
            exitwhen i > 24
            if CAS_ready[i] then
                call LoanCollect(i)
            endif
            set i = i+1
        endloop
    endif
endfunction

function CreditOpen takes integer slot returns boolean
    return CasinoAdmin(slot) and CAS_ready[slot] and GetPlayerSlotState(Player(slot-1)) == PLAYER_SLOT_STATE_PLAYING
endfunction

function CreditTell takes integer s, string message returns nothing
    set CAS_note[s] = message
    call DisplayTimedTextToPlayer(Player(s-1),0,0,5,message)
endfunction

function CreditCancel takes integer offer returns nothing
    local integer owner = CreditOwner[offer]
    if owner == 0 then
        return
    endif
    if not CreditRequest[offer] then
        set CreditHold[owner] = CreditHold[owner]-CreditAmount[offer]
        call CasinoWalletDelta(owner,CreditAmount[offer])
    endif
    set CreditOwner[offer] = 0
endfunction

function CreditPost takes integer s, boolean request, integer target, integer amount, integer mode, integer rate, integer period, integer fee returns nothing
    local integer id = s*2-1
    set CreditSelected[s] = 0
    if not PK_Eligible(s-1) or (target != 0 and not PK_Eligible(target-1)) or not CreditOpen(s) or CAS_ended or amount < 1 or amount > 1000000 or fee < 0 or fee > 1000000 or (request and LoanLender[s] != 0) then
        call CreditTell(s,"Credit unavailable. Check the amount and outstanding debt.")
        return
    endif
    if CreditOwner[id] != 0 then
        set id = id+1
    endif
    if CreditOwner[id] != 0 then
        call CreditTell(s,"Both offer slots are in use. Cancel an offer first.")
        return
    endif
    if not request then
        if CAS_gold[s] < amount then
            call CreditTell(s,"Insufficient available gold to fund this offer.")
            return
        endif
        set CreditHold[s] = CreditHold[s]+amount
        call CasinoWalletDelta(s,-amount)
    endif
    set CreditGeneration[id] = CreditGeneration[id]+1
    set CreditOwner[id] = s
    set CreditTarget[id] = target
    set CreditRequest[id] = request
    set CreditAmount[id] = amount
    set CreditOfferMode[id] = mode
    set CreditOfferRate[id] = rate
    set CreditOfferPeriod[id] = period
    set CreditFee[id] = fee
    set CreditSeen[s] = CreditGeneration[id]
    set CreditSelected[s] = id
    call CreditTell(s,"Offer posted. Select your offer to cancel it.")
endfunction

function CreditAccept takes integer s, integer id returns nothing
    local integer owner = CreditOwner[id]
    local integer lender = owner
    local integer borrower = s
    local integer amount = CreditAmount[id]
    if CreditRequest[id] then
        set lender = s
        set borrower = owner
    endif
    if not PK_Eligible(s-1) or not PK_Eligible(owner-1) or not CreditOpen(s) or not CreditOpen(owner) or owner == s or CAS_ended or (CreditTarget[id] != 0 and CreditTarget[id] != s) then
        call CreditTell(s,"This offer is unavailable.")
        return
    endif
    if LoanLender[borrower] != 0 or LoanLent[lender] > 2147483647-amount or CAS_gold[borrower]+CreditHold[borrower] > 1000000000-amount or FGA_Find(LoanIdentity[lender]) != lender then
        call CreditTell(s,"Cannot accept: check existing debt and account limits.")
        return
    endif
    if CreditRequest[id] then
        if CAS_gold[lender] < amount then
            call CreditTell(s,"Insufficient available gold to fund this request.")
            return
        endif
        call CasinoWalletDelta(lender,-amount)
    else
        set CreditHold[lender] = CreditHold[lender]-amount
        call CasinoWalletDelta(lender,0)
    endif
    set CreditOwner[id] = 0
    call CasinoWalletDelta(borrower,amount)
    set LoanLent[lender] = LoanLent[lender]+amount
    set LoanOutstanding[lender] = LoanOutstanding[lender]+amount
    set LoanLender[borrower] = LoanIdentity[lender]
    set LoanPrincipal[borrower] = amount
    set LoanFee[borrower] = CreditFee[id]
    set CreditMode[borrower] = CreditOfferMode[id]
    set CreditRate[borrower] = CreditOfferRate[id]
    set CreditPeriod[borrower] = CreditOfferPeriod[id]
    set CreditElapsed[borrower] = 0
    set CreditFraction[borrower] = 0
    call LoanSave(borrower)
    call LoanSave(lender)
    call CreditTell(lender,"Loan funded: "+I2S(amount)+"g.")
    call CreditTell(borrower,"Credit received: "+I2S(amount)+"g.")
    // Other borrowing requests are no longer actionable while this debt is open.
    set id = borrower*2-1
    if CreditRequest[id] then
        call CreditCancel(id)
    endif
    if CreditRequest[id+1] then
        call CreditCancel(id+1)
    endif
endfunction

function CreditPay takes integer s returns nothing
    local integer due = LoanPrincipal[s]+LoanFee[s]
    local integer payment = IMinBJ(CAS_gold[s],due)
    local integer principal = IMinBJ(payment,LoanPrincipal[s])
    if payment <= 0 or (CreditMode[s] == 1 and payment != due) then
        call CreditTell(s,"Full repayment requires "+I2S(due)+" available gold.")
        return
    endif
    call CasinoWalletDelta(s,-payment)
    set LoanPrincipal[s] = LoanPrincipal[s]-principal
    set LoanFee[s] = LoanFee[s]-(payment-principal)
    set LoanPendingPrincipal[s] = LoanPendingPrincipal[s]+principal
    set LoanPendingFee[s] = LoanPendingFee[s]+payment-principal
    call LoanSave(s)
    call LoanCollect(s)
    call CreditTell(s,"Repaid "+I2S(payment)+"g.")
endfunction

function CreditTick takes integer s returns nothing
    local integer accrued
    if not PK_Eligible(s-1) then
        call CreditCancel(s*2-1)
        call CreditCancel(s*2)
    endif
    if not CreditOpen(s) or CAS_ended then
        call CreditCancel(s*2-1)
        call CreditCancel(s*2)
        return
    endif
    if CreditMode[s] == 2 and LoanPrincipal[s] > 0 then
        set CreditElapsed[s] = CreditElapsed[s]+1
        if CreditElapsed[s] >= CreditPeriod[s]*60 then
            set CreditElapsed[s] = 0
            set accrued = CreditFraction[s]+LoanPrincipal[s]*CreditRate[s]
            set CreditFraction[s] = ModuloInteger(accrued,100)
            set LoanFee[s] = IMinBJ(1000000000,LoanFee[s]+accrued/100)
            call LoanSave(s)
        elseif ModuloInteger(CreditElapsed[s],10) == 0 then
            call LoanSave(s)
        endif
    endif
endfunction

function LoanStats takes nothing returns string
    local integer s = GetPlayerId(GetLocalPlayer())+1
    local string roi = "--"
    if not CAS_ready[s] then
        return "Lending record unavailable"
    endif
    if LoanLent[s] > 0 then
        set roi = R2SW(100.0*I2R(LoanInterest[s])/I2R(LoanLent[s]),1,2)+"%"
    endif
    return "Lifetime lent: "+I2S(LoanLent[s])+"g|nOutstanding principal: "+I2S(LoanOutstanding[s])+"g|nInterest collected: "+I2S(LoanInterest[s])+"g    ROI: "+roi
endfunction

function WalletText takes nothing returns string
    if WalletBalance < 0 then
        return "Wallet: unavailable"
    endif
    return "Wallet: " + I2S(WalletBalance)
endfunction

function WalletPayParticipation takes nothing returns nothing
    local integer slot = 1
    loop
        exitwhen slot > 24
        if WalletMatchStarted and (WalletPlayedSlot[slot-1] > 0 or (slot <= 12 and FF_gr_participant[slot])) and CAS_ready[slot] and not CasinoPlayed[slot] then
            set CasinoPlayed[slot] = true
            set PF_rewards[slot] = PF_rewards[slot]+200
            call LoanAward(slot,200)
            call DisplayTimedTextToPlayer(Player(slot-1),0,0,8,"+200 to your Wallet for playing.")
        endif
        set slot = slot+1
    endloop
endfunction

function WalletAward takes integer winnerSlot, integer winnerSide returns nothing
    local integer slot = 1
    local integer played
    local integer reward
    if not WalletMatchStarted or WalletSettled then
        return
    endif
    call WalletPayParticipation()
    set WalletSettled = true
    loop
        exitwhen slot > 24
        set reward = 0
        if CAS_ready[slot] and GetPlayerSlotState(Player(slot-1)) == PLAYER_SLOT_STATE_PLAYING then
            set played = WalletPlayedSlot[slot-1]
            if played == 0 then
                set played = slot
            endif
            if played <= 12 and FF_gr_participant[played] then
                if played == winnerSlot or (winnerSide > 0 and FF_gr_IsMember(played,winnerSide)) then
                    set reward = 750
                endif
            elseif IsPlayerObserver(Player(slot-1)) or GetPlayerTeam(Player(slot-1)) == 4 then
                set reward = 50
            endif
            if reward > 0 then
                set PF_rewards[slot] = PF_rewards[slot]+reward
                call LoanAward(slot,reward)
                call DisplayTimedTextToPlayer(Player(slot-1),0,0,8,"+"+I2S(reward)+" to your Wallet.")
            endif
        endif
        set slot = slot+1
    endloop
endfunction

function CAS_Flush takes integer s returns nothing
    if CAS_returnDue[s] > 0 then
        call CasinoWalletDelta(s,CAS_returnDue[s])
    endif
    if CAS_profitDue[s] > 0 then
        call LoanAward(s,CAS_profitDue[s])
    endif
    set CAS_returnDue[s] = 0
    set CAS_profitDue[s] = 0
endfunction

function CAS_Credit takes integer game, integer s, integer principal, integer profit returns nothing
    set PF_gameReturn[s*4+game] = PF_gameReturn[s*4+game]+principal+profit
    set PF_returned[s] = PF_returned[s]+principal+profit
    call PF_Log(s,"return",0,principal+profit,0)
    set CAS_returnDue[s] = CAS_returnDue[s]+principal
    set CAS_profitDue[s] = CAS_profitDue[s]+profit
    call CAS_Flush(s)
endfunction

function CAS_Reserve takes integer game, integer s, integer stake, integer liability returns boolean
    if CAS_ended or not PK_Eligible(s-1) or not CAS_ready[s] then
        set CAS_note[s] = "Wallet unavailable, or this match has ended."
        return false
    endif
    if stake < 10 or stake > 10000 or (game != 0 and ModuloInteger(stake,2) != 0) or CAS_gold[s] < stake then
        set CAS_note[s] = "Choose a wager of 10 to 10,000 gold within your balance."
        return false
    endif
    if liability < 0 or CAS_bank-CAS_liability < liability then
        set CAS_note[s] = "This wager exceeds the remaining house backing. Try a smaller amount."
        return false
    endif
    set PF_gameBets[s*4+game] = PF_gameBets[s*4+game]+1
    set PF_gameStake[s*4+game] = PF_gameStake[s*4+game]+stake
    set PF_wagers[s] = PF_wagers[s]+1
    set PF_staked[s] = PF_staked[s]+stake
    call PF_Log(s,"stake",0,stake,0)
    call CasinoWalletDelta(s,-stake)
    set CAS_escrow[s] = CAS_escrow[s]+stake
    set CAS_liability = CAS_liability+liability
    call CAS_Flush(s)
    return true
endfunction

function CAS_Settle takes integer game, integer s, integer stake, integer payout, integer liability returns nothing
    set CAS_escrow[s] = CAS_escrow[s]-stake
    set CAS_liability = CAS_liability-liability
    set CAS_bank = CAS_bank+stake-payout
    call CAS_Credit(game,s,IMinBJ(stake,payout),IMaxBJ(0,payout-stake))
endfunction

function CreditTerms takes integer mode, integer rate, integer period, integer fee returns string
    if mode == 2 then
        return CUI_Value(I2S(rate)+"%")+" every "+CUI_Value(I2S(period))+" played min on unpaid principal. Earnings repay automatically."
    elseif mode == 1 then
        return CUI_Value(I2S(rate)+"%")+" fixed ("+CUI_Value(I2S(fee)+"g")+"). Repay in one payment."
    endif
    return CUI_Value(I2S(fee)+"g")+" fixed fee. Earnings repay automatically."
endfunction

function CreditBrowse takes integer s, integer step returns nothing
    local integer id = CreditSelected[s]
    local integer count = 0
    loop
        exitwhen count >= 48
        set id = ModuloInteger(id-1+step+48,48)+1
        if CreditOwner[id] != 0 and (CreditOwner[id] == s or CreditTarget[id] == 0 or CreditTarget[id] == s) then
            set CreditSeen[s] = CreditGeneration[id]
            set CreditSelected[s] = id
            return
        endif
        set count = count+1
    endloop
    set CreditSelected[s] = 0
endfunction

function CreditView takes integer s returns nothing
    local integer id = CreditSelected[s]
    local integer owner = CreditOwner[id]
    local integer i = 40
    local string kind = "Lend"
    local string offer = "No offer selected. Use Next to browse."
    local string draft
    if CreditSeen[s] != CreditGeneration[id] then
        set owner = 0
    endif
    if CreditDraftRequest[s] then
        set kind = "Borrow"
    endif
    set draft = kind+" "+CUI_Value(I2S(CAS_amount[s])+"g")+"  /  "+CreditTerms(CreditDraftMode[s],CreditDraftRate[s],CreditDraftPeriod[s],CAS_amount[s]*CreditDraftRate[s]/100)
    if owner != 0 then
        set offer = GetPlayerName(Player(owner-1))+" offers "+CUI_Value(I2S(CreditAmount[id])+"g")
        if CreditRequest[id] then
            set offer = GetPlayerName(Player(owner-1))+" requests "+CUI_Value(I2S(CreditAmount[id])+"g")
        endif
        set offer = offer+"|n"+CreditTerms(CreditOfferMode[id],CreditOfferRate[id],CreditOfferPeriod[id],CreditFee[id])
    endif
    call BlzFrameSetSize(CAS_content[s*32+28],0.650,0.062)
    call BlzFrameSetText(CAS_content[s*32+28],"YOUR TERMS|n"+draft)
    call BlzFrameSetVisible(CAS_content[s*32+28],true)
    call BlzFrameSetText(CAS_content[s*32+29],offer)
    call BlzFrameSetVisible(CAS_content[s*32+29],true)
    loop
        exitwhen i > 52
        call CAS_ShowButton(s,i,true)
        set i = i+1
    endloop
    call CAS_ShowButton(s,48,CreditDraftMode[s] == 2)
    call CAS_ShowButton(s,51,owner != 0 and (owner == s or not CAS_ended))
    if owner == s then
        call CUI_Text(CAS_button[s*64+51],"Cancel offer")
    else
        call CUI_Text(CAS_button[s*64+51],"Accept offer")
    endif
    call CAS_ShowButton(s,52,LoanPrincipal[s]+LoanFee[s] > 0)
endfunction

function FGA_Number takes string x returns boolean
    if x == null or x == "" or StringLength(x) > 11 then
        return false
    endif
    return I2S(S2I(x)) == x
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

function FGA_Find takes integer identity returns integer
    local integer s=1
    local integer found=0
    if identity == 0 then
        return 0
    endif
    loop
        exitwhen s > 24
        if CAS_ready[s] and GetPlayerSlotState(Player(s-1)) == PLAYER_SLOT_STATE_PLAYING and LoanIdentity[s] == identity then
            if found != 0 then
                return 0
            endif
            set found=s
        endif
        set s=s+1
    endloop
    return found
endfunction

function FGA_OnCommand takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local string line = GetEventPlayerChatString()
    local integer target = S2I(FGA_Token(line,1))
    local string amount = FGA_Token(line,2)
    local string fee = FGA_Token(line,3)
    local integer id = 1
    local integer match = 0
    if not PK_Eligible(s-1) then
        return
    endif
    if line == "-accept" then
        loop
            exitwhen id > 48
            if CreditOwner[id] != 0 and CreditTarget[id] == s then
                if match != 0 then
                    call CreditTell(s,"Multiple offers. Select the one you want in Credit.")
                    return
                endif
                set match = id
            endif
            set id = id+1
        endloop
    if match != 0 then
        call CreditAccept(s,match)
    endif
    elseif PK_Eligible(target-1) and CreditOpen(target) and target != s and FGA_Number(amount) and FGA_Number(fee) then
        call CreditPost(s,false,target,S2I(amount),0,0,0,S2I(fee))
        if CreditOwner[CreditSelected[s]] == s and CreditTarget[CreditSelected[s]] == target then
            call CreditTell(target,GetPlayerName(Player(s-1))+" offers "+amount+"g with a "+fee+"g fee. Review in Credit or type -accept.")
        endif
    else
        call CreditTell(s,"Use -loan slot amount fee, or open Casino > Credit.")
    endif
endfunction
