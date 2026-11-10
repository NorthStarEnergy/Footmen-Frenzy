"""Archive/layout checks and execution of translated selection functions.

The selection harness runs the actual JASS branches with mocked Warcraft natives;
it does not substitute for a multiplayer engine test.
"""
from pathlib import Path
import re,struct,json,math,collections,hashlib,subprocess
from archive import ROOT,extract,pack,SOURCE

O=ROOT/'src';s=(O/'war3map.j').read_text();m=json.loads((ROOT/'layout.json').read_text());checks=[]
def check(value,label):
    assert value,label
    checks.append(label)
def fn(name):return re.search(r'^function '+re.escape(name)+r'\b.*?^endfunction',s,re.M|re.S)[0]
slots=m['slots'];units=m['units']
check(re.findall(r'SetPlayerController\(Player\((\d+)\), MAP_CONTROL_USER\)',fn('InitCustomPlayerSlots'))==list(map(str,slots)),'Exactly six playable lobby slots')
check('SetPlayers(6)' in fn('config') and 'SetTeams(6)' in fn('config'),'Six lobby teams')
check(len(set(tuple(x) for x in m['starts'].values()))==6,'Six unique starts')
template=None
for p in slots:
    owned=[u for u in units if u['owner']==p]
    check(sum(u['type']=='hwtw' for u in owned)==2,f'Slot {p}: two owned towers')
    check(sum(u['type']=='n003' for u in owned)==1,f'Slot {p}: own upgrade shop')
    check(sum(u['type']=='necr' for u in owned)==1,f'Slot {p}: own base critter')
    shopset=collections.Counter(u['type'] for u in units if u['base']==p and u['owner']==27)
    if template is None:template=shopset
    check(shopset==template and len(shopset)==11,f'Slot {p}: all eleven neutral back-shop objects/pages')
check(len([u for u in units if u['type']=='hwtw'])==12,'Exactly twelve towers total')
check(not any(u['owner']<24 and u['owner'] not in slots for u in units),'No placements for removed player slots')
for k,p in enumerate(slots):
    check(f'set udg_teamnumber[{p+1}]={k+1}' in s,f'Slot {p}: independent income/research team')
check('CreateMultiboardBJ(4, 7,' in s,'Six scoreboard rows plus header')
info=(O/'war3map.w3i').read_bytes();pos=info.index(struct.pack('<5i',0,1,1,64,1))-4
check(struct.unpack_from('<I',info,pos)[0]==6,'Map metadata: six players')
pos+=4
for p in slots:
    check(struct.unpack_from('<I',info,pos)[0]==p,f'Map metadata: slot {p}')
    pos=info.index(0,pos+20)+1;coords=struct.unpack_from('<ff',info,pos);pos+=24
    check(all(abs(a-b)<.001 for a,b in zip(coords,m['starts'][str(p)])),f'Map metadata: start {p} matches runtime')
check(struct.unpack_from('<I',info,pos)[0]==6,'Map metadata: six forces');pos+=4
for p in slots:
    check(struct.unpack_from('<II',info,pos)==(0,1<<p),f'Map metadata: slot {p} has private unallied force')
    pos=info.index(0,pos+8)+1
check(b'Eight Players KING TEST' not in (O/'war3map.wts').read_bytes(),'No stale eight-player title strings')
check('SF_StartDeadline()' in fn('Trig_Mass_START_Actions'),'Deadline starts at actual mass event')
check('TimerStart(SF_Deadline, 15.' in fn('SF_StartDeadline'),'Fifteen-second delay')
check('SF_RemoveTavern(ownerId)' in fn('SF_AcceptHero'),'Successful pick removes own tavern')
check('SF_Opened or SF_SelectionClosed' in fn('SF_OpenTaverns'),'Permanent reopen guard')
for k in range(1,5):
    for prefix in ['block_from_shop_t','kill_blink_shop_t']:
        check('TriggerRegisterEnterRect' not in fn('InitTrig_'+prefix+str(k)),f'No stale {prefix}{k} kill/teleport region')

# Flood-fill actual pathing: every walkable tile must connect to the arena.
wpm=(O/'war3map.wpm').read_bytes();w,h=struct.unpack_from('<II',wpm,8);grid=wpm[16:]
def cell(x,y):return (int((x+5120)//32),int((y+5376)//32))
def walkable(i,j):return 0<=i<w and 0<=j<h and not grid[j*w+i]&2
center=cell(0,-256);seen={center};queue=collections.deque([center])
while queue:
    i,j=queue.popleft()
    for q in [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]:
        if q not in seen and walkable(*q):seen.add(q);queue.append(q)
check(len(seen)==sum(not value&2 for value in grid),'All walkable terrain connects to central arena; no blocked-off islands')
for p,xy in m['starts'].items():check(cell(*xy) in seen,f'Slot {p}: base reaches arena')
for u in units:check(cell(u['x'],u['y']) in seen,f"Placement {u['id']} ({u['type']}): clear ground")
for p,a in zip(slots,m['angles']):
    x,y=m['starts'][str(p)]
    tx=x-200*math.cos(a)+560*math.sin(a);ty=y-200*math.sin(a)-560*math.cos(a)
    check(cell(tx,ty) in seen,f'Slot {p}: tavern on accessible ground')
    check(min(math.hypot(tx-u['x'],ty-u['y']) for u in units if u['type']!='sloc')>250,f'Slot {p}: tavern clear of placed units')
    for i in range(86):
        r=1200+(i//2)*42;lateral=(i%2*2-1)*160
        check(cell(r*math.cos(a)-lateral*math.sin(a),-256+r*math.sin(a)+lateral*math.cos(a)) in seen,f'Slot {p}: mass unit {i} clear ground')

# Rewrite the selected JASS functions into equivalent Python control flow.
# Only Warcraft native calls are mocked; branch/loop/timer bodies come from src.
names=['SF_RemoveTavern','SF_RefreshPage','SF_OpenTaverns','SF_AcceptHero','SF_OnSale','SF_AssignUnpicked','SF_StartDeadline']
def translate(name):
    block=fn(name).splitlines();sig=re.match(r'function \w+ takes (.*?) returns',block[0])[1]
    args=[] if sig=='nothing' else [v.strip().split()[-1] for v in sig.split(',')]
    locals_=args+[re.match(r'\s*local \w+ (\w+)',line)[1] for line in block if re.match(r'\s*local \w+ (\w+)',line)]
    assigned=set(re.findall(r'^\s*set (\w+)\s*=', '\n'.join(block),re.M))-set(locals_)
    result=['def '+name+'('+','.join(args)+'):']
    if assigned:result.append('    global '+','.join(sorted(assigned)))
    level=1
    for line in block[1:-1]:
        line=line.split('//')[0].strip()
        if not line:continue
        line=re.sub(r'\b(true|false|null)\b',lambda v:{'true':'True','false':'False','null':'None'}[v[1]],line)
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
        result.append('    '*level+line)
        if line.endswith(':'):level+=1
    return '\n'.join(result)
translated='\n\n'.join(translate(name) for name in names)
(ROOT/'selection-translated.py').write_text(translated)

def harness(reentrant):
    e={};created=[];timers=[];poolidx=collections.defaultdict(int)
    globals_block=re.search(r'^globals\s*$(.*?)^endglobals',s,re.M|re.S)[1]
    for typ,array,name in re.findall(r'^\s*(?:constant )?(\w+)\s+(?:(array)\s+)?(\w+)\s*(?:=|$)',globals_block,re.M):
        default=False if typ=='boolean' else '' if typ=='string' else 0 if typ in ['integer','real'] else None
        e[name]=collections.defaultdict(lambda default=default:default) if array else default
    e.update(bj_RADTODEG=180/math.pi,UNIT_TYPE_HERO='hero',SF_Deadline={},udg_total_hero_count=97)
    for i in range(1,98):e['udg_hero_type'][i]='H'+str(i).zfill(3)
    for p,a in zip(slots,m['angles']):
        e['udg_player_active'][p+1]=True;e['SF_BaseX'][p+1],e['SF_BaseY'][p+1]=m['starts'][str(p)];e['SF_Angle'][p+1]=a
    def create(owner,kind,x,y,facing):
        u=dict(owner=owner,kind=kind,x=x,y=y,removed=False,items=[]);created.append(u)
        if reentrant and kind.startswith('H'):e['SF_AcceptHero'](u)
        return u
    def take(p,category):poolidx[p]+=1;return poolidx[p] if poolidx[p]<=24 else 0
    def remove(u):u['removed']=True
    e.update(Player=lambda x:x,ConvertedPlayer=lambda x:x-1,GetPlayerId=lambda x:x,GetConvertedPlayerId=lambda x:x+1,
        Cos=math.cos,Sin=math.sin,CreateUnit=create,RemoveUnit=remove,SoloFootsTakeTavernHero=take,
        GetRandomInt=lambda a,b:a,GetOwningPlayer=lambda u:u['owner'],GetUnitTypeId=lambda u:u['kind'],
        IsUnitType=lambda u,t:u['kind'].startswith('H'),IsUnitIllusion=lambda u:False,
        GetPlayerStartLocationLoc=lambda p:tuple(m['starts'][str(p)]),GetUnitName=lambda u:u['kind'],GetPlayerName=lambda p:'Player '+str(p),
        TimerStart=lambda timer,delay,repeat,callback:timers.append((delay,callback)),I2R=float,R2I=int,
        UnitAddItemByIdSwapped=lambda kind,u:u['items'].append(kind),
        GetSellingUnit=lambda:e['sale_shop'],GetSoldUnit=lambda:e['sale_unit'])
    for called in set(re.findall(r'\b(\w+)\(',translated)):
        if called not in e and called not in names:e[called]=lambda *args:False
    for constant in set(re.findall(r'\b(?:UNIT_IF|UNIT_RF)_[A-Z_]+',translated)):e[constant]=constant
    exec(translated,e)
    return e,created,timers,create

for reentrant in [False,True]:
    e,created,timers,create=harness(reentrant)
    e['SF_OpenTaverns']()
    check(len(created)==6,f'Selection ({reentrant}): one tavern for each of six active players')
    first=slots[0]+1;second=slots[1]+1
    e['sale_shop']=e['SF_Tavern'][first];e['sale_unit']=create(first-1,'hPgN',0,0,0);e['SF_OnSale']()
    check(e['SF_Page'][first]==1 and not e['SF_Picked'][first],f'Selection ({reentrant}): paging does not count as picking')
    tavern=e['SF_Tavern'][first]
    hero=create(first-1,'H001',0,0,0);e['sale_shop']=tavern;e['sale_unit']=hero;e['SF_OnSale']()
    check(e['SF_Picked'][first] and e['SF_Tavern'][first] is None and tavern['removed'],f'Selection ({reentrant}): manual pick removes tavern')
    check(len(hero['items'])==5,f'Selection ({reentrant}): hero initialized exactly once')
    e['udg_player_active'][second]=False;e['SF_RemoveTavern'](second)
    e['SF_StartDeadline']();e['SF_StartDeadline']()
    check(len(timers)==1 and timers[0][0]==15,f'Selection ({reentrant}): deadline armed only once, for 15 seconds')
    timers[0][1]()
    check(len([u for u in created if u['kind'].startswith('H')])==5,f'Selection ({reentrant}): random only for four remaining unpicked players')
    check(all(e['SF_Tavern'][p+1] is None for p in slots),f'Selection ({reentrant}): all taverns removed at deadline')
    check(all(e['SF_Picked'][p+1] for p in slots if p+1!=second),f'Selection ({reentrant}): every active player receives a hero')
    before=len(created);e['SF_OpenTaverns']();e['SF_AssignUnpicked']()
    check(len(created)==before,f'Selection ({reentrant}): no reopening or duplicate fallback heroes')

# Compile both shipped script and World Editor wrapper with the installed API.
work=Path(r'C:/Users/User/Documents/Codex/2026-10-28/thi/work')
for file,log in [(O/'war3map.j','pjass.log'),(ROOT/'editor-validation.j','editor-pjass.log')]:
    result=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(file)],capture_output=True,text=True)
    (ROOT/log).write_text(result.stdout+result.stderr)
    check(result.returncode==0,'Compiler: '+file.name)

output=ROOT/'release/Solo Foots 6 Player FFA v1.w3x';pack(output)
# The Warcraft map-browser HM3W header also carries a title and player count.
data=output.read_bytes()
if data[:4]==b'HM3W':
    end=data.index(0,8);flags=struct.unpack_from('<I',data,end+1)[0];mpq=data[512:]
else:
    check(data[:4]==b'MPQ\x1a','Source is a raw MPQ archive')
    meta=(O/'war3map.w3i').read_bytes();pos=28
    for _ in range(4):pos=meta.index(0,pos)+1
    flags=struct.unpack_from('<I',meta,pos+56)[0];mpq=data
header=b'HM3W'+bytes(4)+m['title'].encode()+b'\0'+struct.pack('<II',flags,6)
check(len(header)<512,'Wrapper title fits fixed header')
output.write_bytes(header+bytes(512-len(header))+mpq)
extract(output,ROOT/'roundtrip')
changed=0;untouched=0
for source in (ROOT/'base').rglob('*'):
    if not source.is_file() or source.name in ['(listfile)','(attributes)','(signature)']:continue
    rel=source.relative_to(ROOT/'base');modified=O/rel;expected=modified if modified.exists() else source
    check((ROOT/'roundtrip'/rel).read_bytes()==expected.read_bytes(),'Archive payload: '+str(rel))
    if modified.exists():changed+=1
    else:untouched+=1
for source in O.rglob('*'):
    if source.is_file():check((ROOT/'roundtrip'/source.relative_to(O)).read_bytes()==source.read_bytes(),'Modified payload: '+source.name)
report=dict(passed=len(checks),changed_payloads=changed,preserved_payloads=untouched,source=str(SOURCE),source_sha256=m['source_sha256'],output=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),bytes=output.stat().st_size,engine_test='Pending: existing Warcraft III process was not interrupted.',selection_test='Actual selection function branches executed with mocked Warcraft natives, including reentrant hero creation.',checks=checks)
(ROOT/'verification.json').write_text(json.dumps(report,indent=2))
(ROOT/'release/Solo Foots 6 Player FFA v1.sha256').write_text(report['sha256']+'  '+output.name+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
