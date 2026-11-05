from pathlib import Path
import sys,re
sys.path.insert(0,str(Path(__file__).parent/'tools'))
import objdata
root=Path(__file__).parent/'base/files'
wts=dict(re.findall(r'STRING (\d+)\s*\{\s*(.*?)\s*\}',(root/'war3map.wts').read_text(encoding='utf-8-sig'),re.S))
def text(v):
 return wts.get(str(int(v[8:])),v) if isinstance(v,str) and v.startswith('TRIGSTR_') else v
for ext in ['w3u','w3q']:
 data=objdata.load(str(root/f'war3map.{ext}'))
 assert objdata.dump(data)==(root/f'war3map.{ext}').read_bytes()
 print('\n',ext)
 for tab in data['tables']:
  for e in tab:
   id=e['newId'] if e['newId']!='\0'*4 else e['oldId']; m={m['id']:text(m['value']) for m in e['mods']}
   if ext=='w3q' or 'useu' in m or id in ['n003','hbar'] or 'R00E' in str(m.get('ureq','')) or ('uupg' in m and m['uupg']):
    print(id,{k:v for k,v in m.items() if k in ['unam','ureq','urqa','uupg','useu','ures','gnam','glvl','gef1','gef2','gef3','gef4']})
