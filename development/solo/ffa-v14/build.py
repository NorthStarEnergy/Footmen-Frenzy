from pathlib import Path
import sys,struct,re,json,ctypes as c,shutil,subprocess,hashlib,copy,math
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive
B=R/'base';O=R/'src'
for d in [B,O,R/'release']:d.mkdir(exist_ok=True)
shutil.copyfile(W/'ffa-v13/release/Solo_Foots_8P_FFA_v13.w3x',R/'baseline.w3x');archive.extract(R/'baseline.w3x',B)
s=(B/'war3map.j').read_text();pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
def put(n,f):
 global s
 s=s.replace(funcs(s)[n],f)
def props(o,id):return {m[0].decode():m[4] for m in (o.find(id) or {}).get('mods',[])}
def slk(path):
 cells={};x=y=1
 for line in Path(path).read_text().splitlines():
  if not line.startswith('C;'):continue
  for k in line.split(';')[1:]:
   if k.startswith('X'):x=int(k[1:])
   elif k.startswith('Y'):y=int(k[1:])
   elif k.startswith('K'):cells[x,y]=k[1:].strip('"')
 headers={x:v for (x,y),v in cells.items() if y==1}
 return {cells[1,y]:{headers[x]:v for (x,yy),v in cells.items() if yy==y and x in headers} for y in sorted({y for x,y in cells}) if y>1 and (1,y) in cells}
standard=slk(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport\item-audit\game-data\base-itemdata.slk')
custom=slk(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\799x-backport\item-audit\game-data\custom-itemdata.slk');standard.update(custom)
u=Obj(B/'war3map.w3u');skin=Obj(B/'war3mapSkin.w3u');items=Obj(B/'war3map.w3t')
# Include standard unmodified items too; map overrides always take priority.
prices=[]
ids=set(standard)|{(o['new'] if o['new']!=bytes(4) else o['old']).decode() for t in items.tables for o in t}
for id in sorted(ids):
 obj=items.find(id);base=obj['old'].decode() if obj else id
 old=props(items,id).get('igol',int(standard.get(base,{}).get('goldcost',0)))
 new=1500 if id=='I004' else 1250 if id=='I00H' else math.floor(old*.9+.5) if old<=7000 else old
 if new!=old:items.set(id,'igol',new);prices.append([id,old,new])
bases=set(re.findall(r"set udg_base_type\[\d+\]='(....)'",s));towers={'hwtw'}
while True:
 new=towers|{v for id in towers for v in props(u,id).get('uupt','').split(',') if v}
 if new==towers:break
 towers=new
defensive=towers.copy()
st={int(k):v for k,v in re.findall(r'STRING (\d+)[^{]*\{\s*(.*?)\s*\}',(B/'war3map.wts').read_text(),re.S)}
for table in u.tables:
 for obj in table:
  id=(obj['new'] if obj['new']!=bytes(4) else obj['old']).decode();name=props(skin,id).get('unam',props(u,id).get('unam',''))
  if name.startswith('TRIGSTR_'):name=st.get(int(name[8:]),name)
  if 'tower' in name.lower():towers.add(id)
balance=slk(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots\audit\game-data\base-unitbalance.slk')
hp=[];tech=[]
for id in sorted(bases|towers):
 obj=u.find(id);p=props(u,id);old=p.get('uhpm',props(u,obj['old'].decode() if obj else id).get('uhpm',int(float(balance.get(obj['old'].decode() if obj else id,{}).get('HP',0)))))
 if old<=0:
  assert obj is None,(id,'missing HP')
  continue
 u.set(id,'uhpm',round(old*1.1));hp.append([id,old,round(old*1.1)])
 if id in bases and p.get('ugol')==600:u.set(id,'ugol',500);tech.append(id)
u.set('hwtw','ugol',250);u.set('hwtw','ulum',0);u.set('hwtw','ureq','')
u.set('h000','ubui','hhou,hwtw');u.set('h000','uabi',props(u,'h000')['uabi'].replace('AIbk','AB14'))
a=Obj(B/'war3map.w3a',True);askin=Obj(B/'war3mapSkin.w3a',True)
for table in [a,askin]:
 obj=copy.deepcopy(table.find('AIbk'));obj['new']=b'AB14'
 for m in obj['mods']:m[5]=b'AB14'
 table.tables[1].append(obj)
 for key,val in [('ahky','Z'),('abpx',1),('abpy',2),('atp1','Blink (Z)')]:table.set('AB14',key,val,level=1 if key=='atp1' else 0)
# Native human Build uses B in the bottom-right; Blink occupies the adjacent free slot.
for table in [u,skin]:
 table.set('hwtw','uhot','T');table.set('hwtw','ubpx',1);table.set('hwtw','ubpy',0)
for table,name in [(u,'war3map.w3u'),(skin,'war3mapSkin.w3u'),(items,'war3map.w3t'),(a,'war3map.w3a'),(askin,'war3mapSkin.w3a')]:table.save(O/name)
s=re.sub(r'(set udg_startgold=)\d+',r'\g<1>200',s)
s=re.sub(r'(call StartTimerBJ\(udg_spawnTimer, true, )([\d.]+)',lambda m:m[1]+f'{float(m[2])/1.2:.6f}',s)
s+='\n'+(R/'construction.j').read_text().replace('TOWER_TYPES',' or '.join("id=='"+id+"'" for id in sorted(defensive)))
put('SF_Initialize',funcs(s)['SF_Initialize'].replace('    call F8_InitShops()','    call F14_Init()\n    call F8_InitShops()'))
title='Solo Foots 8P FFA + King v14';s=re.sub(r'call SetMapName\("[^\"]+"\)',f'call SetMapName("{title}")',s)
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):];tail=tail[:tail.index('# Terrain-derived BLP1 minimaps')]+tail[tail.index('work=Path('):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v14.w3x').replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','')
report={'prices':prices,'health':hp,'first_tier_costs':tech,'spawn_rate_multiplier':1.2};exec(tail)




