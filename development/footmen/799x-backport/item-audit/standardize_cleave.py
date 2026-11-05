import cleave_core as c
import json,copy,hashlib,shutil
ah=c.ah
OUT=c.ROOT/'cleave-v43';OUT.mkdir(exist_ok=True)
TARGET=c.PROJECT/'release/FF799X_Rx_CleaveRanges_v43.w3x'
ids=['A05W','ANca','A08O','ADrc','AMuc']
def index(o):return {(e['newId'] if e['newId']!='\0'*4 else e['oldId']):e for t in o['tables'] for e in t}
def setmod(e,field,level,value,typ):
 m=next((m for m in e['mods'] if m['id']==field and m['level']==level),None)
 if m:m['value']=value
 else:e['mods'].append(dict(id=field,type=typ,level=level,ptr=0,value=value,end='00000000'))
payloads={};edits=[]
for fn in ['war3map.w3a','war3mapSkin.w3a']:
 p=OUT/('before-'+fn);p.write_bytes(c.archive(fn));o=c.objdata.load(str(p));original=copy.deepcopy(o)
 for aid in ids:
  entry=index(o).get(aid)
  if entry is None:continue
  for lev in range(1,int(c.num('ability',aid,'alev'))+1):
   if fn=='war3map.w3a' or any(m['id']=='aare' and m['level']==lev for m in entry['mods']):setmod(entry,'aare',lev,250.0,2)
   if fn=='war3mapSkin.w3a' or any(m['id']=='aub1' and m['level']==lev for m in entry['mods']):
    dmg=round(c.num('ability',aid,'nca1',lev)*100,4)
    setmod(entry,'aub1',lev,f'Basic attacks also deal {dmg:g}% of the damage dealt to other eligible ground enemies within 250 range of the attacked unit.',3)
  for m in entry['mods']:
   before=next((x for x in index(original)[aid]['mods'] if x['id']==m['id'] and x['level']==m['level']),None)
   if before!=m:
    assert m['id'] in ['aare','aub1'];edits.append(dict(file=fn,ability=aid,field=m['id'],level=m['level'],before=before['value'] if before else None,after=m['value']))
 b=c.objdata.dump(o);(OUT/fn).write_bytes(b);assert c.objdata.dump(c.objdata.load(str(OUT/fn)))==b;payloads[fn]=b
 # Merge only the requested fields into editable source; preserve concurrent work.
 sp=c.PROJECT/'src'/fn
 if not sp.exists():continue
 so=c.objdata.load(str(sp));backup=OUT/('source-before-'+fn)
 if not backup.exists():backup.write_bytes(sp.read_bytes())
 for change in [e for e in edits if e['file']==fn]:
  ent=index(so).get(change['ability'])
  if ent is not None:setmod(ent,change['field'],change['level'],change['after'],2 if change['field']=='aare' else 3)
 sp.write_bytes(c.objdata.dump(so))
shutil.copyfile(c.MAP,TARGET)
h=ah.c.c_void_p();assert ah.storm.SFileOpenArchive(str(TARGET),0,0,ah.c.byref(h))
for fn in payloads:assert ah.storm.SFileAddFileEx(h,str(OUT/fn),fn.encode(),0x80000200,2,2)
assert ah.storm.SFileCloseArchive(h)
assert ah.storm.SFileOpenArchive(str(TARGET),0,0x100,ah.c.byref(h))
for fn,b in payloads.items():assert ah.read_storm(h,fn)==b
assert ah.storm.SFileCloseArchive(h)
old=ah.archive(c.MAP);new=ah.archive(TARGET);before=ah.entries(old);after=ah.entries(new)
skip=set()
for fn in [*payloads,'(listfile)','(attributes)','(signature)']:
 e=old.get_hash_table_entry(fn)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(after.get(k)==v for k,v in before.items() if k not in skip)
sha=hashlib.sha256(TARGET.read_bytes()).hexdigest();TARGET.with_suffix('.sha256').write_text(sha+'  '+TARGET.name+'\n')
report=dict(source=c.MAP.name,map=TARGET.name,sha256=sha,area=250,abilities=ids,edits=edits,preservedMembers=len(before.keys()-skip),livePlaytest=False)
(OUT/'changes.json').write_text(json.dumps(report,indent=2))
# Refresh the hero section of the complete report; item values remain the verified v41 values.
D=c.PROJECT/'item-wiki/dist';p=D/'item-value-model.json';model=json.loads(p.read_text())
for hero in model['heroes']:
 aid=hero['ability'];hero['area']=[250]*len(hero['area']);hero['cleave']=[round(c.num('ability',aid,'nca1',lev)*100,4) for lev in range(1,len(hero['area'])+1)]
 hero['raw']=c.ability(aid,True)
 for field in hero['raw']['fields']:
  if field['raw']=='aare':field.update(value=250,source='v43 standardized cleave area')
model['heroSourceMap']=TARGET.name
model['heroNotes']=[n for n in model['heroNotes'] if not any(x in n for x in ['Myrmidon reaches','Pit Lord and Crazy Cat share','Demon Knight and Dr. Mundo receive'])]
model['heroNotes'].insert(0,'v43: all six audited cleaving heroes use 250 area at every rank, matching base-game Cleaving Attack. Pit Lord and Crazy Cat share ANca. Damage percentages are preserved from v42; Demon Knight and Mundo use 40/50/60%.')
model['notes']=[n for n in model['notes'] if 'Hero cleave findings remain' not in n]
model['notes'].append('v43 hero cleave areas and damage ranks are verified from the v42 baseline plus this range patch. Other hero-state notes retain their earlier audit and have not been re-audited here. Item valuation remains based on unchanged v41 item data.')
p.write_text(json.dumps(model,indent=2));(c.ROOT/'item-value-model.json').write_text(json.dumps(model,indent=2))
s=(c.ROOT/'build_static_report.py').read_text(encoding='utf-8').replace('Hero findings retain their separately identified v37 source.','Cleave areas and damage ranks reflect the v43 range patch; other hero-state notes retain their earlier audit.')
(c.ROOT/'build_static_report.py').write_text(s,encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='edits'},indent=2))
