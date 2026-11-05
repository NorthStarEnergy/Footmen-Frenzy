from pathlib import Path
exec((Path(__file__).resolve().parent/'tf_checks.py').read_text())
for n in ['TF46_RevealEnd','TFP_destiny___c','TFP_destiny___gateC']:exec(translate(n),env)
reveal_base_setup=setup
def setup():
 reveal_base_setup()
 env.update(TF46_H=46,FOG_OF_WAR_VISIBLE=1,GetWorldBounds=lambda:1,RemoveRect=lambda r:None,
  GetRectMinX=lambda r:-1800.,GetRectMaxX=lambda r:1800.,GetRectMinY=lambda r:-1800.,GetRectMaxY=lambda r:1800.,
  CreateFogModifierRect=lambda *a:500,FogModifierStart=lambda f:event.update(fog=True),FogModifierStop=lambda f:event.update(fog=False),DestroyFogModifier=lambda f:event.update(fog_destroyed=True),
  TimerStart=lambda t,d,r,cb:timers[t].update(duration=d,callback=cb),
  RemoveSavedHandle=lambda h,i,k:H.pop((h,i,k),None),PATHING_TYPE_WALKABILITY=1,IsTerrainPathable=lambda *a:event.get('blocked',False))
 for typ in ['GroupHandle','FogModifierHandle']:
  env['Save'+typ]=lambda h,i,k,v:H.update({(h,i,k):v})
  env['Load'+typ]=lambda h,i,k:H.get((h,i,k))
for rank,duration in [(1,10.),(2,13.),(3,15.)]:
 for teleport in [False,True]:
  setup();units[1]['ranks']['ATfb']=rank;event['spell']='ATfb';env['TFP_destiny___c']();t=H[46,1,0];g=H[46,t,1];dummies=list(g)
  check(timers[t]['duration']==duration and event['fog'] and len(g)==9,f'Rank {rank}: full-map reveal + detection grid for {duration}s')
  if teleport:
   event.update(spell='ATfc',x=700.,y=200.);env['TF45_GateStart']();gate=H[12,1,0];env['TFP_destiny___gateC']();env['TF45_GateEnd']()
   check(units[1]['x']==700. and 'ATfc' not in units[1]['abilities'] and event['fog'] and not timers[t].get('destroyed'),f'Rank {rank}: one teleport preserves reveal timer')
  tick(t)
  check(not event['fog'] and event['fog_destroyed'] and all(u not in units for u in dummies) and 'ATfc' not in units[1]['abilities'],f'Rank {rank}: reveal cleanup with teleport={teleport}')
setup();units[1]['ranks']['ATfb']=1;event['spell']='ATfb';env['TFP_destiny___c']();t=H[46,1,0]
event.update(spell='ATfc',x=700.,y=200.);env['TF45_GateStart']();env['TF45_GateEnd']()
check(units[1]['x']==0. and 'ATfc' in units[1]['abilities'] and event['fog'],'Interrupted channel does not teleport or consume reveal')
event['blocked']=True;env['TF45_GateStart']();env['TFP_destiny___gateC']()
check(units[1]['x']==0. and 'ATfc' in units[1]['abilities'],'Blocked landing is rejected')
units[1]['alive']=False;tick(t)
check(not event['fog'],'Caster death does not prevent scheduled reveal cleanup')
(R/'reveal-checks.json').write_text(json.dumps(dict(passed=len(results),checks=results),indent=2))
print(len(results),'total TF and reveal checks passed')

