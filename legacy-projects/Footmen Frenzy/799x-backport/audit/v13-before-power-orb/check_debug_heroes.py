"""Execute translated debug recruitment handlers against a small engine mock."""
from pathlib import Path
from collections import defaultdict
import ast, json, re

ROOT = Path(__file__).resolve().parent
source = (ROOT/'src/war3map.j').read_text()
functions = {m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction', source)}
# Reuse just the translator definitions, without executing Orianna's test suite.
tree = ast.parse((ROOT/'check_runtime.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('expression','translate')],type_ignores=[]),'<translator>','exec'))
names = ['FF_DebugOpenHiring','FF_DebugHeroReady','FF_DebugHireComplete','FF_DebugHeroSold','FF_TestExtraHero']
env = {}
exec(re.sub(r'\bfunction (FF_\w+)',r'\1','\n\n'.join(translate(n) for n in names)),env)
checks = []

def check(name, result):
    assert result, name
    checks.append(name)

def setup(debug=True):
    global units, handles, timers, events, quotas, stock, log
    units = {1:dict(kind='HOr1',owner=0,hero=True,level=1,food=True,stats={},items=[]),
             2:dict(kind='HGr1',owner=0,hero=True,level=1,food=True,stats={},items=[]),
             3:dict(kind='hfoo',owner=0,hero=False,level=1,food=True),
             4:dict(kind='HOr1',owner=15,hero=True,level=1,food=True),
             20:dict(kind='tavern',owner=15,hero=False)}
    handles = {}; timers = {}; events = {'sold':1,'shop':20}; quotas = {}; stock = {}; log = []
    def timer():
        t=100+len(timers);timers[t]={};return t
    def level(u,n,_):
        log.append(('level',u,n));units[u]['level']=n
        for stat in ('str','agi','int'):
            units[u]['stats'][stat]=units[u]['stats'].get(stat,0)+(n-1)*units[u].get(stat+'Inc',0)
    noop=lambda *a:None
    env.update(udg_mode_debugmode=debug,FF_DebugHireHash=99,udg_total_hero_count=2,
        udg_hero_type={1:'HOr1',2:'HGr1'},udg_herO={1:1},udg_picked_hero={1:1},FF_TestRecruited=[],
        UNIT_TYPE_HERO='hero',PLAYER_STATE_FOOD_CAP_CEILING='ceiling',PLAYER_STATE_RESOURCE_FOOD_CAP='cap',
        UNIT_RF_STRENGTH_PER_LEVEL='strInc',UNIT_RF_AGILITY_PER_LEVEL='agiInc',UNIT_RF_INTELLIGENCE_PER_LEVEL='intInc',UNIT_RF_TURN_RATE='turn',
        SetPlayerMaxHeroesAllowed=lambda n,p:quotas.update({(p,'heroes'):n}),SetPlayerState=lambda p,k,v:quotas.update({(p,k):v}),
        SetPlayerTechMaxAllowed=lambda p,k,v:quotas.update({(p,k):v}),
        GetUnitTypeId=lambda u:units.get(u,{}).get('kind',0),IsUnitType=lambda u,k:units.get(u,{}).get('hero',False),
        GetOwningPlayer=lambda u:units[u]['owner'],GetPlayerId=lambda p:p,GetConvertedPlayerId=lambda p:p+1,
        SetUnitUseFood=lambda u,b:units[u].update(food=b),GetHeroLevel=lambda u:units[u]['level'],SetHeroLevel=level,
        GetSoldUnit=lambda:events['sold'],GetSellingUnit=lambda:events['shop'],GetExpiredTimer=lambda:events['timer'],GetHandleId=lambda h:h,
        CreateTimer=timer,TimerStart=lambda t,d,r,c:timers[t].update(callback=c,delay=d),DestroyTimer=lambda t:timers[t].update(destroyed=True),
        SaveUnitHandle=lambda h,k,n,v:handles.update({(k,n):v}),SaveInteger=lambda h,k,n,v:handles.update({(k,n):v}),
        LoadUnitHandle=lambda h,k,n:handles.get((k,n)),LoadInteger=lambda h,k,n:handles.get((k,n),0),
        FlushChildHashtable=lambda h,k:[handles.pop(a) for a in list(handles) if a[0]==k],
        RemoveUnitFromStock=lambda s,k:stock.pop((s,k),None),AddUnitToStock=lambda s,k,a,b:stock.update({(s,k):(a,b)}),
        GetPlayerStartLocationLoc=lambda p:p,SetUnitPositionLoc=noop,RemoveLocation=noop,
        IsUnitInGroup=lambda u,g:u in g,GroupAddUnit=lambda g,u:g.append(u),R2I=int,
        SetHeroStr=lambda u,n,b:units[u]['stats'].update(str=n),SetHeroAgi=lambda u,n,b:units[u]['stats'].update(agi=n),SetHeroInt=lambda u,n,b:units[u]['stats'].update(int=n),
        BlzSetUnitRealField=lambda u,k,v:units[u].update({k:v}),SetUnitMoveSpeed=noop,
        UnitAddItemById=lambda u,item:units[u]['items'].append(item),SelectUnitForPlayerSingle=noop)
    for key in ('STR','AGI','INT'):
        env['udg_hero_'+key+'_base']={1:20.,2:30.}
        env['udg_hero_'+key+'_inc']={1:2.,2:3.}
    env['udg_hero_move_base']={1:350.,2:300.};env['udg_hero_turnrate']={1:1.,2:1.}

def finish():
    for t,v in list(timers.items()):
        if not v.get('destroyed'):
            events['timer']=t;v['callback']()

setup(False);env['FF_DebugOpenHiring'](0);env['FF_DebugHeroReady'](1);env['FF_DebugHeroSold']();finish()
check('Normal mode leaves levels, food, quotas and stock unchanged',units[1]['level']==1 and units[1]['food'] and not quotas and not timers and not stock)
setup();env['FF_DebugOpenHiring'](0)
check('Debug removes aggregate and per-hero quotas',all(quotas[0,k]==-1 for k in ('heroes','HOr1','HGr1')))
check('Debug allows initial purchase food headroom',quotas[0,'cap']==300 and quotas[0,'ceiling']==300)
env['FF_DebugHeroReady'](1)
check('First debug hero reaches level 18 and uses no food',units[1]['level']==18 and not units[1]['food'])
env['FF_TestExtraHero'](2)
check('Additional hero reaches level 18 after base stats and growth setup',units[2]['level']==18 and units[2]['stats']==dict(str=81.,agi=81.,int=81.))
check('Additional hero retains original primary-hero tracking',env['udg_herO']=={1:1} and env['udg_picked_hero']=={1:1})
env['FF_TestExtraHero'](2);env['FF_DebugHeroReady'](2)
check('Repeated callbacks do not duplicate starting items or levels',len(units[2]['items'])==4 and sum(x[1]==2 for x in log)==1)
env['FF_DebugHeroReady'](3);env['FF_DebugHeroReady'](4)
check('Nonheroes and neutral showroom heroes stay unchanged',units[3]['level']==1 and units[3]['food'] and units[4]['level']==1 and units[4]['food'])
setup();env['FF_DebugHeroSold']()
check('Sale defers work until engine and initialization finish',units[1]['level']==1 and timers[100]['delay']==0.)
finish();check('Sale restores stock and readies purchased hero',stock[20,'HOr1']==(2,2) and units[1]['level']==18 and not units[1]['food'])
check('Sale callback releases handles and timer',not handles and all(v.get('destroyed') for v in timers.values()))
for _ in range(100):
    env['FF_DebugHeroSold']();finish()
check('Repeated purchases keep stock available without consuming food',stock[20,'HOr1']==(2,2) and not units[1]['food'] and len(log)==1)
setup();events['sold']=3;env['FF_DebugHeroSold']();events['sold']=4;env['FF_DebugHeroSold']()
check('Nonhero and neutral sales do not create debug callbacks',not timers)
setup();env['FF_DebugHeroSold']();units.pop(1);finish()
check('Removed purchase still restocks safely and releases handles',stock[20,'HOr1']==(2,2) and not handles)
setup();env['FF_DebugHeroSold']();units.pop(20);finish()
check('Removed seller is not restocked',not stock and not handles)
setup();env['FF_DebugHeroSold']();env['udg_mode_debugmode']=False;finish()
check('Callback rechecks debug mode',units[1]['level']==1 and units[1]['food'] and not stock and not handles)
check('Primary hero level assigned after all initial stats',functions['Trig_TP_hero_Actions'].rfind('call FF_DebugHeroReady') > functions['Trig_TP_hero_Actions'].rfind('UNIT_IF_STRENGTH'))
check('Additional random hires are permitted only with debug override','and (udg_herO[pn] == null or udg_mode_debugmode) then' in functions['FFRandom_Sold'])
(ROOT/'audit/debug-hiring-checks.json').write_text(json.dumps({'passed':True,'engine_test':False,'checks':checks},indent=2))
print(str(len(checks))+' debug recruitment checks passed')
