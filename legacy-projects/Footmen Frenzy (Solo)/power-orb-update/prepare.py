from pathlib import Path
import re,shutil,subprocess,os
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots')
asset='Spells/Orianna/Feedback/Power_Orb.mdx'
helper='''# Power Orb by Kitabatake: https://www.hiveworkshop.com/threads/power-orb.48602/
import re,shutil
def apply_power_orb(s):
    s=s.replace(r"Spells\\\\Orianna\\\\Feedback\\\\DenseOrb.mdx",r"Spells\\\\Orianna\\\\Feedback\\\\Power_Orb.mdx",2)
    s=s.replace("    local real size = 2.0", "    local real size = 1.0")
    s=s.replace("        // Native missile death animations must not leave a second orb behind.\\n        call BlzSetSpecialEffectAlpha(fx, 0)\\n        call BlzSetSpecialEffectPosition(fx, 0.0, 0.0, -10000.0)", "        // Power Orb has a finite 1.4-second Death sequence; DestroyEffect plays it here.")
    s=s.replace("    if LoadBoolean(OM_Hash, key, -103) != protect then\\n        call OM_ClearBallVisual(i)\\n    endif", "    // Keep one persistent orb across shield changes; only its tint changes.")
    return s
if 's' in globals():
    s=apply_power_orb(s)
    target=O/'Spells/Orianna/Feedback/Power_Orb.mdx'
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(R/'assets/Power_Orb.mdx',target)
'''
(W/'power_orb.py').write_text(helper,encoding='utf8')
ns={};exec(helper,ns)
s=(R/'src/war3map.j').read_text(encoding='utf8');new=ns['apply_power_orb'](s)
assert new!=s and 'Feedback\\\\Power_Orb.mdx' in new
func=lambda text,n:re.search(r'^function '+n+r' takes .*?^endfunction',text,re.M|re.S)[0]
assert '10000' not in func(new,'OM_ClearBallVisual')
assert 'OM_ClearBallVisual' not in func(new,'OM_BallLook')
assert 'local real size = 1.0' in func(new,'OM_UpdateBallVisual')
S=W/'src';shutil.copytree(R/'src',S,dirs_exist_ok=True)
(S/'war3map.j').write_text(new.replace('Mini Foots v7','Mini Foots v8'),encoding='utf8',newline='\n')
for name in ['war3map.wts','war3map.w3i']:
 b=(S/name).read_bytes();assert b'Mini Foots v7' in b;(S/name).write_bytes(b.replace(b'Mini Foots v7',b'Mini Foots v8'))
(S/asset).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/'asset/Power Orb/Power_Orb.mdx',S/asset)
for name in ['build_source.py','Pack-Map.ps1','verify.py','record_delivery.py','render_audit.py']:
 t=(R/name).read_text(encoding='utf-8-sig').replace('Mini Foots v7','Mini Foots v8')
 if name=='build_source.py':t=t.replace("exec((R/'hero_policy.py').read_text(encoding='utf-8'))","exec((R/'hero_policy.py').read_text(encoding='utf-8'))\nexec((R/'power_orb.py').read_text(encoding='utf-8'))")
 if name=='verify.py':
  t=t.replace("for m in re.finditer(r'^function (OM_", "ns={};exec((R/'power_orb.py').read_text(encoding='utf8'),ns);ds=ns['apply_power_orb'](ds)\nfor m in re.finditer(r'^function (OM_")
 (W/name).write_text(t,encoding='utf8')
dot=R/'tools/dotnet/dotnet.exe';add=W.parent/'tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll';env=dict(os.environ,DOTNET_ROLL_FORWARD='Major')
def run(*args):subprocess.run([str(dot),*map(str,args)],env=env,check=True)
current=R/'release/Mini Foots v7.w3x'
for i,name in enumerate(['war3map.j','war3map.wts','war3map.w3i',asset]):
 internal=name.replace('/','\\');out=W/f'step{i}.w3x'
 if i<3:
  removed=W/f'removed{i}.w3x';run(add,'--replace',current,S/name,internal,removed);current=removed
 run(add,current,S/name,internal,out);run(add,'--verify',out,internal,S/name);current=out
shutil.copyfile(current,W/'Mini Foots v8.w3x')
run(W.parent/'tools/bin/JassParseCheck/JassParseCheck.dll',S/'war3map.j')
run(W.parent/'tools/bin/MpqExtract/MpqExtract.dll',W/'Mini Foots v8.w3x',W/'roundtrip')

