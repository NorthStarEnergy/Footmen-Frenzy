from pathlib import Path
R=Path(__file__).resolve().parent
source=(R.parent/'consolidated-v36/tests/tf/checks.py').read_text()
source=source.replace('.*?^endfunction',r'.*?^[ \t]*endfunction')
source=source.replace("if n.startswith('TF33_'):","if n.startswith(('TF33_','TF45_')):")
source=source.replace(r"C:\Users\User\Documents\Codex\2026-10-29\in-x20\work\hero-rework\checks.py",str(R.parent/'consolidated-v36/tests/hero-rework/checks.py'))
source=source.replace("check(gold[0]==[15,20,30,60,80,100][r-1],f'Gamble rank {r}: exact 60-second payout')","check(gold[0]==0,f'Loaded Dice rank {r}: no passive gold')")
source=source.replace("check(gold[0]==1,'Revival resumes normal payout without catch-up')","check(gold[0]==0 and H[11,1,1]==4.,'Revival starts fresh survival credit without passive gold')")
extra='''
base_tf_setup=setup
def setup():
 base_tf_setup()
 env.update(IMinBJ=min,I2R=float,R2I=int,I2S=str,Atan2=math.atan2,bj_RADTODEG=180/math.pi,SetUnitFacing=lambda *a:None,
  BlzSetSpecialEffectScale=lambda *a:None,GetKillingUnit=lambda:event.get('killer',1),
  GetRandomReal=lambda a,b:event.get('roll',0.),DisplayTextToPlayer=lambda *a:event.setdefault('messages',[]).append(a[-1]),
  CreateForce=set,DestroyForce=lambda f:None,ForceAddPlayer=lambda f,p:f.add(p),IsPlayerInForce=lambda p,f:p in f,
  Player=lambda i:i,GetRandomInt=lambda a,b:event.get('start',0),IsPlayerEnemy=lambda p,q:p!=q and p not in event.get('allies',set()),
  GroupEnumUnitsOfPlayer=lambda g,p,f:g.__setitem__(slice(None),[u for u in units if units[u]['owner']==p]),
  TF45_Gate=12,LoadTimerHandle=lambda h,i,k:H.get((h,i,k)),BlzSetSpecialEffectYaw=lambda *a:None,SetUnitAnimation=lambda *a:None,QueueUnitAnimation=lambda *a:None,
  GetSpellTargetX=lambda:event.get('x',500.),GetSpellTargetY=lambda:event.get('y',0.),TFP_wildCards___ENUM_RADIUS=32.)
'''
source=source.replace('results=[]',extra+'\nresults=[]')
source=source[:source.index("(R/'behavior-checks.json').write_text")]
exec(compile(source,str(__file__),'exec'))

setup();cast('ATf2');cast('ATf4');t=H[10,1,1];tick(t,199)
check(not timers[t].get('destroyed') and 'ATf7' in units[1]['abilities'],'Locked card remains usable for 9.95 seconds')
tick(t);check(timers[t]['destroyed'],'Locked card expires at ten seconds')
setup();cast('ATf2');cast('ATf4');cast('ATf7');t=max(timers);effect=H[10,t,6];tick(t,60)
check(fx[effect]['destroyed'],'Homing card attached effect is destroyed on impact')

for seconds,kills,expected in [(0,0,50),(0,5,60),(450,0,55),(450,3,61),(900,0,60),(900,5,70),(1800,99,70)]:
 setup();H[11,1,1]=seconds;H[11,1,2]=kills
 check(env['TF45_Odds'](1)==expected,f'Dice probability: {seconds}s + {kills} kills = {expected}%')
for odds,seconds,kills in [(50,0,0),(60,0,5),(70,900,5)]:
 for roll,delta in [(odds-.01,50),(odds,-50),(99.99,-50)]:
  setup();gold[0]=50;H[11,1,1]=seconds;H[11,1,2]=kills;event.update(spell='ATfg',roll=roll)
  env['TF45_Roll']()
  check(gold[0]==50+delta and cooldowns[-1]==(1,'ATfg',60.),f'Dice {odds}%: roll {roll} settles net {delta} with 60s cooldown')
setup();gold[0]=49;event['spell']='ATfg';env['TF45_Roll']()
check(gold[0]==49 and not any(c[-1]==60. for c in cooldowns),'Insufficient gold does not charge wager or start cooldown')
setup();gold[0]=100;event['spell']='ATfg';units[1]['illusion']=True;env['TF45_Roll']()
check(gold[0]==100 and not any(c[-1]==60. for c in cooldowns),'Illusion cannot gamble')
setup();env['TF33_Heroes'].append(1);H[11,1,1]=900.;H[11,1,2]=5;event.update(unit=1,killer=2);units[1]['alive']=False;env['TF45_Death']()
check(env['TF45_Odds'](1)==50.,'Death immediately clears survival and kill bonuses')
units[1]['alive']=True;event['enum']=1;env['TF33_IncomeHero']()
check(abs(env['TF45_Odds'](1)-(50+1/90))<1e-9,'Respawn begins survival scaling again from zero')
setup();env['TF33_Heroes'].append(1);units[2]['types']={'UNIT_TYPE_HERO'};event.update(unit=2,killer=1)
for _ in range(8):env['TF45_Death']()
check(H[11,1,2]==5 and env['TF45_Odds'](1)==60.,'Hero kills immediately add two points, capped at five')
for reason in ['ally','illusion','troop','dead killer']:
 setup();env['TF33_Heroes'].append(1);units[2]['types']={'UNIT_TYPE_HERO'};event.update(unit=2,killer=1)
 if reason=='ally':units[2]['owner']=0
 elif reason=='illusion':units[2]['illusion']=True
 elif reason=='troop':units[2]['types']=set()
 else:units[1]['alive']=False
 env['TF45_Death']();check(H.get((11,1,2),0)==0,'No kill bonus for '+reason)
setup()
for _ in range(1000):env['TF33_IncomeHero']()
check(H[11,1,1]==900. and gold[0]==0,'Survival stops scaling at 15 minutes and grants no passive income')
for x,y,expected in [(23,31,True),(23,33,False),(0,0,True),(46.7,32,True),(-33,0,False)]:
 check(env['TF45_LineHit'](x,y,0.,0.,46.7,0.)==expected,f'Swept narrow card hit at {x},{y}')
setup();event.update(spell='ATfc',x=700.,y=200.);env['TF45_GateStart']();t=H[12,1,0];effects=[H[12,1,k] for k in (1,2,3)]
check(len(effects)==3 and not any(fx[e].get('destroyed') for e in effects),'Gate creates source ring, destination ring and channel effect before teleport')
tick(t,30);check(not timers[t].get('destroyed'),'Gate visuals persist while channeling')
env['TF45_GateEnd']();check(timers[t]['destroyed'] and all(fx[e]['destroyed'] for e in effects),'Gate completion/interruption cleans all effects and timer')
setup();event['spell']='ATfc';env['TF45_GateStart']();t=H[12,1,0];units[1]['alive']=False;tick(t)
check(timers[t]['destroyed'],'Death cleans active gateway effects')
for count in [1,2,3,6,9,11]:
 setup();units={1:units[1]}
 for p in range(1,count+1):units[10+p]=dict(units[1],owner=p,types={'UNIT_TYPE_HERO'})
 gold[0]=100;event.update(spell='ATfg',roll=99.);env['TF45_Roll']()
 payouts=[gold[p] for p in range(1,count+1)]
 check(gold[0]==50 and sum(payouts)==50 and max(payouts)-min(payouts)<=1,f'Loss split among {count} enemies preserves exactly 50g with fair rounding')
setup();units[2]['types']={'UNIT_TYPE_HERO'};units[4]=dict(units[2]);env['TF45_ShareLoss'](0)
check(gold[1]==50,'Multiple heroes owned by one enemy receive only one share')
setup();units[2]['types']={'UNIT_TYPE_HERO'};units[2]['alive']=False;env['TF45_ShareLoss'](0)
check(sum(gold.values())==0,'No eligible living enemies: no payout or division by zero')
setup();units[2]['types']={'UNIT_TYPE_HERO'};units[2]['illusion']=True;env['TF45_ShareLoss'](0)
check(sum(gold.values())==0,'Illusions do not qualify for lost gold')
setup();units[2]['types']={'UNIT_TYPE_HERO'};event['allies']={1};env['TF45_ShareLoss'](0)
check(sum(gold.values())==0,'Allied players do not receive lost gold')
(R/'tf-checks.json').write_text(json.dumps(dict(passed=len(results),checks=results,scope='Translated JASS with mocked natives; native engine playtest pending'),indent=2))
print(f'{len(results)} TF checks passed')


