from pathlib import Path
import sys,re,difflib,json
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'hero-polish'))
import archive_helpers as a
paths=[Path(r'C:\Users\User\Documents\Warcraft III\Maps\Download\Reforged_Footmen_Frenzy_v7.9.9W-rc6.w3x'),root/'799x-backport/release/FF799X_Rx_Myrmidon_Cleave_v44.w3x']
out=root/'799x-backport/item-audit/koth-comparison';out.mkdir(exist_ok=True)
scripts=[]
for tag,path in zip(['rc6','v44'],paths):
 h=a.c.c_void_p();assert a.storm.SFileOpenArchive(str(path),0,0x100,a.c.byref(h))
 for name in ['war3map.j','war3map.w3u','war3mapSkin.w3u','war3map.wts']:
  try:data=a.read_storm(h,name)
  except AssertionError:continue
  (out/(tag+'-'+name)).write_bytes(data)
 assert a.storm.SFileCloseArchive(h)
 scripts.append((out/(tag+'-war3map.j')).read_text(encoding='utf-8-sig',errors='replace').replace('\r\n','\n'))
func=[a.functions(s) for s in scripts]
names=sorted({n for fs in func for n in fs if re.search('koth|hill',n,re.I)} | {n for fs in func for n,v in fs.items() if re.search('udg_KOTH|gg_trg_KOTH',v,re.I)})
for n in names:
 x,y=[d.get(n,'').splitlines(keepends=True) for d in func]
 if x!=y:
  print('\n'+n+'\n'+''.join(difflib.unified_diff(x,y,fromfile='RC6',tofile='v44',n=2)))
(out/'function-names.json').write_text(json.dumps(names,indent=2))
