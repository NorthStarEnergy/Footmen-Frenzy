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
(R/'behavior-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'scope':'Translated kill handler with mocked natives; damage expression evaluated directly. No Warcraft engine test.'},indent=2))
print(len(checks),'checks passed')

