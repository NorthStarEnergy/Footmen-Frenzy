from pathlib import Path
import sys, ctypes as c, shutil, re, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'make_art.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'test_ui.py')],check=True)
sys.path.insert(0,str(ROOT.parent/'six-player-ffa'))
from archive import s
BASE=ROOT.parent/'799x-backport/release/FF799X_Rx_Orianna_v4.w3x'
OUT=ROOT/'release/FF799X_Observer_Poker_v2.w3x'
def read(handle,name):
    f=c.c_void_p()
    assert s.SFileOpenFileEx(handle,name.encode(),0,c.byref(f)),name
    data=c.create_string_buffer(s.SFileGetFileSize(f,None));count=c.c_uint()
    assert s.SFileReadFile(f,data,len(data),c.byref(count),None)
    s.SFileCloseFile(f)
    return data.raw
def opened(path):
    h=c.c_void_p();assert s.SFileOpenArchive(str(path),0,0,c.byref(h));return h
h=opened(BASE)
source=read(h,'war3map.j').decode('utf-8-sig')
strings=read(h,'war3map.wts')
imports=read(h,'war3map.imp')
s.SFileCloseArchive(h)
(ROOT/'baseline.j').write_text(source,encoding='utf-8')
globals_=(ROOT/'poker-globals.j').read_text()
module=(ROOT/'poker.j').read_text()
ui=(ROOT/'ui.j').read_text()
ui_functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',ui)}
helpers='\n\n'.join(ui_functions[n] for n in ['PK_Texture','PK_Label','PK_ChipArt'])+'\n\n'
for name in ['PK_Render','PK_Start']:
    match=re.search(r'(?ms)^function '+name+r'\b.*?^endfunction',module)
    assert match
    module=module[:match.start()]+ui_functions[name]+module[match.end():]
module=module.replace('function PK_Render takes',helpers+'function PK_Render takes',1)
module=module.replace('BlzFrameSetSize(f,width,0.035)','BlzFrameSetSize(f,width,0.029)')
patched=source.replace('\nendglobals','\n'+globals_+'\nendglobals',1)
assert patched!=source
patched=patched.replace('function main takes nothing returns nothing',module+'\nfunction main takes nothing returns nothing',1)
hook='    call PK_DetectSolo()\n    if not PK_Solo then\n        call InitCustomTriggers()\n    endif\n    call PK_Init()'
assert patched.count('    call InitCustomTriggers()')==1
patched=patched.replace('    call InitCustomTriggers()',hook,1)
# Exact source restoration proves the integrated multiplayer battle code is untouched.
restored=patched.replace(globals_+'\nendglobals','endglobals',1).replace(module+'\nfunction main','function main',1).replace(hook,'    call InitCustomTriggers()',1)
assert restored==source
(ROOT/'src/war3map.j').write_text(patched,encoding='utf-8',newline='\n')
assert b'FF799X - Orianna v4' in strings
(ROOT/'src/war3map.wts').write_bytes(strings.replace(b'FF799X - Orianna v4',b'FF799X - Observer Poker v2'))
import struct
version,count=struct.unpack_from('<II',imports)
artfiles=sorted((ROOT/'src/PokerUI').glob('*.blp'))
assert len(artfiles)==60
paths=['PokerUI\\'+f.name for f in artfiles]
(ROOT/'src/war3map.imp').write_bytes(struct.pack('<II',version,count+len(paths))+imports[8:]+b''.join(b'\r'+p.encode()+b'\0' for p in paths))
home=Path.home()
jass=home/'Documents/Codex/2026-10-20/brin/outputs/Google Drive Files/Old PC/Documents/Warcraft III/JassHelper'
compiler=home/'Documents/Codex/2026-10-28/thi/work/jasshelper/pjass.exe'
result=subprocess.run([str(compiler),str(jass/'common.j'),str(jass/'Blizzard.j'),str(ROOT/'src/war3map.j')],capture_output=True,text=True)
(ROOT/'compile.log').write_text(result.stdout+result.stderr)
print((result.stdout+result.stderr)[:6000])
assert result.returncode==0,'pjass failed'
dotnet=ROOT.parent/'mini-foots/tools/dotnet/dotnet.exe'
packer=home/'Documents/ChatGPT/Footmen Frenzy (Solo)/tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll'
import os,uuid
environment=dict(os.environ,DOTNET_ROLL_FORWARD='Major')
stage=ROOT/('stage-'+uuid.uuid4().hex);stage.mkdir()
current=BASE
payloads=sorted(f for f in (ROOT/'src').rglob('*') if f.is_file())
for i,file in enumerate(payloads):
    internal=str(file.relative_to(ROOT/'src')).replace('/','\\')
    removed=stage/f'{i}-removed.w3x';added=stage/f'{i}-added.w3x'
    commands=[]
    inputmap=current
    if file.parent==ROOT/'src':
        commands.append(['--replace',str(current),str(file),internal,str(removed)])
        inputmap=removed
    commands += [[str(inputmap),str(file),internal,str(added)],['--verify',str(added),internal,str(file)]]
    for args in commands:
        result=subprocess.run([str(dotnet),str(packer),*args],env=environment,capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
    # Only discard explicitly created intermediate files inside this build's stage.
    for old in [removed,current]:
        if old.parent==stage and old.exists():old.unlink()
    current=added
shutil.copy2(current,OUT)
h=opened(OUT)
for file in payloads:assert read(h,str(file.relative_to(ROOT/'src')).replace('/','\\'))==file.read_bytes()
s.SFileCloseArchive(h)
# Verify all inherited entries, including files omitted from the listfile.
sys.path.insert(0,str(ROOT.parent/'799x-backport/tools'))
from mpyq import MPQArchive
def entries(path):
    archive=MPQArchive(str(path),listfile=False);result={}
    for entry in archive.hash_table:
        if entry.block_table_index>=len(archive.block_table):continue
        archive.get_hash_table_entry=lambda _,entry=entry:entry
        key=(entry.hash_a,entry.hash_b,entry.locale,entry.platform)
        try:result[key]=archive.read_file('ignored')
        except (RuntimeError,NotImplementedError):
            block=archive.block_table[entry.block_table_index]
            archive.file.seek(block.offset+archive.header['offset'])
            result[key]=(block.flags,block.size,archive.file.read(block.archived_size))
    return result
a=MPQArchive(str(BASE),listfile=False)
allowed=set()
for name in ['war3map.j','war3map.wts','war3map.imp','(listfile)','(attributes)','(signature)']:
    e=a.get_hash_table_entry(name)
    if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
before,after=entries(BASE),entries(OUT)
preserved=0
for key,value in before.items():
    if key not in allowed:
        assert after[key]==value,key
        preserved+=1
report=dict(baseline=str(BASE),baseline_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),output=str(OUT),sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),preserved_entries=preserved,art_textures=len(artfiles),pjass=True,script_scope=True,roundtrip=True,engine_tested=False)
(ROOT/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
