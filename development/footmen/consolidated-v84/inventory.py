from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
base=W/'veigar-ultimate-v83/release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x'
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,256,c.byref(h));final=functions(read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r',''));storm.SFileCloseArchive(h)
rows=[]
for p in sorted(W.glob('*/verification.json')):
 try:j=json.loads(p.read_text(encoding='utf-8-sig'))
 except Exception:continue
 out=j.get('output')
 if not isinstance(out,str) or not Path(out).exists():continue
 if not storm.SFileOpenArchive(out,0,256,c.byref(h)):continue
 try:
  f=functions(read_storm(h,'war3map.j').decode('utf-8-sig',errors='replace').replace('\r',''))
  changed=j.get('changed_functions',[]);added=j.get('added_functions',j.get('new_functions',[]))
  if not isinstance(added,list):added=[]
  if not isinstance(changed,list):changed=[]
  names=[n for n in changed+added if isinstance(n,str) and n in f]
  row={'branch':p.parent.name,'output':out,'same':[n for n in names if f[n]==final.get(n)],'different':[n for n in names if n in final and f[n]!=final[n]],'missing':[n for n in names if n not in final]}
  rows.append(row)
 finally:storm.SFileCloseArchive(h)
(R/'branch-inventory.json').write_text(json.dumps(rows,indent=2))
for r in rows:print(r['branch'],'same',len(r['same']),'different',r['different'],'MISSING',r['missing'])
# Complete installed side branch member delta relative to its common v67 ancestor.
a=archive(W/'pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x');b=archive(Path('C:/Users/User/Documents/Warcraft III/Maps/Test/FF799X_Rx_Ghoul_Grunt_Buff_v69.w3x'))
ae,be=entries(a),entries(b)
names=b.read_file('(listfile)').decode(errors='replace').splitlines();lookup={}
for n in names:
 e=b.get_hash_table_entry(n)
 if e:lookup[(e.hash_a,e.hash_b,e.locale,e.platform)]=n
print('INSTALLED CHANGED MEMBERS:',[lookup.get(k,str(k)) for k in be if be[k]!=ae.get(k)])
