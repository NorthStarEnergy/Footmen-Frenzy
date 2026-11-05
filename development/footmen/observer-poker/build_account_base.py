"""Build a separate integration baseline; account wagering is not implemented."""
from pathlib import Path
import ctypes as c
import hashlib
import re
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BASE = Path.home() / 'Downloads/FF799X_v42_account_gold_TEST_ONLY.w3x'
OUT = ROOT / 'release/FF799X_account_poker_integration_TEST_ONLY.w3x'
sys.path.insert(0, str(ROOT.parent / '799x-backport/tools'))
from mpyq import MPQArchive
sys.path.insert(0, str(ROOT.parent / 'six-player-ffa'))
from archive import s

a = MPQArchive(str(BASE), listfile=False)
source = a.read_file('war3map.j').decode('utf-8-sig')
imports = a.read_file('war3map.imp')
assert source and imports and 'function FGA_Init takes' in source
module = (ROOT / 'poker.j').read_text(encoding='utf-8')
ui = (ROOT / 'ui.j').read_text(encoding='utf-8')
functions = {m[1]: m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction', ui)}
for name in ('PK_Render', 'PK_Start'):
    module, count = re.subn(r'(?ms)^function ' + name + r'\b.*?^endfunction', lambda _: functions[name], module)
    assert count == 1
helpers = '\n\n'.join(functions[n] for n in ('PK_Texture', 'PK_Label', 'PK_ChipArt'))
module = module.replace('function PK_Render takes', helpers + '\n\nfunction PK_Render takes', 1)
module = module.replace('BlzFrameSetSize(f,width,0.035)', 'BlzFrameSetSize(f,width,0.029)')
module = module.replace('Solo practice pauses the battlefield.', 'Practice chips are separate from account gold.')
globals_ = (ROOT / 'poker-globals.j').read_text(encoding='utf-8')
patched = source.replace('\nendglobals', '\n' + globals_ + '\nendglobals', 1)
patched = patched.replace('function main takes nothing returns nothing', module + '\nfunction main takes nothing returns nothing', 1)
assert patched.count('    call InitCustomTriggers()') == 1
patched = patched.replace('    call InitCustomTriggers()', '    call InitCustomTriggers()\n    call PK_Init()', 1)
work = ROOT / 'account-integration'
work.mkdir(exist_ok=True)
script = work / 'war3map.j'
script.write_text(patched, encoding='utf-8', newline='\n')
version, count = struct.unpack_from('<II', imports)
art = sorted((ROOT / 'src/PokerUI').glob('*.blp'))
assert len(art) == 60
imp = work / 'war3map.imp'
imp.write_bytes(struct.pack('<II', version, count + len(art)) + imports[8:] + b''.join(b'\rPokerUI\\' + f.name.encode() + b'\0' for f in art))
home = Path.home()
compiler = home / 'Documents/Codex/2026-10-28/thi/work/jasshelper/pjass.exe'
jass = home / 'Documents/Codex/2026-10-20/brin/outputs/Google Drive Files/Old PC/Documents/Warcraft III/JassHelper'
result = subprocess.run([str(compiler), str(jass/'common.j'), str(jass/'Blizzard.j'), str(script)], capture_output=True, text=True)
(work/'compile.log').write_text(result.stdout + result.stderr, encoding='utf-8')
assert result.returncode == 0, result.stdout + result.stderr
OUT.parent.mkdir(exist_ok=True)
shutil.copy2(BASE, OUT)
h = c.c_void_p()
assert s.SFileOpenArchive(str(OUT), 0, 0, c.byref(h))
try:
    for file, name in [(script, 'war3map.j'), (imp, 'war3map.imp')] + [(f, 'PokerUI\\' + f.name) for f in art]:
        assert s.SFileAddFileEx(h, str(file), name.encode(), 0x80000200, 2, 2), name
finally:
    s.SFileCloseArchive(h)
check = MPQArchive(str(OUT), listfile=False)
assert check.read_file('war3map.j') == script.read_bytes()
assert check.read_file('war3map.imp') == imp.read_bytes()
for f in art:
    assert check.read_file('PokerUI\\' + f.name) == f.read_bytes(), f.name
print('Created', OUT, 'SHA256', hashlib.sha256(OUT.read_bytes()).hexdigest())
