from pathlib import Path
import sys, re, json, hashlib, subprocess, shutil, copy

O = Path(__file__).resolve().parent
P = O.parents[1]
B = O / 'baseline'
E = O / 'edited'
E.mkdir(exist_ok=True)
SRC = Path(r'C:\Users\Ryan1\Transfer\Veigar_Classic_v68\FF799X_Rx_Veigar_Classic_v68.w3x')
OUT = O / 'FF799X_Rx_DemonKnight_SoulHook_v70.w3x'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected = (O / 'baseline.sha256').read_text().strip()
assert sha(SRC) == expected, (sha(SRC), expected)
sys.path.insert(0, str(P / 'tools'))
import objdata_fieldmerge as obj
MPQ = P / 'tools/external/mpqcli-bin/mpqcli.exe'


def run(args, log):
    r = subprocess.run(list(map(str, args)), capture_output=True, text=True, encoding='utf8', errors='replace')
    (O / log).write_text(r.stdout + r.stderr, encoding='utf8')
    assert r.returncode == 0, (log, (r.stdout + r.stderr)[-1800:])
    return r.stdout


def tool(n, *a):
    return run([next((P / 'tools' / n / 'bin/Release').glob('*/' + n + '.exe')), *a], n + '.log')


def entry(t, k):
    return next(e for tab in t for e in tab if e.key() == k)


def tableof(t, k):
    return next(tab for tab in t if any(e.key() == k for e in tab))


def setv(e, k, v, level=0):
    m = [m for m in e.mods() if m.modid == k and m.level == level]
    assert len(m) == 1, (e.key(), k, level, len(m))
    m[0].value = v


def addv(e, k, v, level=0, pointer=0, typ=None):
    typ = typ if typ is not None else (3 if isinstance(v, str) else 0 if isinstance(v, int) else 1)
    m = [m for m in e.mods() if m.modid == k and m.level == level]
    if m:
        m[0].value = v
        m[0].vartype = typ
    else:
        e.sets[0][1].append(obj.Mod(k, typ, level, pointer, v, e.newid.encode('latin1')))


NAME = 'Soul Hook'
ICON = 'ReplaceableTextures\\CommandButtons\\BTNChainLightning.blp'
MANA = [60, 70, 80, 90, 100, 110]
CD = [12.0, 11.6, 11.2, 10.8, 10.4, 10.0]
DMG = [80 + 40 * r for r in range(1, 7)]
STUN = [0.5 + 0.1 * (r - 1) for r in range(1, 7)]
REQ = [1, 4, 7, 10, 13, 16]


def desc(r):
    return (f'Fire a soul hook 450 distance in about 0.25 seconds. It catches every ground enemy within 150 radius, '
            f'dealing {DMG[r-1]} magic damage and stunning for {STUN[r-1]:.1f} seconds, then drags each one partway '
            f'back toward you: 45% of its distance, at least 150 and at most 400, never closer than 100. Obstacles stop a drag.'
            f'|n|n|cffffcc00Mana:|r {MANA[r-1]}   |cffffcc00Cooldown:|r {CD[r-1]:g} sec.')


def research(r):
    return f'|cffffcc00Requires hero level {REQ[r-1]}|r|n|n' + desc(r)


# ---------------------------------------------------------------- abilities
v, t, l = obj.parse(str(B / 'war3map.w3a'))
assert obj.roundtrip_ok(str(B / 'war3map.w3a'))

assert not any(e.key() == 'ADk5' for tab in t for e in tab), 'ADk5 already exists'
hook = copy.deepcopy(entry(t, 'ADk1'))
hook.newid = 'ADk5'
for m in hook.mods():
    m.endtoken = b'ADk5'
tableof(t, 'ADk1').append(hook)
e = entry(t, 'ADk5')
for k, val in dict(anam=NAME, ahky='C', arhk='E', aart=ICON, arar=ICON, abpx=2, abpy=2, arpx=2, arpy=0,
                   alev=6, aher=1, aite=0, alsk=3, arlv=1, areq='',
                   aret='Learn Soul Hook [|cffffcc00E|r]').items():
    addv(e, k, val)
for r in range(1, 7):
    addv(e, 'atp1', f'{NAME} - Level {r} [|cffffcc00C|r]', r)
    addv(e, 'aub1', desc(r), r)
    addv(e, 'amcs', MANA[r - 1], r)
    addv(e, 'acdn', CD[r - 1], r)
    addv(e, 'aran', 450.0, r)
    addv(e, 'aare', 0.0, r)
    addv(e, 'adur', 0.0, r)
    addv(e, 'ahdu', 0.0, r)
    addv(e, 'atar', '', r)
    addv(e, 'abuf', '', r)
    addv(e, 'Ncl6', 'carrionswarm', r)
addv(e, 'arut', ('|cffffcc00Requires hero level 1|r|n|n'
                  'Fire a soul hook 450 distance. Catches every ground enemy within 150 radius, damaging and stunning them, '
                  'then drags each one partway back toward you. Excludes buildings, flying units and magic-immune targets.'
                  '|n|n|cffffcc00Mana:|r 60/70/80/90/100/110   |cffffcc00Cooldown:|r 12 sec, down to 10 sec.'), 0)

assert not any(e.key() == 'ADk6' for tab in t for e in tab), 'ADk6 already exists'
stun = copy.deepcopy(entry(t, 'AGtz'))
stun.newid = 'ADk6'
for m in stun.mods():
    m.endtoken = b'ADk6'
tableof(t, 'AGtz').append(stun)
e6 = entry(t, 'ADk6')
setv(e6, 'anam', 'Soul Hook stun')
for r in range(1, 7):
    setv(e6, 'adur', STUN[r - 1], r)
    setv(e6, 'ahdu', STUN[r - 1], r)
    setv(e6, 'amcs', 0, r)
    setv(e6, 'acdn', 0.0, r)
    setv(e6, 'aran', 1200.0, r)
    setv(e6, 'Htb1', 0.0, r)
    setv(e6, 'abuf', 'BGr2', r)
    setv(e6, 'atar', 'ground,air,enemies,vulnerable', r)

# Blood Tithe is no longer on the hero: strip its wording from the surviving tooltips.
for k in ('ADk1', 'ADk2'):
    for m in entry(t, k).mods():
        if isinstance(m.value, str):
            m.value = (m.value
                       .replace(' Adds Blood Tithe marks if learned.', '')
                       .replace('Hits ground enemies and adds one Blood Tithe mark if learned.', 'Hits ground enemies.'))
(E / 'war3map.w3a').write_bytes(obj.serialise(v, t, l))

# ---------------------------------------------------------------- hero
v, t, l = obj.parse(str(B / 'war3map.w3u'))
assert obj.roundtrip_ok(str(B / 'war3map.w3u'))
hero = entry(t, 'HDk1')
setv(hero, 'uhab', 'ADk1,ADk2,ADk5,ADk4')
setv(hero, 'utub', '|cff808080Category:|r Same as Monkey King (8)|n|nStrength bruiser. Reaping Axe damages a line and '
                   'pulls enemies on its return. Pulverize triggers on attacks with a short cooldown. Soul Hook fires a '
                   'fast short-range hook that damages, stuns and drags every enemy it catches partway back. Demon '
                   'Ascension grants magic immunity, regeneration, speed, cleave and a final ten seconds of life after '
                   'lethal damage.')
(E / 'war3map.w3u').write_bytes(obj.serialise(v, t, l))

# ---------------------------------------------------------------- script
s = (B / 'war3map.j').read_text(encoding='utf-8-sig')
original = s


def replace(a, b, count=1):
    global s
    assert s.count(a) == count, (a[:80], s.count(a))
    s = s.replace(a, b)


# Blood Tithe wording in the runtime research tooltips.
replace(' Adds Blood Tithe marks if learned.', '', 6)
replace('Hits ground enemies and adds one Blood Tithe mark if learned.', 'Hits ground enemies.', 6)

# Soul Hook helpers must precede DK_Tick, which calls them.
replace('function DK_Tick takes nothing returns nothing',
        (O / 'soulhook.j').read_text(encoding='utf-8') + '\nfunction DK_Tick takes nothing returns nothing')

# Release the tether and the drag claim when a Soul Hook state is recycled.
replace("""    elseif DK_Kind[i] == 9 then
        call DestroyLightning(LoadLightningHandle(DK_Hash, i, -30))
        call RemoveSavedHandle(DK_Hash, i, -30)
    endif""",
        """    elseif DK_Kind[i] == 9 then
        call DestroyLightning(LoadLightningHandle(DK_Hash, i, -30))
        call RemoveSavedHandle(DK_Hash, i, -30)
    elseif DK_Kind[i] == 11 then
        if LoadLightningHandle(DK_Hash, i, -31) != null then
            call DestroyLightning(LoadLightningHandle(DK_Hash, i, -31))
            call RemoveSavedHandle(DK_Hash, i, -31)
        endif
    elseif DK_Kind[i] == 12 then
        if LoadInteger(DK_Hash, GetHandleId(DK_Target[i]), -32) == i then
            call RemoveSavedInteger(DK_Hash, GetHandleId(DK_Target[i]), -32)
        endif
    endif""")

# Per-tick movement: kind 11 flies out then home, kind 12 drags its victim partway.
replace("""                    elseif distance > 0.01 then
                        call DK_Free(i)
                    endif
                endif
            elseif kind == 3 then""",
        """                    elseif distance > 0.01 then
                        call DK_Free(i)
                    endif
                endif
            elseif kind == 11 then
                if DK_End[i] <= DK_Now then
                    call DK_Free(i)
                else
                    if DK_Return[i] then
                        set dx = GetUnitX(DK_Source[i])-DK_X[i]
                        set dy = GetUnitY(DK_Source[i])-DK_Y[i]
                        set distance = SquareRoot(dx*dx+dy*dy)
                        if distance > 0.01 then
                            set DK_DX[i] = dx/distance
                            set DK_DY[i] = dy/distance
                        endif
                        set step = RMinBJ(84.375, distance)
                    else
                        set step = RMinBJ(56.25, DK_Left[i])
                        set DK_Left[i] = DK_Left[i]-step
                    endif
                    set DK_X[i] = DK_X[i]+DK_DX[i]*step
                    set DK_Y[i] = DK_Y[i]+DK_DY[i]*step
                    call BlzSetSpecialEffectX(DK_FX[i], DK_X[i])
                    call BlzSetSpecialEffectY(DK_FX[i], DK_Y[i])
                    call DK_HookChain(i)
                    call DK_HookCatch(i)
                    if DK_Kind[i] != 11 then
                        // Reflected damage may have freed the head inside the catch.
                    elseif DK_Return[i] then
                        if distance <= 84.375 then
                            call DK_Free(i)
                        endif
                    elseif DK_Left[i] <= 0.0 then
                        set DK_Return[i] = true
                    endif
                endif
            elseif kind == 12 then
                set v = DK_Target[i]
                if not FS_Alive(v) or not FS_Enemy(v, DK_Owner[i]) or DK_Left[i] <= 0.0 then
                    call DK_Free(i)
                else
                    set dx = GetUnitX(DK_Source[i])-GetUnitX(v)
                    set dy = GetUnitY(DK_Source[i])-GetUnitY(v)
                    set distance = SquareRoot(dx*dx+dy*dy)
                    set step = RMinBJ(40.0, RMinBJ(distance-100.0, DK_Left[i]))
                    if distance > 100.0 and step > 0.0 then
                        if DK_PullStep(v, GetUnitX(v)+dx/distance*step, GetUnitY(v)+dy/distance*step) then
                            set DK_Left[i] = DK_Left[i]-step
                        else
                            call DK_Free(i)
                        endif
                    else
                        call DK_Free(i)
                    endif
                endif
            elseif kind == 3 then""")

# Cast dispatch for the new C-slot ability.
replace("    elseif abilityId == 'ADk3' then",
        """    elseif abilityId == 'ADk5' then
        call DK_HookCast(source, level)
    elseif abilityId == 'ADk3' then""")

# Learn-panel tooltips, matching the pattern used by the other Demon Knight actives.
block = []
for r in range(1, 7):
    block.append(f"    call BlzSetAbilityResearchTooltip('ADk5', \"Learn Soul Hook [|cffffcc00E|r] - Level {r}\", {r-1})")
    block.append(f"    call BlzSetAbilityResearchExtendedTooltip('ADk5', \"{research(r)}\", {r-1})")
replace('    set DK_Hash = InitHashtable()', '\n'.join(block) + '\n    set DK_Hash = InitHashtable()')

(E / 'war3map.j').write_text(s, encoding='utf8')

# ---------------------------------------------------------------- packaging metadata
# No new assets in v70, so the import table is unchanged. prepare_editor_runtime.py
# still needs it present in the edited directory.
shutil.copyfile(B / 'war3map.imp', E / 'war3map.imp')
run([sys.executable, P / 'tools/prepare_editor_runtime.py', E, O / 'recovered-source'], 'recover-source.log')
notes = ('v70: Demon Knight C slot is Soul Hook (ADk5) instead of Blood Tithe (ADk3). Short-range fast hook: 450 reach in '
         'about 0.25 seconds, 150 catch radius, 120-320 magic damage, 0.5-1.0 sec stun, then each caught enemy is dragged '
         '45% of its distance back (min 150, max 400, never closer than 100). Reaping Axe / Pulverize / Demon Ascension '
         'unchanged. Built from v68; static validation only, engine playtest pending.')
(O / 'maintenance.txt').write_text(notes)
tool('EditorSourceSync', 'write', B / 'war3map.wtg', B / 'war3map.wct',
     O / 'recovered-source/globals.j', O / 'recovered-source/FF_Runtime.j', O / 'maintenance.txt', E)
(E / 'FF_MAINTENANCE.md').write_text((B / 'FF_MAINTENANCE.md').read_text(encoding='utf-8-sig') + '\n\n' + notes, encoding='utf8')
manifest = json.loads((O / 'recovered-source/FF_SOURCE_MANIFEST.json').read_text())
manifest.pop('baseline_checks', None)
manifest.update(source_map_sha256=expected, revision='v70 Demon Knight Soul Hook', engine_playtest=False)
(E / 'FF_SOURCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2))

wts = (B / 'war3map.wts').read_bytes()
wts, n = re.subn(rb'(STRING 1\s*\{\s*)[^\r\n]+', lambda m: m[1] + b'Footmen Frenzy 799X Veigar Classic v70', wts, count=1)
assert n == 1
(E / 'war3map.wts').write_bytes(wts)

# ---------------------------------------------------------------- static validation
tool('JassCheck', E / 'war3map.j')
J = Path(r'C:\Users\Ryan1\Documents\Warcraft III\JassHelper')
compiler = Path(r'C:\Program Files\Warcraft III\_retail_\x86_64\JassHelper\pjass.exe')
run([compiler, J / 'common.j', J / 'Blizzard.j', E / 'war3map.j'], 'pjass.log')
run([compiler, J / 'common.j', J / 'Blizzard.j', O / 'recovered-source/editor_regeneration_input.j'], 'editor-pjass.log')

# ---------------------------------------------------------------- pack and verify
members = [str(f.relative_to(E)) for f in E.rglob('*') if f.is_file()]
shutil.copy2(SRC, OUT)
for n in members:
    run([MPQ, 'add', OUT, E / n, '-p', n, '-w'], 'pack-last.log')
V = O / 'verified'
V.mkdir(exist_ok=True)
for n in members:
    run([MPQ, 'extract', OUT, '-o', V, '-f', n, '-k'], 'extract-last.log')
    assert (E / n).read_bytes() == (V / n).read_bytes(), n
tool('EditorSourceSync', 'export', V / 'war3map.wtg', V / 'war3map.wct', O / 'verified-source')
run([sys.executable, P / 'tools/check_editor_runtime.py', '--globals', O / 'verified-source/globals.j',
     '--runtime', O / 'verified-source/FF_Runtime.j', '--script', V / 'war3map.j',
     '--report', O / 'source-verification.json'], 'source-check.log')
assert sha(SRC) == expected
from check_editor_runtime import parse_source
a = parse_source(original)
b = parse_source(s)
assert a.globals == b.globals, 'global declarations changed'
(O / 'verification.json').write_text(json.dumps(dict(
    passed=True, source_sha256=expected, output_sha256=sha(OUT), changed_members=members,
    changed_functions=[n for n in a.functions if a.functions[n] != b.functions[n]],
    new_functions=sorted(set(b.functions) - set(a.functions)),
    globals_unchanged=True, engine_tested=False), indent=2))
print(OUT)
