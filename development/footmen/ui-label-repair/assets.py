from pathlib import Path
import sys,json,re
sys.path[:0]=['hero-polish','mini-foots/tools']
from archive_helpers import *
from game_data import game_read
names=[x['path'] for x in json.loads(Path('size-audit-v50/archive-files.json').read_text())]
p=Path('pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x');a=archive(p)
for path in [r'ReplaceableTextures\CommandButtons\BTNEnergyPotion.blp',r'ReplaceableTextures\CommandButtonsDisabled\DISBTNEnergyPotion.blp',r'ReplaceableTextures\CommandButtons\BTNPotionOfOmniscience.blp']:
 print(path,'map',bool(a.get_hash_table_entry(path)))
 for ext in ['blp','dds']:
  name=path.rsplit('.',1)[0]+'.'+ext;b=game_read('war3.w3mod:'+name);print('  native',name,len(b) if b else None)
# Scan every known textual archive file for malformed CR runs and all item icon references.
h=c.c_void_p();assert storm.SFileOpenArchive(str(p.resolve()),0,0x100,c.byref(h));bad=[]
for n in names:
 if n.lower().endswith(('.txt','.fdf','.toc','.slk','.wts','.j')):
  try:b=read_storm(h,n)
  except (AssertionError,ValueError):continue
  if b'\r\r' in b:bad.append({'file':n,'bad_runs':len(re.findall(rb'\r{2,}\n',b))})
print('MALFORMED TEXT',bad)
report=[]
for fn in ['war3map.w3t','war3mapSkin.w3t']:
 for t in objdata.load('ui-label-repair/'+fn)['tables']:
  for e in t:
   for m in e['mods']:
    if m['id']!='iico' or not m['value']:continue
    path=m['value']; candidates=[path,path.rsplit('.',1)[0]+'.dds'];found=bool(a.get_hash_table_entry(path)) or any(game_read('war3.w3mod:'+x) for x in candidates)
    if not found:report.append({'file':fn,'id':e['newId'] if e['newId']!='\0'*4 else e['oldId'],'icon':path})
storm.SFileCloseArchive(h)
Path('ui-label-repair/asset-audit.json').write_text(json.dumps({'malformed_text':bad,'unresolved_item_icons':report},indent=2));print('MISSING ICONS',json.dumps(report))
