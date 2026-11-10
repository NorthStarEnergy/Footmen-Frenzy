from pathlib import Path
import shutil,subprocess,os,re,json,hashlib,sys
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport')
W.mkdir(exist_ok=True)
scripts=['power_orb.py','build.py','Pack-Map.ps1','verify.py','check_runtime.py']
for n in scripts:
 s=(R/n).read_text(encoding='utf8').replace('v14','v15')
 if n=='power_orb.py':s=s.replace('local real size = 1.0','local real size = 0.60')
 if n=='check_runtime.py':
  s=s.replace("['scale']==1.","['scale']==0.60").replace("['scale']-1.18","['scale']-0.60*1.18").replace("['scale']-1.)","['scale']-0.60)").replace("v.get('scale',0)>=1.","v.get('scale',0)>=0.60").replace('all(size==1. for size in sizes)','all(size==0.60 for size in sizes)')
 (W/n).write_text(s,encoding='utf8')
s=(R/'src/war3map.j').read_text(encoding='utf8');assert s.count('local real size = 1.0')==1
s=s.replace('local real size = 1.0','local real size = 0.60').replace('Orianna v14','Orianna v15');(W/'war3map.j').write_text(s,encoding='utf8')
(W/'war3map.wts').write_bytes((R/'src/war3map.wts').read_bytes().replace(b'Orianna v14',b'Orianna v15'))
dot=R.parent/'mini-foots/tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';env=dict(os.environ,DOTNET_ROLL_FORWARD='Major')
cur=R/'release/FF799X_Rx_Orianna_v14.w3x'
for i,n in enumerate(['war3map.j','war3map.wts']):
 rm=W/f'remove{i}.w3x';out=W/f'add{i}.w3x'
 for args in [['--replace',cur,W/n,n,rm],[rm,W/n,n,out],['--verify',out,n,W/n]]:subprocess.run([str(dot),str(add),*map(str,args)],env=env,check=True)
 cur=out
shutil.copyfile(cur,W/'FF799X_Rx_Orianna_v15.w3x')
backup=R/'audit/v14-before-smaller-orb';backup.mkdir(exist_ok=False)
for n in scripts+['README.md']:shutil.copy2(R/n,backup/n)
for n in ['war3map.j','war3map.wts']:shutil.copy2(R/'src'/n,backup/n);shutil.copy2(W/n,R/'src'/n)
for n in scripts:shutil.copy2(W/n,R/n)
shutil.copy2(W/'FF799X_Rx_Orianna_v15.w3x',R/'release/FF799X_Rx_Orianna_v15.w3x')
for n in ['check_runtime.py','check_debug_heroes.py','check_gragus.py','verify.py']:subprocess.run([sys.executable,str(R/n)],check=True)
pj=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work\jasshelper\pjass.exe');jass=Path(r'C:\Users\User\Documents\Codex\2026-10-20\brin\outputs\Google Drive Files\Old PC\Documents\Warcraft III\JassHelper')
subprocess.run([str(pj),str(jass/'common.j'),str(jass/'Blizzard.j'),str(R/'src/war3map.j')],check=True)
for folder in [Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')]:
 dest=folder/'FF799X_Rx_Orianna_v15.w3x';assert not dest.exists();shutil.copy2(cur,dest);assert dest.read_bytes()==cur.read_bytes();print('Installed',dest)
s=(R/'README.md').read_text(encoding='utf8').replace('FF799X_Rx_Orianna_v14.w3x','FF799X_Rx_Orianna_v15.w3x').replace('**FF799X - Orianna v14**','**FF799X - Orianna v15**')
s+='\n\n## v15: smaller Power Orb\nThe entire persistent orb effect is scaled to 60% of v14 size, including its surrounding particles and death effect. Gameplay radii remain unchanged. Compilation, lifecycle tests and archive verification pass; in-game appearance awaits testing.\n'
(R/'README.md').write_text(s,encoding='utf8')
