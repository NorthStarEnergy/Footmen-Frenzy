from pathlib import Path
import sys,json,re
R=Path(__file__).resolve().parent; W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c
import objdata
h=c.c_void_p();assert storm.SFileOpenArchive(str(R/'release/FF799X_Rx_Veigar_Classic_v68.w3x'),0,0x100,c.byref(h))
D=R/'icons';D.mkdir(exist_ok=True)
for ext in ['w3u','w3a','wts']:(D/('war3map.'+ext)).write_bytes(read_storm(h,'war3map.'+ext))
strings=dict(re.findall(r'STRING (\d+)\s*\{\s*(.*?)\s*\}',(D/'war3map.wts').read_text(encoding='utf-8-sig'),re.S))
def resolve(v):return strings.get(v[8:],v) if isinstance(v,str) and v.startswith('TRIGSTR_') else v
for ext in ['w3u','w3a']:
 records=[]
 for table in objdata.load(str(D/('war3map.'+ext)))['tables']:
  for e in table:
   f={m['id']:resolve(m['value']) for m in e['mods'] if m.get('level',0)<=1}
   if re.search('orianna|grag|mundo|guardian|twisted|veigar|demon knight|gul.dan',str(f),re.I):records.append({'id':e['newId'] if e['newId']!='\x00'*4 else e['oldId'],**{k:v for k,v in f.items() if k in ['unam','upro','uico','uhab','uabi','anam','aart','arar']}})
 print(ext,json.dumps(records,indent=2))
assert storm.SFileCloseArchive(h)
