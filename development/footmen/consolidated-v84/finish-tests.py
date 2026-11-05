from pathlib import Path
import sys,shutil,json,subprocess
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c
h=c.c_void_p();assert storm.SFileOpenArchive(str(R/'release/FF799X_Rx_Consolidated_v84_TEST.w3x'),0,256,c.byref(h))
(R/'src/war3map.w3h').write_bytes(read_storm(h,'war3map.w3h'))
# Verify that the exact previously parsed cloud models are preserved in the final archive.
models=list((W/'mundo-ui-merge/src').rglob('*.mdx'))
assert len(models)==21,len(models)
for p in models:
 n=str(p.relative_to(W/'mundo-ui-merge/src')).replace('/','\\');assert read_storm(h,n)==p.read_bytes(),n
assert storm.SFileCloseArchive(h)
shutil.copy2(W/'mundo-ui-merge/asset-checks.json',R/'asset-checks.json')
results=json.loads((R/'test-results.json').read_text())
for label in ['mundo-cloud','mundo-cleaver']:
 p=subprocess.run([sys.executable,str(R/(label+'-check.py'))],capture_output=True,text=True,errors='replace',cwd=W)
 (R/(label+'-check.log')).write_text(p.stdout+p.stderr)
 next(r for r in results if r['suite']==label).update(exit_code=p.returncode,output=(p.stdout+p.stderr)[-1200:])
 print(label,p.returncode,p.stdout+p.stderr)
(R/'test-results.json').write_text(json.dumps(results,indent=2));assert all(r['exit_code']==0 for r in results)
