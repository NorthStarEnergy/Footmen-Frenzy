function SF_RevealEliminated takes integer pn returns nothing
    if pn<1 or pn>12 then
        return
    endif
    if udg_player_active[pn] or F8_Team[pn-1]==0 then
        return
    endif
    if SF_EliminatedVision[pn]==null then
        set SF_EliminatedVision[pn]=CreateFogModifierRect(Player(pn-1),FOG_OF_WAR_VISIBLE,GetPlayableMapRect(),false,false)
        call FogModifierStart(SF_EliminatedVision[pn])
    endif
endfunction

function S8Player takes integer row returns integer
    return F8_Slot[row]+1
endfunction

function S8Team takes integer pn returns integer
    if pn<1 or pn>12 then
        return 9
    endif
    if F8_Team[pn-1]==0 then
        return 9
    endif
    return F8_Team[pn-1]
endfunction

function SKRestoreBaseControls takes integer pn returns nothing
    local unit b=udg_base[pn]
    call UnitRemoveAbility(b,'A0FS')
    call UnitRemoveAbility(b,'A0FR')
    if SKProduction[pn] then
        call UnitAddAbility(b,'A0FR')
    else
        call UnitAddAbility(b,'A0FS')
    endif
    call UnitRemoveAbility(b,'A06X')
    call UnitRemoveAbility(b,'A06Y')
    if udg_autosend[pn] then
        call UnitAddAbility(b,'A06Y')
    else
        call UnitAddAbility(b,'A06X')
    endif
    set b=null
endfunction

// Divide the complete hill payout across the current kingdom, including kingdoms of 4-8.
function SKHillIncome takes nothing returns nothing
    local integer owner=GetPlayerId(udg_KOTH_Player)+1
    local integer king
    local integer row=1
    local integer pn
    local integer count=0
    local integer payout
    local integer each
    local integer remainder
    if not SKActive(owner) then
        call TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
        return
    endif
    set king=SKKing[owner]
    loop
        exitwhen row>8
        set pn=S8Player(row)
        if SKActive(pn) and SKKing[pn]==king then
            set count=count+1
        endif
        set row=row+1
    endloop
    if count==0 then
        call PauseTimer(udg_KOTH_Income_Timer)
        return
    endif
    set payout=IMinBJ(udg_KOTH_Gold_Rewarded,udg_KOTH_Gold_Remaining)
    set each=payout/count
    set remainder=ModuloInteger(payout,count)
    set row=1
    loop
        exitwhen row>8
        set pn=S8Player(row)
        if SKActive(pn) and SKKing[pn]==king then
            call AdjustPlayerStateBJ(each,Player(pn-1),PLAYER_STATE_RESOURCE_GOLD)
        endif
        set row=row+1
    endloop
    call AdjustPlayerStateBJ(remainder,Player(king-1),PLAYER_STATE_RESOURCE_GOLD)
    set udg_KOTH_Team_Number=S8Team(king)
    set udg_KOTH_Team=udg_team[udg_KOTH_Team_Number]
    set udg_KOTH_Gold_Remaining=udg_KOTH_Gold_Remaining-payout
    set udg_KOTH_Team_Gold_Earned_Reset[udg_KOTH_Team_Number]=udg_KOTH_Team_Gold_Earned_Reset[udg_KOTH_Team_Number]+payout
    set udg_KOTH_Team_Gold_Earned_Total[udg_KOTH_Team_Number]=udg_KOTH_Team_Gold_Earned_Total[udg_KOTH_Team_Number]+payout
    if udg_KOTH_Gold_Remaining<=0 then
        call TriggerExecute(gg_trg_KOTH_Gold_Depleted)
    elseif udg_KOTH_Team_Gold_Earned_Reset[udg_KOTH_Team_Number]>=udg_KOTH_Gold_Reset_Amount then
        set udg_KOTH_Team_Gold_Earned_Reset[udg_KOTH_Team_Number]=0
        call TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
        call TriggerExecute(gg_trg_KOTH_Reset_Hill)
    endif
    call TriggerExecute(gg_trg_KOTH_Update_Text)
    call SKBoard()
endfunction

function SKChooseMode takes boolean kingMode returns nothing
    if SKModeChosen then
        return
    endif
    set SKModeChosen=true
    call PauseTimer(SKModeTimeout)
    if SKModeHost!=null then
        call DialogDisplay(SKModeHost,SKModeDialog,false)
    endif
    set SKEnabled=kingMode
    call TimerStart(SF_GameClock,86400.,false,null)
    if kingMode then
        call SKInit()
    else
        call DisplayTextToForce(udg_all_players,"Normal FFA selected. Each player fights independently.")
    endif
    call TimerStart(CreateTimer(),.01,false,function SF_StartBaseSelection)
endfunction

function SKModeClicked takes nothing returns nothing
    if GetTriggerPlayer()!=SKModeHost or SKModeChosen then
        return
    endif
    if GetClickedButton()==SKModeButton then
        call SKChooseMode(true)
    elseif GetClickedButton()==SKFfaButton then
        call SKChooseMode(false)
    endif
endfunction

function SKModeDefault takes nothing returns nothing
    call SKChooseMode(false)
endfunction

function SKOpenMode takes nothing returns nothing
    local integer row=1
    local integer pn
    local trigger t=CreateTrigger()
    call DestroyTimer(GetExpiredTimer())
    set SKModeDialog=DialogCreate()
    set SKModeTimeout=CreateTimer()
    loop
        exitwhen row>8 or SKModeHost!=null
        set pn=S8Player(row)
        if SKActive(pn) and GetPlayerController(Player(pn-1))==MAP_CONTROL_USER and GetPlayerSlotState(Player(pn-1))==PLAYER_SLOT_STATE_PLAYING then
            set SKModeHost=Player(pn-1)
        endif
        set row=row+1
    endloop
    if SKModeHost==null then
        call SKChooseMode(false)
    else
        call DialogSetMessage(SKModeDialog,"Choose game mode (FFA in 20 seconds)")
        set SKFfaButton=DialogAddButton(SKModeDialog,"Normal FFA",70)
        set SKModeButton=DialogAddButton(SKModeDialog,"King Mode - capture and defect",75)
        call TriggerRegisterDialogEvent(t,SKModeDialog)
        call TriggerAddAction(t,function SKModeClicked)
        call DialogDisplay(SKModeHost,SKModeDialog,true)
        call DisplayTextToForce(udg_all_players,GetPlayerName(SKModeHost)+" is choosing Normal FFA or King Mode.")
        call TimerStart(SKModeTimeout,20.,false,function SKModeDefault)
    endif
    set t=null
endfunction
