from pathlib import Path
import zipfile,struct,sys,json
r=Path(__file__).resolve().parent
z=zipfile.ZipFile(r/'assets/Guldan.zip')
print(z.namelist())
for n in z.namelist():
 if n.lower().endswith(('.mdx','.blp','.txt')):(r/'assets'/Path(n).name).write_bytes(z.read(n))
sys.path[:0]=['mini-foots/tools','hero-polish']
from game_data import chunks
for p in (r/'assets').glob('*.mdx'):
 ch=chunks(p.read_bytes());seq=ch['SEQS'];print(p.name)
 for i in range(0,len(seq),132):print(i//132,seq[i:i+80].split(b'\0')[0].decode(),struct.unpack_from('<II',seq,i+80))
 print('textures',[(ch['TEXS'][i+4:i+264].split(b'\0')[0].decode()) for i in range(0,len(ch['TEXS']),268)])
 print('camera',len(ch.get('CAMS',b'')))
from archive_helpers import storm,read_storm,c
import objdata
h=c.c_void_p();assert storm.SFileOpenArchive(str(Path('799x-backport/release/FF799X_Rx_RequiemFix_v33.w3x').resolve()),0,0x100,c.byref(h))
(r/'src').mkdir(exist_ok=True)
for name in ['war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3map.j','war3map.wts','war3map.imp']:
 raw=read_storm(h,name);(r/'src'/name).write_bytes(raw)
 if name.endswith('w3u'):
  print(name,[e for t in objdata.load(str(r/'src'/name))['tables'] for e in t if e['newId']=='HOr1'])
storm.SFileCloseArchive(h)
