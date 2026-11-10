from pathlib import Path
import sys,json,subprocess
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c,functions
out=R/'release/FF799X_Rx_Consolidated_v84_TEST.w3x';h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,256,c.byref(h))
for n in ['war3map.j','war3map.wct','war3map.w3u','war3map.w3a','war3map.w3h']:(R/'src'/n).write_bytes(read_storm(h,n))
models=list((W/'mundo-ui-merge/src').rglob('*.mdx'));assert len(models)==21
for p in models:
 n=str(p.relative_to(W/'mundo-ui-merge/src')).replace('/','\\');assert read_storm(h,n)==p.read_bytes(),n
(R/'asset-checks.json').write_bytes((W/'mundo-ui-merge/asset-checks.json').read_bytes())
assert storm.SFileCloseArchive(h)
script=(R/'src/war3map.j').read_text(encoding='utf8');fs=functions(script)
(R/'stalker.j').write_text('\n'.join(f for n,f in fs.items() if n.startswith('ST_')),encoding='utf8')
suites=[('veigar','veigar-ultimate-v83/check.py'),('soulhook','soulhook-mundo-v72/checks.py'),('mundo-cloud','mundo-ui-merge/checks.py'),('mundo-cleaver','mundo-ui-merge/cleaver_checks.py'),('mundo-resources','mundo-ui-merge/resource_checks.py'),('stalker','stalker-movement-merge/checks.py'),('rewards','fed-rewards-v80/verify.py')]
results=[]
for label,path in suites:
 code=(W/path).read_text(encoding='utf8')
 if label=='rewards':
  code=code.replace("(R/'changes.json')","(W/'fed-rewards-v80/changes.json')").replace("(R/'globals.j')","(W/'fed-rewards-v80/globals.j')")
 # Run against unpacked final payload, with original assertions intact.
 test=R/(label+'-check.py');test.write_text(code,encoding='utf8')
 p=subprocess.run([sys.executable,str(test)],capture_output=True,text=True,errors='replace',cwd=W)
 (R/(label+'-check.log')).write_text(p.stdout+p.stderr,encoding='utf8')
 results.append({'suite':label,'exit_code':p.returncode,'output':(p.stdout+p.stderr)[-1200:]});print(label,p.returncode,(p.stdout+p.stderr)[-700:])
(R/'test-results.json').write_text(json.dumps(results,indent=2))
assert all(r['exit_code']==0 for r in results)

