"""Execute edited JASS helpers with mocked natives; engine ordering still needs playtest."""
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
import json,re,struct,sys
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import functions
script=(R/'src/war3map.j').read_text(encoding='utf8');fs=functions(script)
manifest=json.loads((R/'changes.json').read_text())
w=(R/'src/war3map.wct').read_bytes();p=w.index(0,8)+1;chunks=[]
while p<len(w):
 n=struct.unpack_from('<I',w,p)[0];p+=4;chunks.append(w[p:p+n].rstrip(b'\0').decode('utf-8-sig').replace('\r',''));p+=n
efs=functions('\n'.join(chunks))
for n in manifest['changed_functions']+manifest['added_functions']:assert efs[n]==fs[n],n
for line in (R/'globals.j').read_text().splitlines():assert line in script and line in '\n'.join(chunks)
g={}
for line in ((W/'pub-xp-v67/globals.j').read_text()+'\n'+(W/'level10-catchup-v78/globals.j').read_text()+'\n'+(R/'globals.j').read_text()).splitlines():
 if not line.strip():continue
 m=re.match(r'(?:constant )?\w+ (\w+) = (.*)',line)
 if m:g[m[1]]=eval(m[2].replace('false','False').replace('true','True').replace('null','None'))
 else:
  m=re.match(r'(\w+) array (\w+)',line);assert m,line
  g[m[2]]=defaultdict({'real':float,'integer':int,'boolean':bool}.get(m[1],lambda:None))
mode_flags=['udg_mode_pub','FFR4Pro','udg_mode_promode','FFMode4K','FFModePrivateVote','udg_mode_inhouse','udg_mode_debugmode','udg_mode_overdrive','udg_FFCH_Mode','udg_mode_no_mass','udg_colossal_on']
for flag in mode_flags:g[flag]=flag in ['udg_mode_pub','udg_colossal_on']
g.update(udg_player_active=defaultdict(bool),udg_herO=defaultdict(lambda:None),udg_maphack=defaultdict(bool),udg_colossal_wave=1)
global_names=list(g);python=[]
def expr(s):return re.sub(r'\b(null|true|false)\b',lambda m:{'null':'None','true':'True','false':'False'}[m[1]],s).replace('function ','')
for name,body in fs.items():
 if not (name.startswith('P67_') or name=='P78_Rate' or name.startswith('P79_')):continue
 lines=body.splitlines();params=re.search(r'takes (.*?) returns',lines[0])[1]
 params=[] if params=='nothing' else [s.strip().split()[1] for s in params.split(',')]
 python+=['def '+name+'('+','.join(params)+'):', '    global '+','.join(global_names)];depth=1
 for raw in lines[1:-1]:
  line=raw.split('//')[0].strip()
  if not line:continue
  if line in ['endif','endloop']:depth-=1;continue
  if line=='else':depth-=1;python.append('    '*depth+'else:');depth+=1;continue
  if line.startswith('local '):
   parts=line.split(None,2);translated=parts[2] if '=' in parts[2] else parts[2]+' = None'
  elif line.startswith('set '):translated=line[4:]
  elif line.startswith('call '):translated=line[5:]
  elif line.startswith('if ') and line.endswith(' then'):translated=line[:-5]+':'
  elif line=='loop':translated='while True:'
  elif line.startswith('exitwhen '):translated='if '+line[9:]+': break'
  elif line.startswith('return'):translated=line
  else:raise AssertionError(line)
  python.append('    '*depth+expr(translated))
  if line=='loop' or (line.startswith('if ') and line.endswith(' then')):depth+=1
 assert depth==1,name
rates={};xp_calls=[];messages=[];timers=[]
g.update(UNIT_TYPE_HERO=1,GetUnitTypeId=lambda u:0 if u is None or u.removed else 1,
 IsUnitType=lambda u,t:u.hero,IsUnitIllusion=lambda u:u.illusion,
 GetOwningPlayer=lambda u:u.owner,GetPlayerId=lambda p:p,GetHeroLevel=lambda u:u.level,
 GetHeroXP=lambda u:u.xp,Player=lambda p:p,R2I=int,I2R=float,RMaxBJ=max,RMinBJ=min,
 SetPlayerHandicapXPBJ=lambda p,r:rates.__setitem__(p,r),GetPlayersAll=lambda:None,
 DisplayTextToForce=lambda _,s:messages.append(s),CreateTimer=lambda:object(),
 TimerStart=lambda *args:timers.append(args),GetTriggerUnit=lambda:g.get('trigger_unit'))
thresholds=[50*l*(l+1)-100 for l in range(1,20)]
def set_xp(u,amount,eye):
 xp_calls.append(amount-u.xp);old=u.level;u.xp=amount
 u.level=max(i+1 for i,t in enumerate(thresholds) if amount>=t)
 if u.level!=old:
  g['trigger_unit']=u;g['P67_OnLevel']()
g['SetHeroXP']=set_xp
exec('\n'.join(python),g)
def reset():
 for n in ['P67_Running','P67_Reached4','P67_Reached6','P67_MassEnded','P67_FirstColo','P78_Reached10']:g[n]=False
 for n in ['udg_player_active','udg_herO','udg_maphack','P67_Remainder','P67_LastHero']:g[n].clear()
 rates.clear();xp_calls.clear();messages.clear();timers.clear()
class Unit(SimpleNamespace):
    def __eq__(self,other):return self is other
    def __ne__(self,other):return self is not other
def hero(slot,level,xp=None):
    u=Unit(owner=slot-1,level=level,xp=thresholds[level-1] if xp is None else xp,hero=True,illusion=False,removed=False,alive=True,near=True)
    g['udg_herO'][slot]=u;g['udg_player_active'][slot]=True;return u

# In-memory mocks execute the actual tag/death/deferred-payment code.
g.update(udg_teamnumber=defaultdict(int,{pn:(pn-1)//3+1 for pn in range(1,13)}),udg_force_defeat=defaultdict(bool),IMinBJ=min,IMaxBJ=max,now=0.0,EVENT_PLAYER_UNIT_DEATH=1)
pending=[];timer_data={};destroyed=[]
def start_timer(t,duration,repeat,callback):
 timer_data[id(t)]=(g['now'],duration,repeat,callback)
 if duration==0:pending.append((t,callback))
def flush():
 while pending:
  t,callback=pending.pop(0);g['expired_timer']=t;callback()
def save(table,key,child,value):table[key,child]=value
def drop(table,key):
 for k in list(table):
  if k[0]==key:del table[k]
g.update(TimerStart=start_timer,TimerGetElapsed=lambda t:g['now']-timer_data[id(t)][0],GetHandleId=id,
 GetExpiredTimer=lambda:g['expired_timer'],DestroyTimer=lambda t:destroyed.append(t),InitHashtable=dict,
 LoadInteger=lambda t,k,c:t.get((k,c),0),LoadUnitHandle=lambda t,k,c:t.get((k,c)),
 SaveInteger=lambda t,k,c,v:save(t,k,c,int(v)),SaveUnitHandle=save,FlushChildHashtable=drop,
 CreateTrigger=lambda:object(),TriggerRegisterAnyUnitEventBJ=lambda *a:None,TriggerAddAction=lambda *a:None,
 GetKillingUnit=lambda:g.get('killer'),GetUnitLevel=lambda u:u.level,IsUnitAliveBJ=lambda u:u.alive,
 IsUnitInRange=lambda u,v,d:u.near)
def fresh():
 reset();g['now']=0;pending.clear();timer_data.clear();destroyed.clear()
 g['P79_Clock']=None;g['P79_Table']=None;g['udg_force_defeat'].clear()
 for n in ['P79_Hero','P79_Target','P79_Waiting','P79_Active','P79_Since','P79_WaveBonus','P79_WaveCap']:g[n].clear()
 for flag in mode_flags:g[flag]=flag in ['udg_mode_pub','udg_colossal_on']
def field(target=10,lag=7):
 fresh();a=hero(1,lag);b=hero(2,lag);c=hero(3,target)
 for pn in [4,5,6,7,8,9]:hero(pn,target if pn in [4,5,7,8] else target-2)
 g['P67_Start']();return a,b,c
def advance(seconds):g['now']=seconds;g['P67_Refresh']()
def kill(wave=3,level=10,killer=None,tagged=True):
 u=SimpleNamespace(level=level)
 if tagged:g['P79_Tag'](u,wave)
 g['trigger_unit']=u;g['killer']=killer or g['udg_herO'][1]
 g['P79_OnDeath']();return u
checks={}
# Thresholds and native creep XP math match known values.
assert [g['P79_LevelXP'](x) for x in [7,10,13,16]]==[2700,5400,9000,13500]
assert [g['P79_NextTarget'](x) for x in [7,10,13,16]]==[10,13,16,0]
# Strict majority in two OTHER teams; no solitary fed carrier or own-team trigger.
a,b,c=field();assert g['P79_FieldAhead'](1,10)
g['udg_herO'][8].level=8;assert not g['P79_FieldAhead'](1,10)
advance(100);assert not g['P79_Active'][1]
g['udg_herO'][8].level=10;advance(101);advance(190.99);assert not g['P79_Active'][1]
advance(191);assert g['P79_Active'][1] and not xp_calls
g['udg_force_defeat'][3]=True;advance(192);assert g['P79_Active'][1]
# One remaining opponent represents the field; with two opponents, both must lead.
hero(10,9);advance(193);assert not g['P79_Active'][1]
checks['two_opposing_majorities_and_continuous_90s']='passed'
# Exact deficit uses fractional levels, and falling under a full level during
# the wait cancels activation. Once active, tapering continues to the target.
a,b,c=field(lag=9);a.xp=4500;advance(100);assert not g['P79_Active'][1]
a.xp=4400;advance(101);advance(191);assert g['P79_Active'][1]
a.xp=4900;advance(192);assert g['P79_Active'][1]
a.xp=5400;a.level=10;advance(193);assert not g['P79_Active'][1] and g['P79_Target'][1]==13
checks['fractional_entry_and_individual_exit']='passed'
# Every milestone uses the same delayed rule and changes target individually.
for target,lag in [(10,7),(13,10),(16,13)]:
 a,b,c=field(target,lag);advance(89.999);assert not g['P79_Active'][1]
 advance(90);assert g['P79_Active'][1] and g['P79_Target'][1]==target
 old=a.xp;kill(wave=3,level=10);assert a.xp==old
 flush();assert a.xp==old+113 and c.xp==thresholds[target-1]
 assert not g['P79_Table'],'Unit and timer records must be released'
checks['10_13_16_and_deferred_colo_only_awards']='passed'
# A wave budget is fixed at the first processed eligible kill, shared across
# center/enemy packs and kept for that wave even if the next wave has spawned.
a,b,c=field();advance(90)
for _ in range(12):kill(wave=3);flush()
assert g['P79_WaveBonus'][49]==400 and a.xp==3100
before=a.xp;kill(wave=3);flush();assert a.xp==before
kill(wave=4);flush();assert a.xp>before
assert g['P79_WaveBonus'][49]==400 and g['P79_WaveBonus'][65]<=400
checks['half_level_budget_per_spawn_wave']='passed'
# Normal XP applied before deferred payment shrinks the bonus; it cannot push
# a hero above the milestone, and crossing it naturally cancels the award.
a,b,c=field(lag=9);advance(90);a.xp=5399
kill();set_xp(a,5400,True);flush();assert a.xp==5400
a,b,c=field(lag=9);advance(90);a.xp=5399
kill(level=100);flush();assert a.xp<=5400
checks['live_shortfall_and_no_bonus_overshoot']='passed'
# Nearby live allies share the base, including advanced allies. Dead/distant,
# invalid, enemy and untagged recipients do not collect this bonus.
a,b,c=field();advance(90);a.near=False;b.alive=False
before=(a.xp,b.xp);kill();flush();assert (a.xp,b.xp)==before
a.near=True;b.alive=True
kill(tagged=False);flush();assert (a.xp,b.xp)==before
kill();old=a;hero(1,7);flush();assert g['udg_herO'][1].xp==2700 and old.xp==2700
checks['participation_identity_and_no_untagged_awards']='passed'
# Consume each unit's tag exactly once, including invalid kills.
a,b,c=field();advance(90);u=kill();flush();before=a.xp
g['trigger_unit']=u;g['P79_OnDeath']();flush();assert a.xp==before
g['udg_maphack'][1]=True;advance(91);kill();flush();assert a.xp==before
g['FFR4Pro']=True;kill();flush();assert a.xp==before
checks['duplicates_anticheat_and_mode_exclusions']='passed'
# Pure payout caps over diverse deficits, group sizes, budgets and shortfalls.
cases=0
for base in [25,115,340,1000]:
 for sharers in [0,1,2,3,6]:
  for gap in [0,.1,.5,1,2.5,6]:
   for missing in [0,1,100,5000]:
    for allowance in [0,1,400,1000]:
     amount=g['P79_Extra'](base,sharers,gap,missing,allowance)
     assert 0<=amount<=min(missing,allowance)
     if sharers:assert amount<=int(base/sharers)
     else:assert amount==0
     cases+=1
checks['payout_cap_cases']=cases
assert fs['Trig_colossal_spawn_Actions'].count('call P79_Tag(udg_spawned_colo, udg_colossal_wave)')==3
assert 'call P79_Refresh()' in fs['P67_Refresh']
(R/'checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
