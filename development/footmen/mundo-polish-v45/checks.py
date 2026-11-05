from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent
prior=(W/'mundo-ultimate-v42/checks.py').read_text()
# Keep the old suite but update the deliberately changed rank-four landing.
prior=prior.replace("old=\"exec(compile", "prior_code=prior_code.replace(\"units[2]['x']==-200.\", \"units[2]['x']==-290.\")\nold=\"exec(compile",1)
exec(compile(prior,str(W/'mundo-ultimate-v42/checks.py'),'exec'))

for rank in range(1,7):
 setup();units[2]['types']={'UNIT_TYPE_HERO'};cast(rank=rank)
 t=max(timers);event['timer']=t
 check(abs(timers[t]['delay']*16-0.5/1.05)<1e-9,'Flip duration is 5 percent faster at rank '+str(rank))
 for _ in range(16):env['MU_FlingTick']()
 check(abs(units[2]['x']+200.+30.*(rank-1))<1e-7,'Flip distance scales at rank '+str(rank))
 check(not units[2]['paused'] and hits[-1][2]==50.+30.*(rank-1),'Flip releases target and deals unchanged rank damage')

# Endpoints can be walkable even when a wall blocks the trajectory.
setup();units[2]['types']={'UNIT_TYPE_HERO'}
env['IsTerrainPathable']=lambda x,y,p:-110.<x<-70.
cast(rank=6);t=max(timers);event['timer']=t
for _ in range(16):env['MU_FlingTick']()
check(units[2]['x']>=-38. and not units[2]['paused'],'Wall crossing is shortened before target footprint reaches it')
setup();units[2]['types']={'UNIT_TYPE_HERO'}
env['GetTerrainCliffLevel']=lambda x,y:3 if x<-90. else 2
cast(rank=6);t=max(timers);event['timer']=t
for _ in range(16):env['MU_FlingTick']()
check(units[2]['x']>=-58.,'Upper platform is rejected even with a walkable landing')
setup();units[2]['types']={'UNIT_TYPE_HERO'};env['GetRectMinX']=lambda r:-120.
cast(rank=6);t=max(timers);event['timer']=t
for _ in range(16):env['MU_FlingTick']()
check(units[2]['x']>=-88.,'Map edge leaves collision-radius clearance')
setup();units[2]['types']={'UNIT_TYPE_HERO'};cast(rank=6);t=max(timers);event['timer']=t
env['MU_FlingTick']();last=units[2]['x'];env['IsTerrainPathable']=lambda *a:True;env['MU_FlingTick']()
check(units[2]['x']==last and not units[2]['paused'] and timers[t]['destroyed'],'New obstruction stops at last safe location and releases timer and pause')
setup();units[2]['types']={'UNIT_TYPE_HERO'};cast(rank=6);t=max(timers);event['timer']=t;units[2]['alive']=False;env['MU_FlingTick']()
check(not units[2]['paused'] and not hits and timers[t]['destroyed'],'Target death in flight releases all movement state')

setup();i=launch();land(i)
check(not any(v.get('kind') in ['beam','label'] for v in fx.values()),'Cleaver creates no chain/tether or floating countdown label')
check(H[1,i,13] in fx,'Cleaver retains a ground pickup circle')
env['MQ_Free'](i)
check(all(v.get('destroyed') for v in fx.values()),'Pickup circle and blade are released together')
for lv in range(1,7):check(get('AMu1','aran',lv)==1100.,'Cleaver cast range matches projectile at rank '+str(lv))
check(get('AMu1','ahky',0)=='Z' and get('AMu2','ahky',0)=='X','Cleaver Z and burning aura X avoid hotkey collision')
check(get('AMu1','abpx',0)==0 and get('AMu2','abpx',0)==1,'Active ability slots agree with ZXCV grid')

import sys
sys.path.insert(0,str(W/'mini-foots/tools'))
from validate_objdata import validate
import objdata
for n in ['war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3mapSkin.w3a']:
 validate((R/'src'/n).read_bytes(),n.endswith('.w3a'))
check(True,'Independent binary parser accepts all modified object data, retaining startup fix')
stats=json.loads((R/'changes.json').read_text())['stats']
u={e['newId']:e for t in objdata.load(str(R/'src/war3map.w3u'))['tables'] for e in t}['HMu1']
actual={m['id']:m['value'] for m in u['mods']}
check(all(abs(actual[k]-v)<1e-5 if isinstance(v,(int,float)) else actual[k]==v for k,v in stats.items()),'All 37 base combat, movement, health, mana and attribute fields match Strongest Man data')
for field in ['STR_base','STR_inc','AGI_base','AGI_inc','INT_base','INT_inc','move_base','turnrate']:
 one=re.search(r'set udg_hero_'+field+r'\[37\]=([^\n]+)',s)[1]
 two=re.search(r'set udg_hero_'+field+r'\[95\]=([^\n]+)',s)[1]
 check(one==two,'Runtime hero stat matches Strongest Man: '+field)
report=dict(passed=len(results),checks=results,scope='Actual JASS translated with mocked natives, binary format validation and object checks; native visuals and terrain require Warcraft playtest')
(R/'checks.json').write_text(json.dumps(report,indent=2));print(len(results),'total checks passed')
