from pathlib import Path
import json
R=Path(__file__).resolve().parent
# Re-run v31's actual JASS behavior checks against the v32 source, then extend.
prior=R.parent/'hero-rework/checks.py'
exec(compile(prior.read_text(encoding='utf8'),str(prior),'exec'))
for name in ['MD_Clear','MD_Eligible','MD_Resistant','MD_InitTypes','MD_Start','MD_Tick','MD_OnDamage','MD_Burst','MD_OnDeath','MD_OnChannel','MD_OnOrder']:
 exec(translate(name),env)
old_setup=setup
def setup():
 old_setup()
 for key in ['UNIT_TYPE_HERO','UNIT_TYPE_STRUCTURE','UNIT_TYPE_FLYING','UNIT_TYPE_MECHANICAL','UNIT_TYPE_MAGIC_IMMUNE','UNIT_TYPE_RESISTANT']:env[key]=key
 env.update(MD_Hash=4,MD_Types=5,
  GetUnitTypeId=lambda u:units[u].get('skin','hfoo') if u in units else 0,
  IsUnitType=lambda u,t:t in units[u].get('types',set()),IsUnitHidden=lambda u:units[u].get('hidden',False),IsUnitLoaded=lambda u:bool(units[u].get('transport')),
  IsUnitInTransport=lambda u,v:units[u].get('transport')==v,BlzIsUnitInvulnerable=lambda u:units[u].get('invulnerable',False),IsUnitIllusion=lambda u:units[u].get('illusion',False),
  GetPlayerId=lambda p:p,GetUnitAbilityLevel=lambda u,a:units[u].get('ranks',{}).get(a,1 if a in units[u]['abilities'] else 0),
  IsUnitAlly=lambda u,p:units[u]['owner']==p,GetEventDamageSource=lambda:event.get('source'),GetKillingUnit=lambda:event.get('killer'),
  CreateSoundFromLabel=lambda *a:77,SetSoundPosition=lambda *a:None,StartSound=lambda b:event.update(sounds=event.get('sounds',0)+1),KillSoundWhenDone=lambda *a:None,
  MD_Reject=lambda u:event.update(rejected=True),GetSpellAbilityId=lambda:event.get('spell','AMu3'),GetSpellTargetUnit=lambda:event.get('target',2),
  GetIssuedOrderId=lambda:event.get('order','devour'),OrderId=lambda s:s,GetOrderTargetUnit=lambda:event.get('target',2))
 units[1]['skin']='HMu1'
 for kind in ['UnitHandle','TimerHandle','PlayerHandle','EffectHandle']:
  env['Load'+kind]=lambda h,i,k:H.get((h,i,k))
 env['MD_InitTypes']()
def start(rank=1):env['MD_Start'](1,2,rank)

setup();check(env['MD_Eligible'](1,2),'Enemy organic ground soldier is eligible')
units[2]['owner']=0;check(env['MD_Eligible'](1,2),'Allied organic ground soldier is eligible')
for key in ['UNIT_TYPE_HERO','UNIT_TYPE_STRUCTURE','UNIT_TYPE_FLYING','UNIT_TYPE_MECHANICAL','UNIT_TYPE_MAGIC_IMMUNE','UNIT_TYPE_RESISTANT']:
 setup();units[2]['types']={key};check(not env['MD_Eligible'](1,2),f'Devour excludes {key}')
for field,val in [('hidden',True),('transport',3),('illusion',True),('invulnerable',True),('alive',False),('owner',12)]:
 setup();units[2][field]=val;check(not env['MD_Eligible'](1,2),f'Devour excludes {field}={val}')
setup();units[2]['abilities'].add('A0IL');check(not env['MD_Eligible'](1,2),'Colossal marker blocks Devour')
setup();units[2]['abilities'].add('AIsr');check(not env['MD_Eligible'](1,2),'Spell damage resistance blocks Devour')
setup();units[2]['skin']='nogr';check(not env['MD_Eligible'](1,2),'Player-owned creep type remains excluded')
setup();check(not env['MD_Eligible'](1,1),'Cannot devour self')
setup();start();check(H[4,1,1]==2 and H[4,2,10]==1,'Meal stored independently by caster and victim')
env['MD_Start'](1,3,2);check(event.get('rejected') and H[4,1,1]==2,'Second meal rejected without replacing current target')
setup();start();env['MU_Now']=1.;env['MD_Tick'](1);check((4,1,1) not in H and (4,2,10) not in H,'Failed native swallow clears tracking without reward')
setup();start();units[2]['transport']=1;env['MD_Tick'](1);check(H[4,1,5],'Native transport confirms swallowing')
units[2].pop('transport');env['MD_Tick'](1);check((4,1,1) not in H and not event.get('sounds'),'Released meal clears without healing burst')
setup();start();units[2]['transport']=1;units[1]['owner']=1;env['MD_Tick'](1);check((4,1,1) not in H,'Ownership change cancels meal bonuses')
for rank in range(1,7):
 setup();start(rank);units[2]['transport']=1;event.update(unit=2,source=1,damage=100.)
 before=units[1]['hp'];env['MD_OnDamage']();check(abs(units[1]['hp']-before-(20.+5.*rank))<1e-6,f'Rank {rank} digestion heals {20+5*rank}% of damage')
 setup();units[1]['hp']=100.;units[3]['hp']=100.;units[2]['hp']=100.;units[2]['x']=0.
 units[3]['x']=250.+50.*rank;env['MD_Burst'](1,rank)
 check(units[1]['hp']==250.+50.*rank and units[3]['hp']==250.+50.*rank and units[2]['hp']==100.,f'Rank {rank}: exact burst heal and radius; enemies never healed')
 units[3]['x']+=.01;units[3]['hp']=100.;env['MD_Burst'](1,rank);check(units[3]['hp']==100.,f'Rank {rank}: units outside burst radius excluded')
setup();start(6);units[2]['transport']=1;units[2]['hp']=10.;event.update(unit=2,source=1,damage=1000.);env['MD_OnDamage']();check(units[1]['hp']==805.,'Overkill does not inflate digestion healing')
setup();start();units[2]['transport']=1;event.update(unit=2,source=3,damage=100.);env['MD_OnDamage']();check(units[1]['hp']==800.,'Unrelated damage does not grant digestion healing')
setup();start();units[2]['transport']=1;units[1].update(x=900.,y=400.);event.update(unit=2,source=1,damage=100.);env['MD_OnDamage']();check((units[2]['x'],units[2]['y'])==(900.,400.),'Passenger positioned before native lethal damage and XP distribution')
setup();start(3);units[2].update(hidden=True,transport=1,alive=False);units[1].update(x=900.,y=400.,hp=100.);units[3].update(x=900.,y=400.,hp=100.);event.update(unit=2,killer=1)
env['MD_OnDeath']();check(units[1]['hp']==400. and units[3]['hp']==400. and event['sounds']==1,'Finished digestion burps and heals caster plus nearby ally')
check((units[2]['x'],units[2]['y'])==(900.,400.),'Digestion death positioned at Mundo for existing shared XP handlers')
env['MD_OnDeath']();check(event['sounds']==1 and units[1]['hp']==400.,'Repeated death event cannot duplicate burst')
setup();start();units[1]['alive']=False;units[2].update(hidden=True,transport=1,alive=False);event.update(unit=2,killer=1);env['MD_OnDeath']();check(not event.get('sounds'),'Caster death does not produce a completion reward')
setup();start();units[2].update(hidden=True,transport=1,alive=False);event.update(unit=2,killer=3);env['MD_OnDeath']();check(not event.get('sounds'),'Another killer cannot trigger digestion completion')
setup();event.update(unit=1,target=2);units[2]['types']={'UNIT_TYPE_HERO'};env['MD_OnChannel']();check(event.get('rejected'),'Channel guard rejects hero before native Devour effect')
setup();units[1]['ranks']={'AMu3':4};event.update(unit=1,target=2);env['MD_OnChannel']();check('AMdc' in units[1]['abilities'],'Channel prepares native digestion cargo')
setup();env['DR_Start'](1,2);check({'AMui','AMuh','AMuc','AMud'}<=units[1]['abilities'] and 'ADrd' not in units[1]['abilities'],'Mundo Undying uses separately named modifiers')
i=H[3,1,-40];event.update(unit=1,damage=1000.);env['DR_Damage']();env['DK_Now']=9.96875;env['DK_Tick']();check(not units[1]['alive'] and not units[1]['abilities'],'Mundo refuses lethal damage for ten seconds then dies and cleans modifiers')

# Verify native object integration and unchanged kill reward handlers.
import sys
sys.path.insert(0,str(Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots\tools')))
import objdata
a=objdata.load(str(R/'src/war3map.w3a'));es={e['newId']:e for t in a['tables'] for e in t}
check(es['AMu3']['oldId']=='Adev' and es['AMdc']['oldId']=='Advc','Devour and digestion are native Kodo abilities')
get=lambda id,k,lv:next(m['value'] for m in es[id]['mods'] if m['id']==k and m['level']==lv)
for lv in range(1,7):check(get('AMdc','Dev2',lv)==35.+15.*lv and get('AMu3','Dev1',lv)==100,f'Rank {lv}: native digestion DPS and level cap configured')
check(functions['InitTrig_FF_Runtime'].index('call MD_Init()')<functions['InitTrig_FF_Runtime'].index('call FF_Editor_InitTriggers()'),'Devour death handler registered before map XP handlers')
old=(R.parent/'hero-rework/src/war3map.j').read_text(encoding='utf8')
oldf={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',old)}
for name in oldf:
 if 'Experience' in name or 'Exp_system' in name or 'Bounty' in name:assert oldf[name]==functions[name],name
check(True,'Existing XP and bounty logic preserved without manual duplicate payouts')
(R/'behavior-checks.json').write_text(json.dumps(dict(passed=len(results),checks=results,scope='Executed JASS with mocked natives plus native object validation; live engine testing pending'),indent=2))
print(f'{len(results)} total checks passed, including v31 regression checks.')
