[CmdletBinding()]
param(
    [string]$ScriptPath,
    [string]$WtsPath
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ScriptPath)) {
    $ScriptPath = Join-Path $projectRoot 'src\war3map.j'
}
if ([string]::IsNullOrWhiteSpace($WtsPath)) {
    $WtsPath = Join-Path $projectRoot 'Disassembled Map\files\war3map.wts'
}
$script:Text = [IO.File]::ReadAllText($ScriptPath)

function Replace-RequiredRegex {
    param(
        [string]$Pattern,
        [string]$Replacement,
        [int]$Expected = 1,
        [string]$Label = $Pattern
    )
    $matches = [regex]::Matches($script:Text, $Pattern)
    if ($matches.Count -ne $Expected) {
        throw "$Label expected $Expected match(es), found $($matches.Count)"
    }
    $script:Text = [regex]::Replace($script:Text, $Pattern, $Replacement)
}

function Get-FunctionBlock {
    param([string]$Name)
    $pattern = '(?ms)^function\s+' + [regex]::Escape($Name) + '\s+takes\b.*?^endfunction\r?\n(?:\r?\n)?'
    $match = [regex]::Match($script:Text, $pattern)
    if (-not $match.Success) {
        throw "Function not found: $Name"
    }
    return $match.Value
}

function Replace-FunctionBlock {
    param([string]$Name, [string]$Replacement)
    $pattern = '(?ms)^function\s+' + [regex]::Escape($Name) + '\s+takes\b.*?^endfunction\r?\n(?:\r?\n)?'
    Replace-RequiredRegex -Pattern $pattern -Replacement ($Replacement.Trim() + "`r`n`r`n") -Label "function $Name"
}

function Remove-FunctionBlock {
    param([string]$Name)
    Replace-FunctionBlock -Name $Name -Replacement ''
}

# Ranking/export libraries and their editor-generated comment trigger.
Replace-RequiredRegex '(?ms)^//globals from MMD:.*?^//endglobals from MMD\r?\n' '' 1 'MMD globals'
Replace-RequiredRegex '(?ms)^//library MMD:.*?^//library MMD ends\r?\n' '' 1 'MMD library'
Replace-RequiredRegex '(?ms)^//===========================================================================\r?\n// Trigger: W3MMD Library\r?\n.*?(?=^//===========================================================================\r?\n// Trigger: init\r?\n)' '' 1 'W3MMD trigger comments'

# Full-map vote kick and ally base-transfer trigger blocks.
Replace-RequiredRegex '(?ms)^//===========================================================================\r?\n// Trigger: Votekick Initiate\r?\n.*?(?=^//===========================================================================\r?\n// Trigger: suicide\r?\n)' '' 1 'votekick triggers'
Replace-RequiredRegex '(?ms)^//===========================================================================\r?\n// Trigger: BASE destroy\r?\n.*?(?=^//===========================================================================\r?\n// Trigger: SHOP Redirect\r?\n)' '' 1 'ally base transfer trigger'

# W3Champions-only configuration trigger.
Replace-RequiredRegex '(?ms)^//===========================================================================\r?\n// Trigger: W3C JASS\r?\n.*?(?=^//===========================================================================\r?\n// Trigger: Observer Vision Fix\r?\n)' '' 1 'W3C trigger'

# Remove generated MMD struct helpers that live outside the library block.
$mmdFunctionNames = [regex]::Matches($script:Text, '(?m)^function\s+([A-Za-z0-9_]*MMD[A-Za-z0-9_]*)\s+takes') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
if ($mmdFunctionNames.Count -lt 4) {
    throw "Expected generated MMD helpers, found $($mmdFunctionNames.Count)"
}
foreach ($name in $mmdFunctionNames) {
    Remove-FunctionBlock $name
}

# Observer vision remains, but observer-to-player substitution does not.
Remove-FunctionBlock 'SoloSub_IsEffectivePlayer'
Remove-FunctionBlock 'SoloSub_RemoveObserverVision'
Replace-FunctionBlock 'Trig_Observer_Vision_Fix_Func001A' @'
function Trig_Observer_Vision_Fix_Func001A takes nothing returns nothing
    call CreateFogModifierRectBJ(true, GetEnumPlayer(), FOG_OF_WAR_VISIBLE, GetPlayableMapRect())
    if ( Trig_Observer_Vision_Fix_Func001Func004C() ) then
        call DestroyFogModifier(GetLastCreatedFogModifier())
    endif
endfunction
'@

# KOTH counts and pays only active Solo competitors.
Replace-FunctionBlock 'Trig_KOTH_Income_Func006Func001C' @'
function Trig_KOTH_Income_Func006Func001C takes nothing returns boolean
    local integer playerNumber=GetConvertedPlayerId(GetEnumPlayer())
    return playerNumber <= 12 and udg_player_active[playerNumber] and GetPlayerSlotState(GetEnumPlayer()) == PLAYER_SLOT_STATE_PLAYING
endfunction
'@
Replace-FunctionBlock 'Trig_KOTH_Income_Func014A' @'
function Trig_KOTH_Income_Func014A takes nothing returns nothing
    local integer playerNumber=GetConvertedPlayerId(GetEnumPlayer())
    if playerNumber <= 12 and udg_player_active[playerNumber] and GetPlayerSlotState(GetEnumPlayer()) == PLAYER_SLOT_STATE_PLAYING then
        call AdjustPlayerStateBJ(( udg_KOTH_Gold_To_Add + udg_KOTH_Gold_Division_To_Add ), GetEnumPlayer(), PLAYER_STATE_RESOURCE_GOLD)
        set udg_KOTH_Gold_Division_To_Add=0
    endif
endfunction
'@

# The administrator kick remains usable, without ally inheritance or vote-kick state.
Remove-FunctionBlock 'Trig_KICK_execute_Func011Func001Func009Func004C'
Remove-FunctionBlock 'Trig_KICK_execute_Func011Func001Func009Func006C'
Replace-FunctionBlock 'Trig_KICK_execute_Actions' @'
function Trig_KICK_execute_Actions takes nothing returns nothing
    if ( Trig_KICK_execute_Func002C() ) then
        set udg_New_Kick_Is_Active=false
        call DialogDisplayBJ(false, udg_New_Kick_Dialog, udg_New_Kick_Decider)
        set udg_temp_playergroup=GetForceOfPlayer(udg_New_Kick_Decider)
        call SoloFootsDisplayMessageToForce(udg_temp_playergroup, "TRIGSTR_5168")
        call DestroyForce(udg_temp_playergroup)
        return
    endif
    if ( Trig_KICK_execute_Func005C() ) then
        if ( Trig_KICK_execute_Func005Func001C() ) then
            set udg_New_Kick_Current_Page=( udg_New_Kick_Current_Page + 1 )
        else
            set udg_New_Kick_Current_Page=1
        endif
        call TriggerExecute(gg_trg_KICK_rebuild_dialog)
        return
    endif
    if ( Trig_KICK_execute_Func008C() ) then
        if ( Trig_KICK_execute_Func008Func001C() ) then
            set udg_New_Kick_Current_Page=( udg_New_Kick_Current_Page - 1 )
        else
            set udg_New_Kick_Current_Page=udg_New_Kick_Total_Pages
        endif
        call TriggerExecute(gg_trg_KICK_rebuild_dialog)
        return
    endif
    set udg_X=1
    loop
        exitwhen udg_X > 24
        if ( Trig_KICK_execute_Func011Func001C() ) then
            set udg_New_Kick_Is_Active=false
            call DialogDisplayBJ(false, udg_New_Kick_Dialog, udg_New_Kick_Decider)
            call SoloFootsDisplayMessageToForce(GetPlayersAll(), ( GetPlayerName(udg_New_Kick_Decider) + " has removed " + GetPlayerName(ConvertedPlayer(udg_X)) + " from the game." ))
            call CustomDefeatBJ(ConvertedPlayer(udg_X), "TRIGSTR_16610")
            if ( Trig_KICK_execute_Func011Func001Func009C() and udg_player_active[udg_X] ) then
                if udg_mode_koth and udg_KOTH_Team_Number == udg_teamnumber[udg_X] then
                    call TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
                    call TriggerExecute(gg_trg_KOTH_Reset_Hill)
                endif
                set SoloFoots_LastEliminatedPlayerNumber=udg_X
                set SoloFoots_FinalStrikePlayer=null
                set SoloFoots_FinalEliminationWasLeave=true
                set udg_player_active[udg_X]=false
                call ForceRemovePlayerSimple(ConvertedPlayer(udg_X), udg_Active_PlayGroup)
                set SafeRemoval_GraceTicks=0
                call EnableTrigger(gg_trg_Kill_units_of_inactive_player)
                call EnableTrigger(gg_trg_Visibility)
                call ConditionalTriggerExecute(gg_trg_Visibility)
                call ConditionalTriggerExecute(gg_trg_END)
                call EnableTrigger(gg_trg_check_if_team_active)
            endif
            return
        endif
        set udg_X=udg_X + 1
    endloop
endfunction
'@

# Draw remains a gameplay option, without departure state or match-metadata writes.
$drawBlock = Get-FunctionBlock 'Trig_draw_pressed_Actions'
$drawBlock = [regex]::Replace($drawBlock, '(?m)^\s*set udg_leave_or_votekick\[[^\r\n]*\r?\n', '')
$drawBlock = [regex]::Replace($drawBlock, '(?m)^\s*call MMD_[^\r\n]*\r?\n', '')
$drawBlock = [regex]::Replace($drawBlock, '(?m)^\s*call TriggerSleepAction\(0\.25\)\r?\n', '')
Replace-FunctionBlock 'Trig_draw_pressed_Actions' $drawBlock

Replace-FunctionBlock 'Trig_status_Actions' @'
function Trig_status_Actions takes nothing returns nothing
    set udg_temp_playergroup=GetForceOfPlayer(GetTriggerPlayer())
    set udg_X=1
    loop
        exitwhen udg_X > 12
        if udg_player_active[udg_X] then
            set udg_playerstatus[udg_X]="ACTIVE: |cff00ff00YES|r"
        else
            set udg_playerstatus[udg_X]="ACTIVE: |cffff0000NO|r"
        endif
        call SoloFootsDisplayMessageToForce(udg_temp_playergroup, ( GetPlayerName(ConvertedPlayer(udg_X)) + " " + udg_playerstatus[udg_X] ))
        set udg_X=udg_X + 1
    endloop
    call DestroyForce(udg_temp_playergroup)
endfunction
'@
Remove-FunctionBlock 'Trig_status_Func003Func002001'

# Team defeat is one active slot per team in Solo.
Replace-RequiredRegex '(?ms)^//===========================================================================\r?\n// Trigger: check if team active\r?\n.*?(?=^//===========================================================================\r?\n// Trigger: Kill units of inactive player\r?\n)' @'
//===========================================================================
// Trigger: check if team active
//===========================================================================
function Trig_check_if_team_active_Func002C takes nothing returns boolean
    return not udg_force_defeat[1] and not udg_player_active[1]
endfunction

function Trig_check_if_team_active_Func003C takes nothing returns boolean
    return not udg_force_defeat[2] and not udg_player_active[5]
endfunction

function Trig_check_if_team_active_Func004C takes nothing returns boolean
    return not udg_force_defeat[3] and not udg_player_active[8]
endfunction

function Trig_check_if_team_active_Func005C takes nothing returns boolean
    return not udg_force_defeat[4] and not udg_player_active[12]
endfunction

function Trig_check_if_team_active_Actions takes nothing returns nothing
    if ( Trig_check_if_team_active_Func002C() ) then
        set udg_force_defeat[1]=true
        set udg_player_active[1]=false
        set SafeRemoval_GraceTicks=0
        call EnableTrigger(gg_trg_Kill_units_of_inactive_player)
        call SoloFootsDisplayMessageToForce(udg_all_players, "TRIGSTR_2021")
    endif
    if ( Trig_check_if_team_active_Func003C() ) then
        set udg_force_defeat[2]=true
        set udg_player_active[5]=false
        set SafeRemoval_GraceTicks=0
        call EnableTrigger(gg_trg_Kill_units_of_inactive_player)
        call SoloFootsDisplayMessageToForce(udg_all_players, "TRIGSTR_2022")
    endif
    if ( Trig_check_if_team_active_Func004C() ) then
        set udg_force_defeat[3]=true
        set udg_player_active[8]=false
        set SafeRemoval_GraceTicks=0
        call EnableTrigger(gg_trg_Kill_units_of_inactive_player)
        call SoloFootsDisplayMessageToForce(udg_all_players, "TRIGSTR_2023")
    endif
    if ( Trig_check_if_team_active_Func005C() ) then
        set udg_force_defeat[4]=true
        set udg_player_active[12]=false
        set SafeRemoval_GraceTicks=0
        call EnableTrigger(gg_trg_Kill_units_of_inactive_player)
        call SoloFootsDisplayMessageToForce(udg_all_players, "TRIGSTR_2024")
    endif
endfunction

function InitTrig_check_if_team_active takes nothing returns nothing
    set gg_trg_check_if_team_active=CreateTrigger()
    call TriggerRegisterTimerEventPeriodic(gg_trg_check_if_team_active, 10.00)
    call TriggerAddAction(gg_trg_check_if_team_active, function Trig_check_if_team_active_Actions)
endfunction

'@ 1 'solo team-active trigger'

# Replace the full observer-substitution/ally-leave region with Solo leave cleanup.
Replace-RequiredRegex '(?ms)^//===========================================================================\r?\n// Trigger: player leaves\r?\n.*?(?=^//===========================================================================\r?\n// Trigger: player destroyed\r?\n)' @'
//===========================================================================
// Trigger: player leaves
//===========================================================================
function Trig_player_leaves_Actions takes nothing returns nothing
    local player leaver=GetTriggerPlayer()
    local integer playerNumber=GetConvertedPlayerId(leaver)
    if playerNumber > 12 or not udg_player_active[playerNumber] then
        set leaver=null
        return
    endif
    set udg_temp_player=leaver
    set udg_temp_playernumber=playerNumber
    set udg_autopoolto[playerNumber]=0
    if udg_mode_koth and udg_KOTH_Team_Number == udg_teamnumber[playerNumber] then
        call TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
        call TriggerExecute(gg_trg_KOTH_Reset_Hill)
    endif
    call SoloFootsDisplayMessageToForce(udg_all_players, ( GetPlayerName(leaver) + " has left the game..." ))
    call MultiboardDisplayBJ(false, GetLastCreatedMultiboard())
    call MultiboardDisplayBJ(true, GetLastCreatedMultiboard())
    set SoloFoots_LastEliminatedPlayerNumber=playerNumber
    set SoloFoots_FinalStrikePlayer=null
    set SoloFoots_FinalEliminationWasLeave=true
    set udg_player_active[playerNumber]=false
    call ForceRemovePlayerSimple(leaver, udg_Active_PlayGroup)
    set SafeRemoval_GraceTicks=0
    call EnableTrigger(gg_trg_Kill_units_of_inactive_player)
    call EnableTrigger(gg_trg_Visibility)
    call ConditionalTriggerExecute(gg_trg_Visibility)
    call ConditionalTriggerExecute(gg_trg_END)
    call EnableTrigger(gg_trg_check_if_team_active)
    set leaver=null
endfunction

function InitTrig_player_leaves takes nothing returns nothing
    set gg_trg_player_leaves=CreateTrigger()
    call TriggerRegisterPlayerEventLeave(gg_trg_player_leaves, Player(0))
    call TriggerRegisterPlayerEventLeave(gg_trg_player_leaves, Player(4))
    call TriggerRegisterPlayerEventLeave(gg_trg_player_leaves, Player(7))
    call TriggerRegisterPlayerEventLeave(gg_trg_player_leaves, Player(11))
    call TriggerAddAction(gg_trg_player_leaves, function Trig_player_leaves_Actions)
endfunction

'@ 1 'solo player-leave trigger'

# Base destruction eliminates only that Solo competitor; no ally gold/control handoff.
Replace-RequiredRegex '(?ms)^//===========================================================================\r?\n// Trigger: player destroyed\r?\n.*?(?=^//===========================================================================\r?\n// Trigger: Visibility\r?\n)' @'
//===========================================================================
// Trigger: player destroyed
//===========================================================================
function Trig_player_destroyed_Conditions takes nothing returns boolean
    return IsUnitType(GetDyingUnit(), UNIT_TYPE_TOWNHALL)
endfunction

function Trig_player_destroyed_Func010Func010002002 takes nothing returns boolean
    return GetUnitTypeId(GetFilterUnit()) != 'h04R'
endfunction

function Trig_player_destroyed_Func010Func011002 takes nothing returns nothing
    if IsUnitType(GetEnumUnit(), UNIT_TYPE_HERO) then
        call PauseUnit(GetEnumUnit(), true)
        call ShowUnit(GetEnumUnit(), false)
    else
        call KillUnit(GetEnumUnit())
    endif
endfunction

function Trig_player_destroyed_Actions takes nothing returns nothing
    local player defeatedPlayer=GetOwningPlayer(GetDyingUnit())
    local integer playerNumber=GetConvertedPlayerId(defeatedPlayer)
    if playerNumber > 12 or not udg_player_active[playerNumber] then
        set defeatedPlayer=null
        return
    endif
    set udg_temp_playernumber=playerNumber
    if GetKillingUnitBJ() != null then
        call SoloFootsDisplayMessageToForce(udg_all_players, ( GetPlayerName(defeatedPlayer) + " has been destroyed by " + GetPlayerName(GetOwningPlayer(GetKillingUnitBJ())) ))
    else
        call SoloFootsDisplayMessageToForce(udg_all_players, ( GetPlayerName(defeatedPlayer) + " has been destroyed." ))
    endif
    if udg_mode_koth and udg_KOTH_Team_Number == udg_teamnumber[playerNumber] then
        call TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
        call TriggerExecute(gg_trg_KOTH_Reset_Hill)
    endif
    set SoloFoots_LastEliminatedPlayerNumber=playerNumber
    if GetKillingUnitBJ() != null then
        set SoloFoots_FinalStrikePlayer=GetOwningPlayer(GetKillingUnitBJ())
    else
        set SoloFoots_FinalStrikePlayer=null
    endif
    set SoloFoots_FinalEliminationWasLeave=false
    set udg_player_active[playerNumber]=false
    call ForceRemovePlayerSimple(defeatedPlayer, udg_Active_PlayGroup)
    set SafeRemoval_GraceTicks=0
    call EnableTrigger(gg_trg_Kill_units_of_inactive_player)
    call EnableTrigger(gg_trg_Visibility)
    call ConditionalTriggerExecute(gg_trg_Visibility)
    call ConditionalTriggerExecute(gg_trg_END)
    set udg_unitgroup_kill=GetUnitsOfPlayerMatching(defeatedPlayer, Condition(function Trig_player_destroyed_Func010Func010002002))
    call ForGroupBJ(udg_unitgroup_kill, function Trig_player_destroyed_Func010Func011002)
    call DestroyGroup(udg_unitgroup_kill)
    call EnableTrigger(gg_trg_check_if_team_active)
    set defeatedPlayer=null
endfunction

function InitTrig_player_destroyed takes nothing returns nothing
    set gg_trg_player_destroyed=CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(gg_trg_player_destroyed, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddCondition(gg_trg_player_destroyed, Condition(function Trig_player_destroyed_Conditions))
    call TriggerAddAction(gg_trg_player_destroyed, function Trig_player_destroyed_Actions)
endfunction

'@ 1 'solo player-destroyed trigger'

# Keep normal Solo behavior after removing the W3Champions mode flag.
Replace-FunctionBlock 'Trig_admin_level_Conditions' @'
function Trig_admin_level_Conditions takes nothing returns boolean
    return true
endfunction
'@
Replace-FunctionBlock 'Trig_playernameandtag_Conditions' @'
function Trig_playernameandtag_Conditions takes nothing returns boolean
    return true
endfunction
'@
Replace-FunctionBlock 'Trig_Start_SD_Func013Func030C' @'
function Trig_Start_SD_Func013Func030C takes nothing returns boolean
    return false
endfunction
'@
Replace-FunctionBlock 'Trig_suicide_pressed_Conditions' @'
function Trig_suicide_pressed_Conditions takes nothing returns boolean
    return true
endfunction
'@
Replace-FunctionBlock 'Trig_Update_base_variable_Func005C' @'
function Trig_Update_base_variable_Func005C takes nothing returns boolean
    return false
endfunction
'@

# End-game latch and final-opponent announcement stay; placement/ranking output does not.
Remove-FunctionBlock 'SoloFootsDisplayFinalPlacements'
Replace-FunctionBlock 'SoloFootsRecordFinalPlacements' @'
function SoloFootsPrepareEndGame takes nothing returns boolean
    local integer winner
    local integer finalOpponent
    if SoloFoots_EndGameStarted then
        return false
    endif
    set winner=SoloFootsFindWinner()
    if winner == 0 then
        return false
    endif
    set finalOpponent=SoloFootsTeamRepresentative(SoloFoots_LastEliminatedPlayerNumber)
    if finalOpponent == 0 or finalOpponent == winner then
        return false
    endif
    set SoloFoots_FinalOpponentPlayerNumber=finalOpponent
    set SoloFoots_EndGameStarted=true
    return true
endfunction
'@
$script:Text = $script:Text.Replace('SoloFootsRecordFinalPlacements', 'SoloFootsPrepareEndGame')
$script:Text = $script:Text.Replace('SoloFoots_SecondPlacePlayerNumber', 'SoloFoots_FinalOpponentPlayerNumber')
$script:Text = $script:Text.Replace('SoloFoots_EndGameRecorded', 'SoloFoots_EndGameStarted')
$script:Text = [regex]::Replace($script:Text, '(?m)^integer SoloFoots_WinnerPlayerNumber= 0\r?\n', '')

$endBlock = Get-FunctionBlock 'Trig_END_Actions'
$endBlock = [regex]::Replace($endBlock, '(?m)^\s*call MMD_[^\r\n]*\r?\n', '')
$endBlock = [regex]::Replace($endBlock, '(?m)^\s*call TriggerSleepAction\(0\.25\)\r?\n', '')
$endBlock = [regex]::Replace($endBlock, '(?m)^(\s*)call TriggerSleepAction\(17\.25\)\r?\n', '$1call TriggerSleepAction(20.00)' + "`r`n")
$endBlock = [regex]::Replace($endBlock, '(?m)^\s*call s__File_close\(s__File_write\(s__File_open\("wc3mt\.txt"\),"wc3mt-GameEnd"\)\)\r?\n', '')
Replace-FunctionBlock 'Trig_END_Actions' $endBlock

# Anti-map-hack scoring remains local; no external match-data emission.
Remove-FunctionBlock 'AntiMH_Log'
Replace-FunctionBlock 'AntiMH_AddScore' @'
function AntiMH_AddScore takes integer playerIndex, integer amount, string kind, string detail returns nothing
    set AntiMH_Score[playerIndex]=AntiMH_Score[playerIndex] + amount
    if AntiMH_Score[playerIndex] >= 100 and not AntiMH_Flagged[playerIndex] then
        set AntiMH_Flagged[playerIndex]=true
    endif
endfunction
'@
$script:Text = [regex]::Replace($script:Text, '(?m)^\s*call AntiMH_Log\([^\r\n]*\r?\n', '')

# Remove GUI global initializers for deleted systems.
$initLoops = @(
    '(?ms)^    set i=0\r?\n    loop\r?\n        exitwhen \( i > 12 \)\r?\n        set udg_dlg_votekick\[i\]=DialogCreate\(\)\r?\n        set i=i \+ 1\r?\n    endloop\r?\n',
    '(?ms)^    set i=0\r?\n    loop\r?\n        exitwhen \( i > 24 \)\r?\n        set udg_leave_or_votekick\[i\]=false\r?\n        set i=i \+ 1\r?\n    endloop\r?\n',
    '(?ms)^    set i=0\r?\n    loop\r?\n        exitwhen \( i > 24 \)\r?\n        set udg_leaving_gold\[i\]=0\r?\n        set i=i \+ 1\r?\n    endloop\r?\n',
    '(?ms)^    set i=0\r?\n    loop\r?\n        exitwhen \( i > 1 \)\r?\n        set udg_Destroyer_Player_Number\[i\]=0\r?\n        set i=i \+ 1\r?\n    endloop\r?\n'
)
foreach ($pattern in $initLoops) {
    Replace-RequiredRegex $pattern '' 1 'deleted-system InitGlobals loop'
}
Replace-RequiredRegex '(?ms)^    set udg_Votekick_Is_Active=false\r?\n.*?^    set udg_Votekick_Defeat_Kicked_Player=false\r?\n' '' 1 'votekick InitGlobals block'

# Remove deleted globals without touching similarly named gameplay systems.
$globalsMatch = [regex]::Match($script:Text, '(?ms)\Aglobals\r?\n.*?^endglobals')
if (-not $globalsMatch.Success) {
    throw 'Global block not found'
}
$globalForbidden = '(?i)(SoloSub_|SoloTakeover_|Votekick|leave_or_votekick|(?:^|_)MMD(?:_|$)|W3MMD|udg_leaving_gold|udg_Destroyer_Player_Number|gg_trg_BASE_destroy|udg_version_W3C|gg_trg_W3C_JASS)'
$cleanGlobals = [regex]::Replace($globalsMatch.Value, '(?m)^[^\r\n]*' + $globalForbidden + '[^\r\n]*\r?\n', '')
$script:Text = $script:Text.Remove($globalsMatch.Index, $globalsMatch.Length).Insert($globalsMatch.Index, $cleanGlobals)

# Remove initializer calls and generated trigger setup for deleted systems.
$safeLinePatterns = @(
    '(?m)^\s*set udg_version_W3C=false\r?\n',
    '(?m)^\s*call InitTrig_(?:Votekick[A-Za-z0-9_]*|SoloSub_Command|SoloTakeover_Command|BASE_destroy|W3C_JASS)\(\)\r?\n',
    '(?m)^\s*//Function not found: call InitTrig_W3MMD_Library\(\)\r?\n',
    '(?m)^\s*call ConditionalTriggerExecute\(gg_trg_W3MMD_Library\)\r?\n',
    '(?m)^\s*call ExecuteFunc\("MMD___init"\)\r?\n',
    '(?m)^\s*set st__MMD[^\r\n]*\r?\n',
    '(?m)^\s*call TriggerAddCondition\(st__MMD[^\r\n]*\r?\n'
)
foreach ($pattern in $safeLinePatterns) {
    $script:Text = [regex]::Replace($script:Text, $pattern, '')
}
$script:Text = [regex]::Replace($script:Text, '(?im)^\s*//[^\r\n]*MMD[^\r\n]*\r?\n', '')

# Strong postcondition: none of the removed runtime systems may remain.
$forbiddenRuntime = '(?i)(SoloSub|SoloTakeover|Votekick|leave_or_votekick|W3MMD|\bMMD(?:_|\b)|\bW3C\b|version_W3C|W3C_JASS|wc3mt|udg_leaving_gold|udg_Destroyer_Player_Number|gg_trg_BASE_destroy|substitute request|departed teammate)'
$leftovers = [regex]::Matches($script:Text, $forbiddenRuntime)
if ($leftovers.Count -ne 0) {
    $samples = $leftovers | Select-Object -First 10 | ForEach-Object { $_.Value }
    throw "Forbidden runtime artifacts remain: $($samples -join ', ')"
}

$leaveBlock = Get-FunctionBlock 'Trig_player_leaves_Actions'
$destroyBlock = Get-FunctionBlock 'Trig_player_destroyed_Actions'
if ($leaveBlock -match '(?i)ally' -or $destroyBlock -match '(?i)ally') {
    throw 'Ally logic remains in Solo elimination triggers'
}

# Normalize source encoding/line endings to the map script's existing format.
$script:Text = $script:Text.Replace("`r`n", "`n").Replace("`r", "`n").Replace("`n", "`r`n")
[IO.File]::WriteAllText($ScriptPath, $script:Text, [Text.UTF8Encoding]::new($false))

# Remove dead vote-kick help/dialog text while preserving WTS keys and other help lines.
if (Test-Path -LiteralPath $WtsPath -PathType Leaf) {
    $wts = [IO.File]::ReadAllText($WtsPath)
    $wts = [regex]::Replace($wts, '(?im)^.*votekick.*\r?\n', '')
    $wts = $wts.Replace("`r`n", "`n").Replace("`r", "`n").Replace("`n", "`r`n")
    [IO.File]::WriteAllText($WtsPath, $wts, [Text.UTF8Encoding]::new($true))
}

[pscustomobject]@{
    ScriptPath = (Resolve-Path -LiteralPath $ScriptPath).Path
    ScriptBytes = (Get-Item -LiteralPath $ScriptPath).Length
    RemovedMmdHelpers = $mmdFunctionNames.Count
    RuntimeForbiddenMatches = 0
}
