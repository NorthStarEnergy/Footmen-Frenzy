"""Execute actual final JASS bodies with mocked natives; no engine claims."""
from pathlib import Path
from collections import defaultdict
import sys,re,ast,json,math,itertools
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import functions as split_functions,storm,read_storm,c
# Load the reusable translator definitions only (never run its historical test setup).
env={}
for node in ast.parse((W/'799x-backport/check_runtime.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'),env)
env['re']=re
scripts={}
paths={'oldsolo':Path('C:/Users/User/Documents/Warcraft III/Maps/Solo Foots/Solo Tests/Solo_Foots_v1.8_4P_799X_UPDATE08.w3x'),'old':W/'consolidated-v84/release/FF799X_Rx_Consolidated_v84_TEST.w3x','main':R/'release/FF799X_Rx_Shared_Fixes_v85_TEST.w3x','solo':R/'release/Solo_Foots_v1.8_4P_SHARED_FIXES_UPDATE09.w3x'}
for name,path in paths.items():
 h=c.c_void_p();assert storm.SFileOpenArchive(str(path),0,256,c.byref(h));scripts[name]=read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r','');assert storm.SFileCloseArchive(h)
fs={k:split_functions(v) for k,v in scripts.items()};checks=[];cases=0

def code(variant,names,generator=False):
 env['functions']=fs[variant];text='\n\n'.join(env['translate'](n) for n in names)
 text=re.sub(r'\bfunction\s+(\w+)',r'\1',text)
 lines=text.splitlines();result=[]
 for i,line in enumerate(lines):
  result.append(line)
  if line.rstrip().endswith(':') and i+1<len(lines) and len(lines[i+1])-len(lines[i+1].lstrip())<=len(line)-len(line.lstrip()):result.append(' '*(len(line)-len(line.lstrip())+4)+'pass')
 text='\n'.join(result)
 if generator:text=re.sub(r'TriggerSleepAction\s*\(\s*([\d.]+)\s*\)',r'(yield \1)',text)
 return text

def check(label,condition):
 assert condition,label
 checks.append(label)
noop=lambda *a:None
# Differential validation of all original 799X item-cap/hero-block rules.
rawcodes=sorted(set(re.findall(r"'(.{4})'",'\n'.join(f for n,f in fs['old'].items() if n.startswith('Trig_ITEM_limits')))))
heroes=rawcodes+['H043','HVg1','HMu1','HGr1','HOr1','HTf1','hfoo']

def item_env(v,combo=False):
 state={};e={};exec(code(v,[n for n in fs[v] if n.startswith(('Trig_ITEM_combo_limits','ItemCombo_','ItemLimit_') if combo else ('Trig_ITEM_limits','ItemLimit_'))]),e)
 def slot(u,i):return state['inventory'][i-1] if i<=len(state['inventory']) else None
 def drop(it,u=None):
  if it is not None and it in state['inventory']:state['removed'].append(it[0]);state['inventory'][state['inventory'].index(it)]=None
 def item(t):return next((it for it in state['inventory'] if it and it[0]==t),None)
 e.update(GetTriggerUnit=lambda:1,GetManipulatedItem=lambda:state['picked'],GetItemTypeId=lambda i:i[0] if i else '',GetTriggerPlayer=lambda:0,GetConvertedPlayerId=lambda p:p+1,ConvertedPlayer=lambda p:p-1,GetUnitTypeId=lambda u:state['hero'],UnitItemInSlotBJ=slot,UnitItemInSlot=lambda u,i:slot(u,i+1),GetItemOfTypeFromUnitBJ=lambda u,t:item(t),GetItemName=lambda i:i[0] if i else '',GetUnitName=lambda u:state['hero'],UnitRemoveItemSwapped=drop,UnitRemoveItem=lambda u,it:drop(it),RemoveItem=drop,DisplayTextToForce=lambda force,msg:state['messages'].append(msg),DisplayTextToPlayer=lambda p,x,y,msg:state['messages'].append(msg),SoloFootsDisplayMessageToPlayer=lambda p,x,y,msg:state['messages'].append(msg),GetForceOfPlayer=lambda p:p,DestroyForce=noop,DoNothing=noop,I2S=str)
 def run(t,h,count,inventory=None):
  state.update(inventory=[(x,i) if x else None for i,x in enumerate(inventory)] if inventory is not None else [(t,i) for i in range(count)],picked=(t,0),hero=h,removed=[],messages=[])
  e['Trig_ITEM_combo_limits_Actions' if combo else 'Trig_ITEM_limits_Actions']()
  return list(state['removed']),list(state['messages'])
 return run
old,new=item_env('old'),item_env('main')
for t in rawcodes+['zzzz']:
 for h in heroes:
  for count in range(1,7):
   a,b=old(t,h,count),new(t,h,count);assert a==b,(t,h,count,a,b);cases+=1
check('799X item limits preserve all tested original rejection/removal/messages',True)
oldsolo,newsolo=item_env('oldsolo'),item_env('solo')
for t in rawcodes+['zzzz']:
 for h in heroes:
  for count in range(1,7):
   a,b=oldsolo(t,h,count),newsolo(t,h,count)
   if t=='I006' and count>2:a=(a[0],[msg.replace('Only 1x','Only 2x') for msg in a[1]])
   if t=='I009' and count>2:a=(['I009'],['|cffff0000Only 2x |rI009|cffff0000 per hero allowed!|r'])
   assert a==b,(t,h,count,a,b);cases+=1
check('Solo item rules preserved except correct 2x warning and non-destructive Shockwave overflow',True)
for n in fs['oldsolo']:
 if n.startswith(('SoloFoots','SoloCam_','Trig_MODE','InitTrig_MODE','Trig_KOTH','InitTrig_KOTH','OM_','FS_','FFGS_')) or n in ['InitCustomPlayerSlots','InitCustomTeams','Trig_Start_game_Actions','Trig_set_hero_stats_Actions','Trig_set_spawn_variables_Actions']:
  assert fs['oldsolo'][n]==fs['solo'][n],n
check('Solo slots, game modes, roster, Gragus/Guldan, camera and spawn systems preserved',True)
oldcombo,newcombo=item_env('old',True),item_env('main',True)
for t in ['rag1','hval','evtl','zzzz']:
 for tail in itertools.product(['rag1','hval','evtl','zzzz',None],repeat=5):
  inv=[t]+list(tail)
  a,b=oldcombo(t,'H043',1,inv),newcombo(t,'H043',1,inv);assert a==b,(inv,a,b);cases+=1
check('Item combination rules match original for mixed six-slot inventories',True)
# Creep caps preserve all 15 rawcodes and unrestricted fast path.
e={};exec(code('old',[n for n in fs['old'] if n.startswith('Trig_limit_amount_of_creeps')]),e)
e.update(GetUnitTypeId=lambda u:u,DoNothing=noop)
z={};exec(code('main',['CreepLimit_MaxAllowed']),z)
creeps=set(re.findall(r"'(.{4})'",'\n'.join(f for n,f in fs['old'].items() if n.startswith('Trig_limit_amount_of_creeps'))))|{'zzzz'}
for t in creeps:
 for count in range(0,9):
  e.update(udg_temp_unit=t,udg_temp_int=count)
  cap=z['CreepLimit_MaxAllowed'](t);assert e['Trig_limit_amount_of_creeps_Func011C']()==(cap>0 and count>cap),(t,count,cap);cases+=1
check('Creep restriction lookup preserves original 799X cap decisions',True)
check('Observer purchase ownership fix precedes team counting',fs['main']['Trig_limit_amount_of_creeps_Actions'].index('SoloSub_ReownToSlot')<fs['main']['Trig_limit_amount_of_creeps_Actions'].index('GetOwningPlayer'))
check('Personal-shop u01C selector preserved',"'u01C'" in fs['main']['Trig_page_system_Actions'])
# Thor: real JASS executes with strict ownership mocks across ranks and terrain branches.
for rank in range(1,7):
 for walkable in [False,True]:
  e={};exec(code('main',['Trig_HERO_Thor_Powerhit_Actions']),e);locs={};serial=[0]
  def loc(x,y):serial[0]+=1;locs[serial[0]]=(x,y);return serial[0]
  def remove(l):assert l in locs,('double free',l);del locs[l]
  def polar(l,d,a):x,y=locs[l];return loc(x+d*math.cos(a*math.pi/180),y+d*math.sin(a*math.pi/180))
  e.update(GetTriggerUnit=lambda:1,GetSpellTargetUnit=lambda:2,GetOwningPlayer=lambda u:0,GetConvertedPlayerId=lambda p:p+1,GetUnitLoc=lambda u:loc(u*50,0),AngleBetweenPoints=lambda a,b:0,GetUnitAbilityLevelSwapped=lambda a,u:rank,GetSpellAbilityId=lambda:'A0ED',PolarProjectionBJ=polar,RemoveLocation=remove,SetUnitPositionLocFacingBJ=noop,AddSpecialEffectLocBJ=noop,DestroyEffectBJ=noop,GetLastCreatedEffectBJ=lambda:999,Trig_HERO_Thor_Powerhit_Func009Func005C=lambda:walkable,DoNothing=noop)
  e['Trig_HERO_Thor_Powerhit_Actions']();assert not locs,(rank,walkable,locs);assert e['udg_temp_point'] is None and e['udg_temp_point_caster'] is None;cases+=1
check('Thor Powerhit releases every allocation at every rank and terrain branch',True)
# Jaina: two overlapping casts are interleaved at actual script sleeps.
for v in ['main','solo']:
 e={};exec(code(v,['Trig_HERO_Jaina_Ulti_Actions'],True),e)
 units={1:{'owner':0},2:{'owner':1}};event={'caster':1};locs={};groups={};seq=[100];created=[];removed=[];orders=[]
 def handle(store,value):seq[0]+=1;store[seq[0]]=value;return seq[0]
 def create(n,kind,p,pt,face):
  u=handle(units,{'owner':p,'kind':kind});event['last']=u;created.append(u)
 def free(store,h):assert h in store,('invalid cleanup',h);del store[h]
 def order(u,*args):assert u in units;orders.append((u,units[u]['owner'],args));return True
 e.update(GetTriggerUnit=lambda:event['caster'],GetOwningPlayer=lambda u:units[u]['owner'],GetSpellTargetLoc=lambda:handle(locs,(0,0)),GetUnitAbilityLevelSwapped=lambda a,u:3,PolarProjectionBJ=lambda l,d,a:handle(locs,(d,a)),CreateNUnitsAtLoc=create,bj_UNIT_FACING=0,GetLastCreatedUnit=lambda:event['last'],RemoveLocation=lambda l:free(locs,l),udg_orb=defaultdict(lambda:None),UnitAddAbilityBJ=noop,SetUnitAbilityLevelSwapped=noop,IssueImmediateOrderBJ=order,IssuePointOrderLocBJ=order,GetUnitLoc=lambda u:handle(locs,(u,0)),Condition=lambda f:f,Trig_HERO_Jaina_Ulti_Func030003001003=lambda:True,GetUnitsInRangeOfLocMatching=lambda *a:handle(groups,[1]),GroupPickRandomUnit=lambda g:groups[g][0],IssueTargetOrderBJ=order,DestroyGroup=lambda g:free(groups,g),RemoveUnit=lambda u:(removed.append(u),free(units,u)))
 a=e['Trig_HERO_Jaina_Ulti_Actions']();assert next(a)==1
 first=list(created);event['caster']=2;b=e['Trig_HERO_Jaina_Ulti_Actions']();assert next(b)==1
 second=[u for u in created if u not in first]
 assert next(a)==1;assert next(b)==1;assert next(a)==2;assert next(b)==2
 try:next(a)
 except StopIteration:pass
 assert all(u in units for u in second) and all(u not in units for u in first)
 try:next(b)
 except StopIteration:pass
 assert sorted(removed)==sorted(created) and not locs and not groups
 check(v+' Jaina simultaneous casts keep separate orbs and clean all handles',True)
# Alchemist uses the actual caster, while preserving each variant's bounty-dice rule.
for v,dice in [('main',0),('solo',8)]:
 e={};exec(code(v,['FFR9_ApplyAlchemistBounty']),e);writes={}
 e.update(UNIT_TYPE_HERO='hero',UNIT_IF_GOLD_BOUNTY_AWARDED_BASE='base',UNIT_IF_GOLD_BOUNTY_AWARDED_NUMBER_OF_DICE='dice',UNIT_IF_GOLD_BOUNTY_AWARDED_SIDES_PER_DIE='sides',IsUnitType=lambda u,t:u==7,GetUnitAbilityLevel=lambda u,a:1,GetHeroLevel=lambda u:12,udg_hero_bounty_base={12:321},BlzSetUnitIntegerField=lambda u,k,val:writes.update({k:val}))
 e['FFR9_ApplyAlchemistBounty'](7);assert writes=={'base':321,'dice':dice,'sides':3 if dice else 0}
 e['FFR9_ApplyAlchemistBounty'](None);e['FFR9_ApplyAlchemistBounty'](5)
 check(v+' Alchemist correct caster level and preserved dice rules',True)
# Ensure specialized mainline features and mode/player configuration functions were not changed.
for n in fs['old']:
 if n.startswith(('VG','P67_','P78_','P79_','P80_','LX_','ST_','MU_','MW_','MC_','DK_','OM_','FS_','FFMode','SoloSub_')) or n in ['config','InitCustomPlayerSlots','InitCustomTeams','Trig_Start_game_Actions','Trig_set_hero_stats_Actions','Trig_set_spawn_variables_Actions','FFGS_InitSettings']:
  assert fs['old'][n]==fs['main'][n],n
check('799X custom heroes, rewards, balance, observer substitutions and game-mode/player functions preserved',True)
report={'assertion_groups':len(checks),'differential_and_rank_cases':cases,'checks':checks,'engine_playtested':False}
(R/'behavior-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
