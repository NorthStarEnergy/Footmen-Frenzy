"""Execute the shipped JASS bodies with strict mocked Warcraft natives.

These are logic/lifecycle tests, not an in-engine visual or balance playtest.
"""
from pathlib import Path
from collections import defaultdict
import math, re, ast, json, random
R=Path(__file__).resolve().parent
source=(R/'spell.j').read_text()
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
tree=ast.parse((R.parent/'799x-backport/check_runtime.py').read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
code=re.sub(r'\bfunction (LX_\w+)',r'\1','\n\n'.join(translate(n) for n in functions))
checks=[]
def check(label,v):
    assert v,label
    checks.append(label)

def setup():
    units={1:dict(x=0.,y=0.,owner=0,life=1200.,kind='HLx1',rank=1,intelligence=35,locks=0,facing=0.,mana=1500.),2:dict(x=1000.,y=0.,owner=1,life=1000.,kind='hfoo',rank=0,intelligence=0,locks=0)}
    state=dict(next=1000,timer=None,caster=1,spell='ALxR',target=(100.,0.),damage=[],effects={},groups={},timers={},sounds={},fog={},triggers={},bounds=(-10000.,10000.,-10000.,10000.),player=0,command='-lux',humans=1)
    def alloc(store,v):
        state['next']+=1;store[state['next']]=v;return state['next']
    def destroy(store,h):
        assert h in store,('double free or invalid handle',h)
        del store[h]
    def setfx(f,**k):state['effects'][f].update(k)
    def lock(u,b):
        units[u]['locks']+=1 if b else -1
        assert units[u]['locks']>=0,'unbalanced pause'
    def sound(path,*args):return alloc(state['sounds'],dict(path=path,args=args,playing=False))
    def stop(s,*args):destroy(state['sounds'],s)
    def kill(s):state['sounds'][s]['auto_cleanup']=True
    def damage(c,u,d,*a):
        assert c in units and units[c]['kind']!=0
        state['damage'].append((c,u,d))
        if state.get('on_damage'):state['on_damage'](c,u,d)
        return True
    def createunit(p,k,x,y,f):return alloc(units,dict(x=x,y=y,owner=p,kind=k,life=1200.,rank=1,intelligence=35,locks=0,mana=1500.,facing=f))
    noop=lambda *a:None
    env=dict(LX_ABILITY='ALxR',LX_RANGE=3400.,LX_HALF_WIDTH=100.,LX_CHARGE=1.,LX_TICK=.03125,LX_SEGMENTS=8,LX_Hash={},LX_Casters={},LX_Hero=defaultdict(lambda:None),udg_mode_debugmode=False,FF_TestRecruited=[],bj_DEGTORAD=math.pi/180,bj_RADTODEG=180/math.pi,bj_mapInitialPlayableArea=1,UNIT_TYPE_STRUCTURE='building',UNIT_TYPE_MAGIC_IMMUNE='immune',ATTACK_TYPE_NORMAL=1,DAMAGE_TYPE_MAGIC=2,WEAPON_TYPE_WHOKNOWS=0,UNIT_STATE_MANA=1,UNIT_STATE_MAX_MANA=2,FOG_OF_WAR_VISIBLE=1,PLAYER_SLOT_STATE_PLAYING=1,MAP_CONTROL_USER=1,EVENT_PLAYER_UNIT_SPELL_EFFECT=1)
    env.update(RMinBJ=min,RMaxBJ=max,R2I=int,I2R=float,Cos=math.cos,Sin=math.sin,Atan2=math.atan2,GetHandleId=lambda h:h or 0,
        GetUnitTypeId=lambda u:units.get(u,{}).get('kind',0),GetWidgetLife=lambda u:units.get(u,{}).get('life',0.),GetOwningPlayer=lambda u:units.get(u,{}).get('owner'),GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],GetUnitFacing=lambda u:units[u]['facing'],GetHeroInt=lambda u,b:units[u]['intelligence'],GetUnitAbilityLevel=lambda u,a:units.get(u,{}).get('rank',0) if a=='ALxR' else int(units.get(u,{}).get(a,False)),IsUnitIllusion=lambda u:units[u].get('illusion',False),IsUnitEnemy=lambda u,p:units[u]['owner']!=p,IsUnitType=lambda u,k:units[u].get(k,False),BlzIsUnitInvulnerable=lambda u:units[u].get('invulnerable',False),
        GetTriggerUnit=lambda:state['caster'],GetSpellAbilityId=lambda:state['spell'],GetSpellTargetX=lambda:state['target'][0],GetSpellTargetY=lambda:state['target'][1],GetExpiredTimer=lambda:state['timer'],Location=lambda x,y:(x,y),GetLocationZ=lambda p:state.get('terrain',lambda x,y:0.)(*p),RemoveLocation=noop,
        CreateTimer=lambda:alloc(state['timers'],{}),TimerStart=lambda t,d,r,f:state['timers'][t].update(period=d,repeat=r,callback=f),PauseTimer=noop,DestroyTimer=lambda t:destroy(state['timers'],t),BlzPauseUnitEx=lock,SetUnitAnimation=lambda u,a:units[u].update(animation=a),SetUnitFacing=lambda u,f:units[u].update(facing=f),
        AddSpecialEffect=lambda model,x,y:alloc(state['effects'],dict(model=model,x=x,y=y,z=0.,alpha=255)),DestroyEffect=lambda h:destroy(state['effects'],h),BlzSetSpecialEffectZ=lambda h,z:setfx(h,z=z),BlzSetSpecialEffectPosition=lambda h,x,y,z:setfx(h,x=x,y=y,z=z),BlzSetSpecialEffectScale=lambda h,v:setfx(h,scale=v),BlzSetSpecialEffectAlpha=lambda h,v:setfx(h,alpha=v),BlzSetSpecialEffectColor=lambda h,*v:setfx(h,color=v),BlzResetSpecialEffectMatrix=lambda h:setfx(h,matrix=(1.,1.,1.)),BlzSetSpecialEffectMatrixScale=lambda h,*v:setfx(h,matrix=v),BlzSetSpecialEffectOrientation=lambda h,*v:setfx(h,orientation=v),
        CreateGroup=lambda:alloc(state['groups'],[]),DestroyGroup=lambda h:destroy(state['groups'],h),FirstOfGroup=lambda g:state['groups'][g][0] if state['groups'][g] else None,GroupRemoveUnit=lambda g,u:state['groups'][g].remove(u),GroupAddUnit=lambda g,u:g.append(u),GroupEnumUnitsInRange=lambda g,x,y,r,f:state['groups'][g].extend(u for u,v in units.items() if math.hypot(v['x']-x,v['y']-y)<=r),UnitDamageTarget=damage,
        CreateFogModifierRadius=lambda *a:alloc(state['fog'],dict(args=a)),FogModifierStart=lambda h:state['fog'][h].update(active=True),FogModifierStop=lambda h:state['fog'][h].update(active=False),DestroyFogModifier=lambda h:destroy(state['fog'],h),
        CreateSound=sound,SetSoundChannel=noop,SetSoundVolume=lambda h,v:state['sounds'][h].update(volume=v),SetSoundDistances=noop,SetSoundDistanceCutoff=noop,SetSoundPosition=lambda h,*p:state['sounds'][h].update(position=p),StartSound=lambda h:state['sounds'][h].update(playing=True),StopSound=stop,KillSoundWhenDone=kill,
        GetRectMinX=lambda r:state['bounds'][0],GetRectMaxX=lambda r:state['bounds'][1],GetRectMinY=lambda r:state['bounds'][2],GetRectMaxY=lambda r:state['bounds'][3],
        Player=lambda i:i,GetPlayerId=lambda p:p,GetPlayerSlotState=lambda p:1 if p<state['humans'] else 0,GetPlayerController=lambda p:1,GetTriggerPlayer=lambda:state['player'],GetEventPlayerChatString=lambda:state['command'],GetPlayerStartLocation=lambda p:p,GetStartLocationX=lambda p:0.,GetStartLocationY=lambda p:0.,CreateUnit=createunit,SetHeroLevel=lambda u,l,b:units[u].update(level=l),ReviveHero=lambda u,x,y,b:units[u].update(life=1200.,x=x,y=y),SelectUnitForPlayerSingle=lambda u,p:state.update(selected=u),SetUnitAbilityLevel=lambda u,a,r:units[u].update(rank=r),BlzEndUnitAbilityCooldown=lambda u,a:units[u].update(refreshed=True),SetUnitState=lambda u,s,v:units[u].update(mana=v),GetUnitState=lambda u,s:1500.,DisplayTimedTextToPlayer=lambda *a:state.update(message=a[-1]),
        CreateTrigger=lambda:alloc(state['triggers'],dict(events=[],actions=[])),TriggerRegisterAnyUnitEventBJ=lambda t,e:state['triggers'][t]['events'].append(e),TriggerAddAction=lambda t,a:state['triggers'][t]['actions'].append(a),TriggerRegisterPlayerChatEvent=lambda t,*a:state['triggers'][t]['events'].append(a),InitHashtable=dict)
    for kind in ['UnitHandle','PlayerHandle','TimerHandle','EffectHandle','SoundHandle','FogModifierHandle','Real','Integer','Boolean']:
        env['Save'+kind]=lambda table,h,k,v:table.__setitem__((h,k),v)
        env['Load'+kind]=lambda table,h,k,kind=kind:table.get((h,k),False if kind=='Boolean' else 0. if kind in ['Real','Integer'] else None)
    env['RemoveSavedHandle']=lambda table,h,k:table.pop((h,k),None)
    env['FlushChildHashtable']=lambda table,h:[table.pop(k) for k in list(table) if k[0]==h]
    exec(code,env)
    def cast(caster=1,target=None):
        state['caster']=caster
        if target is not None:state['target']=target
        old=set(state['timers']);env['LX_Cast']();new=set(state['timers'])-old
        return next(iter(new)) if new else None
    def tick(n=1,only=None):
        for _ in range(n):
            for t in [only] if only is not None else list(state['timers']):
                if t not in state['timers']:continue
                state['timer']=t;state['timers'][t]['callback']()
    def clean():
        tick(48)
        for h,v in list(state['sounds'].items()):
            if v.get('auto_cleanup'):del state['sounds'][h]
        return not any(state[k] for k in ['timers','effects','fog','groups','sounds']) and not env['LX_Hash'] and not env['LX_Casters'] and all(u['locks']==0 for u in units.values())
    return env,units,state,cast,tick,clean

if __name__=='__main__':
    e,u,s,cast,tick,clean=setup()
    for point,want in [((0,0),True),((3400,100),True),((3400,-100),True),((3400.001,0),False),((-.001,0),False),((1700,100.001),False),((1700,-100.001),False),((0,101),False)]:
        check('Finite beam boundary '+str(point),e['LX_InBeam'](*point,0.,0.,1.,0.,3400.)==want)
    rng=random.Random(840)
    for _ in range(2000):
        a=rng.uniform(-math.pi,math.pi);along=rng.uniform(-50,3500);across=rng.uniform(-150,150);x=rng.uniform(-500,500);y=rng.uniform(-500,500);dx=math.cos(a);dy=math.sin(a)
        assert e['LX_InBeam'](x+dx*along-dy*across,y+dy*along+dx*across,x,y,dx,dy,3400.)==(0<=along<=3400 and abs(across)<=100)
    check('2000 randomized rotated finite-rectangle hit checks',True)
    t=cast();check('Cast creates one timer, 41 effects and 8 temporary vision areas',len(s['timers'])==1 and len(s['effects'])==41 and len(s['fog'])==8)
    check('Caster locked during charge',u[1]['locks']==1)
    guide=e['LX_Hash'][t,100];body=e['LX_Hash'][t,101]
    check('Faint thin initial line, invisible blast body',s['effects'][guide]['matrix'][1]==4 and s['effects'][guide]['alpha']==30 and s['effects'][body]['alpha']==0)
    tick(16);check('Charge visibly intensifies',s['effects'][guide]['alpha']>30 and s['effects'][guide]['matrix'][1]>4)
    tick(15);check('No damage or release before one full second',not s['damage'] and u[1]['locks']==1)
    tick();check('Exactly one damage event at 1 second',s['damage']==[(1,2,435.)])
    check('Blast full width and white core on the damage tick',s['effects'][body]['matrix'][1]>=200 and s['effects'][body]['alpha']>0 and s['effects'][guide]['color']==(255,255,235))
    check('Caster released immediately after fire',u[1]['locks']==0 and not e['LX_Casters'])
    check('Charge audio replaced with self-cleaning blast',len(s['sounds'])==1 and next(iter(s['sounds'].values())).get('auto_cleanup'))
    tick(8);check('Afterglow never repeats damage',len(s['damage'])==1)
    check('Complete normal cleanup without leaked handles',clean())

    for rank,want in [(1,435.),(2,685.),(3,935.)]:
        e,u,s,cast,tick,clean=setup();u[1]['rank']=rank;cast();tick(32)
        check('Rank '+str(rank)+' damage and Intelligence scaling',s['damage']==[(1,2,want)]);assert clean()
    for prop,value in [('owner',0),('building',True),('immune',True),('invulnerable',True),('Aloc',True),('life',0.),('life',.405),('kind',0)]:
        e,u,s,cast,tick,clean=setup();u[2][prop]=value;cast();tick(32)
        check('Target exclusion '+prop+'='+str(value),not s['damage']);assert clean()
    e,u,s,cast,tick,clean=setup();u[2]['flying']=True;cast();tick(32);check('Flying enemy hit',len(s['damage'])==1);assert clean()
    for pos in [(3399.,99.),(3400.,100.),(0.,0.),(425.,0.),(850.,0.)]:
        e,u,s,cast,tick,clean=setup();u[2].update(x=pos[0],y=pos[1]);cast();tick(32)
        check('Hit once at range/segment boundary '+str(pos),len(s['damage'])==1);assert clean()
    for pos in [(3401.,0.),(-1.,0.),(1000.,101.)]:
        e,u,s,cast,tick,clean=setup();u[2].update(x=pos[0],y=pos[1]);cast();tick(32)
        check('Miss beyond beam '+str(pos),not s['damage']);assert clean()
    e,u,s,cast,tick,clean=setup();cast();tick(31);u[2]['y']=101.;tick();check('Enemy can dodge during warning',not s['damage']);assert clean()
    e,u,s,cast,tick,clean=setup();u[2]['y']=200.;cast();tick(31);u[2]['y']=99.;tick();check('Enemy entering beam before impact is hit',len(s['damage'])==1);assert clean()
    e,u,s,cast,tick,clean=setup();cast();tick(16);u[1]['intelligence']=999;u[1]['rank']=3;tick(16);check('Rank and Intelligence snapshot at cast',s['damage']==[(1,2,435.)]);assert clean()
    e,u,s,cast,tick,clean=setup();t=cast();u[1].update(x=500.,y=500.,facing=180.);tick(32);check('Forced movement cannot redirect or move committed laser',s['damage']==[(1,2,435.)] and e['LX_Hash'][t,2]==0.);assert clean()
    for reason in ['death','removal','owner']:
        e,u,s,cast,tick,clean=setup();cast();tick(16)
        if reason=='death':u[1]['life']=0.
        elif reason=='removal':del u[1]
        else:u[1]['owner']=2
        tick();check(reason+' cancels charge, damage and sounds',not s['damage'] and clean())
    e,u,s,cast,tick,clean=setup();cast();tick(32);u[1]['life']=0.;tick();check('Death after firing preserves fading blast',bool(s['effects']) and len(s['damage'])==1);assert clean()
    e,u,s,cast,tick,clean=setup();u[1]['locks']=1;cast();tick(32);check('Releases only its own counted pause',u[1]['locks']==1);u[1]['locks']=0;assert clean()
    for reason in ['illusion','unrelated','unlearned','dead']:
        e,u,s,cast,tick,clean=setup()
        if reason=='illusion':u[1]['illusion']=True
        elif reason=='unrelated':s['spell']='AVgr'
        elif reason=='unlearned':u[1]['rank']=0
        else:u[1]['life']=0.
        check('Ignore '+reason+' cast',cast() is None and clean())
    e,u,s,cast,tick,clean=setup();t=cast();check('Duplicate event cannot create a second charging cast',cast() is None and len(s['timers'])==1);assert clean()
    e,u,s,cast,tick,clean=setup();a=cast();tick(32);b=cast();tick(14)
    check('Old afterglow cleanup cannot release newer caster lock',a not in s['timers'] and b in s['timers'] and u[1]['locks']==1 and e['LX_Casters'][1,0]==b)
    tick(18);check('Same caster can recast after firing independently',len(s['damage'])==2);assert clean()
    e,u,s,cast,tick,clean=setup();u[3]=dict(u[1],owner=2,rank=3);a=cast();b=cast(3);tick(32)
    check('Two casters have independent damage, owner and visual state',(1,2,435.) in s['damage'] and (3,2,935.) in s['damage'] and a!=b);assert clean()
    for target,facing,want in [((0.,0.),90.,(0.,1.)),((0.,100.),0.,(0.,1.)),((-100.,0.),0.,(-1.,0.)),((0.,-100.),0.,(0.,-1.))]:
        e,u,s,cast,tick,clean=setup();u[1]['facing']=facing;t=cast(target=target)
        check('Direction and zero-distance aim '+str(target),abs(e['LX_Hash'][t,4]-want[0])<1e-6 and abs(e['LX_Hash'][t,5]-want[1])<1e-6);assert clean()
    for origin,target,want in [((3200.,0.),(3300.,0.),128.),((-3200.,0.),(-3300.,0.),128.),((0.,2900.),(0.,3000.),172.),((0.,-3500.),(0.,-3550.),84.)]:
        e,u,s,cast,tick,clean=setup();s['bounds']=(-3328.,3328.,-3584.,3072.);u[1].update(x=origin[0],y=origin[1]);t=cast(target=target)
        check('Clip beam at playable edge '+str(origin),abs(e['LX_Hash'][t,8]-want)<1e-5);assert clean()
    e,u,s,cast,tick,clean=setup();s['terrain']=lambda x,y:x*.2;t=cast()
    fx=s['effects'][e['LX_Hash'][t,100]]
    check('Terrain pitch retains continuous horizontal segment length',abs(fx['matrix'][0]*math.cos(fx['orientation'][1])-425.)<.03)
    assert clean()
    e,u,s,cast,tick,clean=setup();e['LX_Summon']();hero=s['selected'];e['LX_Summon']();check('Test summon reuses one extra hero',len(u)==3 and s['selected']==hero and e['FF_TestRecruited']==[hero]);s['command']='-lux3';e['LX_Summon']();check('Test rank command refreshes the same caster',u[hero]['rank']==3 and u[hero]['refreshed']);u[hero]['life']=0.;e['LX_Summon']();check('Dead test hero revives without duplication',u[hero]['life']>0. and len(u)==3)
    e,u,s,cast,tick,clean=setup();s['humans']=2;e['LX_Summon']();check('Public multiplayer cannot summon a free test hero',len(u)==2 and 'Debug' in s['message']);e['udg_mode_debugmode']=True;e['LX_Summon']();check('Debug multiplayer permits test caster',len(u)==3)
    e,u,s,cast,tick,clean=setup();e['LX_Init']();check('Initialization registers spell event and exact commands for 12 players',len(s['triggers'])==2 and sorted(len(v['events']) for v in s['triggers'].values())==[1,36])
    # Sustained casting: count every resource after each finished sequence.
    e,u,s,cast,tick,clean=setup()
    for _ in range(100):cast();assert clean()
    check('100 consecutive casts leave no timer, effect, group, vision, sound or hashtable leaks',True)
    report=dict(passed=len(checks),checks=checks,random_geometry_cases=2000,scope='Actual JASS translated with strict mocked natives. Engine visuals, native targeting and balance still require Warcraft playtesting.')
    (R/'checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
