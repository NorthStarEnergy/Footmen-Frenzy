from pathlib import Path
import sys,re,json
sys.path.insert(0,'hero-polish')
from archive_helpers import *
for folder in ['tf-orb-v53','ryan-v54-cleanup/source','ryan-v54-cleanup/release','ryan-v56-cleanup/release','mundo-v64/release','taverns-v66/release','pub-xp-v67/release','combined-v68/release']:
 ps=list(Path(folder).rglob('*.w3x'));p=ps[0];h=c.c_void_p();assert storm.SFileOpenArchive(str(p.resolve()),0,0x100,c.byref(h))
 b=read_storm(h,'war3map.wts');print(folder,len(b),'CRCR',b.count(b'\r\r'),'CR',b.count(b'\r'),'LF',b.count(b'\n'),repr(b[:95]))
 if folder=='tf-orb-v53':Path('ui-label-repair/old.wts').write_bytes(b)
 storm.SFileCloseArchive(h)
s=Path('ui-label-repair/war3map.wts').read_text(encoding='utf-8-sig');strings=dict(re.findall(r'STRING (\d+)\s*\{\s*(.*?)\s*\}',s,re.S))
for n in ['war3map.w3t','war3mapSkin.w3t']:
 for t in objdata.load('ui-label-repair/'+n)['tables']:
  for e in t:
   v={m['id']:m['value'] for m in e['mods']};v={k:strings.get(str(int(x[8:])),x) if isinstance(x,str) and x.startswith('TRIGSTR_') else x for k,x in v.items()}
   if 'brew' in str(v).lower():print('BREW',n,e['oldId'],e['newId'],v)
