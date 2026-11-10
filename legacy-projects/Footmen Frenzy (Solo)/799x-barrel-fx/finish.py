from pathlib import Path
import sys,subprocess,os,shutil,re,json,ast
from barrel_fx import patch
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport')
dot=R.parent/'mini-foots/tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';environ=dict(os.environ,DOTNET_ROLL_FORWARD='Major');cur=R/'release/FF799X_Rx_Gragus_v23.w3x'
for i,n in enumerate(['war3map.j','war3map.wts']):
 rm=W/f'retry-remove{i}.w3x';out=W/f'retry-add{i}.w3x'
 for args in [['--replace',cur,R/'src'/n,n,rm],[rm,R/'src'/n,n,out],['--verify',out,n,R/'src'/n]]:subprocess.run([str(dot),str(add),*map(str,args)],env=environ,check=True)
 cur=out
name='FF799X_Rx_Gragus_v24.w3x';shutil.copy2(cur,R/'release'/name)
for n in ['check_runtime.py','check_debug_heroes.py','check_gragus.py','verify.py']:subprocess.run([sys.executable,str(R/n)],check=True)
pj=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work\jasshelper\pjass.exe');j=Path(r'C:\Users\User\Documents\Codex\2026-10-20\brin\outputs\Google Drive Files\Old PC\Documents\Warcraft III\JassHelper')
subprocess.run([str(pj),str(j/'common.j'),str(j/'Blizzard.j'),str(R/'src/war3map.j')],check=True)
for folder in [Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')]:
 dest=folder/name;assert not dest.exists();shutil.copy2(cur,dest);assert dest.read_bytes()==cur.read_bytes();print('Installed',dest)
p=R/'README.md';t=p.read_text(encoding='utf8').replace('Gragus_v23','Gragus_v24').replace('Gragus v23','Gragus v24');t+='\n\n## v24: Barrel presentation\nZ barrel scale 1.15; ultimate barrel scale 1.45 with red tint and additional orange-red impact explosion. Native Pandaren Brewmaster Warcry1 plays as a positional sound on ultimate release and cleans up after playback. Damage, radius and timing unchanged. Compile, mocked presentation and regression checks pass. Live visual/audio testing pending.\n';p.write_text(t,encoding='utf8')
