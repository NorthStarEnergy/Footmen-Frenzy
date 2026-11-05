"""Execute edited JASS helpers with mocked natives; engine ordering still needs playtest."""
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
import json,re,struct,sys
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import functions
script=(R/'src/war3map.j').read_text(encoding='utf8');fs=functions(script)
manifest=json.loads((W/'fed-rewards-v80/changes.json').read_text())
w=(R/'src/war3map.wct').read_bytes();p=w.index(0,8)+1;chunks=[]
while p<len(w):
 n=struct.unpack_from('<I',w,p)[0];p+=4;chunks.append(w[p:p+n].rstrip(b'\0').decode('utf-8-sig').replace('\r',''));p+=n
efs=functions('\n'.join(chunks))
for n in manifest['changed_functions']+manifest['added_functions']:assert efs[n]==fs[n],n
for line in (W/'fed-rewards-v80/globals.j').read_text().splitlines():assert line in script and line in '\n'.join(chunks)
g={}
for path in ['pub-xp-v67/globals.j','level10-catchup-v78/globals.j','colo-lag-v79/globals.j','fed-rewards-v80/globals.j']:
 for line in (W/path).read_text().splitlines():
  if not line.strip():continue
  m=re.match(r'(?:constant )?\w+ (\w+) = (.*)',line)
  if m:g[m[1]]=eval(m[2].replace('false','False').replace('true','True').replace('null','None'))
  else:
   m=re.match(r'(\w+) array (\w+)',line);assert m,line
   g[m[2]]=defaultdict({'real':float,'integer':int,'boolean':bool}.get(m[1],lambda:None))
for n in ['udg_player_active','udg_maphack','udg_force_defeat']:g[n]=defaultdict(bool)
g['udg_herO']=defaultdict(lambda:None);g['udg_teamnumber']=defaultdict(int)
flags=['udg_mode_pub','FFR4Pro','udg_mode_promode','FFMode4K','FFModePrivateVote','udg_mode_inhouse','udg_mode_debugmode','udg_mode_overdrive','udg_FFCH_Mode','udg_mode_no_mass','udg_colossal_on']
for n in flags:g[n]=n in ['udg_mode_pub','udg_colossal_on']
global_names=list(g);python=[]
def expr(s):return re.sub(r'\b(null|true|false)\b',lambda m:{'null':'None','true':'True','false':'False'}[m[1]],s).replace('function ','')
for name,body in fs.items():
 if not (name.startswith('P67_') or name=='P78_Rate' or name.startswith('P79_') or name.startswith('P80_')):continue
 lines=body.splitlines();params=re.search(r'takes (.*?) returns',lines[0])[1]
 params=[] if params=='nothing' else [s.strip().split()[1] for s in params.split(',')]
 python+=['def '+name+'('+','.join(params)+'):', '    global '+','.join(global_names)];depth=1
 for raw in lines[1:-1]:
  line=raw.split('//')[0].strip()
  if not line:continue
  if line in ['endif','endloop']:depth-=1;continue
  if line.startswith('elseif '):
   depth-=1;python.append('    '*depth+expr('elif '+line[7:-5]+':'));depth+=1;continue
  if line=='else':depth-=1;python.append('    '*depth+'else:');depth+=1;continue
  if line.startswith('local '):
   parts=line.split(None,2);translated=parts[2] if '=' in parts[2] else parts[2]+' = None'
  elif line.startswith('set '):translated=line[4:]
  elif line.startswith('call '):translated=line[5:]
  elif line.startswith('if ') and line.endswith(' then'):translated=line[:-5]+':'
  elif line=='loop':translated='while True:'
  elif line.startswith('exitwhen '):translated='if '+line[9:]+': break'
  elif line.startswith('return'):translated=line.replace('(5 * level * level + 15 * level + 30) / 2','(5 * level * level + 15 * level + 30) // 2')
  else:raise AssertionError(line)
  python.append('    '*depth+expr(translated))
  if line=='loop' or (line.startswith('if ') and line.endswith(' then')):depth+=1
 assert depth==1,name

class Unit(SimpleNamespace):
 def __eq__(self,other):return self is other
 def __ne__(self,other):return self is not other
 def __hash__(self):return id(self)
states=defaultdict(int);rates={};awards=[];triggers=[];dice_rolls=[];tags=[]
def unit(owner=0,level=1,hero=False,**kw):
 d=dict(owner=owner,level=level,xp=max(0,50*level*(level+1)-100),hero=hero,alive=True,illusion=False,structure=False,summoned=False,removed=False,suspended=False,locust=False,x=0.,y=0.,base=100,dice=0,sides=0,attacks=1)
 d.update(kw);return Unit(**d)
def primary(pn,level,**kw):
 u=unit(pn-1,level,True,**kw);g['udg_herO'][pn]=u;g['udg_player_active'][pn]=True;return u
def put(table,parent,child,value):table[parent,child]=value;return True
def clear(table,parent):
 for k in list(table):
  if k[0]==parent:del table[k]
def team(p):return g['udg_teamnumber'][p+1] if 0<=p<12 else p+10
def set_xp(u,x,show):
 awards.append((u,x-u.xp));u.xp=x;old=u.level;u.level=min(18,max(l for l in range(1,20) if x>=max(0,50*l*(l+1)-100)))
 if u.level!=old:g['trigger']=u;g['P67_OnLevel']()
def create_trigger():
 t=object();triggers.append(t);return t
def roll(a,b):dice_rolls.append((a,b));return a
g.update(UNIT_TYPE_HERO='hero',UNIT_TYPE_STRUCTURE='structure',UNIT_TYPE_SUMMONED='summoned',
 UNIT_IF_GOLD_BOUNTY_AWARDED_BASE='base',UNIT_IF_GOLD_BOUNTY_AWARDED_NUMBER_OF_DICE='dice',UNIT_IF_GOLD_BOUNTY_AWARDED_SIDES_PER_DIE='sides',UNIT_WEAPON_BF_ATTACKS_ENABLED='attacks',
 PLAYER_STATE_RESOURCE_GOLD='gold',PLAYER_STATE_GIVES_BOUNTY='bounty',EVENT_PLAYER_UNIT_DEATH=1,
 GetUnitTypeId=lambda u:0 if u is None or u.removed else 1,IsUnitType=lambda u,t:getattr(u,t),IsUnitIllusion=lambda u:u.illusion,
 GetOwningPlayer=lambda u:u.owner,GetPlayerId=lambda p:p,Player=lambda p:p,GetHeroLevel=lambda u:u.level,GetUnitLevel=lambda u:u.level,GetHeroXP=lambda u:u.xp,
 IsUnitEnemy=lambda u,p:team(u.owner)!=team(p),IsUnitAlly=lambda u,p:team(u.owner)==team(p),IsUnitAliveBJ=lambda u:u.alive,IsSuspendedXP=lambda u:u.suspended,
 GetUnitX=lambda u:u.x,GetUnitY=lambda u:u.y,GetUnitAbilityLevel=lambda u,a:int(u.locust),BlzGetUnitIntegerField=lambda u,f:getattr(u,f),BlzGetUnitWeaponBooleanField=lambda u,f,i:bool(u.attacks),
 RMinBJ=min,RMaxBJ=max,I2R=float,R2I=int,I2S=str,SetHeroXP=set_xp,
 SetPlayerHandicapXPBJ=lambda p,r:rates.__setitem__(p,r),GetPlayerState=lambda p,f:states[p,f],SetPlayerState=lambda p,f,v:states.__setitem__((p,f),v),
 GetTriggerUnit=lambda:g['trigger'],GetKillingUnit=lambda:g['killer'],GetDyingUnit=lambda:g['victim'],GetRandomInt=roll,
 InitHashtable=dict,SaveUnitHandle=put,SaveReal=put,SaveBoolean=put,LoadUnitHandle=lambda t,p,c:t.get((p,c)),LoadReal=lambda t,p,c:t.get((p,c),0.),LoadBoolean=lambda t,p,c:t.get((p,c),False),FlushChildHashtable=clear,
 CreateTrigger=create_trigger,TriggerRegisterAnyUnitEventBJ=lambda *a:None,TriggerAddAction=lambda *a:None,
 GetPlayersAll=lambda:None,DisplayTextToForce=lambda *a:None,CreateTextTag=lambda:object(),GetLocalPlayer=lambda:0)
for n in ['SetTextTagText','SetTextTagPosUnit','SetTextTagColor','SetTextTagVelocity','SetTextTagPermanent','SetTextTagLifespan','SetTextTagFadepoint','SetTextTagVisibility']:g[n]=lambda *a:None
exec('\n'.join(python),g)
# v79 has its own comprehensive verifier; isolate its periodic state from these tests.
g['P79_Refresh']=lambda:None
def reset():
 for n,v in list(g.items()):
  if isinstance(v,defaultdict):v.clear()
 for n in ['P67_Running','P67_Reached4','P67_Reached6','P67_MassEnded','P67_FirstColo','P78_Reached10','P80_Running','P80_Initialized']:g[n]=False
 g['P80_Rewards']=None;g['P80_Sequence']=0
 for n in flags:g[n]=n in ['udg_mode_pub','udg_colossal_on']
 for pn in range(1,13):g['udg_teamnumber'][pn]=(pn-1)//3+1
 states.clear();rates.clear();awards.clear();triggers.clear();dice_rolls.clear()
 for p in range(12):states[p,'bounty']=1

def start():
 g['P80_Start']();g['P67_Running']=True;g['P67_Refresh']()
def death(v,k):
 g['trigger']=v;g['victim']=v;g['killer']=k;v.alive=False;g['P80_OnDeath']()

tests=[]
def check(name,condition):assert condition,name;tests.append(name)
reset()
curve=g['P80_Curve']
for lead,expected in [(0,1),(1,1),(2,.85),(3,.7),(4,.55),(5,.4),(8,.4)]:
 check('curve lead '+str(lead),abs(curve(10,10-lead)-expected)<1e-8)
check('below seven exempt',curve(6.99,1)==1)
check('no baseline exempt',curve(18,0)==1)
cases=0
for i in range(70,181):
 prev=0.
 for j in range(10,181):
  value=curve(i/10,j/10);assert .4-1e-8<=value<=1 and value>=prev-1e-8;prev=value;cases+=1
check('all hero XP table entries',[g['P80_BaseXP'](l,True) for l in range(1,19)]==[100,120,160,220,300,400,500,600,700,800,900,1000,1100,1200,1400,1800,2000,2200])
check('normal XP recurrence',[g['P80_BaseXP'](l,False) for l in range(1,11)]==[25,40,60,85,115,150,190,235,285,340])
reset();fed=primary(1,10);ally=primary(2,7);weak=primary(4,7);start()
check('native rewards suppressed',all(rates[p]==0 and states[p,'bounty']==0 for p in range(12)))
g['P80_Start']();check('idempotent startup',len(triggers)==1)
check('fed factor',abs(g['P80_Factor'](fed,weak)-.7)<1e-8)
check('lower ally protected',g['P80_Factor'](ally,weak)==1)
weak.alive=False;check('dead hero still baseline',abs(g['P80_Factor'](fed,weak)-.7)<1e-8);weak.alive=True
check('structures exempt',g['P80_Factor'](fed,unit(3,structure=True))==1)
check('neutral exempt',g['P80_Factor'](fed,unit(12))==1)
strong=primary(5,11);check('strong hero on weak team exempt',g['P80_Factor'](fed,strong)==1)
g['udg_player_active'][5]=False
# Snapshot sharing: level 10 gets 70% existing rate * 70% anti-farm;
# level 7 ally gets its full 190% catch-up. Base XP for level 2 is 40.
f0=fed.xp;a0=ally.xp;death(unit(3,2),fed)
check('per recipient XP discount',(fed.xp-f0,ally.xp-a0)==(9,38))
check('gold discount',states[0,'gold']==70)
check('temporary reward rows cleaned',not g['P80_Rewards'])
# Army/summon/dummy kill ownership does not bypass the owner's penalty.
reset();fed=primary(1,10);weak=primary(4,7);start();f0=fed.xp
victim=unit(3,2,summoned=True,dice=2,sides=3);death(victim,unit(0,summoned=True))
check('summon XP modifier and ownership',fed.xp-f0==14)
check('authored bounty dice',dice_rolls==[(1,3),(1,3)] and states[0,'gold']==71)
# Hero victims use their level XP table and raise baseline individually.
reset();fed=primary(1,10);weak=primary(4,7);start();f0=fed.xp;death(weak,fed)
check('hero kill discount',abs((fed.xp-f0)+g['P80_XPRemainder'][1]-245)<1e-8 and states[0,'gold']==70)
# No nearby heroes => global allied sharing; nearby hero suppresses distant share.
reset();fed=primary(1,10,x=3000);ally=primary(2,7,x=4000);weak=primary(4,7);start();f0=fed.xp;a0=ally.xp;death(unit(3,2),unit(0))
check('global allied XP fallback',(fed.xp-f0,ally.xp-a0)==(9,38))
reset();fed=primary(1,10,x=3000);ally=primary(2,7,x=1200);weak=primary(4,7);start();f0=fed.xp;a0=ally.xp;death(unit(3,2),unit(0))
check('range boundary and distant exclusion',(fed.xp-f0,ally.xp-a0)==(0,76))
# No max-level XP drain, dead or suspended recipients.
for kind in ['max','dead','suspended','illusion','removed','inactive']:
 reset();fed=primary(1,10);excluded=primary(2,18 if kind=='max' else 7);weak=primary(4,7)
 if kind=='dead':excluded.alive=False
 if kind in ['suspended','illusion','removed']:setattr(excluded,kind,True)
 if kind=='inactive':g['udg_player_active'][2]=False
 start();f0=fed.xp;e0=excluded.xp;death(unit(3,2),unit(0))
 check('excluded recipient '+kind,fed.xp-f0==19 and excluded.xp==e0)
# Enemy structures with attacks give XP; structures doing the killing do not.
for victim_structure,attacks,killer_structure,expected in [(True,1,False,28),(True,0,False,0),(False,1,True,0)]:
 reset();fed=primary(1,10);weak=primary(4,7);start();f0=fed.xp
 death(unit(3,2,structure=victim_structure,attacks=attacks),unit(0,structure=killer_structure))
 check('building XP rules '+str((victim_structure,attacks,killer_structure)),fed.xp-f0==expected)
# Neutral XP full rate; native neutral gold not duplicated.
reset();fed=primary(1,10);weak=primary(4,7);start();f0=fed.xp;death(unit(12,2),fed)
check('colo neutral XP unchanged',fed.xp-f0==28)
check('no duplicate neutral bounty',states[0,'gold']==0)
# Allied kills, environmental deaths and illusions cannot create payouts.
for victim,killer in [(unit(0),unit(0)),(unit(3),None),(unit(3,illusion=True),unit(0))]:
 reset();fed=primary(1,10);weak=primary(4,7);start();f0=fed.xp;death(victim,killer)
 check('invalid kill excluded '+str(len(tests)),fed.xp==f0 and states[0,'gold']==0)
# Scripted supplements receive the same reduction exactly once.
reset();fed=primary(1,10);weak=primary(4,7);start();f0=fed.xp
g['P67_AddSupplement'](fed,100.,weak);check('scripted supplement scaled once',fed.xp-f0==49)
g['udg_maphack'][1]=True;f0=fed.xp;expected=10*g['P80_Factor'](fed,weak);death(unit(3,2),fed);check('anti-cheat retained',abs((fed.xp-f0)+g['P80_XPRemainder'][1]-expected)<1e-8)
# All recipients use pre-award rates even if another hero unlocks level 10.
reset();first=primary(1,9,xp=5399);second=primary(2,7);weak=primary(4,9);start();s0=second.xp;death(unit(12,2),unit(0))
check('same kill snapshot rates',first.level==10 and second.xp-s0==14)
# Payout fractions survive many small bounties without exceeding nominal cap.
reset();fed=primary(1,18);weak=primary(4,7);start()
check('fractional gold accumulates',sum(g['P80_Gold'](0,weak,1) for _ in range(100))==40)
# Runtime mode changes restore native payouts; re-entry doesn't register twice.
g['udg_mode_pub']=False;g['P67_Refresh']();check('mode exit restores native',not g['P80_Running'] and all(states[p,'bounty']==1 and rates[p]==100 for p in range(12)))
g['udg_mode_pub']=True;g['P67_Refresh']();check('mode reentry single handler',g['P80_Running'] and len(triggers)==1)
for flag in flags:
 reset();g[flag]=flag not in ['udg_mode_pub','udg_colossal_on'];g['P80_Start']()
 check('mode gate '+flag,not g['P80_Running'] and not triggers and all(states[p,'bounty']==1 for p in range(12)))
check('reward registration precedes other runtime triggers',fs['InitTrig_FF_Runtime'].splitlines()[1].strip()=='call P80_Init()')
# Identity reset prevents handing accumulated fractions to a replacement hero.
reset();fed=primary(1,10);weak=primary(4,7);start();death(unit(3,1),unit(0));new=primary(1,10);f0=new.xp;death(unit(3,1),unit(0))
check('repick XP fractions reset',new.xp-f0==12)
result=dict(assertions=len(tests),curve_cases=cases,checks=tests,engine_playtested=False)
(R/'checks.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
