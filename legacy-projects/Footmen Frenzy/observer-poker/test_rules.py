"""Execute the actual JASS rules translated to Python, with JASS integer division.
No claim of Warcraft engine/UI or network validation.
"""
from pathlib import Path
from collections import defaultdict,Counter
from itertools import combinations
import re,random,ast,json
ROOT=Path(__file__).resolve().parent
source=(ROOT/'poker.j').read_text()
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',source)}
def expr(s):
    s=re.sub(r'//.*','',s).strip()
    for old,new in [('true','True'),('false','False'),('null','None')]:s=re.sub(r'\b'+old+r'\b',new,s)
    s=re.sub(r'\bfunction (\w+)',r'\1',s)
    return s
def translate(name):
    lines=functions[name].splitlines();args=re.search(r'takes (.*?) returns',lines[0])[1].strip()
    args=[] if args=='nothing' else [a.split()[-1] for a in args.split(',')]
    locals_=re.findall(r'local \w+ (\w+)',functions[name])
    assigned=set(re.findall(r'^\s*set (\w+)',functions[name],re.M))-set(locals_)-set(args)
    out=['def '+name+'('+','.join(args)+'):'];depth=1
    if assigned:out.append('    global '+','.join(sorted(assigned)))
    for line in lines[1:-1]:
        line=expr(line)
        if not line:continue
        if line in ['endif','endloop']:depth-=1;continue
        if line.startswith('elseif '):depth-=1;out.append('    '*depth+'elif '+line[7:-5]+':');depth+=1
        elif line=='else':depth-=1;out.append('    '*depth+'else:');depth+=1
        elif line.startswith('if ') and line.endswith(' then'):out.append('    '*depth+line[:-5]+':');depth+=1
        elif line=='loop':out.append('    '*depth+'while True:');depth+=1
        elif line.startswith('exitwhen '):out.append('    '*depth+'if '+line[9:]+': break')
        elif line.startswith('local '):
            m=re.match(r'local \w+ (\w+)(.*)',line);out.append('    '*depth+m[1]+(m[2] if m[2].strip() else '=None'))
        elif line.startswith(('set ','call ')):out.append('    '*depth+line.split(' ',1)[1])
        else:out.append('    '*depth+line)
    return '\n'.join(out)
class IntegerDiv(ast.NodeTransformer):
    def visit_BinOp(self,node):
        self.generic_visit(node)
        if isinstance(node.op,ast.Div):node.op=ast.FloorDiv()
        return node
env=dict(IMinBJ=min,IMaxBJ=max,ModuloInteger=lambda a,b:a%b,I2S=str,SubString=lambda s,a,b:s[a:b],PK_Seed=81731)
for typ,name in re.findall(r'(\w+) array (PK_\w+)',(ROOT/'poker-globals.j').read_text()):env[name]=defaultdict(lambda:0)
for name in functions:
    if name in ['PK_Eligible','PK_Render','PK_Click','PK_Chat','PK_Tick','PK_Button','PK_Start','PK_PauseUnit','PK_DetectSolo','PK_Init']:continue
    tree=ast.fix_missing_locations(IntegerDiv().visit(ast.parse(translate(name))))
    exec(compile(tree,'translated '+name,'exec'),env)
env['PK_Eligible']=lambda p:True
def call(name,*args):return env['PK_'+name](*args)
def card(s):return '23456789TJQKA'.index(s[0])+13*'CDHS'.index(s[1])
def score(cards):return call('Score5',*[card(c) for c in cards.split()])
fixtures=['2C 5D 7H 9S JC','2C 2D 7H 9S JC','2C 2D 7H 7S JC','2C 2D 2H 9S JC','AC 2D 3H 4S 5C','2C 5C 7C 9C JC','2C 2D 2H 9S 9C','2C 2D 2H 2S JC','9C TC JC QC KC']
for category,hand in enumerate(fixtures):assert score(hand)//759375==category,(category,hand)
assert score('AC 2D 3H 4S 5C')<score('2C 3D 4H 5S 6C')
assert score('AC AD KH QS JC')>score('AS AH KD QC TC')
assert score('AC AD KH KS 2C')>score('AS AH QD QC KC')
assert score('AC AD AH KS KC')>score('AS AH AD QC QH')
# Independent tuple-based rank oracle, including best five of seven.
def oracle(cs):
    ranks=sorted([c%13+2 for c in cs],reverse=True);counts=Counter(ranks)
    groups=sorted(((n,r) for r,n in counts.items()),reverse=True)
    flush=len({c//13 for c in cs})==1
    unique=sorted(counts);straight=0
    if unique==[2,3,4,5,14]:straight=5
    elif len(unique)==5 and unique[-1]-unique[0]==4:straight=unique[-1]
    if flush and straight:return (8,straight)
    if groups[0][0]==4:return (7,groups[0][1],groups[1][1])
    if [g[0] for g in groups]==[3,2]:return (6,groups[0][1],groups[1][1])
    if flush:return (5,*ranks)
    if straight:return (4,straight)
    if groups[0][0]==3:return (3,groups[0][1],*sorted([r for r in ranks if r!=groups[0][1]],reverse=True))
    if [g[0] for g in groups[:2]]==[2,2]:return (2,*sorted([groups[0][1],groups[1][1]],reverse=True),groups[2][1])
    if groups[0][0]==2:return (1,groups[0][1],*sorted([r for r in ranks if r!=groups[0][1]],reverse=True))
    return (0,*ranks)
rng=random.Random(309)
for _ in range(1000):
    cs=rng.sample(range(52),9)
    for i,c in enumerate(cs):env['PK_Cards'][i]=c
    scores=[call('Score',0,s,5) for s in [0,1]]
    expected=[max(oracle(c) for c in combinations(cs[s*2:s*2+2]+cs[4:],5)) for s in [0,1]]
    assert (scores[0]>scores[1])-(scores[0]<scores[1])==(expected[0]>expected[1])-(expected[0]<expected[1])
def reset(p=0,a=500,b=500):
    env['PK_Stack'][p*2]=a;env['PK_Stack'][p*2+1]=b
    call('Deal',p)
def conservation(p=0):
    x=p*2
    assert sum(env[k][x]+env[k][x+1] for k in ['PK_Stack','PK_Total'])==1000
    assert min(env['PK_Stack'][x],env['PK_Stack'][x+1])>=0
    assert len({env['PK_Cards'][p*9+i] for i in range(9)})==9
for hand in range(1000):
    reset();moves=0
    while env['PK_Turn'][0]>=0:
        seat=env['PK_Turn'][0]
        if seat==1:call('Bot',0)
        else:
            before=env['PK_Turn'][0],env['PK_Paid'][0],env['PK_Paid'][1]
            call('Action',0,seat,rng.choice([0,1,1,1,2,3]))
            after=env['PK_Turn'][0],env['PK_Paid'][0],env['PK_Paid'][1]
            if before==after:call('Action',0,seat,1)
        conservation();moves+=1;assert moves<100
    old=env['PK_Stack'][0],env['PK_Stack'][1]
    call('Action',0,0,3)
    assert old==(env['PK_Stack'][0],env['PK_Stack'][1]),'post-settlement duplicate'
# Unequal stacks, short blinds and all-in call/runout.
for a,b in [(1,999),(7,993),(993,7),(30,970),(970,30)]:
    reset(a=a,b=b)
    for _ in range(30):
        seat=env['PK_Turn'][0]
        if seat<0:break
        call('Action',0,seat,1)
        conservation()
    assert env['PK_Turn'][0]==-1
# Short all-in cannot reopen action. Effective-stack cap prevents a HU side pot.
reset(a=40,b=960)
env['PK_Turn'][0]=0;env['PK_Paid'][0]=20;env['PK_Paid'][1]=25
env['PK_LastRaise'][0]=10;env['PK_Acted'][0]=True
old=env['PK_Stack'][0];call('Action',0,0,3);assert env['PK_Stack'][0]==old
# Two independent tables; actions at one never change the other's chips/cards.
reset(0);reset(12)
snapshot=[env[k][24+i] for k in ['PK_Stack','PK_Total','PK_Paid'] for i in [0,1]]+[env['PK_Cards'][108+i] for i in range(9)]
call('Action',0,env['PK_Turn'][0],0)
assert snapshot==[env[k][24+i] for k in ['PK_Stack','PK_Total','PK_Paid'] for i in [0,1]]+[env['PK_Cards'][108+i] for i in range(9)]
# Bot action is invariant when only human and unrevealed board cards change.
reset();env['PK_Turn'][0]=1
import copy
state={k:copy.deepcopy(v) for k,v in env.items() if k.startswith('PK_') and not callable(v)}
call('Bot',0);decision=(env['PK_Turn'][0],env['PK_Stack'][1],env['PK_Note'][0])
env.update(copy.deepcopy(state))
for i in [0,1,4,5,6,7,8]:env['PK_Cards'][i]=(env['PK_Cards'][i]+11)%52
call('Bot',0);assert decision==(env['PK_Turn'][0],env['PK_Stack'][1],env['PK_Note'][0])
report=dict(hand_rank_categories=9,independent_seven_card_comparisons=1000,simulated_hands=1000,edge_cases=['wheel','kickers','short blinds','effective all-in','short raise reopening','table isolation','duplicate action','bot hidden-card independence'],engine_tested=False)
(ROOT/'rule-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
