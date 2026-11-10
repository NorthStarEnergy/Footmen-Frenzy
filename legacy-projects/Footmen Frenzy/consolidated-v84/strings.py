from pathlib import Path
import sys,re,json
W=Path.cwd();sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import *
def read(p,n):
 h=c.c_void_p();assert storm.SFileOpenArchive(str(p),0,256,c.byref(h));b=read_storm(h,n);storm.SFileCloseArchive(h);return b
p=Path('C:/Users/User/Documents/Warcraft III/Maps/Test/FF799X_Rx_Ghoul_Grunt_Buff_v69.w3x')
w=lambda b:dict(re.findall(r'STRING (\d+)\s*\{\s*\n(.*?)\n\}',b.decode('utf-8-sig',errors='replace').replace('\r',''),re.S))
a=w(read(W/'pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x','war3map.wts'));b=w(read(p,'war3map.wts'))
print([(k,a.get(k),v) for k,v in b.items() if a.get(k)!=v])
