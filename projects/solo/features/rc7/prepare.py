"""Stage Solo RC7 from the exact played Solo RC6 and the 799X RC37 casino."""
import argparse
import hashlib
import json
import re
import runpy
import shutil
import sys
from pathlib import Path

FEATURE = Path(__file__).resolve().parent
ROOT = FEATURE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from map_archive import Archive
from restore_rc6_item_text import parse, dump

SOLO_SHA = "2be267d50e6311f0bf68310f48ab63fa1ace5ae3a669d1c84c96377adc61e7e8"
DONOR_SHA = "5d2ddc725afacd699db3f24593f675ed5faa1bb5f621d872d422619e4701388f"
TITLE = "Solo Foots 1.8-RC7"
FUNCTION = re.compile(r"(?ms)^[ \t]*function (\w+) takes [^\n]*\n.*?^[ \t]*endfunction")


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one occurrence of {old[:100]!r}")
    return text.replace(old, new)


def functions(script):
    return {m[1]: m[0] for m in FUNCTION.finditer(script)}


def identifiers(code):
    code = re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*', "", code)
    return set(re.findall(r"\b\w+\b", code))


def declarations(script):
    header = script.split("\nendglobals", 1)[0]
    pattern = r"(?m)^[ \t]*(?:constant[ \t]+)?\w+[ \t]+(?:array[ \t]+)?(\w+)[ \t]*(?:=[^\n]*|//[^\n]*)?$"
    return {m[1]: m[0] for m in re.finditer(pattern, header)}


def adapt_draft(solo, donor):
    fn = solo["DraftUpdate"]
    start = fn.index("                // Neutral shops")
    fn = fn[:start] + """                set DraftX[team] = FFBaseFrontX(pn,320.,0.)
                set DraftY[team] = FFBaseFrontY(pn,320.,0.)
""" + fn[start:]
    fn = once(fn, 'call BlzSetUnitName(DraftShop[team], "Team " + I2S(team) + " Hero Tavern")',
              'call SetUnitScale(DraftShop[team],0.70,0.70,0.70)\n'
              '                    call BlzSetUnitRealField(DraftShop[team],UNIT_RF_SELECTION_SCALE,0.9*BlzGetUnitRealField(DraftShop[team],UNIT_RF_SELECTION_SCALE))\n'
              '                    call BlzSetUnitName(DraftShop[team],GetPlayerName(p) + " - Hero Tavern")')
    solo["DraftUpdate"] = fn
    fn = solo["DraftStart"]
    i = fn.index("        set DraftX[team]")
    fn = fn[:i] + fn[fn.index("        if udg_selected_mode", i):]
    selection = donor["DraftSelect"]
    i = selection.index("    if pn > 12")
    selection = selection[:i] + selection[selection.index("    if pn >= 1", i):]
    selection = selection.replace("DraftShop[pn]", "DraftShop[udg_teamnumber[pn]]")
    fn = once(fn, "    local trigger sales = CreateTrigger()", """    local trigger sales = CreateTrigger()
    local trigger selection = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(selection,EVENT_PLAYER_UNIT_SELECTED)
    call TriggerAddAction(selection,function DraftSelect)
    set selection = null""")
    solo["DraftStart"] = selection + "\n\n" + fn
    # In Solo each team has one seat. Preserve its categories, pool and random-pick rules.
    fn = solo["DraftRefreshPub"].split("    // Random Hero")[0]
    layout = donor["DraftRefreshPub"].split("    // Page one:", 1)[1]
    layout = layout.replace("[pn]", "[team]").replace("[pn*12", "[team*12")
    layout = layout.replace(" and T66_RandomLeft[team] > 0", "")
    solo["DraftRefreshPub"] = fn + "    // Page one:" + layout
    solo["DraftRefresh"] = solo["DraftRefresh"].replace("team*10+i", "team*12+i").replace("set capacity = 10", "set capacity = 11")
    solo["DraftPubSD"] = once(solo["DraftPubSD"], "udg_mode_pub and ", "")


def adapt_profile(solo, donor):
    schema = solo["PF_Schema"].replace("set PF_metrics = 60", "set PF_metrics = 81")
    labels = re.findall(r"(?m)^    set PF_(?:key|label)\[(?:6\d|7\d|80)\].*$", donor["PF_Schema"])
    assert len(labels) == 42
    solo["PF_Schema"] = once(schema, "\nendfunction", "\n" + "\n".join(labels) + "\nendfunction")
    tail = donor["PF_Live"].split("    elseif k == 60 then", 1)[1]
    solo["PF_Live"] = once(solo["PF_Live"], "    endif\n    return 0\nendfunction",
                           "    elseif k == 60 then" + tail)
    profile = solo["PF_ProfileView"].replace("Solo casino preview", "Casino and credit   /   Wallet")
    empty = "    if count == 0 then"
    solo["PF_ProfileView"] = profile[:profile.index(empty)] + donor["PF_ProfileView"][donor["PF_ProfileView"].index(empty):]
    close = solo["CP_PreviewClose"].replace("CP_PreviewClose", "SoloCloseProfile")
    close = close.replace("    set CP_CAS_view[1] = 0\n", "")
    close = close[:close.index("    if CP_CAS_root")] + close[close.index("    call BlzFrameSetVisible(DPS_Panel"):]
    solo["CP_PreviewClose"] = close
    for name in ("DPS_Refresh", "DPS_Toggle", "SpellKeysClick"):
        solo[name] = solo[name].replace("CP_PreviewClose", "SoloCloseProfile").replace(" or CP_CAS_view[1] != 0", "")
    solo["DPS_Create"] = once(solo["DPS_Create"], "call CP_PreviewInit(f)",
        "call BlzTriggerRegisterFrameEvent(SoloCasinoLaunch,f,FRAMEEVENT_CONTROL_CLICK)")


def attach_match_events(solo):
    start = "    call ExecuteFunc(\"DraftStart\")"
    solo["Trig_Start_game_Actions"] = once(solo["Trig_Start_game_Actions"], start, "    set WalletMatchStarted = true\n" + start)
    anchor = "    set udg_temp_playernumber=playerNumber"
    solo["Trig_player_destroyed_Actions"] = once(solo["Trig_player_destroyed_Actions"], anchor, """    set CAS_baseVictim = GetDyingUnit()
    set CAS_baseKiller = GetKillingUnit()
    call TriggerExecute(CAS_baseEvent)
    set CAS_baseVictim = null
    set CAS_baseKiller = null
""" + anchor)
    solo["PF_SoloSnapshot"] = once(solo["PF_SoloSnapshot"], "    call PF_Freeze()",
                                    '    call ExecuteFunc("SoloCasinoSettle")\n    call PF_Freeze()')
    solo["FF_gr_Poll"] = once(solo["FF_gr_Poll"], "    // 2. side bookkeeping.",
                              '    call ExecuteFunc("WalletPayParticipation")\n    // 2. side bookkeeping.')


def script(solo_source, donor_source):
    solo = functions(solo_source)
    donor = functions(donor_source)
    adapt_draft(solo, donor)
    adapt_profile(solo, donor)
    attach_match_events(solo)
    adapter = (FEATURE / "casino.j").read_text().strip()
    # This checkout uses a separate four-seat profile. Its wallet uses the same
    # ledger format with its own family path, so Solo results stay in Solo.
    donor["WalletLoad"] = once(donor["WalletLoad"], r"FootmenFrenzy\\799X\\", r"FootmenFrenzy\\Solo\\")
    donor["CAS_Tick"] = re.sub(r"                if CatalogCasino != null then\n.*?                endif\n",
                               "", donor["CAS_Tick"], count=1, flags=re.S)
    # Solo settles matches by side, including when only one seat remains.
    donor["MK_Refresh"] = once(donor["MK_Refresh"], "FFEnd_ParticipantCount() >= 2 and FFEnd_BlockCount() == 1", "false")
    shared = {"AR_MatchBounds", "AR_Fighter", "FFBaseAngle", "FFBaseFrontX", "FFBaseFrontY"}
    needed = set()

    def include(name):
        if name in needed or name in solo:
            return
        needed.add(name)
        for dependency in identifiers(donor[name]) & donor.keys():
            include(dependency)

    for name in (identifiers(adapter) & donor.keys()) | shared | {"WalletPayParticipation"}:
        include(name)
    early = "\n\n".join(body for name, body in donor.items() if name in shared)
    late = "\n\n".join(body for name, body in donor.items() if name in needed - shared)
    # Match-wide filters retain the original battlefield, excluding the arena.
    for name in solo:
        solo[name] = solo[name].replace("GetWorldBounds()", "AR_MatchBounds()").replace("GetEntireMapRect()", "AR_MatchBounds()")
    solo["FF_oc_OnTick"] = once(solo["FF_oc_OnTick"], "if FF_oc_mode[i] != 0 then",
        "if FF_oc_mode[i] != 0 and not (AR_state == 2 and (i+1 == AR_seat[0] or i+1 == AR_seat[1])) then")
    for name in ("Trig_autorevive_Conditions", "Trig_change_Revive_time_based_on_level_Conditions",
                 "Trig_Multiboard_Update_Conditions", "Trig_set_hero_bounty_Conditions",
                 "Trig_Unit_Experience_System_Actions", "Trig_Foot_Exp_system_Actions",
                 "FF_oc_OnDeath", "FF_kl_OnDeath", "FF_st_OnDeath", "DPS_OnDeath", "GSI_Blocked"):
        fn = solo[name]
        head = re.match(r"[^\n]+\n(?:[ \t]+local [^\n]+\n)*", fn).end()
        unit = "u" if name == "GSI_Blocked" else "GetTriggerUnit()"
        result = " false" if " returns boolean" in fn.splitlines()[0] else ""
        solo[name] = fn[:head] + f"    if AR_Fighter({unit}) then\n        return{result}\n    endif\n" + fn[head:]
    solo["main"] = once(solo["main"], "    call DPS_Init()", "    call SoloCasinoInit()\n    call DPS_Init()")
    solo["config"] = re.sub(r'SetMapName\("[^"]+"\)', 'SetMapName("' + TITLE + '")', solo["config"], count=1)
    solo["main"] = late + "\n\n" + adapter + "\n\n" + solo["main"]
    compiled = FUNCTION.sub(lambda m: "" if m[1].startswith("CP_") and m[1] != "CP_PreviewClose" else solo[m[1]], solo_source)
    compiled = re.sub(r"(?m)^[ \t]*\w+[ \t]+(?:array[ \t]+)?CP_\w+[^\n]*\n", "", compiled)
    existing = declarations(compiled)
    used = identifiers(late + early + adapter + solo["PF_Live"])
    new = [line for name, line in declarations(donor_source).items() if name in used and name not in existing]
    new.append("    trigger SoloCasinoLaunch = CreateTrigger()")
    compiled = once(compiled, "\nendglobals\n", "\n" + "\n".join(new) + "\nendglobals\n\n" + early + "\n")
    return compiled


def stage_project(parent, expected, work):
    if hashlib.sha256(parent.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Unexpected map contents: {parent.name}")
    proj = work / "projects/solo"
    src = proj / "src"
    src.mkdir(parents=True, exist_ok=True)
    release = proj / "release" / parent.name
    release.parent.mkdir(exist_ok=True)
    if not release.exists():
        shutil.copyfile(parent, release)
    for name in ("Build-Map.ps1", "tools.local.json", "tools/build_map.py", "tools/map_archive.py", "tools/Install-Wc3Map.ps1"):
        (work / name).parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / name, work / name)
    meta = dict(map_type="Solo Foots", branch="Solo-Foots-4p", release=parent.name, sha256=expected)
    (proj / "project.json").write_text(json.dumps(meta, indent=2))
    return src


def stage(parent, reference, work):
    if hashlib.sha256(reference.read_bytes()).hexdigest() != DONOR_SHA:
        raise ValueError(f"Unexpected map contents: {reference.name}")
    src = stage_project(parent, SOLO_SHA, work)
    dll = json.loads((ROOT / "tools.local.json").read_text())["stormlib"]
    arena = runpy.run_path(str(ROOT / "projects/799x/features/arena/prepare.py"))
    with Archive(dll, parent) as base, Archive(dll, reference) as donor:
        def jass(archive):
            return archive.read("war3map.j").decode("utf8").replace("\r\n", "\n")
        output = script(jass(base), jass(donor))
        (src / "war3map.j").write_bytes(output.replace("\n", "\r\n").encode("utf8"))
        misc = base.read("war3mapMisc.txt")
        rewards = re.search(rb"(?m)^GrantNormalXP=([0-9,]+)", misc)[1].split(b",")
        assert len(rewards) == 80 and rewards[32:34] == [b"23", b"36"]
        (src / "war3mapMisc.txt").write_bytes(once(misc, b"MaxHeroLevel=18", b"MaxUnitLevel=80\r\nMaxHeroLevel=18"))
        for member, transform in [("war3map.w3e", "terrain"), ("war3map.wpm", "pathing")]:
            (src / member).write_bytes(arena[transform](base.read(member)))
        shadow = base.read("war3map.shd")
        assert len(shadow) == 65536
        (src / "war3map.shd").write_bytes(shadow + bytes(256*128))
        info = base.read("war3map.w3i")
        old_title = info[28:info.index(0, 28)]
        changed = arena["info"](once(info, old_title, arena["PARENT_TITLE"].encode()))
        (src / "war3map.w3i").write_bytes(once(changed, arena["TITLE"].encode(), TITLE.encode()))
        (src / "war3map.wts").write_bytes(once(base.read("war3map.wts"), old_title, TITLE.encode()))
        units = parse(base.read("war3map.w3u"))
        for table in units[1]:
            for ids, mods in table:
                if ids[4:8] == b"hTNP":
                    for idx, (key, kind, value, tag) in enumerate(mods):
                        if key == b"uico":
                            mods[idx] = (key, kind, b"ReplaceableTextures\\CommandButtons\\BTNFootsPageTurn.blp\0", tag)
        (src / "war3map.w3u").write_bytes(dump(units))
        art = [r"CasinoUI\Bold.ttf", r"CasinoUI\panel.blp", r"ReplaceableTextures\CommandButtons\BTNFootsPageTurn.blp",
               r"ReplaceableTextures\CommandButtonsDisabled\DISBTNFootsPageTurn.blp"]
        art += ["PokerUI\\" + name + ".blp" for name in ["table", "empty", "back", "dealer"] +
                [f"chips{i}" for i in range(1,5)] + [f"card{i}" for i in range(52)]]
        for name in art:
            target = src / name
            target.parent.mkdir(exist_ok=True, parents=True)
            target.write_bytes(donor.read(name))
    return src


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("solo", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("stage", type=Path)
    args = parser.parse_args()
    print(stage(args.solo, args.reference, args.stage))
