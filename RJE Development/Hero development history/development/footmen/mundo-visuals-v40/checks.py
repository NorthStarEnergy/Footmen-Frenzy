from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent
prior_code=(W/'mundo-maul-v38/checks.py').read_text()
old="exec(compile(prior.read_text(),str(prior),'exec'))"
replacement="""hero_tests=prior.read_text().replace('def launch(', (R/'test_support.py').read_text()+'\\n\\ndef launch(',1)
exec(compile(hero_tests,str(prior),'exec'))"""
assert old in prior_code
exec(compile(prior_code.replace(old,replacement),str(W/'mundo-maul-v38/checks.py'),'exec'))

def hit_pickup():
 env.update(udg_MissileHitUnit=2,udg_MissileTravelled=550.)
 env['MU_OnCleaverHit']();env['MQ_Remove']();event['timer']=env['udg_MissileData'];units[1]['x']=units[2]['x'];env['MQ_GroundTick']()

setup();i=launch(missing=0.);hit_pickup()
check(H[2,1,60] and H[2,1,61] in fx,'Successful hit plus pickup grants one visible Bloodied charge')
check(all(v.get('destroyed') for k,v in fx.items() if v.get('kind') in ['beam','label']),'Pickup destroys ring tether and countdown handles')
loaded_fx=H[2,1,61];units[1]['hp']=500.;i=launch(missing=0.)
check(H[1,i,12] and (2,1,60) not in H and fx[loaded_fx]['destroyed'],'Throw snapshots and consumes charge and loaded effect')
hit_pickup();check(hits[-1][2]==180. and units[1]['hp']==575.,'Bloodied throw multiplies impact damage and healing by exactly 1.5')
check(H[2,1,60],'Bloodied hit-and-pickup refreshes the next charge')
for _ in range(3):
 units[1]['hp']=500.;i=launch(missing=0.);hit_pickup()
 check(hits[-1][2]==180. and units[1]['hp']==575.,'Repeat chain refreshes one charge without stacking')
i=launch(missing=0.);env['udg_MissilePosition']=(1100.,0.);env['MQ_Finish']();env['MQ_Remove']();event['timer']=i;units[1]['x']=1100.;env['MQ_GroundTick']()
check((2,1,60) not in H,'Empowered miss drops a normal blade and breaks the chain')
setup();i=launch();hit_pickup();j=launch(3)
check(not H[1,j,12] and H[2,1,60],'Another Mundo cannot consume or inherit the charge')
setup();i=launch();hit_pickup();f=H[2,1,61];env['MQ_ClearLoaded'](1)
check(fx[f]['destroyed'] and (2,1,60) not in H and (2,1,61) not in H,'Loaded state and attachment are completely removable')
check('call MQ_ClearLoaded(u)' in functions['MU_Clear'],'Shared death/removal/ownership cleanup clears loaded state')
setup();i=launch();env.update(udg_MissileHitUnit=2,udg_MissileTravelled=0.);env['MU_OnCleaverHit']();env['MQ_Remove']();event['timer']=i
for _ in range(96):env['MQ_GroundTick']()
check((2,1,60) not in H and all(v.get('destroyed') for v in fx.values()),'Expired bloodied drop grants no charge and releases all effects')

setup();start();units[2]['transport']=1;env['MD_Tick'](1)
slot=H[4,1,21];a=env['MDV_Code'][slot]
check(a in units[1]['abilities'] and event['icons'][a]=='icon:hfoo','Confirmed swallow shows victim unit icon on its own ability')
check(event['remaining_cd'][1,a]==20.,'Initial 1000 HP / 50 DPS meal countdown is 20 seconds')
units[2]['hp']=750.;env['MD_Tick'](1)
check(event['remaining_cd'][1,a]==15. and '750' in event['tips'][a],'Meal status tracks remaining HP and time')
event.update(unit=2,source=1,damage=25.);env['MU_Now']=1.;env['MD_OnDamage']();env['MU_Now']=2.;env['MD_OnDamage']();env['MD_Tick'](1)
check(H[4,1,26]==25. and event['remaining_cd'][1,a]==30.,'Countdown adapts to actual reduced digestion DPS')
meal_fx=H[4,1,22];env['MD_Clear'](1)
check(a not in units[1]['abilities'] and not env['MDV_Used'][slot] and fx[meal_fx]['destroyed'],'Meal cleanup removes D button and effect and releases its unique slot')
setup();start();units[2]['transport']=1;env['MD_Tick'](1);a=env['MDV_Code'][H[4,1,21]]
units[4]=dict(units[2],skin='hpea',transport=None,abilities=set());env['MD_Start'](3,4,2);units[4]['transport']=3;env['MD_Tick'](3);b=env['MDV_Code'][H[4,3,21]]
check(a!=b and event['icons'][a]=='icon:hfoo' and event['icons'][b]=='icon:hpea','Concurrent Mundos retain independent victim icons and cooldowns')
units[1]['owner']=1;env['MD_Tick'](1)
check(a not in units[1]['abilities'] and b in units[3]['abilities'],'Ownership cleanup removes only the affected meal indicator')
setup();start();env['MU_Now']=1.;env['MD_Tick'](1)
check(not any(env['MDV_Used'].values()) and not event.get('remaining_cd'),'Failed swallow never displays a phantom meal')
check(all(get(code,'abpx',0)==2 and get(code,'abpy',0)==1 and get(code,'ahky',0)=='D' for code in [f'mD{i:02X}' for i in range(256)]),'All independent meal indicators occupy the D position')
for code in ['AMu1','AMu3']:
 check('BTNMundo' in get(code,'aart',0) and 'BTNMundo' in get(code,'arar',0),code+' uses new active and research icon')
report=dict(passed=len(results),checks=results,scope='Actual JASS translated with mocked engine natives and object checks; native visuals require Warcraft playtest')
(R/'checks.json').write_text(json.dumps(report,indent=2));print('Mundo v40:',len(results),'checks passed')

