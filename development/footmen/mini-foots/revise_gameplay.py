# Executed by build_source with its parsed objects and function replacement helpers.
def setmod(e, key, value, typ):
    found=False
    for m in e['mods']:
        if m['id']==key:
            m['value']=value; m['type']=typ; found=True
    if not found:
        e['mods'].append({'id':key,'type':typ,'value':value,'end':'00000000'})

# T1 melee replacements use the existing modified standard objects, including abilities.
# Keep each replaced tech path's production cadence, bounty and T1 unit level.
for old,new,indices,stats in [
    ('nskf','ugho',[17,44],{'HP':675,'armor':1,'att_base':14,'att_num_dice':2,'att_dice_sides':2,'att_CD':1.1}),
    ('ohun','ogru',[23,27],{'HP':800,'armor':2,'att_base':24,'att_num_dice':1,'att_dice_sides':4,'att_CD':1.6})]:
    s=s.replace("'"+old+"'", "'"+new+"'") # Includes XP classification and stats feed checks.
    for idx in indices:
        for field,value in dict(stats,armor_type=2,range=110).items():
            s,n=re.subn(r'(set udg_unit_'+field+r'\['+str(idx)+r'\]=)[^\r\n]+',lambda m:m[1]+str(value),s)
            assert n>0,(idx,field)
    setmod(es[new],'uhpm',stats['HP'],0)
    setmod(es[new],'udef',stats['armor'],0)
    setmod(es[new],'uabi','ACce,ACev,A0D9' if new=='ugho' else 'ACev,A0D9',3)
    setmod(es[new],'udaa','',3)
    setmod(es[new],'udty','large',3)
    setmod(es[new],'ua1t','normal',3)
    setmod(es[new],'ua2t','normal',3)
for uid,indices in [('esen',[22,28]),('uban',[9,39]),('ngh2',[20,47]),('hmil',[18,48])]:
    armor_type=2 if uid=='hmil' else 7
    setmod(es[uid],'udty','large' if uid=='hmil' else 'none',3)
    for idx in indices:
        s,n=re.subn(r'(set udg_unit_armor_type\['+str(idx)+r'\]=)\d+',lambda m:m[1]+str(armor_type),s)
        assert n>0
        if uid=='hmil':
            s,n=re.subn(r'(set udg_unit_HP\['+str(idx)+r'\]=)\d+',lambda m:m[1]+'900',s)
            assert n>0
    if uid=='hmil':setmod(es[uid],'uhpm',900,0)
# Remove the inherited late override that forced Banshee/Wraith back to medium.
s=s.replace("    if ( GetUnitTypeId(u) == 'uban' ) or ( GetUnitTypeId(u) == 'ngh2' ) then\n        call BlzSetUnitIntegerField(u, UNIT_IF_DEFENSE_TYPE, 1)\n    endif\n",'')
for base,title,icon,description in [
    ('h00Z','Ghoul','BTNGhoul','675 HP; 1 heavy armor. Cleaving Attack, Evasion and Charge.'),
    ('h02O','Ghoul','BTNGhoul','675 HP; 1 heavy armor. Cleaving Attack, Evasion and Charge.'),
    ('h00H','Grunt','BTNGrunt','800 HP; 2 heavy armor. Evasion and Charge.'),
    ('h023','Grunt','BTNGrunt','800 HP; 2 heavy armor. Evasion and Charge.')]:
    setmod(es[base],'unam',title+' Tech',3)
    setmod(es[base],'utip','Upgrade to '+title+' Tech',3)
    setmod(es[base],'utub','Spawns '+title+' units. '+description,3)
    setmod(es[base],'uico','ReplaceableTextures\\CommandButtons\\'+icon+'.blp',3)

special=set()
for id in allowed:
    if id != 'hbar':
        setmod(es[id],'ugol',600 if mods(es[id]).get('ureq')=='R00D' else 1300,0)
    special.update(set(mods(es[id]).get('ures','').split(','))-{'','Rhme','Rhar'})
    setmod(es[id],'ures','Rhme,Rhar',3)
fn('FFRacial_ShareResearch','function FFRacial_ShareResearch takes nothing returns nothing\nendfunction')
spawnids=set(re.findall(r"set udg_spawn_unit\[\d+\]='(....)'",s))
for id in spawnids:
    assert id in es,id
    for field in ['ua1r','ua2r']:
        setmod(es[id],field,0,0)

# Remove transmute heroes from category selection, physical shops and random fallbacks.
xindices=re.findall(r'set udg_hero_category\[(\d+)\]=11',s)
xheroes={re.search(r"set udg_hero_type\["+i+r"\]='(....)'",s)[1] for i in xindices}
for i in xindices:
    s=s.replace(f'set udg_hero_category[{i}]=11',f'set udg_hero_category[{i}]=0')
for e in es.values():
    for m in e['mods']:
        if m['id']=='useu':
            m['value']=','.join(v for v in m['value'].split(',') if v not in xheroes)
s=s.replace('udg_hero_type[i] != 0 and ( udg_hero_category[i] < 12', 'udg_hero_type[i] != 0 and udg_hero_category[i] > 0 and ( udg_hero_category[i] < 12')
s=s.replace('if team < 1 or team > 4 or index < 1 then','if team < 1 or team > 4 or index < 1 or udg_hero_category[index] == 0 then')
s=s.replace('"|cff00ffffNo Transmute:|r |cffff0000Off|r"','"|cff00ffffNo Transmute:|r |cff00ff00On|r"')
extra=''.join(f"        call SetPlayerTechMaxAllowed(Player(i), '{id}', 0)\n" for id in sorted(special|xheroes))
s=s.replace("        call SetPlayerTechMaxAllowed(Player(i), 'R00E', 0)\n", "        call SetPlayerTechMaxAllowed(Player(i), 'R00E', 0)\n"+extra)
(O/'war3map.w3u').write_bytes(objdata.dump(u))

# Separate perpendicular fronts, selected by each player's base position.
s=s.replace('integer array MF_TeamStaged','integer array MF_PlayerStaged')
s=s.replace('local integer n=MF_TeamStaged[team]\n    local real x=160.0 + I2R(ModuloInteger(n, 10)) * 72.0\n    local real y=160.0 + I2R(n / 10) * 72.0', '''local integer n=MF_PlayerStaged[pn]
    local integer col=ModuloInteger(n, 12)
    local real x
    local real y
    if RAbsBJ(GetUnitY(udg_base[pn]) - ffgs_center_y) > RAbsBJ(GetUnitX(udg_base[pn]) - ffgs_center_x) then
        set x=640.0 + I2R(col) * 64.0
        set y=160.0 + I2R(n / 12) * 64.0
    else
        set x=160.0 + I2R(n / 12) * 64.0
        set y=640.0 + I2R(col) * 64.0
    endif
''')
s=s.replace('set MF_TeamStaged[team]=n + 1','set MF_PlayerStaged[pn]=n + 1')
for old,new in [('484.0','688.0'),('412.0','688.0')]:
    body=re.search(r'function MF_MassPoint takes .*?\nendfunction',s,re.S).group()
    fn('MF_MassPoint',body.replace(old,new))

# Only the two RJE accounts already recognized by this map get a mode dialog.
insert_before('Trig_MODE_GUI_show_Actions','''function MF_IsRJE takes player p returns boolean
    local string name=udg_orig_player_name[GetPlayerId(p) + 1]
    return name == "RJE#11113" or name == "RJE#2927"
endfunction''')
fn('Trig_MODE_GUI_show_Actions','''function Trig_MODE_GUI_show_Actions takes nothing returns nothing
    local integer i=0
    local integer pn
    local player p=null
    call FFR4_LockPooling()
    set FFR4Pro=false
    set FFR4NoPool=true
    loop
        exitwhen i >= 12
        if GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING and MF_IsRJE(Player(i)) then
            set p=Player(i)
            exitwhen true
        endif
        set i=i + 1
    endloop
    if p == null then
        set udg_Host=Player(0)
        call FFMode_Resolve()
        call ConditionalTriggerExecute(gg_trg_MODE_set_pub_game_default)
        return
    endif
    set udg_Host=p
    set pn=GetPlayerId(p) + 1
    call DialogClear(udg_dlg_mode[pn])
    call DialogSetMessage(udg_dlg_mode[pn], "Mini Foots: choose mode (10 seconds)")
    set udg_dlg_btn_mode_01[pn]=DialogAddButton(udg_dlg_mode[pn], "Pub Mode", 0)
    set udg_dlg_btn_mode_04[pn]=DialogAddButton(udg_dlg_mode[pn], "Debug Mode", 0)
    call DialogDisplay(p, udg_dlg_mode[pn], true)
    call FFMode_BeginCountdown(1)
    set p=null
endfunction''')
body=re.search(r'function Trig_MODE_GUI_execute_Actions takes .*?\nendfunction',s,re.S).group()
body=body.replace('local integer pn=1','local integer pn=GetPlayerId(p) + 1').replace('if p != Player(0) then','if p != udg_Host or not MF_IsRJE(p) then')
fn('Trig_MODE_GUI_execute_Actions',body)
s=s.replace('set udg_wmd[10]="|cff00ffffNo Pool:|r |cff00ff00On|r"','set udg_wmd[10]="|cff00ffffPooling:|r 10 seconds before T1"')

# Derive pooling from the actual T1 timer, including the immediate debug unlock.
insert_before('Trig_start_timers_Actions','''function MF_EnablePooling takes nothing returns nothing
    set FFR4NoPool=false
    set udg_autopoool_allowed=true
    call SetMapFlag(MAP_RESOURCE_TRADING_ALLIES_ONLY, true)
    call SetMapFlag(MAP_LOCK_RESOURCE_TRADING, false)
    set udg_wmd[10]="|cff00ffffPooling:|r |cff00ff00On|r"
    call EnableTrigger(gg_trg_autopool_time)
    call EnableTrigger(gg_trg_autopool_command)
    call EnableTrigger(gg_trg_autopool_execute)
    call DisplayTextToForce(udg_all_players, "Pooling is now enabled.")
endfunction''')
body=re.search(r'function Trig_start_timers_Actions takes .*?\nendfunction',s,re.S).group()
body=body.replace('    call CreateTimerDialogBJ(udg_timer_tech_delay_t1', '''    call DisableTrigger(gg_trg_turn_trading_ON)
    call PauseTimer(udg_timer_trading)
    if udg_timer_window_trading != null then
        call TimerDialogDisplayBJ(false, udg_timer_window_trading)
    endif
    call TimerStart(udg_timer_trading, RMaxBJ(0.0, TimerGetRemaining(udg_timer_tech_delay_t1) - 10.0), false, function MF_EnablePooling)
    call CreateTimerDialogBJ(udg_timer_tech_delay_t1''')
fn('Trig_start_timers_Actions',body)

# Use a genuine vertical SLIDER with its thumb, rather than a child quest scrollbar.
# Frame layout reference: https://www.hiveworkshop.com/threads/ui-creating-a-cam-control.315961/
(O/'MiniFootsUI.fdf').write_text('''Frame "SLIDER" "MiniFootsZoomSlider" {
    SliderLayoutVertical,
    Width 0.012,
    Height 0.095,
    ControlBackdrop "MFZoomTrack",
    Frame "BACKDROP" "MFZoomTrack" {
        DecorateFileNames,
        BackdropBlendAll,
        BackdropBackground "EscMenuSliderBackground",
        BackdropEdgeFile "EscMenuSliderBorder",
        BackdropCornerFlags "UL|UR|BL|BR|T|L|B|R",
        BackdropCornerSize 0.004,
        BackdropBackgroundInsets 0.002 0.002 0.002 0.002,
    }
    ControlDisabledBackdrop "MFZoomLockedTrack",
    Frame "BACKDROP" "MFZoomLockedTrack" {
        DecorateFileNames,
        BackdropBlendAll,
        BackdropBackground "EscMenuSliderBackground",
        BackdropEdgeFile "EscMenuSliderBorder",
        BackdropCornerFlags "UL|UR|BL|BR|T|L|B|R",
        BackdropCornerSize 0.004,
    }
    SliderThumbButtonFrame "MFZoomThumb",
    Frame "BUTTON" "MFZoomThumb" {
        Width 0.014,
        Height 0.014,
        ControlBackdrop "MFZoomThumbArt",
        Frame "BACKDROP" "MFZoomThumbArt" {
            DecorateFileNames,
            BackdropBlendAll,
            BackdropBackground "EscMenuSliderThumbButton",
        }
        ControlDisabledBackdrop "MFZoomLockedThumbArt",
        Frame "BACKDROP" "MFZoomLockedThumbArt" {
            DecorateFileNames,
            BackdropBlendAll,
            BackdropBackground "EscMenuSliderDisabledThumbButton",
        }
    }
}
''')
(O/'MiniFootsUI.toc').write_text('UI\\FrameDef\\UI\\escmenutemplates.fdf\nMiniFootsUI.fdf\n')
imp=(B/'war3map.imp').read_bytes()
version,count=struct.unpack_from('<ii',imp)
(O/'war3map.imp').write_bytes(struct.pack('<ii',version,count+2)+imp[8:]+b'\rMiniFootsUI.fdf\0\rMiniFootsUI.toc\0')
body=re.search(r'function zoom__CreateSlider takes .*?\nendfunction',s,re.S).group()
body=body.replace('BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)', 'BlzGetFrameByName("ConsoleUIBackdrop", 0)')
body=body.replace('    local trigger sliderTrigger', '    local framehandle minimap=BlzGetOriginFrame(ORIGIN_FRAME_MINIMAP, 0)\n    local trigger sliderTrigger')
body=body.replace('    set zoom__slider=BlzCreateFrameByType("SLIDER", "FootmenZoomVertical", gameUI, "QuestMainListScrollBar", 0)', '''    call BlzLoadTOCFile("MiniFootsUI.toc")
    set zoom__slider=BlzCreateFrame("MiniFootsZoomSlider", gameUI, 0, 0)''')
body=body.replace('call BlzFrameSetAbsPoint(zoom__slider, FRAMEPOINT_CENTER, 0.190, 0.078)', 'call BlzFrameSetPoint(zoom__slider, FRAMEPOINT_LEFT, minimap, FRAMEPOINT_RIGHT, 0.033, 0.0)')
body=body.replace('call BlzFrameSetSize(zoom__slider, 0.009, 0.095)', 'call BlzFrameSetSize(zoom__slider, 0.012, 0.095)\n    call BlzFrameSetLevel(zoom__slider, 20)')
body=body.replace('call BlzFrameSetAbsPoint(zoom__sliderLabel, FRAMEPOINT_CENTER, 0.190, 0.029)', 'call BlzFrameSetPoint(zoom__sliderLabel, FRAMEPOINT_TOP, zoom__slider, FRAMEPOINT_BOTTOM, 0.0, -0.003)\n    call BlzFrameSetEnable(zoom__sliderLabel, false)')
body=body.replace('call BlzFrameSetAbsPoint(zoom__lockButton, FRAMEPOINT_CENTER, 0.190, 0.132)', 'call BlzFrameSetPoint(zoom__lockButton, FRAMEPOINT_BOTTOM, zoom__slider, FRAMEPOINT_TOP, 0.0, 0.003)')
body=body.replace('call BlzFrameSetAbsPoint(zoom__lockLabel, FRAMEPOINT_CENTER, 0.190, 0.132)', 'call BlzFrameSetPoint(zoom__lockLabel, FRAMEPOINT_CENTER, zoom__lockButton, FRAMEPOINT_CENTER, 0.0, 0.0)\n    call BlzFrameSetEnable(zoom__lockLabel, false)')
body=body.replace('    set gameUI=null','    set minimap=null\n    set gameUI=null')
fn('zoom__CreateSlider',body)
body=re.search(r'function DPS_Create takes .*?\nendfunction',s,re.S).group()
body=body.replace('set DPS_Button = BlzCreateFrame("ScriptDialogButton", ui, 0, 0)', 'set DPS_Button = BlzCreateFrame("ScriptDialogButton", BlzGetFrameByName("ConsoleUIBackdrop", 0), 0, 0)')
fn('DPS_Create',body)
s=s.replace('BlzFrameSetText(DPS_Button, "Player stats")','BlzFrameSetText(DPS_Button, "Stats")').replace('BlzFrameSetText(DPS_Button, "Hide player stats")','BlzFrameSetText(DPS_Button, "Stats")')
s=s.replace('call BlzFrameSetSize(DPS_Button, 0.125, 0.024)','call BlzFrameSetSize(DPS_Button, 0.0625, 0.020)')
s=s.replace('call BlzFrameSetPoint(DPS_Button, FRAMEPOINT_TOPRIGHT, board, FRAMEPOINT_BOTTOMRIGHT, 0.0, -0.002)', 'call BlzFrameSetPoint(DPS_Button, FRAMEPOINT_BOTTOM, BlzGetOriginFrame(ORIGIN_FRAME_MINIMAP, 0), FRAMEPOINT_TOP, 0.0, 0.002)')
s=s.replace('call BlzFrameSetPoint(DPS_Panel, FRAMEPOINT_TOPRIGHT, DPS_Button, FRAMEPOINT_BOTTOMRIGHT, 0.0, -0.002)', 'call BlzFrameSetAbsPoint(DPS_Panel, FRAMEPOINT_TOPLEFT, 0.0175, 0.540)')

# Warcraft's range setter adds a delta based on the two weapon fields.
# Compensate for their current difference, making repeated applications idempotent.
# https://www.hiveworkshop.com/threads/snippet-set-unit-range-partial-fix-set-unit-aoe-small-fix.352220/
insert_before('FFGS_ApplyUnit','''function MF_SetAttackRange takes unit u, real desired returns nothing
    local real primary=BlzGetUnitWeaponRealField(u, UNIT_WEAPON_RF_ATTACK_RANGE, 0)
    local real secondary=BlzGetUnitWeaponRealField(u, UNIT_WEAPON_RF_ATTACK_RANGE, 1)
    call BlzSetUnitWeaponRealField(u, UNIT_WEAPON_RF_ATTACK_RANGE, 1, desired - primary + secondary)
endfunction''')
s=s.replace('call BlzSetUnitWeaponRealField(u, UNIT_WEAPON_RF_ATTACK_RANGE, 1, udg_unit_range_actual[idx])','call MF_SetAttackRange(u, udg_unit_range_actual[idx])')
s=re.sub(r'call BlzSetUnitWeaponRealFieldBJ\((udg_spawned_unit\[udg_temp_int\]), UNIT_WEAPON_RF_ATTACK_RANGE, 1, (udg_unit_range(?:_actual)?\[udg_X_base\])\)',r'call MF_SetAttackRange(\1, \2)',s)

# Fortitude armor is an explicit reversible bonus, not a zero-radius devotion aura.
s=s.replace("    call UnitRemoveAbility(FS_U[i], 'AGf1')", "    call BlzSetUnitArmor(FS_U[i], BlzGetUnitArmor(FS_U[i]) - FS_Armor[i])\n    call UnitRemoveAbility(FS_U[i], 'AGf1')")
s=s.replace("                call UnitAddAbility(u, 'AGf1')\n                call SetUnitAbilityLevel(u, 'AGf1', level)", '                call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + FS_Armor[i])')

# Keep portrait and text anchors in one coordinate system; no scaled offsets.
body=re.search(r'function DPS_Text takes .*?\nendfunction',s,re.S).group()
body=body.replace('call BlzFrameSetSize(f, width, 0.018)','call BlzFrameSetSize(f, width, 0.022)').replace('call BlzFrameSetScale(f, 0.85)', 'call BlzFrameSetFont(f, "Fonts\\\\FRIZQT__.TTF", 0.010, 0)\n    call BlzFrameSetEnable(f, false)')
fn('DPS_Text',body)
body=re.search(r'function DPS_Create takes .*?\nendfunction',s,re.S).group()
body=body.replace('    local integer s = 1','    local integer s = 1\n    local integer row = 0')
body=body.replace('0.765, 0.337','0.765, 0.365')
body=body.replace('        set y = 0.059 + I2R(s - 1) * 0.021','        if ModuloInteger(s - 1, 3) != 1 then\n        set y = 0.070 + I2R(row) * 0.029 + I2R(row / 2) * 0.006')
body=body.replace('BlzFrameSetSize(DPS_Icon[s], 0.018, 0.018)','BlzFrameSetSize(DPS_Icon[s], 0.022, 0.022)')
body=body.replace('        set s = s + 1','        set row = row + 1\n        endif\n        set s = s + 1')
body=body.replace('0.014, 0.312, 0.737','0.014, 0.332, 0.737').replace('call BlzFrameSetScale(f, 0.70)', 'call BlzFrameSetFont(f, "Fonts\\\\FRIZQT__.TTF", 0.008, 0)')
fn('DPS_Create',body)
body=re.search(r'function DPS_Refresh takes .*?\nendfunction',s,re.S).group()
body=body.replace('        set i = s * 10','        if ModuloInteger(s - 1, 3) != 1 then\n        set i = s * 10')
body=body.replace('        set s = s + 1','        endif\n        set s = s + 1')
body=body.replace('if udg_coloured_playername[s] != null and udg_coloured_playername[s] != "" then\n            set name = udg_coloured_playername[s]', 'if udg_orig_player_name[s] != null and udg_orig_player_name[s] != "" then\n            set name = udg_orig_player_name[s]')
fn('DPS_Refresh',body)

# Export the generated icon artwork to the existing Warcraft texture paths.
from PIL import Image
for name,asset in [('Fortitude','Fortitude-green'),('Slam','Slam-blue')]:
    target=O/'ReplaceableTextures/CommandButtons'/('BTNRxGragas'+name+'.blp')
    target.parent.mkdir(parents=True,exist_ok=True)
    Image.open(R/'assets'/(asset+'.png')).convert('RGB').resize((64,64),Image.Resampling.LANCZOS).quantize(colors=256).save(target)

# Random reward boots: independent +60 base speed plus a distinct self-only buff.
# Native item-speed abilities select only the highest bonus (Mira supplies 80).
# Applying to base speed preserves the engine's other item/aura/slow modifiers.
abilities=objdata.load(str(B/'war3map.w3a'))
buffs=objdata.load(str(B/'war3map.w3h'))
items=objdata.load(str(B/'war3map.w3t'))
def newobj(data,old,new,fields):
    assert not any(e['newId']==new for tab in data['tables'] for e in tab),new
    entry={'oldId':old,'newId':new,'flags':1,'extra':0,'mods':[]}
    for key,typ,value,level,ptr in fields:
        mod={'id':key,'type':typ,'value':value,'end':'00000000'}
        if data['levelled']:mod.update(level=level,ptr=ptr)
        entry['mods'].append(mod)
    data['tables'][1].append(entry)
newobj(abilities,'AOae','AMFb',[
 ('anam',3,'Boots of Speed - Independent Bonus',0,0),('aher',0,0,0,0),('aite',0,1,0,0),('alev',0,1,0,0),
 ('aart',3,'',0,0),('areq',3,'',0,0),('abpy',0,-11,0,0),
 ('atar',3,'self,ground,air,vuln,invu',1,0),('aare',2,128.0,1,0),('abuf',3,'BMFb',1,0),
 ('Oae1',2,0.0,1,1),('Oae2',2,0.0,1,2),('adur',2,0.1,1,0),('ahdu',2,0.1,1,0)])
newobj(buffs,'BOae','BMFb',[
 ('fnam',3,'Boots of Speed',0,0),('ftip',3,'Boots of Speed',0,0),
 ('fube',3,'Movement speed increased by 60. Stacks with amulet speed bonuses.',0,0),
 ('fart',3,'ReplaceableTextures\\CommandButtons\\BTNBootsOfSpeed.blp',0,0),('ftat',3,'',0,0)])
boot=next((e for e in items['tables'][0] if e['oldId']=='bspd'),None)
if boot is None:
    boot={'oldId':'bspd','newId':'\0'*4,'flags':1,'extra':0,'mods':[]};items['tables'][0].append(boot)
setmod(boot,'iabi','AMFb',3)
setmod(boot,'igol',125,0) # map PawnItemRate=0.6: 125 * 0.6 = 75 gold
setmod(boot,'utub','Increases movement speed by 60. Stacks with amulet speed bonuses. Multiple boots do not stack. Sells for 75 gold.',3)
for file,data in [('war3map.w3a',abilities),('war3map.w3h',buffs),('war3map.w3t',items)]:
    (O/file).write_bytes(objdata.dump(data))
s=s.replace('\nendglobals','\ngroup MF_BootWearers=null\nhashtable MF_BootState=null\nendglobals',1)
insert_before('MF_Init','''function MF_BootBaseSpeed takes unit u returns real
    local integer i=1
    loop
        exitwhen i > udg_total_hero_count
        if udg_hero_type[i] == GetUnitTypeId(u) and udg_hero_move_base[i] > 0.0 then
            return udg_hero_move_base[i]
        endif
        set i=i + 1
    endloop
    return GetUnitDefaultMoveSpeed(u)
endfunction

function MF_BootUpdate takes nothing returns nothing
    local unit u=GetEnumUnit()
    local integer key=GetHandleId(u)
    local boolean hasBoots=UnitHasItemOfTypeBJ(u, 'bspd')
    if GetUnitTypeId(u) == 0 then
        call GroupRemoveUnit(MF_BootWearers, u)
        call FlushChildHashtable(MF_BootState, key)
    elseif hasBoots != LoadBoolean(MF_BootState, key, 0) then
        if hasBoots then
            call SetUnitMoveSpeed(u, MF_BootBaseSpeed(u) + 60.0)
        else
            call SetUnitMoveSpeed(u, MF_BootBaseSpeed(u))
            call UnitRemoveAbility(u, 'BMFb')
            call GroupRemoveUnit(MF_BootWearers, u)
        endif
        call SaveBoolean(MF_BootState, key, 0, hasBoots)
    endif
    set u=null
endfunction

function MF_BootTick takes nothing returns nothing
    call ForGroup(MF_BootWearers, function MF_BootUpdate)
endfunction

function MF_BootPickup takes nothing returns nothing
    if GetItemTypeId(GetManipulatedItem()) == 'bspd' then
        call GroupAddUnit(MF_BootWearers, GetTriggerUnit())
    endif
endfunction

function MF_BootInit takes nothing returns nothing
    local trigger t=CreateTrigger()
    set MF_BootWearers=CreateGroup()
    set MF_BootState=InitHashtable()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_PICKUP_ITEM)
    call TriggerAddAction(t, function MF_BootPickup)
    call TimerStart(CreateTimer(), 0.10, true, function MF_BootTick)
    set t=null
endfunction''')
s=s.replace('function MF_Init takes nothing returns nothing\n    local integer i=0','function MF_Init takes nothing returns nothing\n    local integer i=0\n    call MF_BootInit()')
insert_before('MF_SetAttackRange','''function MF_BootBonus takes unit u returns real
    if UnitHasItemOfTypeBJ(u, 'bspd') then
        return 60.0
    endif
    return 0.0
endfunction''')
# Hero purchase/re-pick speed initialization must preserve equipped boots.
s=re.sub(r'call SetUnitMoveSpeed\((u|udg_temp_unit), (udg_hero_move_base\[[^\]]+\])\)',r'call SetUnitMoveSpeed(\1, \2 + MF_BootBonus(\1))',s)

# Charge is the existing Militia A0D9 Berserk variant. Remove its inherited
# unavailable Robk requirement so all three units can actually use it.
charge=next(e for tab in abilities['tables'] for e in tab if e['newId']=='A0D9')
for field,value in [('anam','Charge'),('areq',''),('atp1','Charge'),('aub1','Increases movement speed by 50% and attack speed by 10% for 5 seconds. No additional damage taken. Cooldown: 30 seconds.')]:
    for m in charge['mods']:
        if m['id']==field:m['value']=value
    if not any(m['id']==field for m in charge['mods']):
        charge['mods'].append({'id':field,'type':3,'level':1 if field in ['atp1','aub1'] else 0,'ptr':0,'value':value,'end':'00000000'})
(O/'war3map.w3a').write_bytes(objdata.dump(abilities))

# HUD controls must not inherit visibility from a named console decoration.
# Create them after initialization, and make Stats independent of the multiboard.
s=s.replace('local framehandle gameUI= BlzGetFrameByName("ConsoleUIBackdrop", 0)', 'local framehandle gameUI= BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)')
s=s.replace('BlzCreateFrame("ScriptDialogButton", BlzGetFrameByName("ConsoleUIBackdrop", 0), 0, 0)', 'BlzCreateFrame("ScriptDialogButton", ui, 0, 0)')
s=s.replace('    call zoom__CreateSlider()\nendfunction', '    call TimerStart(CreateTimer(), 0.50, false, function zoom__CreateSlider)\nendfunction')
s=s.replace('        if udg_multiboard_kills == null or not IsMultiboardDisplayed(udg_multiboard_kills) then\n            return\n        endif\n', '')
s=s.replace('    call BlzFrameSetText(DPS_Button, "Stats")', '    call BlzFrameSetVisible(DPS_Button, true)\n    call BlzFrameSetText(DPS_Button, "Stats")')
s=s.replace('    call BlzFrameSetLevel(zoom__lockButton, 10)', '    call BlzFrameSetLevel(zoom__lockButton, 21)\n    call BlzFrameSetVisible(zoom__lockButton, true)')
s=s.replace('    call BlzFrameSetScale(zoom__sliderLabel, 0.55)', '    call BlzFrameSetFont(zoom__sliderLabel, "Fonts\\\\FRIZQT__.TTF", 0.009, 0)\n    call BlzFrameSetSize(zoom__sliderLabel, 0.035, 0.012)')
# Start Stats before the remaining hero-system initialization can interrupt its setup.
s=s.replace('    call DPS_Init()\n','')
s=s.replace('    call MF_BootInit()','    call MF_BootInit()\n    call DPS_Init()')

# Solo v1.8 active intervals, with Mini roster overrides; keep one unit per wave.
mini_intervals={0:8,3:6,31:6,9:6,39:6,17:4.5,44:4.5,23:4.5,27:4.5,
                13:6.5,36:6.5,21:7,26:7,22:7,28:7,16:5,50:5,
                18:5,48:5,20:5,47:5}
for idx,seconds in mini_intervals.items():
    s,n=re.subn(rf'(set ffgs_spawn_interval\[{idx}\]=)[0-9.]+',
                lambda m:m[1]+f'{seconds:.2f}',s)
    assert n==1,(idx,n)

# Compact Stats with consistent column bounds and an inset footer.
body=re.search(r'function DPS_Create takes .*?\nendfunction',s,re.S).group()
body=body.replace('0.765, 0.365','0.650, 0.305').replace('0.0175, 0.540','0.075, 0.510')
body=body.replace('0.070 + I2R(row) * 0.029 + I2R(row / 2) * 0.006','0.072 + I2R(row) * 0.022 + I2R(row / 2) * 0.003')
body=body.replace('0.022, 0.022','0.018, 0.018').replace('0.014, -y','0.026, -y')
columns={0.040:(0.050,0.150),0.210:(0.205,0.028),0.250:(0.236,0.028),
         0.290:(0.267,0.028),0.330:(0.298,0.032),0.370:(0.333,0.032),
         0.415:(0.370,0.055),0.480:(0.430,0.060),0.565:(0.495,0.060),0.675:(0.565,0.055)}
def compact_cell(m):
    x=float(m[2]);y=m[3];width=float(m[4])
    if x in columns:x,width=columns[x]
    if y=='0.035':y='0.046'
    return m[1]+f'{x:.3f}, {y}, {width:.3f},'
body=re.sub(r'(DPS_Text\("[^"]+", )([0-9.]+), (y|[0-9.]+), ([0-9.]+),',compact_cell,body)
body=body.replace('0.014, 0.010, 0.720','0.026, 0.022, 0.598')
body=body.replace('0.014, 0.332, 0.737','0.026, 0.267, 0.598')
# Remove the panel title and footer; the column headings remain.
body=re.sub(r'    set f = DPS_Text\("DPS_Title"[^\n]*\n', '', body)
body=re.sub(r'    set f = DPS_Text\("DPS_Legend"[^\n]*\n    call BlzFrameSetFont\(f, [^\n]*\n', '', body)
close = """    set f = BlzCreateFrame("ScriptDialogButton", DPS_Panel, 0, 0)
    call BlzFrameSetSize(f, 0.024, 0.020)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPRIGHT, DPS_Panel, FRAMEPOINT_TOPRIGHT, -0.014, -0.014)
    call BlzFrameSetLevel(f, 21)
    call BlzFrameSetText(f, "X")
    call BlzTriggerRegisterFrameEvent(click, f, FRAMEEVENT_CONTROL_CLICK)
"""
body=body.replace('    call BlzFrameSetVisible(DPS_Panel, false)', close+'    call BlzFrameSetVisible(DPS_Panel, false)')
assert 'DPS_Title' not in body and 'DPS_Legend' not in body and 'FRAMEPOINT_TOPRIGHT, DPS_Panel, FRAMEPOINT_TOPRIGHT' in body
fn('DPS_Create',body)
body=re.search(r'function DPS_Text takes .*?\nendfunction',s,re.S).group()
fn('DPS_Text',body.replace('width, 0.022','width, 0.018').replace('0.010, 0)','0.009, 0)'))

# Revised timeline. T3 remains unavailable under the Mini Foots tier cap.
for key,old,new in [('premass_seconds',90,60),('tech1_default_seconds',240,210),
                    ('tech1_alternate_seconds',290,260),('tech2_seconds',540,420),
                    ('tech3_seconds',720,480)]:
    needle=f'set ffgs_{key}={old:.2f}'
    assert needle in s,key
    s=s.replace(needle,f'set ffgs_{key}={new:.2f}')
s=s.replace('Pooling:|r 10 seconds before T1','Pooling:|r Available at 20:00')
s=s.replace('return not FFR4NoPool and not udg_mode_promode and udg_autopoool_allowed',
            'return udg_gametime_s >= 1200 and not FFR4NoPool and not udg_mode_promode and udg_autopoool_allowed')
s=s.replace('function MF_EnablePooling takes nothing returns nothing\n',
            'function MF_EnablePooling takes nothing returns nothing\n    if udg_gametime_s < 1200 then\n        return\n    endif\n    call TimerDialogDisplayBJ(false, udg_timer_window_trading)\n')
s=s.replace('call TimerStart(udg_timer_trading, RMaxBJ(0.0, TimerGetRemaining(udg_timer_tech_delay_t1) - 10.0), false, function MF_EnablePooling)',
'''call FFR4_LockPooling()
    set FFR4NoPool=true
    call TimerStart(udg_timer_trading, RMaxBJ(0.0, 1200.0 - I2R(udg_gametime_s)), false, null)
    if udg_timer_window_trading != null then
        call DestroyTimerDialog(udg_timer_window_trading)
    endif
    call CreateTimerDialogBJ(udg_timer_trading, "Pooling available")
    set udg_timer_window_trading=GetLastCreatedTimerDialogBJ()
    call TimerDialogDisplayBJ(true, udg_timer_window_trading)''')
s=s.replace('set udg_gametime_s=( udg_gametime_s + 1 )',
'''set udg_gametime_s=( udg_gametime_s + 1 )
    if udg_gametime_s == 1200 then
        call ExecuteFunc("MF_EnablePooling")
    endif''')
