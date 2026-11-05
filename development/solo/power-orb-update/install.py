from pathlib import Path
import shutil,json,hashlib,subprocess,sys
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots')
backup=R/'archive/v7-before-power-orb';backup.mkdir(exist_ok=False)
names=['build_source.py','Pack-Map.ps1','verify.py','record_delivery.py','render_audit.py','changes.json','README.md','last-build.txt','verification.json']
for name in names:shutil.copy2(R/name,backup/name)
shutil.copytree(R/'src',backup/'src')
for name in names[:5]+['power_orb.py']:shutil.copy2(W/name,R/name)
for name in ['war3map.j','war3map.wts','war3map.w3i','Spells/Orianna/Feedback/Power_Orb.mdx']:
 target=R/'src'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/'src'/name,target)
(R/'assets').mkdir(exist_ok=True)
shutil.copy2(W/'asset/Power Orb/Power_Orb.mdx',R/'assets/Power_Orb.mdx')
shutil.copy2(W/'asset/Power Orb/readme.html',R/'assets/Power_Orb-credit.html')
data=json.loads((R/'changes.json').read_text(encoding='utf-8-sig'));data['name']='Mini Foots v8'
data['orb']='Power Orb by Kitabatake, https://www.hiveworkshop.com/threads/power-orb.48602/'
(R/'changes.json').write_text(json.dumps(data,indent=2),encoding='utf8')
readme=(R/'README.md').read_text(encoding='utf-8-sig').replace('Current release: Mini Foots v7.','Current release: Mini Foots v8.')
readme+='\n\n### Mini Foots v8 - Power Orb\nOrianna uses Power Orb by Kitabatake (https://www.hiveworkshop.com/threads/power-orb.48602/). Original model preserved, looping Stand and non-looping 1.4-second Death. Shield state reuses the same effect; actual cleanup plays Death. Latest v7 gameplay, towers and hero restrictions preserved. Script parsing and 653 regression checks pass. Live Warcraft visual testing pending.\n'
(R/'README.md').write_text(readme,encoding='utf8')
build=R/'build-v8-power-orb';shutil.copytree(W/'roundtrip',build/'roundtrip')
(R/'last-build.txt').write_text(str(build),encoding='utf8')
shutil.copy2(W/'verification.json',R/'verification.json')
expected=hashlib.sha256((W/'Mini Foots v8.w3x').read_bytes()).hexdigest()
for folder in [R/'release',Path(r'C:\Users\User\Documents\Warcraft III\Maps\Mini Foots'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Mini Foots')]:
 dest=folder/'Mini Foots v8.w3x';assert not dest.exists(),dest
 shutil.copy2(W/'Mini Foots v8.w3x',dest)
 assert hashlib.sha256(dest.read_bytes()).hexdigest()==expected
 print('Installed',dest)
subprocess.run([sys.executable,str(R/'verify.py')],check=True)
subprocess.run([sys.executable,str(R/'record_delivery.py')],check=True)
