"""Execute packaged King-mode JASS with stateful native mocks and adversarial scenarios.

This validates control flow and invariants, not Warcraft rendering/network behavior.
"""
from pathlib import Path
import re,collections,math,json,random
R=Path(__file__).resolve().parent;s=(R/'roundtrip/war3map.j').read_text()
helper=(R.parent/'ffa-v4/verify_behavior.py').read_text()
exec(helper[helper.index('def translate('):helper.index("translated='")])
names=set(re.findall(r'^function (SK\w+|S8Player|S8Team) ',s,re.M))
names|={'SF_Initialize','SF_RevealEliminated','Trig_player_destroyed_Actions','Trig_player_leaves_Actions','Trig_END_Actions','Trig_Multiboard_Update_Actions','Trig_KD_Actions','F8_UpdateBoard','Trig_Multiboard_Create_with_KOTH_Actions'}
code='\n\n'.join(translate(n) for n in sorted(names)).replace('payout/count','payout//count')
(R/'king-translated.py').write_text(code)
slots=[0,4,7,11,1,3,6,9];players=[p+1 for p in slots]
glob=re.search(r'^globals\s*$(.*?)^endglobals',s,re.M|re.S)[1]
class World:
 def __init__(self,active=players,king=True):
  e=self.e={};self.units=[];self.alliances={};self.fog=[];self.messages=[];self.winners=[];self.gold=collections.defaultdict(int);self.tech={};self.timers=[];self.board={};self.scheduled=[]
  for typ,array,name in re.findall(r'^\s*(?:constant )?(\w+)\s+(?:(array)\s+)?(\w+)\s*(?:=|$)',glob,re.M):
   d=False if typ=='boolean' else '' if typ=='string' else 0 if typ in ['integer','real'] else None
   e[name]=collections.defaultdict(lambda d=d:d) if array else d
  for name in e:
   if name.startswith('gg_trg_'):e[name]=name
  for called in set(re.findall(r'\b(\w+)\(',code))|set(re.findall(r'\bfunction (\w+)',s)):
   if called not in e and called not in names:e[called]=lambda *a:None
  e.update(Player=lambda p:p,ConvertedPlayer=lambda p:p-1,GetPlayerId=lambda p:27 if p is None else p,GetConvertedPlayerId=lambda p:p+1,
   GetPlayerName=lambda p:'P'+str(p+1),GetOwningPlayer=lambda u:27 if u is None else u['owner'],
   GetEnumUnit=lambda:e['enumunit'],GetDyingUnit=lambda:e['dead'],GetTriggerUnit=lambda:e['dead'],
   GetKillingUnit=lambda:e.get('killer'),GetKillingUnitBJ=lambda:e.get('killer'),GetTriggerPlayer=lambda:e.get('triggerplayer',0),
   GetEventPlayerChatString=lambda:e.get('chat',''),GetClickedButton=lambda:e.get('clicked'),
   GetUnitTypeId=lambda u:u['kind'],GetUnitX=lambda u:u['x'],GetUnitY=lambda u:u['y'],GetUnitFacing=lambda u:u['facing'],
   BlzGetUnitMaxHP=lambda u:u['maxhp'],BlzGetUnitMaxMana=lambda u:u['maxmp'],
   BlzSetUnitMaxHP=lambda u,n:u.update(maxhp=n),BlzSetUnitMaxMana=lambda u,n:u.update(maxmp=n),
   SetUnitState=lambda u,k,v:u.__setitem__(k,v),SetUnitInvulnerable=lambda u,v:u.update(invul=v),
   IsUnitType=lambda u,t:u.get(t,False),IsUnitIllusion=lambda u:u.get('illusion',False),
   GetUnitAbilityLevel=lambda u,a:int(a in u['abilities']),GetUnitCurrentOrder=lambda u:u.get('order',''),OrderId=lambda v:v,
   IssueImmediateOrder=lambda u,o:u.update(order=o),IssuePointOrder=lambda u,o,x,y:u.update(order=o,target=(x,y)),
   UnitAddAbility=lambda u,a:u['abilities'].add(a),UnitRemoveAbility=lambda u,a:u['abilities'].discard(a),
   GetPlayerTechCountSimple=lambda k,p:self.tech.get((p,k),0),BlzStartUnitAbilityCooldown=lambda u,k,t:u['cooldowns'].__setitem__(k,t),
   TimerGetRemaining=lambda t:7.,GetPlayerController=lambda p:e.get('controllers',{}).get(p,'user'),
   GetPlayerSlotState=lambda p:'playing' if e['udg_player_active'][p+1] else 'empty',
   CreateForce=set,ForceClear=lambda f:f.clear(),ForceAddPlayer=lambda f,p:f.add(p),DestroyForce=lambda f:None,
   ForceRemovePlayerSimple=lambda p,f:f.discard(p),CreateGroup=list,GroupEnumUnitsOfPlayer=self.enumunits,ForGroup=self.forgroup,
   SetPlayerAlliance=lambda p,q,f,v:self.alliances.__setitem__((p,q,f),v),IsUnitEnemy=lambda u,p:u['owner']!=p and not self.alliances.get((p,u['owner'],'passive'),False),
   CreateFogModifierRadius=self.vision,CreateFogModifierRect=lambda p,*a:self.vision(p,0,0,0,99999),FogModifierStop=lambda f:f.update(stopped=True),DestroyFogModifier=lambda f:f.update(destroyed=True),
   DisplayTextToForce=lambda *a:self.messages.append(a[-1]),DisplayTextToPlayer=lambda *a:self.messages.append(a[-1]),
   DisplayTimedTextToPlayer=lambda *a:self.messages.append(a[-1]),CustomVictoryBJ=lambda p,*a:self.winners.append(p),
   CreateUnit=self.unit,CreateTimer=self.timer,TimerStart=self.starttimer,PauseTimer=lambda t:t.update(paused=True) if t else None,
   GetExpiredTimer=lambda:e.get('expired'),TimerGetElapsed=lambda t:0.,
   TriggerExecute=self.trigger,ConditionalTriggerExecute=self.trigger,
   AdjustPlayerStateBJ=lambda n,p,*a:self.gold.__setitem__(p,self.gold[p]+n),
   MultiboardSetItemValueBJ=lambda b,col,row,val:self.board.__setitem__((row,col),val),
   CreateMultiboardBJ=lambda *a:e.__setitem__('lastboard',object()),GetLastCreatedMultiboard=lambda:e['lastboard'],
   GetLastCreatedMultiboardBJ=lambda:e.get('lastboard'),
   DialogCreate=object,DialogAddButton=lambda *a:object(),CreateTrigger=object,
   Location=lambda x,y:(x,y),Cos=math.cos,Sin=math.sin,ModuloInteger=lambda a,b:a%b,IMinBJ=min,I2R=float,I2S=str,
   UNIT_TYPE_HERO='hero',UNIT_TYPE_STRUCTURE='structure',UNIT_TYPE_TOWNHALL='townhall',UNIT_STATE_LIFE='life',UNIT_STATE_MANA='mana',
   PLAYER_STATE_RESOURCE_GOLD=0,FOG_OF_WAR_VISIBLE=0,PLAYER_NEUTRAL_PASSIVE=27,MAP_CONTROL_USER='user',PLAYER_SLOT_STATE_PLAYING='playing',
   ALLIANCE_PASSIVE='passive',ALLIANCE_HELP_REQUEST='help',ALLIANCE_HELP_RESPONSE='response',ALLIANCE_SHARED_XP='xp',
   ALLIANCE_SHARED_VISION='vision',ALLIANCE_SHARED_CONTROL='control',ALLIANCE_SHARED_ADVANCED_CONTROL='advanced',
   bj_ALLIANCE_UNALLIED=0,EVENT_PLAYER_UNIT_SELL=0,EVENT_PLAYER_UNIT_DEATH=1)
  exec(code,e)
  for pn in active:
   e['udg_player_active'][pn]=True;e['udg_unit_production'][pn]=True;e['udg_autosend'][pn]=True
   e['udg_base'][pn]=self.unit(pn-1,'base',pn*100.,pn*200.,180.)
  e['udg_Active_PlayGroup']=set(p-1 for p in active)
  e['SF_Initialize']();e['SKEnabled']=king
  e['udg_KOTH_Player']=27;e['udg_KOTH_Income_Timer']=self.timer()
  e['udg_KOTH_Gold_Rewarded']=9;e['udg_KOTH_Gold_Remaining']=99999;e['udg_KOTH_Gold_Reset_Amount']=300
  if king:e['SKInit']();e['SKCreateBoard']()
 def unit(self,owner,kind,x=0.,y=0.,facing=0.):
  u=dict(owner=owner,kind=kind,x=x,y=y,facing=facing,maxhp=1500,maxmp=300,abilities=set(),cooldowns={},structure=kind=='base',townhall=kind=='base',hero=kind.startswith('H'),invul=False)
  self.units.append(u);return u
 def timer(self):
  t=dict(paused=False);self.timers.append(t);return t
 def starttimer(self,t,d,repeat,callback):t.update(delay=d,repeat=repeat,callback=callback,paused=False);self.scheduled.append(t)
 def vision(self,p,_,x,y,r,*a):
  f=dict(p=p,x=x,y=y,r=r,stopped=False,destroyed=False);self.fog.append(f);return f
 def enumunits(self,g,p,_):g.extend(u for u in self.units if u['owner']==p)
 def forgroup(self,g,callback):
  for u in list(g):self.e['enumunit']=u;callback()
 def trigger(self,t):
  if t=='gg_trg_END':self.e['Trig_END_Actions']()
  elif t=='gg_trg_KOTH_Set_Neutral_Hill':self.e['udg_KOTH_Player']=27;self.e['udg_KOTH_Income_Timer']['paused']=True
  elif t=='gg_trg_KOTH_Gold_Depleted':self.e['udg_KOTH_Income_Timer']['paused']=True
 def tick(self,n=1):
  for _ in range(n):self.e['SKTick']()
 def death(self,victim,attacker=None):
  e=self.e;e['dead']=e['udg_base'][victim];e['killer']=None if attacker is None else self.unit(attacker-1,'hfoo')
  e['Trig_Multiboard_Update_Actions']();e['Trig_player_destroyed_Actions']()
 def invariant(self):
  e=self.e
  for p in players:
   if not e['SKActive'](p):continue
   king=e['SKKing'][p];assert e['SKActive'](king) and e['SKKing'][king]==king
   assert sum(p-1 in e['udg_team'][r] for r in range(1,9))==1
   assert p-1 in e['udg_team'][e['S8Team'](king)]
   for q in players:
    if p==q:continue
    allied=e['SKActive'](q) and king==e['SKKing'][q]
    assert self.alliances[p-1,q-1,'passive']==allied
    assert self.alliances[p-1,q-1,'vision']==allied
    assert not self.alliances[p-1,q-1,'control'] and not self.alliances[p-1,q-1,'advanced']
    f=e['SKBaseVision'][p*16+q];assert (f is not None)==allied

# Every ordered pair can capture, rebuild, defect, and recapture; all eight slot indices matter.
cases=0
for victim in players:
 for attacker in players:
  if attacker==victim:continue
  w=World();e=w.e;old=e['udg_base'][victim];old.update(maxhp=2345,maxmp=678)
  w.tech[victim-1,'R009']=1;e['udg_unit_production'][victim]=False;e['udg_autosend'][victim]=False
  w.death(victim,attacker)
  assert e['SKKing'][victim]==attacker and e['udg_player_active'][victim]
  assert e['SF_EliminatedVision'][victim] is None
  assert e['udg_base'][victim] is None and e['SKRespawnIn'][victim]==3
  assert e['SKCaptures'][attacker]==1 and e['udg_base_kills'][attacker]==1
  w.tick(3);b=e['udg_base'][victim]
  assert b is not old and b['owner']==victim-1 and b['kind']==old['kind']
  assert (b['x'],b['y'],b['facing'],b['maxhp'],b['maxmp'])==(old['x'],old['y'],old['facing'],2345,678)
  assert b['life']==2345 and b['mana']==678 and b['invul']
  assert {'A0FS','A06X','A082'}<=b['abilities'] and not e['udg_unit_production'][victim]
  e['SKDefect'](victim);assert e['SKKing'][victim]==victim and e['SKDefected'][victim]
  w.tick(9);assert b['invul'];w.tick();assert not b['invul']
  w.death(victim,attacker);e['SKDefect'](victim);assert e['SKKing'][victim]==attacker
  w.invariant();cases+=1

# King capture brings all vassals, while a vassal capture moves only that player.
w=World();e=w.e;a,b,c,d=players[:4]
e['SKCapture'](b,a);e['SKCapture'](c,b);e['SKCapture'](d,players[4]);w.invariant()
assert e['SKKing'][c]==a
e['SKTroopKills'][a]=17;e['SKHeroKills'][a]=4;e['udg_KOTH_Team_Gold_Earned_Total'][e['S8Team'](a)]=9
e['SKCapture'](b,d);assert e['SKKing'][b]==players[4] and e['SKKing'][a]==a and e['SKKing'][c]==a
e['SKCapture'](a,d);assert e['SKKing'][c]==players[4] and e['SKTroopKills'][players[4]]==17 and e['SKTroopKills'][a]==0
assert e['udg_KOTH_Team_Gold_Earned_Total'][e['S8Team'](players[4])]==9
w.invariant()

# Defection while rebuilding, neutral/allied base deaths, and rejected invalid requests.
w=World();e=w.e;a,b=players[:2];e['SKDefect'](a);assert not e['SKDefected'][a]
w.death(b,a);e['SKDefect'](b);w.tick(3);assert e['udg_base'][b]['invul'] and e['SKKing'][b]==b
w.tick(8);assert not e['udg_base'][b]['invul']
for attacker in [None,28,a]:
 w=World();e=w.e;a,b=players[:2]
 if attacker==a:e['SKCapture'](b,a)
 kings=dict(e['SKKing']);captures=dict(e['SKCaptures']);w.death(b,attacker);w.tick(3)
 assert dict(e['SKKing'])==kings and dict(e['SKCaptures'])==captures and e['udg_base'][b] is not None
for pn in [0,3,6,9,11,13,24,28]:
 if pn not in players:e['SKDefect'](pn);assert not e['SKDefected'][pn]

# Every player can be the final sovereign. A late defection cancels the countdown.
for king in players:
 w=World();e=w.e
 for p in players:
  if p!=king:e['SKCapture'](p,king)
 assert e['SKPendingKing']==king
 w.tick(19);assert not w.winners
 rebel=next(p for p in players if p!=king);e['SKDefect'](rebel)
 assert e['SKPendingKing']==0 and not e['SoloFoots_EndGameStarted']
 w.tick(3);assert not w.winners
 e['SKCapture'](rebel,king);w.tick(19);assert not w.winners
 w.tick();assert set(w.winners)==set(slots) and len(w.winners)==8 and e['SKWinner']==king

# A leaving king has a live successor; a leaving/rebuilding vassal does not reappear.
for king in players:
 w=World();e=w.e;vassals=[p for p in players if p!=king][:3]
 for p in vassals:e['SKCapture'](p,king)
 e['SKTroopKills'][king]=13;e['triggerplayer']=king-1;e['Trig_player_leaves_Actions']()
 successor=e['SKKing'][vassals[0]];assert successor in vassals and e['SKTroopKills'][successor]==13
 assert not e['udg_player_active'][king];w.invariant()
 v=vassals[-1];w.death(v,next(p for p in players if e['SKActive'](p) and e['SKKing'][p]!=successor))
 e['triggerplayer']=v-1;e['Trig_player_leaves_Actions']();w.tick(4);assert e['udg_base'][v] is None

# Hill income conserves the full payout for kingdoms of every size; neutral pays nothing.
for size in range(1,9):
 w=World();e=w.e;king=players[-1]
 for p in [p for p in players if p!=king][:size-1]:e['SKCapture'](p,king)
 e['udg_KOTH_Player']=king-1;e['SKHillIncome']()
 assert sum(w.gold.values())==9 and sum(v>0 for v in w.gold.values())==size
 assert all(e['SKKing'][p+1]==king for p,v in w.gold.items() if v)
 e['udg_KOTH_Player']=27;e['SKHillIncome']();assert sum(w.gold.values())==9
 assert e['udg_KOTH_Income_Timer']['paused']

# Individual -kd and sovereign totals both credit vassal kills without allied/illusion farming.
w=World();e=w.e;a,b,c=players[:3];e['SKCapture'](b,a)
e['dead']=w.unit(c-1,'H001');e['killer']=w.unit(b-1,'hfoo');e['Trig_Multiboard_Update_Actions']()
assert e['SKHeroKills'][a]==1 and e['udg_hero_kills'][b]==1 and e['udg_hero_deaths'][c]==1
e['dead']=w.unit(a-1,'H001');e['Trig_Multiboard_Update_Actions']();assert e['SKHeroKills'][a]==1
e['Trig_KD_Actions']();assert len([m for m in w.messages if 'Hero K/D:' in m])==8
e['F8_UpdateBoard']();assert all((row,2) in w.board and (row,6) in w.board for row in range(2,10))

# Sparse lobbies, single-player testing and randomized captures/defections/departures.
for active in [players[:1],players[::2],[players[1],players[-1]],players]:
 w=World(active=active);e=w.e
 if len(active)==1:w.tick(30);assert not w.winners
 else:
  rng=random.Random(41)
  for _ in range(120):
   a,b=rng.sample(active,2);e['SKCapture'](a,b)
   if rng.randrange(3)==0:e['SKDefect'](a)
   w.invariant()

# Mode UI is host-only, starts only once, and defaults safely if no human is present.
for chooseking in [False,True]:
 w=World(king=False);e=w.e;e['SKOpenMode']();assert e['SKModeHost']==0
 e['triggerplayer']=4;e['clicked']=e['SKModeButton'];e['SKModeClicked']();assert not e['SKModeChosen']
 e['triggerplayer']=0;e['clicked']=e['SKModeButton'] if chooseking else e['SKFfaButton'];e['SKModeClicked']()
 count=len(w.scheduled);assert e['SKEnabled']==chooseking and e['SKModeChosen']
 e['SKModeDefault']();assert e['SKEnabled']==chooseking and len(w.scheduled)==count
w=World(king=False);e=w.e;e['controllers']={p:'computer' for p in slots};e['SKOpenMode']();assert e['SKModeChosen'] and not e['SKEnabled']
w=World(active=players[1:],king=False);e=w.e;e['SKOpenMode']();assert e['SKModeHost']==4

# Layout/object payloads are exactly v9, and the packaged script contains all mode hooks.
for pn in players:
 w=World(king=False);e=w.e;e['SF_RevealEliminated'](pn);assert e['SF_EliminatedVision'][pn] is None
 w.death(pn,next(p for p in players if p!=pn))
 assert not e['udg_player_active'][pn] and e['SF_EliminatedVision'][pn]['r']==99999
 before=len(w.fog);e['SF_RevealEliminated'](pn);assert len(w.fog)==before
 assert not any(e['SF_EliminatedVision'][other] is not None for other in players if other!=pn)
for name in ['war3map.w3e','war3map.wpm','war3mapUnits.doo','war3map.doo','war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3mapMap.blp','war3mapMap_ingame.blp']:
 assert (R/'roundtrip'/name).read_bytes()==(R/'base'/name).read_bytes(),name
assert 'call SKOnBaseDeath()' in re.search(r'^function Trig_player_destroyed_Actions\b.*?^endfunction',s,re.M|re.S)[0]
assert 'function SKOpenMode' in re.search(r'^function SF_Initialize\b.*?^endfunction',s,re.M|re.S)[0]
assert s.index('call InitTrig_Multiboard_Update()')<s.index('call InitTrig_player_destroyed()')
print(f'PASS: {cases} ordered capture/defect pairs; rebuild/tier/resources/toggles; whole-kingdom transfers; eight sovereign victory/defection cases; succession/leavers; kingdom sizes 1-8 income; scoring/vision/control invariants; sparse lobbies; randomized transitions; mode selection; unchanged v9 geometry/assets.')
