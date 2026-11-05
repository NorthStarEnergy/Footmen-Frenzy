import sys
from pathlib import Path
w=Path.cwd();sys.path.insert(0,str(w/'hero-polish'))
from archive_helpers import storm,read_storm,c,objdata
base=w/'combined-v68/release/FF799X_Rx_Veigar_Classic_v68.w3x';h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for n in ['war3map.w3a','war3map.w3u']:
 p=w/'mundo-health-kit'/n;p.write_bytes(read_storm(h,n));d=objdata.load(str(p))
 for table in d['tables']:
  for e in table:
   if e['newId'] in ['HMu1','AMu2','AMur','Aamk'] or e['oldId']=='Aamk':print(n,e)
storm.SFileCloseArchive(h)
