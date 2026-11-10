from pathlib import Path
import sys,re,shutil,json,hashlib,struct,ast
from archive_helpers import archive,storm,read_storm,c,functions
from patch import patch,objects
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'mini-foots/tools'));import objdata
variants={
 '799x':(W/'799x-backport/release/FF799X_Rx_WC3Icons_v25.w3x',W/'799x-backport/src','FF799X - Hero Polish v26','FF799X_Rx_HeroPolish_v26.w3x','FF799X - WC3 Icons v25'),
 'mini':(W/'hero-sync/release/Mini Foots v9.w3x',W/'hero-sync/mini/src','Mini Foots v10','Mini Foots v10.w3x','Mini Foots v9'),
 'solo':(W/'hero-sync/release/Solo Foots 6 Player FFA v2.w3x',W/'hero-sync/solo/src','Solo Foots 6 Player FFA v3','Solo Foots 6 Player FFA v3.w3x','Solo Foots 6 Player FFA v2')}
for variant,(base,source,title,filename,oldtitle) in variants.items():
 V=R/variant;O=V/'src';V.mkdir(exist_ok=True);(V/'audit').mkdir(exist_ok=True)
 if not (V/'base.w3x').exists():shutil.copy2(base,V/'base.w3x')
 base=V/'base.w3x';shutil.copytree(source,O,dirs_exist_ok=True)
 h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
 # Read authoritative core payloads from the frozen release rather than assuming source freshness.
 for name in ['war3map.j','war3map.w3u','war3map.w3a','war3map.wts','war3map.w3i','war3mapSkin.w3u']:
  if archive(base).get_hash_table_entry(name):(O/name).write_bytes(read_storm(h,name))
 assert storm.SFileCloseArchive(h)
 original=(O/'war3map.j').read_text(encoding='utf-8-sig');s=patch(original)
 s=s.replace(oldtitle,title).replace('Solo Foots v1.8 - 6 Player FFA v2','Solo Foots v1.8 - 6 Player FFA v3')
 (O/'war3map.j').write_text(s,encoding='utf8')
 for name in ['war3map.w3u','war3map.w3a','war3mapSkin.w3u']:
  if (O/name).exists():(O/name).write_bytes(objdata.dump(objects(objdata.load(str(O/name)))))
 for name in ['war3map.wts','war3map.w3i']:
  (O/name).write_bytes((O/name).read_bytes().replace(oldtitle.encode(),title.encode()).replace(b'Solo Foots v1.8 - 6 Player FFA v2',b'Solo Foots v1.8 - 6 Player FFA v3'))
 # Generate mathematical energy fields with continuously feathered alpha. Existing unit-radius
 # ground quads and their BLP texture references are reused; no new imported paths are needed.
 import numpy as np
 from PIL import Image
 module=ast.parse((W/'799x-backport/make_magic_textures.py').read_text());ns=dict(struct=struct,Image=Image)
 for node in module.body:
  if isinstance(node,ast.FunctionDef) and node.name=='blp':exec(compile(ast.Module(body=[node],type_ignores=[]),'blp','exec'),ns)
 y,x=np.mgrid[-1:1:512j,-1:1:512j];radius=np.sqrt(x*x+y*y);angle=np.arctan2(y,x)
 edge=np.clip((1-radius)/.20,0,1);edge=edge*edge*(3-2*edge)
 for name in ['AttackGround','ProtectGround','ShockGround','ShockImpact','MoveGround']:
  if name=='MoveGround':density=np.exp(-(x/.75)**2-(y/.23)**2)*(.65+.35*np.cos(x*9+y*4)**2)
  else:
   petals=10 if name=='AttackGround' else 7 if name=='ProtectGround' else 12
   ray=(.55+.45*np.cos(petals*angle+radius*5)**2)
   wave=np.exp(-((radius-.77-.035*np.sin(5*angle))/.16)**2)
   density=(.88*wave*ray+.30*np.exp(-(radius/.5)**2))*edge
   if name=='ShockGround':density=(.3+.7*(.5+.5*np.cos(3*angle+radius*7))**3)*np.exp(-(radius/.75)**2)*edge
  density=np.clip(density,0,1);rgba=np.zeros((512,512,4),dtype=np.uint8)
  rgba[:,:,0]=35+105*density;rgba[:,:,1]=115+115*density;rgba[:,:,2]=235+20*density;rgba[:,:,3]=250*density
  im=Image.fromarray(rgba);(O/'Spells/Orianna/Feedback'/(name+'.blp')).write_bytes(ns['blp'](im))
  assert rgba[0,:,3].max()==0 and rgba[-1,:,3].max()==0
  if variant=='799x':im.save(V/'audit'/(name+'.png'))
 bf,sf=functions(original),functions(s)
 report=dict(base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),title=title,filename=filename,changed_functions=[n for n in bf if sf[n]!=bf[n]],added_functions=sorted(sf.keys()-bf.keys()))
 (V/'changes.json').write_text(json.dumps(report,indent=2));print(variant,len(report['changed_functions']),'functions changed')
