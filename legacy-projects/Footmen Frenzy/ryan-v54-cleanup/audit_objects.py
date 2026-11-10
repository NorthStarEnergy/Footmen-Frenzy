import sys,re,json,csv
from pathlib import Path
R=Path(__file__).resolve().parent; W=R.parent; O=R/'audit';O.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c,archive,objdata,functions
p=R/'release/FF799X_Rx_UI_Startup_Clean_v55.w3x';a=archive(p);h=c.c_void_p();assert storm.SFileOpenArchive(str(p),0,0x100,c.byref(h))
names=['war3map.'+x for x in ['w3u','w3t','w3a','w3h','w3q','w3b','w3d']]; blobs={}
for n in set(names+['war3map.j','war3map.wct','war3map.wtg','war3map.wts','war3mapUnits.doo','war3map.doo']):
 if a.get_hash_table_entry(n):
  try:blobs[n]=read_storm(h,n)
  except AssertionError:pass
storm.SFileCloseArchive(h)
s=blobs['war3map.j'].decode('latin1');(O/'war3map.j').write_text(s,encoding='utf8')
fs=functions(s)
edges={n:set(re.findall(r'\b[A-Za-z_]\w*\b',b[b.find('\n')+1:]))&fs.keys() for n,b in fs.items()}
roots={'main','config'}&fs.keys();reach=set();todo=list(roots)
while todo:
 n=todo.pop()
 if n in reach:continue
 reach.add(n);todo.extend(edges[n]-reach)
unreach=sorted(fs.keys()-reach)
dynamic=[x.strip() for x in s.splitlines() if 'ExecuteFunc(' in x]
rows=[];objs={};counts={}
wts=blobs.get('war3map.wts',b'').decode('latin1');strings=dict(re.findall(r'STRING\s+(\d+)\s*\{\s*(.*?)\s*\}',wts,re.S))
for ext,kind in [('w3u','units'),('w3t','items'),('w3a','abilities'),('w3h','buffs'),('w3q','upgrades'),('w3b','destructibles'),('w3d','doodads')]:
 n='war3map.'+ext
 if n not in blobs:continue
 f=O/n;f.write_bytes(blobs[n]);ob=objdata.load(str(f));assert objdata.dump(ob)==blobs[n]
 counts[kind]={'modified_standard':len(ob['tables'][0]),'custom':len(ob['tables'][1]),'bytes':len(blobs[n])}
 for ti,table in enumerate(ob['tables']):
  for e in table:
   ident=e['newId'] if ti else e['oldId'];mods=e['mods'];name=next((m['value'] for m in mods if m['id'] in ('unam','anam','fnam','gnam','bnam','dnam')),'')
   if str(name).startswith('TRIGSTR_'):name=strings.get(str(int(name[8:])),name)
   objs[ident]={'id':ident,'kind':kind,'custom':bool(ti),'name':name,'parent':e['oldId'],'values':[m['value'] for m in mods]}
for ident,o in objs.items():
 raw=ident.encode('latin1'); refs=[]
 for other,v in objs.items():
  if other!=ident and (v['parent']==ident or any(raw in str(x).encode('latin1',errors='replace') for x in v['values'])):refs.append(other)
 runtime=[n for n,b in fs.items() if "'"+ident+"'" in b]
 placed=[n for n in ['war3mapUnits.doo','war3map.doo'] if raw in blobs.get(n,b'')]
 editor=[n for n in ['war3map.wct','war3map.wtg'] if raw in blobs.get(n,b'')]
 rows.append({k:o[k] for k in ['id','kind','custom','name']}|{'object_refs':','.join(refs),'runtime_functions':','.join(runtime),'reachable_runtime':','.join(n for n in runtime if n in reach),'placements':','.join(placed),'editor_refs':','.join(editor),'candidate_no_direct_refs':bool(o['custom'] and not refs and not runtime and not placed and not editor)})
with (O/'objects.csv').open('w',newline='',encoding='utf-8-sig') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
fr=[{'name':n,'line':s[:s.find(fs[n])].count('\n')+1,'bytes':len(fs[n]),'reachable':n in reach,'callers':','.join(k for k,v in edges.items() if n in v)} for n in fs]
with (O/'functions.csv').open('w',newline='',encoding='utf-8-sig') as f:
 wr=csv.DictWriter(f,fieldnames=list(fr[0]));wr.writeheader();wr.writerows(fr)
summary={'map':str(p),'counts':counts,'functions':len(fs),'reachable_functions':len(reach),'unreachable_functions':unreach,'dynamic_calls':dynamic,'object_candidates':[r for r in rows if r['candidate_no_direct_refs']],'unreachable_bytes':sum(len(fs[n]) for n in unreach),'editor_files':{n:len(blobs[n]) for n in ['war3map.wtg','war3map.wct'] if n in blobs}}
(O/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))
