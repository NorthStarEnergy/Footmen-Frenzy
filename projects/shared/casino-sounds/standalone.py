"""Preserve the standalone release and port its playable casino into FFA + King."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess

from prepare import ROOT, credit_record, globals_patch, once, open_tables, runtime_patch, solo

CASINO = "ec00baae4d734ee84a8206bd85415a80469b81872a5b6d04541ca93ab2cbd8dd"
FFA = "d09080db2d9f57d25b2159891659f1a2b6af8973df141d619e5a48050a77ab1f"
FEATURE = Path(__file__).resolve().parent
FUN = solo["FUNCTION"]
functions = solo["functions"]
identifiers = solo["identifiers"]
declarations = solo["declarations"]


def decoded(data):
    return data.decode().replace("\r\n", "\n")


def endlines(code, original):
    return (code.replace("\n", "\r\n") if b"\r\n" in original else code).encode()


def ffa_script(original, standalone):
    existing = functions(original)
    donor = functions(open_tables["menu_only"](standalone))
    donor["CAS_Tick"] = once(donor["CAS_Tick"], "    call MK_Refresh()", "    call WalletPayParticipation()\n    call MK_Refresh()").replace(
        "            if GetLocalPlayer() == Player(s-1) then\n            endif\n", "")
    donor["MK_Valid"] = """function MK_Valid takes integer m, integer o returns boolean
    return o >= 1 and o <= 12 and FF_gr_participant[o]
endfunction"""
    donor["MK_Label"] = """function MK_Label takes integer m, integer o returns string
    return CAS_Name(o)
endfunction"""
    donor["MK_Title"] = once(donor["MK_Title"], "    elseif MK_FFA() then",
                              '    elseif SKEnabled then\n        return "PLAYER TO BECOME KING"\n    elseif MK_FFA() then')
    donor["WalletAward"] = once(donor["WalletAward"], "(winnerSide > 0 and FF_gr_IsMember(slot,winnerSide))",
                                  "(SKEnabled and winnerSlot > 0 and SKActive(slot) and SKKing[slot] == winnerSlot)")
    donor["WalletAward"] = donor["WalletAward"].replace(" or GetPlayerTeam(Player(slot-1)) == 4", "")
    donor["WalletLoad"] = once(donor["WalletLoad"], r"FootmenFrenzy\\799X\\", r"FootmenFrenzy\\FFA\\")
    # The FFA map already runs SyncTime continuously, including during the draft.
    for name in ("CAS_Tick", "MK_IsOpen"):
        donor[name] = once(donor[name], "TimerGetElapsed(FF_gameTimer)", "TimerGetElapsed(SyncTime)")
    adapter = (FEATURE / "ffa.j").read_text()
    needed = set()

    def include(name):
        if name in existing or name in needed:
            return
        needed.add(name)
        for dep in identifiers(donor[name]) & donor.keys():
            include(dep)

    for dep in identifiers(adapter) & donor.keys():
        include(dep)
    block = "\n\n".join(body for name, body in donor.items() if name in needed) + "\n\n" + adapter
    # Replace the mock preview on maps that have one, or add its menu entry
    # to the currently embedded editor source, which predates the preview.
    if "CP_PreviewClose" in existing:
        close = existing["CP_PreviewClose"].replace("CP_PreviewClose", "FFA_CloseProfile")
        close = close.replace("    set CP_CAS_view[1] = 0\n", "")
        existing["CP_PreviewClose"] = close[:close.index("    if CP_CAS_root")] + close[close.index("    call BlzFrameSetVisible(DPS_Panel"):]
        for name in ("DPS_Toggle", "SpellKeysClick"):
            existing[name] = existing[name].replace(" or CP_CAS_view[1] != 0", "").replace("CP_PreviewClose", "FFA_CloseProfile")
        existing["DPS_Create"] = once(existing["DPS_Create"], "call CP_PreviewInit(f)",
                                     "call BlzTriggerRegisterFrameEvent(FFA_CasinoLaunch,f,FRAMEEVENT_CONTROL_CLICK)")
    else:
        anchor = "    set DPS_Ready = true"
        existing["DPS_Create"] = once(existing["DPS_Create"], anchor, """    set f = BlzCreateFrame("ScriptDialogButton",DPS_Panel,0,0)
    call BlzFrameSetSize(f,0.09,0.026)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPRIGHT,DPS_Panel,FRAMEPOINT_TOPRIGHT,-0.145,-0.012)
    call BlzFrameSetText(f,"Casino")
    call BlzTriggerRegisterFrameEvent(FFA_CasinoLaunch,f,FRAMEEVENT_CONTROL_CLICK)
""" + anchor)
    base_hook = """    set CAS_baseVictim = GetDyingUnit()
    set CAS_baseKiller = GetKillingUnit()
    call TriggerExecute(CAS_baseEvent)
    set CAS_baseVictim = null
    set CAS_baseKiller = null
"""
    for name, anchor in [("Trig_player_destroyed_Actions", "    set udg_temp_playernumber=playerNumber"),
                         ("SKOnBaseDeath", "    set SKBaseType[victim]=GetUnitTypeId(dead)")]:
        existing[name] = once(existing[name], anchor, base_hook + anchor)
    for name, who in [("SKCheckVictory", "king"), ("SoloFootsPrepareEndGame", "winner")]:
        anchor = "set SoloFoots_EndGameStarted=true"
        indent = "        " if who == "king" else "    "
        existing[name] = once(existing[name], anchor, anchor + f'\n{indent}set CAS_winner = -{who}\n{indent}call ExecuteFunc("FFA_CasinoFinish")')
    name = "Trig_Start_game_Actions"
    existing[name] = once(existing[name], " returns nothing\n", " returns nothing\n    set WalletMatchStarted = true\n")
    main = "main" if "main" in existing else "SFMap_main"
    existing[main] = block + "\n\n" + once(existing[main], "    call DPS_Init()", "    call FFA_CasinoInit()\n    call DPS_Init()")
    result = FUN.sub(lambda m: "" if m[1].startswith("CP_") and m[1] != "CP_PreviewClose" else existing[m[1]], original)
    result = re.sub(r"(?m)^[ \t]*\w+[ \t]+(?:array[ \t]+)?CP_\w+[^\n]*\n", "", result)
    result = once(result, "            set udg_player_active[udg_X]=true",
                  "            set udg_player_active[udg_X]=true\n            set FF_gr_participant[udg_X]=true")
    used = identifiers(block)
    owned = declarations(original)
    new = [line for key,line in declarations(standalone).items() if key in used and key not in owned]
    new.append("    trigger FFA_CasinoLaunch = CreateTrigger()")
    return once(result, "\nendglobals", "\n" + "\n".join(new) + "\nendglobals")


def stage(project, parent, reference):
    for file, sha in [(parent, FFA if project == "ffa" else CASINO), (reference, CASINO)]:
        if hashlib.sha256(file.read_bytes()).hexdigest() != sha:
            raise ValueError(f"Unexpected baseline {file.name}")
    work = ROOT / "build/casino-consolidation" / project
    folder = work / "projects" / project
    src = folder / "src"
    src.mkdir(parents=True, exist_ok=True)
    (folder / "release").mkdir(exist_ok=True)
    shutil.copy2(parent, folder / "release" / parent.name)
    for name in ("Build-Map.ps1","tools.local.json","tools/build_map.py","tools/map_archive.py","tools/Install-Wc3Map.ps1"):
        target = work / name
        target.parent.mkdir(exist_ok=True)
        origin = ROOT / name
        if project == "casino" and name in {"Build-Map.ps1","tools/build_map.py"}:
            # The original standalone builder supports its separate family ID.
            target.write_bytes(subprocess.check_output(["git","show",f"a12ec49:{name}"],cwd=ROOT))
        else:
            shutil.copy2(origin, target)
    family = "FFA Foots" if project == "ffa" else "799-CASINO"
    title = "FFA Foots v83 SD Draft" if project == "ffa" else "799-CASINO v13 - RJE"
    (folder / "project.json").write_text(json.dumps(dict(map_type=family,release=parent.name,sha256=FFA if project=="ffa" else CASINO)))
    dll = json.loads((ROOT / "tools.local.json").read_text())["stormlib"]
    with solo["Archive"](dll, reference) as donor, solo["Archive"](dll, parent) as active:
        legacy = credit_record(runtime_patch(globals_patch(decoded(donor.read("war3map.j")))))
        original = active.read("war3map.j")
        script = ffa_script(decoded(original), legacy) if project == "ffa" else legacy
        script, count = re.subn(r'call SetMapName\("[^"]+"\)', 'call SetMapName("' + title + '")', script)
        assert count == 1
        (src / "war3map.j").write_bytes(endlines(script,original))
        info = active.read("war3map.w3i")
        old = info[28:info.index(0,28)]
        (src / "war3map.w3i").write_bytes(once(info,old+b"\0",title.encode()+b"\0"))
        (src / "war3map.wts").write_bytes(active.read("war3map.wts").replace(old,title.encode()))
        if project == "ffa":
            # The preview contained the art in the MPQ but did not register it
            # with the editor's import manager. Keep it on future editor saves.
            imports = active.read("war3map.imp")
            version, count = struct.unpack_from("<II",imports)
            registered = {item[1:].lower().replace(b"/",b"\\") for item in imports[8:].split(b"\0") if item}
            cards = ["table","empty","back","dealer"] + [f"chips{i}" for i in range(1,5)] + [f"card{i}" for i in range(52)]
            art = [r"CasinoUI\Bold.ttf",r"CasinoUI\panel.blp"] + ["PokerUI\\"+card+".blp" for card in cards]
            extra = []
            for name in art:
                assert active.read(name) == donor.read(name)
                if name.encode().lower() not in registered:
                    extra.append(b"\r"+name.encode()+b"\0")
            if extra:
                (src / "war3map.imp").write_bytes(struct.pack("<II",version,count+len(extra))+imports[8:]+b"".join(extra))
            editor = active.read("war3map.wct")
            offset = editor.index(0,4)+1
            size = struct.unpack_from("<I",editor,offset)[0]
            record = editor[offset+4:offset+4+size]
            assert record[-1] == 0
            updated = endlines(ffa_script(decoded(record[:-1]),legacy),record) + b"\0"
            (src / "war3map.wct").write_bytes(editor[:offset]+struct.pack("<I",len(updated))+updated+editor[offset+4+size:])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", choices=("ffa","casino"))
    parser.add_argument("parent", type=Path)
    parser.add_argument("standalone", type=Path)
    args = parser.parse_args()
    stage(args.project,args.parent,args.standalone)
