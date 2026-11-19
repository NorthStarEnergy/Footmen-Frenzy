"""Stage the RC2 playtest changes against the complete, fingerprinted RC1."""
import hashlib
import json
import math
import re
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))
from map_archive import Archive
from restore_rc6_item_text import parse, dump

RC1 = "Reforged Footmen Frenzy v7.9.9X-rc1"
DIGEST = "7173200a0369e1ed9d89cd703e3c98a70b38fa913f1536c538fcbf835b651381"
work = ROOT / "build/799x-rc2"
project = work / "projects/799x"
src = project / "src"
src.mkdir(parents=True, exist_ok=True)
baseline = project / "release" / (RC1 + ".w3x")
if not baseline.exists():
    baseline.parent.mkdir(exist_ok=True)
    shutil.copy2(Path.home() / "Documents/Warcraft III/Maps/Tests/799X" / baseline.name, baseline)
assert hashlib.sha256(baseline.read_bytes()).hexdigest() == DIGEST
(project / "project.json").write_text(json.dumps(dict(map_type="799X", release=baseline.name, sha256=DIGEST)))
for name in ["Build-Map.ps1", "tools.local.json", "tools/build_map.py", "tools/map_archive.py", "tools/Install-Wc3Map.ps1"]:
    target = work / name
    target.parent.mkdir(exist_ok=True)
    shutil.copy2(ROOT / name, target)
with Archive(json.loads((work / "tools.local.json").read_text())["stormlib"], baseline) as archive:
    original = archive.read("war3map.j")
    title = archive.read("war3map.wts")
    assert title.count(RC1.encode()) == 1
    (src / "war3map.wts").write_bytes(title.replace(RC1.encode(), RC1[:-1].encode() + b'2'))
    assert b'PawnItemRate=0.6' in archive.read("war3mapMisc.txt")
    items = parse(archive.read("war3map.w3t"))
    boots, = [mods for table in items[1] for ids, mods in table if ids[:8] == b'bspdIRb0']
    cost, = [m for m in boots if m[0] == b'igol']
    tooltip, = [m for m in boots if m[0] == b'utub']
    assert b'75 gold' in tooltip[2]
    cost[2] = struct.pack('<i', 42)  # 42 * 0.6 pays 25 whole gold.
    tooltip[2] = tooltip[2].replace(b'75 gold', b'25 gold')
    (src / "war3map.w3t").write_bytes(dump(items))
    placements = archive.read("war3mapUnits.doo")

# RC1 has 131-byte ordinary, empty shop placements in its version-13 table.
# Clone the last team's three shops with fresh creation numbers.
count = struct.unpack_from('<I', placements, 12)[0]
records = []
for match in re.finditer(b'n003', placements):
    start = match.start()
    record = bytearray(placements[start:start + 131])
    if record[36:40] != b'n003' or struct.unpack_from('<ff',record,8) != (2752., -3520.):
        continue
    owner = struct.unpack_from('<I', record, 45)[0]
    assert owner in (6, 7, 8)
    struct.pack_into('<I', record, 45, owner + 3)
    struct.pack_into('<ff', record, 8, -3264., -3008.)
    struct.pack_into('<f', record, 20, math.radians(46.229))
    struct.pack_into('<I', record, 115, 10000 + owner)
    records.append(record)
assert len(records) == 3
(src / "war3mapUnits.doo").write_bytes(placements[:12] + struct.pack('<I',count+3) + placements[16:] + b''.join(records))

script = original.decode().replace('\r\n', '\n')

def replace(old, new, count=1):
    global script
    assert script.count(old) == count, (old, script.count(old))
    script = script.replace(old, new)

def functions(pattern, change):
    global script
    script, n = re.subn(r'^function (' + pattern + r') takes [^\n]*\n.*?^endfunction\n', change,
                        script, flags=re.M | re.S)
    assert n, pattern

def body(name, lines):
    functions(name, lambda m: m[0].split('\n', 1)[0] + '\n' + lines.strip('\n') + '\nendfunction\n')

def drop_lines(pattern):
    global script
    script, n = re.subn('(?m)^' + pattern + r'[^\n]*\n', '', script)
    assert n, pattern

# Items may be bought, dropped, traded, used in recipes and pawned normally.
functions(r'PBI_\w+', '')
drop_lines(r' +call (?:PBI_Init\(|TriggerAddCondition\([^\n]+function PBI_Allowed\b)')
for pn in (9, 10, 11):
    functions('CreateBuildingsForPlayer' + str(pn), lambda m: m[0].replace('endfunction',
        "    set u=BlzCreateUnitWithSkin(p, 'n003', -3264.0, -3008.0, 46.229, 'n003')\n"
        "    call SetUnitColor(u, ConvertPlayerColor(12))\nendfunction"))

# The economy still uses its authored kill rewards and the fixed post-6 XP rate.
# Remove relative-level modifiers, delayed milestone grants and early-level supplements.
for prefix in ('Trig_Footy_Bounty_Increase_Delay','Trig_Unit_Experience_System','Trig_Foot_Exp_system','Trig_Set_Exp_Bonus_Rate_'):
    functions(prefix + r'\w*', '')
    functions('Init' + prefix + r'\w*', '')
    drop_lines(' +call Init' + prefix)
functions(r'P67_Rate|P78_Rate|P79_(?:LevelXP|FractionalLevel|NextTarget|TeamReached|TeamPresent|FieldAhead|Refresh|Extra|Pay)|P80_(?:Curve|TeamLevel|Factor|Gold)|P67_(?:MassFinished|ColoSpawn|OnLevel)', '')
drop_lines(r' +call P67_(?:MassFinished|ColoSpawn)\(')
drop_lines(r'(?:real|integer|unit|boolean|timer|constant (?:integer|real)) (?:array )?(?:P78_\w+|P79_(?!Table)\w+|P67_(?:Reached4|Reached6|FirstColo|MassEnded|CATCHUP_RATE|APPROACH6_RATE)|P80_(?:FREE_LEAD|REDUCTION_PER_LEVEL|MAX_REDUCTION|MIN_LEVEL|GoldRemainder))\b')
replace('return P78_Rate(GetHeroLevel(u), GetHeroXP(u), P78_Reached10, P67_Rate(GetHeroLevel(u), P67_Reached4, P67_Reached6, P67_MassEnded, P67_FirstColo))',
        'if GetHeroLevel(u) >= 7 then\n        return P67_POST7_RATE\n    endif\n    return 100.00')
replace(' * P80_Factor(hero, victim)', '')
replace(' * P80_Factor(u, victim)', '')
replace('        if IsUnitType(victim, UNIT_TYPE_HERO) then\n            set bounty = P80_Gold(owner, victim, bounty)\n        endif\n', '')
start = script.index('            // BONUS GOLD BASED ON WINNING FACTOR:')
end = script.index('            call AdjustPlayerStateBJ(1,', start)
script = script[:start] + script[end:]
body('P67_Refresh', '    call P80_Sync()')
for comment in [
        '// Percent, not a multiplier. Kept pure for boundary tests and tuning.',
        '// Percentage points added to the existing 70% rate. No XP is granted here.',
        "// Stock cumulative XP thresholds, verified against this map's gameplay constants.",
        '// A strict majority prevents one fed carry from qualifying an entire team.',
        '// Multiplicative reward factor. Fractional levels make the transition smooth.',
        '// Run after normal death XP; only the extra grant is clamped to the milestone.']:
    replace(comment + '\n', '')
replace('    local integer nearby = 0\n', '')
replace('''                call SaveBoolean(P80_Rewards, id, pn + 24, true)
                set nearby = nearby + 1
            endif
            call SaveUnitHandle(P80_Rewards, id, pn, hero)
            call SaveReal(P80_Rewards, id, pn + 12, baseXP * P67_HeroRate(hero) * 0.01)
            set count = count + 1''',
'''                call SaveUnitHandle(P80_Rewards, id, pn, hero)
                call SaveReal(P80_Rewards, id, pn + 12, baseXP * P67_HeroRate(hero) * 0.01)
                set count = count + 1
            endif''')
replace('    if nearby > 0 then\n        set count = nearby\n    endif\n', '')
replace('hero != null and count > 0 and LoadBoolean(P80_Rewards, id, pn + 24)', 'hero != null and count > 0')
body('P79_OnDeath', '''    local unit victim = GetTriggerUnit()
    local integer key = GetHandleId(victim)
    if LoadUnitHandle(P79_Table, key, 1) == victim then
        call FlushChildHashtable(P79_Table, key)
    endif
    set victim = null''')

# The ball uses a world-space particle model, independent of unit invisibility.
# Move the presentation below the terrain as well as setting alpha for renderers
# that do not apply effect alpha to every particle. Gameplay positions stay synced.
replace('    call BlzSetSpecialEffectPosition(fx, x, y, GetLocationZ(OM_VisualGround) + GetUnitFlyHeight(OM_Ball[i]) + 20.0 * gesture)',
'''    if IsUnitInvisible(OM_Hero[i], GetLocalPlayer()) or not IsUnitVisible(OM_Hero[i], GetLocalPlayer()) or (OM_State[i] == 0 and not IsUnitVisible(OM_Carrier[i], GetLocalPlayer())) then
        call BlzSetSpecialEffectAlpha(fx, 0)
        call BlzSetSpecialEffectPosition(fx, x, y, -10000.)
    else
        call BlzSetSpecialEffectAlpha(fx, 255)
        call BlzSetSpecialEffectPosition(fx, x, y, GetLocationZ(OM_VisualGround) + GetUnitFlyHeight(OM_Ball[i]) + 20.0 * gesture)
    endif''')
functions('OM_Home', lambda m: m[0].replace('OM_Ball[i], "origin"', 'OM_Hero[i], "overhead"'))

# Profile opens the match table. Hotkeys is an interior page with a Stats return.
for section in ['GLOBALS', 'DATA', 'RUNTIME']:
    script, n = re.subn(r'(?ms)^[ \t]*// BEGIN ITEMS CATALOG ' + section +
                        '.*?// END ITEMS CATALOG ' + section + r'\n', '', script)
    assert n == 1
functions('FFUI_Click|FFUI_Create', '')
drop_lines(r' +(?:framehandle FFUI_(?:Toggle|Items\w*)|boolean FFUI_(?:Hidden|ItemsOpen)|call FFUI_Create\()')
replace(' and (not FFUI_ItemsOpen or FFUI_Hidden)', '')
start = script.index('    set spellKeysToggle = BlzCreateFrame')
end = script.index('    set spellKeysPanel =', start)
script = script[:start] + script[end:]
drop_lines(r' +call BlzTriggerRegisterFrameEvent\(click, spellKeysToggle,')
start = script.index('            set FFUI_ItemsOpen = false')
end = script.index('            set spellKeysEditing = -1', start)
script = script[:start] + '''            set spellKeysOpen = clicked == spellKeysToggle
            call BlzFrameSetVisible(DPS_Panel, not spellKeysOpen)
''' + script[end:]
replace('BlzFrameSetText(spellKeysClose, "Close")','BlzFrameSetText(spellKeysClose, "Stats")')
replace('    call BlzFrameSetVisible(CatalogSkins, CatalogKind == 0)',
        '    call BlzFrameSetVisible(spellKeysToggle, CatalogKind == 0)\n        call BlzFrameSetVisible(CatalogSkins, CatalogKind == 0)')
body('DPS_Toggle', '''    local integer p = GetPlayerId(GetTriggerPlayer())
    local framehandle clicked = BlzGetTriggerFrame()
    if GetLocalPlayer() == GetTriggerPlayer() then
        set DPS_Open[p] = not DPS_Open[p]
        set spellKeysOpen = false
        set spellKeysEditing = -1
        call BlzFrameSetVisible(spellKeysPanel, false)
        if DPS_Open[p] then
            set DPS_Personal = false
            set CatalogKind = 0
            call BlzFrameSetVisible(CatalogPanel, false)
            call BlzFrameSetVisible(DPS_Table, true)
            call BlzFrameSetVisible(DPS_ProfileText, false)
            call BlzFrameSetVisible(DPS_PageButton, true)
            call BlzFrameSetText(DPS_PageButton, "My Stats")
            call BlzFrameSetVisible(spellKeysToggle, true)
            call BlzFrameSetVisible(CatalogSkins, true)
            call BlzFrameSetVisible(CatalogCasino, true)
        endif
        call BlzFrameSetVisible(DPS_Panel, DPS_Open[p])
        call BlzFrameSetEnable(clicked, false)
        call BlzFrameSetEnable(clicked, true)
        call BlzFrameSetFocus(clicked, false)
    endif
    set clicked = null''')
replace('BlzFrameSetSize(DPS_Button, 0.073, 0.028)','BlzFrameSetSize(DPS_Button, 0.057, 0.022)\n    call BlzFrameSetScale(DPS_Button, 0.91)')
replace('FRAMEPOINT_TOP, -0.039, -0.004)', 'FRAMEPOINT_TOP, 0.0, 0.002)')
replace('BlzFrameSetText(DPS_Button, "Stats")','BlzFrameSetText(DPS_Button, "Profile")')
replace('    call CatalogCreate()', '''    call CatalogCreate()
    set pageClick = CreateTrigger()
    set spellKeysToggle = CatalogButton(DPS_Panel, pageClick, "Hotkeys", 0.050, 0.018)
    call BlzFrameSetSize(spellKeysToggle, 0.073, 0.022)
    call TriggerAddAction(pageClick, function SpellKeysClick)
    set pageClick = null''')
replace('BlzFrameSetSize(DPS_PageButton, 0.100, 0.026)', 'BlzFrameSetSize(DPS_PageButton, 0.084, 0.022)')
replace('BlzCreateFrame("EscMenuLabelTextTemplate", zoom__slider, 0, 0)',
        'BlzCreateFrameByType("TEXT", "FFZoomValue", gameUI, "", 0)')
replace('BlzFrameSetTextColor(zoom__sliderLabel, 0xFFFFCC00)',
        'BlzFrameSetTextColor(zoom__sliderLabel, 0xFFFFFFFF)\n    call BlzFrameSetLevel(zoom__sliderLabel, 22)\n    call BlzFrameSetTextAlignment(zoom__sliderLabel, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)')
replace('BlzFrameSetText(zoom__sliderLabel, I2S(cameraDistance))','BlzFrameSetText(zoom__sliderLabel, "|cffffffff" + I2S(cameraDistance) + "|r")')
replace('BlzFrameSetText(zoom__lockLabel, "|cffff3030X|r")','BlzFrameSetText(zoom__lockLabel, "Unlock")')
replace('BlzFrameSetText(zoom__lockLabel, "|cffffffffX|r")','BlzFrameSetText(zoom__lockLabel, "Lock")',2)
replace('BlzFrameSetSize(zoom__lockLabel, 0.010, 0.010)','BlzFrameSetSize(zoom__lockLabel, 0.050, 0.014)\n    call BlzFrameSetTextAlignment(zoom__lockLabel, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)')
replace('BlzFrameSetSize(zoom__lockButton, 0.025, 0.020)','BlzFrameSetSize(zoom__lockButton, 0.035, 0.018)')

# A tavern's command card is shared by everyone selecting that unit. Each
# player gets a separate seller and buyer. Team eligibility and Random uses
# remain synchronized, and only a completed purchase refreshes teammates.
replace('DraftShop[udg_teamnumber[udg_temp_playernumber]]', 'DraftShop[udg_temp_playernumber]', 2)
for name in ('DraftRefreshPub', 'DraftRefresh'):
    functions(name, lambda m: m[0].replace('takes integer team returns nothing\n',
        'takes integer pn returns nothing\n    local integer team = udg_teamnumber[pn]\n')
        .replace('DraftPage[team]', 'DraftPage[pn]').replace('DraftShop[team]', 'DraftShop[pn]')
        .replace('team*12+i', 'pn*12+i').replace('DraftRefreshPub(team)', 'DraftRefreshPub(pn)'))
body('AddAPHeroesToDraft', '''    local integer team = 1
    local integer pn = 1
    if AllowAPHeroes() then
        loop
            exitwhen team > 4
            call DraftAddHero(team, 'HTf1')
            set team = team + 1
        endloop
        loop
            exitwhen pn > 12
            if DraftShop[pn] != null then
                call DraftRefresh(pn)
            endif
            set pn = pn + 1
        endloop
    endif''')
replace('shop != DraftShop[team]', 'shop != DraftShop[pn]')
replace('set DraftPage[team] = DraftPage[team] + 1','set DraftPage[pn] = DraftPage[pn] + 1')
replace('if not DraftSD() and DraftPage[team]*8 >= DraftCount[team] then\n            set DraftPage[team] = 0\n        endif',
'''if not DraftSD() and DraftPage[pn]*8 >= DraftCount[team] then
            set DraftPage[pn] = 0
        endif
        call DraftRefresh(pn)
        set sold = null
        set shop = null
        set p = null
        return''')
replace('        if not DraftEligible(team,id) then', '''        loop
            exitwhen i > DraftCount[team] or DraftPool[team*256+i] == id
            set i = i + 1
        endloop
        if i > DraftCount[team] or DraftTaken[team*256+i] or not DraftEligible(team,id) then''')
start = script.index('                loop\n                    exitwhen i > DraftCount[team]', script.index('function DraftSale takes'))
end = script.index('                endloop',start) + len('                endloop')
script = script[:start] + '                set DraftTaken[team*256+i] = true' + script[end:]
body('DraftUpdate', '''    local integer pn = 1
    local integer team
    local player p
    local unit shop
    local real x
    local real y
    loop
        exitwhen pn > 12
        set p = ConvertedPlayer(pn)
        set team = udg_teamnumber[pn]
        if team >= 1 and team <= 4 and DraftCanPick(pn) then
            if DraftShop[pn] == null then
                set x = DraftX[team] + 180. * (ModuloInteger(pn-1,3) - 1)
                set y = DraftY[team]
                set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'nTDP', x, y, 270.)
                set DraftShop[pn] = shop
                call SetUnitScale(shop, 0.70, 0.70, 0.70)
                call BlzSetUnitName(shop, GetPlayerName(p) + " - Hero Tavern")
                if DraftSD() then
                    call BlzUnitHideAbility(shop, 'Ane2', true)
                endif
                call SetUnitTypeSlots(shop, 12)
                set DraftPage[pn] = 0
                call DraftRefresh(pn)
                set DraftWisp[pn] = CreateUnit(p, 'eTWP', GetUnitX(shop), GetUnitY(shop)-96., 90.)
                call SelectUnitForPlayerSingle(shop, p)
                call PanCameraToTimedForPlayer(p, GetUnitX(shop), GetUnitY(shop), 0.25)
            endif
        elseif DraftShop[pn] != null then
            call RemoveUnit(DraftWisp[pn])
            call RemoveUnit(DraftShop[pn])
            set DraftWisp[pn] = null
            set DraftShop[pn] = null
        endif
        set pn = pn + 1
    endloop
    set p = null
    set shop = null''')
body('DraftAfterSale', '''    local timer deferred = GetExpiredTimer()
    local integer team = LoadInteger(DraftStock, GetHandleId(deferred), 0)
    local integer pn = 1
    call FlushChildHashtable(DraftStock, GetHandleId(deferred))
    call DestroyTimer(deferred)
    call DraftUpdate()
    loop
        exitwhen pn > 12
        if udg_teamnumber[pn] == team and DraftShop[pn] != null then
            call DraftRefresh(pn)
        endif
        set pn = pn + 1
    endloop
    set deferred = null''')
functions('DraftScheduleRefresh', '')
replace('    call ExecuteFunc("DraftScheduleRefresh")','''    set deferred = CreateTimer()
    call SaveInteger(DraftStock, GetHandleId(deferred), 0, team)
    call TimerStart(deferred, 0.0, false, function DraftAfterSale)
    set deferred = null''')
# Place the callbacks in compiler order.
sale = re.search(r'^function DraftSale takes .*?^endfunction\n', script, re.M | re.S)[0]
replace(sale, '')
replace('function DraftStart takes', sale.replace('    local unit shop', '    local timer deferred\n    local unit shop', 1) +
'''
function DraftSelect takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer pn = GetConvertedPlayerId(p)
    if pn > 12 and pn <= 24 then
        set pn = SoloSub_playerForObserver[pn-1]
    endif
    if pn >= 1 and pn <= 12 and GetUnitTypeId(GetTriggerUnit()) == 'nTDP' and DraftShop[pn] != null and GetTriggerUnit() != DraftShop[pn] then
        call SelectUnitForPlayerSingle(DraftShop[pn], p)
    endif
    set p = null
endfunction

function DraftStart takes''')
functions('DraftStart', lambda m: m[0].replace('    local trigger sales = CreateTrigger()', '''    local trigger sales = CreateTrigger()
    local trigger selection = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(selection, EVENT_PLAYER_UNIT_SELECTED)
    call TriggerAddAction(selection, function DraftSelect)
    set selection = null'''))
drop_lines(r' +(?:boolean array DraftPending|set DraftPending\[pn\])')

for token in ('IC_', 'PBI_', 'FFUI_Items', 'FFUI_Toggle', 'FFUI_Hidden', 'P78_', 'P79_Pay',
              'P79_Active', 'P80_Factor', 'DraftPage[team]', 'DraftShop[team]'):
    assert not re.search(r'\b' + re.escape(token), script), token
assert script.count("BlzCreateUnitWithSkin(p, 'n003'") == 12
(src / "war3map.j").write_bytes(script.replace('\n', '\r\n' if b'\r\n' in original else '\n').encode())
print("Prepared RC2 from verified RC1 in", work)
