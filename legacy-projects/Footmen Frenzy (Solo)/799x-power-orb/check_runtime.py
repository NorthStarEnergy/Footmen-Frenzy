"""Mocked JASS lifecycle regression tests; not a Warcraft engine playtest.
Harness adapted from the project's previous Orianna feedback audit.
"""
from pathlib import Path
from collections import defaultdict
import math,re,json
ROOT=Path(__file__).resolve().parent
s=(ROOT/'src/war3map.j').read_text()
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
def expression(line):
    tokens=re.findall(r'"(?:[^"\\]|\\.)*"|\'[^\']*\'|//.*|[A-Za-z_]\w*|[0-9]+(?:\.[0-9]+)?|!=|==|<=|>=|[^\s]',line)
    return ' '.join({'true':'True','false':'False','null':'None'}.get(t,t) for t in tokens if not t.startswith('//'))

def translate(name):
    source=functions[name];lines=source.splitlines()
    args=re.search(r' takes (.*?) returns ',lines[0])[1]
    args=[] if args=='nothing' else [x.strip().split()[-1] for x in args.split(',')]
    locals_=re.findall(r'^\s*local \w+ (\w+)',source,re.M)
    assigned=set(re.findall(r'^\s*set (\w+)',source,re.M))-set(locals_)-set(args)
    out=[f'def {name}({", ".join(args)}):']
    if assigned:out.append('    global '+', '.join(sorted(assigned)))
    depth=1
    for raw in lines[1:-1]:
        line=expression(raw).strip()
        if not line:continue
        if line in ['endif','endloop']:depth-=1;continue
        if line.startswith('elseif '):
            depth-=1;out.append('    '*depth+'elif '+line[7:-5]+':');depth+=1
        elif line=='else':
            depth-=1;out.append('    '*depth+'else:');depth+=1
        elif line.startswith('if ') and line.endswith(' then'):
            out.append('    '*depth+line[:-5]+':');depth+=1
        elif line=='loop':out.append('    '*depth+'while True:');depth+=1
        elif line.startswith('exitwhen '):out.append('    '*depth+'if '+line[9:]+': break')
        elif line.startswith('local '):
            m=re.match(r'local \w+ (\w+)(.*)',line)
            out.append('    '*depth+m[1]+(m[2] if m[2].strip() else '=None'))
        elif line.startswith('set '):out.append('    '*depth+line[4:])
        elif line.startswith('call '):out.append('    '*depth+line[5:])
        else:out.append('    '*depth+line)
    return '\n'.join(out)
def setup():
 global units,handles,effects,timers,sounds,event,hits,slows
 units={1:dict(x=0.,y=0.,height=0.,owner=0,alive=True,skin='HOr1',abilities=set(),paused=False),2:dict(x=600.,y=100.,height=90.,owner=0,alive=True,skin='ally',abilities=set(),paused=False),3:dict(x=300.,y=0.,height=0.,owner=1,alive=True,skin='enemy',abilities=set(),paused=False),10:dict(x=0.,y=0.,height=80.,owner=0,alive=True,skin='hor1',abilities=set(),paused=False)}
 handles={};effects={};timers={};sounds={};event={'spell':'AOz1','target':2,'rank':1,'x':400.,'y':0.};hits=[];slows=[]
 for typ,name in re.findall(r'^\s*(unit|player|group|effect|real|integer|boolean) array (OM_\w+)',s,re.M):env[name]=defaultdict(lambda:0)
 env.update(OM_Count=1,OM_Now=0.,OM_Hastes=0,OM_Pulls=0,OM_Hash=99,OM_Group=[],OM_TICK=.03125,OM_SPEED=1200.,OM_LEASH=1200.,OM_HASTE_DURATION=2.,OM_HERO='HOr1',OM_ATTACK='AOz1',OM_PULSE='AOz2',OM_PROTECT='AOz3',OM_SHOCK='AOz4',bj_mapInitialPlayableArea=1,ANIM_TYPE_STAND=0,UNIT_TYPE_STRUCTURE=1,UNIT_TYPE_MAGIC_IMMUNE=2,UNIT_STATE_MANA=3)
 for key,value in [('OM_Hero',1),('OM_Ball',10),('OM_Owner',0),('OM_Carrier',1),('OM_Hit',[])]:env[key][1]=value
 counter=[100]
 def new(store,**values):counter[0]+=1;store[counter[0]]=values;return counter[0]
 noop=lambda *a:None
 def skin(u,k):units[u].update(skin=k,abilities=set(),paused=False)
 def destroy(fx):assert not effects[fx].get('destroyed');effects[fx]['destroyed']=True
 def enum(g,x,y,r,_):g[:]=[u for u in [3] if math.hypot(units[u]['x']-x,units[u]['y']-y)<=r and units[u]['alive']]
 env.update(GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],GetUnitFlyHeight=lambda u:units[u]['height'],SetUnitX=lambda u,x:units[u].update(x=x),SetUnitY=lambda u,y:units[u].update(y=y),SetUnitFlyHeight=lambda u,h,r:units[u].update(height=h),GetOwningPlayer=lambda u:units[u]['owner'],GetUnitTypeId=lambda u:units[u]['skin'] if u in units else 0,GetHandleId=lambda u:u,
  BlzGetUnitSkin=lambda u:units[u]['skin'],BlzSetUnitSkin=skin,UnitAddAbility=lambda u,a:units[u]['abilities'].add(a),UnitRemoveAbility=lambda u,a:units[u]['abilities'].discard(a),SetUnitPathing=noop,SetUnitMoveSpeed=noop,PauseUnit=lambda u,p:units[u].update(paused=p),SelectUnit=noop,
  LoadEffectHandle=lambda h,k,n:handles.get((k,n)),SaveEffectHandle=lambda h,k,n,v:handles.update({(k,n):v}),RemoveSavedHandle=lambda h,k,n:handles.pop((k,n),None),FlushChildHashtable=lambda h,k:[handles.pop(a) for a in list(handles) if a[0]==k],SaveInteger=lambda *a:None,RemoveSavedInteger=noop,
  AddSpecialEffect=lambda model,x,y:new(effects,model=model,x=x,y=y),AddSpecialEffectTarget=lambda model,u,point:new(effects,model=model,unit=u,point=point),DestroyEffect=destroy,BlzSetSpecialEffectScale=lambda f,v:effects[f].update(scale=v),BlzSetSpecialEffectZ=lambda f,v:effects[f].update(z=v),BlzSetSpecialEffectColor=lambda f,*v:effects[f].update(color=v),BlzPlaySpecialEffect=lambda f,v:effects[f].update(anim=v),
  CreateTimer=lambda:new(timers),TimerStart=lambda t,d,r,c:timers[t].update(duration=d,repeat=r,callback=c),GetExpiredTimer=lambda:event['timer'],DestroyTimer=lambda t:timers[t].update(destroyed=True),
  Location=lambda x,y:(x,y),GetLocationZ=lambda p:100.,RemoveLocation=noop,
  CreateSound=lambda path,*a:new(sounds,path=path,args=a),SetSoundDuration=lambda s,d:sounds[s].update(duration=d),SetSoundChannel=noop,SetSoundVolume=noop,SetSoundDistances=noop,SetSoundDistanceCutoff=noop,AttachSoundToUnit=lambda s,u:sounds[s].update(unit=u),StartSound=lambda s:sounds[s].update(started=True),KillSoundWhenDone=lambda s:sounds[s].update(cleanup=True),
  OM_Alive=lambda u:u in units and units[u]['alive'],OM_Enemy=lambda c,u:units[u]['owner']!=units[c]['owner'],OM_Deal=lambda c,u,d:hits.append((c,u,d)),OM_Slow=lambda c,u:slows.append(u),OM_Haste=noop,OM_ProtectArrival=noop,OM_Pull=noop,OM_Register=lambda u:1,
  IsUnitAlly=lambda u,p:units[u]['owner']==p,IsUnitType=lambda *a:False,IsUnitPaused=lambda u:units[u]['paused'],GetUnitAbilityLevel=lambda u,a:1 if a in units[u]['abilities'] else event['rank'] if a.startswith('AOz') else 0,
  GetTriggerUnit=lambda:1,GetSpellAbilityId=lambda:event['spell'],GetSpellTargetX=lambda:event['x'],GetSpellTargetY=lambda:event['y'],GetSpellTargetUnit=lambda:event['target'],GetRectMinX=lambda r:-4000.,GetRectMaxX=lambda r:4000.,GetRectMinY=lambda r:-4000.,GetRectMaxY=lambda r:4000.,
  SquareRoot=math.sqrt,Sin=math.sin,RMinBJ=min,RMaxBJ=max,GroupClear=lambda g:g.clear(),GroupEnumUnitsInRange=enum,FirstOfGroup=lambda g:g[0] if g else None,GroupRemoveUnit=lambda g,u:g.remove(u),GroupAddUnit=lambda g,u:g.append(u),IsUnitInGroup=lambda u,g:u in g,DestroyGroup=noop,
  SetUnitOwner=lambda u,p,b:units[u].update(owner=p),ShowUnit=lambda u,b:units[u].update(shown=b),RemoveUnit=lambda u:units.pop(u),CreateUnit=lambda *a:(units.update({20:dict(units[10],abilities=set())}),20)[1],SetUnitAbilityLevel=noop,IssueTargetOrder=noop,UnitApplyTimedLife=noop,
  BlzEndUnitAbilityCooldown=noop,GetUnitState=lambda *a:100.,SetUnitState=noop,BlzGetUnitAbilityManaCost=lambda *a:50.)

names=[n for n in functions if n.startswith('OM_') and n not in ('OM_Init',)]
code=re.sub(r'\bfunction (OM_\w+)',r'\1','\n\n'.join(translate(n) for n in names))
env={};exec(code,env)
actual=dict(env)
checks=[]
def check(name,value):
    assert value,name
    checks.append(name)
base_setup=setup
def setup():
    base_setup()
    noop=lambda *a:None
    env.update(OM_HASTE_RADIUS=200.,OM_VisualGround=999,MoveLocation=noop,SetUnitTimeScale=noop,SetUnitAnimationByIndex=lambda u,i:units[u].update(animation=i),QueueUnitAnimation=lambda u,a:units[u].update(queued_animation=a),SetUnitVertexColor=noop,SetUnitScale=noop,
        BlzSetSpecialEffectAlpha=lambda f,v:effects[f].update(alpha=v),LoadInteger=lambda h,k,n:handles.get((k,n),0),
        BlzSetSpecialEffectPosition=lambda f,x,y,z:effects[f].update(x=x,y=y,z=z),BlzSetSpecialEffectTimeScale=noop,
        LoadBoolean=lambda h,k,n:handles.get((k,n),False),SaveBoolean=lambda h,k,n,v:handles.update({(k,n):v}),RemoveSavedBoolean=lambda h,k,n:handles.pop((k,n),None),
        SaveInteger=lambda h,k,n,v:handles.update({(k,n):v}),GetPlayerId=lambda p:p,CreateGroup=lambda:[])
    for kind in ['Real','UnitHandle','GroupHandle']:
        env['Save'+kind]=lambda h,k,n,v:handles.update({(k,n):v})
        env['Load'+kind]=lambda h,k,n:handles.get((k,n),0)
    env.update(R2I=int,BlzUnitHideAbility=noop,RemoveSavedReal=lambda h,k,n:handles.pop((k,n),None))
    env.update(Atan2=math.atan2,BlzSetSpecialEffectYaw=lambda f,v:effects[f].update(yaw=v))
    env.update(Cos=math.cos,GetUnitFacing=lambda u:units[u].get('facing',0.))
    units[2]['x']=100.; units[2]['y']=0.
    env['OM_Register']=lambda u:1

def ticks(n):
    for _ in range(n):
        pending=list(timers)
        env['OM_Tick']()
        for t in pending:
            v=timers[t]
            if v.get('destroyed'):continue
            v['elapsed']=v.get('elapsed',0)+env['OM_TICK']
            if v['elapsed']>=v['duration']:
                v['elapsed']=0
                event['timer']=t;v['callback']()
def cast(a):event['spell']=a;env['OM_OnCast']()
def path_ends(name):return any(v['path'].endswith(name+'.wav') for v in sounds.values())
def clean():
    for _ in range(64):
        for t,v in list(timers.items()):
            if not v.get('destroyed'):event['timer']=t;v['callback']()
    assert all(v.get('destroyed') for v in timers.values())
setup();env['OM_Home'](1);cast('AOz1');ticks(20)
check('Move travels and arrives with separate audio',env['OM_State'][1]==3 and path_ends('Move') and path_ends('Arrival'))
check('Move damages each crossed enemy once',len(hits)==1)
check('Travel effect cleared on arrival',(10,-100) not in handles)
clean();check('Timed effects destroyed while orb persists',all(f.get('destroyed') or key==handles[10,-102] for key,f in effects.items()))
setup();cast('AOz3');ticks(20)
check('Protect arrives on ally with distinct travel/heal sounds',env['OM_Carrier'][1]==2 and env['OM_State'][1]==0 and path_ends('Protect') and path_ends('Heal'))
check('Protect arrival radius matches heal radius',any(f.get('scale')==200. and 'ProtectRing' in f['model'] for f in effects.values()))
setup();cast('AOz1');cast('AOz3')
check('Recast maintains exactly one orb',sum(not f.get('destroyed') for f in effects.values())==1)
for rank,radius in enumerate([207.9,225.225,242.55,277.2,311.85,346.5],1):
    setup();event['rank']=rank;cast('AOz2')
    ticks(8)
    check('Attack radius rank '+str(rank),any('AttackRing' in f['model'] and abs(f['scale']-radius)<.001 for f in effects.values()) and path_ends('Attack'))
for rank,radius in enumerate([211.75,254.1,296.45],1):
    setup();event['rank']=rank;units[10]['x']=300.;cast('AOz4')
    windup=handles[10,-101]
    check('Shockwave uses Enchantress cast gesture rank '+str(rank),units[1]['animation']==1 and units[1]['queued_animation']=='stand')
    check('Visible windup rank '+str(rank),path_ends('Windup') and effects[windup]['alpha']==110 and abs(effects[windup]['scale']-radius)<.001)
    ticks(15);check('No early impact rank '+str(rank),not path_ends('Shockwave'))
    ticks(1);check('Impact at half second rank '+str(rank),path_ends('Shockwave') and effects[windup].get('destroyed') and (10,-101) not in handles)
    clean();check('Ultimate effects clean rank '+str(rank),all(f.get('destroyed') or key==handles[10,-102] for key,f in effects.items()))
setup();cast('AOz4');windup=handles[10,-101];cast('AOz1')
check('Commands cannot displace windup',handles[10,-101]==windup and env['OM_State'][1]==3)
units[1]['alive']=False;ticks(1)
check('Death cancels windup and hides ball',effects[windup].get('destroyed') and not units[10]['shown'] and env['OM_ShockAt'][1]==0)
units[1]['alive']=True;ticks(1)
check('Revive restores active attached ball',units[10]['shown'] and not units[10]['paused'] and env['OM_State'][1]==0)
setup();cast('AOz1');units[1]['owner']=2;ticks(1)
check('Ownership change clears flight',env['OM_State'][1]==0 and (10,-100) not in handles and units[10]['owner']==2)
setup();cast('AOz4');windup=handles[10,-101];env['OM_Unregister'](1)
check('Removal clears windup and ball',effects[windup].get('destroyed') and 10 not in units)
setup();cast('AOz1');units[10]['x']=1400.;ticks(1)
check('Leash return has feedback and clears trail',path_ends('Return') and env['OM_State'][1]==0 and (10,-100) not in handles)
setup();env['OM_Count']=0;env['OM_Register']=actual['OM_Register'];env['OM_OnSold']=actual['OM_OnSold'];env['GetSoldUnit']=lambda:1
env['OM_OnSold']();ball=env['OM_Ball'][1]
check('Purchase registers ball before first cast',env['OM_Count']==1 and ball in units)
env['OM_OnSold']();check('Repeated acquisition cannot duplicate ball',env['OM_Count']==1)
setup();env['OM_ProtectArrival']=actual['OM_ProtectArrival'];units[2]['life']=50.;hasted=[]
env.update(GroupEnumUnitsInRange=lambda g,*a:g.extend([2]),SetWidgetLife=lambda u,h:units[u].update(life=h),
    GetWidgetLife=lambda u:units[u]['life'],GetUnitState=lambda *a:200.,UNIT_STATE_MAX_LIFE=4,OM_Haste=lambda u,d:hasted.append((u,d)))
env['OM_ProtectArrival'](1,2,400.)
check('Protect heal capped and target haste retained',units[2]['life']==200. and hasted==[(2,5.)])
check('Healed target gets heal effect',any('HealTarget' in f['model'] and f.get('unit')==2 for f in effects.values()))
setup();env['OM_Home'](1);orb=handles[10,-102];ticks(96)
check('Idle orb persists across three seconds without recreation',handles[10,-102]==orb and not effects[orb].get('destroyed') and effects[orb]['alpha']==255)
units[1].update(x=60.,y=30.,height=40.);ticks(1)
check('Idle orb follows moving elevated hero in front',effects[orb]['x']==60. and effects[orb]['y']==30. and abs(effects[orb]['z']-(100.+40.+260.))<.001 and effects[orb]['scale']==1. and 'unit' not in effects[orb])
cast('AOz1');ticks(20);parked=handles[10,-102]
check('Launching preserves visible orb and control ball',not effects[orb].get('destroyed') and parked==orb and env['OM_Ball'][1]==10)
orb=parked
check('Parked orb matches control unit position',effects[orb]['x']==units[10]['x'] and effects[orb]['y']==units[10]['y'])
cast('AOz3');gold=handles[10,-102]
check('Protect uses blue variant of same Power Orb and control ball',gold==orb and not effects[orb].get('destroyed') and env['OM_Ball'][1]==10 and effects[gold]['model'].endswith('Power_Orb.mdx') and effects[gold]['color']==(65,145,255))
ticks(20);units[2]['x']=150.;ticks(1)
check('Protect orb follows moving ally overhead at full size',effects[gold]['x']==150. and abs(effects[gold]['z']-(100.+units[2]['height']+260.))<.001 and effects[gold]['scale']==1.)
units[1]['alive']=False;ticks(1);check('Death destroys persistent orb',effects[gold].get('destroyed') and (10,-102) not in handles)
units[1]['alive']=True;ticks(1);new_orb=handles[10,-102]
check('Revive recreates visible orb',new_orb!=gold and effects[new_orb]['alpha']==255)
env['OM_Unregister'](1);check('Unregister releases persistent orb and style',effects[new_orb].get('destroyed') and (10,-102) not in handles and (10,-103) not in handles)

# Damage advances with the ring, and never repeats on a unit already swept.
for ability,animation in [('AOz1',1),('AOz2',1),('AOz3',1),('AOz4',9)]:
    setup();env['OM_Home'](1);event['spell']=ability;env['OM_OnCastAnimation']()
    check('Cast begins with model sequence '+ability,units[1]['animation']==animation and env['OM_State'][1]==0 and not hits and not timers)
setup();event['spell']='unrelated';env['OM_OnCastAnimation']()
check('Unrelated casts do not override animation','animation' not in units[1])
setup();units[1]['skin']='different hero';env['OM_OnCastAnimation']()
check('Other heroes keep native animations','animation' not in units[1])
for rank,radius in enumerate([207.9,225.225,242.55,277.2,311.85,346.5],1):
    setup();event['rank']=rank;units[3]['x']=radius;cast('AOz2')
    check('Pulse is not instantaneous rank '+str(rank),not hits)
    ticks(7);check('Outer edge waits for wave rank '+str(rank),not hits)
    ticks(1);check('Outer edge hit once at 0.25s rank '+str(rank),len(hits)==1 and len(slows)==1)
    ticks(8);check('Pulse expires without repeated damage rank '+str(rank),len(hits)==1 and all(v.get('destroyed') for v in timers.values() if v['callback']==env['OM_PulseTick']))
    setup();event['rank']=rank;units[3]['x']=radius+1.;cast('AOz2');ticks(8)
    check('Outside reduced attack radius excluded rank '+str(rank),not hits)
setup();units[3]['x']=20.;cast('AOz2');ticks(1)
check('Inner target hit on first outward step',len(hits)==1)
ticks(11);check('Inner target cannot be hit repeatedly',len(hits)==1)
setup();units[3]['x']=180.;cast('AOz2');units[10]['x']=800.;ticks(8)
check('Released pulse remains at cast center when ball moves',len(hits)==1)
setup();units[3]['x']=180.;cast('AOz2');ticks(2);cast('AOz2');ticks(10)
check('Overlapping casts have independent hit tracking',len(hits)==2)
clean();check('Pulse groups and timers release hash data',not any(k[0] in timers for k in handles))
setup();cast('AOz2');units.pop(1);ticks(1)
check('Caster removal cancels pulse and frees timer',all(v.get('destroyed') for v in timers.values() if v['callback']==env['OM_PulseTick']) and not hits)
clean()
setup();cast('AOz1');ticks(2)
trail=[(k,v) for k,v in effects.items() if v.get('scale',2)<1 and 'DenseOrb.mdx' in v['model']]
check('Move leaves stationary afterimages behind the ball',len(trail)==2 and all(v['x']<units[10]['x'] for k,v in trail))
old_positions=[v['x'] for k,v in trail];ticks(1)
check('Afterimages fade without following ball',[effects[k]['x'] for k,v in trail]==old_positions and all(effects[k]['alpha']<50 for k,v in trail))
env['OM_Home'](1);ticks(8)
check('Trail fully fades after return',all(effects[k].get('destroyed') for k,v in trail))
setup();env['OM_Haste']=actual['OM_Haste'];env['OM_Haste'](2,2.);fx=handles[2,-104]
check('Haste immediately attaches native speed scroll art',effects[fx]['model'].endswith('AIsp\\SpeedTarget.mdl') and effects[fx]['unit']==2)
ticks(32);env['OM_Haste'](2,5.)
check('Haste refresh retains one effect and extends duration',handles[2,-104]==fx and env['OM_HExpires'][1]==6.)
ticks(159);check('Speed effect persists for entire buff',not effects[fx].get('destroyed'))
ticks(1);check('Speed effect removed at buff expiry',effects[fx].get('destroyed') and (2,-104) not in handles)
setup();env['OM_Haste']=actual['OM_Haste'];env['OM_Haste'](2,2.);fx=handles[2,-104];units[2]['alive']=False;ticks(1)
check('Dead ally releases speed effect immediately',effects[fx].get('destroyed') and env['OM_Hastes']==0)
for rank,radius in enumerate([211.75,254.1,296.45],1):
    setup();event['rank']=rank;units[3]['x']=radius+.1;cast('AOz4');ticks(16)
    check('Outside reduced ultimate radius excluded rank '+str(rank),not hits)
    setup();event['rank']=rank;units[3]['x']=radius-.1;cast('AOz4');ticks(16)
    check('Inside reduced ultimate radius hit rank '+str(rank),len(hits)==1)
setup();units[3]['x']=180.;env['OM_StartPulse'](1,1)
env['OM_Hero'][1]=2;units[10]['x']=300.;env['OM_StartPulse'](1,2)
for _ in range(8):
    for t,v in list(timers.items()):
        if v['callback']==env['OM_PulseTick'] and not v.get('destroyed'):
            event['timer']=t;v['callback']()
check('Two heroes retain separate source, damage and center',sorted(hits)==[(1,3,75.),(2,3,100.)])
clean()
setup();env['OM_Home'](1);orb=handles[10,-102];cast('AOz2');ticks(4)
check('Attack expands and lifts front-held orb',handles[10,-102]==orb and abs(effects[orb]['scale']-1.18)<.001 and abs(effects[orb]['z']-(100.+units[10]['height']+20.))<.001)
ticks(4)
check('Attack gesture settles back after pulse',abs(effects[orb]['scale']-1.)<.001)
cast('AOz2');env['OM_Home'](1)
check('Recall clears active orb gesture',(10,-105) not in handles and effects[orb]['scale']==1.)
cast('AOz2');env['OM_Unregister'](1)
check('Hero removal releases gesture state',(10,-105) not in handles)
setup();env['OM_Home'](1);cast('AOz1');ticks(20);orb=handles[10,-102];cast('AOz2');ticks(4)
check('Parked Attack orb rises with pulse',abs(effects[orb]['z']-(100.+units[10]['height']+20.))<.001)
env['OM_Home'](1)
check('Recall places same small orb in front without duplication',handles[10,-102]==orb and not effects[orb].get('destroyed') and effects[orb]['x']==units[1]['x'] and effects[orb]['y']==units[1]['y'] and effects[orb]['z']==100.+units[10]['height'] and effects[orb]['scale']==1. and sum(not v.get('destroyed') and 'Power_Orb' in v['model'] and v.get('scale',0)>=1. for v in effects.values())==1)

setup();event['x']=0.;event['y']=600.;cast('AOz1');ticks(6)
glyphs=[v for v in effects.values() if v['model'].endswith('MoveGround.mdx')]
check('Move ground chevrons point along travel with bounded emission',len(glyphs)==2 and all(abs(v['yaw']-math.pi/2)<.001 and v['z']==108. for v in glyphs))
env['OM_Home'](1);ticks(10)
check('Move ground marks fade after travel ends',all(v.get('destroyed') for v in glyphs))
setup();cast('AOz2');ticks(4)
glyph=next(v for v in effects.values() if v['model'].endswith('AttackGround.mdx'))
check('Attack ground spokes expand with half-time damage wave',abs(glyph['scale']-207.9*.96*.5)<.001 and glyph['z']==108.)
ticks(8);check('Attack ground spokes finish without timer leak',glyph.get('destroyed') and all(v.get('destroyed') for v in timers.values()))
setup();cast('AOz3');ticks(20)
glyph=next(v for v in effects.values() if v['model'].endswith('ProtectGround.mdx'))
check('Protect rune appears inside unchanged healing ring',glyph['x']==100. and glyph['z']==108. and glyph['scale']<=200. and any('ProtectRing' in v['model'] and v['scale']==200. for v in effects.values()))
ticks(48);check('Protect rune expires',glyph.get('destroyed'))
setup();cast('AOz4');glyph=effects[handles[10,-108]];ticks(8)
check('Shock spiral rotates and contracts inside fixed radius ring',abs(glyph['scale']-211.75*.55)<.001 and abs(glyph['yaw']+1.25)<.001 and effects[handles[10,-101]]['scale']==211.75)
ticks(8);check('Shock impact clears spiral',glyph.get('destroyed') and (10,-108) not in handles)
setup();cast('AOz4');glyph=effects[handles[10,-108]];units[1]['alive']=False;ticks(1)
check('Death cancels Shock ground spiral immediately',glyph.get('destroyed') and (10,-108) not in handles)
setup();cast('AOz4');glyph=effects[handles[10,-108]];env['OM_Unregister'](1)
check('Hero removal cleans Shock ground spiral',glyph.get('destroyed') and (10,-108) not in handles)

setup();env['OM_Home'](1);orb=handles[10,-102];units[1]['facing']=90.;ticks(1)
check('Overhead orb stays still when hero turns',abs(effects[orb]['x'])<.001 and abs(effects[orb]['y'])<.001)
cast('AOz1');sizes=[]
for _ in range(8):ticks(1);sizes.append(effects[orb]['scale'])
check('Orb stays prominent through flight',all(size==1. for size in sizes))
cast('AOz1');ticks(1)
check('Redirecting travelling orb does not shrink it',effects[orb]['scale']==1.)
env['OM_Home'](1);check('Returning orb remains full size overhead',effects[orb]['scale']==1.)
env['OM_Unregister'](1);check('Removal cleans orb growth data',all((10,k) not in handles for k in [-109,-110,-111]))
setup();cast('AOz4');ticks(16)
check('Shockwave releases frost lightning and energy burst',all(any(name in f['model'] for f in effects.values()) for name in ['FrostNovaTarget','MonsoonBoltTarget','ShockImpact']))
clean();check('Dramatic Shockwave effects clean up',all(v.get('destroyed') for v in timers.values()) and all(v.get('destroyed') or k==handles[10,-102] for k,v in effects.items()))

(ROOT/'audit/runtime-checks.json').write_text(json.dumps({'passed':True,'checks':checks,'engine_test':False},indent=2))
print(str(len(checks))+' mocked runtime lifecycle checks passed')


