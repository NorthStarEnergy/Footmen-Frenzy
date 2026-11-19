"""Exercise the staged profile controls, local HUD and account selection using frame mocks."""
import ast
from collections import defaultdict
import re

from prepare import ROOT, WORK

src = WORK / "projects/799x/src"
script = (src / "war3map.j").read_text("utf8")
functions = {m[1]: m[0] for m in re.finditer(r"(?ms)^function (\w+) takes .*?^endfunction", script)}
translator = dict(ast=ast, re=re, FUNCTIONS=functions)
original = (ROOT / "development/footmen/casino-v1/test_casino.py").read_text("utf8")
exec(original[original.index("def expr("):original.index("NOW =")], translator)
env = {k: defaultdict(int) for k in re.findall(r"^\s*\w+ array (\w+)", script.split("\nendglobals")[0], re.M)}
frames, triggers, actions = {}, {}, {}
ui, local, clicked, width, height = object(), 0, None, 1024, 768


def frame(kind, parent):
    handle = object()
    frames[handle] = dict(kind=kind, parent=parent, visible=True, enabled=True, text="")
    return handle


def click(f):
    global clicked
    assert frames[f]["visible"] and frames[f]["enabled"]
    clicked = f
    actions[triggers[f]]()


def setter(name):
    def set_field(f, *values):
        frames[f][name] = values[0] if len(values) == 1 else values
    return set_field


def label(name, index=None):
    handle = env[name] if index is None else env[name][index]
    return frames[handle]["text"]


noop = lambda *_: None
env.update(
    CreateTrigger=object, FFUI_GetRoot=lambda: ui, BlzGetOriginFrame=lambda *_: ui,
    BlzCreateFrameByType=lambda kind, name, parent, *_: frame(kind, parent),
    BlzCreateFrame=lambda kind, parent, *_: frame(kind, parent),
    BlzTriggerRegisterFrameEvent=lambda trig, f, _: triggers.update({f: trig}),
    TriggerAddAction=lambda trig, act: actions.update({trig: act}), BlzFrameSetFocus=noop,
    BlzFrameClearAllPoints=noop, BlzConvertColor=lambda *rgba: rgba, BlzFrameSetTexture=setter("texture"),
    BlzGetLocalClientWidth=lambda: width, BlzGetLocalClientHeight=lambda: height, BlzGetTriggerFrame=lambda: clicked,
    GetTriggerPlayer=lambda: local, GetLocalPlayer=lambda: local, GetPlayerId=lambda p: p, Player=lambda p: p,
    GetPlayerState=lambda p, _: 875+p, GetPlayerName=lambda p: "Player "+str(p+1),
    IsPlayerObserver=lambda p: p >= 12, CAS_winner=0, FF_gr_SideCount=lambda: 0,
    PF_endSecond=0, PF_Clock=lambda _: "0:00", PF_Number=lambda s, k: s*100+k,
    PF_Economy=lambda *_: 0, PF_Average=lambda a, b: a//max(1,b), PF_Name=lambda id: "Unit "+str(id),
    PF_Art=lambda _: "test.blp", LoadInteger=lambda t, k, i: t.get((k, i), 0),
    PF_data={}, PF_local={}, DPS_ProfileLoaded=True, WalletBalance=-1, HUD_walletRead=False,
    HUD_width=-1, HUD_height=-1, DPS_Panel=frame("FRAME", ui),
    FF_US_TECH=1, FF_US_SPELL=2, FF_US_CMD=3, FF_US_TOWER=4, FF_us_CountKey=lambda s, k: s*10+k,
    I2R=float, I2S=str, RMaxBJ=max, IMinBJ=min, IMaxBJ=max, ModuloInteger=lambda a,b: a%b, jdiv=translator["jdiv"],
)
for method, field in {"Alpha":"alpha", "TextColor":"color", "VertexColor":"tint", "Level":"level", "Point":"point",
                      "AbsPoint":"abs", "Size":"size", "Font":"font", "TextAlignment":"alignment",
                      "Text":"text", "Enable":"enabled", "Visible":"visible"}.items():
    env["BlzFrameSet"+method] = setter(field)
for name in ("FRAMEPOINT_TOPLEFT", "FRAMEPOINT_TOP", "FRAMEEVENT_CONTROL_CLICK", "ORIGIN_FRAME_GAME_UI",
             "TEXT_JUSTIFY_MIDDLE", "TEXT_JUSTIFY_RIGHT", "TEXT_JUSTIFY_LEFT", "PLAYER_STATE_RESOURCE_GOLD"):
    env[name] = name
for name in ("PF_Schema", "PF_MySlot", "HUD_Text", "HUD_WalletValue", "HUD_ShowWallet", "HUD_Refresh", "HUD_Create",
             "PF_Text", "PF_Button", "PF_CreateProfile", "PF_AlignNumber", "PF_Create", "PF_Open", "PF_Click",
             "PF_Render", "PF_RenderNavigation", "PF_Row", "PF_StatRow", "PF_Columns", "PF_ProfileView", "PF_ResultsView"):
    tree = translator["Division"]().visit(ast.parse(translator["translate"](name)))
    exec(compile(ast.fix_missing_locations(tree), name, "exec"), env)

env["PF_Schema"]()
env["HUD_Create"]()
env["PF_Create"]()
hud = frames[env["HUD_root"]]
assert hud["parent"] is ui and hud["level"] > frames[env["PF_root"]]["level"]
assert label("HUD_wallet") == "Loading" and label("HUD_gold") == "875"
env["HUD_walletRead"] = True
env["HUD_ShowWallet"]()
assert label("HUD_wallet") == "Unavailable"
for amount in (0, 1000, 2147483647):
    env["WalletBalance"] = amount
    env["HUD_ShowWallet"]()
    assert label("HUD_wallet") == str(amount)
for width, height in [(1024,768), (1920,1080), (3440,1440)]:
    env["HUD_Refresh"]()
    _, x, y = hud["abs"]
    assert abs(x-(0.4-0.3*width/height)-0.012) < 1e-8
    assert y-hud["size"][1] > 0.526 and x+hud["size"][0] < 0.30
for handle in ("HUD_wallet", "HUD_gold"):
    assert frames[env[handle]]["font"][:2] == ("CasinoUI\\Bold.ttf", 0.019)
local = 16
env["HUD_Refresh"]()
assert label("HUD_gold") == "--"
env["SoloSub_playerForObserver"][local] = 2
env["HUD_Refresh"]()
assert label("HUD_gold") == "876" and label("HUD_wallet") == str(amount)
local = 0
env["DPS_Prior"][3] = 50
env["PF_Open"](False)
assert label("PF_line",1) == "Hero kills" and label("PF_value",1) == "129" and label("PF_extra",1) == "179"
for index in range(11):
    click(env["PF_menu"][index])
    assert label("PF_sectionTitle") == env["PF_sectionName"][env["PF_menuOrder"][index]]
    assert env["PF_page"] == 0
    for page in range(1, env["PF_pages"]):
        click(env["PF_next"])
        assert env["PF_page"] == page and label("PF_line",0)
    if env["PF_page"]:
        click(env["PF_prev"])
env["PF_careerCount"][1] = 1
env["PF_local"][11,0] = 25
env["PF_local"][1,25] = 4
env["PF_data"][11,25] = 2
click(env["PF_menu"][4])
assert [label(name,0) for name in ("PF_line","PF_value","PF_extra")] == ["Unit 25","2","6"]
assert frames[env["PF_icon"][0]]["visible"]
click(env["PF_back"])
assert not frames[env["PF_root"]]["visible"] and hud["visible"]
env["PF_Open"](True)
for index, heading in enumerate(("Level","Unit score","Pooled","Trained","Gold mined","Deaths")):
    if index:
        click(env["PF_tab"][index])
    assert label("PF_board",1) == heading
assert not any(frames[env["PF_menu"][i]]["visible"] for i in range(11))
assert all(not label("PF_extra",i) for i in range(9))
assert hud["visible"] and 'BlzFrameSetVisible(HUD_' not in script
print("Passed HUD ownership, zero/max balances, three aspect ratios, all profile sections and pages, lifetime values, and results navigation.")
