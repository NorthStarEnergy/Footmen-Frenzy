from pathlib import Path
import hashlib, json, ast
root = Path(__file__).resolve().parents[1]
for slug in ['799x', 'solo', 'mini', 'ffa']:
    folder = root / 'projects' / slug
    meta = json.loads((folder / 'project.json').read_text())
    release = folder / 'release' / meta['release']
    if hashlib.sha256(release.read_bytes()).hexdigest() != meta['sha256']:
        raise RuntimeError(f'{slug}: release checksum mismatch (run git lfs pull)')
    for name in ['war3map.j', 'war3map.w3i', 'war3map.w3u']:
        if not (folder / 'src' / name).is_file():
            raise RuntimeError(f'{slug}: missing source {name}')
    print(f'{slug}: baseline checksum and required source files verified')
for script in (root / 'tools').glob('*.py'):
    ast.parse(script.read_text(), filename=str(script))
print('Shared Python tools parse successfully')
