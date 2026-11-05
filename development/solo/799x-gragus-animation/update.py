from pathlib import Path
import sys,shutil,subprocess,os,json,re
from gragus_animations import patch
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport')
sys.path.insert(0,str(R/'tools'));from mpyq import MPQArchive
base=MPQArchive(str(R/'release/FF799X_Rx_Orianna_v18.w3x'),listfile=False)
assert base.read_file('InfernalGragas.mdx')==(R.parent/'mini-foots/base/files/InfernalGragas.mdx').read_bytes()
s=patch((R/'src/war3map.j').read_text(encoding='utf8')).replace('Orianna v18','Orianna v19');(W/'war3map.j').write_text(s,encoding='utf8')
(W/'war3map.wts').write_bytes((R/'src/war3map.wts').read_bytes().replace(b'Orianna v18',b'Orianna v19'))
for name in ['build.py','Pack-Map.ps1','verify.py','check_gragus.py']:
 t=(R/name).read_text(encoding='utf8').replace('v18','v19')
 if name=='build.py':t=t.replace('s=patch_fortitude(s)','s=patch_fortitude(s)\nfrom gragus_animations import patch as patch_gragus_animations\ns=patch_gragus_animations(s)')
 if name=='check_gragus.py':
  t=t.replace('SetUnitAnimationByIndex=noop','SetUnitAnimationByIndex=lambda u,index:unit.update(animation=index)')
  t=t.replace("check('Fortitude heal starts '+str(rank)","check('X plays drinking animation '+str(rank),unit.get('animation')==12)\n    check('Fortitude heal starts '+str(rank)")
 (W/name).write_text(t,encoding='utf8')
dot=R.parent/'mini-foots/tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';env=dict(os.environ,DOTNET_ROLL_FORWARD='Major');cur=R/'release/FF799X_Rx_Orianna_v18.w3x'
for i,name in enumerate(['war3map.j','war3map.wts','InfernalGragas.mdx']):
 rm=W/f'remove{i}.w3x';out=W/f'add{i}.w3x'
 for args in [['--replace',cur,W/name,name,rm],[rm,W/name,name,out],['--verify',out,name,W/name]]:subprocess.run([str(dot),str(add),*map(str,args)],env=env,check=True)
 cur=out
backup=R/'audit/v18-before-gragus-animations';backup.mkdir(exist_ok=False)
for n in ['build.py','Pack-Map.ps1','verify.py','check_gragus.py','README.md']:shutil.copy2(R/n,backup/n)
for n in ['war3map.j','war3map.wts']:shutil.copy2(R/'src'/n,backup/n);shutil.copy2(W/n,R/'src'/n)
(backup/'InfernalGragas.mdx').write_bytes(base.read_file('InfernalGragas.mdx'))
for n in ['build.py','Pack-Map.ps1','verify.py','check_gragus.py','gragus_animations.py']:shutil.copy2(W/n,R/n)
shutil.copy2(W/'InfernalGragas.mdx',R/'src/InfernalGragas.mdx');shutil.copy2(W/'InfernalGragas.mdx',R/'assets/InfernalGragas.mdx')
for n in ['animate.cjs','drink-preview.gif','drink-final.png']:shutil.copy2(W/n,backup/n)
name='FF799X_Rx_Orianna_v19.w3x';shutil.copy2(cur,R/'release'/name)
for script in ['check_runtime.py','check_debug_heroes.py','check_gragus.py','verify.py']:subprocess.run([sys.executable,str(R/script)],check=True)
pj=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work\jasshelper\pjass.exe');j=Path(r'C:\Users\User\Documents\Codex\2026-10-20\brin\outputs\Google Drive Files\Old PC\Documents\Warcraft III\JassHelper')
subprocess.run([str(pj),str(j/'common.j'),str(j/'Blizzard.j'),str(R/'src/war3map.j')],check=True)
for folder in [Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')]:
 dest=folder/name;assert not dest.exists();shutil.copy2(cur,dest);assert dest.read_bytes()==cur.read_bytes();print('Installed',dest)
readme=(R/'README.md').read_text(encoding='utf8').replace('FF799X_Rx_Orianna_v18.w3x',name).replace('**FF799X - Orianna v18**','**FF799X - Orianna v19**')
readme+='\n\n## v19: Gragus animations\nRetains InfernalGragas geometry, textures and skeleton. Adds Spell Drink index 12 (1.6 seconds): raises barrel, tips head, holds and returns. Restores Spell Slam index 9 to existing 36167-36667 tracks. X uses Drink, Body Slam uses Slam, barrel spells use original Throw index 11. Geometry previews and parser roundtrip checked; compile, 127 Orianna, 18 hiring, 41 Gragus and full archive checks pass. In-game animation transitions remain to be tested.\n'
(R/'README.md').write_text(readme,encoding='utf8')
