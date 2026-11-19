"""Exercise the packed Wallet load, sync, wager and export paths with native mocks."""
import ast
from collections import defaultdict
import json
from pathlib import Path
import re
import sys
import zlib

from prepare import ROOT, Archive

path = Path(sys.argv[1])
dll = json.loads((ROOT / "tools.local.json").read_text())["stormlib"]
with Archive(dll, path) as archive:
    script = archive.read("war3map.j").decode().replace("\r\n", "\n")
funcs = dict(re.findall(r"(?m)^function (\w+) takes([^\n]*\n[\s\S]*?^endfunction)", script))
translator = dict(ast=ast, re=re, FUNCTIONS={n: "function "+n+" takes"+v for n,v in funcs.items()})
source = (ROOT / "development/footmen/casino-v1/test_casino.py").read_text("utf-8")
exec(source[source.index("def expr("):source.index("NOW =")], translator)
files = {}
packets = []
rows = []
noop = lambda *args: None
account = "WalletTester"
fake_hash = lambda s: zlib.crc32(s.encode()) & 0x7fffffff
integer = lambda s: int(s) if s and re.fullmatch(r"-?\d+", s) else 0
env = dict(I2S=str, S2I=integer, StringHash=fake_hash, StringLength=len, SubString=lambda s,a,b:s[a:b],
           BlzBitXor=lambda a,b:a^b, IMinBJ=min, ModuloInteger=lambda a,b:a%b,
           Player=lambda i:i, GetPlayerId=lambda p:p, GetLocalPlayer=lambda:0, GetTriggerPlayer=lambda:0,
           IsPlayerObserver=lambda p:p==12, GetPlayerName=lambda p:account if p==0 else str(p),
           GetPlayerController=lambda p:p not in (4,12), GetPlayerSlotState=lambda p:p!=6,
           FF_IsBotName=lambda n:n=="3", PLAYER_SLOT_STATE_PLAYING=True, MAP_CONTROL_USER=True,
           DestroyTimer=noop, GetExpiredTimer=noop, s__File_open=lambda p:p, s__File_close=noop,
           s__File_readAndClose=lambda p:files.get(p,""),
           s__File_write=lambda p,data:files.__setitem__(p,data),
           BlzSendSyncData=lambda tag,data:packets.append((tag,data)),
           BlzGetTriggerSyncPrefix=lambda:packets[-1][0], BlzGetTriggerSyncData=lambda:packets[-1][1],
           CAS_ended=False, CAS_bank=10000, CAS_liability=0, LoanCollect=noop, PF_Log=noop,
           WalletAccount=account, CAS_Render=noop, Preload=rows.append, ExecuteFunc=noop,
           FF_Sanitize=lambda s:s, GetEventPlayerChatString=lambda:"-casino", jdiv=translator["jdiv"])
for name in ("WalletLoad","WalletSave","WalletReceive","WalletBroadcast","LoanRecord","LoanLegacyRecord",
             "FFPS_Field","FGA_Number","PK_Eligible","CAS_User","CAS_Chat","CAS_Reserve","CAS_Flush",
             "CasinoWalletDelta","PF_Export","PF_CasinoSlot","WalletText"):
    tree = translator["Division"]().visit(ast.parse(translator["translate"](name)))
    exec(compile(ast.fix_missing_locations(tree), name, "exec"), env)


def new_match():
    for name in re.findall(r"(?m)^\s*\w+ array (\w+)", script.split("\nendglobals",1)[0]):
        env[name] = defaultdict(int)
    env.update(WalletSyncPrefix="FFWallet1", WalletBalance=-1, LoanLocalRecord="", CAS_liability=0)
    env["FF_gr_participant"][1] = True
    env["udg_player_active"][1] = True
    packets.clear()
    rows.clear()


new_match()
for slot in (0,1,12):
    assert env["PK_Eligible"](slot)
env["SoloSub_playerForObserver"][12] = 1
assert env["PK_Eligible"](12)
for slot in (-1,3,4,6,24):
    assert not env["PK_Eligible"](slot)
env["CAS_Chat"]()
assert env["CAS_view"][1] == 1
env["WalletLoad"]()
assert packets[-1][0] == "FFWalletNew" and env["WalletText"]() == "Wallet: 1000"
env["WalletReceive"]()
assert env["CAS_ready"][1] and env["CAS_Reserve"](1,1,100,100)
env["WalletReceive"]()
env["PF_Export"]()
assert "casino,enabled=1,starting_wallet=1000" in rows
assert "wallet,1,known=1,opening=1000,balance=900,starting_grant=1000" in rows
assert env["CAS_escrow"][1] == 100
for balance in (900,0,1000):
    env["WalletBalance"] = balance
    env["WalletSave"]()
    new_match()
    env["WalletLoad"]()
    assert packets[-1][0] == "FFWallet1"
    env["WalletReceive"]()
    env["PF_Export"]()
    assert f"wallet,1,known=1,opening={balance},balance={balance},starting_grant=0" in rows
    if balance == 0:
        assert not env["CAS_Reserve"](1,1,10,10)

# A damaged nonempty save is unavailable and receives no starter grant.
files[env["WalletPath"]] = "invalid"
new_match()
env["WalletLoad"]()
assert not packets
env["PF_Export"]()
assert "wallet,1,known=0" in rows and env["WalletText"]() == "Wallet: unavailable"
assert not any(row.startswith("wallet,2,") for row in rows)
assert all(len(row) <= 240 for row in rows)
assert 'BlzTriggerRegisterPlayerSyncEvent(sync, Player(id), "FFWalletNew", false)' in script
print("Passed Wallet initialization, saved balances, duplicate sync, wager, casino access, and result records.")
