from pathlib import Path
import sys,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'hero-polish'),str(ROOT/'mini-foots/tools')]
import archive_helpers as ah
import objdata
project=ROOT/'799x-backport'; audit=project/'item-audit'; out=audit/'myrmidon-v44';out.mkdir(exist_ok=True)
src=project/'release/FF799X_Rx_CleaveRanges_v43.w3x';target=project/'release/FF799X_Rx_Myrmidon_Cleave_v44.w3x'
levels=[30,40,50,60,70,80]
def index(o):return {(e['newId'] if e['newId']!='\0'*4 else e['oldId']):e for t in o['tables'] for e in t}
def modify(entry,field,level,value,typ):
 m=next((m for m in entry['mods'] if m['id']==field and m.get('level')==level),None)
 if m:m['value']=value
 else:entry['mods'].append(dict(id=field,type=typ,level=level,ptr=1 if field=='nca1' else 0,value=value,end='00000000'))
h=ah.c.c_void_p();assert ah.storm.SFileOpenArchive(str(src),0,0x100,ah.c.byref(h))
payloads={}
for fn in ['war3map.w3a','war3mapSkin.w3a']:
 raw=ah.read_storm(h,fn);(out/('before-'+fn)).write_bytes(raw);o=objdata.load(str(out/('before-'+fn)));entry=index(o)['A05W']
 for level,pct in enumerate(levels,1):
  if fn=='war3map.w3a':modify(entry,'nca1',level,pct/100,2)
  else:modify(entry,'aub1',level,f'Basic attacks also deal {pct}% of the damage dealt to other eligible ground enemies within 250 range of the attacked unit.',3)
 payloads[fn]=objdata.dump(o);(out/fn).write_bytes(payloads[fn]);assert objdata.dump(objdata.load(str(out/fn)))==payloads[fn]
 # Carry the same change into an existing editable source without replacing other changes.
 path=project/'src'/fn
 if path.exists():
  source=objdata.load(str(path));ent=index(source).get('A05W')
  if ent:
   (out/('source-before-'+fn)).write_bytes(path.read_bytes())
   for level,pct in enumerate(levels,1):
    if fn=='war3map.w3a':modify(ent,'nca1',level,pct/100,2)
    else:modify(ent,'aub1',level,f'Basic attacks also deal {pct}% of the damage dealt to other eligible ground enemies within 250 range of the attacked unit.',3)
   path.write_bytes(objdata.dump(source))
assert ah.storm.SFileCloseArchive(h)
assert not target.exists();shutil.copyfile(src,target)
assert ah.storm.SFileOpenArchive(str(target),0,0,ah.c.byref(h))
for fn in payloads:assert ah.storm.SFileAddFileEx(h,str(out/fn),fn.encode(),0x80000200,2,2)
assert ah.storm.SFileCloseArchive(h)
assert ah.storm.SFileOpenArchive(str(target),0,0x100,ah.c.byref(h))
for fn,data in payloads.items():assert ah.read_storm(h,fn)==data
assert ah.storm.SFileCloseArchive(h)
before=ah.entries(ah.archive(src));after=ah.entries(ah.archive(target));a=ah.archive(src);skip=set()
for fn in [*payloads,'(listfile)','(attributes)','(signature)']:
 e=a.get_hash_table_entry(fn)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(after.get(k)==v for k,v in before.items() if k not in skip)
def fields(o):return {(e['newId'] if e['newId']!='\0'*4 else e['oldId'],m['id'],m['level'],m['ptr']):m['value'] for t in o['tables'] for e in t for m in e['mods']}
for fn in payloads:
 old=fields(objdata.load(str(out/('before-'+fn))));new=fields(objdata.load(str(out/fn)))
 for key in old.keys()|new.keys():
  if old.get(key)!=new.get(key):assert key[0]=='A05W' and key[1] in ('nca1','aub1'),key
 if fn=='war3map.w3a':
  for level,pct in enumerate(levels,1):assert abs(new['A05W','nca1',level,1]-pct/100)<1e-6
sha=hashlib.sha256(target.read_bytes()).hexdigest();target.with_suffix('.sha256').write_text(sha+'  '+target.name+'\n')
(out/'changes.json').write_text(json.dumps(dict(source=src.name,map=target.name,sha256=sha,hero='Myrmidon',ability='A05W',cleavePercent=levels,range=250,preservedMembers=len(before.keys()-skip),livePlaytest=False),indent=2))
p=project/'item-wiki/dist/item-value-model.json';model=json.loads(p.read_text(encoding='utf-8'))
hero=next(x for x in model['heroes'] if x['id']=='N02O');hero['cleave']=levels
for f in hero['raw']['fields']:
 if f['raw'].lower()=='nca1' and 1<=f['level']<=6:f['value']=levels[f['level']-1]/100;f['source']='v44 Myrmidon cleave balance'
model['heroSourceMap']=target.name
model['heroNotes']=[n.replace('v43:','v44:').replace('Damage percentages are preserved from v42;','Myrmidon now matches Pit Lord and Crazy Cat at 30/40/50/60/70/80%.') for n in model['heroNotes']]
model['notes']=[n.replace('v43 hero cleave areas and damage ranks are verified from the v42 baseline plus this range patch.','v44 hero cleave areas and damage ranks reflect the v43 range patch and v44 Myrmidon multiplier change.') for n in model['notes']]
p.write_text(json.dumps(model,indent=2),encoding='utf-8');(audit/'item-value-model.json').write_text(json.dumps(model,indent=2),encoding='utf-8')
generator=audit/'build_static_report.py';s=generator.read_text(encoding='utf-8').replace('Cleave areas and damage ranks reflect the v43 range patch;','Cleave areas and damage ranks reflect the v44 map;');generator.write_text(s,encoding='utf-8')
print('PASS: six Myrmidon ranks, tooltips, unchanged map members and report model; map SHA-256:',sha)
