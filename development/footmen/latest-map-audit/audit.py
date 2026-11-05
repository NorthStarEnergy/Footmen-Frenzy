from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c,functions,archive
import objdata
maps=Path('C:/Users/User/Documents/Warcraft III/Maps')
paths={'installed_v69':maps/'Test/FF799X_Rx_Ghoul_Grunt_Buff_v69.w3x','installed_v68':maps/'Test/FF799X_Rx_Spawn_Rates_v68.w3x','v67':W/'pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x','v83':W/'veigar-ultimate-v83/release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x','solo':maps/'Solo Foots/Solo Tests/Solo_Foots_v1.8_4P_799X_UPDATE08.w3x'}
allf={};objects={};report={}
for label,p in paths.items():
 h=c.c_void_p();assert storm.SFileOpenArchive(str(p),0,256,c.byref(h))
 a=archive(p);d=R/label;d.mkdir(exist_ok=True)
 data={}
 for name in ['war3map.j','war3map.w3u','FF_MAINTENANCE.md','FF_SOURCE_MANIFEST.json']:
  if a.get_hash_table_entry(name):
   b=read_storm(h,name);(d/name).write_bytes(b);data[name]=b
 assert storm.SFileCloseArchive(h)
 f=functions(data['war3map.j'].decode('utf-8-sig',errors='replace').replace('\r',''));allf[label]=f
 o=objdata.load(str(d/'war3map.w3u'));objects[label]={(e['oldId'],e['newId'],m['id'],m.get('level',0)):m['value'] for tab in o['tables'] for e in tab for m in e['mods']}
 report[label]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'functions':len(f),'manifest':json.loads(data['FF_SOURCE_MANIFEST.json'].decode('utf-8-sig')) if 'FF_SOURCE_MANIFEST.json' in data else None}
for label in ['installed_v69','solo']:
 f=allf[label];v=allf['v83'];report[label]['missing_v83_functions']=[n for n in v if n not in f]
report['installed_branch_changes']={'functions_vs_v67':[n for n,f in allf['installed_v69'].items() if allf['v67'].get(n)!=f],'unit_fields_vs_v67':[{'key':k,'old':objects['v67'].get(k),'installed':v,'v83':objects['v83'].get(k)} for k,v in objects['installed_v69'].items() if objects['v67'].get(k)!=v]}
report['solo_changes_vs_installed']={'added_functions':[n for n in allf['solo'] if n not in allf['installed_v69']],'changed_functions':[n for n,f in allf['solo'].items() if n in allf['installed_v69'] and allf['installed_v69'][n]!=f]}
(R/'report.json').write_text(json.dumps(report,indent=2))
for label in paths:
 r=report[label];print(label,r['sha256'],r['functions']);print('revision:',(r['manifest'] or {}).get('revision'))
print('Installed branch changes',json.dumps(report['installed_branch_changes'],indent=2))
print('Solo differences',json.dumps(report['solo_changes_vs_installed'],indent=2))
print('Missing newer functions in installed:',report['installed_v69']['missing_v83_functions'])
