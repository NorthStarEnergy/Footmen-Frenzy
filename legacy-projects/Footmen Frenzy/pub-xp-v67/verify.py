"""Source integration gates and execution tests of the actual JASS helper bodies.

The small translation harness stubs engine natives; it does NOT simulate native
death/XP ordering or substitute for a Warcraft playtest.
"""
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
import json
import re
import struct
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parent / 'hero-polish'))
from archive_helpers import archive, functions

manifest = json.loads((R / 'changes.json').read_text())
old = archive(Path(manifest['base'])).read_file('war3map.j').decode('latin1').replace('\r', '')
script = (R / 'src/war3map.j').read_bytes().decode('latin1').replace('\r', '')
oldfs, fs = functions(old), functions(script)
assert set(oldfs) <= set(fs)
assert set(fs) - set(oldfs) == set(manifest['added_functions'])
assert {n for n in oldfs if oldfs[n] != fs[n]} == set(manifest['changed_functions'])

# Reconstruct the compiler input from authoritative editor functions/globals.
w = (R / 'src/war3map.wct').read_bytes()
p = w.index(0, 8) + 1
chunks = []
while p < len(w):
    n = struct.unpack_from('<I', w, p)[0]
    p += 4
    chunks.append(w[p:p+n].rstrip(b'\0').decode('latin1').replace('\r', ''))
    p += n
source = '\n'.join(chunks)
efs = functions(source)
for n in manifest['added_functions'] + manifest['changed_functions']:
    assert efs[n] == fs[n], n
regen = re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction', lambda m: efs.get(m[1], m[0]), script)
header = re.search(r'(?ms)^globals\b(.*?)^endglobals', chunks[0])[1]
packed = re.search(r'(?ms)^globals\b(.*?)^endglobals', regen)[1]
decl = r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)'
names = {m[1] for line in header.splitlines() if (m := re.match(decl, line)) and not line.lstrip().startswith('//')}
extra = [line for line in packed.splitlines() if (m := re.match(decl, line)) and m[1] not in names and not line.lstrip().startswith('//')]
regen = re.sub(r'(?ms)^globals\b.*?^endglobals', lambda _: 'globals\n' + header + '\n' + '\n'.join(extra) + '\nendglobals', regen, count=1)
(R / 'editor-validation.j').write_bytes(regen.encode('latin1'))
for line in (R / 'globals.j').read_text().splitlines():
    assert line in header and line in packed

# Execute the helper bodies themselves, not a separate implementation of rates.
module = (R / 'progression.j').read_text()
g = {}
for line in (R / 'globals.j').read_text().splitlines():
    m = re.match(r'(?:constant )?\w+ (\w+) = (.*)', line)
    if m:
        g[m[1]] = eval(m[2].replace('false', 'False').replace('true', 'True'))
    else:
        m = re.match(r'(\w+) array (\w+)', line)
        assert m, line
        g[m[2]] = defaultdict(float if m[1] == 'real' else lambda: None)
mode_flags = ['udg_mode_pub', 'FFR4Pro', 'udg_mode_promode', 'FFMode4K', 'FFModePrivateVote', 'udg_mode_inhouse', 'udg_mode_debugmode', 'udg_mode_overdrive', 'udg_FFCH_Mode', 'udg_mode_no_mass', 'udg_colossal_on']
for flag in mode_flags:
    g[flag] = flag in ['udg_mode_pub', 'udg_colossal_on']
g.update(udg_player_active=defaultdict(bool), udg_herO=defaultdict(lambda: None), udg_maphack=defaultdict(bool), udg_colossal_wave=1)
global_names = list(g)

def expr(s):
    return re.sub(r'\b(null|true|false)\b', lambda m: {'null': 'None', 'true': 'True', 'false': 'False'}[m[1]], s).replace('function ', '')

python = []
for name, body in functions(module).items():
    lines = body.splitlines()
    params = re.search(r'takes (.*?) returns', lines[0])[1]
    params = [] if params == 'nothing' else [s.strip().split()[1] for s in params.split(',')]
    python += ['def ' + name + '(' + ', '.join(params) + '):', '    global ' + ', '.join(global_names)]
    depth = 1
    for raw in lines[1:-1]:
        line = raw.split('//')[0].strip()
        if not line:
            continue
        if line in ['endif', 'endloop']:
            depth -= 1
            continue
        if line == 'else':
            depth -= 1
            python.append('    ' * depth + 'else:')
            depth += 1
            continue
        if line.startswith('local '):
            parts = line.split(None, 2)
            translated = parts[2] if '=' in parts[2] else parts[2] + ' = None'
        elif line.startswith('set '):
            translated = line[4:]
        elif line.startswith('call '):
            translated = line[5:]
        elif line.startswith('if ') and line.endswith(' then'):
            translated = line[:-5] + ':'
        elif line == 'loop':
            translated = 'while True:'
        elif line.startswith('exitwhen '):
            translated = 'if ' + line[9:] + ': break'
        elif line.startswith('return'):
            translated = line
        else:
            raise AssertionError('Unsupported JASS: ' + line)
        python.append('    ' * depth + expr(translated))
        if line == 'loop' or (line.startswith('if ') and line.endswith(' then')):
            depth += 1
    assert depth == 1, name

rates = {}
timers = []
xp_calls = []
g.update(
    UNIT_TYPE_HERO=1,
    GetUnitTypeId=lambda u: 0 if u is None or u.removed else 1,
    IsUnitType=lambda u, t: u.hero,
    IsUnitIllusion=lambda u: u.illusion,
    GetOwningPlayer=lambda u: u.owner,
    GetPlayerId=lambda p: p,
    GetHeroLevel=lambda u: u.level,
    GetHeroXP=lambda u: u.xp,
    Player=lambda p: p,
    SetPlayerHandicapXPBJ=lambda p, rate: rates.__setitem__(p, rate),
    R2I=int, I2R=float,
    CreateTimer=lambda: object(),
    TimerStart=lambda *args: timers.append(args),
    DisplayTextToForce=lambda *args: None,
    GetPlayersAll=lambda: None,
    GetTriggerUnit=lambda: g.get('trigger_unit'),
)
def set_xp(u, amount, eye_candy):
    xp_calls.append(amount - u.xp)
    u.xp = amount
g['SetHeroXP'] = set_xp
exec('\n'.join(python), g)

rate = g['P67_Rate']
cases = [
    ((3, False, False, False, False), 100),
    ((3, True, False, False, False), 200),
    ((4, True, False, False, False), 100),
    ((5, True, False, False, False), 100),
    ((3, True, True, False, False), 200),
    ((4, True, True, False, False), 150),
    ((5, True, False, True, False), 150),
    ((6, True, True, True, False), 100),
    ((6, True, True, True, True), 200),
    ((7, True, True, True, True), 70),
    ((10, True, True, True, True), 70),
]
for args, expected in cases:
    assert rate(*args) == expected, args
for level in range(1, 7):
    assert rate(level, True, True, True, True) == 200
for level in range(7, 19):
    for first_colo in [False, True]:
        assert rate(level, True, True, True, first_colo) == 70

# Exclude all alternate modes individually; normal Pub is the sole target.
assert g['P67_Enabled']()
for flag in mode_flags:
    original_value = g[flag]
    g[flag] = not original_value
    assert not g['P67_Enabled'](), flag
    g[flag] = original_value

def hero(slot, level):
    u = SimpleNamespace(owner=slot-1, level=level, xp=0, hero=True, illusion=False, removed=False)
    g['udg_herO'][slot] = u
    g['udg_player_active'][slot] = True
    return u

lagger, leader, seven = hero(1, 3), hero(12, 4), hero(3, 7)
g['P67_Start']()
assert rates[0] == 200 and rates[11] == 150 and rates[2] == 70
assert len(timers) == 1 and not xp_calls
g['P67_Start']()
assert len(timers) == 1
# A later hero reaching four gets its own rate reset; nobody else's first five
# can revoke the remaining below-four hero's catch-up.
seven.level = 3
leader.level = 5
lagger.level = 4
g['trigger_unit'] = lagger
g['P67_OnLevel']()
assert rates[0] == 150 and rates[2] == 200
lagger.level = 6
g['P67_MassFinished']()
assert rates[0] == 100
g['P67_ColoSpawn']()
assert g['P67_FirstColo'] and rates[0] == 200
assert not xp_calls, 'No start/phase/level event may grant XP'
lagger.level = 7
g['P67_OnLevel']()
assert rates[0] == 70
for _ in range(10):
    g['P67_AddSupplement'](lagger, 1.0)
assert lagger.xp == 7, 'Fractional reductions must not discard small awards'
lagger.level = 6
g['P67_AddSupplement'](lagger, 6.0 / 12.0)
assert lagger.xp == 8, 'A shared small kill supplement still grants earned XP'
g['udg_maphack'][1] = True
g['P67_Refresh']()
assert rates[0] == 25
g['udg_maphack'][1] = False
lagger.illusion = True
before = lagger.xp
g['P67_AddSupplement'](lagger, 1000.0)
assert lagger.xp == before
lagger.illusion = False
old_lagger = lagger
lagger = hero(1, 6)
g['P67_Refresh']()
assert rates[0] == 200
assert not g['P67_ValidHero'](old_lagger)
g['P67_AddSupplement'](lagger, 0.5)
assert lagger.xp == 1
g['udg_player_active'][1] = False
assert not g['P67_ValidHero'](lagger)

# Every legacy direct SetHeroXP kill supplement is routed through the scaler
# only in Pub; the original arithmetic remains in each non-Pub branch.
for n in manifest['changed_functions']:
    if 'SetHeroXP' in oldfs[n]:
        assert 'P67_AddSupplement' in fs[n] and 'SetHeroXP' in fs[n]
assert 'P67_AddSupplement' in fs['Trig_HERO_Blademaster_Illusions_Actions']
assert 'AddHeroXPSwapped' in fs['Trig_HERO_Blademaster_Illusions_Actions']
assert fs['Trig_TP_hero_Actions'] == oldfs['Trig_TP_hero_Actions']
assert 'if not P67_Enabled() then' in fs['Trig_Footy_Bounty_Increase_Delay_Actions']
assert 'set udg_exp_sys_level_Foot=7' in fs['Trig_Foot_Exp_system_Actions']
assert 'SetHeroXP' not in fs['P67_Refresh'] + fs['P67_MassFinished'] + fs['P67_ColoSpawn']

report = {'passed': True, 'rate_boundary_cases': len(cases) + 6 + 24, 'alternate_mode_guards': len(mode_flags), 'scenarios': ['individual level-4 expiry', 'first-level-5 does not revoke catch-up', 'slot-order-independent milestones', 'mass/colo transitions', 'level-7 slowdown', 'fractional shared rewards', 'anti-cheat penalty', 'illusion/inactive/replaced hero exclusion', 'idempotent start', 'no automatic XP grants'], 'editor_runtime_synchronized': True, 'preserved_functions': len(oldfs) - len(manifest['changed_functions']), 'engine_native_ordering_and_balance': 'Not tested; Warcraft playtest required'}
(R / 'checks.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
