"""Stage the open casino tables on the complete installed RC39 map."""
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
sys.path.insert(0, str(ROOT / 'tools'))
from map_archive import Archive

PARENT = '984b7767b48cdd7ae285b573aa78321862b4a1f898743ce90e5078f5af9685b4'
TITLE = 'Reforged Footmen Frenzy v7.9.9X-rc40 Open Tables'
STAGE = ROOT / 'build/799x-open-casino'


def module(name):
    return (FEATURE / name).read_text(encoding='utf8').strip() + '\n\n'


def span(s, start, end, new):
    i = s.index(start)
    j = s.index(end, i)
    return s[:i] + new + s[j:]


def functions(s, first, after, new):
    return span(s, 'function '+first+' takes', 'function '+after+' takes', new)


def once(s, a, b):
    if s.count(a) != 1:
        raise ValueError(f'Expected one occurrence of {a[:100]!r}, found {s.count(a)}')
    return s.replace(a,b)


def globals_patch(s):
    obsolete = '''PK_Street PK_Turn PK_Dealer PK_Hand PK_LastRaise PK_Actions PK_Clock PK_Wait
                  PK_Reveal PK_Queue PK_Table PK_Guest PK_LastPot PK_Ready PK_Note
                  PK_HumanChips PK_BotChips PK_BotDealer BJ_table BJ_seat BJ_owner'''.split()
    for name in obsolete:
        s, n = re.subn(r'(?m)^[ \t]*(?:integer|boolean|string|framehandle) (?:array )?'+name+r'\b[^\n]*\n','',s)
        assert n == 1, name
    return once(s,'    integer array PokerBuyIn',module('poker-globals.j')+'    integer array PokerBuyIn')


def poker(s):
    s = functions(s,'PK_PlayerAt','PK_Texture',module('poker-table.j'))
    s = functions(s,'PK_Render','PK_Sync',module('poker-panel.j'))
    s = functions(s,'PK_Tick','PK_Button',module('poker-tick.j'))
    s = functions(s,'PK_BoardCount','PK_Pay','')
    s = once(s,'function PK_Score takes integer p, integer seat, integer board returns integer\n    local integer base = p * 9','function PK_Score takes integer seat returns integer')
    s = once(s,'local integer n = board + 2','local integer n = 7')
    s = once(s,'PK_Cards[base + seat * 2]','PK_Cards[seat*2]')
    s = once(s,'PK_Cards[base + seat * 2 + 1]','PK_Cards[seat*2+1]')
    s = once(s,'exitwhen i >= board','exitwhen i >= 5')
    s = once(s,'PK_Cards[base+4+i]','OP_Board[i]')
    s = span(s,'    elseif f == PK_Next[v] then','    elseif f == PK_Call[v] then','''    elseif f == OP_PageButton[v] then
        set OP_Page[v] = ModuloInteger(OP_Page[v]+1,IMaxBJ(1,(OP_RosterCount()+4)/5))
        call PK_Render(v)
        return
    elseif f == PK_Next[v] then
        set action = "j"
    elseif f == PK_Alternate[v] then
        set action = "l"
''')
    s = once(s,'if PK_Table[v] != 0 then','if OP_Turn == v and OP_Phase == 1 then')
    s = once(s,'    set PK_Seed = GetRandomInt','    set OP_ScoreTimer = CreateTimer()\n    set PK_Seed = GetRandomInt')
    for line in ('            set PK_Stack[p*2] = 0','            set PK_Stack[p*2+1] = 0',
                 '            set PK_Turn[p] = -1','            set PK_Note[p] = ""'):
        s = once(s,line+'\n','')
    for frame in ('PK_HumanChips[p]','PK_BotChips[p]','PK_BotDealer[p]','PK_Face[p*9+2]','PK_Face[p*9+3]'):
        s,n = re.subn(r'(?m)^            set '+re.escape(frame)+r' = PK_Texture[^\n]*\n','',s)
        assert n == 1
    s = once(s,'PK_Label(p,0.025,0.086,0.231,0.023,0.91)','PK_Label(p,0.025,0.064,0.270,0.024,1.00)')
    s = once(s,'PK_Label(p,0.025,0.114,0.155,0.056,1.08)','PK_Label(p,0.025,0.090,0.405,0.100,0.98)')
    s = once(s,'0.285,-0.439,0.180,"Practice"','0.455,-0.150,0.190,"Cash out"')
    s = once(s,'0.478,-0.439,0.197,"Find player"','0.478,-0.439,0.197,"Join table"')
    s = once(s,'            set PK_Alternate[p] = PK_Button',
             '            set OP_PageButton[p] = PK_Button(p,click,0.353,-0.060,0.074,"Seats >")\n            set PK_Alternate[p] = PK_Button')
    s = s.replace('FFPK35','FFPK40')
    s = s.replace('// A table is keyed by its first player. Seat 1 is another player, or the house in practice.\n','')
    s = s.replace('// Heads-up human matchmaking and optional computer practice use the same rules.','// One open no-limit table for the match.')
    return s


def blackjack(s):
    # Player number s always owns seat s-1 and the two consecutive split-hand slots.
    s = s.replace('local integer t = BJ_table[s]', 'local integer t = 0')
    s = s.replace('BJ_seat[s]*2','(s-1)*2').replace('BJ_owner[h/2]','(h/2+1)').replace('BJ_owner[(BJ_turn[t]-1)/2]','((BJ_turn[t]-1)/2+1)')
    s = s.replace('t*12+12','48').replace('local integer h = t*12','local integer h = 0').replace('set h = t*12','set h = 0')
    s = functions(s,'BJ_Move','BJ_Tick','')
    s = once(s,'        call BJ_Move(s,BJ_table[s] != 0)','        set BJ_Page[s] = ModuloInteger(BJ_Page[s]+1,IMaxBJ(1,(BJ_SeatCount()+5)/6))')
    s = span(s,'    set BJ_table[s] = s','    set CAS_root[s]','')
    s = span(s,'            if BJ_table[s] == 0 and BJ_owner[BJ_seat[s]] == s then','        endif\n        call CreditTick(s)','')
    s = span(s,'        if t > 0 then\n            set BJ_clock[t] = 3','    endif\n    set CAS_note[s] = "Wager locked','')
    s = once(s,'    local integer stake = CAS_amount[s]\n    local integer i\n    if stake < 10','    local integer stake = CAS_amount[s]\n    if stake < 10')
    s = once(s,'    local integer dealPass = 0','    local integer dealPass = 0\n    local integer decks = 2\n    local integer seats = BJ_SeatCount()')
    s = once(s,'    if BJ_pos[t] > 26 then','''    if seats > 12 then
        set decks = 8
    elseif seats > 6 then
        set decks = 4
    endif
    if decks*52 != BJ_ShoeSize or BJ_pos[t] > BJ_ShoeSize/4 then
        set BJ_ShoeSize = decks*52''')
    # The shared shoe is resized between hands only. Hand storage remains 48 x 22.
    start = s.index('function BJ_Shuffle takes')
    end = s.index('function BJ_Hit takes',start)
    shoe = s[start:end].replace('t*104+','').replace('>= 104','>= BJ_ShoeSize').replace('set i = 103','set i = BJ_ShoeSize-1')
    roster = module('blackjack-roster.j')
    count,renderer = roster.split('function BJ_Roster takes',1)
    s = s[:start]+count+shoe+s[end:]
    s = once(s,'function CAS_BlackjackView takes','function BJ_Roster takes'+renderer+'function CAS_BlackjackView takes')
    start = s.index('function BJ_Tick takes')
    end = s.index('function MK_FFA takes',start)
    tick = s[start:end]
    tick = once(tick,'    loop\n        exitwhen t > 24\n','')
    tick = once(tick,'        set t = t+1\n    endloop\n','')
    tick = span(tick,'            if s < 0 then','                set BJ_state[h] = 2\n                call BJ_Next(t)\n            endif\n        elseif BJ_phase[t] == 3',
                '            if BJ_clock[t] <= 0 or not PK_Eligible(s-1) then\n')
    left = tick.index('        if BJ_phase[t] == 1 then')
    tick = tick[:left]+re.sub(r'(?m)^    ','',tick[left:])
    s = s[:start]+tick+s[end:]
    s = once(s,'    local string mode = "SOLO + BOTS"','    local string mode = "OPEN TABLE"')
    s = once(s,'    if t == 0 then\n        set mode = "COMMUNITY"\n    endif\n','')
    s = span(s,'        set own = BJ_owner[t*6+i]','        set i = i+1\n    endloop\n    if BJ_count[h] > 6','')
    s = once(s,'    if BJ_count[h] > 6 or BJ_count[h+1]','    call BJ_Roster(s)\n    if BJ_count[h] > 6 or BJ_count[h+1]')
    s = span(s,'    call CAS_ShowButton(s,16,BJ_phase','endfunction\n\nfunction CAS_BetsView','')
    s = once(s,'    local integer j\n    local integer own\n    local integer card','    local integer card')
    # A watcher sees the active bettor's cards while keeping their own wager controls.
    start=s.index('function CAS_BlackjackView takes')
    end=s.index('function CAS_BetsView takes',start)
    view=s[start:end]
    view=once(view,'    local integer h = (s-1)*2','    local integer personal = (s-1)*2\n    local integer h = personal')
    view=once(view,'    if BJ_phase[t] == 1 then','''    if BJ_bet[personal] == 0 and BJ_phase[t] == 2 then
        set h = ((BJ_turn[t]-1)/2)*2
        set first = CAS_Name(h/2+1)
    elseif BJ_bet[personal] == 0 then
        set first = "WATCHING"
    endif
    if BJ_phase[t] == 1 then''')
    view=once(view,'        set first = "HAND 1"','''        if personal == h then
            set first = "HAND 1"
        else
            set first = CAS_Name(h/2+1)+" / 1"
        endif''')
    wager=view.index('    set phase = "NEXT BET')
    view=view[:wager]+view[wager:].replace('BJ_bet[h','BJ_bet[personal').replace('BJ_split[h]','BJ_split[personal]')
    view=view.replace('BJ_phase[t] == 4 and (t != 0 or BJ_clock[t] == 0)','BJ_phase[t] == 4 and BJ_clock[t] == 0')
    s=s[:start]+view+s[end:]
    # The wager readout sits below the action buttons, clear of the shared seat list.
    s = once(s,'+"|nHAND 1  "+CUI_Value(I2S(BJ_bet[personal])+"g")+"|nHAND 2', '+"    /    HAND 1  "+CUI_Value(I2S(BJ_bet[personal])+"g")+"    /    HAND 2')
    s = s.replace('+"|nLAST BET  "', '+"    /    LAST BET  "').replace('+"|nIN PLAY  "', '+"    /    IN PLAY  "')
    s = once(s,'CAS_Label(s,0.032,0.184,0.174,0.057,1.05)','CAS_Label(s,0.216,0.417,0.460,0.031,1.02)')
    s = once(s,'0.025,0.248,0.167,"Community"','0.025,0.325,0.167,"Seats"')
    s = once(s,'Opening wager 10-100g / 2 decks / S17','One shared dealer. Bet 10-100g before the deal / 2-8 decks by attendance / S17')
    s = once(s,'        set CAS_note[s] = "Your wager is already placed, or a round is in progress."','        set CAS_note[s] = "Wagers lock at the deal. The table reopens after this round."')
    s = span(s,'    set i = 0\n    loop\n        exitwhen i > 24\n        if i < 24 and PK_Queue','endfunction','''    call OP_EndMatch()
    if BJ_phase[0] >= 1 and BJ_phase[0] <= 3 then
        call BJ_Finish(0,true)
    endif
''')
    return s


def open_tables(s):
    return blackjack(poker(s))


def menu_only(s):
    # CatalogCasino already belongs to the Info panel and calls CasinoFromStats.
    s = span(s, '    set CAS_launch[s] = BlzCreateFrame(', '    set CAS_felt[s] =', '')
    s = once(s, '                call BlzFrameSetVisible(CAS_launch[s],PK_Eligible(s-1))\n', '')
    s = once(s, '    if f == CAS_launch[s] then\n        set CAS_view[s] = 1\n    elseif id <= 3 then',
             '    if id <= 3 then')
    return s


def menu_globals(s):
    return once(s, '    framehandle array CAS_launch\n', '')


def prepare(base, parent=PARENT, title=TITLE, stage=STAGE, runtime=open_tables, edit_globals=globals_patch):
    digest = lambda data:hashlib.sha256(data).hexdigest()
    assert digest(base.read_bytes()) == parent, 'The active map has changed'
    for name in ('Build-Map.ps1','tools.local.json','tools/build_map.py','tools/map_archive.py','tools/Install-Wc3Map.ps1'):
        target = stage/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target)
    project = stage/'projects/799x'
    release = project/'release'/base.name
    release.parent.mkdir(parents=True,exist_ok=True)
    if not release.exists():
        shutil.copy2(base,release)
    (project/'project.json').write_text(json.dumps(dict(map_type='799X',branch='Footmen-Frenzy-12p',release=base.name,sha256=parent)))
    with Archive(json.loads((ROOT/'tools.local.json').read_text())['stormlib'],base) as archive:
        def patch(name,fn):
            original=archive.read(name)
            value=fn(original.decode().replace('\r\n','\n'))
            return (value.replace('\n','\r\n') if b'\r\n' in original else value).encode()
        rname=r'source_roundtrip\FF_Runtime.j'
        gname=r'source_roundtrip\globals.j'
        r=patch(rname,runtime)
        g=patch(gname,edit_globals)
        j=patch('war3map.j',lambda s:re.sub(r'call SetMapName\("[^"]+"\)',f'call SetMapName("{title}")',runtime(edit_globals(s))))
        w=archive.read('war3map.wct')
        for name,data in [(rname,r),(gname,g)]:
            def record(b):
                return struct.pack('<I',len(b)+1)+b+b'\0'
            w=once(w,record(archive.read(name)),record(data))
        meta=json.loads(archive.read('FF_SOURCE_MANIFEST.json'))
        meta.update(compiled_source_sha256=digest(j),runtime_sha256=digest(r),globals_sha256=digest(g),
                    runtime_functions=len(re.findall(rb'(?m)^function ',r)),source_map_sha256=parent,revision=title,engine_playtest=False)
        info=archive.read('war3map.w3i')
        end=info.index(0,28)
        old=info[28:end]
        wts,n=re.subn(rb'(?m)^'+re.escape(old)+rb'(?=\r?$)',title.encode(),archive.read('war3map.wts'))
        assert n==1
        changes={'war3map.j':j,rname:r,gname:g,'war3map.wct':w,'war3map.w3i':info[:28]+title.encode()+info[end:],
                 'war3map.wts':wts,'FF_SOURCE_MANIFEST.json':(json.dumps(meta,indent=2)+'\n').encode()}
        for name,data in changes.items():
            path=project/'src'/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('base',type=Path)
    parser.add_argument('--menu-only', action='store_true', help='Stage RC41 from RC40 with Casino in Info only')
    args = parser.parse_args()
    if args.menu_only:
        prepare(args.base, 'e65a6695b8ebf343f17d88441afc57927d5f246efaf192f49db380b7a2ef306c',
                'Reforged Footmen Frenzy v7.9.9X-rc41 Open Tables', ROOT/'build/799x-rc41-menu',
                menu_only, menu_globals)
    else:
        prepare(args.base)
