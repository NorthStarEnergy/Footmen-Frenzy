from pathlib import Path
import sys,shutil,re,json,subprocess,os
from fortitude import patch,objects
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport')
sys.path.insert(0,str(R.parent/'mini-foots/tools'));import objdata
s=patch((R/'src/war3map.j').read_text(encoding='utf8')).replace('Orianna v17','Orianna v18');(W/'war3map.j').write_text(s,encoding='utf8')
(W/'war3map.w3a').write_bytes(objdata.dump(objects(objdata.load(str(R/'src/war3map.w3a')))))
(W/'war3map.wts').write_bytes((R/'src/war3map.wts').read_bytes().replace(b'Orianna v17',b'Orianna v18'))
for name in ['build.py','Pack-Map.ps1','verify.py']:
 t=(R/name).read_text(encoding='utf8').replace('v17','v18')
 if name=='build.py':
  needle="(OUT / 'war3map.w3a').write_bytes(objdata.dump(abilities))"
  assert needle in t;t=t.replace(needle,"from fortitude import patch as patch_fortitude, objects as fortitude_objects\ns=patch_fortitude(s)\n(OUT/'war3map.j').write_text(s,encoding='utf8')\nabilities=fortitude_objects(abilities)\n"+needle)
 if name=='verify.py':t=t.replace("'AGf1','AGr2'}","'AGf1','AGr2','GF01','GF02','GF03','GF04','GF05','GF06','GFbf'}")
 (W/name).write_text(t,encoding='utf8')
manifest=json.loads((R/'manifest.json').read_text());f=lambda x:{m[1]:m[0] for m in re.finditer(r'^function (\w+) takes .*?^endfunction',x,re.M|re.S)}
b=f((R.parent/'mini-foots/base/files/war3map.j').read_text(encoding='utf-8-sig'));n=f(s);manifest['changed_functions']=[k for k in b if b[k]!=n[k]];manifest['added_functions']=sorted(set(n)-set(b));(W/'manifest.json').write_text(json.dumps(manifest,indent=2))
dot=R.parent/'mini-foots/tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';env=dict(os.environ,DOTNET_ROLL_FORWARD='Major');cur=R/'release/FF799X_Rx_Orianna_v17.w3x'
for i,name in enumerate(['war3map.j','war3map.w3a','war3map.wts']):
 rm=W/f'remove{i}.w3x';out=W/f'add{i}.w3x'
 for args in [['--replace',cur,W/name,name,rm],[rm,W/name,name,out],['--verify',out,name,W/name]]:subprocess.run([str(dot),str(add),*map(str,args)],env=env,check=True)
 cur=out
backup=R/'audit/v17-before-fortitude-rebuild';backup.mkdir(exist_ok=False)
scripts=['build.py','Pack-Map.ps1','verify.py','check_gragus.py','manifest.json']
for name in scripts:shutil.copy2(R/name,backup/name);shutil.copy2(W/name,R/name)
for name in ['war3map.j','war3map.w3a','war3map.wts']:shutil.copy2(R/'src'/name,backup/name);shutil.copy2(W/name,R/'src'/name)
shutil.copy2(W/'fortitude.py',R/'fortitude.py')
name='FF799X_Rx_Orianna_v18.w3x';shutil.copy2(cur,R/'release'/name)
for script in ['check_runtime.py','check_debug_heroes.py','check_gragus.py','verify.py']:subprocess.run([sys.executable,str(R/script)],check=True)
pj=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work\jasshelper\pjass.exe');j=Path(r'C:\Users\User\Documents\Codex\2026-10-20\brin\outputs\Google Drive Files\Old PC\Documents\Warcraft III\JassHelper')
subprocess.run([str(pj),str(j/'common.j'),str(j/'Blizzard.j'),str(R/'src/war3map.j')],check=True)
for folder in [Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')]:
 dest=folder/name;assert not dest.exists();shutil.copy2(cur,dest);assert dest.read_bytes()==cur.read_bytes();print('Installed',dest)
readme=(R/'README.md').read_text(encoding='utf8').replace('FF799X_Rx_Orianna_v17.w3x',name).replace('**FF799X - Orianna v17**','**FF799X - Orianna v18**')
readme+='\n\n## v18: Fortitude rebuild\nReplaces the self-only Devotion Aura with six fixed-rank item armor modifiers (+5/7/9/11/13/15). Correct-rank targeted cosmetic Inner Fire buff is cast after setting its level, with no additional armor/damage/regeneration. Recast, expiry, death and removal clear modifiers. Healing and magic reduction retain five-second duration. Compiler and mocked checks pass; actual engine armor/buff behavior still requires live testing.\n'
(R/'README.md').write_text(readme,encoding='utf8')
