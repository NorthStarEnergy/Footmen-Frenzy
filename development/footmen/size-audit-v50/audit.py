from pathlib import Path
import sys,struct,collections,json,csv,re,hashlib
R=Path(__file__).resolve().parent;W=R.parent;sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive
import objdata
p=W/'tf-wc3-icons-v50/release/FF799X_Rx_TF_Guardian_WC3Icons_v50.w3x';a=archive(p);h=c.c_void_p();assert storm.SFileOpenArchive(str(p),0,0x100,c.byref(h))
imp=read_storm(h,'war3map.imp');count=struct.unpack_from('<I',imp,4)[0];pos=8;names=set();imports=[]
for _ in range(count):
 flag=imp[pos];pos+=1;end=imp.index(0,pos);name=imp[pos:end].decode('latin1');pos=end+1;name=name if flag in (10,13) else 'war3mapImported\\'+name;names.add(name);imports.append(name)
try:names.update(read_storm(h,'(listfile)').decode('latin1').splitlines())
except:pass
for directory in [W/'mini-foots/base/files',W/'799x-backport/src',W/'tf-destiny-v46/src',W/'tf-orb-icons-v49/src']:
 if directory.exists():names.update(str(f.relative_to(directory)).replace('/','\\') for f in directory.rglob('*') if f.is_file())
names.update(['war3map.j','war3map.w3u','war3map.w3a','war3map.w3t','war3map.w3b','war3map.w3d','war3map.w3q','war3map.w3h','war3map.w3w','war3map.wts','war3map.imp','war3map.w3i','war3map.doo','war3mapUnits.doo','war3map.wtg','war3map.wct','war3map.wpm','war3map.w3e','war3mapMisc.txt','(listfile)','(attributes)'])
data={};meta={};namedkeys=set()
for n in sorted(names,key=str.lower):
 e=a.get_hash_table_entry(n)
 if not e or e.block_table_index>=len(a.block_table):continue
 key=(e.hash_a,e.hash_b,e.locale,e.platform)
 if key in namedkeys:continue
 try:raw=read_storm(h,n)
 except:continue
 namedkeys.add(key);data[n]=raw;b=a.block_table[e.block_table_index];meta[n]={'bytes':len(raw),'stored':b.archived_size}
assert storm.SFileCloseArchive(h)
allkeys={(e.hash_a,e.hash_b,e.locale,e.platform) for e in a.hash_table if e.block_table_index<len(a.block_table)};unknown=len(allkeys-namedkeys)
def norm(v):return v.lower().replace(b'/',b'\\').replace(b'\\\\',b'\\')
# Names, import table and credits are metadata, not live uses.
excluded=lambda n:n.lower() in ('(listfile)','(attributes)','war3map.imp') or 'credits' in n.lower()
search={n:norm(raw) for n,raw in data.items() if not excluded(n)}
models={n for n in data if n.lower().endswith(('.mdx','.mdl'))};rows=[]
for n in imports:
 found=next((k for k in data if k.lower()==n.lower()),None)
 if not found:rows.append({'path':n,'status':'MISSING','stored':0,'raw':0,'refs':[]});continue
 key=norm(n.encode('latin1'));alt=key[:-4]+(b'.mdl' if key.endswith(b'.mdx') else b'.mdx') if key.endswith((b'.mdx',b'.mdl')) else key
 refs=[k for k,v in search.items() if k!=found and (key in v or alt in v)]
 status='referenced' if refs else 'no direct reference found'
 if n.lower().endswith('_portrait.mdx'):
  primary=n[:-13]+'.mdx'; m=next((k for k in data if k.lower()==primary.lower()),None)
  if m and any(norm(m.encode('latin1')) in raw for k,raw in search.items() if k!=m):status='implicit portrait of referenced model'
 rows.append({'path':n,'status':status,'stored':meta[found]['stored'],'raw':meta[found]['bytes'],'refs':refs})
(R/'imports.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
with (R/'imports.csv').open('w',newline='',encoding='utf8') as f:
 wr=csv.DictWriter(f,fieldnames=['path','status','stored','raw','refs']);wr.writeheader();wr.writerows({**r,'refs':'; '.join(r['refs'])} for r in rows)
files=[{'path':n,**v} for n,v in meta.items()];files.sort(key=lambda x:-x['stored']);(R/'archive-files.json').write_text(json.dumps(files,indent=2),encoding='utf8')
by=collections.defaultdict(lambda:[0,0,0]);
for f in files:
 ext=Path(f['path'].replace('\\','/')).suffix.lower() or '(no extension)';by[ext][0]+=1;by[ext][1]+=f['stored'];by[ext][2]+=f['bytes']
missing=[r for r in rows if r['status']=='MISSING'];candidates=[r for r in rows if r['status']=='no direct reference found'];candidates.sort(key=lambda x:-x['stored']);
print(json.dumps({'map_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'archive_count':len(allkeys),'known':len(namedkeys),'unknown':unknown,'imports':count,'missing':len(missing),'candidate_count':len(candidates),'candidate_stored_sum':sum(x['stored'] for x in candidates),'by_type':dict(sorted(by.items(),key=lambda x:-x[1][1])[:12]),'largest_files':files[:20],'candidates':candidates[:45]},indent=2))
