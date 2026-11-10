"""Apply the user's October 29 item balance request to v40, preserving other members."""
import balance_core as c
import copy,json,struct,hashlib,re
from pathlib import Path

OUT=c.ROOT/'balance-v41';OUT.mkdir(exist_ok=True)
TARGET=c.PROJECT/'release/FF799X_Rx_ItemBalance_v41.w3x'
recipes=json.loads((c.ROOT/'recipe-audit.json').read_text(encoding='utf-8'))
sold_ids={i['id'] for i in json.loads((c.PROJECT/'item-wiki/dist/data.json').read_text(encoding='utf-8'))['items']}
recipes=[r for r in recipes if r['recipe_id'] in sold_ids]
direct={'rde3':25,'bgst':25,'ratf':25,'I03C':25,'hval':75,'evtl':50,'I00F':50,'cnob':250,'I04B':250,'rag1':250,'I00D':50,'stwa':100,'clfm':100,'I01S':150,'rst1':250,'I00E':100,'I01I':500}
total_targets={'I00W':500,'I04A':500,'I00X':250,'I00V':250,'I00U':250,'I01R':500}
prices={u:int(c.num('item',u,'igol'))+delta for u,delta in direct.items()}
price=lambda u:prices.get(u,int(c.num('item',u,'igol')))
for r in recipes:
 uid=r['result']['id'];rid=r['recipe_id'];oldtotal=r['total_gold']
 newparts=sum(price(i['id']) for i in r['ingredient_list'])
 if uid in total_targets:
  target=oldtotal+total_targets[uid]
  newrecipe=target-newparts
  if rid in direct:assert newrecipe==price(rid),(uid,newrecipe,price(rid))
  prices[rid]=newrecipe
 total=newparts+price(rid)
 if total!=oldtotal:prices[uid]=total
 prices.setdefault(uid,int(c.num('item',uid,'igol')))
prices={u:p for u,p in prices.items() if p!=int(c.num('item',u,'igol'))}
assert prices['I00K']==1400 and prices['I00M']==1500
assert prices['I00B']==1875 and prices['I00L']==1725
assert prices['I01S']==700 and prices['I01R']==3850
assert prices['I01H']==3275
files=['war3map.w3t','war3mapSkin.w3t','war3map.w3a','war3mapSkin.w3a']
objects={}
for fn in files:
 p=OUT/('before-'+fn);p.write_bytes(c.archive(fn));objects[fn]=c.objdata.load(str(p))
def index(o):return {(e['newId'] if e['newId']!='\0'*4 else e['oldId']):e for t in o['tables'] for e in t}
edits=[]
def put(fn,uid,field,value,typ=3,level=None,ptr=0,only_existing=False):
 o=objects[fn];entry=index(o).get(uid)
 if not entry:
  if only_existing:return
  parent=c.parents[('ability' if fn.endswith('w3a') else 'item',uid)]
  entry=dict(oldId=parent,newId=uid if uid!=parent else '\0'*4,flags=1,extra=0,mods=[])
  o['tables'][int(uid!=parent)].append(entry)
 mod=next((m for m in entry['mods'] if m['id']==field and (level is None or m.get('level')==level)),None)
 if mod is None and only_existing:return
 before=mod['value'] if mod else None
 if mod:mod['value']=value
 else:
  mod=dict(id=field,type=typ,value=value,end='00000000')
  if level is not None:mod.update(level=level,ptr=ptr)
  entry['mods'].append(mod)
 if before!=value:edits.append(dict(file=fn,id=uid,field=field,level=level,before=before,after=value))
for uid,p in prices.items():
 put('war3map.w3t',uid,'igol',p,0)
 put('war3mapSkin.w3t',uid,'igol',p,0,only_existing=True)
# A0B9 is shared with the dormant Wand of Interchange; isolate Frosty's nerf.
assert ('ability','AFv1') not in c.parents
for fn in ['war3map.w3a','war3mapSkin.w3a']:
 old=index(objects[fn]).get('A0B9')
 if old:
  new=copy.deepcopy(old);new['newId']='AFv1';objects[fn]['tables'][1].append(new)
put('war3map.w3a','AFv1','Uav1',0.5,2,1,1)
put('war3mapSkin.w3a','AFv1','Uav1',0.5,2,1,1,only_existing=True)
put('war3map.w3a','A0KF','Iatt',140,0,1,1)
put('war3mapSkin.w3a','A0KF','Iatt',140,0,1,1,only_existing=True)
put('war3map.w3t','I00W','iabi',','.join('AFv1' if a=='A0B9' else a for a in c.abil_list('I00W')))
put('war3mapSkin.w3t','I00W','iabi',','.join('AFv1' if a=='A0B9' else a for a in c.abil_list('I00W')),only_existing=True)
tips={}
for r in recipes:
 rid=r['recipe_id'];uid=r['result']['id']
 if rid not in prices and uid not in prices:continue
 total=sum(price(i['id']) for i in r['ingredient_list'])+price(rid)
 for item in [rid,uid]:
  for field in ['utub','ides']:
   text=c.value('item',item,field) or c.value('item',item,'utub') or ''
   if item==rid:
    text=re.sub(r'Recipe: \d+ gold',f'Recipe: {price(rid)} gold',text)
    text=re.sub(r'Total acquisition cost: \d+ gold',f'Total acquisition cost: {total} gold',text)
   if uid=='I00W':text=text.replace('+160 attack damage (150 damage ability plus 10 from frost orb)','+150 attack damage (140 damage ability plus 10 from frost orb)').replace('60% melee life steal','50% melee life steal')
   text=re.sub(r'\|n\|nTotal acquisition cost: \d+ gold\.$','',text)
   if item==uid:text+=f'|n|nTotal acquisition cost: {total} gold.'
   tips[item,field]=text
   put('war3mapSkin.w3t',item,field,text)
   put('war3map.w3t',item,field,text,only_existing=True)
payloads={}
for fn,o in objects.items():
 b=c.objdata.dump(o)
 if b!=c.archive(fn):
  (OUT/fn).write_bytes(b);assert c.objdata.dump(c.objdata.load(str(OUT/fn)))==b;payloads[fn]=b
def encrypt(data,key):
 seed=0xEEEEEEEE;result=bytearray()
 for (v,) in struct.iter_unpack('<I',data):
  seed=(seed+c.mpq.encryption_table[0x400+(key&255)])&0xffffffff
  result+=struct.pack('<I',v^((key+seed)&0xffffffff))
  key=(((~key<<21)+0x11111111)|(key>>11))&0xffffffff;seed=(v+seed+(seed<<5)+3)&0xffffffff
 return result
raw=bytearray(c.MAP.read_bytes());offset=c.mpq.header['offset'];blocks=list(c.mpq.block_table)
for fn,b in payloads.items():
 i=c.mpq.get_hash_table_entry(fn).block_table_index
 blocks[i]=blocks[i]._replace(offset=len(raw)-offset,archived_size=len(b),size=len(b),flags=0x81000000);raw+=b
table_offset=len(raw)-offset;raw+=encrypt(b''.join(struct.pack('<4I',*b) for b in blocks),c.mpq._hash('(block table)','TABLE'))
struct.pack_into('<I',raw,offset+8,len(raw)-offset);struct.pack_into('<I',raw,offset+20,table_offset)
TARGET.write_bytes(raw);new=c.MPQArchive(str(TARGET),listfile=False)
for fn,b in payloads.items():assert new.read_file(fn)==b
changed={tuple(c.mpq.get_hash_table_entry(fn)[:4]) for fn in payloads}
def members(a):
 out={}
 for h in a.hash_table:
  if h.block_table_index>=len(a.block_table):continue
  b=a.block_table[h.block_table_index];a.file.seek(a.header['offset']+b.offset)
  out[tuple(h[:4])]=(b.size,b.flags,a.file.read(b.archived_size))
 return out
before=members(c.mpq);after=members(new);assert before.keys()==after.keys()
assert all(before[k]==after[k] for k in before if k not in changed)
# Verify object-field scope independently, including the cloned ability.
def fields(o):return {(uid,m['id'],m.get('level',0),m.get('ptr',0)):m['value'] for uid,e in index(o).items() for m in e['mods']}
for fn in payloads:
 a=fields(c.objdata.load(str(OUT/('before-'+fn))));b=fields(objects[fn])
 for key in a.keys()|b.keys():
  if a.get(key)==b.get(key):continue
  uid,field,_,_=key
  assert (fn.endswith('w3t') and (field in ['utub','ides'] or (field=='igol' and uid in prices) or (field=='iabi' and uid=='I00W'))) or (fn.endswith('w3a') and (uid=='AFv1' or (uid=='A0KF' and field=='Iatt'))),(fn,key)
assert next(m['value'] for m in index(objects['war3map.w3a'])['A0B9']['mods'] if m['id']=='Uav1')>.59
# Merge only requested fields into editable sources; do not replace newer unrelated source work.
for fn in payloads:
 path=c.PROJECT/'src'/fn
 if not path.exists():continue
 source=c.objdata.load(str(path));source_index=index(source);before_source=path.read_bytes()
 for change in [e for e in edits if e['file']==fn and e['id']!='AFv1']:
  uid=change['id'];target=index(objects[fn])[uid];entry=source_index.get(uid)
  if entry is None:entry=copy.deepcopy(target);source['tables'][int(entry['newId']!='\0'*4)].append(entry);source_index[uid]=entry
  replacement=next(m for m in target['mods'] if m['id']==change['field'] and (change['level'] is None or m.get('level')==change['level']))
  entry['mods']=[m for m in entry['mods'] if not(m['id']==change['field'] and (change['level'] is None or m.get('level')==change['level']))]+[copy.deepcopy(replacement)]
 clone=index(objects[fn]).get('AFv1')
 if clone:
  if 'AFv1' in source_index:assert source_index['AFv1']==clone
  else:source['tables'][1].append(copy.deepcopy(clone))
 backup=OUT/('source-before-'+fn)
 if not backup.exists():backup.write_bytes(before_source)
 path.write_bytes(c.objdata.dump(source))
report=dict(sourceMap=c.MAP.name,sourceSha256=hashlib.sha256(c.MAP.read_bytes()).hexdigest(),outputMap=TARGET.name,outputSha256=hashlib.sha256(raw).hexdigest(),prices=[dict(id=u,name=c.name('item',u),before=int(c.num('item',u,'igol')),after=p,delta=p-int(c.num('item',u,'igol'))) for u,p in sorted(prices.items())],frosty=dict(damageBefore=160,damageAfter=150,lifestealBefore=60,lifestealAfter=50,newLifestealAbility='AFv1',sharedOriginalPreserved=True),changedArchiveMembers=list(payloads),unchangedArchiveMembers=len(before)-len(changed),edits=edits)
report['craftedCosts']=[dict(id=r['result']['id'],name=r['result_name'],before=r['total_gold'],after=sum(price(i['id']) for i in r['ingredient_list'])+price(r['recipe_id']),recipeId=r['recipe_id'],recipeBefore=r['recipe_gold'],recipeAfter=price(r['recipe_id'])) for r in recipes if r['result']['id'] in prices]
(OUT/'balance-changes.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
TARGET.with_suffix('.sha256').write_text(report['outputSha256']+'  '+TARGET.name+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='edits'},indent=2))
