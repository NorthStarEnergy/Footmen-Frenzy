from pathlib import Path
import re,json
R=Path(__file__).resolve().parent
s=(R/'src/war3map.j').read_text(encoding='utf8')
f=re.search(r'function VG_ClassicKill takes.*?endfunction',s,re.S)[0]
lines=['def kill():']; indent=1
for line in f.splitlines()[1:-1]:
 line=line.strip()
 if line=='endif':indent-=1;continue
 line=re.sub(r'^local \w+ ', '',line)
 line=re.sub(r'^(set |call )','',line).replace('null','None')
 if line.startswith('if '):line=line[:-5]+':'
 lines.append('    '*indent+line)
 if line.endswith(':'):indent+=1
units={1:{'kind':'HVg1','owner':0},2:{'owner':1}}
state={};shown=[];killer=1
E=dict(GetKillingUnit=lambda:killer,GetTriggerUnit=lambda:2,GetUnitTypeId=lambda u:units.get(u,{}).get('kind'),IsUnitIllusion=lambda u:units.get(u,{}).get('illusion',False),IsUnitEnemy=lambda u,p:units[u]['owner']!=p,GetOwningPlayer=lambda u:units[u]['owner'],IsUnitType=lambda u,t:units[u].get(t,False),UNIT_TYPE_HERO='hero',UNIT_TYPE_STRUCTURE='structure',GetHandleId=lambda u:u,VG_Hash=state,LoadInteger=lambda h,u,k:h.get((u,k),0),SaveInteger=lambda h,u,k,v:h.update({(u,k):v}),VG82_UpdateCounter=lambda u:shown.append(state[u,702]))
E['LoadUnitHandle']=lambda h,u,k:h.get((u,k))
exec('\n'.join(lines),E)
checks=[]
def check(n,b):
 assert b,n
 checks.append(n)
E['kill']();check('unit kill adds exactly 1',state[1,702]==1)
units[2]['hero']=True;E['kill']();check('hero kill adds exactly 5, not 6',state[1,702]==6)
units[2]['hero']=False
for key in ['illusion','structure']:
 units[2][key]=True;E['kill']();check(key+' victim excluded',state[1,702]==6);units[2][key]=False
units[2]['owner']=0;E['kill']();check('friendly excluded',state[1,702]==6);units[2]['owner']=1
units[1]['illusion']=True;E['kill']();check('illusion killer excluded',state[1,702]==6);units[1]['illusion']=False
units[2]['summoned']=True;E['kill']();check('enemy summoned unit counts',state[1,702]==7)
units[3]={'kind':'HVg1','owner':0};killer=3;E['kill']();check('multiple Veigars independent',state[3,702]==1 and state[1,702]==7)
killer=None;E['kill']();check('no killer safe',state[1,702]==7)
check('counter reflects latest kill',shown==[1,6,7,1])
check('no INT reward', 'SetHeroInt' not in f)
check('stack write only on kill',len(re.findall(r'call SaveInteger\(VG_Hash, GetHandleId\(u\), 702,',s))==1)
check('no stack key removal',not re.search(r'RemoveSaved\w+\([^\n]*702',s))
for rank in range(1,7):
 expr=re.search(r'set damage = (80\.0[^\n]+)',s)[1]
 env=dict(rank=rank,caster=1,GetHeroInt=lambda u,b:20,true=True,I2R=float,LoadInteger=E['LoadInteger'],VG_Hash=state,GetHandleId=lambda u:u)
 check('rank '+str(rank)+' applies exact flat bonus',eval(expr,env)==80+70*rank+12+7)
check('non-Z kills grant no ultimate stacks',state.get((1,703),0)==0)
killer=1
state[1,701]=2
units[2]['hero']=False
E['kill']();check('Z unit kill adds 1 ultimate damage',state[1,703]==1)
units[2]['hero']=True
E['kill']();check('Z hero kill adds 5 ultimate damage',state[1,703]==6)
state.pop((1,701))
E['kill']();check('other hero kill adds no ultimate damage',state[1,703]==6)
state[1,701]=99
E['kill']();check('different victim during Z damage adds no ultimate stack',state[1,703]==6)
state.pop((1,701))
for key in ['illusion','structure']:
 state[1,701]=2;units[2][key]=True
 E['kill']();check('Z '+key+' excluded from ultimate stacks',state[1,703]==6)
 units[2][key]=False
state.pop((1,701))
killer=3;state[3,701]=2
E['kill']();check('ultimate stacks independent per Veigar',state[3,703]==5 and state[1,703]==6)
cast=re.search(r'function VG_ClassicCast takes.*?endfunction',s,re.S)[0]
z=cast.split("if spell == 'AVgq' then")[1].split('elseif')[0]
check('Z kill marker brackets synchronous damage',z.index('SaveUnitHandle')<z.index('UnitDamageTarget')<z.index('RemoveSavedHandle'))
v=cast.split('elseif')[1]
check('V never sets Z marker','SaveUnitHandle' not in v)
expr=re.search(r'set damage = (250\.0[^\n]+)',v)[1]
for rank in range(1,4):
 env.update(rank=rank,enemyInt=30)
 check('ultimate rank '+str(rank)+' adds exact Z-kill bonus',eval(expr,env)==250+300*rank+24+24+6)
check('V stacks only written in kill handler',len(re.findall(r'call SaveInteger\(VG_Hash, GetHandleId\(u\), 703,',s))==1)
check('no ultimate stack reset',not re.search(r'RemoveSaved\w+\([^\n]*703',s))
(R/'behavior-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'scope':'Translated kill handler with mocked natives; damage expression evaluated directly. No Warcraft engine test.'},indent=2))
print(len(checks),'checks passed')


