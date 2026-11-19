"""Prepare 799X RC25 from the full RC24 archive and update its editable JASS."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys
from PIL import Image, ImageEnhance

FEATURE=Path(__file__).resolve().parent
ROOT=FEATURE.parents[3]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'development/footmen/casino-v1')]
from map_archive import Archive
from restore_rc6_item_text import strings
from make_panel import blp
import objects
BASE='1d23bdb925e3e06bd5106e349d19093ef1ea8900f1a1f656e3d8b0b79a5020d4'
FUNC=re.compile(r'^function (\w+) takes[^\n]*\n[\s\S]*?^[ \t]*endfunction',re.M)
sha=lambda b:hashlib.sha256(b).hexdigest()

def once(s,a,b):
    if s.count(a)!=1:
        raise ValueError(f'Expected a single match for {a[:90]!r}, found {s.count(a)}')
    return s.replace(a,b)

def prepare(base,stage):
    assert sha(base.read_bytes())==BASE
    src=stage/'projects/799x/src'
    src.mkdir(parents=True,exist_ok=True)
    for n in ['tools.local.json','Build-Map.ps1','tools/Install-Wc3Map.ps1','tools/build_map.py','tools/map_archive.py']:
        dest=stage/n
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/n,dest)
    release=src.parent/'release'/base.name
    release.parent.mkdir(exist_ok=True)
    if not release.exists(): shutil.copyfile(base,release)
    meta=json.loads((ROOT/'projects/799x/project.json').read_text())
    meta.update(release=base.name,sha256=BASE)
    (src.parent/'project.json').write_text(json.dumps(meta,indent=2))
    dll=json.loads((ROOT/'tools.local.json').read_text())['stormlib']
    with Archive(dll,base) as arc:
        original=arc.read('war3map.j')
        j=original.decode().replace('\r\n','\n')
        roster=[(name,id) for name,idx,id in re.findall(r"// ([^\n]+)\nset udg_spawn_unit\[(\d+)\]='(....)'",j) if int(idx)<26]
        assert len(roster)==len({id for _,id in roster})==26
        roster=[({'Mortat Bombers':'Mortar Bombers','Milita':'Militia'}.get(name,name),id) for name,id in roster]
        registered=re.findall(r"set udg_hero_type\[\d+\]\s*=\s*'(....)'",j)
        heroes=objects.build(arc,src,strings(arc.read('war3map.wts')),roster,registered)
        assert len(heroes)==len(set(heroes)) and len(heroes)>=94
        imported=arc.read('war3map.imp')
        icon=Image.open(FEATURE/'page-turn.png').convert('RGBA').resize((64,64),Image.Resampling.LANCZOS)
        for name,img in [(objects.ICON,icon),(objects.ICON.replace('CommandButtons\\BTN','CommandButtonsDisabled\\DISBTN'),ImageEnhance.Brightness(icon).enhance(0.48))]:
            assert name.encode()+b'\0' not in imported
            dest=src/Path(name)
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(blp(img))
            imported+=bytes([13])+name.encode()+b'\0'
        (src/'war3map.imp').write_bytes(imported[:4]+struct.pack('<I',struct.unpack_from('<I',imported,4)[0]+2)+imported[8:])
        for n in ['war3map.wts','war3map.w3i']:
            (src/n).write_bytes(arc.read(n).replace(b'v7.9.9X-rc24',b'v7.9.9X-rc25'))
        manifest=json.loads(arc.read('FF_SOURCE_MANIFEST.json'))
        wct=arc.read('war3map.wct')
        eg=arc.read(r'source_roundtrip\globals.j')
        er=arc.read(r'source_roundtrip\FF_Runtime.j')
    j=j.replace('v7.9.9X-rc24','v7.9.9X-rc25')
    j=once(j,r'''call SaveStr(PF_prices,3,'hTNP',"ReplaceableTextures\\CommandButtons\\BTNReplay-SpeedUp.blp")''',
           r'''call SaveStr(PF_prices,3,'hTNP',"ReplaceableTextures\\CommandButtons\\BTNFootsPageTurn.blp")''')
    globals_j='''    integer array FFFarmPage
    integer array FFFarmButton
    integer array FFDebugHero
    integer array FFDebugHireButton
    integer FFDebugHeroCount = 0
    boolean FFDebugShopsReady = false
    unit array FFDebugShops'''
    j=once(j,'\nendglobals','\n'+globals_j+'\nendglobals')
    generated=("function FFFarmInitIDs takes nothing returns nothing\n"+
               "\n".join(f"    set FFFarmButton[{i}] = 'aF{i:02}'" for i in range(26))+
               "\n"+"\n".join(f"    set FFDebugHero[{i}] = '{id}'" for i,id in enumerate(heroes))+
               "\n"+"\n".join(f"    set FFDebugHireButton[{i}] = 'd{i:03}'" for i in range(len(heroes)))+
               f"\n    set FFDebugHeroCount = {len(heroes)}\nendfunction")
    def before(name,code):
        nonlocal j
        j=once(j,'function '+name+' takes',code+'\n\nfunction '+name+' takes')
    def edit(name,old,new):
        nonlocal j
        f=next(m[0] for m in FUNC.finditer(j) if m[1]==name)
        j=once(j,f,once(f,old,new))
    before('FF_DebugOpenHiring',generated+'\n\n'+(FEATURE/'farm.j').read_text('utf8'))
    edit('Trig_debugmode_Actions','    set udg_mode_debugmode=true','    set udg_mode_debugmode=true\n    call FFFarmInitIDs()')
    edit('Trig_debugmode_Actions',"""            set udg_temp_point=OffsetLocation(GetPlayerStartLocationLoc(ConvertedPlayer(udg_X)), 175.00, 0)
            call CreateNUnitsAtLoc(1, 'n034', ConvertedPlayer(udg_X), udg_temp_point, bj_UNIT_FACING)""",'            call FFFarmCreate(udg_X)')
    # Replace the obsolete primary-hero and 50-footmen branches at the original trigger entry.
    current=next(m[0] for m in FUNC.finditer(j) if m[1]=='InitTrig_debug_control')
    a=j.index('function Trig_debug_control_Func008Func002C takes')
    b=j.index(current,a)+len(current)
    j=j[:a]+current.replace('EVENT_PLAYER_UNIT_SPELL_CAST','EVENT_PLAYER_UNIT_SPELL_EFFECT').replace('    call TriggerAddCondition(gg_trg_debug_control, Condition(function Trig_debug_control_Conditions))\n','').replace('function Trig_debug_control_Actions','function FFFarmCast')+j[b:]
    before('DraftUpdate',(FEATURE/'high_ground.j').read_text('utf8'))
    edit('DraftUpdate','    loop','    if udg_mode_debugmode and not FFDebugShopsReady then\n        call FFDebugTaverns()\n    endif\n    loop')
    edit('DraftUpdate','if team >= 1','if not udg_mode_debugmode and team >= 1')
    edit('DraftUpdate','                set x = DraftX[team] + 180. * (ModuloInteger(pn-1,3) - 1)\n                set y = DraftY[team]','                set x = FFBaseFrontX(pn,320.,0.)\n                set y = FFBaseFrontY(pn,320.,0.)')
    edit('DraftUpdate','                call BlzSetUnitName(shop,','                call BlzSetUnitRealField(shop,UNIT_RF_SELECTION_SCALE,0.9*BlzGetUnitRealField(shop,UNIT_RF_SELECTION_SCALE))\n                call BlzSetUnitName(shop,')
    # Shared debug shops own their buyers and sight independently of the rolled draft mode.
    f=next(m[0] for m in FUNC.finditer(j) if m[1]=='DraftStart')
    a=f.index('        if udg_mode_debugmode then\n            set i = 1')
    b=f.index('        endif\n    endif\n    call TriggerRegisterAnyUnitEventBJ(sales',a)
    j=once(j,f,f[:a]+f[b+len('        endif\n'):])
    edit('DraftStart','call ShowUnit(udg_real_shop[i], udg_mode_debugmode)','call ShowUnit(udg_real_shop[i], false)')
    edit('DraftClosePlayer','    set DraftPicked[pn] = true','    if udg_mode_debugmode then\n        return\n    endif\n    set DraftPicked[pn] = true')
    edit('FF_AcceptStartingHero','if udg_selected_mode == 3 and DraftPicked','if not udg_mode_debugmode and udg_selected_mode == 3 and DraftPicked')
    edit('FF_AcceptStartingHero','if udg_selected_mode == 3 and not udg_mode_mirror','if not udg_mode_debugmode and udg_selected_mode == 3 and not udg_mode_mirror')
    edit('FF_DebugHireComplete','            call MF_StockUnit(shop, kind, 2, 2)',"""            if GetUnitTypeId(shop) == 'nDbT' then
                call AddUnitToStock(shop,kind,2,2)
            else
                call MF_StockUnit(shop, kind, 2, 2)
            endif""")
    edit('DraftSale',"    if GetUnitTypeId(shop) != 'nTDP' then","""    if udg_mode_debugmode and GetUnitTypeId(shop) == 'nDbT' then
        call SoloSub_ReownToSlot(sold)
        set p = GetOwningPlayer(sold)
        set pn = GetConvertedPlayerId(p)
        call RemoveUnit(sold)
        set i = LoadInteger(DraftStock,GetHandleId(shop),id)
        if pn >= 1 and pn <= 12 and i != 0 then
            set sold = CreateUnit(p,i,FFBaseFrontX(pn,160.,0.),FFBaseFrontY(pn,160.,0.),270.)
            if sold != null then
                call FF_AcceptStartingHero(sold)
            endif
            set deferred = CreateTimer()
            call SaveUnitHandle(FF_DebugHireHash,GetHandleId(deferred),0,sold)
            call SaveUnitHandle(FF_DebugHireHash,GetHandleId(deferred),1,shop)
            call SaveInteger(FF_DebugHireHash,GetHandleId(deferred),2,id)
            call TimerStart(deferred,0.,false,function FF_DebugHireComplete)
            set deferred = null
        endif
        set p = null
    endif
    if GetUnitTypeId(shop) != 'nTDP' then""")
    cam='call PanCameraToTimedForPlayer(udg_temp_player, DraftX[udg_teamnumber[udg_temp_playernumber]], DraftY[udg_teamnumber[udg_temp_playernumber]], 0.25)'
    assert j.count(cam)==2
    j=j.replace(cam,'call PanCameraToTimedForPlayer(udg_temp_player, FFBaseFrontX(udg_temp_playernumber,320.,0.), FFBaseFrontY(udg_temp_playernumber,320.,0.), 0.25)')
    def encode(s,ref):
        return (s.replace('\n','\r\n') if b'\r\n' in ref else s).encode()
    (src/'war3map.j').write_bytes(encode(j,original))
    funcs={m[1]:m[0] for m in FUNC.finditer(j)}
    emitted=set(manifest['editor_generated_functions'])
    assert not emitted-funcs.keys()
    runtime=er.decode().replace('\r\n','\n').split('// FF Runtime is initialized once')[0]+'// FF Runtime is initialized once by the editor.\n\n'+'\n\n'.join(f for n,f in funcs.items() if n not in emitted)+'\n'
    globals_code=once(eg.decode().replace('\r\n','\n'),'\nendglobals','\n'+globals_j+'\nendglobals')
    for old,code,n,key in [(eg,globals_code,'globals','globals_sha256'),(er,runtime,'FF_Runtime','runtime_sha256')]:
        new=encode(code,old)
        wct=once(wct,struct.pack('<I',len(old)+1)+old+b'\0',struct.pack('<I',len(new)+1)+new+b'\0')
        dest=src/'source_roundtrip'/(n+'.j')
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(new)
        manifest[key]=sha(new)
    (src/'war3map.wct').write_bytes(wct)
    manifest.update(revision='799X RC25 tavern and debug farm',source_map_sha256=BASE,compiled_source_sha256=sha((src/'war3map.j').read_bytes()),runtime_functions=len(funcs)-len(emitted),engine_playtest=False)
    (src/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f"Prepared {len(heroes)} debug heroes and {len(roster)} army units.")

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('base',type=Path)
    parser.add_argument('stage',type=Path)
    args=parser.parse_args()
    prepare(args.base,args.stage)
