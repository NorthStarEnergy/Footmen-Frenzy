"""Exercise RC22 accounting, export, UI pagination and final snapshots with native mocks."""
import ast
from collections import defaultdict
from pathlib import Path
import json
import re
import struct
import sys

from metrics import METRICS
from prepare import ROOT, FUNCTION, digest

src = Path(sys.argv[1]) / "projects/799x/src"
script = (src/"war3map.j").read_text("utf8")
functions = {m[1]:m[0] for m in FUNCTION.finditer(script)}
translator = {"ast":ast,"re":re,"FUNCTIONS":functions}
history = (ROOT/"development/footmen/casino-v1/test_casino.py").read_text("utf8")
exec(history[history.index("def expr("):history.index("NOW =")],translator)

env = {name:defaultdict(int) for name in re.findall(r"^\s*\w+ array (\w+)",script.split("\nendglobals")[0],re.M)}
def noop(*_):
    pass
def put(table,key,id,value):
    table[key,id] = value
def get(table,key,id):
    return table.get((key,id),0)
def has(table,key,id):
    return (key,id) in table

balances = defaultdict(int,{1:1000,2:100,3:100})
events = []
env.update(PF_data={},PF_prices={},PF_final={},PF_history={},PF_frozen=False,PF_dirty=False,FF_gameTimer=0,
           jdiv=translator["jdiv"],SaveInteger=put,LoadInteger=get,SaveStr=put,LoadStr=get,HaveSavedInteger=has,
           IMinBJ=min,IMaxBJ=max,I2S=str,R2I=int,StringLength=len,ModuloInteger=lambda n,d:n%d,TimerGetElapsed=lambda _:31,
           GetPlayerState=lambda p,_:balances[p],PLAYER_STATE_RESOURCE_GOLD=0,ConvertedPlayer=lambda s:s,Player=lambda i:i+1,
           FFR4_PoolingAllowed=lambda:True,FFR4Pro=True,IsPlayerAlly=lambda a,b:True,SoloSub_CanReceiveGold=lambda s:True,
           Preload=events.append,FF_PRELOAD_MAX=240,PF_exportSlot=1,PF_exportStart=0,FF_st_Tech=lambda *_:0,
           CAS_ended=False,CAS_bank=10000,CAS_liability=0,PK_Eligible=lambda _:True,CAS_Flush=noop,LoanAward=noop,
           FF_us_Id2S=lambda id:id.to_bytes(4,"big").decode("ascii"),GetPlayerScore=lambda *_:0,
           GetHeroLevel=lambda _:0,FF_st_RaceLevel=lambda _:0,FF_ST_DMG_OUT=0,FF_ST_DMG_BLD=1,FF_ST_DMG_IN=2)
for constant in re.findall(r"\bPLAYER_SCORE_\w+",functions["PF_Live"]):
    env[constant] = constant
names = ["PF_Average","PF_Use","PF_Log","PF_Transfer","PF_ObserveBalance","FFP_Transfer","PF_ExportJournal",
         "PF_ExportSlot","PF_Category","PF_Schema","PF_Live","PF_Number","PF_TeamValue","FF_gr_IsMember",
         "PF_Economy","CAS_Reserve","CAS_Settle","CAS_Credit","PF_Paginate","PF_ResultsView","PF_HeroExperience","PF_Freeze"]
for name in names:
    tree = translator["Division"]().visit(ast.parse(translator["translate"](name)))
    exec(compile(ast.fix_missing_locations(tree),name,"exec"),env)

# Simulate both synchronous gold-change callbacks and delayed callbacks; explicit transfer
# accounting and native balance observation must never charge the same debit twice.
def change(player,_,value):
    balances[player] = value
    env["PF_ObserveBalance"](player,value)
env["SetPlayerState"] = change
env["ExecuteFunc"] = lambda name:env[name]()
env["PF_Schema"]()
for s,balance in balances.items():
    put(env["PF_data"],800,s,balance)
for s in [1,2,3]:
    env["FF_gr_participant"][s] = True
env["udg_mode_6v6"] = False
transfer = env["FFP_Transfer"]
assert transfer(1,2,150)==150 and transfer(1,2,50)==50
env["SetPlayerState"] = lambda s,_,v:balances.__setitem__(s,v)
assert transfer(3,2,200)==100 and transfer(3,2,100)==0 and transfer(1,1,50)==0
assert (env["PF_sent"][1],env["PF_received"][2],env["PF_recordedCost"][1],env["PF_recordedCost"][3])==(2,3,200,100)
ids = {k:i for i,(k,_,_) in enumerate(METRICS)}
assert env["PF_Number"](1,ids["avg_sent"])==100 and env["PF_Number"](2,ids["avg_recv"])==100
assert env["PF_TeamValue"](1,ids["avg_sent"])=="100" and env["PF_Number"](3,ids["avg_recv"])==0
assert env["PF_Economy"](1,6)==200 and env["PF_Economy"](2,7)==300

env["CAS_ready"][13] = True
env["CAS_gold"][13] = 500
env["CasinoWalletDelta"] = lambda s,delta:env["CAS_gold"].__setitem__(s,env["CAS_gold"][s]+delta)
assert env["CAS_Reserve"](1,13,100,150) and not env["CAS_Reserve"](1,13,9999,150)
env["CAS_Settle"](1,13,100,150,150)
assert env["PF_staked"][13]==100 and env["PF_returned"][13]==150 and env["PF_gameReturn"][13*4+1]==150

item = int.from_bytes(b"I001","big")
env["PF_Use"](1,2,item,2)
env["FF_us_kothHold"][1] = 10
env["PF_Freeze"]()
env["FF_st_poolOut"][1] = 9999
assert env["PF_Number"](1,ids["pool_out"])==200
env["PF_ExportSlot"]()
assert any("pool_out=200" in row for row in events)
assert "collection,1,item,I001=2" in events
assert sum(",pool_sent," in row for row in events)==2
assert all(len(row)<=240 for row in events)

env["PF_page"]=15
env["PF_Paginate"](29)
assert (env["PF_pages"],env["PF_page"])==(3,2)
env["PF_Paginate"](0)
assert (env["PF_pages"],env["PF_page"])==(1,0)

# Drive the actual result and collection renderers through all twelve slots.
texts, visible = {}, {}
for key in ("PF_board","PF_band","PF_portrait","PF_line","PF_value","PF_icon"):
    env[key] = [f"{key}{i}" for i in range(102)]
for name in ("PF_ProfileView","PF_Card","PF_Clock","PF_Color","FF_gr_SideCount","PF_CareerRecords",
             "DPS_Field","PF_LoadCareer","PF_SaveCareer","PF_CareerAdd","PF_ReceiveHistory"):
    tree = translator["Division"]().visit(ast.parse(translator["translate"](name)))
    exec(compile(ast.fix_missing_locations(tree),name,"exec"),env)
env.update(PF_title="title",PF_subtitle="subtitle",PF_endSecond=420,PF_section=0,PF_page=0,
           PF_MySlot=lambda:1,GetPlayerId=lambda p:p-1,GetLocalPlayer=lambda:1,GetPlayerName=lambda p:f"Player {p}",
           GetPlayerColor=lambda p:p-1,GetHandleId=lambda x:x,PF_Art=lambda i:"art",PF_Name=lambda i:f"Object {i}",
           BlzFrameSetText=lambda f,s:texts.__setitem__(f,s),BlzFrameSetTexture=noop,
           BlzFrameSetVisible=lambda f,s:visible.__setitem__(f,s),FF_Pad2=lambda v:f"{v:02d}",
           FF_gr_SideParticipated=lambda s:True,FF_gr_SideLabel=lambda s:f"Team {s}",PF_local={},
           SubString=lambda s,a,b:(s or "")[a:b],S2I=lambda s:int(s or 0),DPS_ProfileLoaded=True)
for s in range(1,13):
    env["FF_gr_participant"][s] = True
    env["udg_orig_player_name"][s] = f"Player {s}"
for mode in (False,True):
    env["udg_mode_6v6"] = mode
    for winner,verdict in ((1,"Victory"),(2,"Defeat"),(0,"Draw"),(-1,"Victory")):
        env["CAS_winner"]=winner
        for page in range(6):
            texts.clear()
            env["PF_section"]=page
            env["PF_ResultsView"]()
            assert verdict in texts["title"]
            assert sum(v.startswith("Player ") or "Player 1   /   Winner" in v for v in texts.values())==12

# Lifetime storage must survive multi-page collections and repeated saves in the same match.
files = {}
env.update(PF_CareerPath=lambda kind,page:(kind,page),s__File_open=lambda f:f,
           s__File_readAndClose=lambda f:files.get(f,""),s__File_close=noop,
           s__File_write=lambda f,v:files.__setitem__(f,v),PF_frozen=False)
for i in range(45):
    env["PF_Use"](1,2,item+i,2)
env["PF_SaveCareer"](1,2)
snapshot=dict(files)
env["PF_SaveCareer"](1,2)
assert files==snapshot and len(files)==2 and max(map(len,files.values()))==802
env["PF_section"],env["PF_page"]=2,3
env["PF_ProfileView"]()
assert env["PF_pages"]==4 and "lifetime" in texts["PF_value0"]
env["PF_local"],env["PF_careerCount"]={},defaultdict(int)
env["PF_LoadCareer"](2)
assert env["PF_careerCount"][2]==45 and get(env["PF_local"],2,item)==4
env.update(GetTriggerPlayer=lambda:1,BlzGetTriggerSyncData=lambda:"2"+env["DPS_Field"](item)+env["DPS_Field"](7))
env["PF_ReceiveHistory"]()
env["PF_ReceiveHistory"]()
assert env["PF_historyN"][7]==1
events.clear()
env["PF_CareerRecords"](1)
assert any(f"{item}=11" in row for row in events)
assert all(len(row)<=240 for row in events)
assert script.count("set amount = FFP_Transfer(senderId, targetId, requested)")==2
assert "call PF_Transfer(senderId,targetId,amount)" in functions["FFP_Transfer"]
assert "call PF_Open(true)" in functions["DPS_Refresh"] and functions["FF_gr_Poll"].count("call PF_Freeze()")==2
assert "if PF_draw or (PF_winSide == 0 and participated >= 2 and alive == 0)" in functions["FF_gr_Poll"]
assert functions["Trig_END_Actions"].count('call ExecuteFunc("FF_gr_Poll")')==6
assert set(re.findall(r"PLAYER_SCORE_\w+",functions["PF_Live"]))==set(re.findall(r"constant playerscore (PLAYER_SCORE_\w+)",Path(json.loads((ROOT/"tools.local.json").read_text())["common_j"]).read_text()))
meta=json.loads((src/"FF_SOURCE_MANIFEST.json").read_text())
wct=(src/"war3map.wct").read_bytes()
for name in ["globals","FF_Runtime"]:
    b=(src/"source_roundtrip"/(name+".j")).read_bytes()
    assert wct.count(struct.pack("<I",len(b)+1)+b+b"\0")==1
    if name=="FF_Runtime":
        assert {m[1]:m[0] for m in FUNCTION.finditer(b.decode().replace("\r\n","\n"))}=={k:v for k,v in functions.items() if k not in meta["editor_generated_functions"]}
assert meta["compiled_source_sha256"]==digest((src/"war3map.j").read_bytes())
print("Passed actual JASS transfer, debit, casino, snapshot, export and pagination checks. Verified all native score categories and the authoritative editor source.")
