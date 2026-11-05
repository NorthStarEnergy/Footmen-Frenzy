from pathlib import Path
exec(compile((Path(__file__).resolve().parent/'check.py').read_text().split('# Differential validation')[0],'shared test helpers','exec'))
# Reused groups and per-player cleanup across two simultaneous sinkholes, including slot 12.
e={};names=[n for n in fs['main'] if (n.startswith('SoloFoots') and 'Sinkhole' in n) or n in ['Trig_HERO_Myrmidon_Sinkhole_start_Actions','Trig_HERO_Myrmidon_Sinkhole_suck_Actions','Trig_HERO_Myrmidon_Sinkhole_end_Actions']]
exec(code('main',names),e)
units={1:dict(owner=0,hero=True,x=0.,y=0.,kind='hero',alive=True),12:dict(owner=11,hero=True,x=800.,y=0.,kind='hero',alive=True),3:dict(owner=1,hero=False,x=150.,y=0.,kind='foot',alive=True),4:dict(owner=1,hero=False,x=100.,y=0.,kind='building',structure=True,alive=True),5:dict(owner=1,hero=False,x=200.,y=0.,kind='foot',alive=False)}
locs={};groups={};serial=[100];event={'player':0};enabled=[False];removed=[]
def alloc(store,v):serial[0]+=1;store[serial[0]]=v;return serial[0]
def free(store,h):assert h in store,('duplicate/unowned release',h);del store[h]
def enum_range(g,x,y,r,f):groups[g][:]=[u for u,d in units.items() if d.get('kind')!='h029' and math.hypot(d['x']-x,d['y']-y)<=r]
def enum_player(g,p,f):groups[g][:]=[u for u,d in units.items() if d['owner']==p]
def create(p,k,x,y,f):return alloc(units,dict(owner=p,kind=k,x=x,y=y,hero=False,alive=True))
e.update(udg_sinkhole_active=defaultdict(bool),udg_sinkhole_time=defaultdict(int),udg_waterfall=defaultdict(lambda:None),udg_waterfall_mid=defaultdict(lambda:None),udg_herO=defaultdict(lambda:None,{1:1,12:12}),sf_sinkhole_enum_group=alloc(groups,[]),gg_trg_HERO_Myrmidon_Sinkhole_suck=99,GetTriggerPlayer=lambda:event['player'],GetPlayerId=lambda p:p,Player=lambda p:p,GetSpellTargetLoc=lambda:alloc(locs,(0.,0.) if event['player']==0 else (800.,0.)),GetLocationX=lambda l:locs[l][0],GetLocationY=lambda l:locs[l][1],RemoveLocation=lambda l:free(locs,l),CreateGroup=lambda:alloc(groups,[]),GroupClear=lambda g:groups[g].clear(),FirstOfGroup=lambda g:groups[g][0] if groups[g] else None,GroupRemoveUnit=lambda g,u:groups[g].remove(u),GroupAddUnit=lambda g,u:groups[g].append(u),RemoveUnit=lambda u:(removed.append(u),free(units,u)),CreateUnit=create,Atan2=math.atan2,Cos=math.cos,Sin=math.sin,bj_RADTODEG=180/math.pi,bj_UNIT_FACING=0,TerrainDeformationCraterBJ=noop,EnableTrigger=lambda t:enabled.__setitem__(0,True),DisableTrigger=lambda t:enabled.__setitem__(0,False),GroupEnumUnitsInRange=enum_range,GroupEnumUnitsOfPlayer=enum_player,GetUnitTypeId=lambda u:units[u]['kind'],GetUnitAbilityLevel=lambda u,a:2,GetWidgetLife=lambda u:100 if units[u]['alive'] else 0,IsUnitType=lambda u,t:units[u].get(t,False),UNIT_TYPE_STRUCTURE='structure',UNIT_TYPE_HERO='hero',GetOwningPlayer=lambda u:units[u]['owner'],GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],SetUnitPosition=lambda u,x,y:units[u].update(x=x,y=y),I2R=float,SetUnitAbilityLevel=noop,IssueImmediateOrder=noop,PlaySoundAtPointBJ=noop,gg_snd_ThunderClapCaster=1,UnitApplyTimedLife=noop)
e['Trig_HERO_Myrmidon_Sinkhole_start_Actions']();first=set(u for u,d in units.items() if d['kind']=='h029');assert len(first)==8
# Recast replaces only owned dummies/location.
e['Trig_HERO_Myrmidon_Sinkhole_start_Actions']();assert first.isdisjoint(units) and len(locs)==1
check('Sinkhole recast cleans prior location and all eight owned dummies',True)
event['player']=11;e['Trig_HERO_Myrmidon_Sinkhole_start_Actions']();assert len(locs)==2 and enabled[0]
e['Trig_HERO_Myrmidon_Sinkhole_suck_Actions']();assert units[4]['x']==100 and units[5]['x']==200
check('Sinkhole keeps dead units and structures unaffected',True)
event['player']=0;e['Trig_HERO_Myrmidon_Sinkhole_end_Actions']();assert enabled[0] and e['udg_sinkhole_active'][12] and len(locs)==1
check('Ending one sinkhole leaves another player active',True)
for _ in range(59):e['Trig_HERO_Myrmidon_Sinkhole_suck_Actions']()
assert not enabled[0] and not locs and not any(d['kind']=='h029' for d in units.values())
assert len(groups)==3 and all(not g for g in groups.values())
check('Slot-12 sinkhole expires at 60 ticks; pooled groups remain empty and reusable',True)
# Timer cleanup is idempotent and polling stops only when everyone is idle.
for name,prefix in [('Trig_HERO_Architect_tower_countdown_Actions','tower'),('Trig_ITEM_Wall_countdown_Actions','wall')]:
 e={};exec(code('main',[name]),e);tags={1:True,2:True};times={1:2.,2:0.};disabled=[]
 timer_array='udg_timer_tower' if prefix=='tower' else 'udg_wall_timer';tag_array='udg_'+prefix+'_timer_text'
 e.update({timer_array:defaultdict(lambda:None,{1:1,2:2}),tag_array:defaultdict(lambda:None,{1:1,2:2})})
 e.update(TimerGetRemaining=lambda t:times.get(t,0.),SetTextTagTextBJ=noop,R2SW=lambda r,w,p:str(r),DestroyTextTagBJ=lambda t:free(tags,t),DisableTrigger=lambda t:disabled.append(t),GetTriggeringTrigger=lambda:99)
 e[name]();assert not disabled and e[tag_array][2] is None and 1 in tags
 e[name]();times[1]=0;e[name]();e[name]();assert not tags and disabled
 check(prefix+' timer cleanup is repeat-safe and pauses when idle',True)
# Prison expiry frees each persistent handle once, including on repeated countdown ticks.
e={};name='Trig_HERO_Prison_Wall_countdown_Actions';exec(code('main',[name]),e);tags={};locations={};blocks={};times={1:2.,12:0.};disabled=[]
e['udg_prison_timer']=defaultdict(lambda:None,{1:1,12:12})
for i in range(1,5):
 for field,store in [('wall_text',tags),('wall_point',locations),('block',blocks)]:
  a,b=alloc(store,True),alloc(store,True);e['udg_prison_'+field+'_'+str(i)]=defaultdict(lambda:None,{1:a,12:b})
e.update(TimerGetRemaining=lambda t:times.get(t,0.),SetTextTagTextBJ=noop,R2SW=lambda r,w,p:str(r),DestroyTextTagBJ=lambda t:free(tags,t),RemoveLocation=lambda l:free(locations,l),RemoveDestructable=lambda d:free(blocks,d),DisableTrigger=lambda t:disabled.append(t),GetTriggeringTrigger=lambda:99)
e[name]();assert len(tags)==len(locations)==len(blocks)==4 and not disabled
e[name]();times[1]=0;e[name]();e[name]();assert not tags and not locations and not blocks and disabled
check('Prison countdown cleans text, points and blockers once across slots 1 and 12',True)
# All candidate-only changes are source/metadata: original players, modes and objects survive byte-for-byte.
reports=json.loads((R/'migration.json').read_text())['maps']
for report in reports:
 a=c.c_void_p();b=c.c_void_p();assert storm.SFileOpenArchive(report['base'],0,256,c.byref(a));assert storm.SFileOpenArchive(report['output'],0,256,c.byref(b))
 for name in ['war3map.w3i','war3map.w3u','war3map.w3a','war3map.w3h','war3map.w3t','war3map.w3q','war3map.w3e','war3map.doo','war3mapUnits.doo']:
  assert read_storm(a,name)==read_storm(b,name),(report['variant'],name)
 assert storm.SFileCloseArchive(a) and storm.SFileCloseArchive(b)
 check(report['variant']+' player/terrain/unit/ability/item/upgrade data unchanged',True)
 old=split_functions(Path(report['base']).read_text()) if False else None
for n in fs['old']:
 if n.startswith(('Trig_MODE','InitTrig_MODE','Trig_KOTH','InitTrig_KOTH','FFMode')):assert fs['old'][n]==fs['main'][n],n
check('799X mode and KOTH implementations retained',True)
(R/'lifecycle-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'engine_playtested':False},indent=2));print(len(checks),'lifecycle and preservation groups passed')
