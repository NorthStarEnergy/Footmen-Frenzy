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
for line in ((W/'pub-xp-v67/globals.j').read_text()+'\n'+(R/'globals.j').read_text()).splitlines():
 if not line.strip():continue
 m=re.match(r'(?:constant )?\w+ (\w+) = (.*)',line)
 if m:g[m[1]]=eval(m[2].replace('false','False').replace('true','True'))
 else:
  m=re.match(r'(\w+) array (\w+)',line);assert m,line
  g[m[2]]=defaultdict(float if m[1]=='real' else lambda:None)
mode_flags=['udg_mode_pub','FFR4Pro','udg_mode_promode','FFMode4K','FFModePrivateVote','udg_mode_inhouse','udg_mode_debugmode','udg_mode_overdrive','udg_FFCH_Mode','udg_mode_no_mass','udg_colossal_on']
for flag in mode_flags:g[flag]=flag in ['udg_mode_pub','udg_colossal_on']
g.update(udg_player_active=defaultdict(bool),udg_herO=defaultdict(lambda:None),udg_maphack=defaultdict(bool),udg_colossal_wave=1)
global_names=list(g);python=[]
def expr(s):return re.sub(r'\b(null|true|false)\b',lambda m:{'null':'None','true':'True','false':'False'}[m[1]],s).replace('function ','')
for name,body in fs.items():
 if not (name.startswith('P67_') or name=='P78_Rate'):continue
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
thresholds=[0,200,500,900,1400,2000,2700,3500,4400,5400,6500]
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
def hero(slot,level,xp=None):
 u=SimpleNamespace(owner=slot-1,level=level,xp=thresholds[level-1] if xp is None else xp,hero=True,illusion=False,removed=False)
 g['udg_herO'][slot]=u;g['udg_player_active'][slot]=True;return u
checks={}
assert g['P67_Enabled']()
for flag in mode_flags:
 old=g[flag];g[flag]=not old;assert not g['P67_Enabled']();g[flag]=old
checks['mode_gates']=len(mode_flags)
reset();a=hero(1,7,3100);b=hero(2,9);leader=hero(12,9,5399);low=hero(3,6)
g['P67_Start']();g['P67_ColoSpawn']()
assert rates[0]==rates[1]==rates[11]==70 and rates[2]==200
assert not g['P78_Reached10'] and not xp_calls
# Last player slot reaches the milestone: all earlier slots must refresh in the same pass.
leader.level=10;leader.xp=5400;g['trigger_unit']=leader;g['P67_OnLevel']()
assert g['P78_Reached10'] and rates[0]==170 and rates[1]==110 and rates[11]==70 and rates[2]==200
assert not xp_calls and sum('Level 10 reached.' in x for x in messages)==1
g['P67_Refresh']();assert sum('Level 10 reached.' in x for x in messages)==1
# Removing/repicking the original leader cannot revoke the unlock.
g['udg_player_active'][12]=False;leader.level=1;g['P67_Refresh']();assert rates[0]==170
a.xp=3300;g['P67_Refresh']();assert rates[0]==160
b.level=10;b.xp=5400;g['trigger_unit']=b;g['P67_OnLevel']();assert rates[1]==70
g['udg_maphack'][1]=True;g['P67_Refresh']();assert rates[0]==25;g['udg_maphack'][1]=False
checks['activation_individual_progress_and_latch']='passed'
# Native handicap and supplemental rewards use the same current-rate helper.
a.xp=3100;g['P67_Remainder'][1]=0;g['P67_AddSupplement'](a,100.0);assert a.xp==3270
b.level=10;b.xp=5400;g['P67_AddSupplement'](b,100.0);assert b.xp==5470
assert g['P67_HeroRate'](a)==161.5
# Monotone continuous fractional curve through all level boundaries.
previous=190;count=0
for xp in range(2700,5401):
 level=7 if xp<3500 else 8 if xp<4400 else 9 if xp<5400 else 10
 r=g['P78_Rate'](level,xp,True,70.0)
 assert 70<=r<=190 and r<=previous and previous-r<=0.051
 assert g['P78_Rate'](level,xp,False,70.0)==70
 previous=r;count+=1
for level in [1,6,10,11,18]:assert g['P78_Rate'](level,0,True,123.0)==123
assert g['P78_Rate'](7,-1,True,70)==190
assert g['P78_Rate'](9,999999,True,70)==70
checks['fractional_xp_points']=count
# Only active registered non-illusion heroes may unlock the milestone.
for kind in ['inactive','illusion','removed','nonhero','unregistered']:
 reset();a=hero(1,7);fake=hero(12,10)
 if kind=='inactive':g['udg_player_active'][12]=False
 if kind=='illusion':fake.illusion=True
 if kind=='removed':fake.removed=True
 if kind=='nonhero':fake.hero=False
 if kind=='unregistered':g['udg_herO'][12]=None
 g['P67_Start']();g['trigger_unit']=fake;g['P67_OnLevel']()
 assert not g['P78_Reached10'] and rates[0]==70
# No periodic or milestone function creates XP, and disabled modes cannot unlock.
reset();hero(1,7);hero(12,10);g['FFR4Pro']=True;g['P67_Start']();assert not rates and not g['P78_Reached10'];g['FFR4Pro']=False
g['P67_Start']();g['P67_Start']();assert len(timers)==1 and not xp_calls
checks['invalid_heroes_and_disabled_modes']='passed'
for name in ['P67_Start','P67_Refresh','P67_OnLevel','P78_Rate']:
 assert 'SetHeroXP(' not in fs[name] and 'AddHeroXP' not in fs[name]
checks['no_free_xp']='passed'
(R/'checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks))
