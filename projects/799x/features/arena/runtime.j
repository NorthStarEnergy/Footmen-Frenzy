function AR_CanPlay takes integer s returns boolean
    if not CAS_User(s) then
        return false
    endif
    return GetPlayerController(Player(s-1)) == MAP_CONTROL_USER and not IsPlayerObserver(Player(s-1))
endfunction

function AR_Next takes integer s, integer fromSlot returns integer
    local integer i = 0
    loop
        exitwhen i >= 24
        set fromSlot = ModuloInteger(fromSlot,24)+1
        if fromSlot != s and AR_CanPlay(fromSlot) then
            return fromSlot
        endif
        set i = i+1
    endloop
    return 0
endfunction

function AR_Tell takes integer s, string msg returns nothing
    set CAS_note[s] = msg
    call DisplayTimedTextToPlayer(Player(s-1),0,0,12,msg)
endfunction

function AR_Target takes integer s returns integer
    if AR_pick[s] != s and AR_CanPlay(AR_pick[s]) then
        return AR_pick[s]
    endif
    return AR_Next(s,0)
endfunction

function AR_SelectedStake takes integer s returns integer
    return IMaxBJ(10,IMinBJ(10000,CAS_amount[s])/2*2)
endfunction

function AR_Terms takes integer stake returns string
    if stake == 0 then
        return "Free duel"
    endif
    return I2S(stake)+"g each  /  "+I2S(stake*2)+"g pot"
endfunction

function AR_CanFund takes integer s, integer stake returns boolean
    return CAS_ready[s] and CAS_gold[s] >= stake
endfunction

function AR_Invite takes integer s, integer stake returns nothing
    local integer other = AR_Target(s)
    if AR_state != 0 or CAS_ended or not AR_CanPlay(s) or not AR_CanPlay(other) or s == other then
        call AR_Tell(s,"Choose an available player when the arena is free.")
        return
    endif
    if stake != 0 and (stake != AR_SelectedStake(s) or not AR_CanFund(s,stake)) then
        call AR_Tell(s,"Your Wallet must cover the selected stake.")
        return
    endif
    set AR_offer = AR_offer+1
    set AR_stake = stake
    set AR_seat[0] = s
    set AR_seat[1] = other
    set AR_state = 1
    set AR_until = R2I(TimerGetElapsed(FF_gameTimer))+30
    call AR_Tell(s,"Arena invitation sent to "+CAS_Name(other)+". "+AR_Terms(stake)+".")
    call AR_Tell(other,CAS_Name(s)+" invites you to the arena. "+AR_Terms(stake)+". Type -arena and click Accept within 30 seconds.")
endfunction

// Borrow two empty owners so teammates can duel without changing their match alliance,
// inheriting army upgrades, spending player food, or putting a hero in a player's revive queue.
function AR_EmptyOwner takes player p, player exclude, group scratch returns boolean
    if p == exclude then
        return false
    endif
    call GroupEnumUnitsOfPlayer(scratch,p,null)
    return FirstOfGroup(scratch) == null
endfunction

function AR_FindOwner takes player exclude returns player
    local group g = CreateGroup()
    local player p = Player(bj_PLAYER_NEUTRAL_EXTRA)
    local integer i = 12
    if not AR_EmptyOwner(p,exclude,g) then
        set p = Player(bj_PLAYER_NEUTRAL_VICTIM)
        if not AR_EmptyOwner(p,exclude,g) then
            set p = null
            loop
                exitwhen i >= 24 or p != null
                if GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_EMPTY and AR_EmptyOwner(Player(i),exclude,g) then
                    set p = Player(i)
                endif
                set i = i+1
            endloop
        endif
    endif
    call DestroyGroup(g)
    set g = null
    return p
endfunction

function AR_Flag takes player a, player b, alliancetype flag, boolean value returns nothing
    if GetPlayerAlliance(a,b,flag) != value then
        set AR_flagFrom[AR_flagCount] = a
        set AR_flagTo[AR_flagCount] = b
        set AR_flagType[AR_flagCount] = flag
        set AR_flagBefore[AR_flagCount] = not value
        set AR_flagCount = AR_flagCount+1
        call SetPlayerAlliance(a,b,flag,value)
    endif
endfunction

function AR_Control takes integer side returns nothing
    local player p = AR_owner[side]
    local player human = Player(AR_seat[side]-1)
    local integer i = 0
    loop
        exitwhen i >= 24
        if Player(i) != p and Player(i) != AR_owner[1-side] then
            call AR_Flag(p,Player(i),ALLIANCE_PASSIVE,i != AR_seat[1-side]-1)
            call AR_Flag(Player(i),p,ALLIANCE_PASSIVE,i != AR_seat[1-side]-1)
            call AR_Flag(p,Player(i),ALLIANCE_SHARED_CONTROL,Player(i) == human)
            call AR_Flag(p,Player(i),ALLIANCE_SHARED_ADVANCED_CONTROL,Player(i) == human)
            call AR_Flag(p,Player(i),ALLIANCE_SHARED_XP,false)
        endif
        set i = i+1
    endloop
    call AR_Flag(p,AR_owner[1-side],ALLIANCE_PASSIVE,false)
    call AR_Flag(p,human,ALLIANCE_SHARED_VISION,true)
endfunction

function AR_EnterCamera takes integer side returns nothing
    local integer s = AR_seat[side]
    local player p = Player(s-1)
    set AR_vision[side] = CreateFogModifierRect(p,FOG_OF_WAR_VISIBLE,AR_floor,false,false)
    call FogModifierStart(AR_vision[side])
    set CAS_view[s] = 0
    set PK_Hidden[s-1] = true
    if GetLocalPlayer() == p then
        set AR_oldLeft = GetCameraBoundMinX()
        set AR_oldBottom = GetCameraBoundMinY()
        set AR_oldRight = GetCameraBoundMaxX()
        set AR_oldTop = GetCameraBoundMaxY()
        set AR_oldX = GetCameraTargetPositionX()
        set AR_oldY = GetCameraTargetPositionY()
        set AR_oldZoom = GetCameraField(CAMERA_FIELD_TARGET_DISTANCE)
        call BlzFrameSetVisible(CAS_root[s],false)
        if PK_Dialog[s-1] != null then
            call BlzFrameSetVisible(PK_Dialog[s-1],false)
        endif
        call ResetToGameCamera(0)
        call SetCameraField(CAMERA_FIELD_TARGET_DISTANCE,AR_oldZoom,0)
        call SetCameraBoundsToRect(AR_floor)
        call SetCameraPosition(GetUnitX(AR_hero[side]),GetUnitY(AR_hero[side]))
        call ClearSelection()
        call SelectUnit(AR_hero[side],true)
    endif
endfunction

function AR_End takes integer winner, string message returns nothing
    local integer side = 0
    local integer i = 0
    local integer s
    local boolean fighting = AR_state == 2
    if AR_state == 0 then
        return
    endif
    set AR_state = 0
    call PauseTimer(AR_clock)
    if AR_held[0]+AR_held[1] > 0 then
        if winner != 0 then
            set message = message+" Pot won: "+I2S(AR_held[0]+AR_held[1])+" Wallet gold."
        else
            set message = message+" Reserved gold returned."
        endif
    endif
    if AR_deaths != null then
        call DestroyTrigger(AR_deaths)
        set AR_deaths = null
    endif
    loop
        exitwhen side > 1
        set s = AR_seat[side]
        if AR_held[side] > 0 then
            set CAS_escrow[s] = CAS_escrow[s]-AR_held[side]
            if winner == 0 then
                call CAS_Credit(3,s,AR_held[side],0)
            elseif winner == s then
                call CAS_Credit(3,s,AR_held[side],AR_stake)
            endif
            set AR_held[side] = 0
        endif
        if fighting then
            if AR_vision[side] != null then
                call FogModifierStop(AR_vision[side])
                call DestroyFogModifier(AR_vision[side])
                set AR_vision[side] = null
                if GetLocalPlayer() == Player(s-1) then
                    call SetCameraBounds(AR_oldLeft,AR_oldBottom,AR_oldLeft,AR_oldTop,AR_oldRight,AR_oldTop,AR_oldRight,AR_oldBottom)
                    call SetCameraField(CAMERA_FIELD_TARGET_DISTANCE,AR_oldZoom,0)
                    call SetCameraPosition(AR_oldX,AR_oldY)
                    call ClearSelection()
                    if udg_herO[s] != null then
                        call SelectUnit(udg_herO[s],true)
                    endif
                endif
                set FF_oc_followed[s-1] = null
            endif
            if AR_scroll[side] != null then
                call RemoveItem(AR_scroll[side])
                set AR_scroll[side] = null
            endif
            call RemoveUnit(AR_hero[side])
            set AR_hero[side] = null
        endif
        call AR_Tell(s,message)
        set AR_seat[side] = 0
        set AR_owner[side] = null
        set side = side+1
    endloop
    set AR_stake = 0
    if fighting then
        call DisableTrigger(AR_damage)
        call DisableTrigger(AR_orders)
        loop
            exitwhen i >= 80
            call RemoveUnit(AR_foot[i])
            set AR_foot[i] = null
            set i = i+1
        endloop
        loop
            exitwhen AR_flagCount == 0
            set AR_flagCount = AR_flagCount-1
            call SetPlayerAlliance(AR_flagFrom[AR_flagCount],AR_flagTo[AR_flagCount],AR_flagType[AR_flagCount],AR_flagBefore[AR_flagCount])
        endloop
    endif
endfunction

function AR_Withdraw takes integer s returns nothing
    if s != AR_seat[0] and s != AR_seat[1] then
        return
    endif
    if AR_state == 1 then
        call AR_End(0,CAS_Name(s)+" closed the arena invitation.")
    elseif AR_state == 2 then
        if s == AR_seat[0] then
            call AR_End(AR_seat[1],CAS_Name(AR_seat[1])+" wins the duel by forfeit.")
        else
            call AR_End(AR_seat[0],CAS_Name(AR_seat[0])+" wins the duel by forfeit.")
        endif
    endif
endfunction

function AR_Alive takes unit u returns boolean
    return GetUnitTypeId(u) != 0 and GetWidgetLife(u) > 0.405 and not IsUnitType(u,UNIT_TYPE_DEAD)
endfunction

function AR_Contain takes unit u returns nothing
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    if not RectContainsCoords(AR_floor,x,y) and AR_Alive(u) then
        call SetUnitPosition(u,RMaxBJ(-976,RMinBJ(976,x)),RMaxBJ(5424,RMinBJ(6864,y)))
        call IssueImmediateOrder(u,"stop")
    endif
endfunction

function AR_Tick takes nothing returns nothing
    local integer i = 0
    local boolean left
    local boolean right
    if CAS_ended then
        call AR_End(0,"The main match ended. The arena is closed.")
    elseif AR_state == 1 then
        if R2I(TimerGetElapsed(FF_gameTimer)) >= AR_until or not AR_CanPlay(AR_seat[0]) or not AR_CanPlay(AR_seat[1]) then
            call AR_End(0,"Arena invitation expired.")
        endif
    elseif AR_state == 2 then
        set left = AR_Alive(AR_hero[0]) and AR_CanPlay(AR_seat[0])
        set right = AR_Alive(AR_hero[1]) and AR_CanPlay(AR_seat[1])
        if not left and not right then
            call AR_End(0,"Arena duel drawn. Both sides were eliminated.")
        elseif not left then
            call AR_End(AR_seat[1],CAS_Name(AR_seat[1])+" wins the arena duel!")
        elseif not right then
            call AR_End(AR_seat[0],CAS_Name(AR_seat[0])+" wins the arena duel!")
        else
            // Global Silence uses a native map-wide buff in addition to the match spell guard.
            call UnitRemoveAbility(AR_hero[0],'BGs1')
            call UnitRemoveAbility(AR_hero[0],'BGs2')
            call UnitRemoveAbility(AR_hero[1],'BGs1')
            call UnitRemoveAbility(AR_hero[1],'BGs2')
            call AR_Contain(AR_hero[0])
            call AR_Contain(AR_hero[1])
            loop
                exitwhen i >= 80
                call AR_Contain(AR_foot[i])
                set i = i+1
            endloop
        endif
    endif
endfunction

function AR_HeroDied takes nothing returns nothing
    // Let the native death event finish so all match event guards still see the arena owners.
    call TimerStart(AR_clock,0,false,function AR_Tick)
endfunction

function AR_Army takes integer side, integer roll returns boolean
    local integer i = 0
    local integer index
    local real sign = -1
    local real facing = 0
    local unit u
    local player p = AR_owner[side]
    local playercolor color = GetPlayerColor(Player(AR_seat[side]-1))
    if side == 1 then
        set sign = 1
        set facing = 180
    endif
    set u = CreateUnit(p,AR_roster[roll],sign*880,6144,facing)
    set AR_hero[side] = u
    if u == null then
        return false
    endif
    call SetUnitColor(u,color)
    call RemoveGuardPosition(u)
    call SuspendHeroXP(u,true)
    call SelectHeroSkill(u,AR_skill[roll])
    set AR_scroll[side] = CreateItem('sror',GetUnitX(u),GetUnitY(u))
    if AR_scroll[side] == null or not UnitAddItem(u,AR_scroll[side]) then
        set u = null
        return false
    endif
    call SetItemDroppable(AR_scroll[side],false)
    call SetItemPawnable(AR_scroll[side],false)
    call SetItemDropOnDeath(AR_scroll[side],false)
    loop
        exitwhen i >= 40
        set index = side*40+i
        set u = CreateUnit(p,'hfoo',sign*(464+80*(i/8)),6144+80*(ModuloInteger(i,8)-3.5),facing)
        set AR_foot[index] = u
        if u == null then
            return false
        endif
        call SetUnitColor(u,color)
        call SetUnitUseFood(u,false)
        call RemoveGuardPosition(u)
        set i = i+1
    endloop
    set u = null
    return true
endfunction

function AR_Accept takes integer s, integer offer returns nothing
    local integer roll
    local integer i = 0
    if AR_state != 1 or s != AR_seat[1] or offer != AR_offer then
        return
    endif
    call AR_Tick()
    if AR_state != 1 then
        return
    endif
    set AR_owner[0] = AR_FindOwner(null)
    set AR_owner[1] = AR_FindOwner(AR_owner[0])
    if AR_owner[0] == null or AR_owner[1] == null then
        call AR_End(0,"The arena could not reserve two empty army slots.")
        return
    endif
    if AR_stake > 0 then
        if not AR_CanFund(AR_seat[0],AR_stake) then
            call AR_End(0,"Invitation closed. The challenger can no longer cover the stake.")
            return
        endif
        if not AR_CanFund(s,AR_stake) then
            call AR_Tell(s,"You need "+I2S(AR_stake)+" Wallet gold to accept.")
            return
        endif
        if not CAS_Reserve(3,AR_seat[0],AR_stake,0) then
            call AR_End(0,"Invitation closed. The challenger's stake was unavailable.")
            return
        endif
        set AR_held[0] = AR_stake
        if not CAS_Reserve(3,s,AR_stake,0) then
            call AR_End(0,"Invitation closed. The matching stake was unavailable.")
            return
        endif
        set AR_held[1] = AR_stake
    endif
    set AR_state = 2
    call EnableTrigger(AR_damage)
    call EnableTrigger(AR_orders)
    call AR_Control(0)
    call AR_Control(1)
    set roll = GetRandomInt(0,5)
    if not AR_Army(0,roll) or not AR_Army(1,roll) then
        call AR_End(0,"Arena setup failed. The invitation has been cleared.")
        return
    endif
    set AR_deaths = CreateTrigger()
    call TriggerRegisterUnitEvent(AR_deaths,AR_hero[0],EVENT_UNIT_DEATH)
    call TriggerRegisterUnitEvent(AR_deaths,AR_hero[1],EVENT_UNIT_DEATH)
    call TriggerAddAction(AR_deaths,function AR_HeroDied)
    call AR_EnterCamera(0)
    call AR_EnterCamera(1)
    loop
        exitwhen i >= 80
        call IssuePointOrder(AR_foot[i],"attack",GetUnitX(AR_hero[1-i/40]),6144)
        set i = i+1
    endloop
    call AR_Tell(AR_seat[0],"Arena duel! Protect your "+GetUnitName(AR_hero[0])+" and kill the opposing hero.")
    call AR_Tell(AR_seat[1],"Arena duel! Protect your "+GetUnitName(AR_hero[1])+" and kill the opposing hero.")
    call TimerStart(AR_clock,0.125,true,function AR_Tick)
endfunction

function AR_ReceiveAccept takes nothing returns nothing
    call AR_Accept(GetPlayerId(GetTriggerPlayer())+1,S2I(BlzGetTriggerSyncData()))
endfunction
