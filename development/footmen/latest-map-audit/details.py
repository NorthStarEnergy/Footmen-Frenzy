from pathlib import Path
import sys,difflib,json
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import functions
f={k:functions((R/k/'war3map.j').read_text(encoding='utf8',errors='replace').replace('\r','')) for k in ['v67','v83','installed_v69','solo']}
for n in ['FFGS_InitSettings','Trig_set_spawn_variables_Actions']:
 print(n)
 print(''.join(difflib.unified_diff(f['v83'][n].splitlines(True),f['installed_v69'][n].splitlines(True),fromfile='v83',tofile='installed_v69'))[:6000])
print('Solo specific functions absent v83:',[n for n in f['solo'] if n.startswith(('SoloCam_','SoloFoots')) and n not in f['v83']])
for d in ['veigar-range-v74','spawn-level-v75','colo-xp-v76','colo-curve-v77','level10-catchup-v78','colo-lag-v79','fed-rewards-v80','veigar-visuals-v81','veigar-stacks-v82','veigar-ultimate-v83']:
 p=W/d/'verification.json'
 if p.exists():
  j=json.loads(p.read_text(encoding='utf-8-sig'));print(d,'base:',j.get('base'), 'changed:',j.get('changed_functions'))

