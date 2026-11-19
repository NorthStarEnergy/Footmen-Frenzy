"""Stage Solo RC8 with the Casino launcher inside Info."""
import argparse
import json
import runpy
from pathlib import Path

from prepare import Archive, ROOT, TITLE, once, stage_project

RC7_SHA = "4e899d45a982b93d6b4e33d2c929d483ce61a473c8b661dbb2dcb19f04b1a87b"
RC8_TITLE = "Solo Foots 1.8-RC8"


def stage_menu(base):
    src = stage_project(base, RC7_SHA, ROOT / "build/solo-rc8-menu")
    shared = runpy.run_path(str(ROOT / "projects/799x/features/open-casino/prepare.py"))
    dll = json.loads((ROOT / "tools.local.json").read_text())["stormlib"]
    with Archive(dll, base) as archive:
        jass = archive.read("war3map.j").decode().replace("\r\n", "\n")
        jass = shared["menu_only"](shared["menu_globals"](jass))
        # Solo's refresh block contained only the old battlefield launcher.
        jass = once(jass, "            if GetLocalPlayer() == Player(s-1) then\n            endif\n", "")
        jass = once(jass, 'BlzFrameSetText(DPS_Button, "Profile")', 'BlzFrameSetText(DPS_Button, "Info")')
        jass = once(jass, TITLE, RC8_TITLE)
        (src / "war3map.j").write_bytes(jass.replace("\n", "\r\n").encode())
        for name in ("war3map.w3i", "war3map.wts"):
            (src / name).write_bytes(once(archive.read(name), TITLE.encode(), RC8_TITLE.encode()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    stage_menu(parser.parse_args().base)
