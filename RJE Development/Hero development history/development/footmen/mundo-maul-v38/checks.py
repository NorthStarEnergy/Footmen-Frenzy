from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parent;W=R.parent
prior=W/'consolidated-v36/tests/hero-rework/checks.py'
exec(compile(prior.read_text(),str(prior),'exec'))
md=(W/'consolidated-v36/tests/mundo-kit/checks.py').read_text()
definitions=md[md.index("for name in ['MD_Clear'"):md.index('def start(')]
exec(definitions)
for n in ['FS_Enemy','MU_Fling','MU_FlingTick','MM_IsFlipTarget','MM_CanFlip','MM_CanCast','MM_Timeout','MM_DevourReady','MM_ExecuteDevour','MM_Cast','MU_OnCast','MD_OnChannel','MD_OnOrder']:
    exec(translate(n),env)
md_setup=setup
actual_enemy=env['FS_Enemy']
def setup():
    md_setup()
    env.update(MM_Hash=6,PATHING_TYPE_WALKABILITY=1,FS_Enemy=actual_enemy,IsUnitEnemy=lambda u,p:units[u]['owner']!=p,
      IsTerrainPathable=lambda *a:event.get('blocked',False),GetUnitFlyHeight=lambda u:units[u].get('height',0.),SetUnitFlyHeight=lambda u,h,r:units[u].update(height=h),BlzPauseUnitEx=lambda u,v:units[u].update(paused=v),
      RemoveSavedBoolean=lambda h,i,k:H.pop((h,i,k),None),MU_Register=lambda *a:None,
      SetUnitAbilityLevel=lambda u,a,r:units[u].setdefault('ranks',{}).update({a:r}),
      TimerStart=lambda t,d,r,f:timers[t].update(delay=d,callback=f),
      IssueTargetOrder=lambda u,o,v:(event.update(native_order=(u,o,v)) or not event.get('order_fails',False)))
tests=md[md.index('def start('):]
tests=tests.replace("check(event.get('rejected'),'Channel guard rejects hero before native Devour effect')","check(not event.get('rejected'),'Maul accepts enemy hero at public channel guard')")
tests=tests.replace("check('AMdc' in units[1]['abilities'],'Channel prepares native digestion cargo')","check(not event.get('rejected'),'Maul accepts eligible soldier at public channel guard')")
tests=tests.replace("es['AMu3']['oldId']=='Adev'","es['AMu3']['oldId']=='ANcl' and es['AMdv']['oldId']=='Adev'")
tests=tests.replace("get('AMu3','Dev1',lv)","get('AMdv','Dev1',lv)")
tests=tests.replace("R.parent/'hero-rework/src/war3map.j'","W/'stats-ui-v37/src/war3map.j'")
exec(tests)
def cast(target=2,rank=1):
    units[1].setdefault('ranks',{}).update(AMu3=rank)
    event.update(unit=1,spell='AMu3',target=target)
    env['MU_OnCast']()
def dispatch():
    t=H[6,1,1];event['timer']=t;env['MM_ExecuteDevour']();return t
for kind in ['hero','neutral_creep','owned_creep']:
    setup()
    if kind=='hero':units[2]['types']={'UNIT_TYPE_HERO'}
    elif kind=='neutral_creep':units[2]['owner']=12
    else:units[2]['skin']='nogr'
    cast(rank=4)
    check(units[2].get('paused') and (4,1,1) not in H and (6,1,1) not in H,kind+' routes only to flip')
    t=max(timers);event['timer']=t
    for _ in range(16):env['MU_FlingTick']()
    check(units[2]['x']==-200. and hits==[(1,2,140.)] and not units[2]['paused'],kind+' lands behind Mundo with rank damage and unpauses')
    check(timers[t].get('destroyed') and (2,2,39) not in H,kind+' clears flip timer and target lock')
setup();units[2]['types']={'UNIT_TYPE_HERO'};H[4,1,1]=3;cast()
check(units[2].get('paused') and H[4,1,1]==3,'Hero flip preserves current digestion meal')
for owned in [1,0]:
    setup();units[2]['owner']=owned;cast(rank=3)
    check(H.get((6,1,1)) is not None and not units[2].get('paused'),'Ordinary soldier schedules Devour (owner '+str(owned)+')')
    t=dispatch()
    check(event['native_order']==(1,'devour',2) and units[1]['ranks']['AMdc']==3 and units[1]['ranks']['AMdv']==3,'Native Devour executes on caster with matching rank')
    event.update(unit=1,spell='AMdv',target=2);env['MD_OnChannel']();env['MU_OnCast']()
    check(H[4,1,1]==2 and H[4,1,2]==3 and (6,1,1) not in H,'Native effect starts tracked digestion exactly once')
    env['MU_OnCast']();check(H[4,1,1]==2 and not event.get('rejected'),'Repeated helper effect is ignored')
    event['timer']=t;env['MM_Timeout']()
    check(not cooldowns and timers[t].get('destroyed'),'Successful digestion preserves shared Maul cooldown and frees timer')
setup();cast();t=H[6,1,1];units[1]['alive']=False;event['timer']=t;env['MM_ExecuteDevour']()
check('native_order' not in event and timers[t].get('destroyed') and (6,1,1) not in H,'Caster death before dispatch cancels and cleans pending cast')
setup();cast();units[1]['owner']=1;t=dispatch();check('native_order' not in event and timers[t].get('destroyed'),'Ownership change cancels pending Devour')
setup();cast();event['order_fails']=True;t=dispatch();check(cooldowns==[(1,'AMu3')] and timers[t].get('destroyed'),'Failed native order refunds Maul and clears timer')
setup();cast();t=dispatch();event['timer']=t;env['MM_Timeout']();check(cooldowns==[(1,'AMu3')] and (6,1,1) not in H,'Interrupted native swallow refunds Maul without digestion reward')
setup();units[2]['types']={'UNIT_TYPE_HERO'};event['blocked']=True;cast();check(not units[2].get('paused') and cooldowns==[(1,'AMu3')],'Blocked flip destination refunds shared cooldown')
for kind in ['UNIT_TYPE_MAGIC_IMMUNE','UNIT_TYPE_MECHANICAL','UNIT_TYPE_FLYING','UNIT_TYPE_STRUCTURE']:
    setup();units[2]['types']={'UNIT_TYPE_HERO',kind};cast()
    check(not timers and not units[2].get('paused') and (4,1,1) not in H,'Invalid flip target rejected: '+kind)
setup();units[2]['types']={'UNIT_TYPE_HERO'};units[2]['owner']=0;cast();check(not timers,'Allied heroes cannot be flipped or eaten')
setup();H[4,1,1]=3;cast();check(not timers and H[4,1,1]==3,'Second meal rejected without replacing digestion')
setup();units[2]['abilities'].add('AIsr');cast();check(not timers,'Spell-resistant soldiers remain ineligible for Devour')
setup();units[2]['skin']='nogr';units[2]['abilities'].add('A0IL');cast();check(not timers,'Colossals cannot bypass exclusions through creep classification')
setup();units[2]['types']={'UNIT_TYPE_HERO'};cast();t=max(timers);units[1]['alive']=False;event['timer']=t;env['MU_FlingTick']()
check(not units[2]['paused'] and timers[t].get('destroyed') and not hits,'Interrupted flip restores movement without landing damage')
for rank in range(1,7):
    check(get('AMu3','acdn',rank)==20. and get('AMu3','aran',rank)==250. and get('AMdv','acdn',rank)==0.,'Rank '+str(rank)+' uses one 20-second cooldown and 250 range')
report=dict(passed=len(results),checks=results,scope='Actual JASS translated with mocked natives and native object checks; live playtest pending')
(R/'checks.json').write_text(json.dumps(report,indent=2));print('Maul + regressions:',len(results),'passed')
