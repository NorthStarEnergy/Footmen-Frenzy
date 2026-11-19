"""Stage the wager arena on a verified complete 799X parent for Build-Map.ps1."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys

FEATURE = Path(__file__).resolve().parent
ROOT = FEATURE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from map_archive import Archive

PARENT_SHA = "6792cc51124d9d5d036f95cb58ad92c8161324207f1b270189a4042b134826e9"
PARENT_TITLE = "Reforged Footmen Frenzy v7.9.9X-rc36"
ARENA_SHA = "5d2ddc725afacd699db3f24593f675ed5faa1bb5f621d872d422619e4701388f"
ARENA_TITLE = "Reforged Footmen Frenzy v7.9.9X-rc37 Arena 1v1"
TITLE = "Reforged Footmen Frenzy v7.9.9X-rc38 Arena Wagers"
WORK = ROOT / "build/799x-rc38-arena-wagers"


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one integration point: {old!r}")
    return text.replace(old, new)


def include(filename):
    return (FEATURE / filename).read_text(encoding="utf-8").strip("\n") + "\n"


def wager_controls(script):
    script = once(script, '    call AR_End("The main match ended. The arena is closed.")',
                  '    call AR_End(0,"The main match ended. The arena is closed.")')
    script = once(script, '0.244,0.298,0.212,"Invite")', '0.244,0.298,0.212,"Invite free")')
    script = once(script, '    call CAS_Button(s,53,', '    call CAS_Button(s,19,click,0.430,0.394,0.245,"Invite for gold")\n    call CAS_Button(s,53,')
    script = once(script, '    elseif id == 39 and CAS_view[s] == 3 then',
                  '    elseif id == 19 and CAS_view[s] == 6 then\n        call AR_Invite(s,AR_SelectedStake(s))\n    elseif id == 39 and CAS_view[s] == 3 then')
    script = once(script, "            call AR_Invite(s)", "            call AR_Invite(s,0)")
    script = once(script, "            call AR_Accept(s)", """            if GetLocalPlayer() == Player(s-1) then
                call BlzSendSyncData("AR_Accept",I2S(AR_shownOffer))
            endif""")
    script = once(script, "    local trigger loans = CreateTrigger()", "    local trigger arenaAccept = CreateTrigger()\n    local trigger loans = CreateTrigger()")
    script = once(script, "    call AR_Init()", "    call AR_Init()\n    call TriggerAddAction(arenaAccept,function AR_ReceiveAccept)")
    script = once(script, '        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-arena",true)',
                  '        call BlzTriggerRegisterPlayerSyncEvent(arenaAccept,Player(p),"AR_Accept",false)\n        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-arena",true)')
    script = once(script, "CAS_view[s] != 5 and CAS_view[s] != 6)", "CAS_view[s] != 5 and (CAS_view[s] != 6 or (AR_state == 0 and not CAS_ended)))")
    script = once(script, '        set label = "Free duel"', """        if AR_state == 0 then
            set label = "Selected: "+AR_Terms(AR_SelectedStake(s))+"    /    Exact amount: -stake 250"
        else
            set label = AR_Terms(AR_stake)
        endif""")
    return once(script, "Arena 1v1: a free fight to hero death.", "Arena 1v1: play free or match Wallet stakes. Winner takes the pot.")


def source(data, editor=False, has_arena=False):
    script = data.decode("utf-8", "surrogateescape").replace("\r\n", "\n")
    if has_arena:
        if not editor:
            script = replace_globals(script)
            script = once(script, f'SetMapName("{ARENA_TITLE}")', f'SetMapName("{TITLE}")')
        for start, end, path in (("AR_CanPlay", "AR_Accept", "runtime.j"), ("AR_View", "AR_View", "panel.j")):
            i = script.index(f"function {start} takes")
            j = script.index("\nendfunction\n", script.index(f"function {end} takes", i))+len("\nendfunction\n")
            script = script[:i]+include(path)+script[j:]
        script = wager_controls(script)
        return (script if editor else script.replace("\n", "\r\n")).encode("utf-8", "surrogateescape")
    # Legacy missiles, global reveal/silence and editor indexers use the original battlefield.
    script = script.replace("GetWorldBounds()", "AR_MatchBounds()").replace("GetEntireMapRect()", "AR_MatchBounds()")
    if editor:
        script = once(script, "function FFUI_GetRoot ", include("bounds.j") + "\nfunction FFUI_GetRoot ")
    else:
        script = once(script, "\nendglobals\n", "\n" + include("globals.j") + "endglobals\n\n" + include("bounds.j"))
    script = once(script, "function DU_Cancel takes", include("runtime.j") + "\nfunction DU_Cancel takes")
    script = once(script, "function CAS_DuelsView ", include("panel.j") + "\nfunction CAS_DuelsView ")
    script = once(script, "    set CasinoOpen = CreateTrigger()", "    call AR_Init()\n    set CasinoOpen = CreateTrigger()")
    script = once(script, "    set CAS_ended = true", '    set CAS_ended = true\n    call AR_End("The main match ended. The arena is closed.")')
    script = once(script, "    call BJ_Tick()\n", "    if AR_state == 1 then\n        call AR_Tick()\n    endif\n    call BJ_Tick()\n")
    script = once(script, "if FF_oc_mode[i] != 0 then", "if FF_oc_mode[i] != 0 and not (AR_state == 2 and (i+1 == AR_seat[0] or i+1 == AR_seat[1])) then")

    # Arena kills must never run the native match's revive, score, betting or XP handlers.
    for name in ("Trig_autorevive_Conditions", "Trig_change_Revive_time_based_on_level_Conditions",
                 "Trig_Multiboard_Update_Conditions", "Trig_set_hero_bounty_Conditions",
                 "Trig_Unit_Experience_System_Actions", "Trig_Foot_Exp_system_Actions",
                 "FF_oc_OnDeath", "FF_kl_OnDeath", "FF_st_OnDeath", "DPS_OnDeath", "MK_HeroDeath",
                 "GSI_Blocked"):
        match = re.search(rf"(?m)^function {name} takes [^\n]+ returns (boolean|nothing)\n(?:[ \t]+local [^\n]+\n)*", script)
        if not match:
            raise ValueError(name)
        fallback = " false" if match[1] == "boolean" else ""
        unit = "u" if name == "GSI_Blocked" else "GetTriggerUnit()"
        script = script[:match.end()] + f"    if AR_Fighter({unit}) then\n        return{fallback}\n    endif\n" + script[match.end():]

    script = once(script, "    call CAS_ShowButton(s,38,DU_outgoing[s] > 0)",
                  '    call CAS_ShowButton(s,38,DU_outgoing[s] > 0)\n    call CUI_Text(CAS_button[s*64+39],"Arena 1v1")\n    call CAS_ShowButton(s,39,true)')
    script = once(script, "    elseif CAS_view[s] == 5 then\n        set label = \"|cffe7cb88CREDIT",
                  '    elseif CAS_view[s] == 6 then\n        set label = "|cffe7cb88ARENA 1v1|r"\n        call AR_View(s)\n    elseif CAS_view[s] == 5 then\n        set label = "|cffe7cb88CREDIT')
    script = once(script, "i+1 == CAS_view[s] then", "i+1 == CAS_view[s] or (i == 2 and CAS_view[s] == 6) then")
    script = once(script, "CAS_button[s*64+i],CAS_view[s] != 5)", "CAS_button[s*64+i],CAS_view[s] != 5 and CAS_view[s] != 6)")
    script = once(script, "    call BlzFrameSetText(CAS_status[s],label)",
                  '    if CAS_view[s] == 6 then\n        set label = "Free duel"\n    endif\n    call BlzFrameSetText(CAS_status[s],label)')
    script = once(script, "    elseif id == 33 then\n        call DU_Offer", """    elseif id == 39 and CAS_view[s] == 3 then
        set CAS_view[s] = 6
    elseif id == 39 and CAS_view[s] == 6 then
        set CAS_view[s] = 3
    elseif id >= 53 and id <= 56 and CAS_view[s] == 6 then
        if id == 53 then
            set AR_pick[s] = AR_Next(s,AR_Target(s))
        elseif id == 54 then
            call AR_Invite(s)
        elseif id == 55 then
            call AR_Accept(s)
        else
            call AR_Withdraw(s)
        endif
    elseif id == 33 then
        call DU_Offer""")
    script = once(script, '    elseif line == "-challenges" then', '    elseif line == "-arena" then\n        set CAS_view[s] = 6\n    elseif line == "-challenges" then')
    script = once(script, '        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-challenges",true)',
                  '        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-challenges",true)\n        call TriggerRegisterPlayerChatEvent(chat,Player(p),"-arena",true)')
    script = once(script, "    set CAS_content[b] = CAS_Label", """    call CAS_Button(s,39,click,0.463,0.298,0.212,"Arena 1v1")
    call CAS_Button(s,53,click,0.025,0.298,0.212,"Opponent >")
    call CAS_Button(s,54,click,0.244,0.298,0.212,"Invite")
    call CAS_Button(s,55,click,0.025,0.333,0.212,"Accept")
    call CAS_Button(s,56,click,0.244,0.333,0.212,"Decline")
    set CAS_content[b] = CAS_Label""")
    script = once(script, "Equal stakes. Accept to back the opposite result.", "Prediction: equal stakes on opposite results. Arena 1v1: a free fight to hero death.")
    script = wager_controls(script)
    if not editor:
        script = once(script, f'SetMapName("{PARENT_TITLE}")', f'SetMapName("{TITLE}")')
        script = script.replace("\n", "\r\n")
    return script.encode("utf-8", "surrogateescape")


def terrain(data):
    if data[:8] != b"W3E!\x0c\x00\x00\x00":
        raise ValueError("Expected RC36 version 12 terrain")
    pos = 13
    for _ in range(2):
        pos += 4 + 4 * struct.unpack_from("<I", data, pos)[0]
    if struct.unpack_from("<IIff", data, pos) != (65, 65, -4096., -4096.):
        raise ValueError("Unexpected terrain origin or dimensions")
    header = bytearray(data[:pos+16])
    struct.pack_into("<I", header, pos+4, 97)
    original = data[pos+16:]
    assert len(original) == 65 * 65 * 8
    # Copy a flat Dalaran floor vertex, retaining the actual tileset's height and cliff fields.
    tile = original[(32*65+32)*8:(32*65+32)*8+8]
    extra = bytearray()
    for row in range(65, 97):
        y = -4096 + row*128
        for col in range(65):
            x = -4096 + col*128
            v = bytearray(tile)
            # Marble floor, square-tiled perimeter, brick starting lines and a center stripe.
            surface = 2
            if -1024 <= x < 1024 and 5376 <= y < 6912:
                surface = 8 if x not in (-768, 0, 640) else 3
            elif -1152 <= x <= 1024 and 5248 <= y <= 6912:
                surface = 4
            v[4:6] = struct.pack("<H", surface)
            extra.extend(v)
    return header + original + extra


def pathing(data):
    assert data[:4] == b"MP3W" and struct.unpack_from("<II", data, 8) == (256, 256)
    assert len(data) == 16 + 256*256
    north = bytearray([0xce]) * (128*256)
    # WPM cells are 32 units. The original battlefield pathing is byte-for-byte unchanged.
    for row in range((5376-4096)//32, (6912-4096)//32):
        left = row*256 + (-1024+4096)//32
        north[left:left+64] = bytes([0x08])*64
    return data[:12] + struct.pack("<I", 384) + data[16:] + north


def info(data):
    pos = 28
    for _ in range(4):
        pos = data.index(0, pos)+1
    updated = bytearray(data)
    assert struct.unpack_from("<ii", data, pos+48) == (52, 52)
    for offset in (12, 20):
        top = struct.unpack_from("<f", data, pos+offset)[0]
        assert top == 2816.
        struct.pack_into("<f", updated, pos+offset, top+4096.)
    struct.pack_into("<i", updated, pos+52, 84)
    return once(bytes(updated), PARENT_TITLE.encode(), TITLE.encode())


def replace_globals(script):
    start = script.index("    // One physical arena.")
    end = script.index("    real AR_oldZoom\n", start)+len("    real AR_oldZoom\n")
    return script[:start]+include("globals.j")+script[end:]


def editor_payloads(archive, compiled, parent_sha):
    globals_name = "source_roundtrip\\globals.j"
    runtime_name = "source_roundtrip\\FF_Runtime.j"
    old_globals = archive.read(globals_name)
    old_runtime = archive.read(runtime_name)
    extra = (FEATURE / "globals.j").read_text(encoding="utf8").rstrip().encode()
    has_arena = parent_sha == ARENA_SHA
    if has_arena:
        header = replace_globals(old_globals.decode("utf8")).encode("utf8")
    else:
        header = once(old_globals, b"\nendglobals\n", b"\n" + extra + b"\nendglobals\n")
    runtime = source(old_runtime, editor=True, has_arena=has_arena)
    wct = archive.read("war3map.wct")
    def record(blob):
        return struct.pack("<I", len(blob)+1) + blob + b"\0"
    wct = once(wct, record(old_globals), record(header))
    wct = once(wct, record(old_runtime), record(runtime))
    manifest = json.loads(archive.read("FF_SOURCE_MANIFEST.json"))
    digest = lambda blob: hashlib.sha256(blob).hexdigest()
    manifest.update(compiled_source_sha256=digest(compiled), globals_sha256=digest(header),
                    runtime_sha256=digest(runtime), source_map_sha256=parent_sha, revision=TITLE,
                    runtime_functions=len(re.findall(rb"(?m)^[ \t]*function \w+ takes ", runtime)),
                    engine_playtest=False)
    return {globals_name: header, runtime_name: runtime, "war3map.wct": wct,
            "FF_SOURCE_MANIFEST.json": json.dumps(manifest, indent=2).encode()}


def prepare(baseline):
    parent_sha = hashlib.sha256(baseline.read_bytes()).hexdigest()
    if parent_sha not in (PARENT_SHA, ARENA_SHA):
        raise ValueError("Expected the verified RC36 or RC37 arena parent.")
    has_arena = parent_sha == ARENA_SHA
    project = WORK / "projects/799x"
    src = project / "src"
    src.mkdir(parents=True, exist_ok=True)
    release = project / "release" / baseline.name
    release.parent.mkdir(exist_ok=True)
    if not release.exists():
        shutil.copyfile(baseline, release)
    if hashlib.sha256(release.read_bytes()).hexdigest() != parent_sha:
        raise ValueError("Staged parent checksum mismatch")
    meta = json.loads((ROOT / "projects/799x/project.json").read_text())
    meta.update(release=release.name, sha256=parent_sha, source_payloads=10)
    (project / "project.json").write_text(json.dumps(meta, indent=2))
    for name in ("Build-Map.ps1", "tools.local.json", "tools/build_map.py", "tools/map_archive.py", "tools/Install-Wc3Map.ps1"):
        target = WORK / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    dll = json.loads((WORK / "tools.local.json").read_text())["stormlib"]
    with Archive(dll, release) as a:
        shadow = a.read("war3map.shd")
        assert len(shadow) == 256*(384 if has_arena else 256)
        title_before = (ARENA_TITLE if has_arena else PARENT_TITLE).encode()
        payloads = {
            "war3map.j": source(a.read("war3map.j"), has_arena=has_arena),
            "war3map.w3e": a.read("war3map.w3e") if has_arena else terrain(a.read("war3map.w3e")),
            "war3map.wpm": a.read("war3map.wpm") if has_arena else pathing(a.read("war3map.wpm")),
            "war3map.shd": shadow if has_arena else shadow + bytes(256*128),
            "war3map.w3i": once(a.read("war3map.w3i"), title_before, TITLE.encode()) if has_arena else info(a.read("war3map.w3i")),
            "war3map.wts": once(a.read("war3map.wts"), title_before, TITLE.encode()),
        }
        payloads.update(editor_payloads(a, payloads["war3map.j"], parent_sha))
        for name, data in payloads.items():
            (src / name).parent.mkdir(exist_ok=True)
            (src / name).write_bytes(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    prepare(parser.parse_args().baseline)
