from pathlib import Path
import sys,subprocess,os,shutil,re,json,ast
from barrel_fx import patch
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport')
s=patch((R/'src/war3map.j').read_text(encoding='utf8'));(W/'war3map.j').write_text(s,encoding='utf8')
(W/'war3map.wts').write_bytes((R/'src/war3map.wts').read_bytes().replace(b'Gragus v23',b'Gragus v24'))
for n in ['build.py','Pack-Map.ps1','verify.py']:
 t=(R/n).read_text(encoding='utf8').replace('Gragus_v23','Gragus_v24').replace('Gragus v23','Gragus v24')
 if n=='build.py':t=t.replace('s=patch_gragus_animations(s)','s=patch_gragus_animations(s)\nfrom barrel_fx import patch as patch_barrel_fx\ns=patch_barrel_fx(s)')
 (W/n).write_text(t,encoding='utf8')
funcs=lambda text:{m[1]:m[0] for m in re.finditer(r'^function (\w+) takes .*?^endfunction',text,re.M|re.S)}
old=funcs((R.parent/'mini-foots/base/files/war3map.j').read_text(encoding='utf-8-sig'));new=funcs(s);manifest=json.loads((R/'manifest.json').read_text());manifest['changed_functions']=[n for n in old if old[n]!=new[n]];manifest['added_functions']=sorted(set(new)-set(old));(W/'manifest.json').write_text(json.dumps(manifest,indent=2))
# Execute the new presentation handlers with engine calls recorded.
tree=ast.parse((R/'check_runtime.py').read_text());ns={'re':re,'functions':new};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('expression','translate')],type_ignores=[]),'translator','exec'),ns)
env={};exec('\n\n'.join(ns['translate'](n) for n in ['FS_BarrelPresentation','FS_UltimateBurst']),env)
calls=[]
for name in ['BlzSetSpecialEffectScale','BlzSetSpecialEffectColor','SetSoundDuration','SetSoundChannel','SetSoundVolume','SetSoundDistances','SetSoundDistanceCutoff','AttachSoundToUnit','StartSound','KillSoundWhenDone','DestroyEffect']:
 env[name]=lambda *args,name=name:calls.append((name,args))
env.update(CreateSound=lambda *a:99,GetSoundFileDuration=lambda p:1600,AddSpecialEffect=lambda *a:88)
env['FS_BarrelPresentation'](1,2,False);assert calls==[('BlzSetSpecialEffectScale',(1,1.15))]
calls.clear();env['FS_BarrelPresentation'](1,2,True);assert ('BlzSetSpecialEffectColor',(1,255,55,35)) in calls and ('StartSound',(99,)) in calls and ('KillSoundWhenDone',(99,)) in calls
env['FS_UltimateBurst'](0,0);assert ('DestroyEffect',(88,)) in calls
dot=R.parent/'mini-foots/tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';environ=dict(os.environ,DOTNET_ROLL_FORWARD='Major');cur=R/'release/FF799X_Rx_Gragus_v23.w3x'
for i,n in enumerate(['war3map.j','war3map.wts']):
 rm=W/f'remove{i}.w3x';out=W/f'add{i}.w3x'
 for args in [['--replace',cur,W/n,n,rm],[rm,W/n,n,out],['--verify',out,n,W/n]]:subprocess.run([str(dot),str(add),*map(str,args)],env=environ,check=True)
 cur=out
backup=R/'audit/v23-before-barrel-fx';backup.mkdir(exist_ok=False)
for n in ['build.py','Pack-Map.ps1','verify.py','manifest.json']:shutil.copy2(R/n,backup/n);shutil.copy2(W/n,R/n)
for n in ['war3map.j','war3map.wts']:shutil.copy2(R/'src'/n,backup/n);shutil.copy2(W/n,R/'src'/n)
shutil.copy2(W/'barrel_fx.py',R/'barrel_fx.py');name='FF799X_Rx_Gragus_v24.w3x';shutil.copy2(cur,R/'release'/name)
for n in ['check_runtime.py','check_debug_heroes.py','check_gragus.py','verify.py']:subprocess.run([sys.executable,str(R/n)],check=True)
pj=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work\jasshelper\pjass.exe');j=Path(r'C:\Users\User\Documents\Codex\2026-10-20\brin\outputs\Google Drive Files\Old PC\Documents\Warcraft III\JassHelper')
subprocess.run([str(pj),str(j/'common.j'),str(j/'Blizzard.j'),str(R/'src/war3map.j')],check=True)
for folder in [Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test'),Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test')]:
 dest=folder/name;assert not dest.exists();shutil.copy2(cur,dest);assert dest.read_bytes()==cur.read_bytes();print('Installed',dest)
p=R/'README.md';t=p.read_text(encoding='utf8').replace('Gragus_v23','Gragus_v24').replace('Gragus v23','Gragus v24');t+='\n\n## v24: Barrel presentation\nZ barrel scale 1.15; ultimate barrel scale 1.45 with red tint and additional orange-red impact explosion. Native Pandaren Brewmaster Warcry1 plays as a positional sound on ultimate release and cleans up after playback. Damage, radius and timing unchanged. Compile, mocked presentation and regression checks pass. Live visual/audio testing pending.\n';p.write_text(t,encoding='utf8')
