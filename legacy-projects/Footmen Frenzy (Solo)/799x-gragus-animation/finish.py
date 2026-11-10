from pathlib import Path
import subprocess,os,sys,shutil
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport')
old='FF799X_Rx_Guardian_v21.w3x';name='FF799X_Rx_Gragus_v22.w3x'
for n in ['build.py','Pack-Map.ps1','verify.py','README.md']:
 p=R/n;s=p.read_text(encoding='utf8').replace(old,name).replace('Guardian v21','Gragus v22');p.write_text(s,encoding='utf8')
for n in ['war3map.j','war3map.wts']:
 p=R/'src'/n;b=p.read_bytes().replace(b'Guardian v21',b'Gragus v22');p.write_bytes(b)
dot=R.parent/'mini-foots/tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';env=dict(os.environ,DOTNET_ROLL_FORWARD='Major');cur=R/'release'/old
for i,n in enumerate(['war3map.j','war3map.wts','InfernalGragas.mdx']):
 rm=W/f'latest-remove{i}.w3x';out=W/f'latest-add{i}.w3x'
 for args in [['--replace',cur,R/'src'/n,n,rm],[rm,R/'src'/n,n,out],['--verify',out,n,R/'src'/n]]:subprocess.run([str(dot),str(add),*map(str,args)],env=env,check=True)
 cur=out
shutil.copy2(cur,R/'release'/name)
for script in ['check_runtime.py','check_debug_heroes.py','check_gragus.py','verify.py']:subprocess.run([sys.executable,str(R/script)],check=True)
pj=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work\jasshelper\pjass.exe');j=Path(r'C:\Users\User\Documents\Codex\2026-10-20\brin\outputs\Google Drive Files\Old PC\Documents\Warcraft III\JassHelper')
subprocess.run([str(pj),str(j/'common.j'),str(j/'Blizzard.j'),str(R/'src/war3map.j')],check=True)
for folder in [Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')]:
 dest=folder/name;assert not dest.exists();shutil.copy2(cur,dest);assert dest.read_bytes()==cur.read_bytes();print('Installed',dest)
p=R/'README.md';s=p.read_text(encoding='utf8');s+='\n\n## v22: Gragus animations, based on Guardian v21\nAdds Spell Drink index 12 (1.6 seconds), restores Spell Slam index 9 (0.5 seconds), and explicitly uses Spell Throw index 11 for barrel spells. Keeps original geometry and textures. Drink is previewed as geometry; live Warcraft transition testing pending. Compiler and regression checks pass. Latest Guardian v21 changes preserved.\n';p.write_text(s,encoding='utf8')
