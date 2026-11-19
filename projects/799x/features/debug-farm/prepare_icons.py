"""Stage the RC26 page arrow and Legal Research book against the complete RC25 map."""
import argparse
import json
import shutil
import struct
from pathlib import Path

from PIL import Image, ImageEnhance
from prepare import Archive, FEATURE, ROOT, blp, objects, once, sha
from restore_rc6_item_text import dump, parse

RC25 = "248f228fa0fbf5ea372d374acda456e486dbc811c545c81f97b8e957af217fc0"
BOOK = objects.ICON.replace("FootsPageTurn", "FootsLegalResearch")


def disabled(icon):
    return icon.replace("CommandButtons\\BTN", "CommandButtonsDisabled\\DISBTN")


def prepare(base, stage):
    if sha(base.read_bytes()) != RC25:
        raise ValueError("Expected the verified RC25 map")
    src = stage / "projects/799x/src"
    src.mkdir(parents=True, exist_ok=True)
    for name in ("Build-Map.ps1", "tools/build_map.py", "tools/map_archive.py",
                 "tools/Install-Wc3Map.ps1", "tools.local.json"):
        dest = stage / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    release = src.parent / "release" / base.name
    release.parent.mkdir(exist_ok=True)
    shutil.copyfile(base, release)
    project = json.loads((ROOT / "projects/799x/project.json").read_text())
    project.update(release=base.name, sha256=RC25)
    (src.parent / "project.json").write_text(json.dumps(project, indent=2))
    dll = json.loads((ROOT / "tools.local.json").read_text())["stormlib"]
    with Image.open(FEATURE / "blue-page-arrow.png") as image:
        arrow = image.convert("RGBA").resize((64, 64), Image.Resampling.LANCZOS)
    with Archive(dll, base) as archive:
        imports = archive.read("war3map.imp")
        for page_path, book_path, art in (
            (objects.ICON, BOOK, arrow),
            (disabled(objects.ICON), disabled(BOOK), ImageEnhance.Brightness(arrow).enhance(0.48)),
        ):
            assert page_path.encode()+b"\0" in imports and book_path.encode()+b"\0" not in imports
            (src / page_path).parent.mkdir(parents=True, exist_ok=True)
            (src / book_path).write_bytes(archive.read(page_path))
            (src / page_path).write_bytes(blp(art))
            imports += b"\x0d" + book_path.encode() + b"\0"
        count = struct.unpack_from("<I", imports, 4)[0]
        (src / "war3map.imp").write_bytes(imports[:4] + struct.pack("<I", count+2) + imports[8:])

        table = parse(archive.read("war3mapSkin.w3a"), extended=True)
        records = [mods for entries in table[1] for header,mods in entries if header[4:8] == b"A08Y"]
        [research] = records
        changed = []
        for mod in research:
            if mod[0] in (b"aart", b"arar"):
                assert mod[1] == 3 and mod[2][8:].endswith(b"BTNGreenBook.blp\0")
                mod[2] = mod[2][:8] + BOOK.encode() + b"\0"
                changed.append(mod[0])
        assert sorted(changed) == [b"aart", b"arar"]
        (src / "war3mapSkin.w3a").write_bytes(dump(table))

        for name in ("war3map.wts", "war3map.w3i", "war3map.j"):
            payload = once(archive.read(name), b"v7.9.9X-rc25", b"v7.9.9X-rc26")
            (src / name).write_bytes(payload)
        manifest = json.loads(archive.read("FF_SOURCE_MANIFEST.json"))
        manifest.update(revision="799X RC26 command icons", source_map_sha256=RC25,
                        compiled_source_sha256=sha((src / "war3map.j").read_bytes()), engine_playtest=False)
        (src / "FF_SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("stage", type=Path)
    args = parser.parse_args()
    prepare(args.base, args.stage)
