from pathlib import Path
from collections import defaultdict
import re,math,json,sys
R=Path(__file__).resolve().parent
s=(R/'src/war3map.j').read_text()
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
ref=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport\check_runtime.py').read_text()
exec(ref[ref.index('def expression('):ref.index('def setup():')])
base_expression=expression
def expression(line):
 line=re.sub(r'(?<!\w)(\d+)\.(?!\d)',r'\1.0',line)
 line=re.sub(r'(?<![\w\d])\.(\d+)',r'0.\1',line)
 return base_expression(line).replace('function ','')
env={}
for n in functions:
 if n.startswith('TF33_'):exec(translate(n),env)
prior=Path(r'C:\Users\User\Documents\Codex\2026-10-29\in-x20\work\hero-rework\checks.py').read_text()
exec(prior[prior.index('\ndef setup():'):prior.index('def launch(')])
old_setup=setup
def setup():
 global tags,gold
 old_setup();tags={};gold=defaultdict(int);event.update(unit=1)
 noop=lambda *a:None
 def new(store,**kw):counter[0]+=1;store[counter[0]]=kw;return counter[0]
 def make(p,id,x,y,face):return new(units,x=x,y=y,hp=100.,maxhp=100.,owner=p,alive=True,abilities=set(),skin=id)
 for k in ['UNIT_TYPE_STRUCTURE','UNIT_TYPE_MAGIC_IMMUNE','UNIT_TYPE_HERO','UNIT_TYPE_MECHANICAL','PLAYER_SLOT_STATE_PLAYING','PLAYER_STATE_RESOURCE_GOLD','DAMAGE_TYPE_MAGIC']:env[k]=k
 units[1]['ranks']={'ATf2':1,'ATfg':1};units[1]['abilities'].update(['ATf2','ATfg']);units[1]['types']={'UNIT_TYPE_HERO'}
 units[3]['types']={'UNIT_TYPE_HERO'}
 env.update(TF33_H=10,TF33_G=11,TF33_Heroes=[],TFP_s__tfConsts_CARD_ID={0:'ATf3',1:'ATf4',2:'ATf5'},TFP_pickACard___GOLDFX='gold',
  TFP_TF_Alive=lambda u:u in units and units[u]['alive'] and units[u]['hp']>.405,IsUnitEnemy=lambda u,p:units[u]['owner']!=p,IsUnitAlly=lambda u,p:units[u]['owner']==p,
  IsUnitType=lambda u,t:t in units[u].get('types',set()),BlzIsUnitInvulnerable=lambda u:units[u].get('invulnerable',False),
  TFP_DamageType_dealCodeDamage=lambda c,v,d,t:hits.append((c,v,d)),TFP_TF_CardDebuff=lambda c,v,a,r,o:controls.append((v,a,r)),
  GetUnitAbilityLevel=lambda u,a:units[u].get('ranks',{}).get(a,1 if a in units[u]['abilities'] else 0),SetUnitAbilityLevel=lambda u,a,r:units[u].setdefault('ranks',{}).update({a:r}),
  GetSpellAbilityId=lambda:event['spell'],GetSpellTargetUnit=lambda:event.get('target',2),GetLearnedSkill=lambda:'ATfg',
  CreateUnit=make,RemoveUnit=lambda u:units.pop(u,None),CreateTextTag=lambda:new(tags),DestroyTextTag=lambda t:tags[t].update(destroyed=True),SetTextTagPermanent=noop,
  SetTextTagText=lambda t,v,size:tags[t].update(text=v),SetTextTagPosUnit=noop,SetTextTagVisibility=noop,IsUnitVisible=lambda *a:True,GetLocalPlayer=lambda:0,
  GetUnitFlyHeight=lambda u:units[u].get('height',0.),SetUnitFlyHeight=lambda u,v,r:units[u].update(height=v),
  HaveSavedHandle=lambda h,i,k:(h,i,k) in H,ModuloInteger=lambda a,b:a%b,BlzStartUnitAbilityCooldown=lambda u,a,t:cooldowns.append((u,a,t)),
  GetEnumUnit=lambda:event.get('enum',1),GetPlayerId=lambda p:p,GetPlayerSlotState=lambda p:'PLAYER_SLOT_STATE_PLAYING',IsUnitIllusion=lambda u:units[u].get('illusion',False),
  GetPlayerState=lambda p,k:gold[p],SetPlayerState=lambda p,k,v:gold.update({p:v}))
 for typ in ['TextTagHandle']:
  env['Save'+typ]=lambda h,i,k,v:H.update({(h,i,k):v})
  env['Load'+typ]=lambda h,i,k:H.get((h,i,k),0)
def cast(id,u=1,target=2):event.update(unit=u,spell=id,target=target);env['TF33_Cast']()
def tick(t,n=1):
 for _ in range(n):
  if timers[t].get('destroyed'):break
  event['timer']=t;timers[t]['callback']()
results=[]
def check(ok,label):assert ok,label;results.append(label)
for r in range(1,7):
 setup();units[3].update(owner=1,x=600.)
 env['TF33_Impact'](1,2,1,r)
 check(hits==[(1,2,90.+60*r),(1,3,45.+30*r)],f'Red rank {r}: direct and splash without double hit')
 setup();env['TF33_Impact'](1,2,2,r)
 check(hits==[(1,2,75.+50*r)] and controls==[(2,'ATfa',r)],f'Gold rank {r}: correct damage and stun rank')
 setup();units[4]=dict(units[3],types=set(),hp=800.)
 env['TF33_Impact'](1,2,0,r)
 check(hits==[(1,2,40.+40*r)] and units[1]['hp']==830.+20*r and units[3]['hp']==830.+20*r and units[4]['hp']==815.+10*r,f'Green rank {r}: hero heal, half troop heal, enemy damage')
 setup();units[1]['ranks']['ATfg']=r
 for _ in range(60):env['TF33_IncomeHero']()
 check(gold[0]==[15,20,30,60,80,100][r-1],f'Gamble rank {r}: exact 60-second payout')
setup();env['TF33_Impact'](1,2,0,6);units[3]['x']=301.;units[3]['hp']=800.;env['TF33_Impact'](1,2,0,6)
check(units[1]['hp']==1000. and units[3]['hp']==800.,'Healing respects maximum HP and radius')
for flag in ['UNIT_TYPE_STRUCTURE','UNIT_TYPE_MECHANICAL']:
 setup();units[3]['types']={flag};env['TF33_Impact'](1,2,0,6);check(units[3]['hp']==800.,f'Green excludes {flag}')
setup();env['TF33_Learn']();units[1]['alive']=False
for _ in range(30):env['TF33_IncomeHero']()
check(gold[0]==0 and (11,1,1) not in H,'Death accrues no income or elapsed credit')
units[1]['alive']=True
for _ in range(4):env['TF33_IncomeHero']()
check(gold[0]==1,'Revival resumes normal payout without catch-up')
setup();units[1]['illusion']=True;env['TF33_Heroes'].append(1);env['TF33_IncomeHero']();check(gold[0]==0 and not env['TF33_Heroes'],'Illusions earn no income')
setup();cast('ATf2');t=H[10,1,1];orb=H[10,1,2]
check(not hits and H[10,1,4]==1 and 'ATf4' in units[1]['abilities'],'Selection starts red with no damage')
tick(t,12);check(H[10,1,4]==2 and 'ATf5' in units[1]['abilities'],'Cycle advances to gold at 0.6 seconds')
tick(t,12);check(H[10,1,4]==0 and 'ATf3' in units[1]['abilities'],'Cycle advances to green')
cast('ATf3');tick(t,20);check('ATf6' in units[1]['abilities'] and H[10,1,4]==0,'Locked green stays stable')
cast('ATf6');flight=max(timers)
check(not hits and timers[t]['destroyed'] and orb not in units and cooldowns[-1]==(1,'ATf2',9.),'Throw cleans selection and starts cooldown; no instant damage')
tick(flight,5);check(not hits,'Projectile travel delays effect')
units[2]['x']=650.;tick(flight,40)
check(hits==[(1,2,80.)] and timers[flight]['destroyed'],'Projectile homes to moved target and resolves once')
for reason in ['death','immune','invulnerable','removed']:
 setup();cast('ATf2');cast('ATf4');cast('ATf7');t=max(timers)
 if reason=='death':units[2]['alive']=False
 elif reason=='immune':units[2]['types']={'UNIT_TYPE_MAGIC_IMMUNE'}
 elif reason=='invulnerable':units[2]['invulnerable']=True
 else:
  # Native coordinate and owner queries on removed handles return neutral values.
  units[2]['alive']=False
 tick(t);check(not hits and timers[t]['destroyed'],f'Flight cancels cleanly on target {reason}')
setup();cast('ATf2');t=H[10,1,1];tick(t,120)
check(timers[t]['destroyed'] and not any(k[:2]==(10,1) for k in H) and units[1]['abilities']=={'ATf2','ATfg'},'Selection expires and clears temporary abilities and handles')
setup();cast('ATf2');t=H[10,1,1];units[1]['alive']=False;tick(t)
check(timers[t]['destroyed'] and 'ATf4' not in units[1]['abilities'],'Caster death clears overhead and selection')
setup();units[3]['ranks']={'ATf2':6};units[3]['abilities'].add('ATf2');cast('ATf2');cast('ATf2',3);t1=H[10,1,1];t3=H[10,3,1];cast('ATf4');tick(t3,12)
check(H[10,1,4]==1 and H[10,1,5] and H[10,3,4]==2,'Two same-owner TFs have independent selection states')
(R/'behavior-checks.json').write_text(json.dumps(dict(passed=len(results),checks=results,scope='Executed translated JASS with mocked Warcraft natives; no live-engine test'),indent=2))
print(f'{len(results)} behavior checks passed')


