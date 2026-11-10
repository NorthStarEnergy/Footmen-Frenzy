"""Execute the delivered JASS against strict mocked Warcraft natives."""
from pathlib import Path
from collections import defaultdict
import ast,re,math,json,random
R=Path(__file__).resolve().parent
source=(R/'stalker.j').read_text()
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
tree=ast.parse((R.parent/'799x-backport/check_runtime.py').read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
code=re.sub(r'\bfunction (ST_\w+)',r'\1','\n\n'.join(translate(n) for n in functions))
checks=[]
def check(label,ok):
    assert ok,label
    checks.append(label)
def setup():
    units={1:dict(kind='nStk',x=0.,y=0.,owner=0,life=80.,mana=80.,armor=2,collision=32.,facing=35.,abilities={})}
    state=dict(caster=1,spell='AStB',target=(600.,0.),player=0,damage=0.,attack=True,source=2,groups={},effects={},timers={},triggers={},next=1000,visible=lambda x,y,p:True,pathable=lambda x,y:False,item=[0.,0.],position_adjust=None,teleports=[],cooldowns={},bounds=(-4000.,4000.,-4000.,4000.))
    def alloc(store,value):state['next']+=1;store[state['next']]=value;return state['next']
    def destroy(store,h):assert h in store,('double-free',h);del store[h]
    def group():return alloc(state['groups'],[])
    def prop(u,k,default=0):return units.get(u,{}).get(k,default)
    def position(u,x,y):
        adjust=state['position_adjust'];x,y=adjust(u,x,y) if adjust else (x,y);units[u].update(x=x,y=y)
    def createunit(p,k,x,y,f):return alloc(units,dict(kind=k,x=x,y=y,owner=p,life=80.,mana=80.,armor=2,collision=32.,facing=f,abilities={}))
    def effect(path,*a):return alloc(state['effects'],dict(path=path,args=a))
    noop=lambda *a:None
    env=dict(ST_UNIT='nStk',ST_BLINK='AStB',ST_RANGE=800.,ST_COOLDOWN=7.,ST_REGEN_DELAY=7.,ST_MAX_SHIELD=80.,ST_Hash={},ST_Units=group(),ST_Selected={i:group() for i in range(12)},ST_Now=0.,ST_Probe=99,ST_LandX=0.,ST_LandY=0.,bj_PI=math.pi,bj_mapInitialPlayableArea=1,bj_MAX_PLAYER_SLOTS=24,FF_TestRecruited=group(),UNIT_TYPE_DEAD='dead',UNIT_TYPE_FLYING='flying',UNIT_IF_DEFENSE_TYPE=1,UNIT_STATE_MANA=1,PATHING_TYPE_WALKABILITY=1,EVENT_PLAYER_UNIT_SELECTED=1,EVENT_PLAYER_UNIT_DESELECTED=2,EVENT_PLAYER_UNIT_DAMAGED=3,EVENT_PLAYER_UNIT_DAMAGING=4,EVENT_PLAYER_UNIT_SPELL_EFFECT=5)
    env.update(GetUnitTypeId=lambda u:prop(u,'kind',0),GetWidgetLife=lambda u:prop(u,'life'),IsUnitType=lambda u,k:prop(u,k,False),GetHandleId=lambda h:h or 0,GetOwningPlayer=lambda u:prop(u,'owner'),GetUnitX=lambda u:prop(u,'x'),GetUnitY=lambda u:prop(u,'y'),GetUnitFacing=lambda u:prop(u,'facing'),IsUnitIllusion=lambda u:prop(u,'illusion',False),IsUnitPaused=lambda u:prop(u,'paused',False),IsUnitHidden=lambda u:prop(u,'hidden',False),GetUnitAbilityLevel=lambda u,a:prop(u,'abilities',{}).get(a,0),BlzGetUnitCollisionSize=lambda u:prop(u,'collision',32.),BlzGetUnitIntegerField=lambda u,f:prop(u,'armor'),
        GetUnitState=lambda u,s:prop(u,'mana'),SetUnitState=lambda u,s,v:units[u].update(mana=v),GetTriggerUnit=lambda:state['caster'],GetTriggerPlayer=lambda:state['player'],GetPlayerId=lambda p:p,Player=lambda i:i,GetTriggerEventId=lambda:state.get('event',1),GetSpellAbilityId=lambda:state['spell'],GetSpellTargetX=lambda:state['target'][0],GetSpellTargetY=lambda:state['target'][1],GetEventDamage=lambda:state['damage'],GetEventDamageSource=lambda:state['source'],BlzSetEventDamage=lambda d:state.update(damage=d),BlzGetEventIsAttack=lambda:state['attack'],
        IsVisibleToPlayer=lambda x,y,p:state['visible'](x,y,p),IsTerrainPathable=lambda x,y,p:state['pathable'](x,y),SetItemPosition=lambda it,x,y:state['item'].__setitem__(slice(None),state.get('item_adjust',lambda x,y:(x,y))(x,y)),GetItemX=lambda it:state['item'][0],GetItemY=lambda it:state['item'][1],SetItemVisible=noop,SetItemInvulnerable=noop,CreateItem=lambda *a:99,
        GetRectMinX=lambda r:state['bounds'][0],GetRectMaxX=lambda r:state['bounds'][1],GetRectMinY=lambda r:state['bounds'][2],GetRectMaxY=lambda r:state['bounds'][3],SetUnitPosition=position,SetUnitFacing=lambda u,f:units[u].update(facing=f),SetUnitAnimation=lambda u,a:units[u].update(animation=a),TFP_FFDP_NotifyTeleport=lambda u,b:state['teleports'].append((u,b)),
        CreateGroup=group,DestroyGroup=lambda g:destroy(state['groups'],g),BlzGroupGetSize=lambda g:len(state['groups'][g]),BlzGroupUnitAt=lambda g,i:state['groups'][g][i],IsUnitInGroup=lambda u,g:u in state['groups'][g],GroupAddUnit=lambda g,u:state['groups'][g].append(u) if u not in state['groups'][g] else None,GroupRemoveUnit=lambda g,u:state['groups'][g].remove(u) if u in state['groups'][g] else None,FirstOfGroup=lambda g:state['groups'][g][0] if state['groups'][g] else None,
        GroupEnumUnitsInRange=lambda g,x,y,r,f:state['groups'][g].__setitem__(slice(None),[u for u,v in units.items() if math.hypot(v['x']-x,v['y']-y)<=r]),GroupEnumUnitsInRect=lambda g,r,f:state['groups'][g].__setitem__(slice(None),list(units)),
        AddSpecialEffect=effect,AddSpecialEffectTarget=effect,DestroyEffect=lambda fx:destroy(state['effects'],fx),BlzSetSpecialEffectColor=noop,BlzSetSpecialEffectScale=noop,
        BlzStartUnitAbilityCooldown=lambda u,a,d:state['cooldowns'].__setitem__(u,d),BlzEndUnitAbilityCooldown=lambda u,a:state['cooldowns'].__setitem__(u,0),BlzGetUnitAbilityCooldownRemaining=lambda u,a:state['cooldowns'].get(u,0),RMinBJ=min,RMaxBJ=max,I2R=float,R2I=int,SquareRoot=math.sqrt,Cos=math.cos,Sin=math.sin,ModuloInteger=lambda a,b:a%b,
        LX_TestAllowed=lambda:state.get('allowed',True),GetPlayerStartLocation=lambda p:p,GetStartLocationX=lambda p:0.,GetStartLocationY=lambda p:0.,CreateUnit=createunit,SelectGroupForPlayerBJ=lambda g,p:state.update(selected=list(state['groups'][g])),DisplayTimedTextToPlayer=lambda *a:state.update(message=a[-1]),
        InitHashtable=dict,CreateTrigger=lambda:alloc(state['triggers'],dict(events=[],actions=[])),TriggerRegisterPlayerUnitEvent=lambda t,*a:state['triggers'][t]['events'].append(a),TriggerAddAction=lambda t,a:state['triggers'][t]['actions'].append(a),TriggerRegisterPlayerChatEvent=lambda t,*a:state['triggers'][t]['events'].append(a),TriggerRegisterAnyUnitEventBJ=lambda t,*a:state['triggers'][t]['events'].append(a),CreateRegion=lambda:999,RegionAddRect=noop,GetWorldBounds=lambda:1,TriggerRegisterEnterRegion=noop,CreateTimer=lambda:alloc(state['timers'],{}),TimerStart=lambda t,d,r,cb:state['timers'][t].update(period=d,repeat=r,callback=cb))
    for kind in ['Real','Integer','Boolean']:
        env['Save'+kind]=lambda h,k,n,v:h.__setitem__((k,n),v)
        env['Load'+kind]=lambda h,k,n:h.get((k,n),0)
    env['FlushChildHashtable']=lambda h,k:[h.pop(a) for a in list(h) if a[0]==k]
    exec(code,env)
    env['ST_Register'](1)
    def add(u,**v):units[u]=dict(units[1],abilities={},**{});units[u].update(v);env['ST_Register'](u);return u
    def select(*ids):state['groups'][env['ST_Selected'][state['player']]]=list(ids)
    return env,units,state,add,select
if __name__=='__main__':
    e,u,s,add,select=setup();e['ST_Init']()
    check('Init registers damage handlers for all 24 player slots',sum(any(len(a)>1 and a[1]==3 for a in t['events']) for t in s['triggers'].values())==1 and sum(a[1]==3 for t in s['triggers'].values() for a in t['events'] if len(a)>1)==24)
    check('Initial placed Stalkers registered',s['groups'][e['ST_Units']]==[1])
    for damage,remaining,spill in [(20,60,0),(80,0,0),(120,0,40)]:
        e,u,s,add,select=setup();s['damage']=damage;e['ST_Damage']();check(f'Shield absorbs {damage} including overflow',u[1]['mana']==remaining and s['damage']==spill and not s['effects'])
    e,u,s,add,select=setup();s['damage']=-10;e['ST_Damage']();check('Healing does not consume shields',u[1]['mana']==80 and s['damage']==-10)
    s['damage']=20;e['ST_Damage']()
    for _ in range(27):e['ST_Tick']()
    check('No regeneration before seven seconds',u[1]['mana']==60)
    e['ST_Tick']();check('Regen begins after delay at 2 per second',u[1]['mana']==60.5)
    for _ in range(200):e['ST_Tick']()
    check('Shields cap at 80',u[1]['mana']==80)
    s['damage']=10;e['ST_Damage']();e['ST_Tick']();check('Another hit resets regeneration delay',u[1]['mana']==70)
    u[1]['kind']=0;e['ST_Tick']();check('Removed unit purges group and hashtable state',not s['groups'][e['ST_Units']] and not e['ST_Hash'])
    for armor,bonus in [(0,0),(1,0),(2,5),(3,5),(4,0),(5,0),(7,0)]:
        e,u,s,add,select=setup();add(2,x=800.,kind='hfoo',armor=armor);s.update(source=1,caster=2,damage=13);e['ST_Bonus']();check(f'Armored mapping defense {armor}',s['damage']==13+bonus)
    s['attack']=False;s['damage']=13;e['ST_Bonus']();check('No bonus on spell damage',s['damage']==13)
    e,u,s,add,select=setup();add(2,y=100.);select(1,2);e['ST_Cast']()
    check('Selected squad preserves exact translation',[(u[i]['x'],u[i]['y']) for i in [1,2]]==[(600.,0.),(600.,100.)])
    check('Each mover receives its own cooldown and tether notification',s['cooldowns']=={1:7.,2:7.} and len(s['teleports'])==2)
    check('Facing preserved without missing Spell animation',all(v['facing']==35 and v['animation']=='stand' for v in u.values()))
    e['ST_Cast']();check('Duplicate spell events cannot Blink twice',u[1]['x']==600 and u[2]['x']==600)
    for label,props in [('enemy',dict(owner=1)),('unselected',{}),('paused',dict(paused=True)),('stunned',dict(abilities={'Bstn':1})),('ensnared',dict(abilities={'Bens':1})),('silenced',dict(abilities={'Bsil':1})),('hidden transport',dict(hidden=True)),('illusion',dict(illusion=True)),('dead',dict(life=0)),('other unit',dict(kind='hfoo')),('distant',dict(y=1500.))]:
        e,u,s,add,select=setup();add(2,y=100.,**{k:v for k,v in props.items() if k!='y'});u[2].update({k:v for k,v in props.items() if k=='y'});select(1,*([] if label=='unselected' else [2]));e['ST_Cast']();check('Group excludes '+label,u[2]['x']==0 and 2 not in s['cooldowns'])
    e,u,s,add,select=setup();add(2,y=100.);select(1,2);e['ST_Hash'][2,1]=5;e['ST_Cast']();check('Group excludes custom per-unit cooldown',u[2]['x']==0)
    e,u,s,add,select=setup();add(2,y=100.);select(1,2);s['cooldowns'][2]=5;e['ST_Cast']();check('Group excludes native per-unit cooldown',u[2]['x']==0)
    for label,update in [('terrain',dict(pathable=lambda x,y:True)),('fog',dict(visible=lambda x,y,p:False)),('destructible',dict(item_adjust=lambda x,y:(x+100,y))),('boundary',dict(bounds=(-300.,300.,-300.,300.)))]:
        e,u,s,add,select=setup();s.update(update);e['ST_Cast']();check(label+' blocks Blink without spending cooldown',u[1]['x']==0 and s['cooldowns'].get(1,0)==0 and not s['teleports'])
    e,u,s,add,select=setup();s['position_adjust']=lambda u,x,y:(x+20,y) if x>100 else (x,y);e['ST_Cast']();check('Native placement displacement rolls back and refunds',u[1]['x']==0 and s['cooldowns'][1]==0)
    e,u,s,add,select=setup();add(2,x=600,y=0,kind='hfoo');e['ST_Cast']();check('Occupied landing searches nearby free space',math.hypot(u[1]['x']-600,u[1]['y'])>=64 and math.hypot(u[1]['x'],u[1]['y'])<=800.01)
    e,u,s,add,select=setup();s['target']=(5000.,0);e['ST_Cast']();check('Far click clamps to maximum Blink range',abs(u[1]['x']-800)<.001)
    e,u,s,add,select=setup();s['target']=(0.,0);e['ST_Cast']();check('Zero-distance cast refunds',u[1]['x']==0 and s['cooldowns'][1]==0)
    e,u,s,add,select=setup();s['spell']='ALxR';e['ST_Cast']();check('Unrelated spells untouched',u[1]['x']==0 and not s['cooldowns'])
    e,u,s,add,select=setup();s['allowed']=False;del u[1];s['groups'][e['ST_Units']]=[];e['ST_Summon']();check('Test squad unavailable in normal multiplayer',not u)
    s['allowed']=True;e['ST_Summon']();check('Test command creates eight Stalkers',len(u)==8 and len(s['selected'])==8)
    e['ST_Summon']();check('Repeated test command selects existing squad without duplication',len(u)==8)
    e,u,s,add,select=setup();s['event']=1;e['ST_Selection']();check('Selection event tracks Stalker',1 in s['groups'][e['ST_Selected'][0]])
    s['event']=2;e['ST_Selection']();check('Deselection event removes Stalker',1 not in s['groups'][e['ST_Selected'][0]])
    rng=random.Random(171022)
    for _ in range(1000):
        e,u,s,add,select=setup();s['target']=(rng.uniform(-5000,5000),rng.uniform(-5000,5000));e['ST_Cast']();assert math.hypot(u[1]['x'],u[1]['y'])<=800.00001;assert not s['effects'];assert len(s['groups'])==14
    check('1000 randomized casts respect range and release temporary handles',True)
    (R/'checks.json').write_text(json.dumps(dict(passed=len(checks),checks=checks,random_cases=1000,actual_jass_executed=True,engine_playtested=False),indent=2));print(f'{len(checks)} behavior checks and 1000 randomized casts passed.')
