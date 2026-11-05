"""Repack a current map from editable payloads, retaining every untouched entry."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from map_archive import Archive

ROOT = Path(__file__).resolve().parents[1]


def build(project, name, verify_only=False):
    folder = ROOT / 'projects' / project
    meta = json.loads((folder / 'project.json').read_text())
    config_path = ROOT / 'tools.local.json'
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    dll = os.environ.get('STORMLIB_DLL') or config.get('stormlib')
    if not dll or not Path(dll).is_file():
        raise RuntimeError('Set STORMLIB_DLL or tools.local.json stormlib to a 64-bit StormLib.dll')
    baseline = folder / 'release' / meta['release']
    if hashlib.sha256(baseline.read_bytes()).hexdigest() != meta['sha256']:
        raise RuntimeError('Baseline checksum mismatch; run git lfs pull or restore the verified release')
    files = {str(p.relative_to(folder / 'src')).replace('/', '\\'): p
             for p in (folder / 'src').rglob('*') if p.is_file()}
    if 'war3map.j' not in files:
        raise RuntimeError('Missing authoritative JASS source')
    changed = []
    with Archive(dll, baseline) as archive:
        original_names = archive.names()
        for entry, path in files.items():
            try:
                same = archive.read(entry) == path.read_bytes()
            except KeyError:
                same = False
            if not same:
                changed.append(entry)
    if verify_only:
        if changed:
            raise RuntimeError(f'Snapshot differs from release: {changed}')
        print(f'{project}: {len(files)} source payloads match the verified release')
        return
    if not name or Path(name).name != name or not name.lower().endswith('.w3x'):
        raise ValueError('Provide a versioned .w3x filename without directories')
    if 'war3map.j' in changed:
        required = ['pjass', 'common_j', 'blizzard_j']
        if not all(config.get(k) and Path(config[k]).is_file() for k in required):
            raise RuntimeError('Changed JASS requires pjass, common_j, and blizzard_j in tools.local.json')
        subprocess.run([config['pjass'], config['common_j'], config['blizzard_j'], str(files['war3map.j'])], check=True)
    destination = ROOT / 'build' / project / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f'Build already exists; choose a new version: {destination}')
    shutil.copy2(baseline, destination)
    if changed:
        with Archive(dll, destination, writable=True) as archive:
            for entry in changed:
                archive.add(entry, files[entry])
    with Archive(dll, baseline) as before, Archive(dll, destination) as after:
        for entry, path in files.items():
            if after.read(entry) != path.read_bytes():
                raise RuntimeError(f'Roundtrip mismatch: {entry}')
        for entry in original_names:
            if entry.startswith('(') or entry in files:
                continue
            if before.read(entry) != after.read(entry):
                raise RuntimeError(f'Untouched entry changed: {entry}')
    report = dict(project=project, output=str(destination), sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                  checked_payloads=len(files), changed_entries=changed, verified=True)
    destination.with_suffix('.verification.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('project', choices=['799x', 'solo', 'mini', 'ffa'])
    parser.add_argument('--name')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    build(args.project, args.name, args.verify_only)
