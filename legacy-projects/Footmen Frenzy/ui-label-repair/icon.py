from pathlib import Path
import sys,struct,io,hashlib
sys.path.insert(0,'hero-polish')
from archive_helpers import *
from PIL import Image
for folder in ['tf-orb-v53','ryan-v54-cleanup/source','mundo-v64/release','pub-xp-v67/release']:
 p=list(Path(folder).rglob('*.w3x'))[0];h=c.c_void_p();assert storm.SFileOpenArchive(str(p.resolve()),0,0x100,c.byref(h))
 for n in [r'ReplaceableTextures\CommandButtons\BTNEnergyPotion.blp',r'ReplaceableTextures\CommandButtonsDisabled\DISBTNEnergyPotion.blp']:
  try:b=read_storm(h,n)
  except Exception as ex:
   print('READ FAILED',folder,n,str(ex));continue
  print(folder,n,len(b),b[:32].hex(),hashlib.sha256(b).hexdigest())
  if folder=='pub-xp-v67/release':
   Path('ui-label-repair/'+n.split('\\')[-1]).write_bytes(b)
   try:
    im=Image.open(io.BytesIO(b));im.load();print('DECODE',im.format,im.size);im.save('ui-label-repair/'+n.split('\\')[-1]+'.png')
   except Exception as ex:print('DECODE ERROR',str(ex))
 storm.SFileCloseArchive(h)

