import sys,struct,re
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'hero-polish'))
from archive_helpers import storm,read_storm,c,functions
h=c.c_void_p();assert storm.SFileOpenArchive(str(R.parent/'ryan-v54-cleanup/release/FF799X_Rx_UI_Startup_Clean_v55.w3x'),0,0x100,c.byref(h))
b=read_storm(h,'war3map.wct');storm.SFileCloseArchive(h);(R/'original.wct').write_bytes(b)
print('WCT prefix',repr(b[:200]));pos=b.index(0,8)+1;n=struct.unpack_from('<I',b,pos)[0];s=b[pos+4:pos+4+n].rstrip(b'\0').decode('latin1');(R/'editor-original.j').write_bytes(s.encode('latin1'));print('header',n,'tail',repr(b[pos+4+n:][:1400]));print('functions',len(functions(s)));print(s[:600]);print(s[-1400:])
