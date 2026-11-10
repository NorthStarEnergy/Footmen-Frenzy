"""Deterministic six-player conversion of the latest local Solo Foots FFA."""
from pathlib import Path
import math,struct,re,json,hashlib,sys
from PIL import Image,ImageDraw,ImageFont
from archive import ROOT,SOURCE

B=ROOT/'base'; O=ROOT/'src'; O.mkdir(exist_ok=True)
TITLE='Solo Foots v1.8 - 6 Player FFA v1'
DESC='Six independent bases. Two towers, full back shops and a base pet each. Choose a hero in your base; unpicked heroes are randomized 15 seconds into mass.'
SLOTS=[0,1,3,4,7,11]
ANGLES=[math.radians(150-60*i) for i in range(6)]
W=H=81; OX=-5120.; OY=-5376.; CY=-256.
def xy(radius,lateral,a):return (radius*math.cos(a)-lateral*math.sin(a),CY+radius*math.sin(a)+lateral*math.cos(a))
STARTS={p:xy(3300,0,a) for p,a in zip(SLOTS,ANGLES)}

# Replace the old eight-sector terrain and every old static obstruction. Narrow
# raised cliff dividers run to the perimeter; all intervening ground is usable.
b=(B/'war3map.w3e').read_bytes(); assert struct.unpack_from('<IIff',b,69)==(W,H,OX,OY)
def oldtile(x,y):
    i=round((x-OX)/128);j=round((y-OY)/128)
    return bytearray(b[85+(j*W+i)*8:85+(j*W+i+1)*8])
ground=oldtile(0,CY); ground[7]=(ground[7]&240)|9
def wall(x,y,pad=0):
    yy=y-CY
    for k in range(6):
        a=k*math.pi/3; along=x*math.cos(a)+yy*math.sin(a); across=abs(-x*math.sin(a)+yy*math.cos(a))
        if along>=1920-pad and across<=128+pad:return True
    return False
raw=bytearray(b[:85]);levels=[]
for j in range(H):
    for i in range(W):
        x,y=OX+i*128,OY+j*128;r=math.hypot(x,y-CY)
        t=oldtile(x,y) if r<1664 else bytearray(ground)
        edge=i<4 or j<4 or i>W-5 or j>H-5
        raised=wall(x,y) and not edge
        texture=2 if r<786 else 8 if r<=914 else 4 if r<=1088 else 5 if r<2350 else 7
        if raised:texture=1
        if not raised and r>=2350:
            a=ANGLES[min(range(6),key=lambda k:abs(math.atan2(math.sin(math.atan2(y-CY,x)-ANGLES[k]),math.cos(math.atan2(y-CY,x)-ANGLES[k]))))]
            if abs(-x*math.sin(a)+(y-CY)*math.cos(a))<320:texture=5
        struct.pack_into('<H',t,2,(struct.unpack_from('<H',t,2)[0]&0x3fff)|(0x4000 if edge else 0))
        struct.pack_into('<H',t,4,texture)
        t[6]=0;t[7]=(ground[7]&240)|(11 if raised else 9)
        raw.extend(t);levels.append(t[7]&15)
(O/'war3map.w3e').write_bytes(raw)

# Pathing follows actual cliff cells plus a small clearance margin. No old
# cardinal islands, invisible blockers, or old shop kill zones remain.
pw=ph=320; path=bytearray(struct.pack('<4sIII',b'MP3W',0,pw,ph))
for j in range(ph):
    for i in range(pw):
        x,y=OX+(i+.5)*32,OY+(j+.5)*32
        outside=not (-4608<x<4608 and -4864<y<4352)
        ti=i//4;tj=j//4
        cliff=any(levels[(tj+dy)*W+ti+dx]>9 for dx,dy in [(0,0),(1,0),(0,1),(1,1)])
        path.append(0xfe if outside else 10 if cliff else 0)
(O/'war3map.wpm').write_bytes(path)
(O/'war3map.shd').write_bytes(bytes(pw*ph))

# Preserve the center decorations only. Exterior doodads include invisible
# blockers for the obsolete layout and must be discarded, not merely hidden.
db=(B/'war3map.doo').read_bytes();off=16;kept=[];dcount=struct.unpack_from('<I',db,12)[0]
for i in range(dcount):
    st=off;x,y,z=struct.unpack_from('<3f',db,off+8)
    off+=8+12+4+12+4+4+2+4
    count=struct.unpack_from('<I',db,off)[0];off+=4
    for _ in range(count):n=struct.unpack_from('<I',db,off)[0];off+=4+n*8
    off+=4+4+12
    if math.hypot(x,y-CY)<1100:kept.append(db[st:off])
assert off+8==len(db),(off,len(db))
head=bytearray(db[:16]);struct.pack_into('<I',head,12,len(kept))
(O/'war3map.doo').write_bytes(head+b''.join(kept)+struct.pack('<II',0,0))

# Clone one complete west-base set, including every hidden shop page, six times.
units=json.loads((ROOT/'source-units.json').read_text());ub=(B/'war3mapUnits.doo').read_bytes()
template=[u for u in units if u['owner']==9 or (u['owner']==27 and u['xyz'][0]<-3000 and abs(u['xyz'][1]-CY)<800)]
records=[];placed=[];ident=2000
def add(u,owner,x,y,angle,base=None):
    global ident
    rec=bytearray(ub[u['start']:u['end']]);struct.pack_into('<ff',rec,8,x,y);struct.pack_into('<f',rec,20,angle)
    struct.pack_into('<I',rec,45,owner);struct.pack_into('<I',rec,len(rec)-16,ident)
    records.append(rec);placed.append(dict(type=u['type'],owner=owner,x=x,y=y,angle=angle,id=ident,base=base));ident+=1
for p,a in zip(SLOTS,ANGLES):
    tower=0
    for u in template:
        r=-u['xyz'][0]-400; lateral=-(u['xyz'][1]-CY)
        if u['type']=='sloc':r,lateral=3300,0
        if u['type']=='hwtw':r,lateral=2736,(-600 if tower==0 else 600);tower+=1
        if u['type'] in ['n03L','n02U']:r,lateral=3450,-560
        if u['type']=='n02Z':r,lateral=3800,-650
        if u['type']=='necr':r,lateral=3660,600
        x,y=xy(r,lateral,a)
        add(u,p if u['owner']==9 else 27,x,y,(u['angle']+a-math.pi)%(2*math.pi),p)
    assert tower==2
# Preserve the five central shared shops and their original named script refs.
central=[u for u in units if u['type'] in ['n01B','n004','n000']]
for i,u in enumerate(central):
    if u['type']=='n000':x,y=0,CY
    else:
        a=math.radians(45+90*i);x,y=xy(1320,0,a)
    add(u,27,x,y,u['angle'])
head=bytearray(ub[:16]);struct.pack_into('<I',head,12,len(records))
(O/'war3mapUnits.doo').write_bytes(head+b''.join(records))

s=(B/'war3map.j').read_text(encoding='utf-8-sig')
def get(name):return re.search(r'^function '+re.escape(name)+r'\b.*?^endfunction',s,re.M|re.S)[0]
def replace(name,body):
    global s
    old=get(name);s=s.replace(old,old.splitlines()[0]+'\n'+body+'\nendfunction',1)
def edit(name,func):
    global s
    old=get(name);s=s.replace(old,func(old),1)

# Runtime placements exactly match editor placements. Retain named central shops.
refs={'n01B':['gg_unit_n01B_0055','gg_unit_n01B_0056'],'n004':['gg_unit_n004_0057','gg_unit_n004_0058'],'n000':['gg_unit_n000_0054']}
lines=['    local unit u']
for u in placed:
    if u['type']=='sloc':continue
    dst=refs[u['type']].pop(0) if u['type'] in refs else 'u'
    lines.append(f"    set {dst}=BlzCreateUnitWithSkin(Player({u['owner']}), '{u['type']}', {u['x']:.3f}, {u['y']:.3f}, {math.degrees(u['angle']):.3f}, '{u['type']}')")
    if u['type']=='necr':lines.append(f'    call IssueImmediateOrder({dst}, "holdposition")')
replace('CreateAllUnits','\n'.join(lines))
slots=[];teams=[]
for p in range(24):
    if p in SLOTS:
        k=SLOTS.index(p)
        slots.extend([f'    call SetPlayerStartLocation(Player({p}), {k})',f'    call ForcePlayerStartLocation(Player({p}), {k})',f'    call SetPlayerColor(Player({p}), ConvertPlayerColor({p}))',f'    call SetPlayerRacePreference(Player({p}), RACE_PREF_HUMAN)',f'    call SetPlayerRaceSelectable(Player({p}), false)',f'    call SetPlayerController(Player({p}), MAP_CONTROL_USER)'])
        teams.extend([f'    call SetPlayerTeam(Player({p}), {k})',f'    call SetPlayerState(Player({p}), PLAYER_STATE_ALLIED_VICTORY, 0)'])
    else:slots.append(f'    call SetPlayerController(Player({p}), MAP_CONTROL_NONE)')
replace('InitCustomPlayerSlots','\n'.join(slots));replace('InitCustomTeams','\n'.join(teams));replace('InitAllyPriorities','')
replace('config',f'    call SetMapName("{TITLE}")\n    call SetMapDescription("{DESC}")\n    call SetPlayers(6)\n    call SetTeams(6)\n    call SetGamePlacement(MAP_PLACEMENT_FIXED)\n'+''.join(f'    call DefineStartLocation({k}, {STARTS[p][0]:.3f}, {STARTS[p][1]:.3f})\n' for k,p in enumerate(SLOTS))+'    call InitCustomPlayerSlots()\n    call InitCustomTeams()')

# Six independent force records support KOTH income, research and scoreboard.
s=s.replace('exitwhen ( i > 5 )\n        set udg_team[i]=CreateForce()','exitwhen ( i > 6 )\n        set udg_team[i]=CreateForce()')
setup='\n'.join(f'    call ForceAddPlayerSimple(Player({p}), udg_team[{k+1}])\n    set udg_teamnumber[{p+1}]={k+1}' for k,p in enumerate(SLOTS))
edit('Trig_init_Actions',lambda t:re.sub(r'    // Set Teams.*?    // save orig player name','    // Six independent FFA teams\n'+setup+'\n    // save orig player name',t,flags=re.S).replace('exitwhen udg_X > 4\n        set udg_frostbolt','exitwhen udg_X > 6\n        set udg_frostbolt'))
# Initial visibility follows each player's base, not the old four team corners.
for n in ['Trig_init_Func082A','Trig_init_Func083A','Trig_init_Func084A','Trig_init_Func085A']:
    replace(n,'    // Base vision is initialized for all six slots in SF_Initialize.')
edit('Trig_Multiboard_Create_with_KOTH_Actions',lambda t:t.replace('CreateMultiboardBJ(4, 5,','CreateMultiboardBJ(4, 7,').replace('udg_X > 4','udg_X > 6').replace('udg_X > 5','udg_X > 7').replace('"T" + I2S(udg_X)','"P" + I2S(udg_X)'))

# Put base, shops, pet, hero arrival and respawn at the same six centers.
def init(t):
    t=re.sub(r'^    set SF_(?:BaseX|BaseY|Angle)\[\d+\]=.*\n','',t,flags=re.M)
    coords=''.join(f'    set SF_BaseX[{p+1}]={STARTS[p][0]:.3f}\n    set SF_BaseY[{p+1}]={STARTS[p][1]:.3f}\n    set SF_Angle[{p+1}]={a:.9f}\n' for p,a in zip(SLOTS,ANGLES))
    t=t.replace('    set SF_GameClock=CreateTimer()',coords+'    set SF_GameClock=CreateTimer()')
    t=t.replace(' + 320. * Cos(SF_Angle[p]) - 360. * Sin(SF_Angle[p])',' + 140. * Cos(SF_Angle[p]) - 600. * Sin(SF_Angle[p])').replace(' + 320. * Sin(SF_Angle[p]) + 360. * Cos(SF_Angle[p])',' + 140. * Sin(SF_Angle[p]) + 600. * Cos(SF_Angle[p])')
    t=t.replace('            call SetPlayerMaxHeroesAllowed(2, Player(p - 1))','            call SetPlayerMaxHeroesAllowed(2, Player(p - 1))\n            call FogModifierStart(CreateFogModifierRadius(Player(p-1), FOG_OF_WAR_VISIBLE, SF_BaseX[p], SF_BaseY[p], 1200., true, false))')
    return t
edit('SF_Initialize',init)
# The old four base shop strips can teleport/kill units on newly playable land.
# Their replacement is physical terrain separation and each player's own shops.
for prefix in ['block_from_shop_t','kill_blink_shop_t']:
    for k in range(1,5):replace('InitTrig_'+prefix+str(k),f'    set gg_trg_{prefix}{k}=CreateTrigger()\n    call DisableTrigger(gg_trg_{prefix}{k})')

# Never respawn selection taverns, including after a delayed mode event.
s=re.sub(r'^endglobals\s*$', '    boolean SF_SelectionClosed=false\nendglobals',s,count=1,flags=re.M)
edit('SF_OpenTaverns',lambda t:t.replace('if SF_Opened then','if SF_Opened or SF_SelectionClosed then').replace('if udg_player_active[p] then','if udg_player_active[p] and not SF_Picked[p] then').replace('320. * Cos(a) - 256. * Sin(a)','-200. * Cos(a) + 560. * Sin(a)').replace('320. * Sin(a) + 256. * Cos(a)','-200. * Sin(a) - 560. * Cos(a)'))
# Filter non-roster heroes/illusions from the inherited map-enter acceptance hook.
hero_guard='''    local integer rosterIndex=1
    local boolean knownHero=false
    if hero==null or IsUnitIllusion(hero) or not IsUnitType(hero, UNIT_TYPE_HERO) then
        return
    endif
    loop
        exitwhen rosterIndex>udg_total_hero_count
        if GetUnitTypeId(hero)==udg_hero_type[rosterIndex] then
            set knownHero=true
        endif
        set rosterIndex=rosterIndex+1
    endloop
    if not knownHero then
        return
    endif
'''
edit('SF_AcceptHero',lambda t:t.replace('    if ownerId > 12',hero_guard+'    if ownerId > 12'))
edit('SF_AssignUnpicked',lambda t:t.replace('    loop\n','    set SF_SelectionClosed=true\n    loop\n',1))
# Close a departed/defeated player's tavern immediately.
for n in ['Trig_player_leaves_Actions','Trig_player_destroyed_Actions']:
    edit(n,lambda t:t.replace('    set udg_player_active[playerNumber]=false','    call SF_RemoveTavern(playerNumber)\n    set udg_player_active[playerNumber]=false'))

# Match base sectors while retaining 86 opening units per player and the original
# wave rules. Two dense files leave a walkable lane in the middle of each base.
edit('Trig_Foot_Spawn_Actions',lambda t:t.replace('1280.0 + I2R(i / 2) * 48.0','1200.0 + I2R(i / 2) * 42.0'))
# Remove obsolete four-team shared-vision updates after eliminations.
replace('Trig_Visibility_Actions','    // FFA players retain their own base vision; living opponents are never allied.')
(O/'war3map.j').write_text(s,encoding='utf-8')

# Preserve all unknown v39 metadata and rewrite only parsed player/force records.
info=(B/'war3map.w3i').read_bytes();start=info.index(struct.pack('<5i',0,1,1,64,1))-4
off=start;count=struct.unpack_from('<I',info,off)[0];off+=4;players={}
for _ in range(count):
    st=off;pid=struct.unpack_from('<I',info,off)[0];off+=20;end=info.index(0,off);off=end+1+8+16;players[pid]=info[st:off]
force_count=struct.unpack_from('<I',info,off)[0];off+=4
for _ in range(force_count):off+=8;off=info.index(0,off)+1
new=bytearray(info[:start]);new.extend(struct.pack('<I',6))
for k,p in enumerate(SLOTS):
    rec=bytearray(players[p]);end=rec.index(0,20);struct.pack_into('<ff',rec,end+1,*STARTS[p]);struct.pack_into('<4I',rec,end+9,0,0,0,0);new.extend(rec)
new.extend(struct.pack('<I',6))
for k,p in enumerate(SLOTS):new.extend(struct.pack('<II',0,1<<p)+f'Player {k+1}'.encode()+b'\0')
new.extend(info[off:])
oldtitle=b'Solo Foots v1.8 - Eight Players KING TEST04'
new=new.replace(oldtitle,TITLE.encode()).replace(b'2-8\0',b'2-6 FFA\0')
(O/'war3map.w3i').write_bytes(new)
wts=(B/'war3map.wts').read_bytes();wts=re.sub(rb'Solo Foots v1\.8 - Eight Players KING TEST\d+',TITLE.encode(),wts)
for number,value in [(3435,DESC)]:
    wts,n=re.subn(rb'(STRING '+str(number).encode()+rb'\s*\{\s*).*?(\r?\n\})',lambda m:m[1]+value.encode()+m[2],wts,count=1,flags=re.S);assert n==1
(O/'war3map.wts').write_bytes(wts)

# Update minimap/preview from the terrain and real placement table.
colors={1:(94,91,84),2:(76,76,79),4:(135,132,119),5:(150,148,131),7:(65,101,48),8:(198,194,172)}
im=Image.new('RGB',(W,H))
for j in range(H):
    for i in range(W):
        off=85+(j*W+i)*8;tex=struct.unpack_from('<H',raw,off+4)[0]&63
        color=colors.get(tex,(110,110,100))
        if struct.unpack_from('<H',raw,off+2)[0]&0x4000:color=(25,30,24)
        im.putpixel((i,H-1-j),color)
mini=im.resize((256,256),Image.Resampling.NEAREST).quantize(colors=256)
for name in ['war3mapMap.blp','war3mapMap_ingame.blp']:mini.save(O/name)
icons=[struct.pack('<4I',0,round((x-OX)/10240*256),round((y-OY)/10240*256),0xffffffff) for x,y in STARTS.values()]
(O/'war3map.mmp').write_bytes(struct.pack('<II',0,6)+b''.join(icons))
preview=im.resize((972,972),Image.Resampling.NEAREST);draw=ImageDraw.Draw(preview)
def pixel(x,y):return ((x-OX)/10240*972,972-(y-OY)/10240*972)
for u in placed:
    x,y=pixel(u['x'],u['y']);kind=u['type'];size=6 if kind=='hwtw' else 3
    draw.ellipse((x-size,y-size,x+size,y+size),fill='#f5c15b' if kind=='hwtw' else '#86cfff')
for k,(p,a) in enumerate(zip(SLOTS,ANGLES)):
    x,y=pixel(*STARTS[p]);draw.rectangle((x-11,y-11,x+11,y+11),fill='#f2e6c6',outline='black',width=2)
    tx,ty=pixel(*xy(2220,0,a));draw.text((tx-18,ty-8),f'P{k+1}',fill='white',stroke_width=2,stroke_fill='black')
preview.save(ROOT/'layout-preview.png')
manifest=dict(title=TITLE,source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),slots=SLOTS,starts=STARTS,angles=ANGLES,units=placed,removed_doodads=dcount-len(kept),retained_doodads=len(kept),hero_deadline='Actual mass start + 15 seconds')
(ROOT/'layout.json').write_text(json.dumps(manifest,indent=2))
print('Generated six bases:',len(placed),'placements;',len(kept),'central doodads; source',manifest['source_sha256'])
