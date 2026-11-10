$src = 'C:\Users\Ryan1\Documents\Footmen Frenzy Development\outputs\v54-killlog-schema\verified\war3map.j'
$outDir = 'C:\Users\Ryan1\Documents\Solo Foots Development\src\systems'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$L = [System.Text.Encoding]::GetEncoding(28591)
$text = $L.GetString([IO.File]::ReadAllBytes($src))
$NL = "`r`n"

function Fail([string]$m) { throw "EXTRACT FAILED: $m" }

# Pull one top-level function definition by name, verbatim, including its trailing newline.
function Fn([string]$name) {
    $pat = '(?ms)^function\s+' + [regex]::Escape($name) + '\s+takes\b.*?^endfunction\r?\n'
    $m = [regex]::Matches($text, $pat)
    if ($m.Count -ne 1) { Fail "function $name matched $($m.Count) definitions" }
    return $m[0].Value
}
# Pull a contiguous line range delimited by two unique anchors (inclusive of both lines).
function Between([string]$startAnchor, [string]$endAnchor) {
    $i = $text.IndexOf($startAnchor)
    if ($i -lt 0) { Fail "start anchor not found: $startAnchor" }
    $j = $text.IndexOf($endAnchor, $i)
    if ($j -lt 0) { Fail "end anchor not found: $endAnchor" }
    return $text.Substring($i, $j - $i + $endAnchor.Length) + $NL
}
# One global declaration line, by the exact declaration text.
function GlobalLine([string]$decl) {
    $line = '    ' + $decl
    $n = ([regex]::Matches($text, [regex]::Escape($line + $NL))).Count
    if ($n -ne 1) { Fail "global '$decl' matched $n lines" }
    return $line + $NL
}

# ============================ MMD ============================
$mmd = @(
    '//===========================================================================',
    '// MMD (Warcraft 3 Map Meta Data) - verbatim copy of the library in',
    '// FF799X_v54_killlog_schema.w3x. Verified self-contained: it references no other library',
    '// and no udg_ global, so it drops in unchanged. Host bots read the messages it emits.',
    '//===========================================================================',
    '//= MMD-GLOBALS-BEGIN'
) -join $NL
$mmd += $NL + (Between '//globals from MMD:' '//endglobals from MMD')
$mmd += '//= MMD-GLOBALS-END' + $NL
$mmd += '//= MMD-FUNCTIONS-BEGIN' + $NL
$mmd += (Between '//library MMD:' '//library MMD ends')
$mmd += '//= MMD-FUNCTIONS-END' + $NL

# MMD contains a vJass struct (MMD__QueueNode). JassHelper emits its state, its allocator and its
# onDestroy dispatch OUTSIDE the library block, in the generated-struct sections, so those have to
# travel too - pjass caught their absence on the first attempt.
# si__MMD__QueueNode is a type id: it is declared and never read (verified by grep), and the target
# map's ids run 1,3,4..10, so slot 2 is free either way.
function TopLevelLine([string]$decl) {
    $n = ([regex]::Matches($text, [regex]::Escape($decl + $NL))).Count
    if ($n -ne 1) { Fail "top-level line '$decl' matched $n times" }
    return $decl + $NL
}
$mmd += '//= MMD-STRUCT-GLOBALS-BEGIN' + $NL
foreach ($d in @('constant integer si__MMD__QueueNode=2',
                 'integer si__MMD__QueueNode_F=0',
                 'integer si__MMD__QueueNode_I=0',
                 'integer array si__MMD__QueueNode_V',
                 'real array s__MMD__QueueNode_timeout',
                 'string array s__MMD__QueueNode_msg',
                 'integer array s__MMD__QueueNode_checksum',
                 'string array s__MMD__QueueNode_key',
                 'integer array s__MMD__QueueNode_next',
                 'trigger st__MMD__QueueNode_onDestroy')) {
    $mmd += TopLevelLine $d
}
$mmd += '//= MMD-STRUCT-GLOBALS-END' + $NL

$mmd += '//= MMD-ALLOC-BEGIN' + $NL
$mmd += '//Generated allocator of MMD__QueueNode' + $NL
$mmd += (Fn 's__MMD__QueueNode__allocate')
$mmd += '//Generated destructor of MMD__QueueNode' + $NL
$mmd += (Fn 'sc__MMD__QueueNode_deallocate')
$mmd += '//= MMD-ALLOC-END' + $NL

$mmd += '//= MMD-ONDESTROY-BEGIN' + $NL
$mmd += (Fn 'sa__MMD__QueueNode_onDestroy')
$mmd += '//= MMD-ONDESTROY-END' + $NL

$mmd += '//= MMD-STRUCT-INIT-BEGIN' + $NL
$mmd += '    set st__MMD__QueueNode_onDestroy=CreateTrigger()' + $NL
$mmd += '    call TriggerAddCondition(st__MMD__QueueNode_onDestroy,Condition( function sa__MMD__QueueNode_onDestroy))' + $NL
$mmd += '//= MMD-STRUCT-INIT-END' + $NL

[IO.File]::WriteAllBytes((Join-Path $outDir 'mmd_library.jass'), $L.GetBytes($mmd))

# ========================= FF host-bot =======================
$header = @(
    '//===========================================================================',
    '// FF host-bot logging for Solo Foots - ported from FF799X_v54_killlog_schema.w3x.',
    '//',
    '// Carried over: the shared helpers, KillLog (ff_killlog.txt) and GameResult (ff_result.txt).',
    '// Deliberately NOT carried over:',
    '//   * FF_oc_ (observer camera)  - this map already has SoloCam_.',
    '//   * FFEnd_ (collapsed-block end override) - 799x needed it because a 1v1 seated both',
    '//     players inside one slot block. Solo Foots seats its four players at 1, 5, 8 and 12,',
    '//     one per block, so every block holds exactly one competitor and the stock side model',
    '//     resolves correctly. SoloFootsPrepareEndGame already latches the finale as well.',
    '//   * FF_kl_LocalClientIsBot / FF_EndsWith - the battletag gate they implemented was removed',
    '//     in 799x v51; every client writes its own file.',
    '//   * FF_gr_outOrder / FF_gr_outN - only the FFEnd path consumed them. In this map each',
    '//     side is a single player, so the stock side placement table is already per player.',
    '//===========================================================================',
    '//= FF-GLOBALS-BEGIN'
) -join $NL
$header += $NL

$globals = @(
    '    // Never expires; only TimerGetElapsed is read off it, to timestamp log rows.',
    'timer FF_gameTimer = null',
    'boolean FF_kl_dirty = false',
    'integer array FF_kl_unitKills',
    'integer array FF_kl_heroKills',
    'integer array FF_kl_unitDeaths',
    'integer array FF_kl_heroDeaths',
    '    // The "who killed whom" feed; capped so the file stays constant-ish sized.',
    'string array FF_kl_feed',
    'integer FF_kl_feedN = 0',
    '    // Slots 1..12 (index 0 unused): ever-active participants, and who we already reported out.',
    'boolean array FF_gr_participant',
    'boolean array FF_gr_eliminated',
    '    // Side index 1..4; in this map that is one side per competitor.',
    'boolean array FF_gr_sideDead',
    '    // Sides in elimination order (first to die = last place).',
    'integer array FF_gr_deathOrder',
    'integer FF_gr_deathN = 0',
    'string array FF_gr_events',
    'integer FF_gr_eventN = 0',
    'boolean FF_gr_ended = false',
    'timer FF_gr_pollTimer = null'
)
$body = ''
foreach ($g in $globals) {
    if ($g.StartsWith('    ')) { $body += $g + $NL } else { $body += (GlobalLine $g) }
}
$header += $body + '//= FF-GLOBALS-END' + $NL + '//= FF-FUNCTIONS-BEGIN' + $NL

foreach ($f in @('FF_Pad2', 'FF_Elapsed', 'FF_Sanitize', 'FF_UnitAlive',
                 'FF_kl_OwnerName', 'FF_kl_Flush', 'FF_kl_OnFlushTick', 'FF_kl_OnDeath', 'FF_KillLog_Init',
                 'FF_gr_SideCount', 'FF_gr_SideLabel', 'FF_gr_IsMember', 'FF_gr_SideLabelOf',
                 'FF_gr_SideParticipated', 'FF_gr_SideAlive', 'FF_gr_Name', 'FF_gr_RosterOf',
                 'FF_gr_AddEvent', 'FF_gr_Flush', 'FF_gr_Poll', 'FF_GameResult_Init')) {
    $header += (Fn $f) + $NL
}
$header += '//= FF-FUNCTIONS-END' + $NL

# ---- adapt the 799x body to this map (kept here so the module regenerates deterministically) ----
function Sub([string]$label, [string]$from, [string]$to) {
    $n = ([regex]::Matches($script:header, [regex]::Escape($from))).Count
    if ($n -ne 1) { Fail "adapt '$label' matched $n times, expected 1" }
    $script:header = $script:header.Replace($from, $to)
}

# The per-player elimination order only fed the FFEnd placement table.
Sub 'drop-outOrder' `
    (@('            call FF_gr_AddEvent("out," + now + "," + I2S(p) + "," + FF_gr_SideLabelOf(p) + "," + FF_gr_Name(p))',
       '            // Kept so a collapsed-block game can still emit a placement table.',
       '            set FF_gr_outOrder[FF_gr_outN] = p',
       '            set FF_gr_outN = FF_gr_outN + 1',
       '            set changed = true') -join $NL) `
    (@('            call FF_gr_AddEvent("out," + now + "," + I2S(p) + "," + FF_gr_SideLabelOf(p) + "," + FF_gr_Name(p))',
       '            set changed = true') -join $NL)

# The FFEnd verdict branch has no counterpart here.
$ffendStart = $header.IndexOf('    // 1b. If FFEnd settled')
$ffendEnd = $header.IndexOf('    // 2. side bookkeeping.', $ffendStart)
if ($ffendStart -lt 0 -or $ffendEnd -lt 0) { Fail 'FFEnd branch not found in FF_gr_Poll' }
$header = $header.Remove($ffendStart, $ffendEnd - $ffendStart).Insert($ffendStart, (@(
    '    // (799x has an extra branch here for its FFEnd override. This map does not need it: its',
    '    //  four competitors sit at slots 1, 5, 8 and 12, one per slot block, so the side model',
    '    //  below can always name a winner.)',
    '') -join $NL))

Sub 'add-report-globals' `
    ('    timer FF_gr_pollTimer = null' + $NL + '//= FF-GLOBALS-END') `
    ((@('    timer FF_gr_pollTimer = null',
        '    // End-of-game reporting (MMD flags + the wc3mt signal); latched so a second END',
        '    // execution cannot flag anybody twice.',
        '    boolean FF_endReported = false',
        '    integer FF_endWinner = 0',
        '//= FF-GLOBALS-END') -join $NL))

Sub 'add-report-and-boot' '//= FF-FUNCTIONS-END' ((@(
    '//===========================================================================',
    '// End-of-game reporting: MMD winner/loser/drawer flags plus the wc3mt-GameEnd signal, both of',
    '// which 799x emits from its END paths. Called once from Trig_END_Actions, after',
    '// SoloFootsPrepareEndGame has decided the finale may start.',
    '//',
    '// The flags go out one slot at a time with the same 0.25s spacing 799x uses, so the MMD',
    '// emitter queue drains the same way. TriggerSleepAction only works on a trigger thread, and',
    '// blocking Trig_END_Actions for ~3s would delay the victory announcement, so this hands off to',
    '// its own timer-event trigger and returns immediately.',
    '',
    'function FF_ReportTick takes nothing returns nothing',
    '    local integer p = 1',
    '    loop',
    '        exitwhen p > 12',
    '        if FF_endWinner == 0 then',
    '            call MMD_FlagPlayer(ConvertedPlayer(p), MMD_FLAG_DRAWER)',
    '        elseif p == FF_endWinner then',
    '            call MMD_FlagPlayer(ConvertedPlayer(p), MMD_FLAG_WINNER)',
    '        else',
    '            call MMD_FlagPlayer(ConvertedPlayer(p), MMD_FLAG_LOSER)',
    '        endif',
    '        call TriggerSleepAction(0.25)',
    '        set p = p + 1',
    '    endloop',
    '    // Same host-bot signal the 799x END paths write once the MMD queue has drained.',
    '    call s__File_close(s__File_write(s__File_open("wc3mt.txt"), "wc3mt-GameEnd"))',
    'endfunction',
    '',
    '// winnerSlot 0 means nobody was left standing, which MMD reports as a draw.',
    'function FF_ReportEndGame takes integer winnerSlot returns nothing',
    '    local trigger t',
    '    if FF_endReported then',
    '        return',
    '    endif',
    '    set FF_endReported = true',
    '    set FF_endWinner = winnerSlot',
    '    set t = CreateTrigger()',
    '    call TriggerRegisterTimerEvent(t, 0.10, false)',
    '    call TriggerAddAction(t, function FF_ReportTick)',
    '    set t = null',
    'endfunction',
    '',
    '//===========================================================================',
    '// Startup. FF_Init is called from main() after InitCustomTriggers and defers the system inits',
    '// by 0.10s, so the map''s own init (udg_ globals, GUI triggers) has finished before these hook',
    '// events off it - same shape as the 799x build. FF_ObserverCamera_Init has no counterpart here',
    '// because SoloCam_Init already runs.',
    '',
    'function FF_BootTick takes nothing returns nothing',
    '    call DestroyTimer(GetExpiredTimer())',
    '    set FF_gameTimer = CreateTimer()',
    '    call TimerStart(FF_gameTimer, 1000000.0, false, null)',
    '    call FF_KillLog_Init()',
    '    call FF_GameResult_Init()',
    'endfunction',
    '',
    'function FF_Init takes nothing returns nothing',
    '    call TimerStart(CreateTimer(), 0.10, false, function FF_BootTick)',
    'endfunction',
    '',
    '//= FF-FUNCTIONS-END') -join $NL))

foreach ($bad in @('FFEnd_', 'FF_oc_', 'FF_gr_outOrder', 'FF_gr_outN', 'FF_kl_LocalClientIsBot')) {
    $code = ($header -split $NL | Where-Object { $_.TrimStart() -notlike '//*' }) -join $NL
    if ($code.Contains($bad)) { Fail "adapted module still references $bad" }
}
[IO.File]::WriteAllBytes((Join-Path $outDir 'ff_hostbot.jass'), $L.GetBytes($header))

foreach ($f in @('mmd_library.jass', 'ff_hostbot.jass')) {
    $p = Join-Path $outDir $f
    Write-Host ("{0}  {1} bytes  {2} lines" -f $f, (Get-Item $p).Length, ((Get-Content $p | Measure-Object -Line).Lines))
}
