from pathlib import Path
import re,sys,shutil,struct,subprocess,os,json
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport');M=R.parent/'mini-foots'
sys.path.insert(0,str(M/'tools'));import objdata
S=W/'src';shutil.copytree(R/'src',S,dirs_exist_ok=True)
shutil.copyfile(M/'power_orb.py',W/'power_orb.py')
ns={};exec((W/'power_orb.py').read_text(encoding='utf8'),ns)
s=ns['apply_power_orb']((S/'war3map.j').read_text(encoding='utf8'))
policy=(M/'hero_policy.py').read_text(encoding='utf8')
start=policy.index('needle="        call SetPlayerTechMaxAllowed')
end=policy.index("s=re.sub(r'function Trig_spawn_killa",start)
policy=policy[:start]+'''init="function MF_InitHeroPolicy takes nothing returns nothing\\n    local integer i = 0\\n    loop\\n        exitwhen i >= 12\\n"+'\\n'.join("        call SetPlayerTechMaxAllowed(Player(i), '"+uid+"', 0)" for uid in sorted(tech_blocked))+"\\n        set i = i + 1\\n    endloop\\nendfunction\\n\\n"
pos=re.search(r'^function ',s,re.M).start();s=s[:pos]+init+s[pos:]
main=re.search(r'^function main takes .*?^endfunction',s,re.M|re.S)[0]
s=s.replace(main,main.replace('endfunction','    call MF_InitHeroPolicy()\\nendfunction'))
'''+policy[end:]
policy=policy.replace('Mini Foots','799X')
(W/'hero_policy.py').write_text(policy,encoding='utf8')
scope=dict(s=s,O=S,R=W,re=re,json=json,objdata=objdata);exec(policy,scope);s=scope['s']
s=s.replace('Orianna v13','Orianna v14');(S/'war3map.j').write_text(s,encoding='utf8')
for n in ['war3map.wts']:(S/n).write_bytes((S/n).read_bytes().replace(b'Orianna v13',b'Orianna v14'))
asset='Spells/Orianna/Feedback/Power_Orb.mdx';shutil.copyfile(M/'src'/asset,S/asset)
imp=(S/'war3map.imp').read_bytes();v,n=struct.unpack_from('<ii',imp);(S/'war3map.imp').write_bytes(struct.pack('<ii',v,n+1)+imp[8:]+b'\r'+asset.replace('/','\\').encode()+b'\0')
for name in ['build.py','Pack-Map.ps1','verify.py','check_runtime.py','check_debug_heroes.py','check_gragus.py']:
 t=(R/name).read_text(encoding='utf8').replace('v13','v14')
 if name=='build.py':
  needle="(OUT / 'war3map.w3u').write_bytes(objdata.dump(units))"
  t=t.replace(needle,needle+"\nfrom power_orb import apply_power_orb\ns=apply_power_orb(s)\nexec((ROOT/'hero_policy.py').read_text(encoding='utf8'),dict(),scope := dict(s=s,O=OUT,R=ROOT,re=re,json=json,objdata=objdata))\ns=scope['s']\n(OUT/'war3map.j').write_text(s,encoding='utf8')")
 if name=='check_runtime.py':
  t=t.replace("effects[orb]['scale']==2.","effects[orb]['scale']==1.").replace("effects[gold]['scale']==2.","effects[gold]['scale']==1.")
  t=t.replace("effects[orb].get('destroyed') and env['OM_Ball'][1]==10", "gold==orb and not effects[orb].get('destroyed') and env['OM_Ball'][1]==10")
  t=t.replace("endswith('DenseOrb.mdx')","endswith('Power_Orb.mdx')").replace("'DenseOrb' in v['model'] and v.get('scale',0)>=2.","'Power_Orb' in v['model'] and v.get('scale',0)>=1.")
  t=t.replace('same Enchantress orb','same Power Orb')
 (W/name).write_text(t,encoding='utf8')
(W/'audit').mkdir(exist_ok=True)
dot=M/'tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';env=dict(os.environ,DOTNET_ROLL_FORWARD='Major')
def run(*args):subprocess.run([str(dot),*map(str,args)],env=env,check=True)
current=R/'release/FF799X_Rx_Orianna_v13.w3x'
for i,name in enumerate(['war3map.j','war3map.wts','war3map.w3u','war3map.imp',asset]):
 internal=name.replace('/','\\');out=W/f'step{i}.w3x'
 if i<4:
  removed=W/f'removed{i}.w3x';run(add,'--replace',current,S/name,internal,removed);current=removed
 run(add,current,S/name,internal,out);run(add,'--verify',out,internal,S/name);current=out
(W/'release').mkdir(exist_ok=True);shutil.copyfile(current,W/'release/FF799X_Rx_Orianna_v14.w3x')
run(W.parent/'tools/bin/JassParseCheck/JassParseCheck.dll',S/'war3map.j')

