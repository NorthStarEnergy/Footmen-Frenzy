from pathlib import Path
import sys,json,re
sys.path.insert(0,'hero-polish')
from archive_helpers import *
R=Path('ui-label-repair');p=Path('pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x')
h=c.c_void_p();assert storm.SFileOpenArchive(str(p.resolve()),0,0x100,c.byref(h))
names=[x['path'] for x in json.loads(Path('size-audit-v50/archive-files.json').read_text())]
for n in names:
 if n.lower().endswith(('.fdf','.toc')) or 'skin.txt' in n.lower():
  b=read_storm(h,n);print('\nFILE',n,'\n',b.decode('latin1')[:18000]);(R/n.replace('\\','_')).write_bytes(b)
for n in ['war3map.w3t','war3mapSkin.w3t','war3map.wts','war3map.j']:(R/n).write_bytes(read_storm(h,n))
storm.SFileCloseArchive(h)
wts=(R/'war3map.wts').read_text(encoding='utf-8-sig');strings=dict(re.findall(r'STRING (\d+)\s*\{\s*(.*?)\s*\}',wts,re.S))
for n in ['war3map.w3t','war3mapSkin.w3t']:
 for t in objdata.load(str(R/n))['tables']:
  for e in t:
   vals={m['id']:m['value'] for m in e['mods']}
   resolved={k:strings.get(v[8:],v) if isinstance(v,str) and v.startswith('TRIGSTR_') else v for k,v in vals.items()}
   if 'brew' in str(resolved).lower():print('BREW',n,e['oldId'],e['newId'],resolved)

