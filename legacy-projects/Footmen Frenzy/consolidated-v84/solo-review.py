from pathlib import Path
import sys,json,re
W=Path.cwd();sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import functions
f={k:functions((W/'latest-map-audit'/k/'war3map.j').read_text(encoding='utf8',errors='replace')) for k in ['solo','v67','v83']}
# Shared functions where Solo diverged while the latest 799X body still matches the common candidate.
names=[n for n,s in f['solo'].items() if n in f['v83'] and f['v83'][n]==f['v67'].get(n) and re.sub(r'\s+','',s)!=re.sub(r'\s+','',f['v83'][n])]
(W/'consolidated-v84/solo-review.json').write_text(json.dumps({'not_a_799x_ancestor':True,'shared_function_differences':names,'scope':'Independent four-player variant; do not substitute its gameplay, slot arithmetic, caps or UI for current 799X.'},indent=2))
print(len(names));print('\n'.join(names))
