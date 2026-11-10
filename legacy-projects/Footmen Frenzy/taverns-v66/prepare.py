from pathlib import Path
import re,struct,sys,copy,json
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'hero-polish'))
from archive_helpers import functions,objdata
O=R/'src';O.mkdir(exist_ok=True)
added='''hashtable T66_StockHash = InitHashtable()
integer array T66_RandomLeft
unit array T66_Buyer
unit array T66_CarryBuyer
unit T66_LastBuyer = null
boolean array T66_Archived
quest array T66_RecordQuest
string array T66_RecordText
string array T66_Offers
integer T66_ViewCount = 0
fogmodifier array T66_Views
'''
rangehelper='''function MF_SetAttackRange takes unit u, real desired returns nothing
    local real primary = BlzGetUnitWeaponRealField(u, UNIT_WEAPON_RF_ATTACK_RANGE, 0)
    local real secondary = BlzGetUnitWeaponRealField(u, UNIT_WEAPON_RF_ATTACK_RANGE, 1)
    call BlzSetUnitWeaponRealField(u, UNIT_WEAPON_RF_ATTACK_RANGE, 1, desired - primary + secondary)
endfunction
'''
def patch(s):
 s=s.replace('\r','')
 def put(n,body):
  nonlocal s
  old=functions(s)[n];s=s.replace(old,body.strip(),1)
 s=s.replace(functions(s)['FFGS_ApplyUnit'],rangehelper+'\n'+functions(s)['FFGS_ApplyUnit'],1)
 s=s.replace('call BlzSetUnitWeaponRealField(u, UNIT_WEAPON_RF_ATTACK_RANGE, 1, udg_unit_range_actual[idx])','call MF_SetAttackRange(u, udg_unit_range_actual[idx])')
 s=re.sub(r'call BlzSetUnitWeaponRealFieldBJ\((udg_spawned_unit\[udg_temp_int\]), UNIT_WEAPON_RF_ATTACK_RANGE, 1, (udg_unit_range(?:_actual)?\[udg_X_base\])\)',r'call MF_SetAttackRange(\1, \2)',s)
 # Remember the actual offered stock, including mirror and old SD paths.
 b=functions(s)['MF_StockUnit']
 b=b.replace('returns nothing\n','returns nothing\n    local integer key = GetHandleId(shop)\n    local integer count\n',1)
 b=b.replace('        call AddUnitToStock', """        if current > 0 and id != 'h004' and id != 'H0R0' and not LoadBoolean(T66_StockHash, key, id) then
            set count = LoadInteger(T66_StockHash, key, 0) + 1
            call SaveInteger(T66_StockHash, key, 0, count)
            call SaveInteger(T66_StockHash, key, count, id)
            call SaveBoolean(T66_StockHash, key, id, true)
        endif
        call AddUnitToStock""")
 put('MF_StockUnit',b)
 # AR repick now leaves the slot ready for the team's shared Random button.
 for n in ['Trig_repick_command_Func002Func006Func002A','Trig_repick_command_Func002Func006Func003A']:
  put(n,functions(s)[n].replace('call CreateNUnitsAtLoc(1, udg_random_hero[udg_temp_playernumber], udg_temp_player, udg_loc_tavern, bj_UNIT_FACING)', 'call T66_Position(udg_teamnumber[udg_temp_playernumber], false)\n            call SelectUnitForPlayerSingle(CarryTav_shop[udg_teamnumber[udg_temp_playernumber]], udg_temp_player)\n            call PanCameraToTimedForPlayer(udg_temp_player, GetUnitX(CarryTav_shop[udg_teamnumber[udg_temp_playernumber]]), GetUnitY(CarryTav_shop[udg_teamnumber[udg_temp_playernumber]]), 0.25)'))
 # Track only tavern vision so the draft archive can stop it without changing combat vision.
 s=re.sub(r'call CreateFogModifierRectBJ\(true, (.*?), FOG_OF_WAR_VISIBLE, (gg_rct_TAVERN_AREA)\)',r'call T66_View(\1, \2)',s)
 s=s.replace('set udg_Tavern_Visibility[udg_X]=GetLastCreatedFogModifier()','set udg_Tavern_Visibility[udg_X]=T66_Views[T66_ViewCount]')
 helper=(R/'draft.j').read_text()
 helper=helper.replace('call QuestSetDescription(T66_RecordQuest[team], T66_Offers[team]', 'set T66_RecordText[team] = T66_Offers[team]').replace('team category limits still apply.")','team category limits still apply."\n            call QuestSetDescription(T66_RecordQuest[team], T66_RecordText[team])')
 helper=helper.replace('QuestGetDescription(T66_RecordQuest[team])','T66_RecordText[team]')
 # Early helper location precedes all existing vision setup.
 s=s.replace(functions(s)['MF_HeroDisabled'],helper+'\n'+functions(s)['MF_HeroDisabled'],1)
 for n in ['Trig_Start_SD_Func015A','Trig_Start_SD_Func016A','Trig_Start_SD_Func017A','Trig_Start_SD_Func018A','Trig_restore_visibility_to_tavern_Func002A']:
  put(n,'function '+n+' takes nothing returns nothing\n    // Draft records are public without permanent tavern vision.\nendfunction')
 put('FFHire_CreateBuyer',functions(s)['FFHire_CreateBuyer'].replace('    set buyer = null','    set T66_LastBuyer = buyer\n    set buyer = null'))
 put('FFHire_Prepare',(R/'hiring.j').read_text())
 for n,b in functions((R/'random.j').read_text()).items():put(n,b)
 put('CarryTav_MakeAltar',functions(s)['CarryTav_MakeAltar'].replace("'n02I'","'n66A'").replace("    call MF_StockUnit(CarryTav_shop[whichTeam], 'H0R0', 1, 1)\n",''))
 # Lock every carry stock entry, including mirror/legacy drafts moved at startup.
 b=functions(s)['CarryTav_LockTeam']
 b=b.replace('    call DisplayTimedTextToForce', """    set i = 1
    loop
        exitwhen i > LoadInteger(T66_StockHash, GetHandleId(CarryTav_shop[whichTeam]), 0)
        call RemoveUnitFromStock(CarryTav_shop[whichTeam], LoadInteger(T66_StockHash, GetHandleId(CarryTav_shop[whichTeam]), i))
        set i = i + 1
    endloop
    call DisplayTimedTextToForce""")
 put('CarryTav_LockTeam', b)
 put('FFR_Choose',functions(s)['FFR_Choose'].replace(' and not FFR_Seeded[i]',''))
 # Purchases at the base use the same initialization as purchases at the west plaza.
 sale='''function T66_HeroSold takes nothing returns nothing
    local unit u = GetSoldUnit()
    local unit shop = GetSellingUnit()
    local integer team = 1
    if IsUnitType(u, UNIT_TYPE_HERO) and not RectContainsUnit(gg_rct_TAVERN_AREA, u) then
        loop
            exitwhen team > 4
            if shop == udg_real_shop[team] or shop == CarryTav_shop[team] then
                call SetUnitPosition(u, GetRectCenterX(gg_rct_TAVERN_AREA), GetRectCenterY(gg_rct_TAVERN_AREA))
                exitwhen true
            endif
            set team = team + 1
        endloop
    endif
    set u = null
    set shop = null
endfunction
'''
 put('InitTrig_TP_hero',sale+'\n'+functions(s)['InitTrig_TP_hero'].replace('call TriggerAddAction(debugSales, function FF_DebugHeroSold)','call TriggerAddAction(debugSales, function T66_HeroSold)\n    call TriggerAddAction(debugSales, function FF_DebugHeroSold)'))
 put('Trig_Start_game_Actions',functions(s)['Trig_Start_game_Actions'].replace('        call T66_View(ConvertedPlayer(udg_X), gg_rct_TAVERN_AREA)', '        if udg_selected_mode == 2 then\n            call T66_View(ConvertedPlayer(udg_X), gg_rct_TAVERN_AREA)\n        endif'))
 # AP iterates the authoritative roster; nine shops, max eleven units each.
 b=functions(s)['Trig_Start_AP_Actions']
 start=b.index('    set udg_X=1\n    loop\n        exitwhen udg_X > 11')
 end=b.index('    call EnableSelect',start)
 b=b[:start]+'''    set udg_X=1
    loop
        exitwhen udg_X > udg_total_hero_count
        call MF_StockUnitBJ(udg_hero_type[udg_X], udg_real_shop[13 + (udg_X - 1) / 11], 2, 2)
        set udg_X=udg_X+1
    endloop
'''+b[end:]
 b=b.replace('exitwhen udg_X > 8','exitwhen udg_X > 9')
 put('Trig_Start_AP_Actions',b)
 return s

def globals_patch(s):
 return s.replace('boolean FFHire_Ready',added+'boolean FFHire_Ready',1)
original=(R/'original/war3map.j').read_bytes().decode('latin1')
s=globals_patch(patch(original));(O/'war3map.j').write_bytes(s.encode('latin1'))
w=(R/'original/war3map.wct').read_bytes();p=w.index(0,8)+1;prefix=w[:p];chunks=[]
while p<len(w):
 n=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+n];p+=n
 t=b.rstrip(b'\0').decode('latin1')
 if 'function Trig_Start_game_Actions takes' in t:t=patch(t)
 if 'boolean FFHire_Ready' in t:t=globals_patch(t)
 chunks.append(t.encode('latin1')+(b'\0' if b.endswith(b'\0') else b''))
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))

def field(e,k,t,v):
 e['mods']=[m for m in e['mods'] if m['id']!=k];e['mods'].append(dict(id=k,type=t,value=v,end='00000000'))
for file in ['war3map.w3u','war3mapSkin.w3u']:
 d=objdata.load(str(R/'original'/file));base=next(e for e in d['tables'][1] if e['newId']=='n02I')
 altar=copy.deepcopy(base);altar['newId']='n66A';d['tables'][1].append(altar)
 if file=='war3mapSkin.w3u':
  field(base,'umdl',3,r'buildings\other\Tavern\Tavern.mdl');field(base,'usca',1,0.8)
  field(altar,'umdl',3,r'buildings\human\AltarofKings\AltarofKings.mdl');field(altar,'usca',1,0.85)
  field(altar,'uico',3,r'ReplaceableTextures\CommandButtons\BTNAltarOfKings.blp');field(altar,'unam',3,'Carry Altar')
 for tab in d['tables']:
  for e in tab:
   if e['newId'] in ['n02I','n66A','n01A'] and file=='war3map.w3u':
    field(e,'usid',0,0);field(e,'usin',0,0)
   if e['newId']=='h004':
    if file=='war3map.w3u':
     field(e,'usrg',0,999999);field(e,'usma',0,3);field(e,'usst',0,0)
    field(e,'utub',3,'Random Hero: 3 shared uses per team. Draws from the full eligible roster, respecting team carry/category limits. Available only at your team Carry Altar.')
 (O/file).write_bytes(objdata.dump(d))
wts=(R/'original/war3map.wts').read_bytes().decode('utf-8-sig')
for n,text in {1:'Footmen Frenzy 799X v66 - Team Taverns',997:'799X v66 - Team Taverns',998:'Test build - October 29, 2026',999:'v66: Base taverns and Human Carry Altars. Three shared Random uses per team. Public draft records in F9 / -draft. Footman range correction. Includes Mundo cloud fix.',3435:'799X v66 - Team Taverns|nBase draft taverns; 3 shared Random uses per team.|nPublic draft records: F9 or -draft.|nFootman range and Mundo cloud fixes.|n'}.items():
 wts=re.sub(r'(STRING '+str(n)+r'\s*\{).*?(\})',lambda m:m[1]+'\n'+text+'\n'+m[2],wts,flags=re.S)
(O / 'war3map.wts').write_bytes(re.sub(r'\r+\n', '\n', wts).replace('\n', '\r\n').encode('utf-8'))
(O/'FF_MAINTENANCE.md').write_bytes((R/'original/FF_MAINTENANCE.md').read_bytes()+b'\n\nv66: Base SD taverns, Human Carry Altar, team-wide 3-use Random, public F9 draft archive, dynamic AP roster bound, compensated spawn attack range. Runtime and WCT synchronized. Engine playtest pending.\n')
print('Prepared v66')
