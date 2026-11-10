import sys,re
from pathlib import Path
sys.path.insert(0,'../Footmen Frenzy/hero-polish')
from archive_helpers import archive,functions
R=Path('solo-v1.8-799x')
paths={'base':Path('C:/Users/User/Documents/Warcraft III/Maps/Solo Foots/GPT/Solo_Foots_v1.8_4P_PRELOAD_TEST07/Solo_Foots_v1.8_4P_PRELOAD_TEST07.w3x'),'donor':Path('../Footmen Frenzy/fed-rewards-v80/release/FF799X_Rx_Fed_Rewards_v80_TEST.w3x')}
for kind,path in paths.items():
 a=archive(path); out=R/kind;out.mkdir(exist_ok=True)
 for name in ['war3map.'+ext for ext in ['j','w3u','w3a','w3h','w3t','w3q','w3b','w3d','wts','w3i','wct','imp']]+['war3mapSkin.w3u']:
  raw=a.read_file(name)
  if raw:(out/name).write_bytes(raw)
 s=(out/'war3map.j').read_text(encoding='cp1252' if kind=='base' else 'utf-8-sig');fs=functions(s)
 print(kind,len(fs),[n for n in fs if n.startswith(('OM_','FS_','GD_'))][-15:])
 print('roster', '\n'.join(x for x in s.splitlines() if 'udg_hero_type[9' in x or 'total_hero_count=' in x))
 print('init', '\n'.join(x for x in s.splitlines() if re.search(r'call (OM_|FS_|GD_|GTW_|FF_|P67_).*Init',x)))

