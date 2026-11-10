"""Compile and package the blackjack / match betting test map, without editing inputs."""
from pathlib import Path
import ctypes as c
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
POKER = ROOT.parent / 'observer-poker'
BASE = Path.home() / 'Downloads/FF799X_v42_account_gold_TEST_ONLY.w3x'
OUT = ROOT / 'release/FF799X_v42_Casino_v1_2_TEST_ONLY.w3x'
sys.path.insert(0,str(ROOT.parent/'799x-backport/tools'))
from mpyq import MPQArchive
sys.path.insert(0,str(ROOT.parent/'six-player-ffa'))
from archive import s

def replace_once(text, before, after):
    assert text.count(before) == 1, before[:100]
    return text.replace(before,after,1)

def archive_entries(path):
    a = MPQArchive(str(path),listfile=False)
    result = {}
    for e in a.hash_table:
        if e.block_table_index >= len(a.block_table):
            continue
        key = (e.hash_a,e.hash_b,e.locale,e.platform)
        a.get_hash_table_entry = lambda _, e=e:e
        try:
            result[key] = a.read_file('ignored')
        except (RuntimeError,NotImplementedError):
            block = a.block_table[e.block_table_index]
            a.file.seek(block.offset+a.header['offset'])
            result[key] = (block.flags,block.size,a.file.read(block.archived_size))
    return result

def main():
    from make_panel import main as make_panel
    make_panel()
    a = MPQArchive(str(BASE),listfile=False)
    original = a.read_file('war3map.j').decode('utf-8-sig')
    source = original
    imports = a.read_file('war3map.imp')
    strings = a.read_file('war3map.wts')
    poker = (POKER/'poker.j').read_text(encoding='utf-8')
    ui = (ROOT/'poker-ui.j').read_text(encoding='utf-8')
    functions = {m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',ui)}
    for name in ('PK_Render','PK_Start','PK_Button'):
        poker,n = re.subn(r'(?ms)^function '+name+r'\b.*?^endfunction',lambda _:functions[name],poker)
        assert n == 1
    helpers = '\n\n'.join(functions[n] for n in ('PK_Texture','PK_Label','PK_ChipArt'))
    poker = replace_once(poker,'function PK_Render takes',helpers+'\n\nfunction PK_Render takes')
    poker = poker.replace('BlzFrameSetSize(f,width,0.035)','BlzFrameSetSize(f,width,0.029)')
    poker = poker.replace('Solo practice pauses the battlefield.','Open -blackjack / -bets for account-gold games.')
    poker = replace_once(poker,'        set PK_Hidden[p] = false','        set CAS_view[p+1] = 0\n        if GetLocalPlayer() == Player(p) and CAS_root[p+1] != null then\n            call BlzFrameSetVisible(CAS_root[p+1],false)\n        endif\n        set PK_Hidden[p] = false')
    globals_ = (POKER/'poker-globals.j').read_text(encoding='utf-8')+'\n'+(ROOT/'casino-globals.j').read_text(encoding='utf-8')
    module = (ROOT/'buttons.j').read_text(encoding='utf-8')+'\n'+poker+'\n'+'\n'.join((ROOT/name).read_text(encoding='utf-8') for name in ('wallet.j','blackjack.j','markets.j','duels.j','ui.j','start.j'))
    source = replace_once(source,'\nendglobals','\n'+globals_+'\nendglobals')
    source = replace_once(source,'function main takes nothing returns nothing',module+'\nfunction main takes nothing returns nothing')
    source = replace_once(source,'    call InitCustomTriggers()','    call InitCustomTriggers()\n    call PK_Init()\n    call CAS_Init()')
    before_base = 'function Trig_player_destroyed_Actions takes nothing returns nothing\n'
    base_hook = '    if CAS_baseEvent != null then\n        set CAS_baseVictim = GetDyingUnit()\n        set CAS_baseKiller = GetKillingUnit()\n        call TriggerExecute(CAS_baseEvent)\n        set CAS_baseVictim = null\n        set CAS_baseKiller = null\n    endif\n'
    source = replace_once(source,before_base,before_base+base_hook)
    settle_hook = '    set CAS_winner = winner\n    if CAS_matchEvent != null then\n        call TriggerExecute(CAS_matchEvent)\n    endif\n'
    source = replace_once(source,'    set FGA_settled=true',settle_hook+'    set FGA_settled=true')
    # Show a unique lobby name. WTS remains otherwise byte-for-byte identical.
    name = b'FF799X - Casino v1.2 TEST ONLY'
    wts,n = re.subn(rb'(STRING 1\s*\{\s*)[^\r\n]+',lambda m:m[1]+name,strings,count=1)
    assert n == 1
    work = ROOT/'src'
    work.mkdir(exist_ok=True)
    script = work/'war3map.j'
    script.write_text(source,encoding='utf-8',newline='\n')
    (work/'war3map.wts').write_bytes(wts)
    version,count = struct.unpack_from('<II',imports)
    art = sorted((POKER/'src/PokerUI').glob('*.blp'))
    assert len(art) == 60
    artwork = [(f,'PokerUI\\'+f.name) for f in art]+[(f,str(f.relative_to(ROOT/'art')).replace('/','\\')) for f in sorted((ROOT/'art').rglob('*')) if f.is_file()]
    manifest = struct.pack('<II',version,count+len(artwork))+imports[8:]+b''.join(b'\r'+name.encode()+b'\0' for _,name in artwork)
    (work/'war3map.imp').write_bytes(manifest)
    home = Path.home()
    compiler = home/'Documents/Codex/2026-10-28/thi/work/jasshelper/pjass.exe'
    natives = home/'Documents/Codex/2026-10-20/brin/outputs/Google Drive Files/Old PC/Documents/Warcraft III/JassHelper'
    result = subprocess.run([str(compiler),str(natives/'common.j'),str(natives/'Blizzard.j'),str(script)],capture_output=True,text=True)
    (ROOT/'compile.log').write_text(result.stdout+result.stderr,encoding='utf-8')
    assert result.returncode == 0,result.stdout+result.stderr
    restored = source.replace(globals_+'\nendglobals','endglobals',1).replace(module+'\nfunction main','function main',1)
    restored = restored.replace('    call InitCustomTriggers()\n    call PK_Init()\n    call CAS_Init()','    call InitCustomTriggers()',1)
    restored = restored.replace(before_base+base_hook,before_base,1).replace(settle_hook+'    set FGA_settled=true','    set FGA_settled=true',1)
    assert restored == original, 'Unexpected battle-script change'
    OUT.parent.mkdir(exist_ok=True)
    shutil.copy2(BASE,OUT)
    payload = [(f,f.name) for f in sorted(work.glob('*')) if f.is_file()]+artwork
    handle = c.c_void_p()
    assert s.SFileOpenArchive(str(OUT),0,0,c.byref(handle))
    try:
        for file,name in payload:
            assert s.SFileAddFileEx(handle,str(file),name.encode(),0x80000200,2,2),name
    finally:
        s.SFileCloseArchive(handle)
    check = MPQArchive(str(OUT),listfile=False)
    for file,name in payload:
        assert check.read_file(name) == file.read_bytes(),name
    allowed = set()
    for name in ('war3map.j','war3map.imp','war3map.wts','(listfile)','(attributes)','(signature)'):
        e = a.get_hash_table_entry(name)
        if e:
            allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
    before,after = archive_entries(BASE),archive_entries(OUT)
    preserved = 0
    for key,value in before.items():
        if key not in allowed:
            assert after[key] == value,key
            preserved += 1
    report = dict(input=str(BASE),input_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),output=str(OUT),sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),compiler_passed=True,exact_battle_source_restoration=True,verified_payloads=len(payload),preserved_entries=preserved,engine_tested=False)
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2))
    OUT.with_suffix('.sha256').write_text(report['sha256']+'  '+OUT.name+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
