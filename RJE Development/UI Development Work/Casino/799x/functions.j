function CasinoAdmin takes integer s returns boolean
    return s >= 1 and s <= 24 and udg_admin_level[s] >= 90
endfunction

function CAS_User takes integer s returns boolean
    if s < 1 or s > 24 then
        return false
    endif
    return GetPlayerSlotState(Player(s-1)) == PLAYER_SLOT_STATE_PLAYING and (GetPlayerController(Player(s-1)) == MAP_CONTROL_USER or IsPlayerObserver(Player(s-1))) and not FF_IsBotName(GetPlayerName(Player(s-1)))
endfunction

function CAS_Announce takes string msg returns nothing
    local integer p = 0
    loop
        exitwhen p >= 24
        if PK_Eligible(p) then
            call DisplayTimedTextToPlayer(Player(p),0,0,10,msg)
        endif
        set p = p+1
    endloop
endfunction

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

function HUD_WalletValue takes nothing returns string
    if WalletBalance >= 0 then
        return I2S(WalletBalance)
    elseif HUD_walletRead then
        return "Unavailable"
    endif
    return "Loading"
endfunction

function HUD_ShowWallet takes nothing returns nothing
    if HUD_wallet != null then
        call BlzFrameSetText(HUD_wallet,HUD_WalletValue())
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

function HUD_Text takes real x, real y, real width, real height, real size, string value returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","",HUD_root,"",0)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,HUD_root,FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetSize(f,width,height)
    call BlzFrameSetFont(f,"CasinoUI\\Bold.ttf",size,0)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetEnable(f,false)
    call BlzFrameSetText(f,value)
    return f
endfunction

function HUD_Refresh takes nothing returns nothing
    local integer width = BlzGetLocalClientWidth()
    local integer height = BlzGetLocalClientHeight()
    local integer slot = PF_MySlot()
    local real left = 0.012
    if width != HUD_width or height != HUD_height then
        if height > 0 then
            set left = left-RMaxBJ(0.0,(0.6*I2R(width)/I2R(height)-0.8)*0.5)
        endif
        call BlzFrameClearAllPoints(HUD_root)
        call BlzFrameSetAbsPoint(HUD_root,FRAMEPOINT_TOPLEFT,left,0.542)
        set HUD_width = width
        set HUD_height = height
    endif
    call HUD_ShowWallet()
    if slot <= 12 then
        call BlzFrameSetText(HUD_gold,I2S(GetPlayerState(Player(slot-1),PLAYER_STATE_RESOURCE_GOLD)))
    else
        call BlzFrameSetText(HUD_gold,"--")
    endif
endfunction

function HUD_Create takes nothing returns nothing
    local framehandle label
    set HUD_root = BlzCreateFrameByType("BACKDROP","FFBalanceHud",FFUI_GetRoot(),"",0)
    call BlzFrameSetSize(HUD_root,0.166,0.033)
    call BlzFrameSetTexture(HUD_root,"CasinoUI\\panel.blp",0,true)
    call BlzFrameSetEnable(HUD_root,false)
    call BlzFrameSetLevel(HUD_root,110)
    set label = HUD_Text(0.006,0.002,0.074,0.012,0.008,"WALLET")
    call BlzFrameSetTextColor(label,BlzConvertColor(255,255,215,132))
    set HUD_wallet = HUD_Text(0.006,0.014,0.074,0.016,0.011,"")
    set label = HUD_Text(0.085,0.002,0.075,0.012,0.008,"MATCH GOLD")
    call BlzFrameSetTextColor(label,BlzConvertColor(255,255,215,132))
    set HUD_gold = HUD_Text(0.085,0.014,0.075,0.016,0.011,"")
    call HUD_Refresh()
    set label = null
endfunction

function CUI_Value takes string value returns string
    return "|cffffe39a"+value+"|r"
endfunction

function CUI_Text takes framehandle f, string label returns nothing
    call BlzFrameSetText(f,label)
endfunction

function CUI_Paint takes framehandle f, integer tone, boolean enabled returns nothing
    local integer color = BlzConvertColor(255,255,250,240)
    if not enabled then
        set color = BlzConvertColor(255,145,158,170)
    elseif tone == 1 then
        set color = BlzConvertColor(255,255,155,150)
    elseif tone == 2 or tone == 3 then
        set color = BlzConvertColor(255,169,241,180)
    elseif tone == 4 then
        set color = BlzConvertColor(255,163,208,255)
    elseif tone == 5 then
        set color = BlzConvertColor(255,255,213,121)
    endif
    call BlzFrameSetTextColor(f,color)
    if BlzFrameGetEnable(f) != enabled then
        call BlzFrameSetEnable(f,enabled)
    endif
endfunction

function CUI_Create takes framehandle parent, integer context, real x, real y, real w, real h, string label, integer tone returns framehandle
    local framehandle f = BlzCreateFrame("ScriptDialogButton",parent,0,context)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,parent,FRAMEPOINT_TOPLEFT,x,y)
    call BlzFrameSetLevel(f,65)
    call BlzFrameSetText(f,label)
    call CUI_Paint(f,tone,true)
    return f
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

function CAS_ResultSound takes integer s, integer net returns nothing
    if s > 0 then
        if net > 0 then
            call StartSoundForPlayerBJ(Player(s-1),CAS_winSound)
        elseif net < 0 then
            call StartSoundForPlayerBJ(Player(s-1),CAS_lossSound)
        endif
    endif
endfunction

function CAS_Settle takes integer game, integer s, integer stake, integer payout, integer liability returns nothing
    set CAS_escrow[s] = CAS_escrow[s]-stake
    set CAS_liability = CAS_liability-liability
    set CAS_bank = CAS_bank+stake-payout
    call CAS_Credit(game,s,IMinBJ(stake,payout),IMaxBJ(0,payout-stake))
endfunction

function CAS_Random takes integer bound returns integer
    local integer hi = CAS_seed / 127773
    local integer lo = ModuloInteger(CAS_seed,127773)
    set CAS_seed = 16807*lo-2836*hi
    if CAS_seed <= 0 then
        set CAS_seed = CAS_seed+2147483647
    endif
    return ModuloInteger(CAS_seed,bound)
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

function CAS_EndMatch takes nothing returns nothing
    local integer winner = CAS_winner
    local integer m = 1
    local integer i = 1
    local boolean ffa = winner < 0
    if CAS_ended then
        return
    endif
    set CAS_ended = true
    call AR_End(0,"The main match ended. The arena is closed.")
    loop
        exitwhen i > 48
        call CreditCancel(i)
        set i = i+1
    endloop
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
    set i = 1
    loop
        exitwhen i > 24
        call HousePK_Refund(i-1)
        if BJ_phase[i] >= 1 and BJ_phase[i] <= 3 then
            call BJ_Finish(i,true)
        endif
        set i = i+1
    endloop
    call OP_EndMatch()
endfunction

function CAS_SafeX takes real x returns real
    return x
endfunction

function CAS_SafeW takes real width returns real
    return width
endfunction

function CAS_Label takes integer s, real x, real y, real w, real h, real scale returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","CasinoLabel",CAS_root[s],"",s)
    call BlzFrameSetSize(f,CAS_SafeW(w),h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,CAS_SafeX(x),-y)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetFont(f,"CasinoUI\\Bold.ttf",0.0115*scale,0)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function CAS_Texture takes integer s, string path, real x, real y, real w, real h returns framehandle
    local framehandle f = BlzCreateFrameByType("BACKDROP","CasinoArt",CAS_root[s],"",s)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetTexture(f,path,0,true)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function CAS_Tone takes integer id returns integer
    if id == 6 or id == 10 or id == 37 or id == 38 then
        return 1
    elseif id == 7 or id == 8 or id == 9 or id == 11 or id == 14 or id == 32 or id == 33 or id == 36 then
        return 2
    elseif id == 12 then
        return 3
    elseif id == 15 or id == 16 or id == 34 or id == 35 then
        return 4
    endif
    return 0
endfunction

function CAS_Button takes integer s, integer id, trigger click, real x, real y, real w, string label returns nothing
    local framehandle f = CUI_Create(CAS_root[s],s*64+id,CAS_SafeX(x),-y,CAS_SafeW(w),0.027,label,CAS_Tone(id))
    call BlzTriggerRegisterFrameEvent(click,f,FRAMEEVENT_CONTROL_CLICK)
    set CAS_button[s*64+id] = f
    set f = null
endfunction

function CAS_ShowButton takes integer s, integer id, boolean enabled returns nothing
    if GetLocalPlayer() == Player(s-1) and not BlzFrameIsVisible(CAS_button[s*64+id]) then
        call BlzFrameSetVisible(CAS_button[s*64+id],true)
    endif
    call CUI_Paint(CAS_button[s*64+id],CAS_Tone(id),enabled)
endfunction

function CAS_CardFace takes framehandle f, integer card, boolean back returns nothing
    local string name = "empty"
    if back then
        set name = "back"
    elseif card >= 0 then
        set name = "card"+I2S(card)
    endif
    call BlzFrameSetVisible(f,true)
    call BlzFrameSetTexture(f,"PokerUI\\"+name+".blp",0,true)
endfunction

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
    call CAS_ShowButton(s,33,DU_active[s] == 0 and DU_outgoing[s] == 0 and PK_Eligible(DU_opponent[s]-1) and MK_Valid(5,DU_pick[s]) and not CAS_ended)
    call CAS_ShowButton(s,34,DU_active[s] == 0)
    call CAS_ShowButton(s,35,DU_active[s] == 0)
    call CAS_ShowButton(s,36,DU_incoming[s] > 0 and DU_active[s] == 0 and not CAS_ended)
    call CAS_ShowButton(s,37,DU_incoming[s] > 0)
    call CAS_ShowButton(s,38,DU_outgoing[s] > 0)
    call CUI_Text(CAS_button[s*64+39],"Arena 1v1")
    call CAS_ShowButton(s,39,true)
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

function CAS_Render takes integer s returns nothing
    local integer i = 0
    local integer b = s*32
    local integer host = s
    local string label = "|cffe7cb88RULES|r"
    if CAS_root[s] == null then
        return
    endif
    if GetLocalPlayer() == Player(s-1) then
        call BlzFrameSetVisible(CAS_root[s],CAS_view[s] > 0)
    endif
    if CAS_view[s] == 0 then
        return
    endif
    if HousePK_Started[s-1] and not HousePK_Hidden[s-1] then
        set HousePK_Hidden[s-1] = true
        call HousePK_Render(s-1)
    endif
    set i = 0
    loop
        exitwhen i > 3
        if i+1 == CAS_view[s] or (i == 2 and CAS_view[s] == 6) then
            call CUI_Paint(CAS_button[s*64+i],5,true)
        else
            call CUI_Paint(CAS_button[s*64+i],0,true)
        endif
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 32
        if CAS_content[b+i] != null then
            call BlzFrameSetVisible(CAS_content[b+i],false)
        endif
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 18
        call BlzFrameSetVisible(CAS_card[s*18+i],false)
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 6
        call BlzFrameSetVisible(CAS_seatTotal[s*6+i],false)
        call BlzFrameSetVisible(CAS_row[s*6+i],false)
        call BlzFrameSetVisible(CAS_track[s*6+i],false)
        call BlzFrameSetVisible(CAS_bar[s*6+i],false)
        set i = i+1
    endloop
    if CasinoLastView[s] != CAS_view[s] then
        set i = 6
        loop
            exitwhen i > 10
            if CAS_view[s] == 1 then
                call BlzFrameSetSize(CAS_button[s*64+i],0.087,0.037)
                call BlzFrameSetPoint(CAS_button[s*64+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,0.216+I2R(i-6)*0.093,-0.402)
            else
                call BlzFrameSetSize(CAS_button[s*64+i],0.075,0.027)
                call BlzFrameSetPoint(CAS_button[s*64+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,0.025+I2R(i-6)*0.080,-0.394)
            endif
            set i = i+1
        endloop
    set i = 11
    loop
        exitwhen i >= 57
        if CAS_button[s*64+i] != null then
            call BlzFrameSetVisible(CAS_button[s*64+i],false)
        endif
        set i = i+1
    endloop
        set CasinoLastView[s] = CAS_view[s]
    endif
    call BlzFrameSetVisible(BJWatchHistory[s],false)
    if BJWatchHost[s] != 0 then
        if CAS_view[s] == 1 and BJWatchActive(BJWatchHost[s]) then
            set host = BJWatchHost[s]
        else
            set BJWatchHost[s] = 0
        endif
    endif
    call BJWatchList(s)
    call BlzFrameSetVisible(CAS_felt[s],CAS_view[s] == 1)
    call BlzFrameSetVisible(BJ_wagerLabel[s],CAS_view[s] == 1)
    call BlzFrameSetVisible(CAS_status[s],CAS_view[s] != 1)
    call BlzFrameSetVisible(CAS_chip[s],false)
    set i = 6
    loop
        exitwhen i > 10
        if CAS_view[s] != 1 then
            call CUI_Paint(CAS_button[s*64+i],0,true)
        endif
        call BlzFrameSetVisible(CAS_button[s*64+i],CAS_view[s] != 5 and (CAS_view[s] != 6 or (AR_state == 0 and not CAS_ended)))
        set i = i+1
    endloop
    if CAS_view[s] == 1 then
        set label = "|cffe7cb88BLACKJACK|r"
        call BlzFrameSetText(BJ_wagerLabel[s],"NEXT BET   "+CUI_Value(I2S(CAS_amount[s])+"g"))
        call CUI_Text(CAS_button[s*64+11],"Place bet  "+I2S(CAS_amount[s])+"g")
        call CUI_Paint(CAS_button[s*64+6],0,CAS_amount[s] > 10)
        call CUI_Paint(CAS_button[s*64+7],0,CAS_amount[s] < 100)
        call CUI_Paint(CAS_button[s*64+8],0,CAS_amount[s] < 100)
        call CUI_Paint(CAS_button[s*64+9],0,CAS_amount[s] < 100)
        call CUI_Paint(CAS_button[s*64+10],0,CAS_amount[s] > 10)
        if host != s then
            set label = "Watching  "+SubString(CAS_Name(host),0,20)
        endif
        call CAS_BlackjackView(s,host)
    elseif CAS_view[s] == 2 then
        set label = "|cffe7cb88MATCH BETS|r"
        call CAS_BetsView(s)
    elseif CAS_view[s] == 3 then
        set label = "|cffe7cb88CHALLENGES|r"
        call CAS_DuelsView(s)
    elseif CAS_view[s] == 6 then
        set label = "|cffe7cb88ARENA 1v1|r"
        call AR_View(s)
    elseif CAS_view[s] == 5 then
        set label = "|cffe7cb88CREDIT|r"
        call CreditView(s)
    else
        call BlzFrameSetVisible(CAS_content[b+30],true)
        call BlzFrameSetText(CAS_content[b+30],"|cffe7cb88BLACKJACK|r|nPrivate dealer. Bet 10-100g before the deal / 2 decks / S17 / blackjack 3:2 / win 1:1 / ties push|nDouble first 2 cards. Split once. Split aces: 1 card.|nSplit 21 pays 1:1. Timeout stands. No insurance/surrender.|n|n|cffe7cb88MATCH BETS|r|nClose 2:10 / warning 2:00 / accepted odds stay locked|nBase kill: any enemy base. No first event or draw: refund.|n|n|cffe7cb88CHALLENGES|r|nPrediction: equal stakes on opposite results. Arena 1v1: play free or match Wallet stakes. Winner takes the pot.|n|n|cffe7cb88Wallet|r|nStakes come from your Wallet. Open bets are at risk if you quit.")
    endif
    call BlzFrameSetVisible(CAS_button[s*64+60],CAS_view[s] == 5)
    call BlzFrameSetVisible(CAS_button[s*64+59],CAS_view[s] == 1)
    call BlzFrameSetText(CAS_title[s],label)
    if CAS_view[s] == 5 then
        call CUI_Paint(CAS_button[s*64+57],5,true)
    else
        call CUI_Paint(CAS_button[s*64+57],0,true)
    endif
    set label = "LOADING GOLD"
    if CAS_ready[s] then
        set label = "Wallet "+CUI_Value(I2S(CAS_gold[s]))
        if CAS_escrow[s] > 0 then
            set label = label+"  /  HELD "+CUI_Value(I2S(CAS_escrow[s]))
        endif
        if CAS_returnDue[s]+CAS_profitDue[s] > 0 then
            set label = label+"  /  CREDIT "+CUI_Value(I2S(CAS_returnDue[s]+CAS_profitDue[s]))
        endif
    endif
    call BlzFrameSetText(CAS_balance[s],label)
    set label = "SELECTED BET  "+CUI_Value(I2S(CAS_amount[s])+"g")
    if CAS_ended then
        set label = label+"  /  SETTLED"
    elseif CAS_view[s] == 2 and (CAS_closed or CAS_seconds >= 130) then
        set label = label+"  /  BETS CLOSED"
    elseif CAS_view[s] == 2 then
        set label = label+"  /  CLOSE "+CUI_Value(I2S(130-CAS_seconds)+"s")
    endif
    if CAS_view[s] == 5 then
        set label = "Escrow: "+CUI_Value(I2S(CreditHold[s])+"g")+"     Your debt: "+CUI_Value(I2S(LoanPrincipal[s]+LoanFee[s])+"g")
    endif
    if CAS_view[s] == 1 then
        set label = label+"    /    ON TABLE  "+CUI_Value(I2S(BJ_bet[BJ_seat[s]*2]+BJ_bet[BJ_seat[s]*2+1])+"g")
    endif
    if CAS_view[s] == 6 then
        if AR_state == 0 then
            set label = "Selected: "+AR_Terms(AR_SelectedStake(s))+"    /    Exact amount: -stake 250"
        else
            set label = AR_Terms(AR_stake)
        endif
    endif
    call BlzFrameSetText(CAS_status[s],label)
    if host == s then
        call BlzFrameSetText(CAS_footer[s],CAS_note[s])
    elseif BJ_phase[host] == 4 then
        set label = BJ_result[BJ_seat[host]*2]
        if BJ_split[BJ_seat[host]*2] then
            set label = label+"  /  "+BJ_result[BJ_seat[host]*2+1]
        endif
        call BlzFrameSetText(CAS_footer[s],label)
    else
        call BlzFrameSetText(CAS_footer[s],"Round "+I2S(BJ_round[host])+"  /  Viewing "+CAS_Name(host))
    endif
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

function CasinoStakeMax takes integer s returns integer
    if CAS_view[s] == 1 then
        return 100
    elseif PK_Started[s-1] and not PK_Hidden[s-1] then
        return 1500
    endif
    return 10000
endfunction

function CAS_Click takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local framehandle f = BlzGetTriggerFrame()
    local integer id = 0
    local integer i
    local integer count
    local integer target
    if not PK_Eligible(s-1) then
        return
    endif
    loop
        exitwhen id >= 64 or CAS_button[s*64+id] == f
        set id = id+1
    endloop
    if CAS_view[s] == 1 then
        set target = 1
        loop
            exitwhen target > 24
            if f == BJWatchEye[s*25+target] and f != null then
                if target != s and BJWatchActive(target) then
                    set BJWatchHost[s] = target
                endif
                call CAS_Render(s)
                return
            endif
            set target = target+1
        endloop
        if id == 16 then
            set BJWatchPage[s] = BJWatchPage[s]+1
            call CAS_Render(s)
            return
        elseif id == 61 then
            set BJWatchHost[s] = 0
            call CAS_Render(s)
            return
        elseif BJWatchHost[s] != 0 and id >= 6 and id <= 15 then
            return
        endif
    endif
    if id >= 11 and id <= 15 and CAS_view[s] != 1 then
        return
    endif
    if id <= 5 or id == 57 or id == 59 then
        set BJWatchHost[s] = 0
    endif
    if id <= 3 then
        set CAS_view[s] = id+1
    elseif id == 4 then
        set CAS_view[s] = 0
    elseif id == 5 then
        if PK_Started[s-1] then
            set CAS_view[s] = 0
            set PK_Hidden[s-1] = false
            call PK_Render(s-1)
        else
            set CAS_note[s] = "Your poker table is still loading."
        endif
    elseif id == 60 and CAS_view[s] == 5 then
        if CAS_ready[s] then
            call DisplayTimedTextToPlayer(Player(s-1),0,0,10,"Wallet: "+I2S(CAS_gold[s])+"g  /  Lifetime lent: "+I2S(LoanLent[s])+"g|nOutstanding principal: "+I2S(LoanOutstanding[s])+"g  /  Interest collected: "+I2S(LoanInterest[s])+"g")
            if LoanLent[s] > 0 then
                call DisplayTimedTextToPlayer(Player(s-1),0,0,10,"Lending ROI: "+R2SW(100.*I2R(LoanInterest[s])/I2R(LoanLent[s]),1,2)+"%")
            endif
        endif
    elseif id == 59 and CAS_view[s] == 1 then
        set CAS_view[s] = 0
        call HousePK_Start(s-1)
    elseif id == 57 then
        set CAS_view[s] = 5
        call CreditBrowse(s,1)
    elseif id >= 40 and id <= 52 and CAS_view[s] == 5 then
        if id == 40 then
            set CreditDraftRequest[s] = not CreditDraftRequest[s]
        elseif id == 41 then
            set CAS_amount[s] = IMaxBJ(10,CAS_amount[s]-10)
        elseif id == 42 then
            set CAS_amount[s] = IMinBJ(10000,CAS_amount[s]+10)
        elseif id == 43 then
            set CAS_amount[s] = IMinBJ(10000,CAS_amount[s]+100)
        elseif id == 44 then
            set CreditDraftRate[s] = IMaxBJ(0,CreditDraftRate[s]-1)
        elseif id == 45 then
            set CreditDraftRate[s] = IMinBJ(100,CreditDraftRate[s]+1)
        elseif id == 46 then
            set CreditDraftMode[s] = 3-CreditDraftMode[s]
        elseif id == 47 then
            call CreditPost(s,CreditDraftRequest[s],0,CAS_amount[s],CreditDraftMode[s],CreditDraftRate[s],CreditDraftPeriod[s],CAS_amount[s]*CreditDraftRate[s]/100*(2-CreditDraftMode[s]))
        elseif id == 48 then
            set CreditDraftPeriod[s] = ModuloInteger(CreditDraftPeriod[s],10)+1
        elseif id == 49 then
            call CreditBrowse(s,-1)
        elseif id == 50 then
            call CreditBrowse(s,1)
        elseif id == 51 then
            set i = CreditSelected[s]
            if CreditSeen[s] != CreditGeneration[i] then
                call CreditTell(s,"Offer changed. Browse again to review the new terms.")
            elseif CreditOwner[i] == s then
                call CreditCancel(i)
            elseif CreditOwner[i] != 0 then
                call CreditAccept(s,i)
            endif
        else
            call CreditPay(s)
        endif
    elseif id == 6 then
        set CAS_amount[s] = IMaxBJ(10,CAS_amount[s]-10)
    elseif id == 7 then
        set CAS_amount[s] = IMinBJ(CasinoStakeMax(s),CAS_amount[s]+10)
    elseif id == 8 then
        set CAS_amount[s] = IMinBJ(CasinoStakeMax(s),CAS_amount[s]+50)
    elseif id == 9 then
        set CAS_amount[s] = IMinBJ(CasinoStakeMax(s),CAS_amount[s]*2)
    elseif id == 10 then
        set CAS_amount[s] = IMaxBJ(10,CAS_amount[s]/4*2)
    elseif id == 11 then
        call BJ_Wager(s)
    elseif id >= 12 and id <= 15 then
        call BJ_Action(s,id-11)
    elseif id >= 20 and id <= 24 then
        set MK_tab[s] = id-19
        set MK_page[s] = 0
        set MK_pick[s] = 0
    elseif id == 25 then
        set MK_page[s] = 1-MK_page[s]
    elseif id >= 26 and id <= 31 then
        set i = 1
        set count = 0
        set target = MK_page[s]*6+id-26
        loop
            exitwhen i > 12
            if MK_Valid(MK_tab[s],i) then
                if count == target then
                    set MK_pick[s] = i
                endif
                set count = count+1
            endif
            set i = i+1
        endloop
    elseif id == 32 then
        call MK_Buy(s,MK_tab[s],MK_pick[s])
    elseif id == 19 and CAS_view[s] == 6 then
        call AR_Invite(s,AR_SelectedStake(s))
    elseif id == 39 and CAS_view[s] == 3 then
        set CAS_view[s] = 6
    elseif id == 39 and CAS_view[s] == 6 then
        set CAS_view[s] = 3
    elseif id >= 53 and id <= 56 and CAS_view[s] == 6 then
        if id == 53 then
            set AR_pick[s] = AR_Next(s,AR_Target(s))
        elseif id == 54 then
            call AR_Invite(s,0)
        elseif id == 55 then
            if GetLocalPlayer() == Player(s-1) then
                call BlzSendSyncData("AR_Accept",I2S(AR_shownOffer))
            endif
        else
            call AR_Withdraw(s)
        endif
    elseif id == 33 then
        call DU_Offer(s)
    elseif id == 34 then
        set i = 0
        loop
            exitwhen i >= 24
            set DU_opponent[s] = ModuloInteger(DU_opponent[s],24)+1
            exitwhen DU_opponent[s] != s and PK_Eligible(DU_opponent[s]-1)
            set i = i+1
        endloop
    elseif id == 35 then
        set DU_pick[s] = CAS_CycleTarget(DU_pick[s])
    elseif id == 36 then
        call DU_Accept(s)
    elseif id == 37 then
        call DU_Cancel(DU_incoming[s])
    elseif id == 38 then
        call DU_Cancel(DU_outgoing[s])
    endif
    if CAS_view[s] == 1 then
        set CAS_amount[s] = IMinBJ(100,CAS_amount[s])
    endif
    if CAS_view[s] > 0 and PK_Started[s-1] then
        set PK_Hidden[s-1] = true
        call PK_Render(s-1)
    endif
    if id >= 6 and id <= 10 then
        set CAS_note[s] = "Selected bet is now "+I2S(CAS_amount[s])+"g."
    elseif id >= 26 and id <= 31 and MK_pick[s] > 0 then
        set CAS_note[s] = "Selected "+MK_Label(MK_tab[s],MK_pick[s])+"  /  wager "+I2S(CAS_amount[s])+"g"
    elseif id == 34 then
        set CAS_note[s] = "Challenge opponent  /  "+CAS_Name(DU_opponent[s])
    elseif id == 35 then
        set CAS_note[s] = "Backing  /  "+MK_Label(5,DU_pick[s])
    endif
    call CAS_Render(s)
    set f = null
endfunction

function CasinoFromStats takes nothing returns nothing
    local integer s = CasinoLauncherSlot
    if not PK_Eligible(s-1) then
        return
    endif
    set BJWatchHost[s] = 0
    set CAS_view[s] = 1
    set CAS_amount[s] = IMinBJ(100,CAS_amount[s])
    if CAS_root[s] == null then
        return
    endif
    if PK_Started[s-1] then
        set PK_Hidden[s-1] = true
        call PK_Render(s-1)
    endif
    if GetLocalPlayer() == Player(s-1) then
        set DPS_Open[s-1] = false
        call BlzFrameSetVisible(DPS_Panel,false)
    endif
    call CAS_Render(s)
endfunction

function CAS_Chat takes nothing returns nothing
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local string line = GetEventPlayerChatString()
    local string amount
    local integer value
    if not PK_Eligible(s-1) then
        return
    endif
    if SubString(line,0,7) != "-stake " then
        set BJWatchHost[s] = 0
    elseif CAS_view[s] == 1 and BJWatchHost[s] != 0 then
        return
    endif
    if line == "-casino" or line == "-blackjack" then
        set CAS_view[s] = 1
    elseif line == "-bets" then
        set CAS_view[s] = 2
    elseif line == "-arena" then
        set CAS_view[s] = 6
    elseif line == "-challenges" then
        set CAS_view[s] = 3
    elseif SubString(line,0,7) == "-stake " then
        set amount = SubString(line,7,StringLength(line))
        if HousePK_Started[s-1] and not HousePK_Hidden[s-1] then
            set value = S2I(amount)
            if I2S(value) == amount and value >= 10 and value <= 300 and ModuloInteger(value,2) == 0 then
                set HouseStake[s-1] = value
                set HousePK_Note[s-1] = "Next buy-in set to "+I2S(value)+"g."
            else
                set HousePK_Note[s-1] = "Choose an even buy-in from 10 to 300g."
            endif
            call HousePK_Render(s-1)
            return
        endif
        if PK_Started[s-1] and not PK_Hidden[s-1] then
            call PK_Submit(s-1,"b",amount)
            return
        endif
        set value = S2I(amount)
        if I2S(value) == amount and value >= 10 and value <= CasinoStakeMax(s) and ModuloInteger(value,2) == 0 then
            set CAS_amount[s] = value
            set CAS_note[s] = "Wager set to "+I2S(value)+" gold."
        else
            set CAS_note[s] = "Use -stake EVEN_AMOUNT, from 10 to "+I2S(CasinoStakeMax(s))+"."
        endif
    endif
    if CAS_view[s] == 1 then
        set CAS_amount[s] = IMinBJ(100,CAS_amount[s])
    endif
    if CAS_view[s] > 0 and PK_Started[s-1] then
        set PK_Hidden[s-1] = true
        call PK_Render(s-1)
    endif
    if PK_Started[s-1] and not PK_Hidden[s-1] then
        call PK_Render(s-1)
        call DisplayTextToPlayer(Player(s-1),0,0,CAS_note[s])
    endif
    call CAS_Render(s)
endfunction

function CAS_Tick takes nothing returns nothing
    local integer s = 1
    local integer id = 1
    local integer clientSlot = GetPlayerId(GetLocalPlayer())+1
    if CasinoAdmin(clientSlot) and not CAS_ready[clientSlot] and WalletBalance >= 0 and CasinoWalletRetries < 5 and ModuloInteger(CAS_seconds,5) == 0 then
        set CasinoWalletRetries = CasinoWalletRetries+1
        call WalletBroadcast()
    endif
    set CAS_seconds = R2I(TimerGetElapsed(FF_gameTimer))
    if not CAS_closed then
        call MK_Refresh()
    endif
    if CAS_seconds >= 120 and not CAS_warned then
        set CAS_warned = true
        call CAS_Announce("|cffe7cb88BETTING LAST CALL|r: all match markets close at 2:10. Open -bets for live odds.")
    endif
    if CAS_seconds >= 130 and not CAS_closed then
        set CAS_closed = true
        call CAS_Announce("|cffe7cb88MATCH BETTING CLOSED|r. Accepted odds are locked. Player challenges remain available.")
    endif
    if AR_state == 1 then
        call AR_Tick()
    endif
    call BJ_Tick()
    call HousePK_Tick()
    loop
        exitwhen id > DU_n
        if DU_state[id] == 1 and (CAS_seconds >= DU_expire[id] or not PK_Eligible(DU_from[id]-1) or not PK_Eligible(DU_to[id]-1)) then
            call DU_Cancel(id)
        endif
        set id = id+1
    endloop
    loop
        exitwhen s > 24
        if not PK_Eligible(s-1) then
            set CAS_view[s] = 0
        endif
        call CreditTick(s)
        if CAS_ready[s] then
            call CAS_Flush(s)
        endif
        if CAS_root[s] != null and CAS_User(s) then
            if GetLocalPlayer() == Player(s-1) then
                if CatalogCasino != null then
                    call BlzFrameSetVisible(CatalogCasino,CasinoAdmin(GetPlayerId(GetLocalPlayer())+1) and CatalogKind == 0)
                endif
            endif
            call CAS_Render(s)
        endif
        set s = s+1
    endloop
endfunction

function CAS_BuildPlayer takes integer s returns nothing
    local framehandle eye
    local framehandle icon
    local integer i = 0
    local integer b = s*32
    local integer c = s*18
    local real y
    local trigger click = CreateTrigger()
    set CreditDraftMode[s] = 1
    set CreditDraftRate[s] = 5
    set CreditDraftPeriod[s] = 5
    set BJ_table[s] = s
    set BJ_seat[s] = s*6
    set BJ_owner[s*6] = s
    set BJ_owner[s*6+1] = -1
    set BJ_owner[s*6+2] = -1
    call BJ_Shuffle(s)
    set CAS_amount[s] = 50
    set CAS_note[s] = "Blackjack accepts even bets from 10 to 100g."
    set MK_tab[s] = 1
    set CAS_root[s] = BlzCreateFrameByType("BACKDROP","CasinoTable",BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI,0),"",s)
    call BlzFrameSetSize(CAS_root[s],0.70,0.48)
    call BlzFrameSetAbsPoint(CAS_root[s],FRAMEPOINT_TOPLEFT,0.05,0.526)
    call BlzFrameSetTexture(CAS_root[s],"CasinoUI\\panel.blp",0,true)
    call BlzFrameSetLevel(CAS_root[s],60)
    call BlzFrameSetVisible(CAS_root[s],false)
    set CAS_felt[s] = CAS_Texture(s,"PokerUI\\table.blp",0.208,0.106,0.474,0.252)
    set CAS_title[s] = CAS_Label(s,0.025,0.016,0.53,0.027,1.15)
    set CAS_balance[s] = CAS_Label(s,0.025,0.041,0.65,0.026,1.13)
    set CAS_status[s] = CAS_Label(s,0.025,0.366,0.65,0.024,1.08)
    set BJWatchHistory[s] = CAS_Label(s,0.216,0.399,0.459,0.045,1.08)
    call BlzFrameSetVisible(BJWatchHistory[s],false)
    set CAS_footer[s] = CAS_Label(s,0.025,0.455,0.65,0.024,0.92)
    call CAS_Button(s,0,click,0.025,0.073,0.105,"Blackjack")
    call CAS_Button(s,1,click,0.134,0.073,0.105,"Match bets")
    call CAS_Button(s,2,click,0.243,0.073,0.105,"Duels")
    call CAS_Button(s,3,click,0.352,0.073,0.105,"Rules")
    call CAS_Button(s,4,click,0.575,0.014,0.10,"Hide")
    call CAS_Button(s,5,click,0.461,0.073,0.105,"Poker")
    call CAS_Button(s,60,click,0.419,0.014,0.150,"Lending record")
    call CAS_Button(s,59,click,0.440,0.014,0.130,"House poker")
    call CAS_Button(s,57,click,0.570,0.073,0.105,"Credit")
    call CAS_Button(s,40,click,0.025,0.182,0.145,"Lend / Borrow")
    call BlzFrameSetVisible(CAS_button[s*64+40],false)
    call CAS_Button(s,41,click,0.176,0.182,0.091,"-10g")
    call BlzFrameSetVisible(CAS_button[s*64+41],false)
    call CAS_Button(s,42,click,0.273,0.182,0.091,"+10g")
    call BlzFrameSetVisible(CAS_button[s*64+42],false)
    call CAS_Button(s,43,click,0.370,0.182,0.095,"+100g")
    call BlzFrameSetVisible(CAS_button[s*64+43],false)
    call CAS_Button(s,44,click,0.471,0.182,0.099,"-1%")
    call BlzFrameSetVisible(CAS_button[s*64+44],false)
    call CAS_Button(s,45,click,0.576,0.182,0.099,"+1%")
    call BlzFrameSetVisible(CAS_button[s*64+45],false)
    call CAS_Button(s,46,click,0.025,0.215,0.207,"Repay type")
    call BlzFrameSetVisible(CAS_button[s*64+46],false)
    call CAS_Button(s,47,click,0.456,0.215,0.219,"Post offer")
    call BlzFrameSetVisible(CAS_button[s*64+47],false)
    call CAS_Button(s,48,click,0.238,0.215,0.212,"Interval +")
    call BlzFrameSetVisible(CAS_button[s*64+48],false)
    call CAS_Button(s,49,click,0.025,0.310,0.158,"Previous")
    call BlzFrameSetVisible(CAS_button[s*64+49],false)
    call CAS_Button(s,50,click,0.189,0.310,0.158,"Next")
    call BlzFrameSetVisible(CAS_button[s*64+50],false)
    call CAS_Button(s,51,click,0.353,0.310,0.158,"Accept offer")
    call BlzFrameSetVisible(CAS_button[s*64+51],false)
    call CAS_Button(s,52,click,0.517,0.310,0.158,"Repay debt")
    call BlzFrameSetVisible(CAS_button[s*64+52],false)
    call CAS_Button(s,6,click,0.025,0.394,0.075,"-10")
    call CAS_Button(s,7,click,0.105,0.394,0.075,"+10")
    call CAS_Button(s,8,click,0.185,0.394,0.075,"+50")
    call CAS_Button(s,9,click,0.265,0.394,0.075,"2x")
    call CAS_Button(s,10,click,0.345,0.394,0.075,"Half")
    call CAS_Button(s,11,click,0.490,0.355,0.185,"Place bet")
    call BlzFrameSetSize(CAS_button[s*64+11],0.185,0.039)
    call CAS_Button(s,12,click,0.216,0.402,0.109,"Hit")
    call CAS_Button(s,13,click,0.332,0.402,0.109,"Stand")
    call CAS_Button(s,14,click,0.448,0.402,0.109,"Double")
    call CAS_Button(s,15,click,0.564,0.402,0.109,"Split")
    loop
        exitwhen i >= 4
        call BlzFrameSetSize(CAS_button[s*64+12+i],0.109,0.042)
        set i = i+1
    endloop
    set i = 0
    call CAS_Button(s,16,click,0.025,0.336,0.167,"More games")
    call CAS_Button(s,61,click,0.025,0.372,0.167,"My table")
    call BlzFrameSetVisible(CAS_button[s*64+16],false)
    call BlzFrameSetVisible(CAS_button[s*64+61],false)
    set i = 1
    loop
        exitwhen i > 24
        if i != s and GetPlayerSlotState(Player(i-1)) == PLAYER_SLOT_STATE_PLAYING then
            set eye = CUI_Create(CAS_root[s],s*25+i,0.159,-0.174,0.034,0.034,"",0)
            set BJWatchEye[s*25+i] = eye
            set icon = BlzCreateFrameByType("BACKDROP","BlackjackWatchIcon",eye,"",s*25+i)
            call BlzFrameSetAllPoints(icon,eye)
            call BlzFrameSetTexture(icon,"CasinoUI\\WatchEye.tga",0,true)
            call BlzFrameSetEnable(icon,false)
            call BlzFrameSetLevel(icon,66)
            call BlzTriggerRegisterFrameEvent(click,eye,FRAMEEVENT_CONTROL_CLICK)
            call BlzFrameSetVisible(eye,false)
        endif
        set i = i+1
    endloop
    set eye = null
    set icon = null
    set i = 0
    call CAS_Button(s,20,click,0.025,0.110,0.125,"Hero kill")
    call CAS_Button(s,21,click,0.155,0.110,0.125,"Base kill")
    call CAS_Button(s,22,click,0.285,0.110,0.125,"Base lost")
    call CAS_Button(s,23,click,0.415,0.110,0.125,"Level 16")
    call CAS_Button(s,24,click,0.545,0.110,0.13,"Win match")
    call CAS_Button(s,25,click,0.555,0.336,0.12,"MORE")
    call CAS_Button(s,32,click,0.43,0.394,0.245,"BET")
    call CAS_Button(s,33,click,0.43,0.394,0.245,"CHALLENGE")
    call CAS_Button(s,34,click,0.025,0.298,0.212,"Opponent >")
    call CAS_Button(s,35,click,0.244,0.298,0.212,"Winner >")
    call CAS_Button(s,36,click,0.025,0.333,0.212,"Accept")
    call CAS_Button(s,37,click,0.244,0.333,0.212,"Decline")
    call CAS_Button(s,38,click,0.463,0.333,0.212,"Cancel")
    call CAS_Button(s,39,click,0.463,0.298,0.212,"Arena 1v1")
    call CAS_Button(s,19,click,0.430,0.394,0.245,"Invite for gold")
    call CAS_Button(s,53,click,0.025,0.298,0.212,"Opponent >")
    call CAS_Button(s,54,click,0.244,0.298,0.212,"Invite free")
    call CAS_Button(s,55,click,0.025,0.333,0.212,"Accept")
    call CAS_Button(s,56,click,0.244,0.333,0.212,"Decline")
    set CAS_content[b] = CAS_Label(s,0.032,0.111,0.174,0.022,0.92)
    set CAS_content[b+1] = CAS_Label(s,0.032,0.137,0.174,0.038,1.01)
    set CAS_content[b+2] = CAS_Label(s,0.215,0.111,0.460,0.025,1.18)
    set CAS_content[b+3] = CAS_Label(s,0.215,0.227,0.460,0.040,1.85)
    set CAS_content[b+4] = CAS_Label(s,0.025,0.414,0.170,0.033,0.94)
    set BJ_wagerLabel[s] = CAS_Label(s,0.258,0.359,0.228,0.040,1.60)
    call BlzFrameSetVisible(BJ_wagerLabel[s],false)
    set CAS_content[b+5] = CAS_Label(s,0.445,0.227,0.230,0.040,1.85)
    set CAS_content[b+6] = CAS_Label(s,0.19,0.252,0.48,0.020,0.80)
    set CAS_content[b+7] = CAS_Label(s,0.025,0.143,0.65,0.021,0.95)
    set CAS_content[b+8] = CAS_Label(s,0.032,0.168,0.248,0.018,0.88)
    set CAS_content[b+9] = CAS_Label(s,0.025,0.330,0.52,0.035,0.85)
    set CAS_content[b+28] = CAS_Label(s,0.025,0.115,0.650,0.115,1.0)
    set CAS_content[b+29] = CAS_Label(s,0.025,0.246,0.650,0.050,1.0)
    set CAS_content[b+30] = CAS_Label(s,0.025,0.112,0.65,0.25,0.88)
    // Pool heading and values share their right edge.
    set CAS_content[b+31] = CAS_Label(s,0.290,0.168,0.140,0.018,0.88)
    call BlzFrameSetTextAlignment(CAS_content[b+2],TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_CENTER)
    call BlzFrameSetTextAlignment(CAS_content[b+3],TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_CENTER)
    call BlzFrameSetTextAlignment(CAS_content[b+5],TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_CENTER)
    call BlzFrameSetTextAlignment(CAS_content[b+31],TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_RIGHT)
    loop
        exitwhen i >= 6
        set y = 0.190+I2R(i)*0.023
        set CAS_content[b+10+i*3] = CAS_Label(s,0.032,y,0.248,0.021,0.96)
        set CAS_content[b+11+i*3] = CAS_Label(s,0.290,y,0.140,0.018,0.98)
        set CAS_content[b+12+i*3] = CAS_Label(s,0.443,y,0.095,0.021,1.09)
        call BlzFrameSetTextAlignment(CAS_content[b+11+i*3],TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_RIGHT)
        call BlzFrameSetTextAlignment(CAS_content[b+12+i*3],TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_RIGHT)
        call BlzFrameSetTextAlignment(CAS_content[b+10+i*3],TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_LEFT)
        set CAS_track[s*6+i] = CAS_Texture(s,"UI\\Widgets\\EscMenu\\Human\\blank-background.blp",CAS_SafeX(0.290),y+0.018,CAS_SafeW(0.140),0.003)
        call BlzFrameSetVertexColor(CAS_track[s*6+i],BlzConvertColor(255,30,55,49))
        set CAS_bar[s*6+i] = CAS_Texture(s,"UI\\Widgets\\EscMenu\\Human\\blank-background.blp",CAS_SafeX(0.290),y+0.018,CAS_SafeW(0.140),0.003)
        call BlzFrameSetVertexColor(CAS_bar[s*6+i],BlzConvertColor(255,214,184,106))
        call CAS_Button(s,26+i,click,0.555,y-0.003,0.12,"Select")
        call BlzFrameSetSize(CAS_button[s*64+26+i],CAS_SafeW(0.12),0.023)
        set CAS_row[s*6+i] = CAS_Label(s,0.025,0.174+I2R(i)*0.039,0.130,0.037,0.98)
        set CAS_seatTotal[s*6+i] = CAS_Label(s,0.159,0.179+I2R(i)*0.019,0.046,0.018,0.98)
        call BlzFrameSetTextAlignment(CAS_seatTotal[s*6+i],TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_RIGHT)
        set CAS_card[c+i] = CAS_Texture(s,"PokerUI\\empty.blp",0.195+I2R(i)*0.067,0.178,0.054,0.060)
        set CAS_card[c+6+i] = CAS_Texture(s,"PokerUI\\empty.blp",0.205+I2R(i)*0.028,0.274,0.050,0.072)
        set CAS_card[c+12+i] = CAS_Texture(s,"PokerUI\\empty.blp",0.430+I2R(i)*0.028,0.274,0.050,0.060)
        set i = i+1
    endloop
    set CAS_chip[s] = CAS_Texture(s,"PokerUI\\chips1.blp",0.216,0.363,0.038,0.021)
    call TriggerAddAction(click,function CAS_Click)
    call CAS_Render(s)
    if PK_Eligible(s-1) then
        call DisplayTimedTextToPlayer(Player(s-1),0,0,15,"Casino ready: -blackjack / -bets / -challenges. Wagers use your Wallet. Open Rules for table details.")
    endif
    set click = null
endfunction

function CAS_BuildNext takes nothing returns nothing
    set CAS_buildSlot = CAS_buildSlot+1
    if CAS_User(CAS_buildSlot) then
        call CAS_BuildPlayer(CAS_buildSlot)
    endif
    if CAS_buildSlot >= 24 then
        call DestroyTimer(GetExpiredTimer())
    endif
endfunction

function CAS_Init takes nothing returns nothing
    local trigger arenaAccept = CreateTrigger()
    local trigger loans = CreateTrigger()
    local trigger chat = CreateTrigger()
    local trigger death = CreateTrigger()
    local trigger level = CreateTrigger()
    local integer p = 0
    set CAS_winSound = CreateSound("Abilities\\Spells\\Items\\ResourceItems\\ReceiveGold.flac",false,false,false,0,0,"")
    call SetSoundVolume(CAS_winSound,100)
    set CAS_lossSound = CreateSound("Sound\\Interface\\MouseClick1.wav",false,false,false,0,0,"")
    call SetSoundVolume(CAS_lossSound,72)
    set HousePK_Seed = GetRandomInt(1,2147483646)
    set CAS_seed = GetRandomInt(1,2147483646)
    call AR_Init()
    call TriggerAddAction(arenaAccept,function AR_ReceiveAccept)
    set CasinoOpen = CreateTrigger()
    call TriggerAddAction(CasinoOpen,function CasinoFromStats)
    set CAS_baseEvent = CreateTrigger()
    set CAS_matchEvent = CreateTrigger()
    set MK_payTimer = CreateTimer()
    call TriggerAddAction(CAS_baseEvent,function MK_BaseDeath)
    call TriggerAddAction(CAS_matchEvent,function CAS_EndMatch)
    loop
        exitwhen p >= 24
        call TriggerRegisterPlayerChatEvent(loans,Player(p),"-loan ",false)
        call TriggerRegisterPlayerChatEvent(loans,Player(p),"-accept",true)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-casino",true)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-blackjack",true)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-bets",true)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-challenges",true)
        call BlzTriggerRegisterPlayerSyncEvent(arenaAccept,Player(p),"AR_Accept",false)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-arena",true)
        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-stake ",false)
        set p = p+1
    endloop
    call TriggerRegisterAnyUnitEventBJ(death,EVENT_PLAYER_UNIT_DEATH)
    call TriggerRegisterAnyUnitEventBJ(level,EVENT_PLAYER_HERO_LEVEL)
    call TriggerAddAction(loans,function FGA_OnCommand)
    set loans = null
    call TriggerAddAction(chat,function CAS_Chat)
    call TriggerAddAction(death,function MK_HeroDeath)
    call TriggerAddAction(level,function MK_Level)
    call TimerStart(CreateTimer(),0.20,true,function CAS_BuildNext)
    call TimerStart(CreateTimer(),1.00,true,function CAS_Tick)
    set chat = null
    set death = null
    set level = null
endfunction
