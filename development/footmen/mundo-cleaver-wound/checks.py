"""Execute actual shipped JASS with mocked native casting and lifecycle events.

This validates script behavior, not Warcraft's native animation/cast timing.
"""
from pathlib import Path
import ast, re, json, sys, copy
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'mini-foots/tools'))
import objdata
source=(R/'src/war3map.j').read_text(encoding='utf8')
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
tree=ast.parse((R.parent/'799x-backport/check_runtime.py').read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'))
names=[n for n in functions if n.startswith('MW_')]+['MU_OnCleaverHit']
code=re.sub(r'\bfunction (MW_\w+)',r'\1','\n\n'.join(translate(n) for n in names))
abilities={e['newId']:e for t in objdata.load(str(R/'src/war3map.w3a'))['tables'] for e in t}
buffs={e['newId']:e for t in objdata.load(str(R/'src/war3map.w3h'))['tables'] for e in t}
def value(e,key,level=0):return next(m['value'] for m in e['mods'] if m['id']==key and m.get('level',0)==level)
checks=[]
def check(label,ok):
    assert ok,label
    checks.append(label)

def setup():
    units={1:dict(owner=0,life=1000.,kind='HMu1',buffs=set(),abilities=set(),x=0.,y=0.),2:dict(owner=1,life=1000.,kind='hfoo',buffs={'Bspe','Bloodlust','Beng'},abilities=set(),x=50.,y=0.),3:dict(owner=1,life=1000.,kind='hfoo',buffs={'Bspe'},abilities=set(),x=90.,y=0.)}
    state=dict(next=1000,timer=None,fail=set(),silent=False,timers={},sounds={},effects={},removed=[],events=[])
    def alloc(store,v):state['next']+=1;store[state['next']]=v;return state['next']
    def remove_unit(u):
        assert u in units and units[u].get('dummy'),'only owned dummy can be removed'
        state['removed'].append(u);del units[u]
    def create(owner,kind,x,y,f):return alloc(units,dict(owner=owner,life=100.,kind=kind,buffs=set(),abilities=set(),x=x,y=y,dummy=True))
    def cast(dummy,order,target):
        ability=next(iter(units[dummy]['abilities']))
        assert units[dummy].get('castpoint')==0. and units[dummy].get('backswing')==0.
        if ability in state['fail']:return False
        if not state['silent']:units[target]['buffs'].add(value(abilities[ability],'abuf',1))
        state['events'].append(('cast',ability,target))
        return True
    def damage(a,b,d):state['events'].append(('damage',b,d));units[b]['life']-=d
    noop=lambda *a:None
    env=dict(MW_Hash={},MQ_Hash={(100,9):1,(100,10):0.},udg_MissileData=100,udg_MissileSource=1,udg_MissileHitUnit=2,udg_MissileOwner=0,udg_MissileTravelled=0.,udg_MissileDestroy=False,UNIT_TYPE_MAGIC_IMMUNE='immune',UNIT_RF_CAST_POINT='castpoint',UNIT_RF_CAST_BACK_SWING='backswing')
    env.update(GetHandleId=lambda h:h or 0,FS_Alive=lambda u:units.get(u,{}).get('kind',0)!=0 and units.get(u,{}).get('life',0)>.405,GetOwningPlayer=lambda u:units.get(u,{}).get('owner'),IsUnitType=lambda u,k:units.get(u,{}).get(k,False),BlzIsUnitInvulnerable=lambda u:units.get(u,{}).get('invulnerable',False),GetUnitAbilityLevel=lambda u,a:int(a in units.get(u,{}).get('buffs',set())),GetUnitX=lambda u:units[u]['x'],GetUnitY=lambda u:units[u]['y'],UnitRemoveAbility=lambda u,a:units.get(u,{}).get('buffs',set()).discard(a),UnitAddAbility=lambda u,a:units[u]['abilities'].add(a),CreateUnit=create,RemoveUnit=remove_unit,BlzSetUnitRealField=lambda u,k,v:units[u].update({k:v}),IssueTargetOrder=cast,UnitApplyTimedLife=noop,CreateTimer=lambda:alloc(state['timers'],{}),TimerStart=lambda t,p,r,f:state['timers'][t].update(period=p,callback=f),GetExpiredTimer=lambda:state['timer'],PauseTimer=noop,DestroyTimer=lambda t:state['timers'].pop(t),RMinBJ=min,RMaxBJ=max,MQ_Land=lambda *a:state['events'].append(('land',)),FS_Hit=damage,MU_Heal=lambda u,v:state['events'].append(('heal',u,v)),DK_GroundZ=lambda *a:0.)
    for kind in ['UnitHandle','TimerHandle','PlayerHandle','Integer','Real','Boolean']:
        env['Save'+kind]=lambda table,h,k,v:table.__setitem__((h,k),v)
        env['Load'+kind]=lambda table,h,k,kind=kind:table.get((h,k),0 if kind in ['Integer','Real','Boolean'] else None)
    env['RemoveSavedHandle']=lambda table,h,k:table.pop((h,k),None)
    env['FlushChildHashtable']=lambda table,h:[table.pop(k) for k in list(table) if k[0]==h]
    def sound(label,*args):state['events'].append(('sound',label));return alloc(state['sounds'],dict(label=label,args=args))
    env.update(CreateSoundFromLabel=sound,SetSoundChannel=noop,SetSoundVolume=noop,SetSoundDistances=noop,SetSoundDistanceCutoff=noop,SetSoundPosition=lambda h,*p:state['sounds'][h].update(position=p),StartSound=lambda h:state['sounds'][h].update(started=True),KillSoundWhenDone=lambda h:state['sounds'][h].update(auto_cleanup=True),AddSpecialEffectTarget=lambda model,u,point:alloc(state['effects'],dict(model=model,target=u,point=point)),BlzSetSpecialEffectScale=lambda h,v:state['effects'][h].update(scale=v),DestroyEffect=lambda h:state['effects'].pop(h))
    exec(code,env)
    def tick(n=1):
        for _ in range(n):
            for t in list(state['timers']):
                if t in state['timers']:state['timer']=t;state['timers'][t]['callback']()
    def clean():return not env['MW_Hash'] and not state['timers'] and not any(v.get('dummy') for v in units.values())
    return env,units,state,tick,clean

e,u,s,tick,clean=setup();e['MW_Start'](1,2)
check('Impact removes only target speed-scroll haste',u[2]['buffs']=={'Bloodlust','Beng','BMwR','BMwS'} and 'Bspe' in u[3]['buffs'])
check('One per-target timer, two zero-castpoint helpers',len(s['timers'])==1 and sum(v.get('dummy',False) for v in u.values())==2)
tick(7);check('Root still active at 0.175 seconds','BMwR' in u[2]['buffs'])
tick();check('Private root explicitly cleared at 0.200 seconds','BMwR' not in u[2]['buffs'] and 'BMwS' in u[2]['buffs'] and 'Beng' in u[2]['buffs'])
u[2]['buffs'].add('Bspe');tick();check('Speed Scroll reapplied during wound suppressed on next 25ms tick','Bspe' not in u[2]['buffs'])
tick(78);check('Slow remains through 2.175 seconds','BMwS' in u[2]['buffs'])
tick();check('Slow, timer, and helpers cleared at 2.200 seconds',clean() and u[2]['buffs']=={'Bloodlust','Beng'})
u[2]['buffs'].add('Bspe');tick();check('Speed Scroll works after expiry','Bspe' in u[2]['buffs'])

for why in ['death','removed','owner','immune','invulnerable','dispel']:
    e,u,s,tick,clean=setup();e['MW_Start'](1,2);tick(4)
    if why=='death':u[2]['life']=0.
    elif why=='removed':del u[2]
    elif why=='owner':u[2]['owner']=0
    elif why=='immune':u[2]['immune']=True
    elif why=='invulnerable':u[2]['invulnerable']=True
    else:u[2]['buffs'].discard('BMwS')
    tick();check(why+' releases owned state without leaks',clean())
    if 2 in u:check(why+' leaves no private movement buff',not {'BMwR','BMwS'} & u[2]['buffs'])

e,u,s,tick,clean=setup();e['MW_Start'](1,2);tick(6);old=next(iter(s['timers']));e['MW_Start'](1,2)
check('Rehit replaces timer and does not stack',len(s['timers'])==1 and old not in s['timers'] and sum(v.get('dummy',False) for v in u.values())==2)
tick(7);check('Refreshed root lasts its own 0.2 seconds','BMwR' in u[2]['buffs']);tick(81);check('Refreshed wound cleans',clean())
e,u,s,tick,clean=setup();e['MW_Start'](1,2);tick(8);e['MW_Start'](1,3);tick(80)
check('Two victims have independent expiry','BMwS' not in u[2]['buffs'] and 'BMwS' in u[3]['buffs']);tick(8);check('Two-victim cleanup',clean())

for failed in ['AMwR','AMwS']:
    e,u,s,tick,clean=setup();s['fail'].add(failed);e['MW_Start'](1,2);tick(88)
    check('Failed '+failed+' order cannot leak helpers or lock',clean() and not {'BMwR','BMwS'} & u[2]['buffs'])
e,u,s,tick,clean=setup();s['silent']=True;e['MW_Start'](1,2);tick(4)
check('Accepted order with no applied slow cleans after grace',clean())
e,u,s,tick,clean=setup();e['MU_OnCleaverHit']();check('Hit produces sound once before damage',len(s['sounds'])==1 and [a[0] for a in s['events']][:3]==['land','sound','damage'])
check('Sound is positional/self-cleaning and blood effect released',all(v.get('started') and v.get('auto_cleanup') and v.get('position') for v in s['sounds'].values()) and not s['effects'])
check('Hit preserves damage, refund and landing semantics',('damage',2,80.) in s['events'] and ('heal',1,25.) in s['events'] and e['udg_MissileDestroy'])
tick(88);check('Full hit cleanup',clean())
e,u,s,tick,clean=setup();u[2]['life']=1.;e['MU_OnCleaverHit']();check('Lethal hit still has impact sound and no control helpers',len(s['sounds'])==1 and clean())

for uid in ['AMwR','AMwS']:
    check(uid+' has no projectile or spell art',all(value(abilities[uid],k)=='' for k in ['amat','atat','acat','aeat','asat']))
for uid in ['BMwR','BMwS']:
    check(uid+' has no inherited net or slow model',all(value(buffs[uid],k)=='' for k in ['ftat','feat','fsat','fmat','flig']))
check('Native root hero and unit durations are 0.2',all(abs(value(abilities['AMwR'],k,1)-.2)<1e-6 for k in ['adur','ahdu']))
check('Native slow is 70%, no attack slow, total 2.2 seconds',abs(value(abilities['AMwS'],'Slo1',1)-.7)<1e-6 and value(abilities['AMwS'],'Slo2',1)==0 and all(abs(value(abilities['AMwS'],k,1)-2.2)<1e-6 for k in ['adur','ahdu']))
check('Hit callback no longer calls old shared root/slow',"'AMqr'" not in functions['MU_OnCleaverHit'] and "'AMus'" not in functions['MU_OnCleaverHit'])
check('No full-unit pause, broad dispel or forced movement used',not any(n in '\n'.join(functions[n] for n in names) for n in ['PauseUnit(', 'BlzPauseUnitEx(', 'UnitRemoveBuffs(', 'SetUnitX(', 'SetUnitY(', 'SetUnitPosition(']))
report=dict(passed=len(checks),checks=checks,scope='Actual JASS translated with mocked Warcraft natives; native control timing, root interaction with attacks/channeling and audible/visual rendering need in-game testing.')
(R/'checks.json').write_text(json.dumps(report,indent=2))
print(f'{len(checks)} behavior/object checks passed.')
