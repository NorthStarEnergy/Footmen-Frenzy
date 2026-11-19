"""Repack a current map from editable payloads, retaining every untouched entry."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
from map_archive import Archive

ROOT = Path(__file__).resolve().parents[1]


def client_header(project, info, strings, baseline):
    """Use the same display name in the lobby header and the W3I metadata."""
    version = int.from_bytes(info[:4], 'little')
    if version not in (33, 39):
        raise ValueError(f'Unsupported W3I version {version}')
    offset = 28
    title = info[offset:info.index(0, offset)]
    reference = re.fullmatch(rb'TRIGSTR_(\d+)', title)
    if reference:
        key = str(int(reference[1])).encode()
        pattern = (rb'(?m)^(?:\xef\xbb\xbf)?STRING[ \t]+0*' + key +
                   rb'[ \t]*\r?\n(?:[ \t]*//[^\n]*\n)*[ \t]*\{[ \t]*\r?\n'
                   rb'([^\r\n]+)\r?\n[ \t]*\}[ \t]*\r?$')
        matches = re.findall(pattern, strings)
        if len(matches) != 1:
            raise ValueError('Cannot resolve unique map title')
        title = matches[0]
    if not title.strip():
        raise ValueError('Empty client title')
    for _ in range(4):
        offset = info.index(0, offset) + 1
    flags = struct.unpack_from('<I', info, offset + 56)[0]
    with baseline.open('rb') as stream:
        original = stream.read(512)
    if original.startswith(b'HM3W'):
        end = original.index(0, 8)
        if any(original[end + 9:]):
            raise ValueError('Unexpected map header extension')
        players = struct.unpack_from('<I', original, end + 5)[0]
    elif original.startswith(b'MPQ\x1a'):
        players = {'799x': 12, 'solo': 4, 'mini': 8, 'ffa': 8}[project]
    else:
        raise ValueError('Unknown map container')
    header = b'HM3W' + bytes(4) + title + b'\0' + struct.pack('<II', flags, players)
    if len(header) > 512:
        raise ValueError('Map title exceeds header capacity')
    return header.ljust(512, b'\0'), original.startswith(b'HM3W')


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
    if not verify_only:
        draft_art = ROOT / 'projects' / 'shared' / 'sd-draft-ground'
        for texture in draft_art.rglob('*.blp'):
            entry = str(texture.relative_to(draft_art)).replace('/', '\\')
            files.setdefault(entry, texture)
    if 'war3map.j' not in files:
        raise RuntimeError('Missing authoritative JASS source')
    changed = []
    with Archive(dll, baseline) as archive:
        original_names = archive.names()
        if not verify_only:
            def payload(entry):
                return files[entry].read_bytes() if entry in files else archive.read(entry)
            header, had_header = client_header(project, payload('war3map.w3i'), payload('war3map.wts'), baseline)
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
    with baseline.open('rb') as source, destination.open('xb') as output:
        output.write(header)
        if had_header:
            source.seek(512)
        shutil.copyfileobj(source, output)
    if changed:
        with Archive(dll, destination, writable=True) as archive:
            for entry in changed:
                archive.add(entry, files[entry])
    with Archive(dll, baseline) as before, Archive(dll, destination) as after:
        with destination.open('rb') as stream:
            if stream.read(512) != header:
                raise RuntimeError('Packed map header mismatch')
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
