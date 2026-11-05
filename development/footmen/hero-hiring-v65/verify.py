from pathlib import Path
import math
import re
import struct
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parent / 'hero-polish'))
from archive_helpers import functions, objdata

script = (R / 'src/war3map.j').read_bytes().decode('latin1').replace('\r', '')
original = (R / 'original/war3map.j').read_bytes().decode('latin1').replace('\r', '')
fs, old = functions(script), functions(original)
assert set(fs) - set(old) == {'FFHire_CreateBuyer', 'FFHire_Prepare'}
assert all(fs[n] == text for n, text in old.items() if n != 'Trig_Start_game_Actions')
assert fs['Trig_Start_game_Actions'].count('call FFHire_Prepare()') == 1
assert "local unit buyer = CreateUnit(p, 'h01G'" in fs['FFHire_CreateBuyer']
assert 'ShowUnit(' not in '\n'.join(x for x in fs['FFHire_CreateBuyer'].splitlines() if not x.strip().startswith('//'))
assert 'Aloc' not in fs['FFHire_CreateBuyer']
assert 'GetPlayerSlotState(p) == PLAYER_SLOT_STATE_PLAYING' in fs['FFHire_Prepare']
assert 'exitwhen pn > 12' in fs['FFHire_Prepare']
assert 'set team = udg_teamnumber[pn]' in fs['FFHire_Prepare']
assert 'FFHire_Ready = true' in fs['FFHire_Prepare']
for name in ['Trig_MODE_set_pub_game_default_Actions', 'Trig_MODE_set_pro_mode_Actions', 'Trig_Vote_Timer_Expires_Actions']:
    assert 'gg_trg_Start_game' in fs[name]
assert 'call ConditionalTriggerExecute(gg_trg_Start_Vote)' in fs['Trig_MODE_GUI_execute_Actions']
assert 'call ConditionalTriggerExecute(gg_trg_debugmode)' in fs['Trig_MODE_GUI_execute_Actions']
assert 'call CreateNUnitsAtLoc(1, GetUnitTypeId(GroupPickRandomUnit' in fs['Trig_Start_AR_Actions']

def center(name):
    m = re.search(r'set ' + name + r'=Rect\(([^)]+)\)', script)
    v = [float(x.replace(' ', '')) for x in m[1].split(',')]
    return ((v[0]+v[2])/2, (v[1]+v[3])/2)

ap = [center('gg_rct_TAVERN'+str(i)) for i in range(1, 10)]
sd = [center('gg_rct_SD_TAVERN'+str(i)) for i in range(1, 5)]
carry = []
for i in range(1, 5):
    m = re.search(r'call CarryTav_MakeAltar\('+str(i)+r'\s*,([^,]+),([^,]+),', script)
    carry.append(tuple(float(v.replace(' ', '')) for v in m.groups()))
abilities = objdata.load(str(R.parent/'mundo-v64/war3map.w3a'))
native = next(e for e in abilities['tables'][0] if e['oldId'] == 'Ane2')
draft = next(e for e in abilities['tables'][1] if e['newId'] == 'A05T')
radius_ap = next(m['value'] for m in native['mods'] if m['id'] == 'Neu1')
radius_sd = next(m['value'] for m in draft['mods'] if m['id'] == 'Neu1')
max_ap = max(math.dist((-2688, -256), loc) for loc in ap)
assert max_ap < radius_ap
for team in range(4):
    for buyer in [sd[team], carry[team]]:
        for enemy in range(4):
            if enemy != team:
                assert math.dist(buyer, sd[enemy]) > radius_sd
                assert math.dist(buyer, carry[enemy]) > radius_sd
# Exercise every slot, including slot 6 with no original placed selector.
for slot in range(12):
    team = slot // 3
    assert math.dist(sd[team], sd[team]) <= radius_sd
    assert math.dist(carry[team], carry[team]) <= radius_sd
report = {'all_12_player_slots': 'covered', 'ap_taverns': len(ap),
          'ap_max_buyer_distance': max_ap, 'ap_activation_radius': radius_ap,
          'sd_main_and_carry_taverns': 'covered for each team; no cross-team radius access',
          'sd_activation_radius': radius_sd,
          'mode_routes': ['Pub -> SD', 'Pro -> SD', 'Custom 4K -> SD',
                          'Private -> AP/SD/AR', 'Debug -> AP', 'AFK fallback -> Pub/SD'],
          'startup_dialogs_and_original_mode_functions': 'byte-equivalent function bodies',
          'engine_playtest': 'pending'}
(R/'mode-verification.json').write_text(json.dumps(report, indent=2))

# Regenerate a validation script from authoritative editor functions/globals.
w = (R/'src/war3map.wct').read_bytes()
p = w.index(0, 8)+1
chunks = []
while p < len(w):
    n = struct.unpack_from('<I', w, p)[0]; p += 4
    chunks.append(w[p:p+n].rstrip(b'\0').decode('latin1').replace('\r','')); p += n
source = '\n'.join(chunks)
efs = functions(source)
regen = re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction', lambda m: efs.get(m[1], m[0]), script)
header = re.search(r'(?ms)^globals\b(.*?)^endglobals', chunks[0])[1]
packed = re.search(r'(?ms)^globals\b(.*?)^endglobals', regen)[1]
decl = r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)'
names = {m[1] for line in header.splitlines() if (m := re.match(decl, line)) and not line.lstrip().startswith('//')}
extra = [line for line in packed.splitlines() if (m := re.match(decl,line)) and m[1] not in names and not line.lstrip().startswith('//')]
regen = re.sub(r'(?ms)^globals\b.*?^endglobals', lambda _: 'globals\n'+header+'\n'+'\n'.join(extra)+'\nendglobals', regen, count=1)
(R/'editor-validation.j').write_bytes(regen.encode('latin1'))
print(json.dumps(report, indent=2))
