from pathlib import Path
import sys,re
W=Path.cwd();sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import objdata,storm,read_storm,c
for label in ['solo','799x']:
 d=objdata.load(str(W/'shared-sync-v85'/(label+'.w3t')))
 for tab in d['tables']:
  for e in tab:
   if e['newId']=='I009':print(label,e)
