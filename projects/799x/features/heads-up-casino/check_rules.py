"""Execute the staged JASS using the project's existing JASS-to-Python rule-test translator."""
import ast
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
script = Path(sys.argv[1]).read_text(encoding='utf8')
functions = {m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',script)}
# The historical suite runs its old fixture on import. Reuse its pure translator
# definitions without importing those obsolete maps or executing its old tests.
harness = ast.parse((ROOT/'development/footmen/casino-v1/test_casino.py').read_text(encoding='utf8'))
harness.body = [node for node in harness.body if getattr(node,'name',None) in ('expr','translate','jdiv','Division')]
engine = dict(ast=ast,re=re,FUNCTIONS=functions)
exec(compile(harness,'casino test translator','exec'),engine)
env = dict(jdiv=engine['jdiv'],IMinBJ=min,IMaxBJ=max,IAbsBJ=abs,ModuloInteger=lambda x,y:x%y,
           I2S=str,S2I=lambda s:int(s) if s.isdigit() else 0,Player=int,GetPlayerName=lambda p:f'Player{p}',
           GetPlayerId=int,DisplayTimedTextToPlayer=lambda *args:None,PF_Log=lambda *args:None,
           CAS_ended=False,CAS_bank=50000,CAS_liability=0,PK_Queue=0,PK_Seed=91)
for typ,name in re.findall(r'(?m)^[ \t]*(integer|boolean|string|framehandle) array (\w+)',script):
    env[name] = defaultdict(str if typ=='string' else int)
leavers=set()
env['PK_Eligible']=lambda v:0<=v<24 and v not in leavers
env['CasinoWalletDelta']=lambda s,d:env['CAS_gold'].__setitem__(s,env['CAS_gold'][s]+d)
env['LoanAward']=env['CasinoWalletDelta']
names = '''PK_Random PK_Card PK_Score5 PK_Score PK_Category PK_BoardCount PK_Pay CAS_Flush CAS_Credit
CAS_Reserve CAS_Settle PK_PlayerAt PK_SeatName PK_TableChanged PK_Top PK_End PK_Showdown PK_Advance
PK_Deal PK_Action PK_Return PK_CloseTable PK_CancelQueue PK_Join PK_Bot PK_Submit PK_Tick
BJ_Value BJ_CardSum BJ_Recount BJ_Draw BJ_DealerHit BJ_Hit BJ_Payout BJ_Finish BJ_Next BJ_Action'''.split()
for name in names:
    tree=ast.fix_missing_locations(engine['Division']().visit(ast.parse(engine['translate'](name))))
    exec(compile(tree,name,'exec'),env)
env.update(PK_Refresh=lambda v:None,PK_Render=lambda v:None)
def call(name,*args):
    return env[name](*args)
def A(name):
    return env[name]
for v in range(12):
    A('PK_Started')[v]=True
    A('CAS_ready')[v+1]=True
    A('CAS_gold')[v+1]=2500
    A('PK_Turn')[v]=-1

# Odd buy-ins, range errors, cancellation, unequal stacks, click isolation.
for amount in (0,99,1501):
    call('PK_Join',2,amount,False)
assert env['PK_Queue']==0 and A('CAS_gold')[3]==2500
call('PK_Join',2,101,False)
call('PK_Join',2,101,False)
assert env['PK_Queue']==3 and A('CAS_gold')[3]==2399
call('PK_CancelQueue',2)
assert A('CAS_gold')[3]==2500 and A('CAS_escrow')[3]==0
call('PK_Join',2,1500,False)
call('PK_Join',7,123,False)
t=2; x=4
assert A('PK_Table')[7]==3 and A('PK_Guest')[t]==8 and A('PK_Turn')[t]==1
assert A('PK_Paid')[x]==10 and A('PK_Paid')[x+1]==5
assert len(set(A('PK_Cards')[t*9+i] for i in range(9)))==9
call('PK_Submit',2,'f','0')
call('PK_Submit',7,'r','19')
call('PK_Submit',7,'r','124')
assert A('PK_Turn')[t]==1 and A('PK_Paid')[x+1]==5
call('PK_Submit',7,'r','37')
assert A('PK_LastRaise')[t]==27 and A('PK_Paid')[x+1]==37
call('PK_Submit',2,'r','63')
assert A('PK_Turn')[t]==0
call('PK_Submit',2,'r','1467')
call('PK_Submit',7,'c','0')
assert A('PK_Turn')[t]==-1 and A('PK_LastPot')[t]==246 and A('PK_Reveal')[t]
assert A('PK_Stack')[x]+A('PK_Stack')[x+1]==1623 and min(A('PK_Stack')[x],A('PK_Stack')[x+1])>=0
call('PK_Submit',7,'l','0')
assert A('CAS_gold')[3]+A('CAS_gold')[8]==5000 and env['CAS_bank']==50000 and env['CAS_liability']==0
assert not A('CAS_escrow')[3] and not A('CAS_escrow')[8]
# Full orbit, alternating blinds, folds, consecutive ready clicks, showdown tie.
call('PK_Join',0,500,False); call('PK_Join',1,500,False)
call('PK_Submit',1,'c','0'); call('PK_Submit',0,'c','0')
assert A('PK_Street')[0]==1 and A('PK_Turn')[0]==0 and A('PK_Paid')[0]==0
for street in (1,2,3):
    assert A('PK_Street')[0]==street and A('PK_Turn')[0]==0
    if street==3:
        for i,val in enumerate([13,14,26,27,8,9,10,11,12]):
            A('PK_Cards')[i]=val
    call('PK_Submit',0,'c','0');call('PK_Submit',1,'c','0')
assert A('PK_Turn')[0]==-1 and A('PK_Stack')[0]==500 and A('PK_Stack')[1]==500
call('PK_Submit',0,'n','0');call('PK_Submit',0,'n','0')
assert A('PK_Turn')[0]==-1
call('PK_Submit',1,'n','0')
assert A('PK_Turn')[0]==0 and A('PK_Hand')[0]==2 and A('PK_Paid')[0]==5
# A departed human forfeits committed chips. Repeated ticks cannot pay twice.
leavers.add(0);call('PK_Tick');call('PK_Tick');leavers.clear()
assert A('CAS_gold')[1]==2495 and A('CAS_gold')[2]==2505
# House practice, timeout and match-end void settle the correct wallets once.
call('PK_Join',4,111,True)
assert env['CAS_liability']==111 and A('PK_Table')[4]==5
for _ in range(34):call('PK_Tick')
call('PK_CloseTable',4,True)
assert env['CAS_liability']==0 and A('CAS_gold')[5]+env['CAS_bank']==52500
call('PK_Join',5,123,False);call('PK_Join',9,244,False)
call('PK_CloseTable',5,True)
assert A('CAS_gold')[6]==2500 and A('CAS_gold')[10]==2500
# Every possible two-card dealer hand, every possible next card, all four suits.
def total(cards):
    values=[min(10,c%13+2) if c%13!=12 else 1 for c in cards]
    low=sum(values)
    return low+10 if 1 in values and low<=11 else low
for a in range(52):
    for b in range(52):
        for c in range(13):
            cards=[a,b]
            A('BJ_dealerCount')[1]=2
            A('BJ_dealerCard')[22]=a; A('BJ_dealerCard')[23]=b
            A('BJ_pos')[1]=0; A('BJ_shoe')[104]=c
            call('BJ_DealerHit',1)
            if total(cards)<17:cards.append(c)
            assert A('BJ_dealerCount')[1]==len(cards) and A('BJ_dealerTotal')[1]==total(cards)
            assert A('BJ_pos')[1]==len(cards)-2
for cards in ((12,12,7),(12,12,12,8),(12,12,12,12,9),(12,4),(8,10)):
    A('BJ_count')[0]=len(cards)
    for i,c in enumerate(cards):A('BJ_card')[i]=c
    call('BJ_Recount',0)
    assert A('BJ_total')[0]==total(cards)
for args,out in [((21,True,20,False,100),250),((21,True,21,True,100),100),((21,False,21,True,100),0),((21,False,20,False,100),200),((18,False,18,False,100),100),((22,False,22,False,100),0)]:
    assert call('BJ_Payout',*args)==out
# Only keep hitting when a live hand actually needs a comparison.
A('BJ_state')[0]=4;A('BJ_bet')[0]=100;A('BJ_owner')[0]=-1
call('BJ_Next',0)
assert A('BJ_phase')[0]==4
# Confirm pocket-card privacy for both views and the actual control wiring.
frames={}
def frame_prop(key):
    def put(frame,*values):
        frames[frame,key]=values
    return put
for key in ('PK_Dialog','PK_Title','PK_HumanLabel','PK_BotLabel','PK_HumanStack','PK_BotStack','PK_PotLabel','PK_Prompt','PK_Input','PK_CallLabel','PK_Fold','PK_Call','PK_Raise','PK_Allin','PK_Next','PK_Alternate','PK_Status','PK_Text','PK_HumanChips','PK_BotChips','PK_PotChips','PK_HumanDealer','PK_BotDealer','PK_Face'):
    for v in range(220):
        A(key)[v]=(key,v)
env.update(BlzFrameSetText=frame_prop('text'),BlzFrameSetVisible=frame_prop('visible'),BlzFrameSetTexture=frame_prop('texture'),
           CUI_Text=frame_prop('text'),CUI_Paint=frame_prop('paint'),PK_ChipArt=frame_prop('chips'),CUI_Value=str,
           GetLocalPlayer=lambda:0,GetTriggerPlayer=lambda:env['viewer'],BlzGetTriggerFrame=lambda:env['clicked'],
           BlzFrameSetFocus=frame_prop('focus'),BlzFrameGetText=lambda f:frames[f,'text'][0],
           BlzGetTriggerSyncData=lambda:env['packet'],BlzSendSyncData=lambda prefix,packet:env.update(packet=packet),
           SubString=lambda s,a,b:s[a:b],StringLength=len)
for name in ('PK_Render','PK_Refresh','PK_Click','PK_Sync'):
    tree=ast.fix_missing_locations(engine['Division']().visit(ast.parse(engine['translate'](name))))
    exec(compile(tree,name,'exec'),env)
def click(v,key,amount=None):
    env.update(viewer=v,GetLocalPlayer=lambda:v,clicked=A(key)[v])
    if amount is not None:
        frames[A('PK_Input')[v],'text']=(str(amount),)
    call('PK_Click')
    call('PK_Sync')
for v in (0,1):
    A('PK_Default')[v]=100
    call('PK_Render',v)
click(0,'PK_Next',107);click(1,'PK_Next',900)
for viewer in (0,1):
    for i in (0,1):
        assert frames[A('PK_Face')[viewer*9+i],'texture'][0].endswith('card'+str(A('PK_Cards')[viewer*2+i])+'.blp')
        assert frames[A('PK_Face')[viewer*9+i+2],'texture'][0].endswith('back.blp')
turn=A('PK_Turn')[0]
click(turn,'PK_Raise',39)
assert A('PK_Paid')[turn]==39
old_packet=env['packet']
click(1-turn,'PK_Call')
env.update(viewer=turn,packet=old_packet)
call('PK_Sync')
assert A('PK_Street')[0]==1 and A('PK_Paid')[turn]==0
# Ace splits receive one card apiece and a split 21 never becomes a natural.
def start_hand(cards):
    s=1; t=1; h=12
    A('BJ_table')[s]=t; A('BJ_seat')[s]=6; A('BJ_owner')[6]=s; A('BJ_turn')[t]=h+1
    A('BJ_phase')[t]=2; A('BJ_state')[h]=1; A('BJ_state')[h+1]=0
    A('BJ_bet')[h]=20; A('BJ_bet')[h+1]=0; A('BJ_split')[h]=False; A('BJ_count')[h]=2
    A('BJ_pos')[t]=0;A('BJ_shoe')[104]=8; A('BJ_shoe')[105]=4
    A('BJ_card')[h*22],A('BJ_card')[h*22+1]=cards
    call('BJ_Recount',h)
start_hand((12,25));call('BJ_Action',1,4)
assert [A('BJ_state')[h] for h in (12,13)]==[2,2] and A('BJ_phase')[1]==3
assert [A('BJ_total')[h] for h in (12,13)]==[21,17] and A('BJ_bet')[13]==20
start_hand((2,3));call('BJ_Action',1,3)
assert A('BJ_bet')[12]==40 and A('BJ_count')[12]==3 and A('BJ_state')[12]==2
# A canceled card order cannot apply a card. A committed one applies once,
# after endcast, even when an earlier attack lands during the handoff.
saved={}; callbacks=[]; casts=[]; guard=[]
env.update(TF_PendingCard=1,GetHandleId=lambda h:h,GetTriggerUnit=lambda:73,GetSpellTargetUnit=lambda:81,
           GetSpellAbilityId=lambda:env['spell'],CreateTimer=lambda:201,GetExpiredTimer=lambda:201,
           DestroyTimer=lambda t:None,TimerStart=lambda t,dt,rep,fn:callbacks.append(fn),
           FlushChildHashtable=lambda tab,k:[saved.pop(key) for key in list(saved) if key[:2]==(tab,k)],
           TFP_TF_Alive=lambda u:True,TF33_Cast=lambda *args:casts.append(args),GetUnitTypeId=lambda u:'HTf1',
           GetOwningPlayer=lambda u:0,IsUnitIllusion=lambda u:False,SetUnitCreepGuard=lambda u,b:guard.append((u,b)),
           RemoveGuardPosition=lambda u:guard.append(u))
for kind in ('Integer','Boolean','UnitHandle'):
    env['Save'+kind]=lambda t,k,f,v:saved.__setitem__((t,k,f),v)
    env['Load'+kind]=lambda t,k,f:saved.get((t,k,f),0)
for kind in ('Integer','Boolean'):
    env['RemoveSaved'+kind]=lambda t,k,f:saved.pop((t,k,f),None)
for name in ('TF_IsCardOrder','TF_CardChannel','TF_CardEffect','TF_ApplyCardCast','TF_CardEnd','TF_ClearPlayerGuard'):
    tree=ast.fix_missing_locations(engine['Division']().visit(ast.parse(engine['translate'](name))))
    exec(compile(tree,name,'exec'),env)
for spell in ('ATf2','ATf3','ATf4','ATf5','ATf6','ATf7','ATf8'):
    env['spell']=spell
    call('TF_CardChannel'); call('TF_CardEnd')
    assert not callbacks and not saved
    call('TF_CardChannel');call('TF_CardEffect')
    assert not callbacks
    call('TF_CardEnd');call('TF_CardEnd')
    assert len(callbacks)==1
    callbacks.pop()()
    assert casts[-1]==(73,81,spell) and not saved
assert len(casts)==7
call('TF_ClearPlayerGuard',73)
assert guard==[(73,False),73]
assert 'EVENT_PLAYER_HERO_LEVEL' in functions['TF33_Init'] and 'EVENT_PLAYER_HERO_SKILL' in functions['TF33_Init']
assert 'CreateUnit' not in functions['TF33_Cast'].split('elseif HaveSavedHandle')[0]
print("Twisted Fate interrupted/completed card orders and player guard hooks passed.")
print("Both poker views, exact-raise button, stale-click rejection, blackjack splits and doubles passed.")
print("Poker matchmaking, wallets, turns, raises, showdown, ties, timeouts and departure passed.")
print("35,152 dealer draw decisions, soft aces, payouts and natural-only settlement passed.")
