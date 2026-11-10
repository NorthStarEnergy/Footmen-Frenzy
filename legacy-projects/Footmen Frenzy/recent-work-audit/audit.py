from pathlib import Path
import sys,re,json,hashlib
sys.path.insert(0,'hero-polish')
from archive_helpers import storm,c,read_storm,functions
root=Path(r'\\10.0.0.106\Users\Ryan1\Documents\Footmen Frenzy Development\outputs')
paths=[]
for n in ['v54-ui-startup','veigar-pentagon-v56','veigar-cage-v57','veigar-darkmatter-v58','orianna-effects-v59','hero-tooltips-v60','mode-debug-v61','pool-cap-v62','item-tooltips-v63']:
 paths+=list((root/n).glob('*.w3x'))
for n in ['tf-orb-v53','ryan-v56-cleanup','mundo-v64','hero-hiring-v65','taverns-v66','pub-xp-v67']:paths+=list(Path(n,'release').glob('*.w3x'))
def read(p):
 h=c.c_void_p();assert storm.SFileOpenArchive(str(p.resolve()),0,0x100,c.byref(h))
 data={n:read_storm(h,n) for n in ['war3map.j','war3map.wct','war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3mapSkin.w3a','war3map.w3t','war3mapSkin.w3t']};storm.SFileCloseArchive(h)
 return data
current=read(Path('pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x'));cf=functions(current['war3map.j'].decode('latin1').replace('\r',''))
rows=[]
for p in paths:
 data=read(p);fs=functions(data['war3map.j'].decode('latin1').replace('\r',''))
 missing=sorted(set(fs)-set(cf));changed=[n for n in fs if n in cf and fs[n]!=cf[n]]
 row=dict(map=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),missing_functions=missing,changed_functions=changed,identical_functions=sum(cf.get(n)==b for n,b in fs.items()),identical_object_files=[n for n in data if n.endswith(('.w3u','.w3a','.w3t')) and data[n]==current[n]])
 rows.append(row);print(p.name,'missing',len(missing),'changed',len(changed),'same_objects',len(row['identical_object_files']))
 if missing:print('MISSING',missing[:35])
for p in [Path('taverns-v66/release/FF799X_Rx_Team_Taverns_v66.w3x'),Path('pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x')]:
 d=read(p);s=d['war3map.j'].decode('latin1');print('CASINO SCAN',p.name,re.findall(r'(?m)^function ((?:CAS_|PK_|BJ_|MK_|DU_|ObsCasino|ObsDraft)\w*) takes',s))
Path('recent-work-audit/comparison.json').write_text(json.dumps(rows,indent=2))
