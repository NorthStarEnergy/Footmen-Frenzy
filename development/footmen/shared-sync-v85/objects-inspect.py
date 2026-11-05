from pathlib import Path
import sys,json
W=Path.cwd();sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import *
for label,path in [('solo',Path('C:/Users/User/Documents/Warcraft III/Maps/Solo Foots/Solo Tests/Solo_Foots_v1.8_4P_799X_UPDATE08.w3x')),('799x',W/'consolidated-v84/release/FF799X_Rx_Consolidated_v84_TEST.w3x')]:
 h=c.c_void_p();assert storm.SFileOpenArchive(str(path),0,256,c.byref(h))
 for ext in ['w3u','w3a','w3t']:
  p=W/'shared-sync-v85'/(label+'.'+ext);p.write_bytes(read_storm(h,'war3map.'+ext));d=objdata.load(str(p))
  for tab in d['tables']:
   for e in tab:
    if (e['newId'] if e['newId']!='\0'*4 else e['oldId']) in ['o011','A0IP','A0F1','rat6','I02J','I00V','A0DT','A0HZ']:
     print(label,e['oldId'],e['newId'],[(m['id'],m['value']) for m in e['mods'] if m['id'] in ['uabi','unam','anam','alev','iabi','utip','utub','ides']])
 assert storm.SFileCloseArchive(h)
