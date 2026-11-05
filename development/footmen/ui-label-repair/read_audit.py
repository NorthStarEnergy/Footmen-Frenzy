from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'hero-polish')
from archive_helpers import *
paths={'old':list(Path('tf-orb-v53/release').glob('*.w3x'))[0],'current':list(Path('pub-xp-v67/release').glob('*.w3x'))[0]};handles={}
for k,p in paths.items():
 h=c.c_void_p();assert storm.SFileOpenArchive(str(p.resolve()),0,0x100,c.byref(h));handles[k]=h
names=[x['path'] for x in json.loads(Path('size-audit-v50/archive-files.json').read_text())];rows=[];ok=0
for n in names:
 try:b=read_storm(handles['current'],n);ok+=1
 except Exception as ex:
  try:old=read_storm(handles['old'],n);recoverable=True
  except Exception:recoverable=False
  rows.append(dict(path=n,error=str(ex),recoverable=recoverable))
for h in handles.values():storm.SFileCloseArchive(h)
Path('ui-label-repair/read-audit.json').write_text(json.dumps({'readable':ok,'failed':rows},indent=2));print(json.dumps({'readable':ok,'failed':rows},indent=2))
