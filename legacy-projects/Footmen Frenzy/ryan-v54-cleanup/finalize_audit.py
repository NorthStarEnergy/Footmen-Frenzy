import sys,json,csv,collections,re
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'audit';sys.path.insert(0,str(R.parent/'hero-polish'))
from archive_helpers import storm,read_storm,c,archive
p=R/'release/FF799X_Rx_UI_Startup_Clean_v55.w3x';a=archive(p);h=c.c_void_p();assert storm.SFileOpenArchive(str(p),0,0x100,c.byref(h))
names=[x['path'] for x in json.loads((R.parent/'size-audit-v50/archive-files.json').read_text())];data={}
for n in names:
 if n.lower().endswith(('.slk','.txt','.lua','.j','.fdf','.toc')) and a.get_hash_table_entry(n):
  try:data[n]=read_storm(h,n)
  except:pass
storm.SFileCloseArchive(h)
rows=list(csv.DictReader((O/'objects.csv').open(encoding='utf-8-sig')))
for r in rows:
 r['additional_data_mentions']=','.join(n for n,b in data.items() if n!='war3map.j' and r['id'].encode() in b)
 # SLK rows can define an object rather than use it: keep all such hits for manual review.
 r['candidate_no_direct_refs']=r['candidate_no_direct_refs']=='True' and not r['additional_data_mentions']
with (O/'objects.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=json.loads((O/'summary.json').read_text());s['object_candidates']=[r for r in rows if r['candidate_no_direct_refs']];s['additional_text_data_scanned']=list(data);(O/'summary.json').write_text(json.dumps(s,indent=2))
cnt=collections.Counter(r['kind'] for r in s['object_candidates']);print('Final candidates',dict(cnt));print('Additional data files',len(data))
lines=['# Ryan v54 / cleaned v55 object and code audit','', 'Read-only audit; map unchanged. All seven object tables parsed and byte-exact round-trip checked.','', '| Category | Custom | Modified standard | No-direct-reference candidates |','|---|---:|---:|---:|']
for k,v in s['counts'].items():lines.append(f"| {k} | {v['custom']} | {v['modified_standard']} | {cnt[k]} |")
lines+=['',f"Script: {s['functions']} functions; {len(s['unreachable_functions'])} have no discovered path from main/config ({s['unreachable_bytes']:,} bytes of uncompressed function bodies). Direct callbacks and literal ExecuteFunc targets are included conservatively by identifier matching. This is a static candidate list, not proof every candidate can be deleted.",'','Examples of leftover code include the disconnected Guardian Force Field Detonate trigger, old Twisted Fate pickACard/destiny helper functions, old MODE_1v1/Overdrive/camera initializer functions, and unused generated GUI condition helpers. Do not remove whole libraries merely because some public helpers are unused.','', 'The script also retains GST Example expiry triggers: their initializer calls remain present, so these are not classified as disconnected merely because they start disabled. Disabled triggers may be executed or enabled elsewhere.','',f"Editor data: war3map.wct {s['editor_files'].get('war3map.wct',0):,} bytes; war3map.wtg {s['editor_files'].get('war3map.wtg',0):,} bytes. Runtime and editor custom source must be changed together to prevent old code returning on editor save.",'','Review objects.csv for every object and its references; functions.csv for every function, callers and static reachability. Additional SLK/TXT data mentions are retained conservatively; a mention may be a definition rather than a use. Blank object names mean no name override exists in the binary object record, not an unnamed in-game object.','', 'Limits: static scan does not resolve computed rawcodes, numeric encodings, all engine-inherited dependencies, arbitrary dynamic calls or unnamed archive files. Modified standard objects are not deletion candidates; reverting them requires comparing gameplay fields with Warcraft defaults. No live match or editor save test was performed.','', 'Recommended next cleanup: remove individually proven disconnected code from both runtime and editor source, then resolve object candidates against inherited/default and SLK data before deleting them. Keep active hero scripts, shops, tech trees, summoned/dummy units, buff chains and core systems. Compressed map savings will be smaller than uncompressed code sizes.']
(O/'REPORT.md').write_text('\n'.join(lines),encoding='utf8')
