from pathlib import Path
import shutil,hashlib,subprocess,sys
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport')
backup=R/'audit/v13-before-power-orb';backup.mkdir(exist_ok=False)
names=['build.py','Pack-Map.ps1','verify.py','check_runtime.py','check_debug_heroes.py','check_gragus.py','manifest.json','README.md']
for n in names:shutil.copy2(R/n,backup/n)
shutil.copytree(R/'src',backup/'src')
for n in names[:-1]+['power_orb.py','hero_policy.py','hero-policy.json']:shutil.copy2(W/n,R/n)
for n in ['war3map.j','war3map.wts','war3map.w3u','war3map.imp','Spells/Orianna/Feedback/Power_Orb.mdx']:
 dest=R/'src'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/'src'/n,dest)
asset=R/'assets/Spells/Orianna/Feedback/Power_Orb.mdx';asset.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/'src/Spells/Orianna/Feedback/Power_Orb.mdx',asset)
name='FF799X_Rx_Orianna_v14.w3x';expected=hashlib.sha256((W/'release'/name).read_bytes()).hexdigest()
shutil.copy2(W/'release'/name,R/'release'/name)
for script in ['check_runtime.py','check_debug_heroes.py','check_gragus.py','verify.py']:subprocess.run([sys.executable,str(R/script)],check=True)
for folder in [Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')]:
 dest=folder/name;assert not dest.exists();shutil.copy2(W/'release'/name,dest);assert hashlib.sha256(dest.read_bytes()).hexdigest()==expected;print('Installed',dest)
readme=(R/'README.md').read_text(encoding='utf8');readme=readme.replace('FF799X_Rx_Orianna_v13.w3x','FF799X_Rx_Orianna_v14.w3x').replace('**FF799X - Orianna v13**','**FF799X - Orianna v14**')
readme+='\n\n## Current v14 working base\nPower Orb by Kitabatake: https://www.hiveworkshop.com/threads/power-orb.48602/ . Persistent Stand animation, finite Death cleanup, and no recreation on Protect tint changes. Test heroes disabled except Orianna and Gragus. Preserves the 799X layout, latest hero/UI/zoom code, and current working item data. JASS compilation, 127 spell lifecycle checks, 18 recruitment checks, 35 Gragus checks and full archive verification passed. Live game testing pending.\n'
(R/'README.md').write_text(readme,encoding='utf8')
