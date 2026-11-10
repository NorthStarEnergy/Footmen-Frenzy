from pathlib import Path
import sys,re,json,difflib
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import functions
ss=(W/'latest-map-audit/solo/war3map.j').read_text(encoding='utf-8-sig');ms=(W/'consolidated-v84/src/war3map.j').read_text(encoding='utf-8-sig')
s,m=functions(ss),functions(ms)
selected=['Trig_HERO_Throw_Glaive_Loop_Func001Func001Func016Func001Func002C','Trig_HERO_Throw_Glaive_Loop_Func001Func001Func016Func001C','Trig_HERO_Throw_Glaive_Loop_Actions','Trig_HERO_Jaina_Ulti_Actions','Trig_HERO_Prison_Actions','Trig_HERO_Thor_Powerhit_Actions','Trig_Staff_of_the_River_Actions','Trig_Guardian_Energy_Chamber_Ally_Cast_Func006Func002A','Trig_SovietSniper_Decoy_Bomb_Cast_Actions','Trig_SovietSniper_Golovu_Shot_Loop_Func002A','Trig_limit_amount_of_creeps_Actions','Trig_page_system_Actions','Trig_ITEM_limits_Actions']
text=[]
for n in selected:
 if n not in s or n not in m:print('missing',n);continue
 diff=''.join(difflib.unified_diff(m[n].splitlines(True),s[n].splitlines(True),fromfile='799X/'+n,tofile='Solo/'+n))
 text.append(diff)
(R/'selected.diff').write_text('\n\n'.join(text),encoding='utf8')
# Compact overview of non-GUI/shared helpers.
names=[]
for n in s:
 if n in m and s[n]!=m[n] and not n.startswith(('Trig_','InitTrig_','s__','sa__','Create','Init','Solo','zoom_','FF_','FFGS_')):
  diff=[l for l in difflib.ndiff(m[n].splitlines(),s[n].splitlines()) if l.startswith(('+ ','- '))]
  if len(diff)<30:names.append(n+'\n'+'\n'.join(diff))
(R/'helpers.diff').write_text('\n\n'.join(names),encoding='utf8')
print('Selected diff lines',sum(len(x.splitlines()) for x in text));print('\n'.join(n for n in s if n not in m and n.startswith(('Item','Shop','Creep','SF','SoloFoots'))))
