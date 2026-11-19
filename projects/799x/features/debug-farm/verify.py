"""Exercise real farm and tavern JASS with mocked natives and inspect the packed objects and terrain."""
import ast
from collections import defaultdict
import json
import math
from pathlib import Path
import re
import struct
import sys
from prepare import FUNC, ROOT, objects
from map_archive import Archive
from restore_rc6_item_text import strings
from build_799x_items_catalog import merged_objects

path = Path(sys.argv[1])
dll = json.loads((ROOT/'tools.local.json').read_text())['stormlib']
with Archive(dll,path) as arc:
    source = arc.read('war3map.j').decode().replace('\r\n','\n')
    wts = strings(arc.read('war3map.wts'))
    units = merged_objects(arc,wts,'w3u')
    abilities = merged_objects(arc,wts,'w3a')
    terrain = arc.read('war3map.w3e')
    pathing = arc.read('war3map.wpm')
    icons = [objects.ICON,objects.ICON.replace('CommandButtons\\BTN','CommandButtonsDisabled\\DISBTN')]
    textures = [arc.read(icon) for icon in icons]
    assert textures[0] != textures[1]
    for name,data in zip(icons,textures):
        assert name.encode()+b'\0' in arc.read('war3map.imp')
        assert data[:4] == b'BLP1' and struct.unpack_from('<2I',data,12) == (64,64)
        offsets = struct.unpack_from('<7I',data,28)
        sizes = struct.unpack_from('<7I',data,92)
        assert sizes == tuple(2*(64>>i)**2 for i in range(7))
        assert offsets[0] == 1180 and offsets[-1]+sizes[-1] == len(data)
        assert len(set(data[1180:1180+4096])) > 80
assert units['hTNP']['fields']['uico',0] == abilities['aFPg']['fields']['aart',0] == icons[0]
assert set(units['n034']['fields']['uabi',0].split(',')) == {'Avul','aFLu','aFLd','aFPg'}
functions = {m[1]:m[0] for m in FUNC.finditer(source)}
assert 'function FFFarmCast' in functions['InitTrig_debug_control']
assert 'EVENT_PLAYER_UNIT_SPELL_EFFECT' in functions['InitTrig_debug_control']
harness = dict(ast=ast,re=re,FUNCTIONS=functions)
compiler = (ROOT/'development/footmen/casino-v1/test_casino.py').read_text('utf8')
exec(compiler[compiler.index('def expr('):compiler.index('NOW =')],harness)
env = {name:defaultdict(int) for name in re.findall(r'^\s*\w+ array (\w+)',source.split('\nendglobals')[0],re.M)}
starts = [tuple(map(float,row.replace(' ','').split(',')[1:])) for row in re.findall(r'call DefineStartLocation\((.*?)\)',source)[:12]]
seen, stock, mapping, stats = [],defaultdict(set),{},[]
def create(p,id,x,y,ang):
    unit = dict(p=p,id=id,x=x,y=y,level=1,buttons=set(),hero=id[0].isupper())
    seen.append(unit)
    return unit
def noop(*args): pass
def native(fn):
    tree = harness['Division']().visit(ast.parse(harness['translate'](fn)))
    exec(compile(ast.fix_missing_locations(tree),fn,'exec'),env)
env.update(dict(udg_mode_debugmode=True,FFDebugShopsReady=False,GetPlayerStartLocation=lambda p:p-1,ConvertedPlayer=lambda p:p,
    GetStartLocationX=lambda i:starts[i][0],GetStartLocationY=lambda i:starts[i][1],Cos=math.cos,Sin=math.sin,Atan2=math.atan2,
    I2R=float,I2S=str,jdiv=harness['jdiv'],ModuloInteger=lambda a,b:a%b,CreateUnit=create,Player=lambda p:p,
    GetUnitTypeId=lambda u:u['id'] if u else 0,GetHandleId=id,GetOwningPlayer=lambda u:u['p'],GetConvertedPlayerId=lambda p:p,
    GetPlayerId=lambda p:p-1,IsUnitType=lambda u,t:u['hero'],UNIT_TYPE_HERO=1,GetWidgetLife=lambda _:500,
    GetHeroLevel=lambda u:u['level'],SetHeroLevel=lambda u,n,_:u.update(level=n),UnitStripHeroLevel=lambda u,n:u.update(level=u['level']-n),
    UnitAddAbility=lambda u,a:u['buttons'].add(a),UnitRemoveAbility=lambda u,a:u['buttons'].discard(a),BlzSetUnitName=lambda u,n:u.update(name=n),
    FFGS_ComputeStats=lambda i,p:stats.append(('compute',i,p)),FFGS_ApplyUnit=lambda u,i,p:stats.append(('apply',i,p)),
    IssueImmediateOrder=noop,udg_spawnprotection=True,PLAYER_NEUTRAL_AGGRESSIVE=24,PLAYER_NEUTRAL_PASSIVE=27,bj_RADTODEG=180/math.pi,
    GetRectCenterX=lambda _:-2672.,GetRectCenterY=lambda _:-256.,gg_rct_TAVERN_AREA=1,
    SetUnitScale=noop,BlzSetUnitRealField=lambda u,f,val:u.update(scale=val),BlzGetUnitRealField=lambda u,f:2.,
    UNIT_RF_SELECTION_SCALE=1,SetUnitTypeSlots=noop,DraftStock=1,SaveInteger=lambda _,s,b,v:mapping.update({(s,b):v}),
    AddUnitToStock=lambda u,b,*_:stock[id(u)].add(b),ShowUnit=noop,FF_DebugOpenHiring=noop,SetPlayerTechMaxAllowed=noop,
    FFHire_CreateBuyer=noop,FogModifierStart=noop,CreateFogModifierRect=noop,FOG_OF_WAR_VISIBLE=1,SelectUnitForPlayerSingle=noop,
    PanCameraToTimedForPlayer=noop,SetUnitUseFood=lambda u,value:u.update(food=value)))
for fn in ('FFFarmInitIDs','FFBaseAngle','FFBaseFrontX','FFBaseFrontY','FFFarmSetPage','FFFarmCreate','FFFarmSpawn','FFFarmCast','FFDebugTaverns','FF_DebugHeroReady'):
    native(fn)
env['FFFarmInitIDs']()
for name in ('udg_spawn_unit','udg_base_type'):
    env[name].update({int(i):v for i,v in re.findall(r'set '+name+r"\[(\d+)\]\s*=\s*'(....)'",source)})
assert len(env['udg_spawn_unit'])>=51
def walkable(u):
    _,_,w,h = struct.unpack_from('<4s3i',pathing)
    x,y=int((u['x']+4096)//32),int((u['y']+4096)//32)
    return 0<=x<w and 0<=y<h and not pathing[16+x+w*y]&2
def click(farm,button,target=None):
    env.update(GetTriggerUnit=lambda:farm,GetSpellAbilityId=lambda:button,GetSpellTargetUnit=lambda:target)
    env['FFFarmCast']()
for pn in range(1,13):
    env['udg_player_active'][pn]=True
    env['udg_base'][pn]={'id':env['udg_base_type'][26+pn]}
    env['FFFarmCreate'](pn)
    farm=seen[-1]
    assert walkable(farm)
    for page in range(3):
        buttons=[f'aF{i:02}' for i in range(page*9,min(page*9+9,26))]
        assert farm['buttons']==set(buttons)
        card=[abilities[b]['fields'] for b in buttons+['aFLu','aFLd','aFPg']]
        assert len({(r['abpx',0],r['abpy',0]) for r in card})==len(card)
        assert len({r['Ncl6',1] for r in card})==len(card)
        for button in buttons:
            i=int(button[2:])
            click(farm,button)
            u=seen[-1]
            assert u['id']==env['udg_spawn_unit'][i] and u['p']==24 and walkable(u)
            expected=next((v for v in range(26,51) if env['udg_base_type'][v]==env['udg_base'][pn]['id'] and env['udg_spawn_unit'][v]==u['id']),i)
            assert stats[-2:]==[('compute',expected,pn),('apply',expected,pn)]
        click(farm,'aFPg')
    assert env['FFFarmPage'][pn]==0
    target={'level':1,'hero':True}
    for button,level in [('aFLd',1),('aFLu',2),('aFLu',3),('aFLd',2)]:
        click(farm,button,target)
        assert target['level']==level
env['FFDebugTaverns']()
count=env['FFDebugHeroCount']
shops=list(env['FFDebugShops'].values())
assert sum(map(len,stock.values()))==count and count==128
offset=13
for _ in range(2):
    offset+=4+4*struct.unpack_from('<I',terrain,offset)[0]
width,height,x0,y0=struct.unpack_from('<2i2f',terrain,offset)
tile_size=(len(terrain)-offset-16)//(width*height)
for shop in shops:
    tile=round((shop['x']-x0)/128)+width*round((shop['y']-y0)/128)
    assert terrain[offset+16+tile*tile_size+tile_size-1]&15==4 and walkable(shop) and shop['scale']==1.8
    buttons=stock[id(shop)]
    assert len(buttons)<=10
    for b in buttons:
        row=units[b]['fields']
        assert units[b]['parent']=='hfoo' and all(row[k,0]==0 for k in ('ugol','ulum','ufoo','usst'))
        assert row['ureq',0]=='' and mapping[id(shop),b] in units
pending = {}
accepted = []
shop = shops[0]
button = sorted(stock[id(shop)])[0]
def save(table,key,field,value):
    mapping[table,key,field] = value
def load(table,key,field):
    return mapping.get((table,key,field),mapping.get((key,field),0))
env.update(GetSellingUnit=lambda:shop,GetSoldUnit=lambda:token,SoloSub_ReownToSlot=noop,
    RemoveUnit=lambda u:u.update(removed=True),FF_AcceptStartingHero=accepted.append,CreateTimer=object,
    FF_DebugHireHash=2,SaveUnitHandle=save,SaveInteger=save,LoadInteger=load,LoadUnitHandle=load,
    TimerStart=lambda t,seconds,repeat,callback:pending.update({t:callback}),
    GetExpiredTimer=lambda:t,FlushChildHashtable=noop,DestroyTimer=noop,
    RemoveUnitFromStock=lambda u,b:stock[id(u)].discard(b))
for fn in ('FF_DebugHireComplete','DraftSale'):
    native(fn)
for i in range(150):
    pn=i%12+1
    token=create(pn,button,0,0,0)
    stock[id(shop)].discard(button)
    env['DraftSale']()
    t,restock=pending.popitem()
    restock()
    hero=accepted[-1]
    assert token['removed'] and hero['p']==pn and hero['id']==mapping[id(shop),button]
    assert hero['level']==18 and not hero['food'] and button in stock[id(shop)]
assert len(accepted)==150 and len({id(u) for u in accepted})==150
print(f'Verified both icon textures and bindings, {count} hero buttons, 150 repeated hires, targeted leveling and all 312 player/unit spawn combinations.')
