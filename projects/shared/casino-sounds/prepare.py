"""Stage casino outcome sounds against the complete 799X RC41 or Solo RC8 map."""
import argparse
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[3]
open_tables = runpy.run_path(str(ROOT / "projects/799x/features/open-casino/prepare.py"))
solo = runpy.run_path(str(ROOT / "projects/solo/features/rc7/prepare.py"))
once = open_tables["once"]


def globals_patch(code):
    anchor = "    integer CAS_seed = 71983"
    return once(code, anchor, "    sound CAS_winSound = null\n    sound CAS_lossSound = null\n" + anchor)


def runtime_patch(code):
    anchor = "function CAS_Settle takes"
    code = once(code, anchor, """function CAS_ResultSound takes integer s, integer net returns nothing
    if s > 0 then
        if net > 0 then
            call StartSoundForPlayerBJ(Player(s-1),CAS_winSound)
        elseif net < 0 then
            call StartSoundForPlayerBJ(Player(s-1),CAS_lossSound)
        endif
    endif
endfunction

""" + anchor)
    anchor = "    set CAS_seed = GetRandomInt(1,2147483646)"
    code = once(code, anchor, r'''    set CAS_winSound = CreateSound("Abilities\\Spells\\Items\\ResourceItems\\ReceiveGold.flac",false,false,false,0,0,"")
    call SetSoundVolume(CAS_winSound,100)
    set CAS_lossSound = CreateSound("Sound\\Interface\\MouseClick1.wav",false,false,false,0,0,"")
    call SetSoundVolume(CAS_lossSound,72)
''' + anchor)
    legacy = "function CAS_Settle takes integer s," in code
    for settle, net in [
        ("                call CAS_Settle(1,s,stake,payout,BJ_reserve[h])", "payout-stake"),
        ("    call CAS_Settle(2,s,MK_stake[ticket],payout,MK_reserve[ticket])", "payout-MK_stake[ticket]"),
    ]:
        if legacy:
            settle = settle.replace("CAS_Settle(1,s,", "CAS_Settle(s,").replace("CAS_Settle(2,s,", "CAS_Settle(s,")
        indent = settle[:len(settle)-len(settle.lstrip())]
        code = once(code, settle, settle + "\n" + indent + f"call CAS_ResultSound(s,{net})")

    anchor = "                call CAS_Credit(3,won,stake,stake)"
    if legacy:
        anchor = anchor.replace("(3,won", "(won")
    code = once(code, anchor, anchor + """
                call CAS_ResultSound(won,stake)
                if won == DU_from[id] then
                    call CAS_ResultSound(DU_to[id],-stake)
                else
                    call CAS_ResultSound(DU_from[id],-stake)
                endif""")
    if "function OP_Finish takes" in code:
        anchor = "            set PK_Stack[v] = PK_Stack[v]+OP_Award[v]"
        code = once(code, anchor, "            call CAS_ResultSound(v+1,OP_Award[v]-PK_Total[v])\n" + anchor)
        anchor = "                call CAS_Credit(3,s,AR_held[side],AR_stake)"
        code = once(code, anchor, anchor + """
                call CAS_ResultSound(s,AR_stake)
            else
                call CAS_ResultSound(s,-AR_held[side])""")
    elif legacy:
        anchor = "        call CAS_Settle(p+1,PokerBuyIn[p],PK_Stack[x],PokerBuyIn[p])"
        code = once(code, anchor, anchor + "\n        call CAS_ResultSound(p+1,PK_Stack[x]-PokerBuyIn[p])")
    else:
        anchor = "        set PK_Stack[first+winner] = PK_Stack[first+winner]+pot"
        code = once(code, anchor, anchor + """
        call CAS_ResultSound(PK_PlayerAt(table,winner)+1,pot/2)
        call CAS_ResultSound(PK_PlayerAt(table,1-winner)+1,-(pot/2))""")
    return code


def credit_record(code):
    anchor = "    call CAS_Button(s,57,"
    code = once(code, anchor, '    call CAS_Button(s,60,click,0.419,0.014,0.150,"Lending record")\n'+anchor)
    anchor = "    call BlzFrameSetText(CAS_title[s],label)"
    code = once(code, anchor, "    call BlzFrameSetVisible(CAS_button[s*64+60],CAS_view[s] == 5)\n"+anchor)
    anchor = "    elseif id == 57 then"
    code = once(code, anchor, """    elseif id == 60 and CAS_view[s] == 5 then
        if CAS_ready[s] then
            call DisplayTimedTextToPlayer(Player(s-1),0,0,10,"Wallet: "+I2S(CAS_gold[s])+"g  /  Lifetime lent: "+I2S(LoanLent[s])+"g|nOutstanding principal: "+I2S(LoanOutstanding[s])+"g  /  Interest collected: "+I2S(LoanInterest[s])+"g")
            if LoanLent[s] > 0 then
                call DisplayTimedTextToPlayer(Player(s-1),0,0,10,"Lending ROI: "+R2SW(100.*I2R(LoanInterest[s])/I2R(LoanLent[s]),1,2)+"%")
            endif
        endif
""" + anchor)
    return code


def stage(project, parent, standalone=None, solo_parent=None):
    from house import attach, modules
    from standalone import CASINO, decoded
    import hashlib
    work = ROOT / "build/casino-consolidation" / project
    if project == "799x":
        dll = json.loads((ROOT / "tools.local.json").read_text())["stormlib"]
        for source, expected in [(standalone,CASINO), (solo_parent,"3716cb848c82c13f36baee7ba5e96a9a943c982bf6ab0548db50298d76e575c4")]:
            if source is None or hashlib.sha256(source.read_bytes()).hexdigest() != expected:
                raise ValueError("Expected the standalone v12 and Solo RC8 donors")
        with solo["Archive"](dll, standalone) as classic, solo["Archive"](dll, solo_parent) as private:
            header, games, view = modules(runtime_patch(decoded(classic.read("war3map.j"))),
                                          runtime_patch(decoded(private.read("war3map.j"))))
        def apply_globals(code):
            return once(globals_patch(code),"    sound CAS_winSound",header+"\n    sound CAS_winSound")
        open_tables["prepare"](parent, "352e820ed2450ae3e83ceb76c47dea7557260b39e8e89e0f1418845fb6b06802",
                               "Reforged Footmen Frenzy v7.9.9X-rc42 Open Tables", work,
                               lambda code: attach(credit_record(runtime_patch(code)),games,view), apply_globals)
    else:
        src = solo["stage_project"](parent, "3716cb848c82c13f36baee7ba5e96a9a943c982bf6ab0548db50298d76e575c4", work)
        dll = json.loads((ROOT / "tools.local.json").read_text())["stormlib"]
        with solo["Archive"](dll, parent) as archive:
            original = archive.read("war3map.j")
            jass = credit_record(runtime_patch(globals_patch(original.decode().replace("\r\n", "\n"))))
            if b"\r\n" in original:
                jass = jass.replace("\n", "\r\n")
            for name in ("war3map.j", "war3map.w3i", "war3map.wts"):
                data = jass.encode() if name == "war3map.j" else archive.read(name)
                (src / name).write_bytes(once(data, b"Solo Foots 1.8-RC8", b"Solo Foots 1.8-RC9"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", choices=("799x", "solo"))
    parser.add_argument("parent", type=Path)
    parser.add_argument("--standalone", type=Path)
    parser.add_argument("--solo-parent", type=Path)
    args = parser.parse_args()
    stage(args.project, args.parent, args.standalone, args.solo_parent)
