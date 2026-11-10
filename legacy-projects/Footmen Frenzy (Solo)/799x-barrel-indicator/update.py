from pathlib import Path
import sys,shutil,subprocess,os
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport');sys.path.insert(0,str(R.parent/'mini-foots/tools'));import objdata
data=objdata.load(str(R/'src/war3map.w3a'));a=next(e for t in data['tables'] for e in t if e['newId']=='AGr1')
for m in a['mods']:
 if m['id']=='aare':m['value']=260.0
 if m['id']=='Ncl3':m['value']|=2
assert len([m for m in a['mods'] if m['id']=='aare' and m['value']==260.])==6
(W/'war3map.w3a').write_bytes(objdata.dump(data))
(W/'war3map.wts').write_bytes((R/'src/war3map.wts').read_bytes().replace(b'Gragus v22',b'Gragus v23'))
for n in ['build.py','Pack-Map.ps1','verify.py']:
 s=(R/n).read_text(encoding='utf8').replace('Gragus_v22','Gragus_v23').replace('Gragus v22','Gragus v23')
 if n=='build.py':
  needle="(OUT / 'war3map.w3a').write_bytes(objdata.dump(abilities))"
  assert needle in s
  s=s.replace(needle,"# Barrel Roll target cursor matches the scripted 260-unit explosion radius.\nfor table in abilities['tables']:\n    for entry in table:\n        if entry['newId']=='AGr1':\n            for mod in entry['mods']:\n                if mod['id']=='aare':mod['value']=260.0\n                if mod['id']=='Ncl3':mod['value'] |= 2\n"+needle)
 if n=='verify.py':s=s.replace("'AGf1','AGr2',","'AGf1','AGr1','AGr2',").replace("'AGr2':{'Ncl6'}","'AGr1':{'aare','Ncl3'},'AGr2':{'Ncl6'}")
 (W/n).write_text(s,encoding='utf8')
dot=R.parent/'mini-foots/tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';env=dict(os.environ,DOTNET_ROLL_FORWARD='Major');cur=R/'release/FF799X_Rx_Gragus_v22.w3x'
for i,n in enumerate(['war3map.w3a','war3map.wts']):
 rm=W/f'remove{i}.w3x';out=W/f'add{i}.w3x'
 for args in [['--replace',cur,W/n,n,rm],[rm,W/n,n,out],['--verify',out,n,W/n]]:subprocess.run([str(dot),str(add),*map(str,args)],env=env,check=True)
 cur=out
backup=R/'audit/v22-before-barrel-indicator';backup.mkdir(exist_ok=False)
for n in ['build.py','Pack-Map.ps1','verify.py']:shutil.copy2(R/n,backup/n);shutil.copy2(W/n,R/n)
for n in ['war3map.w3a','war3map.wts']:shutil.copy2(R/'src'/n,backup/n);shutil.copy2(W/n,R/'src'/n)
name='FF799X_Rx_Gragus_v23.w3x';shutil.copy2(cur,R/'release'/name)
subprocess.run([sys.executable,str(R/'verify.py')],check=True)
for folder in [Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')]:
 dest=folder/name;assert not dest.exists();shutil.copy2(cur,dest);assert dest.read_bytes()==cur.read_bytes();print('Installed',dest)
p=R/'README.md';s=p.read_text(encoding='utf8').replace('Gragus_v22','Gragus_v23').replace('Gragus v22','Gragus v23');s+='\n\n## v23: Barrel Roll targeting circle\nEnables Channel targeting image on AGr1 and sets its radius to 260 at every rank, matching both automatic and manual explosion damage searches. Gameplay values unchanged. Archive validation passes; in-game cursor appearance pending.\n';p.write_text(s,encoding='utf8')
