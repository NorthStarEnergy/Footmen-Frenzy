from pathlib import Path
import sys,json
r=Path(__file__).parent
sys.path.insert(0,str(r.parent/'799x-backport/tools'))
import mpyq
name=json.loads((r/'changes.json').read_text())['name']
archive=mpyq.MPQArchive(str(r/'release'/(name+'.w3x')),listfile=False)
dest=Path(sys.argv[1])/'files'
for f in (r/'src').rglob('*'):
    if f.is_file():
        rel=f.relative_to(r/'src')
        data=archive.read_file(str(rel).replace('/','\\'))
        assert data==f.read_bytes(),str(rel)
        out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
print('All named payloads extracted directly from archive and verified')
