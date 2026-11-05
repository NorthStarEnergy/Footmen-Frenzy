"""Run actual JASS functions under a small native mock, with JASS division semantics.

This verifies rules/accounting and frame rendering; it is not an engine playtest.
"""
from pathlib import Path
from collections import defaultdict, Counter
import ast
import copy
import json
import random
import re

ROOT = Path(__file__).resolve().parent
MODULES = ('buttons.j','wallet.j','blackjack.j','markets.j','duels.j','ui.j','start.j')
SOURCE = '\n'.join((ROOT/f).read_text(encoding='utf-8') for f in MODULES)
FUNCTIONS = {m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',SOURCE)}
reference = (ROOT.parent/'observer-poker/account-reference/war3map.j').read_text(encoding='utf-8-sig')
for name in ('FGA_Award','FGA_Find','FGA_Number'):
    FUNCTIONS[name] = re.search(r'(?ms)^function '+name+r'\b.*?^endfunction',reference)[0]

def expr(line):
    # Split comments outside string literals; retain literal words like "true" in labels.
    parts = re.split(r'("(?:[^"\\]|\\.)*")',line)
    for i in range(0,len(parts),2):
        parts[i] = parts[i].split('//')[0]
        for a,b in [('true','True'),('false','False'),('null','None')]:
            parts[i] = re.sub(r'\b'+a+r'\b',b,parts[i])
        parts[i] = re.sub(r'\bfunction (\w+)',r'\1',parts[i])
    return ''.join(parts).strip()

def translate(name):
    source = FUNCTIONS[name]
    lines = source.splitlines()
    args = re.search(r'takes (.*?) returns',lines[0])[1].strip()
    args = [] if args == 'nothing' else [a.split()[-1] for a in args.split(',')]
    local = re.findall(r'local \w+ (\w+)',source)
    assigned = set(re.findall(r'^\s*set (\w+)',source,re.M))-set(local)-set(args)
    out = ['def '+name+'('+','.join(args)+'):']
    depth = 1
    if assigned:
        out.append('    global '+','.join(sorted(assigned)))
    for raw in lines[1:-1]:
        line = expr(raw)
        if not line:
            continue
        if line in ('endif','endloop'):
            depth -= 1
            continue
        if line.startswith('elseif '):
            depth -= 1
            out.append('    '*depth+'elif '+line[7:-5]+':')
            depth += 1
        elif line == 'else':
            depth -= 1
            out.append('    '*depth+'else:')
            depth += 1
        elif line.startswith('if ') and line.endswith(' then'):
            out.append('    '*depth+line[:-5]+':')
            depth += 1
        elif line == 'loop':
            out.append('    '*depth+'while True:')
            depth += 1
        elif line.startswith('exitwhen '):
            out.append('    '*depth+'if '+line[9:]+': break')
        elif line.startswith('local '):
            m = re.match(r'local \w+ (\w+)(.*)',line)
            out.append('    '*depth+m[1]+(m[2] if m[2].strip() else '=None'))
        elif line.startswith(('set ','call ')):
            out.append('    '*depth+line.split(' ',1)[1])
        else:
            out.append('    '*depth+line)
    return '\n'.join(out)

def jdiv(a,b):
    if isinstance(a,int) and isinstance(b,int):
        return int(a/b)
    return a/b

class Division(ast.NodeTransformer):
    def visit_BinOp(self,node):
        self.generic_visit(node)
        if isinstance(node.op,ast.Div):
            return ast.copy_location(ast.Call(func=ast.Name(id='jdiv',ctx=ast.Load()),args=[node.left,node.right],keywords=[]),node)
        return node

NOW = 20.0
LOCAL = 0
frames = {}
messages = []
serial = 0
timers = {}

def create_frame(*args):
    global serial
    serial += 1
    frames[serial] = dict(kind=args[0],parent=args[2],visible=True,children=[])
    if args[2] in frames:
        frames[args[2]]['children'].append(serial)
    return serial

def frame_set(f,key,value):
    assert f in frames, ('invalid frame',f,key)
    frames[f][key] = value

def award_log(*args):
    messages.append(args)

ENV = dict(jdiv=jdiv,IMinBJ=min,IMaxBJ=max,ModuloInteger=lambda a,b:a%b,I2S=str,S2I=lambda a:int(a or 0),I2R=float,R2I=int,
    SubString=lambda s,a,b:s[a:b],StringLength=len,StringCase=lambda s,up:s.upper() if up else s.lower(),StringHash=lambda s:sum(ord(c) for c in s),
    Player=lambda p:p,GetPlayerId=lambda p:p,GetPlayerName=lambda p:'Player '+str(p+1),GetPlayerController=lambda p:1,
    GetPlayerSlotState=lambda p:1,MAP_CONTROL_USER=1,PLAYER_SLOT_STATE_PLAYING=1,FGA_SaveLocal=lambda:None,
    GetPlayersAll=lambda:0,DisplayTimedTextToForce=award_log,DisplayTimedTextToPlayer=award_log,
    FF_gr_SideCount=lambda:4,FF_gr_SideParticipated=lambda side:side in (1,2,3,4),FF_gr_SideLabel=lambda side:'team'+str(side),
    FFEnd_ParticipantCount=lambda:12,FFEnd_BlockCount=lambda:4,FF_gameTimer=1,TimerGetElapsed=lambda _:NOW,
    FF_Pad2=lambda n:str(n).zfill(2),GetUnitName=lambda u:u['name'],IsUnitType=lambda u,t:u.get('hero',False),IsUnitIllusion=lambda u:u.get('illusion',False),
    GetOwningPlayer=lambda u:u['owner'],IsPlayerEnemy=lambda a,b:a!=b,UNIT_TYPE_HERO=1,GetHeroLevel=lambda u:u.get('level',1),
    GetLocalPlayer=lambda:LOCAL,BlzCreateFrameByType=create_frame,BlzFrameSetSize=lambda f,*v:frame_set(f,'size',v),
    BlzFrameSetPoint=lambda f,*v:frame_set(f,'point',v),BlzFrameSetAbsPoint=lambda f,*v:frame_set(f,'abs',v),
    BlzFrameSetTextAlignment=lambda f,*v:frame_set(f,'align',v),BlzFrameSetScale=lambda f,v:frame_set(f,'scale',v),
    BlzFrameSetFont=lambda f,*v:frame_set(f,'font',v),BlzFrameSetAllPoints=lambda f,p:frame_set(f,'allpoints',p),
    BlzFrameGetChild=lambda f,i:frames[f]['children'][i],BlzFrameSetTextColor=lambda f,v:frame_set(f,'textcolor',v),
    BlzFrameSetText=lambda f,v:frame_set(f,'text',v),BlzFrameSetTexture=lambda f,v,*_:frame_set(f,'texture',v),
    BlzFrameSetVisible=lambda f,v:frame_set(f,'visible',v),BlzFrameSetEnable=lambda f,v:frame_set(f,'enabled',v),
    BlzFrameSetVertexColor=lambda f,v:frame_set(f,'color',v),BlzFrameSetLevel=lambda f,v:frame_set(f,'level',v),
    BlzConvertColor=lambda *v:v,BlzGetOriginFrame=lambda *v:0,CreateTrigger=lambda:1,TriggerAddAction=lambda *v:None,
    TimerStart=lambda t,d,repeat,fn:timers.update({t:fn}),PauseTimer=lambda t:timers.pop(t,None),
    BlzTriggerRegisterFrameEvent=lambda *v:None,PK_Render=lambda p:None,PK_ChipArt=lambda f,n:frame_set(f,'chips',n),
    ORIGIN_FRAME_GAME_UI=0,TEXT_JUSTIFY_TOP=1,TEXT_JUSTIFY_LEFT=2,TEXT_JUSTIFY_MIDDLE=3,TEXT_JUSTIFY_CENTER=4,FRAMEPOINT_TOPLEFT=0,FRAMEEVENT_CONTROL_CLICK=1)
GLOBALS = (ROOT/'casino-globals.j').read_text()
array_names = re.findall(r'\w+ array (\w+)',GLOBALS)+['FGA_gold','FGA_debt','FGA_lender','FGA_pending','FGA_ready','FF_gr_participant','udg_herO','PK_Started','PK_Hidden']
for name in array_names:
    if re.search(r'framehandle array '+name+r'\b',GLOBALS) or name == 'udg_herO':
        ENV[name] = defaultdict(lambda:None)
    else:
        ENV[name] = defaultdict(lambda:0)
for typ,name,value in re.findall(r'^\s*(\w+) (\w+) = ([^\n]+)',GLOBALS,re.M):
    ENV[name] = eval(expr(value),{},ENV)
for name in FUNCTIONS:
    tree = ast.fix_missing_locations(Division().visit(ast.parse(translate(name))))
    exec(compile(tree,'JASS '+name,'exec'),ENV)

def call(name,*args):
    return ENV[name](*args)

def drain():
    for _ in range(100):
        if not timers:
            return
        for timer,callback in list(timers.items()):
            callback()
    raise AssertionError('Payout queue did not drain')

def reset():
    global NOW
    NOW = 20.0
    timers.clear()
    ENV['FFEnd_ParticipantCount'] = lambda:12
    ENV['FFEnd_BlockCount'] = lambda:4
    for name in array_names:
        ENV[name].clear()
    for typ,name,value in re.findall(r'^\s*(\w+) (\w+) = ([^\n]+)',GLOBALS,re.M):
        ENV[name] = eval(expr(value),{},ENV)
    for s in range(1,25):
        ENV['FGA_ready'][s] = True
        ENV['FGA_gold'][s] = 1000
        ENV['FF_gr_participant'][s] = s <= 12
        ENV['CAS_amount'][s] = 50
        ENV['BJ_table'][s] = s
        ENV['BJ_seat'][s] = s*6
        ENV['BJ_owner'][s*6] = s
        ENV['BJ_owner'][s*6+1] = -1
        ENV['BJ_owner'][s*6+2] = -1
        call('BJ_Shuffle',s)
    call('BJ_Shuffle',0)
    call('MK_Refresh')

def all_money():
    return ENV['CAS_bank']+sum(ENV['FGA_gold'].values())+sum(ENV['CAS_escrow'].values())+sum(ENV['CAS_returnDue'].values())+sum(ENV['CAS_profitDue'].values())+sum(ENV['FGA_pending'].values())

def cards(h,values):
    ENV['BJ_count'][h] = len(values)
    for i,c in enumerate(values):
        ENV['BJ_card'][h*22+i] = c
    call('BJ_Recount',h)

def check_money(expected):
    assert all_money() == expected,(all_money(),expected)
    assert ENV['CAS_bank'] >= ENV['CAS_liability'] >= 0
    assert min(ENV['CAS_escrow'].values(),default=0) >= 0
    assert min(ENV['FGA_gold'].values(),default=0) >= 0

reset()
for t in (0,1,24):
    assert Counter(ENV['BJ_shoe'][t*104+i] for i in range(104)) == Counter({c:2 for c in range(52)})
cards(12,[12,25,7]); assert ENV['BJ_total'][12] == 21 and ENV['BJ_aces'][12] == 1
cards(12,[12,25,38,6]); assert ENV['BJ_total'][12] == 21
cards(12,[12,8,8]); assert ENV['BJ_total'][12] == 21 and ENV['BJ_aces'][12] == 0
assert call('BJ_Payout',21,True,20,False,50) == 125
assert call('BJ_Payout',21,True,21,True,50) == 50
assert call('BJ_Payout',21,False,21,True,50) == 0
assert call('BJ_Payout',22,False,24,False,50) == 0
assert call('BJ_Payout',17,False,22,False,50) == 100
assert call('BJ_Payout',18,False,18,False,50) == 50

# Random full rounds execute the actual rules, rather than a mirrored engine.
rng = random.Random(77142)
rounds = 0
for _ in range(600):
    reset()
    money = all_money()
    call('BJ_Wager',1)
    call('BJ_Deal',1)
    moves = 0
    while ENV['BJ_phase'][1] in (2,3):
        h = ENV['BJ_turn'][1]-1
        if ENV['BJ_phase'][1] == 2 and ENV['BJ_owner'][h//2] == 1:
            action = rng.choice([1,2,3,4])
            call('BJ_Action',1,action)
            if moves > 50:
                call('BJ_Action',1,2)
        else:
            call('BJ_Tick')
        check_money(money)
        moves += 1
        assert moves < 150
    assert ENV['CAS_escrow'][1] == 0
    assert ENV['CAS_liability'] == 0
    paid = all_money()
    gold = ENV['FGA_gold'][1]
    call('BJ_Finish',1,False)
    assert ENV['FGA_gold'][1] == gold
    check_money(paid)
    rounds += 1

# Carry the two-deck shoe across rounds, then reshuffle only between rounds.
reset(); money = all_money(); shuffle_count = 0
for _ in range(100):
    if ENV['BJ_phase'][1] == 4:
        call('BJ_Reset',1)
    pos_before = ENV['BJ_pos'][1]
    call('BJ_Wager',1); call('BJ_Deal',1)
    if pos_before > 26:
        shuffle_count += 1
        assert ENV['BJ_pos'][1] < pos_before
    else:
        assert ENV['BJ_pos'][1] > pos_before
    while ENV['BJ_phase'][1] in (2,3):
        hand = ENV['BJ_turn'][1]-1
        if ENV['BJ_phase'][1] == 2 and ENV['BJ_owner'][hand//2] == 1:
            call('BJ_Action',1,2)
        else:
            call('BJ_Tick')
    check_money(money)
assert shuffle_count > 10

# Shared table: two humans, same dealer, isolated wagers and turn ownership.
reset(); money = all_money()
call('BJ_Move',1,True); call('BJ_Move',2,True)
assert ENV['BJ_seat'][1] == 0 and ENV['BJ_seat'][2] == 1
call('BJ_Wager',1); call('BJ_Wager',2); call('BJ_Deal',0)
if ENV['BJ_phase'][0] == 2:
    owner = ENV['BJ_owner'][(ENV['BJ_turn'][0]-1)//2]
    before = copy.deepcopy(ENV['BJ_card'])
    call('BJ_Action',3-owner,1)
    assert ENV['BJ_card'] == before
while ENV['BJ_phase'][0] in (2,3):
    if ENV['BJ_phase'][0] == 2:
        owner = ENV['BJ_owner'][(ENV['BJ_turn'][0]-1)//2]
        call('BJ_Action',owner,2)
    else:
        call('BJ_Tick')
check_money(money)
assert ENV['CAS_escrow'][1] == ENV['CAS_escrow'][2] == 0

# Exact split-ace, split-21, double, and exhaustion behavior.
reset(); money = all_money(); call('BJ_Wager',1)
h = 12
ENV['BJ_phase'][1] = 2; ENV['BJ_turn'][1] = h+1
cards(h,[12,25]); ENV['BJ_state'][h] = 1
call('BJ_Action',1,4)
assert ENV['BJ_split'][h] and ENV['BJ_split'][h+1]
assert ENV['BJ_count'][h] == ENV['BJ_count'][h+1] == 2
assert ENV['BJ_state'][h] == ENV['BJ_state'][h+1] == 2
assert ENV['CAS_escrow'][1] == 100
call('BJ_Finish',1,True); check_money(money)
assert ENV['FGA_gold'][1] == 1000
reset(); money = all_money(); call('BJ_Wager',1)
ENV['BJ_phase'][1] = 2; ENV['BJ_turn'][1] = 13
cards(12,[3,4]); ENV['BJ_state'][12] = 1
call('BJ_Action',1,3)
assert ENV['BJ_bet'][12] == 100 and ENV['CAS_escrow'][1] == 100
call('BJ_Action',1,3); assert ENV['BJ_bet'][12] == 100
call('BJ_Finish',1,True); check_money(money)
reset(); money = all_money(); call('BJ_Wager',1)
ENV['BJ_phase'][1] = 2; ENV['BJ_turn'][1] = 13; ENV['BJ_pos'][1] = 104
cards(12,[0,1]); ENV['BJ_state'][12] = 1
call('BJ_Action',1,1)
assert ENV['BJ_phase'][1] == 4 and ENV['FGA_gold'][1] == 1000
check_money(money)

# Quoted odds move with money; purchased odds do not change.
reset(); money = all_money()
ENV['udg_herO'][1] = dict(name='Shadow Hunter')
assert call('MK_Prior',1,1) == 300
ENV['udg_herO'][2] = dict(name='Cattle Bruiser')
assert call('MK_Prior',1,2) == 300
call('MK_Refresh')
fav = call('MK_Quote',1,1,0); other = call('MK_Quote',1,3,0)
ENV['CAS_amount'][1] = 500
call('MK_Buy',1,1,1)
locked = ENV['MK_return'][1]
assert call('MK_Quote',1,1,0) < fav
assert call('MK_Quote',1,3,0) > other
call('MK_Buy',2,1,1); assert ENV['MK_return'][1] == locked
check_money(money)
call('MK_Resolve',1,1); drain(); check_money(money)
gold = ENV['FGA_gold'][1]
call('MK_Resolve',1,1); drain(); assert ENV['FGA_gold'][1] == gold
assert not call('MK_IsOpen',1,1)
NOW = 129.99; assert call('MK_IsOpen',2,1)
NOW = 130.0; assert not call('MK_IsOpen',2,1)

# Debt only consumes profit. A push/refund returns the complete original stake.
reset(); money = all_money()
ENV['FGA_debt'][1] = 100; ENV['FGA_lender'][1] = ENV['StringHash']('Player 2')
assert call('CAS_Reserve',1,50,75)
call('CAS_Settle',1,50,50,75)
assert ENV['FGA_gold'][1] == 1000 and ENV['FGA_debt'][1] == 100
assert call('CAS_Reserve',1,50,75)
call('CAS_Settle',1,50,125,75)
assert ENV['FGA_gold'][1] == 1000 and ENV['FGA_debt'][1] == 25 and ENV['FGA_gold'][2] == 1075
check_money(money)

# House liability rejection is atomic.
reset(); ENV['CAS_bank'] = 10
before = all_money(); gold = ENV['FGA_gold'][1]
assert not call('CAS_Reserve',1,50,75)
assert ENV['FGA_gold'][1] == gold and ENV['CAS_escrow'][1] == 0
check_money(before)

# Base kill is any enemy base, while first-base-lost settles immediately.
reset(); money = all_money()
call('MK_Buy',1,2,1); call('MK_Buy',2,2,2); call('MK_Buy',3,3,4)
victim = dict(owner=3); killer = dict(owner=0)
ENV['GetDyingUnit'] = lambda:victim; ENV['GetKillingUnit'] = lambda:killer
ENV['CAS_baseVictim'] = victim; ENV['CAS_baseKiller'] = killer
call('MK_BaseDeath')
drain()
assert ENV['MK_baseScored'][1] and ENV['MK_done'][3] and ENV['MK_winner'][3] == 4
assert ENV['MK_paid'][1] and not ENV['MK_paid'][2]
ENV['CAS_winner'] = 1; call('CAS_EndMatch'); drain(); check_money(money)
assert all(ENV['MK_paid'][i] for i in range(1,ENV['MK_n']+1))
assert ENV['CAS_liability'] == 0

# Explicit challenge acceptance, rejection, expiry and final settlement.
reset(); money = all_money()
ENV['DU_opponent'][1] = 2; ENV['DU_pick'][1] = 1
call('DU_Offer',1)
assert ENV['FGA_gold'][1] == 950 and ENV['FGA_gold'][2] == 1000
call('DU_Accept',3); assert ENV['DU_state'][1] == 1
call('DU_Accept',2)
assert ENV['DU_state'][1] == 2 and ENV['FGA_gold'][2] == 950
call('DU_Finish',1,False); check_money(money)
assert ENV['FGA_gold'][1] == 1050 and ENV['FGA_gold'][2] == 950
call('DU_Finish',1,False); check_money(money)
reset(); money = all_money(); ENV['DU_opponent'][1] = 2; ENV['DU_pick'][1] = 1
call('DU_Offer',1); ENV['CAS_seconds'] = 31
call('DU_Accept',2); assert ENV['DU_state'][1] == 4
check_money(money)

# Capacity and batch stress: the 4,096th ticket is rejected without taking gold.
reset(); ENV['FGA_gold'][1] = 100000; ENV['CAS_amount'][1] = 10
money = all_money()
for ticket in range(4095):
    call('MK_Buy',1,1,ticket%12+1)
gold = ENV['FGA_gold'][1]
call('MK_Buy',1,1,1)
assert ENV['MK_n'] == 4095 and ENV['FGA_gold'][1] == gold
call('MK_Resolve',1,1)
call('MK_PayBatch')
assert sum(ENV['MK_paid'].values()) <= 64
drain(); check_money(money)
assert sum(ENV['MK_paid'].values()) == 4095 and ENV['CAS_liability'] == 0

# Single-block FFA uses player outcomes, and a draw refunds every winner ticket.
reset(); money = all_money()
ENV['FFEnd_BlockCount'] = lambda:1
call('MK_Refresh'); assert call('MK_FFA')
call('MK_Buy',1,5,2); locked = ENV['MK_return'][1]
ENV['CAS_winner'] = -2
call('CAS_EndMatch'); drain(); check_money(money)
assert ENV['FGA_gold'][1] == 950+locked
reset(); money = all_money()
call('MK_Buy',1,5,2)
ENV['CAS_winner'] = 0
call('CAS_EndMatch'); drain(); check_money(money)
assert ENV['FGA_gold'][1] == 1000

# Actual frame builders/renderers: card hiding, foreign view isolation, no wallet mutation.
reset(); frames.clear(); serial = 0
call('CAS_BuildPlayer',1); call('CAS_BuildPlayer',2)
ENV['CAS_view'][1] = 1
call('BJ_Wager',1); call('BJ_Deal',1)
ENV['BJ_reveal'][1] = False
snapshot = {k:copy.deepcopy(ENV[k]) for k in ('FGA_gold','CAS_escrow','CAS_bank','CAS_liability','BJ_card','BJ_shoe','BJ_pos','MK_n')}
call('CAS_Render',1)
assert frames[ENV['CAS_card'][19]]['texture'] == 'PokerUI\\back.blp'
assert frames[ENV['CAS_root'][1]]['visible'] is True
ENV['CAS_view'][2] = 1
call('CAS_Render',2)
assert frames[ENV['CAS_root'][2]]['visible'] is False
ENV['CAS_view'][1] = 2; call('CAS_Render',1)
assert all(not frames[ENV['CAS_card'][18+i]]['visible'] for i in range(18))
for view in (3,4,0):
    ENV['CAS_view'][1] = view
    call('CAS_Render',1)
def meaningful(value):
    return {k:v for k,v in value.items() if v} if isinstance(value,dict) else value
assert all(meaningful(ENV[k]) == meaningful(v) for k,v in snapshot.items()), 'Renderer mutated economy/rules'
assert not frames[ENV['CAS_root'][1]]['visible']
assert max((max(a.keys(),default=0) for a in (ENV['BJ_card'],ENV['BJ_shoe'],ENV['BJ_dealerCard'])),default=0) < 8192

# The modified poker renderer uses the same button factory. Check the actual
# zero-call / owed-call transition, including fill colors and label children.
import runpy
poker_rules = runpy.run_path(str(ROOT.parent/'observer-poker/test_rules.py'))
poker = poker_rules['env']
poker.update({k:v for k,v in ENV.items() if k.startswith(('Blz','CUI_','TEXT_JUSTIFY','FRAMEPOINT','ORIGIN_FRAME','FRAMEEVENT'))})
poker.update(CreateTrigger=lambda:1,TriggerAddAction=lambda *v:None,TriggerRegisterPlayerChatEvent=lambda *v:None,
    TimerStart=lambda *v:None,DestroyTimer=lambda *v:None,GetExpiredTimer=lambda:1,DisplayTimedTextToPlayer=lambda *v:None,
    GetLocalPlayer=lambda:0,Player=lambda p:p,I2R=float,PK_Eligible=lambda p:p == 0,
    PK_Click=lambda:None,PK_Chat=lambda:None,PK_Tick=lambda:None,CreateTimer=lambda:1)
poker_ui = (ROOT/'poker-ui.j').read_text()
for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',poker_ui):
    FUNCTIONS[m[1]] = m[0]
for name in ('PK_Texture','PK_Label','PK_ChipArt','PK_Button','PK_Render','PK_Start'):
    tree = ast.fix_missing_locations(Division().visit(ast.parse(translate(name))))
    poker['jdiv'] = jdiv
    exec(compile(tree,'poker UI '+name,'exec'),poker)
poker['PK_Start']()
poker['PK_Turn'][0] = 0
poker['PK_Paid'][0] = poker['PK_Paid'][1] = 10
poker['PK_Acted'][0] = False
poker['PK_Render'](0)
def button_fill(f):
    return frames[frames[f]['children'][0]]['texture']
def button_text(f):
    return frames[frames[f]['children'][1]]['text']
assert button_fill(poker['PK_Fold'][0]) == 'CasinoUI\\button1.blp'
assert button_fill(poker['PK_Raise'][0]) == 'CasinoUI\\button2.blp'
assert button_fill(poker['PK_Call'][0]) == 'CasinoUI\\button0.blp'
assert button_text(poker['PK_Call'][0]) == 'Check'
poker['PK_Paid'][1] = 40
poker['PK_Render'](0)
assert button_fill(poker['PK_Call'][0]) == 'CasinoUI\\button3.blp'
assert button_text(poker['PK_Call'][0]) == 'Call 30'
assert button_fill(ENV['CAS_button'][40+6]) == 'CasinoUI\\button1.blp'
assert button_fill(ENV['CAS_button'][40+7]) == 'CasinoUI\\button2.blp'

report = dict(actual_jass_random_blackjack_rounds=rounds,continuous_shoe_rounds=100,two_deck_shoe=True,soft_aces=True,natural_and_push_payouts=True,split_aces_and_double=True,community_turn_isolation=True,exhaustion_refunds=True,odds_movement_and_locked_tickets=True,cutoff_exact=True,any_base_kill_and_first_base_loss=True,ffa_and_draw_settlement=True,principal_and_debt_accounting=True,house_liability_backing=True,challenge_acceptance_expiry_settlement=True,ticket_capacity_and_batched_payouts=4095,renderer_pure_and_hole_card_hidden=True,engine_tested=False)
report['colored_poker_check_call_transition'] = True
(ROOT/'rule-tests.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
