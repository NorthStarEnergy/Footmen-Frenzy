from pathlib import Path
import re
import struct
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parent / 'hero-polish'))
from archive_helpers import functions

O = R / 'src'
O.mkdir(exist_ok=True)
helper = (R / 'hiring.j').read_text().replace('\n', '\r\n')

def patch_functions(s):
    fs = functions(s)
    anchor = fs['Trig_Start_game_Actions']
    assert 'FFHire_Prepare' not in s
    # Shops are already created by AP/SD before Start_game is invoked.
    replacement = anchor.replace('    call EnableTrigger(gg_trg_Update_Game_Time)',
                                 '    call FFHire_Prepare()\r\n    call EnableTrigger(gg_trg_Update_Game_Time)', 1)
    assert replacement != anchor
    return s.replace(anchor, helper + '\r\n' + replacement, 1)

def patch_globals(s):
    matches = list(re.finditer(r'(?m)^([ \t]*)hashtable FF_DebugHireHash\s*=\s*InitHashtable\(\)', s))
    assert len(matches) == 1
    m = matches[0]
    return s[:m.start()] + m[1] + 'boolean FFHire_Ready = false\r\n' + s[m.start():]

original = (R / 'original/war3map.j').read_bytes().decode('latin1')
runtime = patch_globals(patch_functions(original))
(O / 'war3map.j').write_bytes(runtime.encode('latin1'))
wct = (R / 'original/war3map.wct').read_bytes()
p = wct.index(0, 8) + 1
prefix = wct[:p]
chunks = []
changed_funcs = changed_globals = 0
while p < len(wct):
    n = struct.unpack_from('<I', wct, p)[0]
    p += 4
    b = wct[p:p+n]
    p += n
    txt = b.rstrip(b'\0').decode('latin1')
    if 'function Trig_Start_game_Actions takes' in txt:
        txt = patch_functions(txt)
        changed_funcs += 1
    if re.search(r'(?m)^[ \t]*hashtable FF_DebugHireHash\s*=', txt):
        txt = patch_globals(txt)
        changed_globals += 1
    chunks.append(txt.encode('latin1') + (b'\0' if b.endswith(b'\0') else b''))
assert p == len(wct) and changed_funcs == changed_globals == 1
(O / 'war3map.wct').write_bytes(prefix + b''.join(struct.pack('<I', len(b)) + b for b in chunks))
efs = functions(b'\n'.join(chunks).decode('latin1'))
rfs = functions(runtime)
for n in ['FFHire_CreateBuyer', 'FFHire_Prepare', 'Trig_Start_game_Actions']:
    assert efs[n].replace('\r', '') == rfs[n].replace('\r', '')
for n, body in functions(original).items():
    if n != 'Trig_Start_game_Actions':
        assert rfs[n] == body, n

s = (R / 'original/war3map.wts').read_bytes().decode('utf-8-sig')
values = {1: 'Footmen Frenzy 799X v65 - Hero Hiring Fix',
          997: '799X v65 - Hero Hiring Fix',
          998: 'Test build - October 29, 2026',
          999: 'v65: Restores hero hiring after dialog startup. Includes v64 Mundo cloud damage and visuals.'}
for n, text in values.items():
    pat = r'(STRING ' + str(n) + r'\s*\{)(.*?)(\})'
    assert len(re.findall(pat, s, re.S)) == 1
    s = re.sub(pat, lambda m: m[1] + '\r\n' + text + '\r\n' + m[3], s, flags=re.S)
s = s.replace('799X v64 - Mundo Cloud Fix|nPoison damage over time and denser disease clouds.|nBased on v63 item tooltip fixes.|n',
              '799X v65 - Hero Hiring Fix|nHero hiring restored for dialog-based modes.|nIncludes v64 Mundo cloud fix and v63 item tooltip fixes.|n')
(O / 'war3map.wts').write_bytes(s.encode('utf-8'))
maintenance = (R / 'original/FF_MAINTENANCE.md').read_bytes()
(O / 'FF_MAINTENANCE.md').write_bytes(maintenance + b'\r\n\r\nv65: Restore neutral-tavern buyer units after dialog startup, for all active AP players and team-specific SD/Carry taverns. AR direct assignment unchanged. Preserve v64 Mundo cloud fix. Runtime and WCT synchronized. Engine playtest pending.\r\n')
print('Prepared v65: startup dialogs and all existing functions preserved except shared game-start hiring hook.')
