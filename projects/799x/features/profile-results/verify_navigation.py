"""Exercise the registered frame events on each staged map with Warcraft natives mocked."""
import ast
from collections import defaultdict
from pathlib import Path
import re
import sys

from prepare import ROOT, FUNCTION

script = Path(sys.argv[1]).read_text("utf8")
funcs = {m[1]: re.sub(r"(?m)^[ \t]*//[^\n]*", "", m[0]) for m in FUNCTION.finditer(script)}
t = dict(ast=ast, re=re, FUNCTIONS=funcs)
src = (ROOT/"development/footmen/casino-v1/test_casino.py").read_text("utf8")
exec(src[src.index("def expr("):src.index("NOW =")],t)

frames, handlers, labels, enabled, visible, removed = {}, {}, {}, {}, {}, []
player = 1
clicked = None
def noop(*args):
    pass
def register(trigger, frame, event):
    assert event == "CLICK"
    frames[frame] = trigger
def click(frame, who=1):
    global clicked, player
    player, clicked = who, frame
    assert who not in removed, "client was removed before it could click"
    assert enabled.get(frame,True) and visible.get(frame,True)
    handlers[frames[frame]]()
    player = 1
def finish(p, *args):
    removed.append(p)

env = {k:defaultdict(int) for k in re.findall(r"^\s*\w+ array (\w+)",script.split("\nendglobals")[0],re.M)}
env.update(dict(
    CreateTrigger=object, BlzCreateFrame=lambda *args:object(), BlzCreateFrameByType=lambda *args:object(),
    BlzTriggerRegisterFrameEvent=register, TriggerAddAction=lambda trig,fn:handlers.update({trig:fn}),
    BlzGetOriginFrame=noop, BlzFrameSetLevel=noop, BlzFrameSetAbsPoint=noop, BlzFrameSetSize=noop,
    BlzFrameSetPoint=noop, BlzFrameSetTextColor=noop, BlzFrameSetAlpha=noop, BlzConvertColor=noop,
    BlzFrameSetTexture=noop, BlzFrameSetFocus=noop, PF_Text=lambda *args:object(),
    BlzFrameSetText=lambda f,v:labels.update({f:v}), BlzFrameSetEnable=lambda f,v:enabled.update({f:v}),
    BlzFrameSetVisible=lambda f,v:visible.update({f:v}), FRAMEEVENT_CONTROL_CLICK="CLICK", FRAMEPOINT_TOP=0,
    FRAMEPOINT_TOPLEFT=0, ORIGIN_FRAME_GAME_UI=0, GetTriggerPlayer=lambda:player, GetLocalPlayer=lambda:1,
    GetPlayerId=lambda p:p-1, BlzGetTriggerFrame=lambda:clicked, GetPlayerController=lambda _:1,
    MAP_CONTROL_USER=1, GetPlayerSlotState=lambda _:1, PLAYER_SLOT_STATE_PLAYING=1,
    IsPlayerObserver=lambda _:False, FF_IsBotName=lambda _:False, GetPlayerName=lambda p:f"Player {p}",
    AllowVictoryDefeat=lambda _:True, PLAYER_GAME_RESULT_VICTORY=1, PLAYER_GAME_RESULT_DEFEAT=2,
    CustomVictoryBJ=finish, CustomDefeatBJ=finish, jdiv=t["jdiv"], I2R=float, I2S=str,
    IMinBJ=min, IMaxBJ=max, ModuloInteger=lambda a,b:a%b, PF_MySlot=lambda:1,
    FF_gr_SideCount=lambda:0, PF_Clock=lambda t:"01:00", PF_endSecond=60, PF_winSide=1,
    FF_gr_IsMember=lambda p,s:p==s, CAS_winner=1, PF_frozen=True, PF_visible=True, PF_results=True,
    PF_section=0, PF_page=0, DPS_Panel=object(), PF_ProfileView=noop
))
for name in ("PF_Schema","PF_Button","PF_Click","PF_Render","PF_ResultsView","PF_Create","PF_NativeResult"):
    tree = t["Division"]().visit(ast.parse(t["translate"](name)))
    exec(compile(ast.fix_missing_locations(tree),name,"exec"),env)
env["PF_Schema"]()
env["PF_Create"]()
env["FF_gr_participant"][1] = True
env["PF_Render"]()
assert not enabled[env["PF_continue"]]
assert "PLAYER_STATE_GAME_RESULT" not in funcs["Trig_END_Actions"]
if "FFEnd_Resolve" in funcs:
    assert "PLAYER_STATE_GAME_RESULT" not in funcs["FFEnd_Resolve"]

for won in (True, False):
    removed.clear()
    env["PF_verdict"][1] = 0
    env.update(PF_visible=True,PF_results=True,PF_section=0,PF_page=0)
    env["PF_Render"]()
    click(env["PF_tab"][1])
    assert labels[env["PF_board"][1]]=="Unit score"
    env["PF_NativeResult"](1,won,"defeat")
    assert not removed and enabled[env["PF_continue"]]
    click(env["PF_next"])
    assert labels[env["PF_board"][1]]=="Heroes used"
    click(env["PF_prev"])
    assert labels[env["PF_board"][1]]=="Unit score"
    for tab, heading in [(2,"Pooled"),(3,"Trained"),(4,"Gold mined"),(5,"Deaths"),(0,"Level")]:
        click(env["PF_tab"][tab])
        assert labels[env["PF_board"][1]]==heading
    click(env["PF_tab"][2],2)  # Another client cannot switch my view.
    assert env["PF_section"]==0
    click(env["PF_continue"])
    assert removed==[1] and not env["PF_visible"] and env["PF_verdict"][1]==-1
    env["PF_NativeResult"](1,won,"defeat")
    assert removed==[1] and env["PF_verdict"][1]==-1
print("Registered controls changed visible columns before and after the verdict, and Continue applied it once.")
