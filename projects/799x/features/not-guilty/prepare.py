"""Prepare the Not Guilty radius update on the complete 799X RC27 map."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))
from map_archive import Archive
from restore_rc6_item_text import parse, dump

BASE_HASH = "6eff2795dad5ed8b5aae2b6bb945bd6d22d78efa0e22c26178327de19e89283d"
RANKS = ((350, 400), (450, 500), (500, 600))


def replace_once(data, old, new):
    if data.count(old) != 1:
        raise ValueError(f"Expected exactly one match for {old[:80]!r}")
    return data.replace(old, new)


def update_trigger(script):
    start = script.index(b"function Trig_HERO_Not_Guilty_Actions takes")
    end = script.index(b"endfunction", start)
    body = script[start:end]
    eol = b"\r\n" if b"\r\n" in body else b"\n"
    for old, _ in RANKS:
        body = replace_once(body, f"        set udg_temp_AoE={old}.00".encode()+eol, b"")
    body = replace_once(body, b"returns nothing"+eol, b"returns nothing"+eol+
        b"    local real buffRadius = BlzGetAbilityRealLevelField(GetSpellAbility(), "+
        b"ABILITY_RLF_AREA_OF_EFFECT, GetUnitAbilityLevel(GetTriggerUnit(), GetSpellAbilityId()) - 1)"+eol)
    body = replace_once(body, b"GetUnitsInRangeOfLocMatching(udg_temp_AoE,",
                        b"GetUnitsInRangeOfLocMatching(buffRadius,")
    return script[:start] + body + script[end:]


def prepare(base, stage):
    if hashlib.sha256(base.read_bytes()).hexdigest() != BASE_HASH:
        raise ValueError("Expected verified 799X RC27 as the baseline")
    src = stage / "projects/799x/src"
    (src / "source_roundtrip").mkdir(parents=True, exist_ok=True)
    for name in ("Build-Map.ps1", "tools/build_map.py", "tools/map_archive.py",
                 "tools/Install-Wc3Map.ps1", "tools.local.json"):
        dest = stage / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    release = src.parent / "release" / base.name
    release.parent.mkdir(exist_ok=True)
    shutil.copyfile(base, release)
    project = json.loads((ROOT / "projects/799x/project.json").read_text())
    project.update(release=base.name, sha256=BASE_HASH)
    (src.parent / "project.json").write_text(json.dumps(project, indent=2))
    dll = json.loads((ROOT / "tools.local.json").read_text())["stormlib"]
    with Archive(dll, base) as arc:
        name = "war3map.w3a"
        table = parse(arc.read(name), extended=True)
        [mods] = [mods for entries in table[1] for header,mods in entries if header[4:8] == b"A08Z"]
        fields = {struct.unpack_from("<i", m[2])[0]:m for m in mods if m[0] == b"aare"}
        assert set(fields) == {1,2,3}
        for rank, (old, new) in enumerate(RANKS, 1):
            mod = fields[rank]
            assert struct.unpack("<iif",mod[2]) == (rank,0,old)
            mod[2] = struct.pack("<iif",rank,0,new)
        (src / name).write_bytes(dump(table))
        jass = replace_once(update_trigger(arc.read("war3map.j")), b"v7.9.9X-rc26", b"v7.9.9X-rc28")
        (src / "war3map.j").write_bytes(jass)
        old_runtime = arc.read(r"source_roundtrip\FF_Runtime.j")
        runtime = update_trigger(old_runtime)
        (src / "source_roundtrip/FF_Runtime.j").write_bytes(runtime)
        def wct_entry(data):
            return struct.pack("<I",len(data)+1) + data + b"\0"
        wct = replace_once(arc.read("war3map.wct"), wct_entry(old_runtime), wct_entry(runtime))
        (src / "war3map.wct").write_bytes(wct)
        for name in ("war3map.w3i", "war3map.wts"):
            (src / name).write_bytes(replace_once(arc.read(name), b"v7.9.9X-rc27", b"v7.9.9X-rc28"))
        manifest = json.loads(arc.read("FF_SOURCE_MANIFEST.json"))
        manifest.update(revision="799X RC28 Not Guilty radius", source_map_sha256=BASE_HASH,
                        compiled_source_sha256=hashlib.sha256(jass).hexdigest(),
                        runtime_sha256=hashlib.sha256(runtime).hexdigest(), engine_playtest=False)
        (src / "FF_SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("stage", type=Path)
    args = parser.parse_args()
    prepare(args.base, args.stage)
