from pathlib import Path
import sys,ast,json,re
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'mini-foots/tools'))
import objdata
from validate_objdata import validate
source=(W/'mini-foots/tools/game_data.py').read_text()
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='slk'],type_ignores=[]),'slk','exec'))
cache=W/'799x-backport/item-audit/game-data'
report={}
for suffix,kind in [('w3u','unit'),('w3a','ability')]:
    meta=slk((cache/f'base-{kind}metadata.slk').read_bytes())
    doc=objdata.load(str(R/'src'/('war3map.'+suffix)))
    count=validate((R/'src'/('war3map.'+suffix)).read_bytes(),suffix=='w3a')
    new=[e for table in doc['tables'] for e in table if e['newId'] in ['nStk','AStB','AStS']]
    for e in new:
        for mod in e['mods']:
            assert mod['id'] in meta,('Unknown field',e['newId'],mod)
            md=meta[mod['id']];typ=md['type']
            expected=0 if typ in ['int','bool','attackBits','deathType','teamColor','spellDetail','channelType','channelFlags','fullFlags','silenceFlags','pickFlags','stackFlags','morphFlags','versionFlags','interactionFlags','pathingListPrevent','pathingListRequire'] else 1 if typ in ['real','unreal'] else 3
            assert mod['type']==expected or {mod['type'],expected}<={1,2},('Type mismatch',e['newId'],mod['id'],typ,mod['type'],expected)
    report[kind]=dict(objects=count,added=[e['newId'] for e in new])
    if suffix=='w3u':
        report['launch_metadata']={k:meta[k]['field'] for k in ['ulpx','ulpy','ulpz']}
(R/'object-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
