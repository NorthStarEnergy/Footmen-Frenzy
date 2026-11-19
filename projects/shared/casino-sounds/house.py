"""Keep house tables alongside 799X's multiplayer tables using the same wallet."""
import re
from textwrap import dedent, indent

from prepare import once, solo


def modules(classic, solo_map):
    poker = solo["functions"](classic)
    blackjack = solo["functions"](solo_map)
    # Create the practice panel on first use. All clients create the same
    # handles, and the table renderer controls visibility for its owner.
    start = poker["PK_Start"]
    start = start[start.index("            set PK_Hidden"):start.index("            call PK_Render(p)")]
    start = "\n".join(line for line in start.splitlines() if "TriggerRegisterPlayerChatEvent" not in line)
    poker["PK_Start"] = """function PK_Start takes integer p returns nothing
    local integer i = 0
    local trigger click = null
    if not PK_Started[p] then
""" + indent(dedent(start),"        ") + """
    endif
    set PK_Hidden[p] = false
    call PK_Render(p)
    set click = null
endfunction"""
    poker["PK_Deal"] = once(poker["PK_Deal"], "CAS_Reserve(p+1,", "CAS_Reserve(0,p+1,")
    poker["PK_End"] = once(poker["PK_End"], "CAS_Settle(p+1,", "CAS_Settle(0,p+1,")
    # Return the buy-in once when a player disconnects or the match ends.
    close = """function PK_Refund takes integer p returns nothing
    if PokerBuyIn[p] > 0 then
        call CAS_Settle(0,p+1,PokerBuyIn[p],PokerBuyIn[p],PokerBuyIn[p])
        set PokerBuyIn[p] = 0
        set PK_Turn[p] = -1
    endif
endfunction"""
    poker["PK_Tick"] = once(poker["PK_Tick"], "                call BlzFrameSetVisible(PK_Dialog[p],false)",
                            "                call PK_Refund(p)\n                call BlzFrameSetVisible(PK_Dialog[p],false)")
    poker["PK_Tick"] = close + "\n\n" + poker["PK_Tick"]
    poker_names = ["PK_Random","PK_Score","PK_BoardCount","PK_Limit","PK_Pay","PK_End","PK_Showdown",
                   "PK_Advance","PK_Deal","PK_Action","PK_Texture","PK_Label","PK_Render","PK_Bot",
                   "PK_Click","PK_Tick","PK_Button","PK_Start"]
    # Preserve donor declaration order, including forward dependencies.
    pk = "\n\n".join(body for name,body in poker.items() if name in poker_names)
    assert all(name in poker for name in poker_names)
    view = blackjack["CAS_BlackjackView"].split("    call CAS_ShowButton(s,16")[0] + "endfunction"
    view = view.replace("|nHAND 1 ", "    /    HAND 1 ").replace("|nHAND 2 ", "    /    HAND 2 ")
    view = view.replace("|nLAST BET ", "    /    LAST BET ").replace("|nIN PLAY ", "    /    IN PLAY ")
    view = view.replace("function CAS_BlackjackView", "function HouseBlackjackView")
    bj = "\n\n".join(body for name,body in blackjack.items() if name.startswith("BJ_") and name not in
                     {"BJ_Move","BJ_Value","BJ_Payout","BJ_CardStart"})
    decl = []
    for code, source, prefix in [(pk,classic,"PK_"),(bj+view,solo_map,"BJ_")]:
        used = solo["identifiers"](code)
        for key,line in solo["declarations"](source).items():
            if key in used and (key.startswith(prefix) or key=="PokerBuyIn") and key!="BJ_wagerLabel":
                decl.append(line)
    private = {re.search(r"(?:array\s+)?((?:PK_|BJ_)\w+|PokerBuyIn)\b",line)[1] for line in decl}
    private |= set(poker_names) | {"PK_Refund"} | set(re.findall(r"(?m)^function (BJ_\w+)",bj))
    pattern = re.compile(r"\b(?:"+"|".join(sorted(private))+r")\b")
    rename = lambda text: pattern.sub(lambda m:"House"+m[0],text)
    return (rename("\n".join(decl))+"\n    boolean array HouseBlackjack",
            rename(pk+"\n\n"+bj), rename(view))


def attach(code, games, view):
    # Place the two engines after shared card and wallet helpers. The private
    # blackjack renderer additionally needs the CAS frame helpers declared later.
    code = once(code, "function MK_FFA takes", games + "\n\nfunction MK_FFA takes")
    code = once(code, "    set CAS_seed = GetRandomInt", "    set HousePK_Seed = GetRandomInt(1,2147483646)\n    set CAS_seed = GetRandomInt")
    code = once(code, "function CAS_Render takes", view + "\n\nfunction CAS_Render takes")
    code = once(code, "    call OP_EndMatch()", """    set i = 1
    loop
        exitwhen i > 24
        call HousePK_Refund(i-1)
        if HouseBJ_phase[i] >= 1 and HouseBJ_phase[i] <= 3 then
            call HouseBJ_Finish(i,true)
        endif
        set i = i+1
    endloop
    call OP_EndMatch()""")
    code = once(code, "    call BJ_Tick()", "    call BJ_Tick()\n    call HouseBJ_Tick()\n    call HousePK_Tick()")
    anchor = "        call CAS_BlackjackView(s)"
    code = once(code, anchor, """        if HouseBlackjack[s] then
            call HouseBlackjackView(s)
            call BlzFrameSetVisible(CAS_button[s*64+16],false)
            call CUI_Text(CAS_button[s*64+58],"Open table")
        else
            call CAS_BlackjackView(s)
            call CUI_Text(CAS_button[s*64+58],"Solo + bots")
        endif""")
    code = once(code, "    call BlzFrameSetText(CAS_title[s],label)", """    call BlzFrameSetVisible(CAS_button[s*64+58],CAS_view[s] == 1)
    call BlzFrameSetVisible(CAS_button[s*64+59],CAS_view[s] == 1)
    call BlzFrameSetText(CAS_title[s],label)""")
    code = once(code, "    call CAS_Button(s,57,", """    call CAS_Button(s,58,click,0.314,0.014,0.121,"Solo + bots")
    call CAS_Button(s,59,click,0.440,0.014,0.130,"House poker")
    call CAS_Button(s,57,""")
    code = once(code, "    elseif id == 57 then", """    elseif id == 58 and CAS_view[s] == 1 then
        if (HouseBlackjack[s] and HouseBJ_phase[s] >= 1 and HouseBJ_phase[s] <= 3) or (not HouseBlackjack[s] and BJ_bet[(s-1)*2] > 0 and BJ_phase[0] >= 1 and BJ_phase[0] <= 3) then
            set CAS_note[s] = "Finish your blackjack wager before switching tables."
        else
            set HouseBlackjack[s] = not HouseBlackjack[s]
            if HouseBlackjack[s] and HouseBJ_table[s] == 0 then
                set HouseBJ_table[s] = s
                set HouseBJ_seat[s] = s*6
                set HouseBJ_owner[s*6] = s
                set HouseBJ_owner[s*6+1] = -1
                set HouseBJ_owner[s*6+2] = -1
                call HouseBJ_Shuffle(s)
            endif
        endif
    elseif id == 59 and CAS_view[s] == 1 then
        set CAS_view[s] = 0
        call HousePK_Start(s-1)
    elseif id == 57 then""")
    for call in ["BJ_Wager(s)", "BJ_Action(s,id-11)"]:
        code = once(code, "        call "+call, f"        if HouseBlackjack[s] then\n            call House{call}\n        else\n            call {call}\n        endif")
    # Hide the practice panel when opening Info > Casino, a casino shortcut,
    # the arena or the open poker table; outstanding hands still time out.
    anchor = "    if CAS_view[s] == 0 then\n        return\n    endif"
    code = once(code, anchor, anchor + """
    if HousePK_Started[s-1] and not HousePK_Hidden[s-1] then
        set HousePK_Hidden[s-1] = true
        call HousePK_Render(s-1)
    endif""")
    anchor = '        if line == "-poker" then'
    code = once(code, anchor, anchor + """
            set HousePK_Hidden[v] = true
            if GetLocalPlayer() == Player(v) and HousePK_Dialog[v] != null then
                call BlzFrameSetVisible(HousePK_Dialog[v],false)
            endif""")
    code = once(code, "    set PK_Hidden[s-1] = true\n    if GetLocalPlayer()", """    set PK_Hidden[s-1] = true
    set HousePK_Hidden[s-1] = true
    if GetLocalPlayer() == Player(s-1) and HousePK_Dialog[s-1] != null then
        call BlzFrameSetVisible(HousePK_Dialog[s-1],false)
    endif
    if GetLocalPlayer()""")
    return code
