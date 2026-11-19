"""Prepare the RC24 payloads from the verified RC21 archive, including editable WCT."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys

FEATURE = Path(__file__).resolve().parent
ROOT = FEATURE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from map_archive import Archive
from build_799x_items_catalog import parse_objects, quoted
from restore_rc6_item_text import strings
from metrics import METRICS, schema

BASE_HASH = "8032316d738ffd50e0ace345d92f67864fd1b518a9100e66b076883d9d542987"
FUNCTION = re.compile(r"^function (\w+) takes[^\n]*\n[\s\S]*?^[ \t]*endfunction", re.M)
digest = lambda data: hashlib.sha256(data).hexdigest()

def read(name):
    return (FEATURE / name).read_text(encoding="utf8").strip("\n")

def generate_prices(archive):
    catalog = json.loads((ROOT/"development/footmen/799x-backport/item-wiki/dist/data.json").read_text("utf8"))
    old_prices = {r["id"]: r.get("cost") for r in catalog["items"]}
    wts = strings(archive.read("war3map.wts"))
    lines = []
    for ext, cost, art in [("w3t","igol","iico"),("w3u","ugol","uico"),("w3q","gglb","gar1")]:
        rows = {}
        for name in ["war3mapSkin."+ext, "war3map."+ext]:
            try:
                raw = archive.read(name)
            except KeyError:
                continue
            for oid, row in parse_objects(raw,wts,ext=="w3q").items():
                rows.setdefault(oid,{"parent":row["parent"],"fields":{}})["fields"].update(row["fields"])
        def get(oid, field):
            row = rows.get(oid,{})
            for level in (0,1):
                if (field,level) in row.get("fields",{}):
                    return row["fields"][field,level]
            parent = row.get("parent",oid)
            if parent != oid:
                return get(parent,field)
            if ext == "w3t" and field == cost:
                return old_prices.get(oid)
            return None
        for oid in sorted(rows):
            for key, field in [(1,cost),(2,"gglm"),(3,art)]:
                value = get(oid,field)
                if value is None:
                    continue
                if key == 3 and isinstance(value,str) and value:
                    lines.append(f"    call SaveStr(PF_prices,3,'{oid}',{quoted(value.split(',')[0])})")
                elif key != 3 and isinstance(value,(float,int)):
                    lines.append(f"    call SaveInteger(PF_prices,{key},'{oid}',{int(value)})")
    actions = {"gold_out":"Gold debit","pool_sent":"Sent to","pool_received":"Received from","item":"Bought","hire":"Hired","research":"Researched","upgrade":"Upgraded","hero":"Hero selected","train":"Trained","construct":"Built","stake":"Casino stake","return":"Casino return","research_start":"Research started","research_cancel":"Research cancelled","train_start":"Training started","train_cancel":"Training cancelled","construct_start":"Construction started","construct_cancel":"Construction cancelled"}
    actions["skill"] = "Learned"
    actions["research"] = "Research complete"
    for key, name in actions.items():
        lines.append(f'    call SaveStr(PF_prices,4,StringHash("{key}"),"{name}")')
    for i, name in enumerate(["Stats","Heroes","Items","Units","Skins","Build order","Casino","Usage","","","Overview","Scores","Transfers","Army","Economy","Combat"]):
        lines.append(f'    set PF_tabName[{i}] = "{name}"')
    body, calls = [], []
    for i in range(0,len(lines),100):
        name = f"PF_ObjectData{i//100}"
        body += ["function "+name+" takes nothing returns nothing",*lines[i:i+100],"endfunction",""]
        calls.append(f'    call ExecuteFunc("{name}")')
    body += ["function PF_LoadObjects takes nothing returns nothing",*calls,"endfunction"]
    return "\n".join(body)

def defer_winner_state(script):
    # The result dialog applies the native winner state when the player finishes browsing.
    block = (r"            set udg_X=\d+\n            loop\n                exitwhen udg_X > \d+\n"
             r"                call SetPlayerStateBJ\(ConvertedPlayer\(udg_X\), PLAYER_STATE_GAME_RESULT, 0\)\n"
             r"                set udg_X=udg_X \+ 1\n            endloop\n")
    script, count = re.subn(block, "", script)
    if count != 8:
        raise ValueError(f"Expected eight legacy winner-state loops, found {count}")
    return script

def inline_timer_titles(script, wts):
    # Native countdown dialogs receive their visible label directly, as Colossal does.
    titles = strings(wts)
    def replace_title(match):
        label = titles[int(match[2])].decode("utf8").strip()
        if not label or "\n" in label:
            raise ValueError(f"Invalid countdown title for TRIGSTR_{match[2]}")
        return match[1] + quoted(label)
    return re.sub(r'(\bCreateTimerDialogBJ\(\w+,\s*)"TRIGSTR_(\d+)"', replace_title, script)

def prepare(base,stage):
    if digest(base.read_bytes()) != BASE_HASH:
        raise ValueError("The selected baseline differs from the tested RC21 build")
    src = stage/"projects/799x/src"
    src.mkdir(parents=True,exist_ok=True)
    for name in ["Build-Map.ps1","tools.local.json","tools/map_archive.py","tools/build_map.py","tools/Install-Wc3Map.ps1"]:
        (stage/name).parent.mkdir(exist_ok=True,parents=True)
        shutil.copyfile(ROOT/name,stage/name)
    release = src.parent/"release"/base.name
    release.parent.mkdir(exist_ok=True)
    if not release.exists():
        shutil.copyfile(base,release)
    meta = json.loads((ROOT/"projects/799x/project.json").read_text())
    meta.update(release=base.name,sha256=BASE_HASH)
    (src.parent/"project.json").write_text(json.dumps(meta,indent=2))
    dll = json.loads((ROOT/"tools.local.json").read_text())["stormlib"]
    with Archive(dll,base) as a:
        original = a.read("war3map.j")
        meta = json.loads(a.read("FF_SOURCE_MANIFEST.json"))
        wct = a.read("war3map.wct")
        editor_globals = a.read(r"source_roundtrip\globals.j")
        editor_runtime = a.read(r"source_roundtrip\FF_Runtime.j")
        for name in ["war3map.w3i","war3map.wts"]:
            (src/name).write_bytes(a.read(name).replace(b"v7.9.9X-rc21",b"v7.9.9X-rc24"))
        prices = generate_prices(a)
    def decode(b):
        return b.decode("utf8").replace("\r\n","\n")
    def encode(s,original):
        return (s.replace("\n","\r\n") if b"\r\n" in original else s).encode("utf8")
    j = defer_winner_state(decode(original)).replace("v7.9.9X-rc21","v7.9.9X-rc24")
    j = inline_timer_titles(j, (src/"war3map.wts").read_bytes())
    def replace(old,new):
        nonlocal j
        if j.count(old)!=1:
            raise ValueError((old[:100],j.count(old)))
        j = j.replace(old,new)
    def before(name,code):
        sig = "function "+name+" takes"
        replace(sig,code+"\n\n"+sig)
    def edit(name,old,new):
        f = next(m[0] for m in FUNCTION.finditer(j) if m[1]==name)
        if f.count(old)!=1:
            raise ValueError((name,old[:80],f.count(old)))
        replace(f,f.replace(old,new))
    extra_globals = read("globals.j")
    edit("FFEnd_Resolve","        call SetPlayerStateBJ(ConvertedPlayer(winner), PLAYER_STATE_GAME_RESULT, 0)\n","")
    replace("\nendglobals","\n"+extra_globals+"\nendglobals")
    before("FFGS_SpawnForPlayer",read("tracking.j"))
    edit("FFGS_SpawnForPlayer","        call FFGS_ApplyUnit","        call PF_Use(pn,3,GetUnitTypeId(ffgs_new_unit[i]),1)\n        call PF_Appearance(pn,ffgs_new_unit[i],1)\n        call FFGS_ApplyUnit")
    edit("FFP_Transfer","        set FF_st_poolIn[targetId]", "        call PF_Transfer(senderId,targetId,amount)\n        set FF_st_poolIn[targetId]")
    edit("FFP_Transfer","        call SetPlayerState(sender", "        call PF_ObserveBalance(senderId,available)\n        call SetPlayerState(sender")
    edit("FFP_Transfer","        call SetPlayerState(target", "        call PF_ObserveBalance(senderId,available-amount)\n        call SetPlayerState(target")
    before("Trig_draw_pressed_Func011Func002Func027A",read("settlement.j").split("function PF_Freeze")[0].strip())
    edit("Trig_draw_pressed_Actions",'            call DisplayTextToForce(udg_all_players, "TRIGSTR_10479")','            set PF_draw = true\n            call ExecuteFunc("FF_gr_Poll")\n            call DisplayTextToForce(udg_all_players, "TRIGSTR_10479")')
    edit("Trig_draw_pressed_Func011Func002Func027A","CustomDefeatBJ(GetEnumPlayer(),","PF_NativeResult(GetEnumPlayer(),false,")
    # Only terminal win/defeat callbacks use the delayed menu. Votekick and early exits keep their behavior.
    for m in list(FUNCTION.finditer(j)):
        if m[1].startswith("Trig_END_") or m[1]=="FFEnd_Resolve":
            f = re.sub(r"CustomVictoryBJ\((.+?), true, true\)",r'PF_NativeResult(\1,true,"")',m[0])
            f = re.sub(r"CustomDefeatBJ\((.+?), ",r'PF_NativeResult(\1,false, ',f)
            if f != m[0]:
                replace(m[0],f)
    ids = {key:i for i,(key,_,_) in enumerate(METRICS)}
    metrics = schema()
    init = []
    for variable, key in [("casinoFirst","bets"),("combatFirst","kills"),("poolOutMetric","pool_out"),("poolInMetric","pool_in"),("sentMetric","sent_n"),("receivedMetric","received_n")]:
        init.append(f"    set PF_{variable} = {ids[key]}")
    metrics = metrics.replace("    set PF_metrics =", "\n".join(init)+"\n    set PF_metrics =")
    before("FF_gr_RefreshStats",metrics+"\n\n"+read("export.j")+"\n\nfunction PF_Freeze"+read("settlement.j").split("function PF_Freeze")[1])
    edit("FF_gr_Flush","    if FF_gr_gameendRow != null then",'    call ExecuteFunc("PF_Export")\n    if FF_gr_gameendRow != null then')
    edit("FF_gr_RefreshStats","    loop","    set changed = changed or PF_dirty\n    set PF_dirty = false\n    loop")
    edit("FF_gr_Poll","    if FFEnd_settled then","    if FFEnd_settled and not PF_draw then")
    for branch,side in [(7,1),(9,2),(11,3),(13,4),(2,1),(4,2)]:
        condition = f"        if ( Trig_END_Func001Func{branch:03d}C() ) then"
        edit("Trig_END_Actions",condition,condition+f'\n            set PF_winSide = {side}\n            call ExecuteFunc("FF_gr_Poll")')
    edit("FF_gr_Poll","    if participated >= 2 and alive == 0 then","    if PF_draw or (participated >= 2 and alive == 0) then")
    edit("FF_gr_Poll","        call WalletAward(0, 0)","        call WalletAward(0, 0)\n        set FF_gr_ended=true\n        call PauseTimer(FF_gr_pollTimer)\n        call FF_kl_Final()\n        call FF_gr_AddEvent(\"draw,\"+now)\n        set FF_gr_gameendRow=\"gameend,\"+now\n        set changed=true")
    edit("FF_gr_Poll","    if PF_draw or (participated >= 2 and alive == 0) then","    if PF_draw or (PF_winSide == 0 and participated >= 2 and alive == 0) then")
    edit("FF_gr_Poll","    if participated >= 2 and alive == 1 then","    if not FF_gr_ended and (PF_winSide > 0 or (participated >= 2 and alive == 1)) then\n        if PF_winSide > 0 then\n            set lastAlive = PF_winSide\n        endif")
    edit("WalletPayParticipation","            call LoanAward(slot,200)","            set PF_rewards[slot] = PF_rewards[slot]+200\n            call LoanAward(slot,200)")
    edit("WalletAward","                call LoanAward(slot,reward)","                set PF_rewards[slot] = PF_rewards[slot]+reward\n                call LoanAward(slot,reward)")
    freeze = '        set PF_endSecond = R2I(TimerGetElapsed(FF_gameTimer))\n        call PF_Freeze()'
    edit("FF_gr_Poll","        call FF_gr_Flush()\n        return",freeze+"\n        call FF_gr_Flush()\n        return")
    edit("FF_gr_Poll","    if changed then\n        call FF_gr_RefreshStats()","    if changed then\n        call FF_gr_RefreshStats()\n        if FF_gr_ended then\n"+freeze.replace("        ","            ")+"\n        endif")
    before("FF_BootTick",prices)
    edit("FF_BootTick","    call FF_GameResult_Init()","    call PF_Schema()\n    call PF_LoadObjects()\n    call PF_InitGold()\n    call FF_GameResult_Init()")
    edit("FF_us_OnItemSold","    call FF_us_Add(",'''    local integer s = FF_st_Slot(GetOwningPlayer(GetBuyingUnit()))
    local item it = GetSoldItem()
    local integer id = GetItemTypeId(it)
    if s > 0 and id != 0 then
        call SaveStr(PF_prices,3,id,BlzGetItemIconPath(it))
        call PF_Use(s,2,id,1)
        call PF_Purchase(s,"item",id,PF_Price(id,1))
    endif
    set it = null
    call FF_us_Add(''')
    edit("FF_us_OnSoldTick","                call FF_us_Add(s, FF_US_UNIT, id)",'''                call FF_us_Add(s, FF_US_UNIT, id)
                if IsUnitType(u,UNIT_TYPE_HERO) then
                    call PF_Hero(s,u)
                else
                    call PF_Use(s,3,id,1)
                    call PF_Appearance(s,u,1)
                endif
                if FF_us_soldCost[i] > 0 then
                    call PF_Purchase(s,"hire",id,FF_us_soldCost[i])
                else
                    call PF_Purchase(s,"hire",id,PF_Price(id,1))
                endif''')
    edit("FF_us_PollPicks",'                set how = "pick"','                call PF_Hero(s,u)\n                call PF_Log(s,"hero",GetUnitTypeId(u),-1,0)\n                set how = "pick"')
    edit("FF_us_HeroKey","    loop","    call PF_Hero(slot,hero)\n    loop")
    edit("FF_us_PollPicks","        set u = udg_herO[s]","        if not PF_frozen then\n            call PF_HeroExperience(s)\n        endif\n        set u = udg_herO[s]")
    edit("FF_us_OnSkill","                call SaveInteger(FF_us_ht, key, n, abil)",'                call PF_Log(s,"skill",abil,-1,0)\n                call SaveInteger(FF_us_ht, key, n, abil)')
    edit("FF_us_OnResearch","        call FF_us_Put","        call PF_Purchase(s,\"research\",oid,PF_Price(oid,GetPlayerTechCount(p,oid,true)))\n        call FF_us_Put")
    edit("FF_us_OnUpgrade","        if FF_us_IsBase(u) then","        call PF_Purchase(s,\"upgrade\",id,PF_Price(id,1))\n        if FF_us_IsBase(u) then")
    before("FF_Usage_Init",read("orders.j"))
    edit("FF_Usage_Init","    set FF_us_soldTimer","    call PF_InitOrders()\n    set FF_us_soldTimer")
    edit("CAS_Reserve","    call CasinoWalletDelta(s,-stake)",'''    set PF_wagers[s] = PF_wagers[s]+1
    set PF_staked[s] = PF_staked[s]+stake
    call PF_Log(s,"stake",0,stake,0)
    call CasinoWalletDelta(s,-stake)''')
    edit("CAS_Credit","    set CAS_returnDue",'''    set PF_returned[s] = PF_returned[s]+principal+profit
    call PF_Log(s,"return",0,principal+profit,0)
    set CAS_returnDue''')
    # Keep the game identity through settlement, including challenge cancellations and tied bets.
    for m in list(FUNCTION.finditer(j)):
        name, f = m[1], m[0]
        for game, prefix in enumerate(["PK_", "BJ_", "MK_", "DU_"]):
            if name.startswith(prefix):
                for fn in ["CAS_Reserve", "CAS_Settle", "CAS_Credit"]:
                    f = f.replace(fn+"(",fn+"("+str(game)+",")
        if name == "CAS_EndMatch":
            f = f.replace("CAS_Settle(","CAS_Settle(0,")
        if name in ("CAS_Reserve","CAS_Settle","CAS_Credit"):
            f = f.replace("takes integer s,", "takes integer game, integer s,")
        if name == "CAS_Settle":
            f = f.replace("CAS_Credit(","CAS_Credit(game,")
        if name == "CAS_Reserve":
            f = f.replace("    set PF_wagers", "    set PF_gameBets[s*4+game] = PF_gameBets[s*4+game]+1\n    set PF_gameStake[s*4+game] = PF_gameStake[s*4+game]+stake\n    set PF_wagers")
        if name == "CAS_Credit":
            f = f.replace("    set PF_returned", "    set PF_gameReturn[s*4+game] = PF_gameReturn[s*4+game]+principal+profit\n    set PF_returned")
        if f != m[0]:
            replace(m[0],f)
    career = read("career.j").replace("function PF_UpdateCareer takes",read("history.j")+"\n\nfunction PF_UpdateCareer takes")
    before("DPS_Flip",career+"\n\n"+read("screens.j"))
    edit("DPS_Init",'        call BlzTriggerRegisterPlayerSyncEvent(sync,', '        call BlzTriggerRegisterPlayerSyncEvent(PF_sync,Player(id),"FFCareer22",false)\n        call BlzTriggerRegisterPlayerSyncEvent(sync,')
    edit("DPS_Init","    local trigger sync", "    local trigger PF_sync = CreateTrigger()\n    local trigger sync")
    edit("DPS_Init","    call TriggerAddAction(sync", "    call TriggerAddAction(PF_sync,function PF_ReceiveHistory)\n    set PF_sync = null\n    call TriggerAddAction(sync")
    edit("FF_gr_OnStatsTick","    if not FF_gr_ended", "    if FF_gr_ended and PF_dirty then\n        set PF_dirty = false\n        call FF_gr_Flush()\n    endif\n    if not FF_gr_ended")
    f = next(m[0] for m in FUNCTION.finditer(j) if m[1]=="DPS_Flip")
    replace(f,'''function DPS_Flip takes nothing returns nothing
    if GetTriggerPlayer() == GetLocalPlayer() then
        call PF_UpdateCareer()
        call PF_Open(false)
    endif
endfunction''')
    edit("DPS_Create","    set DPS_Ready = true","    call PF_Create()\n    set DPS_Ready = true")
    edit("DPS_Refresh","    call DPS_ProfileUpdate()",'''    call DPS_ProfileUpdate()
    set PF_saveTick = PF_saveTick+1
    if not PF_careerReady or ModuloInteger(PF_saveTick,15) == 0 or (PF_frozen and not PF_shown) then
        call PF_UpdateCareer()
    endif
    call PF_SendHistory()
    call PF_SendHistory()
    if PF_frozen and not PF_shown then
        set PF_shown = true
        call FF_CloseProfilePanels()
        call PF_Open(true)
    elseif PF_visible and not PF_results then
        call PF_Render()
    endif''')
    edit("DPS_Toggle","        set DPS_Open[p] = not DPS_Open[p]",'''        if PF_frozen then
            call PF_Open(true)
            return
        endif
        set DPS_Open[p] = not DPS_Open[p]''')
    j = j.replace('"My Stats")','"My Profile")')
    j = j.replace('function PF_ResultsView takes',read("color.j")+"\n\nfunction PF_ResultsView takes")
    (src/"war3map.j").write_bytes(encode(j,original))
    funcs = {m[1]:m[0] for m in FUNCTION.finditer(j)}
    emitted = set(meta["editor_generated_functions"])
    assert not emitted-funcs.keys()
    er = decode(editor_runtime).split("// FF Runtime is initialized once")[0]+"// FF Runtime is initialized once by the editor.\n\n"+"\n\n".join(f for n,f in funcs.items() if n not in emitted)+"\n"
    eg = decode(editor_globals).replace("\nendglobals","\n"+extra_globals+"\nendglobals")
    for old,code,name,key in [(editor_globals,eg,"globals","globals_sha256"),(editor_runtime,er,"FF_Runtime","runtime_sha256")]:
        b = encode(code,old)
        record = struct.pack("<I",len(old)+1)+old+b"\0"
        assert wct.count(record)==1
        wct = wct.replace(record,struct.pack("<I",len(b)+1)+b+b"\0")
        path = src/"source_roundtrip"/(name+".j")
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(b)
        meta[key] = digest(b)
    (src/"war3map.wct").write_bytes(wct)
    meta.update(revision="799X RC24 countdown titles",source_map_sha256=BASE_HASH,
                compiled_source_sha256=digest((src/"war3map.j").read_bytes()),runtime_functions=len(funcs)-len(emitted),engine_playtest=False)
    (src/"FF_SOURCE_MANIFEST.json").write_text(json.dumps(meta,indent=2)+"\n")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("base",type=Path)
    p.add_argument("stage",type=Path)
    args = p.parse_args()
    prepare(args.base,args.stage)
