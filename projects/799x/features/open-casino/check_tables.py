"""Run installed JASS table functions with deterministic Warcraft native mocks."""
import ast
from collections import defaultdict
from pathlib import Path
import random
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(sys.argv[1]).read_text(encoding='utf8')
FUN = {m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',SOURCE)}
harness = ast.parse((ROOT/'development/footmen/casino-v1/test_casino.py').read_text(encoding='utf8'))
harness.body = [n for n in harness.body if getattr(n,'name',None) in ('expr','translate','jdiv','Division')]
translator = dict(ast=ast,re=re,FUNCTIONS=FUN)
exec(compile(harness,'JASS translator','exec'),translator)
names = '''PK_Score5 PK_Score PK_Random PK_Card PK_Pay PK_Render PK_Submit PK_Tick PK_Click PK_Sync
           BJ_Value BJ_CardSum BJ_Recount BJ_Payout BJ_Hit BJ_DealerHit BJ_Shuffle BJ_Draw BJ_SeatCount
           BJ_Deal BJ_Next BJ_Finish BJ_Reset BJ_Wager BJ_Action BJ_Tick BJ_SeatTotal BJ_Roster
           CAS_Random CAS_Flush CAS_Credit CAS_Reserve CAS_Settle'''.split()
names += [name for name in FUN if name.startswith('OP_')]
code = {}
for name in names:
    tree=ast.fix_missing_locations(translator['Division']().visit(ast.parse(translator['translate'](name))))
    code[name]=compile(tree,name,'exec')


def game():
    e=dict(jdiv=translator['jdiv'],IMinBJ=min,IMaxBJ=max,ModuloInteger=lambda a,b:a%b,I2S=str,
           S2I=lambda s:int(s) if s.isdigit() else 0,Player=int,GetPlayerId=int,GetPlayerName=lambda v:'P'+str(v),
           PF_Log=lambda *args:None,TimerStart=lambda *args:None,PauseTimer=lambda t:None,
           SubString=lambda s,a,b:s[a:b],StringLength=len,CUI_Value=str,CAS_Name=lambda s:'P'+str(s-1),
           CAS_ended=False,CAS_bank=50000,CAS_liability=0,PK_Seed=91,CAS_seed=301,
           viewer=0,missing=set(),frames={})
    for typ,key in re.findall(r'(?m)^[ \t]*(integer|boolean|string|framehandle) array (\w+)',SOURCE):
        e[key]=defaultdict(str if typ=='string' else int)
        if typ=='framehandle':
            for i in range(600):
                e[key][i]=(key,i)
    for typ,key,value in re.findall(r'(?m)^[ \t]*(integer|boolean|string|timer) (OP_\w+|BJ_ShoeSize) = ([^\r\n]+)',SOURCE):
        e[key]=eval(translator['expr'](value))
    e['PK_Eligible']=lambda v:0<=v<24 and v not in e['missing']
    e['CasinoWalletDelta']=lambda p,amt:e['CAS_gold'].__setitem__(p,e['CAS_gold'][p]+amt)
    e['LoanAward']=e['CasinoWalletDelta']
    e['GetLocalPlayer']=lambda:e['viewer']
    e['GetTriggerPlayer']=e['GetLocalPlayer']
    e['BlzGetTriggerFrame']=lambda:e['clicked']
    e['BlzGetTriggerSyncData']=lambda:e['packet']
    e['BlzSendSyncData']=lambda prefix,data:e.update(packet=data)
    e['BlzFrameGetText']=lambda f:e['frames'][f,'text'][0]
    e['CAS_ShowButton']=lambda s,id,on:e['frames'].__setitem__((s,id),on)
    for func,prop in [('BlzFrameSetVisible','visible'),('BlzFrameSetText','text'),('BlzFrameSetTexture','texture'),
                      ('CUI_Text','text'),('CUI_Paint','paint'),('PK_ChipArt','chips'),('BlzFrameSetFocus','focus')]:
        e[func]=lambda f,*args,key=prop:e['frames'].__setitem__((f,key),args)
    for item in code.values():exec(item,e)
    for v in range(24):
        e['CAS_ready'][v+1]=True
        e['CAS_gold'][v+1]=5000
        e['CAS_amount'][v+1]=20
        e['PK_Started'][v]=True
        e['PK_Default'][v]=100
        e['PK_Version'][v]=1
        e['PK_Hidden'][v]=True
    return e


def seat(e,ids,amount=500):
    for v in ids:e['OP_Join'](v,amount)


def deal(e):
    before=e['OP_Hand']
    for i in range(12):
        e['PK_Tick']()
        if before!=e['OP_Hand']: return
    raise AssertionError('hand did not start')


def finish(e):
    for _ in range(25):
        if e['OP_Phase']!=2:return
        e['OP_ScoreTick']()
    assert e['OP_Phase']==0


def click(e,v,key,digits=''):
    e.update(viewer=v,clicked=e[key][v])
    e['frames'][e['PK_Input'][v],'text']=(digits,)
    e['PK_Click']()
    e['PK_Sync']()


def conservation(e):
    assert sum(e['PK_Stack'].values())+sum(e['PK_Total'].values())+sum(e['CAS_gold'].values())==24*5000
    assert sum(e['CAS_escrow'].values())==sum(e['PokerBuyIn'].values())
    assert min(e['PK_Stack'].values(),default=0)>=0


# Normal UI entry, shared blinds/board, private pockets, spectator joining during a hand.
e=game()
for v in (0,4,9,16):e['PK_Hidden'][v]=False
for v,amt in ((0,101),(4,501),(9,1500)):click(e,v,'PK_Next',str(amt))
deal(e)
assert (e['OP_Button'],e['OP_Turn'],e['PK_Paid'][4],e['PK_Paid'][9])==(0,0,5,10)
click(e,16,'PK_Next','200')
assert e['OP_Seats']==4 and not e['OP_Dealt'][16]
click(e,4,'PK_Raise','100');assert e['OP_Turn']==0
click(e,0,'PK_Raise','37');old=e['packet']
click(e,4,'PK_Call');click(e,9,'PK_Call');assert e['OP_Street']==1
e.update(viewer=0,packet=old);e['PK_Sync']();assert e['OP_Turn']==4
for v in (0,4,9,16):
    e['viewer']=v
    e['PK_Render'](v)
    frames=e['frames']
    for i in (0,1):
        art=frames[e['PK_Face'][v*9+i],'texture'][0]
        assert art.endswith(('empty' if v==16 else 'card'+str(e['PK_Cards'][2*v+i]))+'.blp')
    for i in range(3):
        assert frames[e['PK_Face'][v*9+4+i],'texture'][0].endswith('card'+str(e['OP_Board'][i])+'.blp')
    assert 'P4' in frames[e['PK_BotStack'][v],'text'][0] and 'P16' in frames[e['PK_BotStack'][v],'text'][0]
# Leave mid-hand. Other seats continue and the late arrival plays the following hand.
e['OP_Leave'](9)
while e['OP_Phase']==1:
    v=e['OP_Turn']
    e['OP_Action'](v,'f' if e['OP_Leaving'][v] else 'c',0)
finish(e)
assert not e['PokerBuyIn'][9] and e['PokerBuyIn'][0] and e['PokerBuyIn'][4]
deal(e);assert e['OP_Dealt'][16]
conservation(e)
# One shared hand for all 12 player slots. At the engine limit all 24 can buy
# in; one rotating slot waits and all 23 active hands use distinct cards.
for size in (2,12,23,24):
    e=game();seat(e,range(size));deal(e)
    expected=min(size,23)
    cards=[e['PK_Cards'][v*2+i] for v in range(size) if e['OP_Dealt'][v] for i in range(2)]
    cards.extend(e['OP_Board'][i] for i in range(5))
    assert len(set(cards))==2*expected+5
    if size==2:assert e['OP_Turn']==e['OP_Button'] and e['PK_Paid'][e['OP_Button']]==5
    old_rest=e['OP_Rest']
    actions=0
    while e['OP_Phase']==1:
        e['OP_Action'](e['OP_Turn'],'c',0)
        actions+=1
    assert actions==expected*4
    finish(e);conservation(e)
    if size==24:
        deal(e);assert e['OP_Rest']!=old_rest and e['OP_Dealt'][old_rest]
# Explicit layered pot with unequal all-ins, dead money, a tied side pot,
# a one-chip odd split and uncalled excess.
e=game()
for v,(n,live,score) in enumerate([(20,True,900),(61,True,800),(100,True,800),(60,False,0),(101,True,100)]):
    e['PK_Total'][v]=n;e['OP_Live'][v]=live;e['OP_Score'][v]=score
e['OP_Button']=1;e['OP_AwardPots']()
# 100 to seat 0; 160 and 3 split between 1 and 2, next odd chip to seat 2;
# 78 to seat 2, final uncalled chip to seat 4.
assert [e['OP_Award'][v] for v in range(5)]==[100,81,160,0,1]
# A real three-way showdown: aces beat kings and queens for the main pot;
# kings take the side pot, and the largest stack gets its unmatched chips back.
e=game()
for v,amt in enumerate((100,200,500)):e['OP_Join'](v,amt)
deal(e)
for v,rank in enumerate((12,11,10)):
    e['PK_Cards'][v*2]=rank
    e['PK_Cards'][v*2+1]=rank+13
for i,card in enumerate((0,16,32,47,7)):e['OP_Board'][i]=card
for v,move,target in ((0,'r',100),(1,'r',200),(2,'r',500)):
    # The third player can only call an all-in when no opponent can act again.
    if v==2:
        assert not e['OP_CanRaise'](v)
        e['OP_Action'](v,'c',0)
    else:e['OP_Action'](v,move,target)
finish(e)
assert [e['PK_Stack'][v] for v in range(3)]==[300,200,300]
conservation(e)
# Short all-in raises do not automatically reopen betting, cumulative full raises do.
e=game()
for v,amt in enumerate((500,103,130,500)):e['OP_Join'](v,amt)
deal(e) # button 0, SB 1, BB 2, first 3
e['OP_Action'](3,'r',60);e['OP_Action'](0,'c',0)
e['OP_Action'](1,'r',103)
assert not e['OP_CanRaise'](3)
e['OP_Action'](2,'r',130)
assert e['OP_Turn']==3 and e['OP_CanRaise'](3)
e['OP_Action'](3,'r',179);assert e['OP_Turn']==3
e['OP_Action'](3,'r',180);assert e['OP_Turn']==0
e['OP_EndMatch']();conservation(e);assert all(e['CAS_gold'][v+1]==5000 for v in range(4))
# Exercise actual betting sequences, timeouts, folding, disconnects, and cash-out.
rng=random.Random(7560)
for n in range(2,25):
    e=game()
    for v in range(n):e['OP_Join'](v,rng.randint(100,1500))
    deal(e)
    if n>2:e['missing'].add((e['OP_Turn']+1)%n)
    for _ in range(500):
        if e['OP_Phase']!=1:break
        v=e['OP_Turn'];roll=rng.random()
        if roll<.22 and e['OP_CanRaise'](v):
            cap=e['PK_Paid'][v]+e['PK_Stack'][v]
            e['OP_Action'](v,'r',rng.randint(min(cap,e['OP_Bet']+e['OP_MinRaise']),cap))
        elif roll<.40:e['OP_Action'](v,'f',0)
        elif roll<.50:
            e['OP_Clock']=1;e['PK_Tick']()
        else:e['OP_Action'](v,'c',0)
        conservation(e)
    assert e['OP_Phase']!=1
    finish(e);conservation(e);e['OP_EndMatch']();conservation(e)
    assert e['OP_Seats']==0
# Every blackjack slot shares table 0; a mid-hand arrival cannot alter the
# current wagers. Exercise turn ownership, dealer rule, results, and escrow.
for ids in ([23],[1,5,11,12,17,23],list(range(7)),list(range(12)),list(range(13)),list(range(24))):
    e=game();e['BJ_Shuffle'](0)
    for v in ids:e['BJ_Wager'](v+1)
    assert e['BJ_SeatCount']()==len(ids) and e['BJ_phase'][0]==1
    for _ in range(12):e['BJ_Tick']()
    assert e['BJ_ShoeSize']==(104 if len(ids)<=6 else 208 if len(ids)<=12 else 416)
    assert all(e['BJ_count'][v*2]==2 for v in ids) and e['BJ_dealerCount'][0]==2
    if len(ids)<24:
        other=next(v for v in range(24) if v not in ids);e['BJ_Wager'](other+1)
        assert e['BJ_bet'][other*2]==0
    e['BJ_Page'][1]=1;e['BJ_Roster'](1)
    page=(1%max(1,(len(ids)+5)//6))*6
    assert 'P'+str(ids[page]) in e['frames'][e['CAS_row'][6],'text'][0]
    for _ in range(300):
        phase=e['BJ_phase'][0]
        if phase==4:break
        if phase==2:
            h=e['BJ_turn'][0]-1;current=h//2
            e['BJ_Action']((current+1)%24+1,2)
            assert e['BJ_turn'][0]==h+1
            if current==5:
                e['missing'].add(5);e['BJ_Tick']()
            else:e['BJ_Action'](current+1,1 if e['BJ_total'][h]<17 else 2)
        else:
            before=e['BJ_dealerCount'][0];total=e['BJ_dealerTotal'][0]
            e['BJ_Tick']()
            if total>=17:assert e['BJ_dealerCount'][0]==before
    assert e['BJ_phase'][0]==4 and not e['BJ_error'][0] and not sum(e['CAS_escrow'].values())
    assert sum(e['CAS_gold'].values())+e['CAS_bank']==170000
# The last seat can split and double independently, including its second hand.
e=game()
for v in range(24):e['BJ_Wager'](v+1)
e['BJ_ShoeSize']=416;e['BJ_Shuffle'](0)
# Two 8s to the final bettor, dealer stands on 19. Every other seat has 2+3.
for i in range(24):
    e['BJ_shoe'][i]=6 if i==23 else 0
    e['BJ_shoe'][25+i]=19 if i==23 else 1
for i,c in ((24,8),(49,7),(50,2),(51,3),(52,6),(53,2)):e['BJ_shoe'][i]=c
e['BJ_Deal'](0)
for v in range(23):e['BJ_Action'](v+1,2)
assert e['BJ_turn'][0]==47
e['BJ_Action'](24,4)
assert e['BJ_split'][46] and e['BJ_split'][47]
e['BJ_Action'](24,3);assert e['BJ_turn'][0]==48
e['BJ_Action'](24,3)
assert [e['BJ_bet'][h] for h in (46,47)]==[40,40] and e['BJ_phase'][0]==3
for _ in range(4):e['BJ_Tick']()
assert e['BJ_phase'][0]==4 and e['BJ_dealerTotal'][0]==19 and e['CAS_escrow'][24]==0
# Shared match-end refund covers pending poker joins and all blackjack wagers.
e=game();seat(e,range(12));deal(e);seat(e,[23]);e['BJ_Shuffle'](0)
for v in range(24):e['BJ_Wager'](v+1)
e['OP_EndMatch']();e['BJ_Finish'](0,True);e['BJ_Finish'](0,True)
assert all(e['CAS_gold'][v+1]==5000 for v in range(24)) and not sum(e['CAS_escrow'].values())
print('Passed shared poker seating, card privacy, late joins, 2-24 seats, full betting rounds, side pots, short raises, departures and wallet conservation.')
print('Passed shared blackjack at 1, 6, 7, 12, 13 and 24 seats, visible roster pages, turn ownership, dealer stands, and match-end refunds.')
