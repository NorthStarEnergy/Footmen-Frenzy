import sys,json
from pathlib import Path
sys.path.insert(0,'mini-foots/tools')
from game_data import game_read,ini,slk
for file in ['units\\unitskin.txt','units\\unitui.slk']:
 raw=game_read('war3.w3mod:'+file)
 data=ini(raw) if file.endswith('.txt') else slk(raw)
 print(file,{k:v for k,v in data.items() if 'gul' in str(v).lower()})
