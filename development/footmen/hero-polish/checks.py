"""Execute the existing lifecycle tests with the deliberately updated visual/radius contract."""
from pathlib import Path
import re,ast,sys,math,struct
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'mini-foots/tools'));import objdata
def run(V,variant):
 for name in ['check_runtime.py','check_gragus.py','check_guardian.py','check_guardian_bolts.py']:
  code=(W/'799x-backport'/name).read_text()
  code=code.replace('ROOT=Path(__file__).resolve().parent','ROOT=Path('+repr(str(V))+')')
  code=code.replace("(ROOT/'check_runtime.py')","(Path("+repr(str(W/'799x-backport'))+")/'check_runtime.py')")
  code=code.replace("(ROOT/'audit/v18-before-guardian/war3map.j')","(Path("+repr(str(W/'799x-backport'))+")/'audit/v18-before-guardian/war3map.j')")
  if name=='check_runtime.py':
   code=code.replace('[207.9,225.225,242.55,277.2,311.85,346.5]','[259.875,281.53125,303.1875,346.5,389.8125,433.125]')
   code=code.replace('[211.75,254.1,296.45]','[264.6875,317.625,370.5625]')
   code=code.replace("'AttackRing'", "'AttackGround'").replace("'ProtectRing'", "'ProtectGround'")
   code=code.replace("abs(glyph['scale']-207.9*.96*.5)<.001 and glyph['z']==108.","abs(glyph['scale']-259.875*.5)<.001 and glyph['z']==112.")
   code=code.replace("abs(glyph['scale']-211.75*.55)<.001", "abs(glyph['scale']-264.6875*.55)<.001")
   code=code.replace("effects[handles[10,-101]]['scale']==211.75", "abs(effects[handles[10,-101]]['scale']-264.6875*.625)<.001")
   extra='''
setup();units[3]['x']=500.;env.update(UNIT_TYPE_FLYING=99,PATHING_TYPE_WALKABILITY=0,SetUnitPosition=lambda u,x,y:units[u].update(x=x,y=y),IsTerrainPathable=lambda *a:False,RemoveSavedInteger=lambda h,k,n:handles.pop((k,n),None))
actual['OM_Pull'](3,0.,0.);ticks(10)
check('Actual Shockwave motion is 25% farther over unchanged duration',abs(units[3]['x']-(500.-234.375))<.001)
ticks(1);check('Completed pull clears tracking',env['OM_Pulls']==0)
setup();units[3]['x']=500.;env.update(UNIT_TYPE_FLYING=99,PATHING_TYPE_WALKABILITY=0,SetUnitPosition=lambda u,x,y:units[u].update(x=x,y=y),IsTerrainPathable=lambda *a:True,RemoveSavedInteger=lambda h,k,n:handles.pop((k,n),None))
actual['OM_Pull'](3,0.,0.);ticks(2)
check('Blocked terrain still stops upgraded pull',units[3]['x']==500. and env['OM_Pulls']==0)
'''
   code=code.replace("(ROOT/'audit/runtime-checks.json')",extra+"\n(ROOT/'audit/runtime-checks.json')")
  if name=='check_gragus.py':
   # This existing harness exercises buff lifecycle; deferred animation is executed independently below.
   code=code.replace('FS_Alive=lambda u:', 'FS_DrinkAnimation=lambda u:unit.update(animation=12),FS_Alive=lambda u:')
  if name=='check_guardian.py':
   code=code.replace('72.0, PATHING_TYPE_ANY','75.6, PATHING_TYPE_ANY').replace('), 0.675)', '), 0.70875)')
   if variant=='solo':code=code.replace("assert \"id == 'H043'\" not in functions['MF_HeroDisabled']", "assert \"'H043'\" not in functions['SoloFootsIsNoMuteHeroType']")
  exec(compile(code,name,'exec'),{'__file__':str(W/'799x-backport'/name),'__name__':'__main__'})
 s=(V/'src/war3map.j').read_text();functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
 ns=dict(re=re,functions=functions)
 for node in ast.parse((W/'799x-backport/check_runtime.py').read_text()).body:
  if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'),ns)
 data={};timers={};animation=[];counter=[100];order=[0];alive=[True];paused=[False];expired=[0]
 def timer():counter[0]+=1;return counter[0]
 def flush(h,k):
  for pair in list(data):
   if pair[0]==k:del data[pair]
 ns.update(FS_Hash=1,CreateTimer=timer,SaveUnitHandle=lambda h,k,c,u:data.__setitem__((k,c),u),LoadUnitHandle=lambda h,k,c:data.get((k,c)),GetHandleId=lambda t:t,TimerStart=lambda t,d,r,f:timers.__setitem__(t,(d,r,f)),GetExpiredTimer=lambda:expired[0],GetUnitCurrentOrder=lambda u:order[0],FS_Alive=lambda u:alive[0],IsUnitPaused=lambda u:paused[0],OrderId=lambda n:852164,SetUnitAnimationByIndex=lambda u,n:animation.append((u,n)),QueueUnitAnimation=lambda *a:None,FlushChildHashtable=flush,DestroyTimer=lambda t:timers.pop(t))
 for n in ['FS_DrinkDeferred','FS_DrinkAnimation']:exec(ns['translate'](n).replace('function ',''),ns)
 for current,live,pause,expected in [(0,True,False,True),(852164,True,False,True),(851986,True,False,False),(0,False,False,False),(0,True,True,False)]:
  order[0]=current;alive[0]=live;paused[0]=pause;animation.clear();ns['FS_DrinkAnimation'](7)
  assert not animation and len(timers)==1
  t=next(iter(timers));delay,repeating,callback=timers[t];assert delay==.03125 and not repeating
  expired[0]=t;callback();assert bool(animation)==expected and not timers and not data
 # A free target moves exactly 25% farther during the unchanged pull duration; collision/center guards remain.
 assert '750.0 * OM_TICK' in functions['OM_Tick'] and 'd - 48.0' in functions['OM_Tick'] and 'IsTerrainPathable(x, y, PATHING_TYPE_WALKABILITY)' in functions['OM_Tick']
 assert sum(750*.03125 for _ in range(10))==sum(600*.03125 for _ in range(10))*1.25
 assert not any('Ring.mdx' in functions[n] for n in ['OM_StartPulse','OM_WindupFX','OM_ArrivalFX'])
 assert 'AddSpecialEffect(model' not in functions['OM_GroundRing']
 assert '55, 105, 255' in functions['GFW_Create']
 for filename in ['war3map.w3u','war3mapSkin.w3u']:
  d=objdata.load(str(V/'src'/filename))
  for t in d['tables']:
   for e in t:
    if e['newId']=='HGr1':assert next(m['value'] for m in e['mods'] if m['id']=='umvr')==1.0
 print('Deferred X animation/order interruption/death cleanup, turn rate, +25% pull and soft-ground contracts passed')
