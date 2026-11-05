from pathlib import Path
import sys,json
R=Path('ryan-v54-cleanup');W=Path.cwd();sys.path.insert(0,str(W/'hero-polish'));from archive_helpers import storm,read_storm,c
base=R/'source/FF799X_Rx_UI_Startup_v54.w3x';out=R/'release/FF799X_Rx_UI_Startup_Clean_v55.w3x';names=[x['path'] for x in json.loads(Path('size-audit-v50/archive-files.json').read_text())]+['war3mapImported\\TFWildOrb.mdx','war3map.j','war3map.w3u'];removed={s.lower() for s in json.loads((R/'verification.json').read_text())['removed_imports']};a=c.c_void_p();b=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(a));assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(b));passed=0
for n in dict.fromkeys(names):
 if n.lower() in removed or n.lower() in ['(attributes)','(listfile)','(signature)','war3map.imp']:continue
 try:old=read_storm(a,n)
 except:continue
 try:new=read_storm(b,n)
 except:raise AssertionError('Unable to read '+n)
 assert new==old,n;passed+=1
assert storm.SFileCloseArchive(a) and storm.SFileCloseArchive(b);print('Named files independently opened and compared:',passed)
p=R/'verification.json';report=json.loads(p.read_text());report['stormlib_named_files_verified']=passed;p.write_text(json.dumps(report,indent=2))
