"""Build the eight-player FFA shop, selection, and camera update."""
from pathlib import Path
import sys, re, struct, math, ctypes as c, shutil, hashlib, json, subprocess

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa')
from objectio import Obj
import archive
B=ROOT/'base'; O=ROOT/'src'; O.mkdir(exist_ok=True)
archive.extract(ROOT/'baseline.w3x',B)
s=(B/'war3map.j').read_text()
changed_functions=[]
def get(name,text=None):
    m=re.search(r'^function '+re.escape(name)+r'\b.*?^endfunction',s if text is None else text,re.M|re.S)
    assert m,name
    return m[0]
def put(name,new):
    global s
    old=get(name); assert new.startswith(old.splitlines()[0]),name
    s=s.replace(old,new); changed_functions.append(name)
def body(name,new):put(name,get(name).splitlines()[0]+'\n'+new.strip('\n')+'\nendfunction')

# Consolidate recipe pages in one physical shop, retaining all seventeen recipes.
objects=Obj(B/'war3map.w3u')
def props(id):return {m[0].decode():m[4] for m in objects.find(id)['mods']}
recipes=[props(id)['usei'].split(',') for id in ['n01Y','n02Z']]
assert list(map(len,recipes))==[11,6]
objects.set('n01Y','uabi','A021,Avul,Apit,Asid,Asud')
objects.set('n01Y','useu','h037')
objects.set('n01Y','unam','Recipe Shop')
objects.set('n01Y','utip','Recipe Shop')
objects.set('h037','unam','Next page')
objects.set('h037','utip','Next page')
objects.set('h037','utub','Show the next recipe page. The last page cycles back to the first.')
objects.set('h037','ubpx',3); objects.set('h037','ubpy',2)
objects.set('hPgN','unam','Next page'); objects.set('hPgN','utip','Next page')
objects.set('hPgN','utub','Show the next hero page. The last page cycles back to the first.')
objects.find('nFHT')['mods']=[m for m in objects.find('nFHT')['mods'] if m[0] != b'umdl']
objects.set('nFHT','unam','Hero Tavern')
objects.set('nFHT','utip','Choose your hero')
objects.set('nFHT','utub','Choose your hero. Next page cycles through every page and back to the first.')
objects.save(O/'war3map.w3u'); Obj(O/'war3map.w3u')

# Read every modern unit-placement record to its boundary before editing it.
class Reader:
    def __init__(self,b):self.b=b;self.o=0
    def get(self,f):
        v=struct.unpack_from('<'+f,self.b,self.o);self.o+=struct.calcsize('<'+f)
        return v[0] if len(v)==1 else v
    def skip(self,n):self.o+=n
def placements(b):
    r=Reader(b);r.o=12;count=r.get('I');out=[]
    for _ in range(count):
        start=r.o; kind=r.get('4s').decode();r.skip(4);x,y,z=r.get('fff');angle=r.get('f')
        r.skip(12+4+4+1);owner=r.get('I');r.skip(2+12)
        for _ in range(r.get('I')):r.skip(r.get('I')*8)
        r.skip(24);r.skip(r.get('I')*8);r.skip(r.get('I')*12);random=r.get('I')
        if random==0:r.skip(4)
        elif random==1:r.skip(8)
        elif random==2:r.skip(r.get('I')*8)
        else:raise AssertionError(random)
        r.skip(8);ident=r.get('I');r.skip(12)
        out.append(dict(kind=kind,x=x,y=y,angle=angle,owner=owner,id=ident,start=start,end=r.o))
    assert r.o==len(b),(r.o,len(b))
    return out
shop_types={'n00R','n01T','n01Y','n007','n012','n045','n02N','n046','n03L','n02U','n02Z','n01B','n004','n000'}
def facing(x,y):return math.atan2(-256-y,-x)%(2*math.pi) if math.hypot(x,y+256)>.01 else None
unitbytes=(B/'war3mapUnits.doo').read_bytes();before=placements(unitbytes);records=[];facing_count=0
for u in before:
    if u['kind']=='n02Z':continue
    raw=bytearray(unitbytes[u['start']:u['end']])
    a=facing(u['x'],u['y'])
    if u['kind'] in shop_types and a is not None:
        struct.pack_into('<f',raw,20,a);facing_count+=1
    records.append(raw)
assert sum(u['kind']=='n02Z' for u in before)==8
head=bytearray(unitbytes[:16]);struct.pack_into('<I',head,12,len(records))
(O/'war3mapUnits.doo').write_bytes(head+b''.join(records))
after=placements((O/'war3mapUnits.doo').read_bytes())
assert len(before)-len(after)==8

creation=get('CreateAllUnits')
creation=re.sub(r"^.*BlzCreateUnitWithSkin\([^\n]*'n02Z'[^\n]*\n",'',creation,flags=re.M)
pattern=r"(BlzCreateUnitWithSkin\(Player\(\d+\), '(....)', )([\d. -]+), ([\d. -]+), ([\d. -]+)(, '....'\))"
def rotate(m):
    if m[2] not in shop_types:return m[0]
    x=float(m[3].replace(' ',''));y=float(m[4].replace(' ',''));a=facing(x,y)
    return m[1]+m[3]+', '+m[4]+', '+(f'{math.degrees(a):.6f}' if a is not None else m[5])+m[6]
creation=re.sub(pattern,rotate,creation)
assert "'n02Z'" not in creation
put('CreateAllUnits',creation)

camera_helper='''function SF_CenterBaseCamera takes integer p returns nothing
    local real x=SF_BaseX[p]
    local real y=SF_BaseY[p]
    if udg_base[p] != null then
        set x=GetUnitX(udg_base[p])
        set y=GetUnitY(udg_base[p])
    endif
    call ResetToGameCameraForPlayer(Player(p - 1), 0.)
    call zoom_RestoreFromCacheForPlayer(Player(p - 1))
    if GetLocalPlayer() == Player(p - 1) then
        call StopCamera()
        call SetCameraPosition(x, y)
    endif
endfunction'''
recipe_helper='''function SF_FlipRecipePage takes unit shop,player buyer returns nothing
    local integer key=GetHandleId(shop)
    local boolean second=not LoadBoolean(GST_Hash, key, 104701)
REMOVALS
    call SaveBoolean(GST_Hash, key, 104701, second)
    if second then
PAGE2
    else
PAGE1
    endif
    call SelectUnitForPlayerSingle(shop, buyer)
endfunction'''
recipe_helper=recipe_helper.replace('REMOVALS','\n'.join(f"    call RemoveItemFromStock(shop, '{id}')" for page in recipes for id in page))
for i,page in enumerate(recipes,1):
    recipe_helper=recipe_helper.replace('PAGE'+str(i),'\n'.join(f"        call AddItemToStock(shop, '{id}', 1, 1)" for id in page))
s=s.replace('function Trig_Start_game_Func006C takes',camera_helper+'\n\nfunction Trig_Start_game_Func006C takes',1)
s=s.replace('function SF_RemoveTavern takes',recipe_helper+'\n\nfunction SF_RemoveTavern takes',1)

page=get('SF_RefreshPage').replace("    call AddUnitToStock(SF_Tavern[p], 'hPgP', 1, 1)\n",'')
put('SF_RefreshPage',page)
sale=get('SF_OnSale')
start=sale.index("        if id == 'hPgN' or id == 'hPgP' then")
end=sale.index('        elseif IsUnitType(sold, UNIT_TYPE_HERO) then',start)
sale=sale[:start]+'''        if id == 'hPgN' then
            call RemoveUnit(sold)
            if SF_Tavern[p] != null and not SF_Picked[p] then
                set SF_Page[p]=SF_Page[p] + 1
                if SF_Page[p] * 10 >= SF_PoolCount[p] then
                    set SF_Page[p]=0
                endif
                call SF_RefreshPage(p)
                call SelectUnitForPlayerSingle(shop, Player(p - 1))
            endif
'''+sale[end:]
sale=sale.replace("    if p <= 12 and GetUnitTypeId(shop) == 'nFHT' then",'''    if GetUnitTypeId(shop) == 'n01Y' and id == 'h037' then
        call SF_FlipRecipePage(shop, GetOwningPlayer(sold))
        call RemoveUnit(sold)
    elseif p <= 12 and GetUnitTypeId(shop) == 'nFHT' then''')
put('SF_OnSale',sale)
legacy=get('Trig_page_system_Conditions').replace(' returns boolean\n',' returns boolean\n    if GetUnitTypeId(GetSellingUnit()) == \'n01Y\' then\n        return false\n    endif\n',1)
put('Trig_page_system_Conditions',legacy)

taverns=get('SF_OpenTaverns')
taverns=taverns.replace('a * bj_RADTODEG + 180.)','Atan2(-256. - (SF_BaseY[p] + 320. * Sin(a) + 256. * Cos(a)), -(SF_BaseX[p] + 320. * Cos(a) - 256. * Sin(a))) * bj_RADTODEG)')
taverns=taverns.replace('call PanCameraToTimedForPlayer(Player(p - 1), SF_BaseX[p], SF_BaseY[p], 0.)','call SF_CenterBaseCamera(p)')
taverns=taverns.replace('Use Next / Previous to browse.','Use Next page to cycle through all pages.')
put('SF_OpenTaverns',taverns)

# Every start-game camera path now targets that player's actual main.
for name in ['Trig_Start_game_Func024Func001A','Trig_Start_game_Func024Func002A']:
    body(name,'    call SF_CenterBaseCamera(GetPlayerId(GetEnumPlayer()) + 1)')
startup='''function SF_StartBaseSelection takes nothing returns nothing
    local integer p=1
    local timer startup=GetExpiredTimer()
    call PauseTimer(udg_Host_AFK_Timer)
    call ConditionalTriggerExecute(gg_trg_MODE_set_pub_game)
    loop
        exitwhen p > 12
        if udg_player_active[p] then
            call SF_CenterBaseCamera(p)
            if SF_Tavern[p] != null then
                call SelectUnitForPlayerSingle(SF_Tavern[p], Player(p - 1))
            endif
        endif
        set p=p + 1
    endloop
    call DestroyTimer(startup)
    set startup=null
endfunction'''
s=s.replace('function SF_Initialize takes',startup+'\n\nfunction SF_Initialize takes',1)
init=get('SF_Initialize')
init=re.sub(r"            if p == 1 then\n.*?            endif\n(?=            call PanCamera)","            set udg_mode_selector[p]=null\n",init,flags=re.S)
assert "'h03Y'" not in init and "'h01G'" not in init
init=init.replace('    local trigger t=CreateTrigger()','    local trigger t=CreateTrigger()\n    local timer startup=CreateTimer()')
init=init.replace('    set t=null','''    call DisableTrigger(gg_trg_AFK_Host_Setup)
    call DisableTrigger(gg_trg_AFK_Host_Timer_Expires)
    call DisableTrigger(gg_trg_MODE_GUI_show)
    call DisableTrigger(gg_trg_MODE_GUI_execute)
    call PauseTimer(udg_Host_AFK_Timer)
    call TimerStart(startup, 1.10, false, function SF_StartBaseSelection)
    set startup=null
    set t=null''')
put('SF_Initialize',init)
spawn=get('Trig_Foot_Spawn_Actions')
spawn=spawn.replace('set r=1280.0 + I2R(i / 2) * 48.0','set r=560.0 + I2R(i / 4) * 64.0 - I2R(ModuloInteger(i / 2, 2)) * 16.0')
spawn=spawn.replace('set lateral=I2R(side) * 160.0','set lateral=I2R(side) * (32.0 + I2R(i / 4) * 20.0 + I2R(ModuloInteger(i / 2, 2)) * 48.0)')
put('Trig_Foot_Spawn_Actions',spawn)
title='Solo Foots 8 Player FFA v6'
s=s.replace('call SetMapName("Solo Foots v1.8 - Eight Players KING TEST04")',f'call SetMapName("{title}")')
(O/'war3map.j').write_text(s)

# Keep the existing editor wrapper in sync without regenerating terrain/minimaps.
b=(B/'war3map.wct').read_bytes();comment_end=b.index(0,4)+1;length=struct.unpack_from('<I',b,comment_end)[0]
editor=b[comment_end+4:comment_end+4+length].rstrip(b'\0').decode()
editor=editor.replace('function Trig_Start_game_Func006C takes',camera_helper+'\n\nfunction Trig_Start_game_Func006C takes',1)
editor=editor.replace('function SF_RemoveTavern takes',recipe_helper+'\n\nfunction SF_RemoveTavern takes',1)
editor=editor.replace('function SF_Initialize takes',startup+'\n\nfunction SF_Initialize takes',1)
for name in changed_functions:
    target='SFMap_CreateAllUnits' if name=='CreateAllUnits' else name
    replacement=get(name)
    if name=='CreateAllUnits':
        replacement=replacement.replace('function CreateAllUnits ','function SFMap_CreateAllUnits ').replace('BlzCreateUnitWithSkin','SF_FindPlacement').replace('gg_unit_','sf_unit_')
    old=get(target,editor);editor=editor.replace(old,replacement)
payload=editor.encode()+b'\0'
(O/'war3map.wct').write_bytes(b[:comment_end]+struct.pack('<I',len(payload))+payload+b[comment_end+4+length:])
regions=sorted(set(re.findall(r'\bgg_rct_\w+\b',editor)))
decl='globals\n    trigger gg_trg_SoloFootsRuntime=null\n'+''.join('    rect '+name+'=null\n' for name in regions)+'endglobals\n'
wrapper=decl+editor+'''\nfunction main takes nothing returns nothing
    call InitBlizzard()
    call SFMap_main()
endfunction
function config takes nothing returns nothing
endfunction
'''
(ROOT/'editor-validation.j').write_text(wrapper)

# Change the lobby title, preserving the rest of the modern map-info record.
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28)
(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])

# Compilation is mandatory before packing.
work=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work')
preprocess=subprocess.run([str(ROOT/'tools/jasshelper/clijasshelper.exe'),'--scriptonly','--nooptimize',str(work/'common.j'),str(work/'Blizzard.j'),str(ROOT/'editor-validation.j'),str(ROOT/'editor-compiled.j')],cwd=ROOT,capture_output=True,text=True)
(ROOT/'editor-preprocess.log').write_text(preprocess.stdout+preprocess.stderr)
assert preprocess.returncode==0,preprocess.stdout[-4000:]
for source,logname in [(O/'war3map.j','runtime-pjass.log'),(ROOT/'editor-compiled.j','editor-pjass.log')]:
    result=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(source)],capture_output=True,text=True)
    (ROOT/logname).write_text(result.stdout+result.stderr)
    assert result.returncode==0,(logname,result.stdout[-4000:],result.stderr[-1000:])

output=ROOT/'release/Solo_Foots_8P_FFA_v6.w3x';shutil.copyfile(ROOT/'baseline.w3x',output)
h=c.c_void_p();assert archive.s.SFileOpenArchive(str(output),0,0,c.byref(h))
try:
    for file in O.iterdir():
        if file.is_file():assert archive.s.SFileAddFileEx(h,str(file),file.name.encode(),0x80000200,2,2),file.name
finally:assert archive.s.SFileCloseArchive(h)
raw=output.read_bytes();assert raw[:4]==b'HM3W'
header=b'HM3W'+bytes(4)+title.encode()+b'\0'+struct.pack('<II',196218,8)
output.write_bytes(header+bytes(512-len(header))+raw[512:])
names=archive.extract(output,ROOT/'roundtrip');changed=[];preserved=[]
for name in names:
    if name in ['(listfile)','(attributes)','(signature)']:continue
    source=O/name if (O/name).exists() else B/name
    assert source.read_bytes()==(ROOT/'roundtrip'/name).read_bytes(),name
    (changed if (O/name).exists() else preserved).append(name)
assert set(changed)=={'war3map.j','war3map.w3u','war3mapUnits.doo','war3map.wct','war3map.w3i'}
for file,levels in [('war3map.w3u',False),('war3map.w3t',False),('war3map.w3a',True),('war3map.w3h',False),('war3map.w3q',True),('war3map.w3b',False),('war3map.w3d',True)]:
    if (ROOT/'roundtrip'/file).exists():Obj(ROOT/'roundtrip'/file,levels)
assert all((ROOT/'roundtrip'/name).read_bytes()[:4]==b'BLP1' for name in ['war3mapMap.blp','war3mapMap_ingame.blp'])
report=dict(output=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),changed_entries=changed,
            preserved_entries=len(preserved),removed_recipe_page_buildings=8,inward_shop_facings=facing_count,
            recipe_pages=recipes,hero_pool='Existing 24 choices; 10 per page; Next only, wrapping',
            compilation='Runtime and editor wrapper passed pjass',live_test='Pending')
(ROOT/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
