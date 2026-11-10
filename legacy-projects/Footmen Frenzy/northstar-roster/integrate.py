from pathlib import Path
import json, hashlib, shutil, datetime
work=Path(__file__).parent
runtime=Path('C:/Users/User/NorthStar/northstar-local')
coord=runtime/'outputs/change-coordinator'
lock=coord/'integration.lock'
request='20261022-worker-company-groups'
base=json.loads((work/'base-hashes.json').read_text(encoding='utf-8-sig'))
base.append(json.loads((work/'chrome-base-hash.json').read_text(encoding='utf-8-sig')))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
lock.mkdir()
try:
    (lock/'owner.json').write_text(json.dumps({'request':request,'time':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
    for entry in base:
        assert digest(Path(entry['Path']))==entry['Hash'], 'Runtime changed: '+entry['Path']
    with (coord/'inbox'/f'{request}.json').open('x') as f:
        json.dump({'request':request,'status':'VERIFIED_READY','files':[Path(e['Path']).name for e in base]},f)
    backup=work/'preimages';backup.mkdir(exist_ok=True)
    for entry in base:
        target=Path(entry['Path']);shutil.copy2(target,backup/target.name)
    for entry in base:
        target=Path(entry['Path']);shutil.copy2(work/target.name,target)
        assert digest(target)==digest(work/target.name)
    output=runtime/'outputs'/request;output.mkdir(exist_ok=True)
    for name in ['field-roster.js','field-roster.css','dashboard-chrome.js','REPORT.md','verify.cjs']:
        shutil.copy2(work/name,output/name)
    shutil.copy2(work/'REPORT.md',runtime/'outputs/HANDOFF.md')
    shutil.copy2(work/'REPORT.md',runtime/'docs/packets/2026-10-22-worker-company-groups.md')
    with (coord/'queue.md').open('a') as f:f.write('\n'+request+': APPLIED; responsive grouping and company priority checks pass.\n')
    with (runtime/'docs/PACKET-LOG.md').open('a') as f:f.write('\n2026-10-22: Worker company groups applied; see packets/2026-10-22-worker-company-groups.md. Runtime has no Git metadata.\n')
    (coord/'inbox'/f'{request}.json').write_text(json.dumps({'request':request,'status':'APPLIED','hashes':{Path(e['Path']).name:digest(Path(e['Path'])) for e in base}}))
    print('Applied three verified assets; baseline checks and installed hash checks passed.')
finally:
    (lock/'owner.json').unlink(missing_ok=True)
    lock.rmdir()
