from pathlib import Path
import sys,re,json,io
R=Path(__file__).resolve().parent; W=R.parent
sys.path.insert(0,str(W/'799x-backport/tools'))
sys.path.insert(0,str(W/'mini-foots/tools'))
from mpyq import MPQArchive
import objdata
maps={'donor':W/'799x-backport/release/FF799X_Rx_WC3Icons_v25.w3x','mini':W/'mini-foots/release/Mini Foots v8.w3x','solo':W/'six-player-ffa/release/Solo Foots 6 Player FFA v1.w3x'}
for name,path in maps.items():
 data=path.read_bytes();a=MPQArchive(io.BytesIO(data[512:] if data[:4]==b'HM3W' else data),listfile=False);out=R/name/'base';out.mkdir(parents=True,exist_ok=True)
 for f in ['war3map.j','war3map.w3u','war3map.w3a','war3map.w3h','war3mapSkin.w3u','war3map.imp','war3map.wts','war3map.w3i','war3map.wct','war3map.wtg']:
  if a.get_hash_table_entry(f):(out/f).write_bytes(a.read_file(f))
 s=(out/'war3map.j').read_text(encoding='utf-8-sig')
 fs={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
 print(name,len(fs),'hero funcs',len([n for n in fs if n.startswith(('OM_','FS_','GD_','GFW_','GFB_','GDV_','GDB_'))]))
 print('init',[(n,[x.strip() for x in b.splitlines() if re.search(r'call (OM_|FS_|GD_|GFW_|GFB_)',x)]) for n,b in fs.items() if any('call '+p+'Init(' in b for p in ['OM_','FS_','GD_'])])
 print('hero rows',re.findall(r'.*set udg_hero_\w+\[(?:72|92|93)\].*',s))
 print('globals', '\n'.join(x for x in s[:re.search(r'^endglobals',s,re.M).start()].splitlines() if re.search(r'\b(?:OM|FS|GD|GFW|GFB|GDV|GDB)_',x)))
 if name=='solo':print('Guardian funcs',[n for n in fs if 'Guardian' in n])
