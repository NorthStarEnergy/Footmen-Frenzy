from pathlib import Path
import json
import re
import struct
import sys

R = Path(__file__).resolve().parent
W = R.parent
sys.path.insert(0, str(W / 'hero-polish'))
from archive_helpers import archive, functions

BASE = W / 'taverns-v66/release/FF799X_Rx_Team_Taverns_v66.w3x'
O = R / 'src'
O.mkdir(exist_ok=True)
a = archive(BASE)
original = a.read_file('war3map.j').decode('latin1').replace('\r', '')
module = (R / 'progression.j').read_text()
declarations = (R / 'globals.j').read_text()
changed = {}

def replace_function(s, name, body):
    old = functions(s)[name]
    return s.replace(old, body, 1)

fs = functions(original)
for name, call in [
    ('Trig_Start_game_Actions', 'P67_Start'),
    ('Trig_Mass_END_Actions', 'P67_MassFinished'),
    ('Trig_colossal_spawn_Actions', 'P67_ColoSpawn'),
]:
    old = fs[name]
    # These three functions have no locals.
    changed[name] = old.replace('returns nothing\n', 'returns nothing\n    call ' + call + '()\n', 1)

name = 'Trig_Set_Exp_Bonus_Rate_Upon_Leveling_Actions'
changed[name] = fs[name].replace('returns nothing\n', '''returns nothing
    if P67_Enabled() then
        call P67_OnLevel()
        return
    endif
''', 1)

name = 'Trig_Footy_Bounty_Increase_Delay_Actions'
changed[name] = fs[name].replace('    call DisableTrigger(gg_trg_Foot_Exp_system)', '''    // Pub recovery follows individual levels instead of map-load time.
    if not P67_Enabled() then
        call DisableTrigger(gg_trg_Foot_Exp_system)
    endif''')

name = 'Trig_Foot_Exp_system_Actions'
changed[name] = fs[name].replace('        set udg_exp_sys_level_Foot=6', '''        set udg_exp_sys_level_Foot=6
        if P67_Enabled() and P67_FirstColo then
            set udg_exp_sys_level_Foot=7
        endif''')

name = 'Trig_HERO_Blademaster_Illusions_Actions'
changed[name] = fs[name].replace('        call AddHeroXPSwapped(udg_temp_int, udg_herO[udg_temp_playernumber], true)', '''        if P67_Enabled() then
            call P67_AddSupplement(udg_herO[udg_temp_playernumber], I2R(udg_temp_int))
        else
            call AddHeroXPSwapped(udg_temp_int, udg_herO[udg_temp_playernumber], true)
        endif''')

for name, suffix in [
    ('Trig_Unit_Experience_System_Func004Func012A', '_Copy'),
    ('Trig_Unit_Experience_System_Func005Func012A', ''),
    ('Trig_Unit_Experience_System_Func006Func012A', '_T2'),
    ('Trig_Foot_Exp_system_Func002Func011A', '_Foot'),
]:
    old = fs[name]
    condition = re.search(r'    if \( (\w+)\(\) \) then', old)[1]
    legacy = old[old.index('        set udg_ExpInt'):old.index('\n    else')]
    changed[name] = f'''function {name} takes nothing returns nothing
    if ( {condition}() ) then
        if P67_Enabled() then
            if udg_ExpInt{suffix}[0] > 0 then
                call P67_AddSupplement(GetEnumUnit(), I2R(udg_exp_sys_high{suffix} - udg_exp_sys_low{suffix}) / I2R(udg_ExpInt{suffix}[0]))
            endif
        else
{''.join('    ' + line + chr(10) for line in legacy.splitlines()).rstrip()}
        endif
    endif
endfunction'''

def patch(s):
    s = s.replace('\r', '')
    for name, body in changed.items():
        s = replace_function(s, name, body)
    anchor = 'function FFHire_CreateBuyer takes'
    assert s.count(anchor) == 1
    return s.replace(anchor, module + '\n' + anchor, 1)

s, count = re.subn(r'^endglobals\b', lambda _: declarations + '\nendglobals', patch(original), count=1, flags=re.M)
assert count == 1
(O / 'war3map.j').write_bytes(s.encode('latin1'))

w = a.read_file('war3map.wct')
p = w.index(0, 8) + 1
prefix = w[:p]
chunks = []
patch_count = 0
global_count = 0
while p < len(w):
    n = struct.unpack_from('<I', w, p)[0]
    p += 4
    b = w[p:p+n]
    p += n
    t = b.rstrip(b'\0').decode('latin1').replace('\r', '')
    if 'function Trig_Start_game_Actions takes' in t:
        t = patch(t)
        patch_count += 1
    if re.search(r'^globals\b', t, re.M):
        t, count = re.subn(r'^endglobals\b', lambda _: declarations + '\nendglobals', t, count=1, flags=re.M)
        assert count == 1
        global_count += 1
    chunks.append(t.encode('latin1') + (b'\0' if b.endswith(b'\0') else b''))
assert patch_count == global_count == 1
(O / 'war3map.wct').write_bytes(prefix + b''.join(struct.pack('<I', len(b)) + b for b in chunks))

wts = a.read_file('war3map.wts').decode('utf-8-sig')
for n, text in {
    1: 'Footmen Frenzy 799X v67 - Pub XP Test',
    997: '799X v67 - Pub XP Test',
    998: 'Test build - October 30, 2026',
    999: 'v67: Kill-earned pub catch-up through level 6, then 70% XP from level 7 onward. First colo activates double XP below 7. No free levels. Includes v66 team taverns and range corrections.',
    3435: '799X v67 - Pub XP Test|nKill-earned catch-up toward level 7; 70% XP at 7+.|nFirst colo activates double XP below 7.|nPublic draft records: F9 or -draft.|n',
}.items():
    wts, count = re.subn(r'(STRING ' + str(n) + r'\s*\{).*?(\})', lambda m: m[1] + '\n' + text + '\n' + m[2], wts, flags=re.S)
    assert count == 1
(O / 'war3map.wts').write_bytes(re.sub(r'\r+\n', '\n', wts).replace('\n', '\r\n').encode('utf-8'))
(O / 'FF_MAINTENANCE.md').write_bytes(a.read_file('FF_MAINTENANCE.md') + b'\n\nv67 Pub XP TEST: normal Pub with mass and colossals only. Existing below-4 200% catch-up now expires per hero; below-6 150% after first level 6 or mass end; from first colo spawn below-7 200%; level 7+ 70%. Native kill XP and scripted unit supplements use the rate. Footman supplement extends to below 7 after first colo and no longer expires at map-time 480s in normal Pub. All XP remains kill-earned; no free XP or level floors. Runtime/WCT synchronized. In-engine and balance playtests pending.\n')
(R / 'changes.json').write_text(json.dumps({'base': str(BASE), 'changed_functions': sorted(changed), 'added_functions': sorted(functions(module)), 'rates': {'approach6': 150, 'catchup': 200, 'level7plus': 70}}, indent=2))
print('Prepared v67 pub XP test source and synchronized editor source.')
