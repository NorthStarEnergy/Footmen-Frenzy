from pathlib import Path
import shutil,subprocess,os,re,json,hashlib,sys
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport')
W.mkdir(exist_ok=True)
scripts=['power_orb.py','build.py','Pack-Map.ps1','verify.py','check_runtime.py']
for n in scripts:
 s=(R/n).read_text(encoding='utf8').replace('v16','v17')
 if n=='power_orb.py':s=s.replace('    return s',"    s=s.replace("+'    if LoadBoolean(OM_Hash, key, -103) then\n        call BlzSetSpecialEffectColor(fx, 65, 145, 255)\n    else\n        call BlzSetSpecialEffectColor(fx, 255, 255, 255)\n    endif'.__repr__()+", "+'    if LoadBoolean(OM_Hash, key, -103) then\n        call BlzSetSpecialEffectColor(fx, 30, 90, 255)\n    else\n        call BlzSetSpecialEffectColor(fx, 65, 145, 255)\n    endif'.__repr__()+")\n    return s")
 if n=='check_runtime.py':s=s.replace("effects[gold]['color']==(65,145,255)","effects[gold]['color']==(30,90,255)")
 (W/n).write_text(s,encoding='utf8')
s=(R/'src/war3map.j').read_text(encoding='utf8');old='    if LoadBoolean(OM_Hash, key, -103) then\n        call BlzSetSpecialEffectColor(fx, 65, 145, 255)\n    else\n        call BlzSetSpecialEffectColor(fx, 255, 255, 255)\n    endif';assert s.count(old)==1
s=s.replace(old,'    if LoadBoolean(OM_Hash, key, -103) then\n        call BlzSetSpecialEffectColor(fx, 30, 90, 255)\n    else\n        call BlzSetSpecialEffectColor(fx, 65, 145, 255)\n    endif').replace('Orianna v16','Orianna v17');(W/'war3map.j').write_text(s,encoding='utf8')
(W/'war3map.wts').write_bytes((R/'src/war3map.wts').read_bytes().replace(b'Orianna v16',b'Orianna v17'))
dot=R.parent/'mini-foots/tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';env=dict(os.environ,DOTNET_ROLL_FORWARD='Major')
cur=R/'release/FF799X_Rx_Orianna_v16.w3x'
for i,n in enumerate(['war3map.j','war3map.wts']):
 rm=W/f'remove{i}.w3x';out=W/f'add{i}.w3x'
 for args in [['--replace',cur,W/n,n,rm],[rm,W/n,n,out],['--verify',out,n,W/n]]:subprocess.run([str(dot),str(add),*map(str,args)],env=env,check=True)
 cur=out
shutil.copyfile(cur,W/'FF799X_Rx_Orianna_v17.w3x')
backup=R/'audit/v16-before-blue-tint';backup.mkdir(exist_ok=False)
for n in scripts+['README.md']:shutil.copy2(R/n,backup/n)
for n in ['war3map.j','war3map.wts']:shutil.copy2(R/'src'/n,backup/n);shutil.copy2(W/n,R/'src'/n)
for n in scripts:shutil.copy2(W/n,R/n)
shutil.copy2(W/'FF799X_Rx_Orianna_v17.w3x',R/'release/FF799X_Rx_Orianna_v17.w3x')
for n in ['check_runtime.py','check_debug_heroes.py','check_gragus.py','verify.py']:subprocess.run([sys.executable,str(R/n)],check=True)
pj=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work\jasshelper\pjass.exe');jass=Path(r'C:\Users\User\Documents\Codex\2026-10-20\brin\outputs\Google Drive Files\Old PC\Documents\Warcraft III\JassHelper')
subprocess.run([str(pj),str(jass/'common.j'),str(jass/'Blizzard.j'),str(R/'src/war3map.j')],check=True)
for folder in [Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')]:
 dest=folder/'FF799X_Rx_Orianna_v17.w3x';assert not dest.exists();shutil.copy2(cur,dest);assert dest.read_bytes()==cur.read_bytes();print('Installed',dest)
s=(R/'README.md').read_text(encoding='utf8').replace('FF799X_Rx_Orianna_v16.w3x','FF799X_Rx_Orianna_v17.w3x').replace('**FF799X - Orianna v16**','**FF799X - Orianna v17**')
s+='\n\n## v17: softer blue orb\nNormal orb uses the previous Protect tint (65,145,255). Protect now uses a deeper blue (30,90,255). Size and gameplay unchanged. Compilation and regression checks pass; in-game color testing pending.\n'
(R/'README.md').write_text(s,encoding='utf8')
