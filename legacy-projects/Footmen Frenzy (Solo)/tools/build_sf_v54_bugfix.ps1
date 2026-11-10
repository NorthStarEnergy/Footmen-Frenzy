<#
    build_sf_v54_bugfix.ps1

    Reproducible build of SF_Test1.7_v54 from the verified SF_Test1.7_v53_TEST baseline.

    Three reported bugs:

      B1. Players can build more than one Altar of Kings.
          Root cause: "Altar limit" fired on CONSTRUCT_FINISH and revoked upgrade 'R00I'.
          'R00I' occurs exactly once in the whole map - its own definition in war3map.w3q.
          No unit, ability, item or upgrade lists it as a requirement (0 hits across w3u,
          w3a, w3t, w3b, w3d), so revoking it gated nothing. 'hhou' ureq is 'R00H' only,
          which is the 300s altar delay. The limit has therefore never worked.
          Fix: fire on CONSTRUCT_START, disable 'hhou' for that player, cancel a duplicate
          if two placements slip through in the same tick, and re-enable 'hhou' when the
          altar dies or its construction is cancelled.

      B2. No second hero until ~30 minutes.
          Root cause: all six altar summon abilities (A0H7, A0EO, A0GE, A0EA, A0EG, A0GG)
          carry areq='R00J', arqa='1'. 'R00J' is granted only by "Third Hero Delay" at
          t=1800s, and Trig_Altar_Hero_Summon revokes it on use. So the altar's buttons
          were dead for the first 30 minutes.
          Fix: grant 'R00J' at Start_game alongside 'R00I'. The 1800s grant is deliberately
          kept (Ryan's call, 2026-08-07): it now hands out a charge for a third hero.

      B3. Mass foot spawn is ~45 degrees out of phase.
          v52 ("spawnfix") replaced the per-quadrant bracket formation with a single
          diagonal line per team running out toward that team's corner. Every army ended
          up rotated 45 degrees off the axes it used to line up on.
          Fix: restore the v7..v51 coordinates verbatim (taken from
          roundtrip\SF_Test1.7_v49\files\war3map.j). Roar caster offsets were already
          per-quadrant in both versions and are untouched.

    Usage:
      pwsh -File tools\build_sf_v54_bugfix.ps1
      pwsh -File tools\build_sf_v54_bugfix.ps1 -Force
#>

[CmdletBinding()]
param(
    [string] $Root         = 'C:\Users\Ryan1\Documents\Solo Foots Development',
    [string] $FfTools      = 'C:\Users\Ryan1\Documents\Footmen Frenzy Development\tools',
    [string] $BaselineName = 'SF_Test1.7_v53_TEST',
    [string] $Version      = 'SF_Test1.7_v54',
    [switch] $Force
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$BaselineMap = Join-Path $Root "releases\$BaselineName.w3x"
$BuildDir    = Join-Path $Root "outputs\$Version-bugfix"
$BaseDir     = Join-Path $BuildDir 'base'
$EditedDir   = Join-Path $BuildDir 'edited'
$VerifyDir   = Join-Path $BuildDir 'verified'
$OutMap      = Join-Path $Root "releases\$Version.w3x"
$SrcScript   = Join-Path $Root 'src\war3map.j'
$RoundTrip   = Join-Path $Root "roundtrip\$Version\files"
$DeliverDir  = Join-Path 'C:\Users\Ryan1\Documents\Warcraft III\Maps\Solo Foots\GPT' $Version

$MapExtract = Join-Path $FfTools 'MapExtract\bin\Release\net6.0\MapExtract.exe'
$JassCheck  = Join-Path $FfTools 'JassCheck\bin\Release\net6.0\JassCheck.exe'
# This archive has no (listfile); ReplaceWar3MapScript resolves the member by hash.
$Packer     = Join-Path $Root 'tools\bin\ReplaceWar3MapScript\ReplaceWar3MapScript.exe'
$Pjass      = 'C:\Program Files\Warcraft III\_retail_\x86_64\JassHelper\pjass.exe'
$CommonJ    = 'C:\Users\Ryan1\Documents\Warcraft III\JassHelper\common.j'
$BlizzardJ  = 'C:\Users\Ryan1\Documents\Warcraft III\JassHelper\Blizzard.j'
$Latin1     = [System.Text.Encoding]::GetEncoding(28591)

function Fail([string]$m) { throw "BUILD STOPPED: $m" }
function Step([string]$m) { Write-Host "==> $m" }
function Sha([string]$p) { (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash }
function ReadText([string]$p) { $Latin1.GetString([IO.File]::ReadAllBytes($p)) }
function WriteText([string]$p, [string]$t) { [IO.File]::WriteAllBytes($p, $Latin1.GetBytes($t)) }
# war3map.j is mixed: ~47.8k CRLF lines and 73 lone-LF lines. Anchors must reproduce the
# ending the target region actually uses, so every splice states it explicitly.
function CRLF([string[]]$lines) { ($lines -join "`r`n") + "`r`n" }
function LF  ([string[]]$lines) { ($lines -join "`n")   + "`n" }

# ------------------------------------------------- 0. preflight guards ----
Step 'Preflight'
foreach ($p in @($BaselineMap, $SrcScript, $MapExtract, $Packer, $JassCheck, $Pjass, $CommonJ, $BlizzardJ)) {
    if (-not (Test-Path -LiteralPath $p)) { Fail "missing required input: $p" }
}
if (Test-Path -LiteralPath $BuildDir) {
    if (-not $Force) { Fail "build directory already exists (refusing to reuse): $BuildDir" }
    Remove-Item -LiteralPath $BuildDir -Recurse -Force
}
foreach ($p in @($OutMap, $RoundTrip, $DeliverDir)) {
    if (Test-Path -LiteralPath $p) { Fail "output already exists (refusing to overwrite): $p" }
}
New-Item -ItemType Directory -Force -Path $BuildDir, $EditedDir | Out-Null

# ----------------------------------------------- 1. extract the baseline ---
Step 'Extract baseline'
& $MapExtract $BaselineMap $BaseDir | Out-Null
if ($LASTEXITCODE -ne 0) { Fail 'MapExtract failed on the baseline map' }
$BaseScript = Join-Path $BaseDir 'war3map.j'
if (-not (Test-Path -LiteralPath $BaseScript)) { Fail 'baseline extraction produced no war3map.j' }
$baseScriptSha = Sha $BaseScript
$baseText = ReadText $BaseScript
$actualSha = Sha $BaselineMap
Write-Host "    baseline war3map.j $((Get-Item -LiteralPath $BaseScript).Length) bytes $baseScriptSha"
if ((Sha $SrcScript) -ne $baseScriptSha) { Fail "src\war3map.j is not the script inside $BaselineName - another build landed; re-baseline" }

# --------------------------------------------------------- 2. the edits ---
Step 'Edit war3map.j'
$script = $baseText
$editLog = New-Object System.Collections.Generic.List[string]

function Splice([string]$name, [string]$from, [string]$to, [string]$note) {
    $hits = ([regex]::Matches($script:script, [regex]::Escape($from))).Count
    if ($hits -ne 1) { Fail "edit '$name' matched $hits anchor(s), expected exactly 1" }
    $script:script = $script:script.Replace($from, $to)
    $script:editLog.Add("$name : $note")
}

# --- B3. restore the pre-v52 mass formation (this region is lone-LF) -------
Splice 'b3-mass-formation' `
    (LF @(
        '    // Spawn the matching batch for all four teams on the same simulation tick.',
        '    // Each team now occupies one diagonal line in its own quadrant. The nearest',
        '    // batch stops 240 units from both center axes, leaving an initial enemy gap.',
        '    if ( sf_mass_batch_step == 1 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 10, -240.00, 240.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 10, 240.00, 240.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 10, 240.00, -240.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 10, -240.00, -240.00)',
        '    elseif ( sf_mass_batch_step == 2 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 13, -450.00, 450.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 13, 450.00, 450.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 13, 450.00, -450.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 13, -450.00, -450.00)',
        '    elseif ( sf_mass_batch_step == 3 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 12, -660.00, 660.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 12, 660.00, 660.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 12, 660.00, -660.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 12, -660.00, -660.00)',
        '    elseif ( sf_mass_batch_step == 4 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 12, -870.00, 870.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 12, 870.00, 870.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 12, 870.00, -870.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 12, -870.00, -870.00)',
        '    elseif ( sf_mass_batch_step == 5 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 13, -1080.00, 1080.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 13, 1080.00, 1080.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 13, 1080.00, -1080.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 13, -1080.00, -1080.00)',
        '    elseif ( sf_mass_batch_step == 6 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 13, -1290.00, 1290.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 13, 1290.00, 1290.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 13, 1290.00, -1290.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 13, -1290.00, -1290.00)',
        '    elseif ( sf_mass_batch_step == 7 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 12, -1500.00, 1500.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 12, 1500.00, 1500.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 12, 1500.00, -1500.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 12, -1500.00, -1500.00)'
    )) `
    (LF @(
        '    // Spawn the matching batch for all four teams on the same simulation tick.',
        '    // Each team brackets its own quadrant with two arms laid along the map axes,',
        '    // so adjacent teams meet head-on across the axis they share. v52 replaced this',
        '    // with one diagonal line per team running out to that team''s corner, which put',
        '    // every army 45 degrees off. These are the v7..v51 coordinates, restored.',
        '    if ( sf_mass_batch_step == 1 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 10, -60.00, 1000.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 10, 60.00, 1000.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 10, 1000.00, 60.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 10, -1000.00, -60.00)',
        '    elseif ( sf_mass_batch_step == 2 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 13, -60.00, 650.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 13, 60.00, 650.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 13, 650.00, 60.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 13, -650.00, -60.00)',
        '    elseif ( sf_mass_batch_step == 3 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 12, -60.00, 200.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 12, 60.00, 200.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 12, 200.00, 60.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 12, -200.00, -60.00)',
        '    elseif ( sf_mass_batch_step == 4 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 12, -221.00, -200.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 12, 221.00, -200.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 12, 200.00, -221.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 12, -200.00, -221.00)',
        '    elseif ( sf_mass_batch_step == 5 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 13, -475.00, -200.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 13, 475.00, -200.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 13, 200.00, -475.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 13, -200.00, -475.00)',
        '    elseif ( sf_mass_batch_step == 6 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 13, -850.00, -200.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 13, 850.00, -200.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 13, 200.00, -850.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 13, -200.00, -850.00)',
        '    elseif ( sf_mass_batch_step == 7 ) then',
        '        call SoloFootsMassSpawnBatch(Player(0), 12, -1100.00, -200.00)',
        '        call SoloFootsMassSpawnBatch(Player(4), 12, 1100.00, -200.00)',
        '        call SoloFootsMassSpawnBatch(Player(7), 12, 200.00, -1100.00)',
        '        call SoloFootsMassSpawnBatch(Player(11), 12, -200.00, -1100.00)'
    )) `
    'mass formation restored to the v7..v51 per-quadrant brackets'

# --- B2. grant R00J at game start so the altar can summon hero #2 ----------
Splice 'b2-grant-r00j-at-start' `
    (CRLF @(
        "    call SetPlayerTechResearchedSwap('R00I', 1, GetEnumPlayer())",
        '    // T1 Unavailable'
    )) `
    (CRLF @(
        "    call SetPlayerTechResearchedSwap('R00I', 1, GetEnumPlayer())",
        "    // The altar's six summon abilities all require 'R00J'. It used to be granted only",
        '    // by "Third Hero Delay" at t=1800s, which left the altar useless for the first 30',
        '    // minutes. Grant it here for hero #2; the 1800s grant still lands, for hero #3.',
        "    call SetPlayerTechResearchedSwap('R00J', 1, GetEnumPlayer())",
        '    // T1 Unavailable'
    )) `
    "'R00J' granted at Start_game"

# --- B1. make the altar limit actually limit -------------------------------
Splice 'b1-altar-limit' `
    (CRLF @(
        'function Trig_Altar_limit_Func002C takes nothing returns boolean',
        "    if ( ( GetUnitTypeId(GetTriggerUnit()) == 'hhou' ) ) then",
        '        return true',
        '    endif',
        '    return false',
        'endfunction',
        '',
        'function Trig_Altar_limit_Conditions takes nothing returns boolean',
        '    if ( not Trig_Altar_limit_Func002C() ) then',
        '        return false',
        '    endif',
        '    return true',
        'endfunction',
        '',
        'function Trig_Altar_limit_Actions takes nothing returns nothing',
        "    call SetPlayerTechResearchedSwap('R00I', 0, GetOwningPlayer(GetTriggerUnit()))",
        'endfunction',
        '',
        '//===========================================================================',
        'function InitTrig_Altar_limit takes nothing returns nothing',
        '    set gg_trg_Altar_limit=CreateTrigger()',
        '    call TriggerRegisterAnyUnitEventBJ(gg_trg_Altar_limit, EVENT_PLAYER_UNIT_CONSTRUCT_FINISH)',
        '    call TriggerAddCondition(gg_trg_Altar_limit, Condition(function Trig_Altar_limit_Conditions))',
        '    call TriggerAddAction(gg_trg_Altar_limit, function Trig_Altar_limit_Actions)',
        'endfunction'
    )) `
    (CRLF @(
        "// One altar at a time. The old version fired on CONSTRUCT_FINISH and revoked 'R00I',",
        '// but nothing in the object data requires that upgrade - it appears exactly once in the',
        "// whole map, as its own definition in war3map.w3q. 'hhou' requires only 'R00H', the 300s",
        '// altar delay. So the limit gated nothing and players could stack altars.',
        'function Trig_Altar_limit_Conditions takes nothing returns boolean',
        "    return GetUnitTypeId(GetConstructingStructure()) == 'hhou'",
        'endfunction',
        '',
        'function Trig_Altar_limit_CountAltars takes player owner returns integer',
        '    local group g=CreateGroup()',
        '    local integer i=0',
        '    local integer size',
        '    local integer count=0',
        '    local unit checked=null',
        '    call GroupEnumUnitsOfPlayer(g, owner, null)',
        '    set size=BlzGroupGetSize(g)',
        '    loop',
        '        exitwhen i >= size',
        '        set checked=BlzGroupUnitAt(g, i)',
        "        if GetUnitTypeId(checked) == 'hhou' and GetUnitState(checked, UNIT_STATE_LIFE) > 0.00 then",
        '            set count=count + 1',
        '        endif',
        '        set i=i + 1',
        '    endloop',
        '    call GroupClear(g)',
        '    call DestroyGroup(g)',
        '    set g=null',
        '    set checked=null',
        '    return count',
        'endfunction',
        '',
        'function Trig_Altar_limit_Actions takes nothing returns nothing',
        '    local unit built=GetConstructingStructure()',
        '    local player owner=GetOwningPlayer(built)',
        '    // `built` is already in the count, so >1 means one was standing before this one.',
        '    // That only happens if two placements land in the same tick, before the button',
        '    // is greyed out; cancelling refunds the player.',
        '    if Trig_Altar_limit_CountAltars(owner) > 1 then',
        '        call IssueImmediateOrder(built, "cancel")',
        '    else',
        "        call SetPlayerUnitAvailableBJ('hhou', false, owner)",
        '    endif',
        '    set built=null',
        '    set owner=null',
        'endfunction',
        '',
        '//===========================================================================',
        'function InitTrig_Altar_limit takes nothing returns nothing',
        '    set gg_trg_Altar_limit=CreateTrigger()',
        '    call TriggerRegisterAnyUnitEventBJ(gg_trg_Altar_limit, EVENT_PLAYER_UNIT_CONSTRUCT_START)',
        '    call TriggerAddCondition(gg_trg_Altar_limit, Condition(function Trig_Altar_limit_Conditions))',
        '    call TriggerAddAction(gg_trg_Altar_limit, function Trig_Altar_limit_Actions)',
        'endfunction',
        '',
        '//===========================================================================',
        '// Trigger: Altar limit release',
        '//',
        '// Hands the build button back once the altar is gone, so "one at a time" does not',
        '// become "one per game".',
        '//===========================================================================',
        'function Trig_Altar_limit_Release_Conditions takes nothing returns boolean',
        "    return GetUnitTypeId(GetTriggerUnit()) == 'hhou'",
        'endfunction',
        '',
        'function Trig_Altar_limit_Release_Actions takes nothing returns nothing',
        "    call SetPlayerUnitAvailableBJ('hhou', true, GetOwningPlayer(GetTriggerUnit()))",
        'endfunction',
        '',
        '//===========================================================================',
        'function InitTrig_Altar_limit_Release takes nothing returns nothing',
        '    local trigger t=CreateTrigger()',
        '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)',
        '    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_CONSTRUCT_CANCEL)',
        '    call TriggerAddCondition(t, Condition(function Trig_Altar_limit_Release_Conditions))',
        '    call TriggerAddAction(t, function Trig_Altar_limit_Release_Actions)',
        '    set t=null',
        'endfunction'
    )) `
    'altar limit moved to CONSTRUCT_START with a release trigger'

Splice 'b1-altar-limit-init' `
    (CRLF @('    call InitTrig_Altar_limit()')) `
    (CRLF @('    call InitTrig_Altar_limit()', '    call InitTrig_Altar_limit_Release()')) `
    'InitTrig_Altar_limit_Release wired into InitCustomTriggers'

# --- version stamp (this line is lone-LF) ----------------------------------
Splice 'version-stamp' `
    (LF @('    call SetMapName("Footmen Frenzy Solo TEST v53")')) `
    (LF @('    call SetMapName("Footmen Frenzy Solo TEST v54")')) `
    'map name bumped to v54'

$EditedScript = Join-Path $EditedDir 'war3map.j'
WriteText $EditedScript $script
$editedSha = Sha $EditedScript
Write-Host "    wrote $EditedScript ($((Get-Item -LiteralPath $EditedScript).Length) bytes)"
$editLog | ForEach-Object { Write-Host "    $_" }

# ------------------------------------------------------ 3. validate JASS ---
Step 'Validate JASS'
& $JassCheck $EditedScript
if ($LASTEXITCODE -ne 0) { Fail 'JassCheck (War3Net syntax parse) failed' }
$pjassOut = & $Pjass $CommonJ $BlizzardJ $EditedScript 2>&1 | Out-String
Write-Host $pjassOut
if ($pjassOut -notmatch 'Parse successful.*war3map\.j') { Fail "pjass rejected the edited script:`n$pjassOut" }
if ($pjassOut -match 'error') { Fail "pjass reported errors:`n$pjassOut" }

# -------------------------------------------- 4. static acceptance checks --
Step 'Static acceptance checks'
$checks = New-Object System.Collections.Generic.List[object]
function Check([string]$name, [bool]$ok, [string]$detail) {
    $checks.Add([pscustomobject]@{ Check = $name; Result = $(if ($ok) { 'PASS' } else { 'FAIL' }); Detail = $detail })
    if (-not $ok) { Write-Host "    FAIL $name - $detail" -ForegroundColor Red }
}
function CountIn([string]$text, [string]$needle) { ([regex]::Matches($text, [regex]::Escape($needle))).Count }

Check 'single globals block' `
    ((([regex]::Matches($script, '(?m)^globals\s*$')).Count -eq 1) -and (([regex]::Matches($script, '(?m)^endglobals\s*$')).Count -eq 1)) 'one globals/endglobals pair'
$fnOpen  = ([regex]::Matches($script, '(?m)^\s*function\s')).Count
$fnClose = ([regex]::Matches($script, '(?m)^\s*endfunction\s*$')).Count
Check 'function/endfunction balance' ($fnOpen -eq $fnClose) "$fnOpen function / $fnClose endfunction"
$fnNames = [regex]::Matches($script, '(?m)^\s*function\s+([A-Za-z0-9_]+)\s') | ForEach-Object { $_.Groups[1].Value }
$dupFn = @($fnNames | Group-Object | Where-Object Count -gt 1 | ForEach-Object { $_.Name })
Check 'unique function names' ($dupFn.Count -eq 0) $(if ($dupFn.Count -gt 0) { "duplicates: $($dupFn -join ', ')" } else { "$(@($fnNames).Count) functions, no duplicates" })
$initBase = ([regex]::Matches($baseText, '(?m)^\s*call InitTrig_')).Count
$initNow  = ([regex]::Matches($script,   '(?m)^\s*call InitTrig_')).Count
Check 'InitTrig entry points +1' ($initNow -eq $initBase + 1) "$initBase -> $initNow (Altar_limit_Release added)"

# B1
Check 'b1 altar limit on CONSTRUCT_START' `
    ((CountIn $script 'TriggerRegisterAnyUnitEventBJ(gg_trg_Altar_limit, EVENT_PLAYER_UNIT_CONSTRUCT_START)') -eq 1 -and
     (CountIn $script 'TriggerRegisterAnyUnitEventBJ(gg_trg_Altar_limit, EVENT_PLAYER_UNIT_CONSTRUCT_FINISH)') -eq 0) 'START replaces FINISH'
Check 'b1 build button disabled and released' `
    ((CountIn $script "call SetPlayerUnitAvailableBJ('hhou', false, owner)") -eq 1 -and
     (CountIn $script "call SetPlayerUnitAvailableBJ('hhou', true, GetOwningPlayer(GetTriggerUnit()))") -eq 1) 'one disable, one re-enable'
Check 'b1 release trigger registered' `
    ((CountIn $script 'call InitTrig_Altar_limit_Release()') -eq 1 -and
     (CountIn $script 'function InitTrig_Altar_limit_Release takes nothing returns nothing') -eq 1) 'defined once, called once'
Check 'b1 release covers death and cancel' `
    ((CountIn $script 'TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)') -eq 1 -and
     (CountIn $script 'TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_CONSTRUCT_CANCEL)') -eq 1) 'both events'
Check 'b1 dead R00I revoke removed' `
    ((CountIn $script "call SetPlayerTechResearchedSwap('R00I', 0, GetOwningPlayer(GetTriggerUnit()))") -eq 0) 'no-op revoke dropped'
Check 'b1 duplicate placement cancelled' `
    ((CountIn $script 'call IssueImmediateOrder(built, "cancel")') -eq 1) 'same-tick race handled'

# B2
Check 'b2 R00J granted at start' `
    ((CountIn $script "call SetPlayerTechResearchedSwap('R00J', 1, GetEnumPlayer())") -eq 2) 'Start_game + Third Hero Delay'
Check 'b2 third hero delay kept' `
    ((CountIn $script 'function Trig_Third_Hero_Delay_Actions takes nothing returns nothing') -eq 1 -and
     (CountIn $script 'call StartTimerBJ(udg_timer_3rd_hero, false, 1800.00)') -eq 1) '1800s timer untouched'
Check 'b2 summon still consumes the charge' `
    ((CountIn $script "call SetPlayerTechResearchedSwap('R00J', 0, udg_temp_player)") -eq 1) 'one hero per charge'

# B3
Check 'b3 v49 mass coordinates restored' `
    ((CountIn $script 'call SoloFootsMassSpawnBatch(Player(0), 10, -60.00, 1000.00)') -eq 1 -and
     (CountIn $script 'call SoloFootsMassSpawnBatch(Player(11), 12, -200.00, -1100.00)') -eq 1 -and
     (CountIn $script 'call SoloFootsMassSpawnBatch(Player(0), 10, -240.00, 240.00)') -eq 0) 'brackets in, diagonals out'
$massCalls = ([regex]::Matches($script, 'call SoloFootsMassSpawnBatch\(')).Count
Check 'b3 still 28 batches' ($massCalls -eq 28) "$massCalls calls (7 steps x 4 teams)"
$counts = [regex]::Matches($script, 'call SoloFootsMassSpawnBatch\(Player\((\d+)\), (\d+),') |
    Group-Object { $_.Groups[1].Value } | ForEach-Object { [pscustomobject]@{ P = $_.Name; N = ($_.Group | ForEach-Object { [int]$_.Groups[2].Value } | Measure-Object -Sum).Sum } }
Check 'b3 equal army sizes' `
    ((@($counts | Select-Object -ExpandProperty N | Sort-Object -Unique)).Count -eq 1 -and $counts[0].N -eq 85) `
    (($counts | ForEach-Object { "P$($_.P)=$($_.N)" }) -join ' ')
Check 'b3 roar offsets untouched' `
    ((CountIn $script 'call SoloFootsMassCastRoar(Player(0), -480.00, 340.00)') -eq 1 -and
     (CountIn $baseText 'call SoloFootsMassCastRoar(Player(0), -480.00, 340.00)') -eq 1) 'unchanged from baseline'

# definition-before-use - the failure mode that shipped v43 unhostable
foreach ($pair in @(@('function Trig_Altar_limit_CountAltars takes player owner returns integer', 'if Trig_Altar_limit_CountAltars(owner) > 1 then'),
                    @('function Trig_Altar_limit_Release_Conditions takes nothing returns boolean', 'Condition(function Trig_Altar_limit_Release_Conditions)'),
                    @('function Trig_Altar_limit_Release_Actions takes nothing returns nothing', 'function Trig_Altar_limit_Release_Actions)'),
                    @('function InitTrig_Altar_limit_Release takes nothing returns nothing', 'call InitTrig_Altar_limit_Release()'))) {
    Check "defined before use: $($pair[0])" ($script.IndexOf($pair[0]) -ge 0 -and $script.IndexOf($pair[0]) -lt $script.IndexOf($pair[1])) 'definition precedes first use'
}

# nothing else moved
foreach ($m in @('SoloCam_', 'zoom___', 'SoloFootsPrepareEndGame', 'SoloFootsFindWinner', 'SoloSub_', 'FF_ReportEndGame', 'MMD__init')) {
    $b = CountIn $baseText $m; $o = CountIn $script $m
    Check "preserved: $m" ($o -eq $b) "$b -> $o"
}
$baseCmds = @([regex]::Matches($baseText, 'TriggerRegisterPlayerChatEvent\([^\r\n]*?"([^"]*)"') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
$nowCmds  = @([regex]::Matches($script,   'TriggerRegisterPlayerChatEvent\([^\r\n]*?"([^"]*)"') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
Check 'command surface unchanged' `
    ((@($nowCmds | Where-Object { $baseCmds -notcontains $_ }).Count -eq 0) -and (@($baseCmds | Where-Object { $nowCmds -notcontains $_ }).Count -eq 0)) "$($nowCmds.Count) commands"

if (@($checks | Where-Object Result -eq 'FAIL').Count -gt 0) { Fail 'static acceptance checks failed' }
Write-Host "    $($checks.Count) static checks passed"

# ------------------------------------------------------------ 5. repack ----
Step 'Repack with ReplaceWar3MapScript'
$subOut = & $Packer $BaselineMap $EditedScript $OutMap 'war3map.j' | Out-String
if ($LASTEXITCODE -ne 0) { Fail 'ReplaceWar3MapScript failed' }
Write-Host $subOut
$outSize = (Get-Item -LiteralPath $OutMap).Length
$outSha = Sha $OutMap

Step 'Verify the packed map'
& $MapExtract $OutMap $VerifyDir | Out-Null
if ($LASTEXITCODE -ne 0) { Fail 'MapExtract failed on the output map' }
$packedScript = Join-Path $VerifyDir 'war3map.j'
if ((Sha $packedScript) -ne $editedSha) { Fail "packed war3map.j SHA $(Sha $packedScript) != validated $editedSha" }

$memberDiff = New-Object System.Collections.Generic.List[string]
foreach ($bf in (Get-ChildItem -LiteralPath $BaseDir -Recurse -File)) {
    $rel = $bf.FullName.Substring($BaseDir.Length + 1)
    $vf = Join-Path $VerifyDir $rel
    if (-not (Test-Path -LiteralPath $vf)) { $memberDiff.Add("$rel : MISSING from output"); continue }
    if ((Sha $bf.FullName) -ne (Sha $vf)) { $memberDiff.Add("$rel : changed") }
}
$unexpected = @($memberDiff | Where-Object { $_ -notmatch '^war3map\.j : changed$' -and $_ -notmatch '^\(attributes\) :' })
if ($unexpected.Count -gt 0) {
    $unexpected | ForEach-Object { Write-Host "    UNEXPECTED $_" -ForegroundColor Red }
    Fail 'members other than war3map.j changed'
}
Write-Host "    member diff: $($memberDiff -join '; ')"

$pjassOut2 = & $Pjass $CommonJ $BlizzardJ $packedScript 2>&1 | Out-String
if ($pjassOut2 -notmatch 'Parse successful.*war3map\.j' -or $pjassOut2 -match 'error') { Fail "pjass failed on the repacked script:`n$pjassOut2" }

# ------------------------------------- 6. adopt into src, roundtrip, GPT ---
Step 'Adopt into the workspace'
if ((Sha $SrcScript) -ne $baseScriptSha) { Fail 'src\war3map.j changed during the build - not overwriting' }
Copy-Item -LiteralPath $EditedScript -Destination $SrcScript -Force
New-Item -ItemType Directory -Force -Path $RoundTrip | Out-Null
Copy-Item -LiteralPath $packedScript -Destination (Join-Path $RoundTrip 'war3map.j')
New-Item -ItemType Directory -Force -Path $DeliverDir | Out-Null
Copy-Item -LiteralPath $OutMap -Destination (Join-Path $DeliverDir "$Version.w3x")
Write-Host "    src\war3map.j updated, roundtrip written, delivered to $DeliverDir"

# ------------------------------------------------------------ 7. report ----
Step 'Write report'
$now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$report = @()
$report += "# $Version - altar limit, second hero, mass spawn placement"
$report += ''
$report += "Built $now"
$report += ''
$report += '| Artifact | Value |'
$report += '|---|---|'
$report += "| Parent map | ``$BaselineName.w3x`` |"
$report += "| Parent SHA-256 | ``$actualSha`` |"
$report += "| Parent war3map.j SHA-256 | ``$baseScriptSha`` |"
$report += "| Map | ``$Version.w3x`` |"
$report += "| Size | $outSize bytes |"
$report += "| SHA-256 | ``$outSha`` |"
$report += "| war3map.j SHA-256 | ``$editedSha`` |"
$report += ''
$report += '## B1 - two altars'
$report += ''
$report += 'The "Altar limit" trigger fired on `EVENT_PLAYER_UNIT_CONSTRUCT_FINISH` and revoked'
$report += 'upgrade `R00I`. `R00I` appears exactly once in the entire map - its own definition in'
$report += '`war3map.w3q`. Zero references across `w3u`, `w3a`, `w3t`, `w3b`, `w3d`, so no unit,'
$report += 'ability or item has ever listed it as a requirement. `hhou` requires only `R00H`, the'
$report += '300s altar delay. Revoking `R00I` was a no-op; the limit has never worked.'
$report += ''
$report += 'Now: on `CONSTRUCT_START` the altar is disabled for that player with'
$report += '`SetPlayerUnitAvailableBJ`, which greys the build button out immediately. If a second'
$report += 'placement lands in the same tick (two builders), the duplicate is cancelled and'
$report += 'refunded. A new "Altar limit release" trigger re-enables the button on altar death or'
$report += 'construction cancel, so one-at-a-time does not become one-per-game.'
$report += ''
$report += '## B2 - no second hero until 30 minutes'
$report += ''
$report += 'All six altar summon abilities carry `areq=R00J`, `arqa=1`:'
$report += ''
$report += '```text'
$report += 'A0H7  A0EO  A0GE  A0EA  A0EG  A0GG'
$report += '```'
$report += ''
$report += '`R00J` was granted only by "Third Hero Delay" at `t=1800s`, and'
$report += '`Trig_Altar_Hero_Summon` revokes it on use. The altar was therefore inert for the'
$report += 'first 30 minutes even though it can be built from `t=300s`.'
$report += ''
$report += 'Now: `R00J` is granted in `Trig_Start_game_Func025A` next to `R00I`. The 1800s grant is'
$report += 'kept as-is per your call, so it hands out a second charge - a third hero. Note that'
$report += '`SetPlayerMaxHeroesAllowed` is 2, but the summon uses `CreateUnit`, which ignores that'
$report += 'cap, so the third hero will work.'
$report += ''
$report += '## B3 - mass spawn 45 degrees out of phase'
$report += ''
$report += 'The four start locations are corners: P0 `(-2240, 1984)`, P4 `(2304, 1984)`,'
$report += 'P7 `(2304, -2496)`, P11 `(-2240, -2496)`.'
$report += ''
$report += 'v52 ("spawnfix", `tmp\SF_Test1.7_v52-spawnfix.w3x`) rewrote the seven batches so each'
$report += 'team formed a single diagonal line running out toward its own corner - offsets'
$report += '`(-240,240) (-450,450) ... (-1500,1500)`. Every army ended up on a 45-degree ray'
$report += 'instead of bracketing the axes, which is the rotation you saw.'
$report += ''
$report += 'Restored the v7..v51 coordinates verbatim from'
$report += '`roundtrip\SF_Test1.7_v49\files\war3map.j`: each team lays two arms along the map axes'
$report += 'inside its own quadrant, so adjacent teams meet head-on across the axis they share.'
$report += 'Army sizes stay at 85 per team and the roar caster offsets were already per-quadrant'
$report += 'in both versions - untouched.'
$report += ''
$report += '## Script edits'
$report += ''
$editLog | ForEach-Object { $report += "- $_" }
$report += ''
$report += '## Changed MPQ members'
$report += ''
$memberDiff | ForEach-Object { $report += "- $_" }
$report += ''
$report += '## Static acceptance checks'
$report += ''
$report += '| Check | Result | Detail |'
$report += '|---|---|---|'
$checks | ForEach-Object { $report += "| $($_.Check) | $($_.Result) | $($_.Detail) |" }
$report += ''
$report += '## Validation'
$report += ''
$report += '- JassCheck (War3Net syntax parse): PASS'
$report += '- pjass, edited script: PASS'
$report += '- pjass, repacked script: PASS'
$report += '- Packed war3map.j SHA matches the validated input: PASS'
$report += '- Every non-script member byte-identical to the parent: PASS'
$report += ''
$report += '## Not yet done'
$report += ''
$report += '- No runtime test. Host one game and confirm: a second altar cannot be placed while'
$report += '  the first stands, the build button comes back after the altar dies, the altar can'
$report += '  summon a hero as soon as it finishes, and the mass formation lines up on the axes.'
$report | Set-Content -LiteralPath (Join-Path $BuildDir 'build-report.md') -Encoding utf8

Write-Host ''
Write-Host "BUILD OK  $OutMap" -ForegroundColor Green
Write-Host "          $outSize bytes  $outSha"
