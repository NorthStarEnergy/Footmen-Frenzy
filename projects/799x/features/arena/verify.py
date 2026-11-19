"""Run the staged duel JASS with native mocks and check its binary terrain/pathing."""
import ast
from collections import defaultdict
import json
import re
from types import SimpleNamespace

from prepare import Archive, ROOT, WORK


def check_rounds(src):
    jass = (src / "war3map.j").read_text(encoding="utf-8", errors="surrogateescape")
    functions = dict((m[1], m[0]) for m in re.finditer(r"(?ms)^function (AR_\w+|CAS_Reserve|CAS_Credit|CAS_Flush|LoanAward)\b.*?^endfunction", jass))
    # Use the same JASS expression translator as the casino accounting regression checks.
    translator = dict(ast=ast, re=re, FUNCTIONS=functions)
    existing = (ROOT / "development/footmen/casino-v1/test_casino.py").read_text()
    exec(existing[existing.index("def expr("):existing.index("NOW =")], translator)
    noop = lambda *_: None
    e = {"jdiv": translator["jdiv"]}
    for name in functions:
        tree = translator["Division"]().visit(ast.parse(translator["translate"](name)))
        exec(compile(ast.fix_missing_locations(tree), name, "exec"), e)
    for kind, name in re.findall(r"^\s*(\w+) array (\w+)", jass.split("\nendglobals")[0], re.M):
        e[name] = defaultdict(int if kind == "integer" else lambda: None)

    players = {0, 1, 2}
    units, scrolls, messages, rolls, flags = [], [], [], [], {}
    def spawn(owner, raw, x, y, facing):
        u = SimpleNamespace(owner=owner, raw=raw, x=x, y=y, facing=facing, alive=True)
        units.append(u)
        return u
    def item(raw, x, y):
        i = SimpleNamespace(raw=raw, removed=False)
        scrolls.append(i)
        return i
    def accept(s):
        e["AR_Accept"](s,e["AR_offer"])
    def engage(stake=100):
        e["CAS_amount"][1] = stake or 50
        e["AR_Invite"](1,stake)
        assert e["AR_state"] == 1 and e["AR_seat"][1] == 2
        accept(3)
        assert e["AR_state"] == 1
        accept(2)
    for name in ("DestroyGroup", "DisplayTimedTextToPlayer", "SetUnitColor", "RemoveGuardPosition",
                 "SuspendHeroXP", "SelectHeroSkill", "SetUnitUseFood", "SetItemPawnable", "SetItemDroppable",
                 "SetItemDropOnDeath", "IssuePointOrder", "TimerStart", "PauseTimer", "DestroyTrigger",
                 "EnableTrigger", "DisableTrigger", "FogModifierStart", "FogModifierStop", "DestroyFogModifier",
                 "TriggerRegisterUnitEvent", "TriggerAddAction", "TriggerRegisterEnterRectSimple",
                 "TriggerRegisterAnyUnitEventBJ", "UnitRemoveAbility"):
        e[name] = noop
    for name in re.findall(r"\b(?:ALLIANCE_|EVENT_|FOG_OF_WAR_|UNIT_TYPE_)\w+", "\n".join(functions.values())):
        e[name] = name
    def wallet_delta(slot, delta):
        e["CAS_gold"][slot] += delta
    e.update(AR_state=0, AR_stake=0, AR_offer=0, AR_deaths=None, AR_flagCount=0, FF_gameTimer=0, CAS_ended=False,
             CAS_bank=0,CAS_liability=0,PF_Log=noop,CasinoWalletDelta=wallet_delta,
             LoanSave=noop,LoanCollect=noop,PK_Eligible=lambda p:p in players,I2S=str,IMaxBJ=max,IMinBJ=min,
             Player=lambda i:i, GetPlayerId=lambda p:p, GetLocalPlayer=lambda:23,
             CAS_User=lambda s:s-1 in players, IsPlayerObserver=lambda _:False,
             GetPlayerController=lambda _:1, MAP_CONTROL_USER=1, GetPlayerColor=lambda p:p,
             AR_Tell=lambda s,m:messages.append((s,m)), CAS_Name=lambda s:f"P{s}",
             TimerGetElapsed=lambda _:e["now"], now=0, R2I=int, ModuloInteger=lambda a,b:a%b,
             CreateTimer=object, CreateTrigger=object, CreateGroup=list, Rect=lambda *r:r,
             CreateFogModifierRect=lambda *_:object(), bj_PLAYER_NEUTRAL_EXTRA=26, bj_PLAYER_NEUTRAL_VICTIM=25,
             GetPlayerAlliance=lambda a,b,f:flags.get((a,b,f),False),
             SetPlayerAlliance=lambda a,b,f,v:flags.__setitem__((a,b,f),v),
             GroupEnumUnitsOfPlayer=lambda g,p,_:g.__setitem__(slice(None),[u for u in units if u.owner==p and not getattr(u,"removed",False)]),
             FirstOfGroup=lambda g:g[0] if g else None, GetRandomInt=lambda a,b:rolls.append((a,b)) or e["roll"],
             CreateUnit=spawn, GetUnitX=lambda u:u.x, GetUnitY=lambda u:u.y, GetUnitName=lambda u:u.raw,
             CreateItem=item, UnitAddItem=lambda h,i:True, GetUnitTypeId=lambda u:u.raw if u else 0,
             IsUnitType=lambda u,_:not u.alive, GetWidgetLife=lambda u:100 if u.alive else 0,
             RemoveUnit=lambda u:setattr(u,"removed",True) if u else None,
             RemoveItem=lambda i:setattr(i,"removed",True), RMaxBJ=max, RMinBJ=min,
             SetUnitPosition=lambda u,x,y:(setattr(u,"x",x),setattr(u,"y",y)), IssueImmediateOrder=noop,
             RectContainsCoords=lambda r,x,y:r[0]<=x<=r[2] and r[1]<=y<=r[3])
    e["AR_Init"]()
    e["CAS_ready"].update({1:True,2:True})
    e["CAS_gold"].update({1:1000,2:1000})
    # Existing escrow from other casino games must survive arena settlement.
    e["CAS_escrow"].update({1:15,2:25})
    wallet = lambda: (e["CAS_gold"][1],e["CAS_gold"][2])
    escrow = lambda: (e["CAS_escrow"][1],e["CAS_escrow"][2])
    assert len(set(e["AR_roster"].values())) == 6
    for roll in range(6):
        e["roll"] = roll
        before = wallet()
        engage()
        assert wallet() == (before[0]-100,before[1]-100) and escrow() == (115,125)
        accept(2)
        assert escrow() == (115,125)
        assert e["AR_state"] == 2 and len(rolls) == roll+1
        assert flags[26,0,"ALLIANCE_SHARED_ADVANCED_CONTROL"] and flags[25,1,"ALLIANCE_SHARED_CONTROL"]
        assert not e["GetPlayerAlliance"](26,25,"ALLIANCE_PASSIVE")
        l, r = e["AR_hero"][0], e["AR_hero"][1]
        assert l.raw == r.raw == e["AR_roster"][roll] and l.x == -r.x and l.y == r.y
        assert len(units) == 82 and [i.raw for i in scrolls] == ["sror","sror"]
        for i in range(40):
            a, b = e["AR_foot"][i], e["AR_foot"][40+i]
            assert a.raw == b.raw == "hfoo" and a.x == -b.x and a.y == b.y
            assert a.owner == l.owner and b.owner == r.owner
        l.x, r.y = -3000, 9000
        e["AR_Tick"]()
        assert l.x == -976 and r.y == 6864
        for i in range(40):
            e["AR_foot"][i].alive = False
        e["AR_Tick"]()
        assert e["AR_state"] == 2
        if roll < 2:
            (l,r)[roll].alive = False
            e["AR_Tick"]()
            assert f"P{2-roll} wins" in messages[-1][1]
        elif roll == 2:
            e["AR_Withdraw"](2)
            assert "P1 wins" in messages[-1][1]
        elif roll == 3:
            players.remove(0)
            e["AR_Tick"]()
            players.add(0)
            assert "P2 wins" in messages[-1][1]
        elif roll == 4:
            l.alive = r.alive = False
            e["AR_Tick"]()
            assert "drawn" in messages[-1][1]
        else:
            e["CAS_ended"] = True
            e["AR_Tick"]()
            e["CAS_ended"] = False
        assert e["AR_state"] == 0 and all(u.removed for u in units) and all(i.removed for i in scrolls)
        assert not any(flags.values()) and e["AR_flagCount"] == 0
        gain = [-100,100,100,-100,0,0][roll]
        assert wallet() == (before[0]+gain,before[1]-gain)
        assert escrow() == (15,25) and e["CAS_bank"] == e["CAS_liability"] == 0
        e["AR_End"](1,"late death")
        assert wallet() == (before[0]+gain,before[1]-gain)
        units.clear()
        scrolls.clear()
    assert e["PF_gameStake"][7] == e["PF_gameStake"][11] == 600
    assert sum(e["PF_gameReturn"].values()) == 1200
    before = wallet()
    e["AR_Invite"](1,100)
    e["now"] = 30
    accept(2)
    assert e["AR_state"] == 0 and not units and wallet() == before
    e["AR_Invite"](1,100)
    old_offer = e["AR_offer"]
    e["AR_Withdraw"](2)
    assert e["AR_state"] == 0 and wallet() == before
    e["AR_Invite"](1,100)
    e["AR_Accept"](2,old_offer)
    assert e["AR_state"] == 1 and wallet() == before
    e["CAS_amount"][1] = 500
    e["CAS_amount"][2] = 10
    e["CAS_gold"][2] = 99
    accept(2)
    assert e["AR_state"] == 1 and escrow() == (15,25) and wallet() == (before[0],99)
    e["CAS_gold"][2] = before[1]
    accept(2)
    assert e["AR_stake"] == 100 and escrow() == (115,125)
    e["AR_Withdraw"](1)
    assert wallet() == (before[0]-100,before[1]+100)
    e["CAS_amount"][1] = 100
    e["AR_Invite"](1,100)
    e["CAS_gold"][1] = 9
    before = wallet()
    accept(2)
    assert e["AR_state"] == 0 and wallet() == before and escrow() == (15,25)
    e["AR_Invite"](1,100)
    assert e["AR_state"] == 0 and wallet() == before
    e["CAS_gold"][1] = 1000
    before = wallet()
    e["UnitAddItem"] = lambda hero,scroll:hero.owner == 26
    engage()
    assert e["AR_state"] == 0 and all(u.removed for u in units) and not any(flags.values())
    assert wallet() == before and escrow() == (15,25)
    reserve = e["CAS_Reserve"]
    e["CAS_Reserve"] = lambda game,s,stake,liability: s != 2 and reserve(game,s,stake,liability)
    engage()
    assert e["AR_state"] == 0 and wallet() == before and escrow() == (15,25)
    e["UnitAddItem"] = lambda h,i:True
    e["CAS_Reserve"] = reserve
    e["CAS_ready"][1] = e["CAS_ready"][2] = False
    engage(0)
    assert e["AR_state"] == 2 and escrow() == (15,25)
    e["AR_Withdraw"](2)
    assert wallet() == before
    print("Arena rounds and Wallet accounting passed under native mocks, including locked offers, stale accepts, double settlement, funds checks, forfeits and refunds.")


def check_floor(src):
    project = src.parent
    parent = project / "release" / json.loads((project / "project.json").read_text())["release"]
    dll = json.loads((WORK / "tools.local.json").read_text())["stormlib"]
    with Archive(dll, parent) as a:
        old = a.read("war3map.wpm")
        new = (src / "war3map.wpm").read_bytes()
        assert new[16:len(old)] == old[16:]
        for y in range(256,384):
            for x in range(256):
                inside = 96 <= x < 160 and 296 <= y < 344
                assert bool(new[16+y*256+x] & 2) != inside
        ground = a.read("war3map.w3e")
        revised = (src / "war3map.w3e").read_bytes()
        assert revised[85:len(ground)] == ground[85:]
        assert (src / "war3map.shd").read_bytes().startswith(a.read("war3map.shd"))
    print("Original terrain, pathing and shadow rows preserved. All 32,768 new pathing cells checked.")


if __name__ == "__main__":
    src = WORK / "projects/799x/src"
    check_rounds(src)
    check_floor(src)
