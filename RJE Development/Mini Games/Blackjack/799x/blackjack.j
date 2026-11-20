function BJ_Wager takes integer s returns nothing
    local integer t = BJ_table[s]
    local integer h = BJ_seat[s]*2
    local integer stake = CAS_amount[s]
    local integer i
    if stake < 10 or stake > 100 then
        set CAS_note[s] = "Blackjack opening bet: 10 to 100 gold."
        return
    endif
    if BJ_phase[t] == 4 then
        if t == 0 and BJ_clock[t] > 0 then
            set CAS_note[s] = "Next round opens in "+I2S(BJ_clock[t])+"s."
            return
        endif
        call BJ_Reset(t)
    endif
    if BJ_phase[t] > 1 or BJ_bet[h] > 0 then
        set CAS_note[s] = "Your wager is already placed, or a round is in progress."
        return
    endif
    if not CAS_Reserve(1,s,stake,stake*3/2) then
        return
    endif
    set BJWatchOlder[s] = ""
    set BJWatchPrevious[s] = ""
    set BJWatchLast[s] = "Bet "+I2S(stake)+"g"
    set BJ_bet[h] = stake
    set BJ_reserve[h] = stake*3/2
    set BJ_state[h] = 1
    if BJ_phase[t] == 0 then
        set BJ_phase[t] = 1
        set BJ_clock[t] = 12
        if t > 0 then
            set BJ_clock[t] = 3
            set i = 1
            loop
                exitwhen i > 2
                set BJ_bet[(t*6+i)*2] = stake
                set BJ_state[(t*6+i)*2] = 1
                set i = i+1
            endloop
        endif
    endif
    set CAS_note[s] = "Wager locked: "+I2S(stake)+" gold from your Wallet."
endfunction

function BJ_Value takes integer card returns integer
    if ModuloInteger(card,13) == 12 then
        return 11
    endif
    return IMinBJ(10,ModuloInteger(card,13)+2)
endfunction

function BJ_Payout takes integer total, boolean natural, integer dealer, boolean dealerNatural, integer bet returns integer
    if total > 21 then
        return 0
    elseif dealerNatural then
        if natural then
            return bet
        endif
        return 0
    elseif natural then
        return bet*5/2
    elseif dealer > 21 or total > dealer then
        return bet*2
    elseif total == dealer then
        return bet
    endif
    return 0
endfunction

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

function BJ_Shuffle takes integer t returns nothing
    local integer i = 0
    local integer j
    local integer temp
    loop
        exitwhen i >= 104
        set BJ_shoe[t*104+i] = ModuloInteger(i,52)
        set i = i+1
    endloop
    set i = 103
    loop
        exitwhen i <= 0
        set j = CAS_Random(i+1)
        set temp = BJ_shoe[t*104+i]
        set BJ_shoe[t*104+i] = BJ_shoe[t*104+j]
        set BJ_shoe[t*104+j] = temp
        set i = i-1
    endloop
    set BJ_pos[t] = 0
    set BJ_error[t] = false
endfunction

function BJ_Draw takes integer t returns integer
    local integer card
    if BJ_pos[t] >= 104 then
        set BJ_error[t] = true
        return 0
    endif
    set card = BJ_shoe[t*104+BJ_pos[t]]
    set BJ_pos[t] = BJ_pos[t]+1
    return card
endfunction

function BJ_Hit takes integer t, integer h returns nothing
    if BJ_count[h] >= 22 then
        set BJ_error[t] = true
        return
    endif
    set BJ_card[h*22+BJ_count[h]] = BJ_Draw(t)
    set BJ_count[h] = BJ_count[h]+1
    call BJ_Recount(h)
    if BJ_total[h] > 21 then
        set BJ_state[h] = 3
    elseif BJ_total[h] == 21 then
        set BJ_state[h] = 2
    endif
endfunction

function BJ_DealerHit takes integer t returns nothing
    local integer count = BJ_dealerCount[t]
    local integer before = BJ_CardSum(t,count,true)
    set BJ_dealerTotal[t] = before
    if count >= 2 and before >= 17 then
        return
    endif
    set BJ_dealerCard[t*22+count] = BJ_Draw(t)
    set BJ_dealerCount[t] = count+1
    set BJ_dealerTotal[t] = BJ_CardSum(t,count+1,true)
    if count >= 2 then
        set BJ_dealerAction[t] = "Hit on "+I2S(before)+"  /  now "+I2S(BJ_dealerTotal[t])
    endif
endfunction

function BJ_Finish takes integer t, boolean refund returns nothing
    local integer h = t*12
    local integer s
    local integer payout
    local integer stake
    loop
        exitwhen h >= t*12+12
        if BJ_bet[h] > 0 and BJ_state[h] != 5 then
            set stake = BJ_bet[h]
            set s = BJ_owner[h/2]
            if refund then
                set payout = stake
            else
                set payout = BJ_Payout(BJ_total[h],BJ_state[h] == 4,BJ_dealerTotal[t],BJ_dealerCount[t] == 2 and BJ_dealerTotal[t] == 21,stake)
            endif
            // Mark paid before touching the wallet: duplicate finish calls are harmless.
            set BJ_state[h] = 5
            if s > 0 then
                call CAS_Settle(1,s,stake,payout,BJ_reserve[h])
                call CAS_ResultSound(s,payout-stake)
                if refund then
                    set BJ_result[h] = "Round void / returned "+I2S(payout)
                elseif payout == stake then
                    set BJ_result[h] = "Push / returned "+I2S(payout)
                elseif payout > stake then
                    set BJ_result[h] = "Won +"+I2S(payout-stake)+" / return "+I2S(payout)
                else
                    set BJ_result[h] = "Lost "+I2S(stake)
                endif
                if ModuloInteger(h,2) == 1 then
                    set CAS_note[s] = "Hand 1: "+BJ_result[h-1]+"  /  Hand 2: "+BJ_result[h]
                else
                    set CAS_note[s] = BJ_result[h]
                endif
            endif
        endif
        set h = h+1
    endloop
    set BJ_reveal[t] = true
    set BJ_phase[t] = 4
    set BJ_clock[t] = 5
    set BJ_turn[t] = 0
endfunction

function BJ_Next takes integer t returns nothing
    local integer h = t*12
    local boolean compare = false
    if BJ_error[t] then
        call BJ_Finish(t,true)
        return
    endif
    loop
        exitwhen h >= t*12+12
        if BJ_state[h] == 2 and BJ_bet[h] > 0 then
            set compare = true
        endif
        if BJ_state[h] == 1 then
            set BJ_turn[t] = h+1
            set BJ_clock[t] = 20
            return
        endif
        set h = h+1
    endloop
    set BJ_turn[t] = 0
    if not compare then
        set BJ_dealerAction[t] = "No hands left to compare"
        call BJ_Finish(t,false)
        return
    endif
    set BJ_dealerAction[t] = "Hole card revealed"
    set BJ_phase[t] = 3
    set BJ_reveal[t] = true
    set BJ_clock[t] = 2
endfunction

function BJ_Deal takes integer t returns nothing
    local integer h
    local integer dealPass = 0
    // The cut card triggers before the next round; live cards are never recycled.
    if BJ_pos[t] > 26 then
        call BJ_Shuffle(t)
    endif
    set BJ_dealerAction[t] = ""
    set BJ_round[t] = BJ_round[t]+1
    set BJ_dealerCount[t] = 0
    set BJ_dealerTotal[t] = 0
    set BJ_dealerAces[t] = 0
    set BJ_reveal[t] = false
    loop
        exitwhen dealPass >= 2
        set h = t*12
        loop
            exitwhen h >= t*12+12
            if BJ_bet[h] > 0 then
                set BJ_state[h] = 1
                call BJ_Hit(t,h)
            endif
            set h = h+2
        endloop
        call BJ_DealerHit(t)
        set dealPass = dealPass+1
    endloop
    set h = t*12
    loop
        exitwhen h >= t*12+12
        if BJ_bet[h] > 0 and BJ_total[h] == 21 then
            set BJ_state[h] = 4
        endif
        set h = h+2
    endloop
    set BJ_phase[t] = 2
    if BJ_error[t] then
        call BJ_Finish(t,true)
    elseif BJ_dealerTotal[t] == 21 then
        set BJ_dealerAction[t] = "Blackjack"
        call BJ_Finish(t,false)
    else
        call BJ_Next(t)
    endif
endfunction

function BJ_Reset takes integer t returns nothing
    local integer h = t*12
    loop
        exitwhen h >= t*12+12
        set BJ_count[h] = 0
        set BJ_total[h] = 0
        set BJ_aces[h] = 0
        set BJ_state[h] = 0
        set BJ_bet[h] = 0
        set BJ_reserve[h] = 0
        set BJ_split[h] = false
        set BJ_result[h] = ""
        set h = h+1
    endloop
    set BJ_dealerCount[t] = 0
    set BJ_dealerTotal[t] = 0
    set BJ_reveal[t] = false
    set BJ_phase[t] = 0
endfunction

function BJWatchActive takes integer host returns boolean
    return host > 0 and PK_Eligible(host-1) and not CAS_ended and BJ_phase[host] >= 1 and (BJ_phase[host] <= 3 or (BJ_phase[host] == 4 and BJ_clock[host] > 0))
endfunction

function BJWatchRecord takes integer host, string action returns nothing
    set BJWatchOlder[host] = BJWatchPrevious[host]
    set BJWatchPrevious[host] = BJWatchLast[host]
    set BJWatchLast[host] = action
endfunction

function BJWatchAction takes integer s, integer hand, integer action returns nothing
    local string detail
    if action == 1 then
        set detail = "Hit"
    elseif action == 2 then
        set detail = "Stand"
    elseif action == 3 then
        set detail = "Double"
    else
        set detail = "Split"
    endif
    if BJ_split[hand] and action != 4 then
        set detail = detail+" (hand "+I2S(ModuloInteger(hand,2)+1)+")"
    endif
    call BJWatchRecord(s,detail)
endfunction

function BJ_Action takes integer s, integer action returns nothing
    local integer t = BJ_table[s]
    local integer h = BJ_turn[t]-1
    local integer stake
    local integer card
    if not PK_Eligible(s-1) or BJ_phase[t] != 2 or h < 0 or BJ_owner[h/2] != s or BJ_state[h] != 1 then
        return
    endif
    if action == 1 then
        call BJ_Hit(t,h)
        set BJ_clock[t] = 20
        set CAS_note[s] = "Hit  /  drew "+PK_Card(BJ_card[h*22+BJ_count[h]-1])+"  /  total "+I2S(BJ_total[h])
    elseif action == 2 then
        set CAS_note[s] = "Standing on "+I2S(BJ_total[h])
        set BJ_state[h] = 2
    elseif action == 3 then
        if BJ_count[h] != 2 or BJ_bet[h] > 10000 or (BJ_split[h] and ModuloInteger(BJ_card[h*22],13) == 12) then
            return
        endif
        set stake = BJ_bet[h]
        if not CAS_Reserve(1,s,stake,stake*3/2) then
            return
        endif
        set CAS_note[s] = "Doubled  /  wager now "+I2S(stake*2)+"g"
        set BJ_bet[h] = stake*2
        set BJ_reserve[h] = BJ_reserve[h]+stake*3/2
        call BJ_Hit(t,h)
        if BJ_state[h] == 1 then
            set BJ_state[h] = 2
        endif
    elseif action == 4 then
        if BJ_count[h] != 2 or BJ_split[h] or ModuloInteger(h,2) != 0 or BJ_Value(BJ_card[h*22]) != BJ_Value(BJ_card[h*22+1]) or (ModuloInteger(BJ_card[h*22],13) == 12) != (ModuloInteger(BJ_card[h*22+1],13) == 12) then
            return
        endif
        set stake = BJ_bet[h]
        if not CAS_Reserve(1,s,stake,stake*3/2) then
            return
        endif
        set CAS_note[s] = "Split  /  "+I2S(stake)+"g on each hand"
        set card = BJ_card[h*22+1]
        set BJ_count[h] = 1
        set BJ_count[h+1] = 1
        set BJ_card[(h+1)*22] = card
        set BJ_bet[h+1] = stake
        set BJ_reserve[h+1] = stake*3/2
        set BJ_split[h] = true
        set BJ_split[h+1] = true
        set BJ_state[h+1] = 1
        call BJ_Hit(t,h)
        call BJ_Hit(t,h+1)
        if ModuloInteger(card,13) == 12 then
            set BJ_state[h] = 2
            set BJ_state[h+1] = 2
        endif
    endif
    call BJWatchAction(s,h,action)
    if BJ_error[t] then
        call BJ_Finish(t,true)
    elseif BJ_state[h] != 1 then
        call BJ_Next(t)
    endif
endfunction

function BJ_Tick takes nothing returns nothing
    local integer t = 1
    local integer h
    local integer s
    loop
        exitwhen t > 24
        if BJ_phase[t] == 1 then
            set BJ_clock[t] = BJ_clock[t]-1
            if BJ_clock[t] <= 0 then
                call BJ_Deal(t)
            endif
        elseif BJ_phase[t] == 2 then
            set h = BJ_turn[t]-1
            set s = BJ_owner[h/2]
            set BJ_clock[t] = BJ_clock[t]-1
            if s < 0 then
                if BJ_total[h] < 17 then
                    call BJ_Hit(t,h)
                else
                    set BJ_state[h] = 2
                endif
                if BJ_state[h] != 1 then
                    call BJ_Next(t)
                elseif BJ_error[t] then
                    call BJ_Finish(t,true)
                endif
            elseif BJ_clock[t] <= 0 or not PK_Eligible(s-1) then
                call BJWatchRecord(s,"Auto-stand")
                set BJ_state[h] = 2
                call BJ_Next(t)
            endif
        elseif BJ_phase[t] == 3 then
            set BJ_clock[t] = BJ_clock[t]-1
            if BJ_clock[t] <= 0 then
                if BJ_CardSum(t,BJ_dealerCount[t],true) < 17 then
                    call BJ_DealerHit(t)
                    set BJ_clock[t] = 1
                    if BJ_error[t] then
                        call BJ_Finish(t,true)
                    endif
                else
                    if BJ_dealerTotal[t] > 21 then
                        set BJ_dealerAction[t] = "Bust on "+I2S(BJ_dealerTotal[t])
                    else
                        set BJ_dealerAction[t] = "Stands on "+I2S(BJ_dealerTotal[t])
                    endif
                    call BJ_Finish(t,false)
                endif
            endif
        elseif BJ_phase[t] == 4 then
            set BJ_clock[t] = IMaxBJ(0,BJ_clock[t]-1)
        endif
        set t = t+1
    endloop
endfunction

function BJ_Summary takes integer h returns string
    local string text = I2S(BJ_total[h])
    if BJ_total[h] > 21 then
        return "|cffff9090BUST "+text+"|r"
    elseif BJ_state[h] == 4 then
        return "|cffe7cb88BLACKJACK 21|r"
    elseif BJ_state[h] == 1 then
        return CUI_Value(text)
    elseif BJ_state[h] == 0 then
        return "--"
    endif
    return CUI_Value(text)
endfunction

function BJ_SeatTotal takes integer hand returns string
    if BJ_state[hand] == 0 then
        return "--"
    elseif BJ_total[hand] > 21 then
        return "|cffff9090"+I2S(BJ_total[hand])+"|r"
    endif
    return CUI_Value(I2S(BJ_total[hand]))
endfunction

function BJ_CardStart takes real center, integer count, real width, real spacing returns real
    local integer visible = IMaxBJ(2,IMinBJ(6,count))
    return center-(width+I2R(visible-1)*spacing)*0.5
endfunction

function BJWatchList takes integer s returns nothing
    local integer host = 1
    local integer count = 0
    local integer index = 0
    local integer row
    local integer key
    local integer pages
    local integer hand
    local boolean show
    local framehandle eye
    local string name
    loop
        exitwhen host > 24
        if host != s and BJWatchActive(host) then
            set count = count+1
        endif
        set host = host+1
    endloop
    set pages = IMaxBJ(1,(count+3)/4)
    set BJWatchPage[s] = ModuloInteger(BJWatchPage[s],pages)
    set host = 1
    loop
        exitwhen host > 24
        set key = s*25+host
        set eye = BJWatchEye[key]
        if eye != null then
            set show = false
            if BJWatchActive(host) then
                set show = CAS_view[s] == 1 and index/4 == BJWatchPage[s]
                if show then
                    set row = ModuloInteger(index,4)
                    set hand = BJ_seat[host]*2
                    set name = CAS_Name(host)
                    if StringLength(name) > 14 then
                        set name = SubString(name,0,14)+"..."
                    endif
                    call BlzFrameSetText(CAS_row[s*6+row],name+"|n"+CUI_Value(I2S(BJ_bet[hand]+BJ_bet[hand+1])+"g"))
                    call BlzFrameSetVisible(CAS_row[s*6+row],true)
                    call BlzFrameSetPoint(eye,FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,0.159,-0.174-0.039*I2R(row))
                endif
                set index = index+1
            endif
            call BlzFrameSetVisible(eye,show)
        endif
        set host = host+1
    endloop
    call BlzFrameSetVisible(CAS_button[s*64+16],CAS_view[s] == 1 and pages > 1)
    call CUI_Text(CAS_button[s*64+16],"Games "+I2S(BJWatchPage[s]+1)+"/"+I2S(pages)+" >")
    call BlzFrameSetVisible(CAS_button[s*64+61],CAS_view[s] == 1 and BJWatchHost[s] > 0)
    if CAS_view[s] == 1 then
        call BlzFrameSetText(CAS_content[s*32],"LIVE GAMES  "+I2S(count))
        call BlzFrameSetVisible(CAS_content[s*32],true)
        if count == 0 then
            call BlzFrameSetText(CAS_row[s*6],"No other games")
            call BlzFrameSetVisible(CAS_row[s*6],true)
        endif
    endif
    set eye = null
endfunction

function CAS_BlackjackView takes integer s, integer host returns nothing
    local integer t = BJ_table[host]
    local integer h = BJ_seat[host]*2
    local integer b = s*32
    local integer c = s*18
    local integer i = 0
    local integer card
    local real dealerX
    local real handX
    local real splitX = 0.0
    local real cardWidth = 0.060
    local real cardHeight = 0.082
    local real spacing = 0.067
    local boolean turn = BJ_phase[t] == 2 and BJ_turn[t]-1 >= h and BJ_turn[t]-1 <= h+1
    local boolean ownTable = host == s
    local boolean betting = ownTable and not CAS_ended and (BJ_phase[t] == 0 or BJ_phase[t] == 4)
    local string history = BJWatchOlder[host]
    local string phase = "PLACE BET"
    local string dealer = "DEALER"
    local string first = "YOU"
    local string second = "HAND 2"
    if not ownTable then
        set first = SubString(CAS_Name(host),0,16)
    endif
    if BJ_phase[t] == 1 then
        set phase = "DEAL IN "+CUI_Value(I2S(BJ_clock[t])+"s")
    elseif BJ_phase[t] == 2 then
        set phase = CAS_Name(BJ_owner[(BJ_turn[t]-1)/2])+" / "+CUI_Value(I2S(BJ_clock[t])+"s")
        if turn and ownTable then
            set phase = "YOUR TURN / "+CUI_Value(I2S(BJ_clock[t])+"s")
        endif
    elseif BJ_phase[t] == 3 then
        set phase = "DEALER'S TURN"
    elseif BJ_phase[t] == 4 then
        set phase = "NEXT ROUND"
    endif
    call BlzFrameSetText(CAS_content[b+1],phase)
    call BlzFrameSetVisible(CAS_content[b+1],true)
    if BJ_reveal[t] then
        set dealer = dealer+"  "+CUI_Value(I2S(BJ_dealerTotal[t]))+"   /   "+BJ_dealerAction[t]
    elseif BJ_dealerCount[t] > 0 then
        set dealer = dealer+"   /   Shows "+PK_Card(BJ_dealerCard[t*22])+"   /   Hole card down"
    endif
    call BlzFrameSetText(CAS_content[b+2],dealer)
    call BlzFrameSetVisible(CAS_content[b+2],true)
    set dealerX = BJ_CardStart(0.445,BJ_dealerCount[t],0.054,0.067)
    if BJ_split[h] then
        set first = "HAND 1"
        if turn then
            if BJ_turn[t]-1 == h then
                set first = "> HAND 1"
            else
                set second = "> HAND 2"
            endif
        endif
        set cardWidth = 0.043
        set cardHeight = 0.062
        set spacing = 0.028
        set handX = BJ_CardStart(0.330,BJ_count[h],cardWidth,spacing)
        set splitX = BJ_CardStart(0.560,BJ_count[h+1],cardWidth,spacing)
        call BlzFrameSetSize(CAS_content[b+3],0.230,0.040)
        call BlzFrameSetText(CAS_content[b+5],second+"  "+BJ_Summary(h+1)+"  /  "+I2S(BJ_bet[h+1])+"g")
        call BlzFrameSetVisible(CAS_content[b+5],true)
    else
        set handX = BJ_CardStart(0.445,BJ_count[h],cardWidth,spacing)
        call BlzFrameSetSize(CAS_content[b+3],0.460,0.040)
    endif
    call BlzFrameSetText(CAS_content[b+3],first+"  "+BJ_Summary(h)+"  /  "+I2S(BJ_bet[h])+"g")
    call BlzFrameSetVisible(CAS_content[b+3],true)
    loop
        exitwhen i >= 6
        call BlzFrameSetPoint(CAS_card[c+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,dealerX+I2R(i)*0.067,-0.140)
        call BlzFrameSetSize(CAS_card[c+i],0.054,0.078)
        set card = -1
        if i < BJ_dealerCount[t] then
            set card = BJ_dealerCard[t*22+i]
        endif
        call CAS_CardFace(CAS_card[c+i],card,i == 1 and BJ_dealerCount[t] > 1 and not BJ_reveal[t])
        call BlzFrameSetVisible(CAS_card[c+i],i < IMaxBJ(2,BJ_dealerCount[t]))
        set card = -1
        if i < BJ_count[h] then
            set card = BJ_card[h*22+i]
        endif
        call BlzFrameSetPoint(CAS_card[c+6+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,handX+I2R(i)*spacing,-0.268)
        call BlzFrameSetSize(CAS_card[c+6+i],cardWidth,cardHeight)
        call CAS_CardFace(CAS_card[c+6+i],card,false)
        call BlzFrameSetVisible(CAS_card[c+6+i],i < IMaxBJ(2,BJ_count[h]))
        if BJ_split[h] then
            set card = -1
            if i < BJ_count[h+1] then
                set card = BJ_card[(h+1)*22+i]
            endif
            call BlzFrameSetPoint(CAS_card[c+12+i],FRAMEPOINT_TOPLEFT,CAS_root[s],FRAMEPOINT_TOPLEFT,splitX+I2R(i)*spacing,-0.268)
            call BlzFrameSetSize(CAS_card[c+12+i],cardWidth,cardHeight)
            call CAS_CardFace(CAS_card[c+12+i],card,false)
            call BlzFrameSetVisible(CAS_card[c+12+i],i < IMaxBJ(2,BJ_count[h+1]))
        endif
        set i = i+1
    endloop
    if BJ_count[h] > 6 or BJ_count[h+1] > 6 or BJ_dealerCount[t] > 6 then
        call BlzFrameSetText(CAS_content[b+4],"First 6 cards shown")
    elseif BJ_phase[t] >= 2 then
        call BlzFrameSetText(CAS_content[b+4],"Bots   "+BJ_SeatTotal(h+2)+" / "+BJ_SeatTotal(h+4))
    else
        call BlzFrameSetText(CAS_content[b+4],"Private table + 2 bots")
    endif
    call BlzFrameSetVisible(CAS_content[b+4],true)
    call BlzFrameSetVisible(CAS_chip[s],true)
    if betting then
        call PK_ChipArt(CAS_chip[s],CAS_amount[s])
    else
        call PK_ChipArt(CAS_chip[s],BJ_bet[h]+BJ_bet[h+1])
    endif
    if betting then
        call BlzFrameSetText(BJ_wagerLabel[s],"NEXT BET   "+CUI_Value(I2S(CAS_amount[s])+"g"))
    else
        call BlzFrameSetText(BJ_wagerLabel[s],"WAGER   "+CUI_Value(I2S(BJ_bet[h]+BJ_bet[h+1])+"g"))
    endif
    set i = 6
    loop
        exitwhen i > 10
        call BlzFrameSetVisible(CAS_button[s*64+i],betting)
        set i = i+1
    endloop
    call CAS_ShowButton(s,11,not CAS_ended and CAS_ready[s] and CAS_gold[s] >= CAS_amount[s] and (BJ_phase[t] == 0 or (BJ_phase[t] == 4 and (t != 0 or BJ_clock[t] == 0)) or (BJ_phase[t] == 1 and BJ_bet[h] == 0)))
    call CAS_ShowButton(s,12,turn)
    call CAS_ShowButton(s,13,turn)
    call CAS_ShowButton(s,14,turn and CAS_gold[s] >= BJ_bet[BJ_turn[t]-1] and BJ_count[BJ_turn[t]-1] == 2)
    call CAS_ShowButton(s,15,turn and CAS_gold[s] >= BJ_bet[BJ_turn[t]-1] and not BJ_split[h] and BJ_count[h] == 2 and BJ_Value(BJ_card[h*22]) == BJ_Value(BJ_card[h*22+1]) and (ModuloInteger(BJ_card[h*22],13) == 12) == (ModuloInteger(BJ_card[h*22+1],13) == 12))
    call BlzFrameSetVisible(CAS_button[s*64+11],betting)
    set i = 12
    loop
        exitwhen i > 15
        call BlzFrameSetVisible(CAS_button[s*64+i],ownTable and turn)
        set i = i+1
    endloop
    if BJWatchPrevious[host] != "" then
        if history != "" then
            set history = history+"  >  "
        endif
        set history = history+BJWatchPrevious[host]
    endif
    if BJWatchLast[host] != "" then
        if history != "" then
            set history = history+"  >  "
        endif
        set history = history+BJWatchLast[host]
    endif
    call BlzFrameSetText(BJWatchHistory[s],history)
    call BlzFrameSetVisible(BJWatchHistory[s],not betting and (not ownTable or not turn))
endfunction
