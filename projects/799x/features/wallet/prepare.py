"""Stage the player casino and Wallet export on the preserved RC28 release."""
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

BASE = "85b639fd873dcfb663a6aec3d143225ae0b40af772f9bca7aee78cc148da7543"


def once(data, before, after):
    if data.count(before) != 1:
        raise ValueError(f"Expected one occurrence of {before[:90]!r}")
    return data.replace(before, after)


def globals_edit(text):
    return once(text, "    boolean array WalletKnown", """    string WalletSyncPrefix = "FFWallet1"
    integer array WalletOpening
    integer array WalletStartingGrant
    boolean array WalletKnown""")


def runtime_edit(text):
    start = text.index("function PK_Eligible takes")
    body = text.index("\n", start) + 1
    text = text[:body] + "    return CAS_User(p+1)\n" + text[text.index("endfunction", body):]
    changes = [
        ('BlzSendSyncData("FFWallet1",', 'BlzSendSyncData(WalletSyncPrefix,'),
        ('        set WalletBalance = 1000', '        set WalletSyncPrefix = "FFWalletNew"\n        set WalletBalance = 1000'),
        ('        call BlzTriggerRegisterPlayerSyncEvent(sync, Player(id), "FFWallet1", false)',
         '        call BlzTriggerRegisterPlayerSyncEvent(sync, Player(id), "FFWallet1", false)\n'
         '        call BlzTriggerRegisterPlayerSyncEvent(sync, Player(id), "FFWalletNew", false)'),
        ('        set WalletKnown[id] = true', '''        set WalletKnown[id] = true
        set WalletOpening[id] = amount
        if BlzGetTriggerSyncPrefix() == "FFWalletNew" and amount == 1000 then
            set WalletStartingGrant[id] = amount
        endif
        set PF_dirty = true'''),
        ('    set PF_exportSlot = 1\n    loop', '''    local integer account
    call Preload("casino,enabled=1,starting_wallet=1000")
    set PF_exportSlot = 1
    loop'''),
        ('        if FF_gr_participant[PF_exportSlot] or PF_wagers[PF_exportSlot] > 0 or WalletPlayedSlot[PF_exportSlot-1] > 0 then',
         '''        set account = PF_exportSlot-1
        if WalletKnown[account] or FF_gr_participant[PF_exportSlot] or PF_wagers[PF_exportSlot] > 0 or WalletPlayedSlot[account] > 0 then
            if WalletKnown[account] then
                call Preload("wallet,"+I2S(PF_exportSlot)+",known=1,opening="+I2S(WalletOpening[account])+",balance="+I2S(WalletPublic[account])+",starting_grant="+I2S(WalletStartingGrant[account]))
            else
                call Preload("wallet,"+I2S(PF_exportSlot)+",known=0")
            endif'''),
        ('"Account gold"', '"Wallet"'), ('"Match award (account gold)"', '"Match award (Wallet)"'),
        ('"Account Gold: unavailable"', '"Wallet: unavailable"'), ('"Account Gold: "', '"Wallet: "'),
        ('"+200 account gold for playing."', '"+200 to your Wallet for playing."'),
        ('I2S(reward)+" account gold."', 'I2S(reward)+" to your Wallet."'),
        ('Casino and credit   /   Account gold', 'Casino and credit   /   Wallet'),
        ('    Account gold earned   ', '    Wallet earnings   '),
        ('DPS_GoldHeader", 0.620, 0.046, 0.070, "|cffffcc00Gold|r"', 'DPS_GoldHeader", 0.620, 0.046, 0.070, "|cffffcc00Wallet|r"'),
        ('"Account gold unavailable, or this match has ended."', '"Wallet unavailable, or this match has ended."'),
        ('I2S(stake)+" account gold."', 'I2S(stake)+" gold from your Wallet."'),
        ('|cffe7cb88GOLD|r|nStakes use locally saved account gold.', '|cffe7cb88Wallet|r|nStakes come from your Wallet.'),
        ('"ACCOUNT GOLD "', '"Wallet "'),
        ('Poker practice is available in custom observer slots.', 'Your poker table is still loading.'),
        ('Account gold wagers.', 'Wagers use your Wallet.'),
    ]
    for before, after in changes:
        text = once(text, before, after)
    return text


def edit(data, transform):
    newline = "\r\n" if b"\r\n" in data else "\n"
    return transform(data.decode("utf-8").replace("\r\n", "\n")).replace("\n", newline).encode("utf-8")


def framed(data):
    return struct.pack("<I", len(data) + 1) + data + b"\0"


def prepare(base, stage):
    if hashlib.sha256(base.read_bytes()).hexdigest() != BASE:
        raise ValueError("Expected the preserved RC28 baseline")
    src = stage / "projects/799x/src"
    (src / "source_roundtrip").mkdir(parents=True, exist_ok=True)
    for name in ("Build-Map.ps1", "tools.local.json", "tools/build_map.py", "tools/map_archive.py", "tools/Install-Wc3Map.ps1"):
        dest = stage / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, dest)
    release = src.parent / "release" / base.name
    release.parent.mkdir(exist_ok=True)
    shutil.copyfile(base, release)
    project = json.loads((ROOT / "projects/799x/project.json").read_text())
    project.update(release=base.name, sha256=BASE)
    (src.parent / "project.json").write_text(json.dumps(project, indent=2))
    dll = json.loads((stage / "tools.local.json").read_text())["stormlib"]
    with Archive(dll, base) as arc:
        old, new = b"v7.9.9X-rc28", b"v7.9.9X-rc29"
        script = once(edit(arc.read("war3map.j"), lambda s: globals_edit(runtime_edit(s))), old, new)
        (src / "war3map.j").write_bytes(script)
        manifest = json.loads(arc.read("FF_SOURCE_MANIFEST.json"))
        wct = arc.read("war3map.wct")
        for name, transform, key in (("FF_Runtime", runtime_edit, "runtime_sha256"), ("globals", globals_edit, "globals_sha256")):
            data = arc.read("source_roundtrip\\" + name + ".j")
            updated = edit(data, transform)
            wct = once(wct, framed(data), framed(updated))
            (src / "source_roundtrip" / (name + ".j")).write_bytes(updated)
            manifest[key] = hashlib.sha256(updated).hexdigest()
        (src / "war3map.wct").write_bytes(wct)
        for name in ("war3map.w3i", "war3map.wts"):
            (src / name).write_bytes(once(arc.read(name), old, new))
        manifest.update(revision="799X RC29 player casino and Wallet", source_map_sha256=BASE,
                        compiled_source_sha256=hashlib.sha256(script).hexdigest(), engine_playtest=False)
        (src / "FF_SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("stage", type=Path)
    args = parser.parse_args()
    prepare(args.base, args.stage)
