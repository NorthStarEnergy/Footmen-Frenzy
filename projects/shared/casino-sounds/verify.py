"""Exercise the packed casino settlement functions against Warcraft native mocks."""
import ast
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

from prepare import ROOT, solo


def check(path):
    dll = json.loads((ROOT/"tools.local.json").read_text())["stormlib"]
    with solo["Archive"](dll,path) as archive:
        source = archive.read("war3map.j").decode().replace("\r\n","\n")
        functions = solo["functions"](source)
        for key in ("CasinoUI\\panel.blp","PokerUI\\card51.blp"):
            assert len(archive.read(key)) > 1024
        if "FFA_CasinoFinish" in functions:
            editor = archive.read("war3map.wct")
            for key in ("FFA_CasinoFinish","MK_Pay","CAS_ResultSound","WalletReceive"):
                assert functions[key].encode() in editor.replace(b"\r\n",b"\n")
            assert "CP_PreviewInit" not in source
            assert 'ExecuteFunc("FFA_CasinoFinish")' in functions["SKCheckVictory"] and 'ExecuteFunc("FFA_CasinoFinish")' in functions["SoloFootsPrepareEndGame"]
    harness = ast.parse((ROOT/"development/footmen/casino-v1/test_casino.py").read_text("utf8"))
    harness.body = [n for n in harness.body if getattr(n,"name","") in {"expr","translate","Division","jdiv"}]
    engine = dict(re=re,ast=ast,FUNCTIONS=functions)
    exec(compile(harness,"JASS translator","exec"),engine)
    calls = []
    env = dict(Player=int,StartSoundForPlayerBJ=lambda p,sound:calls.append((p,sound)),CAS_winSound="gold",
               CAS_lossSound="click",jdiv=engine["jdiv"],I2S=str,IMaxBJ=max,IMinBJ=min,IAbsBJ=abs,
               ModuloInteger=lambda a,b:a%b,CAS_Settle=lambda *a:None,CAS_Credit=lambda *a:None,
               MK_Title=str,GetPlayerName=str,PK_TableChanged=lambda t:None,PK_SeatName=lambda t,s:str(s))
    for key in re.findall(r"(?m)^\s*\w+ array (\w+)",source):
        env[key] = defaultdict(int)
    def load(*names):
        for key in names:
            tree = engine["Division"]().visit(ast.parse(engine["translate"](key)))
            exec(compile(ast.fix_missing_locations(tree),key,"exec"),env)
    def expect(expected):
        assert calls == expected,(path.name,expected,calls)
        calls.clear()
    load("CAS_ResultSound","MK_Pay","BJ_Payout","BJ_Finish","DU_Finish")
    for ticket,(win,refund,expected) in enumerate([(True,False,[(3,"gold")]),(False,False,[(3,"click")]),(False,True,[])]):
        env["MK_player"][ticket]=4
        env["MK_stake"][ticket]=50
        env["MK_return"][ticket]=110
        env["MK_Pay"](ticket,win,refund)
        env["MK_Pay"](ticket,win,refund)
        expect(expected)
    for dealer,points,refund,expected in [(19,20,False,"gold"),(20,19,False,"click"),(20,20,False,None),(20,19,True,None)]:
        if "BJ_owner" in env:
            env["BJ_owner"][2]=3
        env["BJ_bet"][4]=50
        env["BJ_state"][4]=2
        env["BJ_total"][4]=points
        env["BJ_dealerTotal"][0]=dealer
        env["BJ_Finish"](0,refund)
        env["BJ_Finish"](0,refund)
        expect([(2,expected)] if expected else [])
    for winner,expected in [(2,[(1,"gold"),(6,"click")]),(7,[(6,"gold"),(1,"click")]),(0,[])]:
        env["DU_n"]=1
        for key,value in [("DU_state",2),("DU_from",2),("DU_to",7),("DU_target",2),("DU_stake",50),("DU_ffa",True)]:
            env[key][1]=value
        env["DU_Finish"](winner,True)
        env["DU_Finish"](winner,True)
        expect(expected)
    if "OP_Finish" in functions:
        load("OP_Finish","OP_AwardPots")
        env.update(OP_Button=0,PK_Eligible=lambda v:True)
        for v,total,score in [(2,30,3),(3,50,2),(4,50,1)]:
            env["OP_Dealt"][v]=env["OP_Live"][v]=True
            env["PK_Stack"][v]=100
            env["PK_Total"][v]=total
            env["OP_Score"][v]=score
        env["OP_Finish"]()
        expect([(2,"gold"),(3,"click"),(4,"click")])
    if "PK_PlayerAt" in functions:
        load("PK_End","PK_PlayerAt")
        for winner,expected in [(0,[(2,"gold"),(7,"click")]),(1,[(7,"gold"),(2,"click")]),(2,[])]:
            env["PK_Turn"][2]=0
            env["PK_Guest"][2]=8
            env["PK_Total"][4]=35
            env["PK_Total"][5]=20
            env["PK_End"](2,winner,"hand")
            expect(expected)
    else:
        prefix = "House" if "HousePK_End" in functions else ""
        load(prefix+"PK_End")
        for winner,expected in [(0,"gold"),(1,"click"),(2,None)]:
            env[prefix+"PokerBuyIn"][3]=50
            for i in [6,7]:
                env[prefix+"PK_Total"][i]=10
                env[prefix+"PK_Stack"][i]=40
            env[prefix+"PK_End"](3,winner,"hand")
            expect([(3,expected)] if expected else [])
    print(path.name,"passed wager outcomes, recipient routing, pushes, refunds and repeat settlement.")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        check(Path(arg))
