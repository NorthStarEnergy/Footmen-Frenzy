"""Execute the edited JASS control flow with mocked Warcraft natives."""
from pathlib import Path
import re, math, collections, json
ROOT=Path(__file__).resolve().parent
s=(ROOT/'src/war3map.j').read_text()
names=['SF_CenterBaseCamera','SF_FlipRecipePage','SF_RefreshPage','SF_OpenTaverns','SF_OnSale','SF_StartBaseSelection','SF_Initialize','Trig_Start_game_Func024Func001A','Trig_Start_game_Func024Func002A']
def translate(name):
    block=re.search(r'^function '+name+r'\b.*?^endfunction',s,re.M|re.S)[0].splitlines()
    sig=re.match(r'function \w+ takes (.*?) returns',block[0])[1]
    args=[] if sig=='nothing' else [v.strip().split()[-1] for v in sig.split(',')]
    locals_=args+[re.match(r'\s*local \w+ (\w+)',line)[1] for line in block if re.match(r'\s*local \w+ (\w+)',line)]
    assigned=set(re.findall(r'^\s*set (\w+)\s*=', '\n'.join(block),re.M))-set(locals_)
    out=['def '+name+'('+','.join(args)+'):']
    if assigned:out.append('    global '+','.join(sorted(assigned)))
    level=1
    for line in block[1:-1]:
        line=line.split('//')[0].strip()
        if not line:continue
        line=re.sub(r'\b(true|false|null)\b',lambda m:{'true':'True','false':'False','null':'None'}[m[1]],line)
        line=re.sub(r'\bfunction (\w+)',r'\1',line)
        if line.startswith('local '):
            line=re.sub(r'^local \w+ ','',line)
            if '=' not in line:line+='=None'
        elif line.startswith('set '):line=line[4:]
        elif line.startswith('call '):line=line[5:]
        elif line=='loop':line='while True:'
        elif line.startswith('exitwhen '):line='if '+line[9:]+': break'
        elif line.startswith('if '):line=line[:-5]+':'
        elif line.startswith('elseif '):level-=1;line='elif '+line[7:-5]+':'
        elif line=='else':level-=1;line='else:'
        elif line in ['endif','endloop']:level-=1;continue
        out.append('    '*level+line)
        if line.endswith(':'):level+=1
    return '\n'.join(out)
translated='\n\n'.join(translate(n) for n in names)
(ROOT/'behavior-translated.py').write_text(translated)
e={};created=[];timers=[];cameras=[];selections=[];flags={};poolidx=collections.defaultdict(int)
globals_block=re.search(r'^globals\s*$(.*?)^endglobals',s,re.M|re.S)[1]
for typ,array,name in re.findall(r'^\s*(?:constant )?(\w+)\s+(?:(array)\s+)?(\w+)\s*(?:=|$)',globals_block,re.M):
    default=False if typ=='boolean' else '' if typ=='string' else 0 if typ in ['integer','real'] else None
    e[name]=collections.defaultdict(lambda d=default:d) if array else default
slots=[0,4,7,11,1,3,6,9]
for p in slots:
    e['udg_player_active'][p+1]=True
    e['udg_base'][p+1]={'owner':p,'x':100+p,'y':200+p}
def create(owner,kind,x,y,a):
    u=dict(owner=owner,kind=kind,x=x,y=y,facing=a,stock=set(),items=set(),removed=False)
    created.append(u);return u
def take(p,category):poolidx[p]+=1;return poolidx[p] if poolidx[p]<=24 else 0
def tick(timer,delay,repeat,callback):timers.append((timer,delay,callback))
e.update(Player=lambda p:p,GetPlayerId=lambda p:p,GetLocalPlayer=lambda:e['local_player'],
         GetUnitX=lambda u:u['x'],GetUnitY=lambda u:u['y'],Cos=math.cos,Sin=math.sin,Atan2=math.atan2,bj_RADTODEG=180/math.pi,
         CreateUnit=create,GetUnitTypeId=lambda u:u['kind'],GetOwningPlayer=lambda u:u['owner'],
         GetSellingUnit=lambda:e['shop'],GetSoldUnit=lambda:e['sold'],IsUnitType=lambda u,t:u['kind'].startswith('H'),
         RemoveUnit=lambda u:u.update(removed=True),GetHandleId=id,LoadBoolean=lambda h,k,c:flags.get((k,c),False),
         SaveBoolean=lambda h,k,c,v:flags.__setitem__((k,c),v),
         RemoveItemFromStock=lambda u,k:u['items'].discard(k),AddItemToStock=lambda u,k,a,b:u['items'].add(k),
         RemoveUnitFromStock=lambda u,k:u['stock'].discard(k),AddUnitToStock=lambda u,k,a,b:u['stock'].add(k),
         SoloFootsTakeTavernHero=take,SelectUnitForPlayerSingle=lambda u,p:selections.append((u,p)),
         SetCameraPosition=lambda x,y:cameras.append((e['local_player'],x,y)),CreateTimer=lambda:object(),TimerStart=tick,
         GetExpiredTimer=lambda:e.get('expired'),GetEnumPlayer=lambda:e['enum_player'],
         udg_total_hero_count=91,local_player=0)
e.update(bj_ALLIANCE_UNALLIED=0,EVENT_PLAYER_UNIT_SELL=1,UNIT_TYPE_HERO=2)
for i in range(1,92):e['udg_hero_type'][i]='H'+str(i).zfill(3)
for called in set(re.findall(r'\b(\w+)\(',translated)):
    if called not in e and called not in names:e[called]=lambda *args:None
e['ConditionalTriggerExecute']=lambda trigger:e['SF_OpenTaverns']()
exec(translated,e)
e['SF_Initialize']()
assert not created,'Ground selector must not be spawned'
assert all(e['udg_mode_selector'][p+1] is None for p in slots)
stats_init=re.search(r'^function InitTrig_set_hero_stats\b.*?^endfunction',s,re.M|re.S)[0]
stats_delay=float(re.search(r'TriggerRegisterTimerEventSingle\([^,]+, ([\d.]+)\)',stats_init)[1])
startup=[t for t in timers if t[2]==e['SF_StartBaseSelection']]
assert startup[0][1]>stats_delay,'Hero stock must be populated after hero categories initialize'
assert len(startup)==1
e['expired']=startup[0][0];startup[0][2]()
assert len(created)==8 and all(u['kind']=='nFHT' for u in created)
assert all(e['SF_PoolCount'][p+1]==24 for p in slots)
assert cameras and all(p==0 and (x,y)==(100,200) for p,x,y in cameras),'Only local camera moves to local main'
for p in slots:
    tavern=e['SF_Tavern'][p+1]
    assert 'hPgP' not in tavern['stock'] and 'hPgN' in tavern['stock']
    pages=[];e['shop']=tavern
    for expected_page in [0,1,2,0]:
        assert e['SF_Page'][p+1]==expected_page
        pages.append({k for k in tavern['stock'] if k!='hPgN'})
        e['sold']=create(p,'hPgN',0,0,0);e['SF_OnSale']()
        assert e['sold']['removed'] and not e['SF_Picked'][p+1]
    assert list(map(len,pages[:3]))==[10,10,4]
    assert len(set.union(*pages[:3]))==24 and pages[0]==pages[3]
recipe_pages=json.loads((ROOT/'verification.json').read_text())['recipe_pages']
shop=create(27,'n01Y',0,0,0);shop['items']=set(recipe_pages[0]);e['shop']=shop
for expected in [recipe_pages[1],recipe_pages[0],recipe_pages[1]]:
    e['sold']=create(0,'h037',0,0,0);e['SF_OnSale']()
    assert shop['items']==set(expected) and e['sold']['removed']
assert len(set(recipe_pages[0]+recipe_pages[1]))==17
for p in slots:
    e['local_player']=p;e['enum_player']=p
    for name in ['SF_CenterBaseCamera','Trig_Start_game_Func024Func001A','Trig_Start_game_Func024Func002A']:
        before=len(cameras)
        if name=='SF_CenterBaseCamera':e[name](p+1)
        else:e[name]()
        assert cameras[-1]==(p,100+p,200+p) and len(cameras)==before+1
e['local_player']=0;before=len(cameras);e['SF_CenterBaseCamera'](5)
assert len(cameras)==before,'Remote players must not move local camera'
print('PASS: eight base taverns; no mode-selector units; all 24 heroes reachable per player; Next wraps; all 17 recipes reachable in one shop; all eight cameras target their actual main; remote cameras stay local.')
