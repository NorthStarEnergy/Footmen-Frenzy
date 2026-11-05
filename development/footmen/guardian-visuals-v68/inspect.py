from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c,objdata
base=W/'dark-matter-icon-v68/FF799X_Rx_Veigar_Classic_v68_DarkMatterIcon.w3x'
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
names=['war3map.j','war3map.wct','war3map.w3u','war3map.w3a','war3map.imp','war3mapImported\\HiveForceShield.mdx','war3mapImported\\TFWhite.blp']
names += ['ReplaceableTextures\\'+folder+'\\'+prefix+'GuardianForceField.blp' for folder,prefix in [('CommandButtons','BTN'),('CommandButtonsDisabled','DISBTN')]]
for n in names:
 p=R/'base'/n.replace('\\','/');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(read_storm(h,n))
storm.SFileCloseArchive(h)
o=objdata.load(str(R/'base/war3map.w3u'))
print(json.dumps([e for t in o['tables'] for e in t if e['newId']=='htf4'],indent=2))
print('WCT', (R/'base/war3map.wct').stat().st_size)

