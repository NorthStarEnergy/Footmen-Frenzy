from pathlib import Path
import sys,re
sys.path.insert(0,'hero-polish')
from archive_helpers import *
R=Path('ui-label-repair');s=re.sub(rb'\r+\n',b'\n',(R/'war3map.wts').read_bytes()).decode('utf-8-sig');strings=dict(re.findall(r'STRING (\d+)[^\{]*\{\n(.*?)\n\}',s,re.S))
for n in ['war3map.w3t','war3mapSkin.w3t']:
 for t in objdata.load(str(R/n))['tables']:
  for e in t:
   v={m['id']:m['value'] for m in e['mods']};v={k:strings.get(str(int(x[8:])),x) if isinstance(x,str) and x.startswith('TRIGSTR_') else x for k,x in v.items()}
   if 'brew' in str(v).lower():print('BREW',n,e['oldId'],e['newId'],v)
print('STRINGS',len(strings))
for k,v in strings.items():
 if v in ['AutoSend:','Swap ends:'] or 'Brew' in v and len(v)<150:print(k,repr(v))
