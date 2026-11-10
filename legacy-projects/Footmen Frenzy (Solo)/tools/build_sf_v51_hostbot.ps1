<#
    build_sf_v51_hostbot.ps1

    Reproducible build of SF_Test1.7_v51 from the verified SF_Test1.7_v50 baseline.

    Ports the host-bot instrumentation this map had none of, from FF799X_v54_killlog_schema.w3x:

      M1. The MMD (Map Meta Data) library - globals and functions, verbatim. Verified
          self-contained: no other library and no udg_ global is referenced. Placed in exactly the
          slot 799x uses, between GUISimpleTimers and TimerUtils, and initialised from main() with
          the same `call ExecuteFunc("MMD__init")` in the same position.
      F1. KillLog  -> CustomMapData/ff_killlog.txt   (schema v2: slot,owner,unit,hero,...)
      F2. GameResult -> CustomMapData/ff_result.txt
      F3. FF_ReportEndGame: MMD winner/loser/drawer flags plus the wc3mt-GameEnd signal, fired once
          from Trig_END_Actions after SoloFootsPrepareEndGame allows the finale.

    Deliberately NOT ported (see the header of src\systems\ff_hostbot.jass):
      * FF_oc_    - this map already has SoloCam_.
      * FFEnd_    - 799x needed it only because a 1v1 seated both players in one slot block. This
                    map seats its four competitors at 1, 5, 8 and 12, one per block, so the stock
                    side model always resolves. SoloFootsPrepareEndGame already latches the finale.

    Usage:
      pwsh -File tools\build_sf_v51_hostbot.ps1
      pwsh -File tools\build_sf_v51_hostbot.ps1 -Force
#>

[CmdletBinding()]
param(
    [string] $Root         = 'C:\Users\Ryan1\Documents\Solo Foots Development',
    [string] $FfTools      = 'C:\Users\Ryan1\Documents\Footmen Frenzy Development\tools',
    [string] $BaselineName = 'SF_Test1.7_v50',
    [string] $Version      = 'SF_Test1.7_v51',
    [switch] $Force
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$BaselineMap = Join-Path $Root "releases\$BaselineName.w3x"
$BuildDir    = Join-Path $Root "outputs\$Version-hostbot"
$BaseDir     = Join-Path $BuildDir 'base'
$EditedDir   = Join-Path $BuildDir 'edited'
$VerifyDir   = Join-Path $BuildDir 'verified'
$OutMap      = Join-Path $Root "releases\$Version.w3x"
$SrcScript   = Join-Path $Root 'src\war3map.j'
$MmdModule   = Join-Path $Root 'src\systems\mmd_library.jass'
$FfModule    = Join-Path $Root 'src\systems\ff_hostbot.jass'
$RoundTrip   = Join-Path $Root "roundtrip\$Version\files"
$DeliverDir  = Join-Path 'C:\Users\Ryan1\Documents\Warcraft III\Maps\Solo Foots\GPT' $Version

$MapExtract = Join-Path $FfTools 'MapExtract\bin\Release\net6.0\MapExtract.exe'
$JassCheck  = Join-Path $FfTools 'JassCheck\bin\Release\net6.0\JassCheck.exe'
# This archive has no (listfile), so MpqSubstitute cannot match members by name and would add a
# second war3map.j instead of replacing the first. ReplaceWar3MapScript resolves by hash.
$Packer     = Join-Path $Root 'tools\bin\ReplaceWar3MapScript\ReplaceWar3MapScript.exe'
$Pjass      = 'C:\Program Files\Warcraft III\_retail_\x86_64\JassHelper\pjass.exe'
$CommonJ    = 'C:\Users\Ryan1\Documents\Warcraft III\JassHelper\common.j'
$BlizzardJ  = 'C:\Users\Ryan1\Documents\Warcraft III\JassHelper\Blizzard.j'
$Latin1     = [System.Text.Encoding]::GetEncoding(28591)
$NL         = "`r`n"

function Fail([string]$m) { throw "BUILD STOPPED: $m" }
function Step([string]$m) { Write-Host "==> $m" }
function Sha([string]$p) { (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash }
function ReadText([string]$p) { $Latin1.GetString([IO.File]::ReadAllBytes($p)) }
function WriteText([string]$p, [string]$t) { [IO.File]::WriteAllBytes($p, $Latin1.GetBytes($t)) }
function J([string[]]$lines) { ($lines -join "`n").Replace("`n", $NL) + $NL }

# ------------------------------------------------- 0. preflight guards ----
Step 'Preflight'
foreach ($p in @($BaselineMap, $SrcScript, $MmdModule, $FfModule, $MapExtract, $Packer, $JassCheck, $Pjass, $CommonJ, $BlizzardJ)) {
    if (-not (Test-Path -LiteralPath $p)) { Fail "missing required input: $p" }
}
$newest = Get-ChildItem -LiteralPath (Join-Path $Root 'releases') -Filter 'SF_Test1.7_v*.w3x' |
    Sort-Object { [int]([regex]::Match($_.Name, 'v(\d+)').Groups[1].Value) } -Descending | Select-Object -First 1
if ($newest.BaseName -ne $BaselineName) { Fail "newest release is $($newest.BaseName), pinned baseline is $BaselineName" }

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

# --------------------------------------------------- 2. read the modules ---
Step 'Read modules'
function Region([string]$path, [string]$name) {
    $t = ReadText $path
    $b = "//= $name-BEGIN"; $e = "//= $name-END"
    $bi = $t.IndexOf($b); $ei = $t.IndexOf($e)
    if ($bi -lt 0 -or $ei -lt 0) { Fail "region $name not found in $path" }
    $start = $t.IndexOf("`n", $bi) + 1
    $body = $t.Substring($start, $ei - $start)
    return (($body -replace "`r`n", "`n") -replace "`n", $NL)
}
$mmdGlobals    = Region $MmdModule 'MMD-GLOBALS'
$mmdFns        = Region $MmdModule 'MMD-FUNCTIONS'
# JassHelper emits MMD's struct state, allocator and onDestroy dispatch outside the library block.
# Leaving them behind is what pjass rejected on the first attempt with 22 undeclared-symbol errors.
$mmdStructGl   = Region $MmdModule 'MMD-STRUCT-GLOBALS'
$mmdAlloc      = Region $MmdModule 'MMD-ALLOC'
$mmdOnDestroy  = Region $MmdModule 'MMD-ONDESTROY'
$mmdStructInit = Region $MmdModule 'MMD-STRUCT-INIT'
$ffGlobals     = Region $FfModule  'FF-GLOBALS'
$ffFns         = Region $FfModule  'FF-FUNCTIONS'
Write-Host "    MMD $($mmdGlobals.Length) + $($mmdFns.Length) + struct $($mmdStructGl.Length)/$($mmdAlloc.Length)/$($mmdOnDestroy.Length); FF $($ffGlobals.Length) + $($ffFns.Length) bytes"

# Nothing the port introduces may already exist in the map.
foreach ($sym in @('MMD__init', 'MMD_FlagPlayer', 'FF_kl_Flush', 'FF_gr_Poll', 'FF_ReportEndGame', 'FF_Init')) {
    if ($baseText.Contains($sym)) { Fail "symbol '$sym' already exists in the map - refusing to double-define" }
}

# --------------------------------------------------------- 3. the edits ---
Step 'Edit war3map.j'
$script = $baseText
$editLog = New-Object System.Collections.Generic.List[string]

function Splice([string]$name, [string]$from, [string]$to, [string]$note) {
    $hits = ([regex]::Matches($script:script, [regex]::Escape($from))).Count
    if ($hits -ne 1) { Fail "edit '$name' matched $hits anchor(s), expected exactly 1" }
    $script:script = $script:script.Replace($from, $to)
    $script:editLog.Add("$name : $note")
}

# M1a. MMD globals, in the same slot 799x uses (after GUISimpleTimers, before TimerUtils).
Splice 'm1a-mmd-globals' `
    (J @('//endglobals from GUISimpleTimers', '//globals from TimerUtils:')) `
    ((J @('//endglobals from GUISimpleTimers')) + $mmdGlobals + (J @('//globals from TimerUtils:'))) `
    'MMD globals inserted'

# M1b. MMD library body, same relative position.
Splice 'm1b-mmd-functions' `
    (J @('//library GUISimpleTimers ends', '//library TimerUtils:')) `
    ((J @('//library GUISimpleTimers ends')) + $mmdFns + (J @('//library TimerUtils:'))) `
    'MMD functions inserted'

# M1b2. MMD__QueueNode struct state, alongside the map's other struct globals.
Splice 'm1b2-struct-globals' `
    (J @('trigger st__Missiles_move')) `
    ((J @('trigger st__Missiles_move')) + $mmdStructGl) `
    'MMD__QueueNode struct globals inserted'

# M1b3. Its generated allocator/destructor, with the map's other generated allocators and before
#       the library body that calls them.
Splice 'm1b3-struct-alloc' `
    (J @('//library Alloc:')) `
    ($mmdAlloc + (J @('//library Alloc:'))) `
    'MMD__QueueNode allocator/destructor inserted'

# M1b4. Its onDestroy dispatch condition, and the two lines that register it.
Splice 'm1b4-struct-ondestroy' `
    (J @('function jasshelper__initstructs604298953 takes nothing returns nothing')) `
    ($mmdOnDestroy + (J @('function jasshelper__initstructs604298953 takes nothing returns nothing'))) `
    'sa__MMD__QueueNode_onDestroy inserted'
Splice 'm1b5-struct-init' `
    (J @('    call TriggerAddCondition(st__Missiles_move,Condition( function sa__Missiles_move))')) `
    ((J @('    call TriggerAddCondition(st__Missiles_move,Condition( function sa__Missiles_move))')) + $mmdStructInit) `
    'onDestroy trigger registered in jasshelper__initstructs'

# M1c. MMD init, same position in main() as 799x.
Splice 'm1c-mmd-init' `
    (J @('call ExecuteFunc("jasshelper__initstructs604298953")', 'call ExecuteFunc("TimerUtils___init")')) `
    (J @('call ExecuteFunc("jasshelper__initstructs604298953")', 'call ExecuteFunc("MMD__init")', 'call ExecuteFunc("TimerUtils___init")')) `
    'MMD__init wired into main'

# F1. FF globals at the end of the globals block.
Splice 'f1-ff-globals' `
    (J @('//endglobals from MissileUtils')) `
    ((J @('//endglobals from MissileUtils', '', '// === FF host-bot logging (ported from FF799X v54) ==='))) `
    'FF globals marker'
$script = $script.Replace(
    (J @('// === FF host-bot logging (ported from FF799X v54) ===')),
    (J @('// === FF host-bot logging (ported from FF799X v54) ===')) + $ffGlobals)
$editLog.Add('f1b-ff-globals : FF globals inserted')

# F2. FF functions after every library, before any map trigger. Everything they touch - natives,
#     udg_ globals, the FileIO s__File helpers and MMD_FlagPlayer - is defined above this point,
#     and both call sites (Trig_END_Actions and main) are below it.
Splice 'f2-ff-functions' `
    (J @('//library MissileUtils ends')) `
    ((J @('//library MissileUtils ends', '')) + $ffFns) `
    'FF functions inserted'

# F3. FF_Init from main, right after InitCustomTriggers - same as 799x.
Splice 'f3-ff-init' `
    (J @('    call InitCustomTriggers()')) `
    (J @('    call InitCustomTriggers()', '    call FF_Init()')) `
    'FF_Init wired into main'

# F4. Report the result once, where the map has already decided the finale may start.
Splice 'f4-end-report' `
    (J @(
        '        if not SoloFootsPrepareEndGame() then',
        '            return',
        '        endif'
    )) `
    (J @(
        '        if not SoloFootsPrepareEndGame() then',
        '            return',
        '        endif',
        '        // Host-bot reporting: MMD winner/loser flags and the wc3mt-GameEnd signal. Runs on',
        '        // its own trigger thread, so it does not delay the announcements below.',
        '        call FF_ReportEndGame(SoloFootsFindWinner())'
    )) `
    'FF_ReportEndGame called from Trig_END_Actions'

$EditedScript = Join-Path $EditedDir 'war3map.j'
WriteText $EditedScript $script
$editedSha = Sha $EditedScript
Write-Host "    wrote $EditedScript ($((Get-Item -LiteralPath $EditedScript).Length) bytes)"
$editLog | ForEach-Object { Write-Host "    $_" }

# ------------------------------------------------------ 4. validate JASS ---
Step 'Validate JASS'
& $JassCheck $EditedScript
if ($LASTEXITCODE -ne 0) { Fail 'JassCheck (War3Net syntax parse) failed' }
$pjassOut = & $Pjass $CommonJ $BlizzardJ $EditedScript 2>&1 | Out-String
Write-Host $pjassOut
if ($pjassOut -notmatch 'Parse successful.*war3map\.j') { Fail "pjass rejected the edited script:`n$pjassOut" }
if ($pjassOut -match 'error') { Fail "pjass reported errors:`n$pjassOut" }

# -------------------------------------------- 5. static acceptance checks --
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
Check 'InitTrig entry points preserved' `
    (([regex]::Matches($script, '(?m)^\s*call InitTrig_')).Count -eq ([regex]::Matches($baseText, '(?m)^\s*call InitTrig_')).Count) 'unchanged'

# MMD
Check 'MMD library present once' ((CountIn $script 'function MMD__init takes nothing returns nothing') -eq 1 -and
                                  (CountIn $script 'function MMD_FlagPlayer takes player p,integer flag_type returns nothing') -eq 1) 'init + FlagPlayer defined once'
Check 'MMD initialised from main' ((CountIn $script 'call ExecuteFunc("MMD__init")') -eq 1) 'single ExecuteFunc'
Check 'MMD init ordered before TimerUtils' `
    ($script.IndexOf('call ExecuteFunc("MMD__init")') -lt $script.IndexOf('call ExecuteFunc("TimerUtils___init")')) 'same order as 799x'
Check 'MMD globals inside the globals block' `
    ($script.IndexOf('constant boolean LIBRARY_MMD=true') -lt $script.IndexOf($NL + 'endglobals')) 'declared before endglobals'
Check 'MMD self-contained' `
    (($mmdFns -notmatch 's__File') -and ($mmdFns -notmatch 'udg_') -and ($mmdFns -notmatch 'GST_')) 'no external references in the ported body'
Check 'MMD struct plumbing complete' `
    ((CountIn $script 'function s__MMD__QueueNode__allocate takes nothing returns integer') -eq 1 -and
     (CountIn $script 'function sc__MMD__QueueNode_deallocate takes integer this returns nothing') -eq 1 -and
     (CountIn $script 'function sa__MMD__QueueNode_onDestroy takes nothing returns boolean') -eq 1 -and
     (CountIn $script 'integer array s__MMD__QueueNode_next') -eq 1 -and
     (CountIn $script 'trigger st__MMD__QueueNode_onDestroy') -eq 1) 'allocator, destructor, onDestroy and state all present once'
Check 'MMD onDestroy registered' `
    ((CountIn $script 'set st__MMD__QueueNode_onDestroy=CreateTrigger()') -eq 1 -and
     (CountIn $script 'call TriggerAddCondition(st__MMD__QueueNode_onDestroy,Condition( function sa__MMD__QueueNode_onDestroy))') -eq 1) 'wired in jasshelper__initstructs'
Check 'struct type id does not collide' `
    ((CountIn $script 'constant integer si__MMD__QueueNode=2') -eq 1 -and (CountIn $script 'constant integer si__File=2') -eq 0 -and
     ([regex]::Matches($script, '(?m)^constant integer si__[A-Za-z_0-9]+=2\s*$')).Count -eq 1) 'exactly one struct claims id 2'

# log systems
Check 'ff_killlog.txt written' ((CountIn $script 'call PreloadGenEnd("ff_killlog.txt")') -eq 1) 'single PreloadGenEnd'
Check 'ff_result.txt written' ((CountIn $script 'call PreloadGenEnd("ff_result.txt")') -eq 1) 'single PreloadGenEnd'
Check 'killlog schema v2' ((CountIn $script 'call Preload("slot,owner,unit,hero,unit_died,hero_died")') -eq 1) 'slot column first'
Check 'no bot battletag gate' ((CountIn $script 'FF_kl_LocalClientIsBot') -eq 0) 'every client writes'
Check 'end-of-game kill-log flush' ((CountIn $script 'call FF_kl_Flush()') -eq 3) 'init + 30s tick + result path'
Check 'wc3mt GameEnd signal' ((CountIn $script 'call s__File_close(s__File_write(s__File_open("wc3mt.txt"), "wc3mt-GameEnd"))') -eq 1) 'written once'
Check 'result reporting called once' ((CountIn $script 'call FF_ReportEndGame(SoloFootsFindWinner())') -eq 1) 'from Trig_END_Actions'
Check 'report latched' ((CountIn $script 'set FF_endReported = true') -eq 1) 'cannot flag twice'
Check 'FF_Init wired once' ((CountIn $script 'call FF_Init()') -eq 1) 'from main'
Check 'boot starts both systems' `
    ((CountIn $script 'call FF_KillLog_Init()') -eq 1 -and (CountIn $script 'call FF_GameResult_Init()') -eq 1) 'KillLog + GameResult'
Check 'no 799x-only symbols carried over' `
    ((CountIn $script 'FFEnd_') -eq 0 -and (CountIn $script 'FF_oc_') -eq 0) 'FFEnd / FF_oc not ported'

# definition-before-use, the failure mode that shipped v43 unhostable
foreach ($pair in @(@('function MMD_FlagPlayer takes', 'call MMD_FlagPlayer(ConvertedPlayer(p)'),
                    @('function FF_ReportEndGame takes', 'call FF_ReportEndGame(SoloFootsFindWinner())'),
                    @('function FF_Init takes', 'call FF_Init()'),
                    @('function FF_kl_Flush takes', 'call FF_kl_Flush()'),
                    @('function s__File_close takes', 'call s__File_close(s__File_write(s__File_open("wc3mt.txt")'))) {
    Check "defined before use: $($pair[0])" ($script.IndexOf($pair[0]) -ge 0 -and $script.IndexOf($pair[0]) -lt $script.IndexOf($pair[1])) 'definition precedes first call'
}

# this map's own systems must be untouched
foreach ($m in @('SoloCam_', 'zoom___', 'SoloFootsPrepareEndGame', 'SoloFootsFindWinner', 'SoloSub_')) {
    $b = CountIn $baseText $m; $o = CountIn $script $m
    Check "preserved: $m" ($o -ge $b) "$b -> $o"
}
$baseCmds = @([regex]::Matches($baseText, 'TriggerRegisterPlayerChatEvent\([^\r\n]*?"([^"]*)"') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
$nowCmds  = @([regex]::Matches($script,   'TriggerRegisterPlayerChatEvent\([^\r\n]*?"([^"]*)"') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
Check 'command surface unchanged' `
    ((@($nowCmds | Where-Object { $baseCmds -notcontains $_ }).Count -eq 0) -and (@($baseCmds | Where-Object { $nowCmds -notcontains $_ }).Count -eq 0)) "$($nowCmds.Count) commands"

if (@($checks | Where-Object Result -eq 'FAIL').Count -gt 0) { Fail 'static acceptance checks failed' }
Write-Host "    $($checks.Count) static checks passed"

# ------------------------------------------------------------ 6. repack ----
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

# ------------------------------------- 7. adopt into src, roundtrip, GPT ---
Step 'Adopt into the workspace'
if ((Sha $SrcScript) -ne $baseScriptSha) { Fail 'src\war3map.j changed during the build - not overwriting' }
Copy-Item -LiteralPath $EditedScript -Destination $SrcScript -Force
New-Item -ItemType Directory -Force -Path $RoundTrip | Out-Null
Copy-Item -LiteralPath $packedScript -Destination (Join-Path $RoundTrip 'war3map.j')
New-Item -ItemType Directory -Force -Path $DeliverDir | Out-Null
Copy-Item -LiteralPath $OutMap -Destination (Join-Path $DeliverDir "$Version.w3x")
Write-Host "    src\war3map.j updated, roundtrip written, delivered to $DeliverDir"

# ------------------------------------------------------------ 8. report ----
Step 'Write report'
$now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$report = @()
$report += "# $Version - host-bot stats ported from FF799X v54"
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
$report += '## What this map now emits'
$report += ''
$report += 'All three into the client''s `CustomMapData`, matching FF799X v54 byte-for-byte in format:'
$report += ''
$report += '```text'
$report += 'ff_killlog.txt   slot,owner,unit,hero,unit_died,hero_died'
$report += '                 herokill,<mm:ss>,<killerSlot>,<killerOwner>,<killerUnit>,<victimSlot>,<victimOwner>,<victimUnit>'
$report += 'ff_result.txt    mode,ffa | roster | out | sidedead | winner | placement | gameend'
$report += 'wc3mt.txt        wc3mt-GameEnd'
$report += '```'
$report += ''
$report += 'Plus MMD messages: every slot is flagged winner / loser / drawer once the finale starts.'
$report += ''
$report += 'The grammars are documented in the script itself, in `FILE FORMAT` blocks above'
$report += '`FF_kl_Flush` and `FF_gr_Flush`, exactly as in 799x.'
$report += ''
$report += '`slot` is the 1-based player slot and is the join key between the two files. In this map'
$report += 'the four competitors sit at slots 1, 5, 8 and 12, which puts each of them alone in one'
$report += 'of the side model''s four slot blocks - so `ff_result.txt` side labels `team1`..`team4`'
$report += 'are one-to-one with the players, and `placement` rows are already per player.'
$report += ''
$report += '## Not ported, and why'
$report += ''
$report += '- `FF_oc_` (799x observer camera): this map already has `SoloCam_`.'
$report += '- `FFEnd_` (collapsed-block end override): 799x needed it because a 1v1 seated both'
$report += '  players inside one slot block, which made its END trigger crown a block that had no'
$report += '  living member. This map''s seating puts one competitor per block, and'
$report += '  `SoloFootsPrepareEndGame` already latches the finale on the two-to-one transition.'
$report += '- `FF_kl_LocalClientIsBot` / `FF_EndsWith`: the battletag gate was removed in 799x v51.'
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
$report += '- Explicit definition-before-use checks on every ported call site. This is the failure'
$report += '  mode that shipped v43 unhostable: JassParseCheck is grammar-only and reports OK on a'
$report += '  forward reference that single-pass JASS rejects at load.'
$report += ''
$report += '## Not yet done'
$report += ''
$report += '- No runtime test, and this is a large port into a map that had none of it. Host one'
$report += '  full game and confirm: the lobby loads at all, both files appear in CustomMapData with'
$report += '  plausible numbers, and the host bot sees MMD winner/loser flags.'
$report | Set-Content -LiteralPath (Join-Path $BuildDir 'build-report.md') -Encoding utf8

Write-Host ''
Write-Host "BUILD OK  $OutMap" -ForegroundColor Green
Write-Host "          $outSize bytes  $outSha"
