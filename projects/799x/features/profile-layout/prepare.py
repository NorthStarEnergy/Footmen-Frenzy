"""Stage the personal HUD and profile on the complete RC38 arena/wagers map."""
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

PARENT = "Reforged Footmen Frenzy v7.9.9X-rc38 Arena Wagers"
PARENT_SHA = "274ade135468dc528556a65666686975cee519818d2189069a5acc51c9c60442"
TITLE = "Reforged Footmen Frenzy v7.9.9X-rc39 Wallet and Profiles"
WORK = ROOT / "build/799x-rc39-profile"
MENU = [(0, "Overview"), (8, "Combat"), (9, "Economy"), (10, "Army and tech"),
        (1, "Heroes"), (2, "Items"), (3, "Units"), (4, "Skins"),
        (5, "Build order"), (7, "Usage"), (6, "Casino")]
METRICS = {
    0: [25, 29, 30, 28, 26, 27, 31, 34, 24],
    8: [29, 30, 28, 26, 27, 31, 32, 33, 34, 35, 36, 47, 48, 49, 50, 51, 7],
    9: [10, 37, 38, 39, 40, 41, 42, 43, 46, 11, 12, 13, 14, 15, 44, 45, 53, 16,
        17, 18, 19, 20, 81, 82, 83, 84, 85],
    10: [0, 1, 2, 3, 4, 5, 6, 8, 9, 52, 54, 55, 56, 57, 58, 59, 21, 22, 23],
    6: [64, 66, 65, 60, 61, 62, 63, 67, 68, *range(69, 81)],
}


def once(data, old, new):
    if data.count(old) != 1:
        raise ValueError(f"Expected one integration point: {str(old)[:110]}")
    return data.replace(old, new)


def include(name):
    return (FEATURE / name).read_text(encoding="utf-8").rstrip() + "\n"


def between(data, start, end, replacement):
    a = data.index(start)
    b = data.index(end, a)
    return data[:a] + replacement + data[b:]


def schema():
    assert set.union(*(set(ids) for ids in METRICS.values())) == set(range(86))
    lines = []
    for i, (kind, title) in enumerate(MENU):
        lines.extend([f"    set PF_menuOrder[{i}] = {kind}",
                      f'    set PF_sectionName[{kind}] = "{title}"'])
    for kind, ids in METRICS.items():
        lines.append(f"    set PF_sectionCount[{kind}] = {len(ids)}")
        for i, metric in enumerate(ids):
            lines.append(f"    set PF_metricOrder[{kind*100+i}] = {metric}")
    return "\n".join(lines) + "\n"


def add_globals(code):
    return once(code, "    framehandle PF_root = null", include("globals.j") + "    framehandle PF_root = null")


def transform(raw, compiled):
    code = raw.decode("utf-8", "surrogateescape").replace("\r\n", "\n")
    code = once(code, "function WalletLoad takes", include("wallet.j") + "\nfunction WalletLoad takes")
    wallet = code.index("function WalletLoad takes")
    stop = code.index("function CasinoWalletDelta", wallet)
    load = code[wallet:stop].replace("    call DestroyTimer", "    set HUD_walletRead = true\n    call DestroyTimer")
    load = load.replace("        return\n", "        call HUD_ShowWallet()\n        return\n")
    load = once(load, "    call WalletBroadcast()", "    call HUD_ShowWallet()\n    call WalletBroadcast()")
    code = code[:wallet] + load + code[stop:]
    code = once(code, "        set WalletBalance = CAS_gold[s]\n", "        set WalletBalance = CAS_gold[s]\n        call HUD_ShowWallet()\n")
    code = once(code, "function PF_Text takes", include("hud.j") + "\nfunction PF_Text takes")
    code = once(code, "    call TimerStart(CreateTimer(), 0.00, false, function WalletLoad)",
                "    call HUD_Create()\n    call TimerStart(CreateTimer(), 0.00, false, function WalletLoad)")
    code = once(code, "    if not DPS_Ready then\n        call DPS_Create()", "    call HUD_Refresh()\n    if not DPS_Ready then\n        call DPS_Create()")
    code = once(code, "    set PF_metrics = 81", schema() + "    set PF_metrics = 81")
    code = between(code, "function PF_Card takes", "function PF_TeamValue takes", include("profile.j") + "\n")
    code = once(code, "function PF_Render takes", include("layout.j") + "\nfunction PF_Render takes")
    code = once(code, '        exitwhen i >= 14\n        call BlzFrameSetText(PF_line[i],"")',
                '        exitwhen i >= 9\n        call BlzFrameSetVisible(PF_stripe[i],false)\n        call BlzFrameSetText(PF_extra[i],"")\n        call BlzFrameSetText(PF_line[i],"")')
    code = between(code, "    set i = 0\n    loop\n        exitwhen i >= 8\n        call BlzFrameSetVisible(PF_tab",
                   "    if PF_results then\n        call PF_ResultsView()", "    call PF_RenderNavigation()\n")
    code = once(code, "                exitwhen i >= 8\n                if f == PF_tab[i] then",
                "                exitwhen i >= 11\n                if not PF_results and f == PF_menu[i] then\n                    set PF_section = PF_menuOrder[i]\n                    set PF_page = 0\n                elseif PF_results and i < 6 and f == PF_tab[i] then")
    code = once(code, "    set PF_title = PF_Text(-0.365,0.020,0.59,0.033,0.021)",
                '    set PF_title = PF_Text(-0.100,0.018,0.370,0.035,0.020)\n    call BlzFrameSetFont(PF_title,"CasinoUI\\\\Bold.ttf",0.020,0)')
    code = once(code, "    set PF_subtitle = PF_Text(-0.365,0.059,0.735,0.021,0.011)", "    set PF_subtitle = PF_Text(-0.365,0.069,0.735,0.019,0.010)")
    code = once(code, "    set PF_results = results", """    set PF_results = results
    call BlzFrameClearAllPoints(PF_subtitle)
    if results then
        call BlzFrameSetPoint(PF_subtitle,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.365,-0.069)
        call BlzFrameSetSize(PF_subtitle,0.735,0.019)
    else
        call BlzFrameSetPoint(PF_subtitle,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.100,-0.051)
        call BlzFrameSetSize(PF_subtitle,0.370,0.019)
    endif""")
    code = once(code, "        exitwhen i >= 8\n        set PF_tab[i] = PF_Button(t,-0.366+I2R(i)*0.092,0.089,0.091)",
                "        exitwhen i >= 6\n        set PF_tab[i] = PF_Button(t,-0.366+I2R(i)*0.123,0.089,0.118)")
    code = between(code, "    set i = 0\n    loop\n        exitwhen i >= 14\n        set x = -0.362", "    set PF_prev = PF_Button", "    call PF_CreateProfile(t)\n")
    for frame, before, after in [("DPS_Panel", " FRAMEPOINT_TOPLEFT, 0.0425, 0.565", " FRAMEPOINT_TOPLEFT, 0.0425, 0.526"),
                                 ("CAS_root[s]", "FRAMEPOINT_TOPLEFT,0.05,0.57", "FRAMEPOINT_TOPLEFT,0.05,0.526"),
                                 ("PK_Dialog[p]", "FRAMEPOINT_TOPLEFT,0.05,0.57", "FRAMEPOINT_TOPLEFT,0.05,0.526")]:
        code = once(code, f"SetAbsPoint({frame},{before})", f"SetAbsPoint({frame},{after})")
    gold = '        set DPS_Gold[s] = DPS_Text("DPS_Gold", 0.620, y, 0.070, "-")'
    code = once(code, gold, gold + '\n        call BlzFrameSetFont(DPS_Gold[s],"CasinoUI\\\\Bold.ttf",0.011,0)')
    if compiled:
        code = add_globals(code)
        code = once(code, f'SetMapName("{PARENT}")', f'SetMapName("{TITLE}")')
        code = code.replace("\n", "\r\n")
    return code.encode("utf-8", "surrogateescape")


def record(data):
    return struct.pack("<I", len(data)+1) + data + b"\0"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(baseline):
    if sha(baseline.read_bytes()) != PARENT_SHA:
        raise ValueError("Expected the complete RC38 arena wagers map")
    project = WORK / "projects/799x"
    release = project / "release" / baseline.name
    release.parent.mkdir(parents=True, exist_ok=True)
    if not release.exists():
        shutil.copyfile(baseline, release)
    if sha(release.read_bytes()) != PARENT_SHA:
        raise ValueError("Staged baseline checksum mismatch")
    for name in ("Build-Map.ps1", "tools.local.json", "tools/build_map.py", "tools/map_archive.py", "tools/Install-Wc3Map.ps1"):
        dest = WORK / name
        dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    config = json.loads((WORK / "tools.local.json").read_text())
    with Archive(config["stormlib"], release) as archive:
        glob = r"source_roundtrip\globals.j"
        runtime = r"source_roundtrip\FF_Runtime.j"
        old_globals, old_runtime = archive.read(glob), archive.read(runtime)
        payloads = {"war3map.j": transform(archive.read("war3map.j"), True),
                    glob: add_globals(old_globals.decode("utf-8")).encode("utf-8"),
                    runtime: transform(old_runtime, False)}
        wct = once(archive.read("war3map.wct"), record(old_globals), record(payloads[glob]))
        payloads["war3map.wct"] = once(wct, record(old_runtime), record(payloads[runtime]))
        for name in ("war3map.w3i", "war3map.wts"):
            payloads[name] = once(archive.read(name), PARENT.encode(), TITLE.encode())
        manifest = json.loads(archive.read("FF_SOURCE_MANIFEST.json"))
        manifest.update(compiled_source_sha256=sha(payloads["war3map.j"]), globals_sha256=sha(payloads[glob]),
                        runtime_sha256=sha(payloads[runtime]), source_map_sha256=PARENT_SHA, revision=TITLE,
                        runtime_functions=len(re.findall(rb"(?m)^[ \t]*function \w+ takes ", payloads[runtime])),
                        engine_playtest=False)
        payloads["FF_SOURCE_MANIFEST.json"] = json.dumps(manifest, indent=2).encode()
    for name, data in payloads.items():
        dest = project / "src" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    meta = json.loads((ROOT / "projects/799x/project.json").read_text())
    meta.update(release=release.name, sha256=PARENT_SHA, source_payloads=len(payloads))
    (project / "project.json").write_text(json.dumps(meta, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    prepare(parser.parse_args().baseline)
