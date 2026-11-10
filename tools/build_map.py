"""Repack a current map from editable payloads, retaining every untouched entry."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory
from map_archive import Archive

ROOT = Path(__file__).resolve().parents[1]


def title_field(info, strings):
    # W3I formats 33 and 39 both have seven 32-bit fields before the map name.
    if int.from_bytes(info[:4], 'little') not in (33, 39):
        raise ValueError('Unsupported map information format')
    end = info.index(b'\0', 28)
    reference = re.fullmatch(rb'TRIGSTR_(\d+)', info[28:end])
    if not reference:
        return 'war3map.w3i', info, 28, end
    number = str(int(reference[1])).encode()
    pattern = (rb'(?m)^(?:\xef\xbb\xbf)?STRING[ \t]+0*' + number +
               rb'[ \t]*\r?\n(?:[ \t]*//[^\n]*\n)*[ \t]*\{[ \t]*\r?\n'
               rb'([\s\S]*?)\r?\n[ \t]*\}[ \t]*\r?$')
    matches = list(re.finditer(pattern, strings))
    if len(matches) != 1:
        raise ValueError(f'Missing or ambiguous map title string {number!r}')
    start, end = matches[0].span(1)
    return 'war3map.wts', strings, start, end


def map_header_with_title(path, title):
    # Some maps also advertise their name in a 512-byte header before the MPQ.
    with path.open('rb') as stream:
        header = stream.read(512)
    if not header.startswith(b'HM3W'):
        return None
    end = header.index(b'\0', 8)
    tail = header[end + 1:end + 9]  # map flags and player count
    if len(tail) != 8 or any(header[end + 9:]):
        raise ValueError('Unexpected data in map header')
    result = header[:8] + title + b'\0' + tail
    if len(result) > 512:
        raise ValueError('Map title exceeds the header capacity')
    return result.ljust(512, b'\0')


def build(project, name, verify_only=False):
    output_root = ROOT / 'build'
    output_root.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=output_root) as staging:
        _build(project, name, verify_only, Path(staging))


def _build(project, name, verify_only, staging):
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
    if not verify_only:
        if not name or Path(name).name != name or not name.lower().endswith('.w3x'):
            raise ValueError('Provide a versioned .w3x filename without directories')
        client_title = Path(name).stem
        title = client_title.encode('utf-8')
        entry, data, start, end = title_field(files['war3map.w3i'].read_bytes(),
                                              files['war3map.wts'].read_bytes())
        files[entry] = staging / entry
        files[entry].write_bytes(data[:start] + title + data[end:])
        header = map_header_with_title(baseline, title)
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
    if header is not None:
        with destination.open('r+b') as stream:
            stream.write(header)
    if changed:
        with Archive(dll, destination, writable=True) as archive:
            for entry in changed:
                archive.add(entry, files[entry])
    with Archive(dll, baseline) as before, Archive(dll, destination) as after:
        _, packed, start, end = title_field(after.read('war3map.w3i'), after.read('war3map.wts'))
        if packed[start:end] != title:
            raise RuntimeError('Packed client title differs from output filename')
        if header is not None:
            with destination.open('rb') as stream:
                if stream.read(512) != header:
                    raise RuntimeError('Packed map header differs from expected header')
        for entry, path in files.items():
            if after.read(entry) != path.read_bytes():
                raise RuntimeError(f'Roundtrip mismatch: {entry}')
        for entry in original_names:
            if entry.startswith('(') or entry in files:
                continue
            if before.read(entry) != after.read(entry):
                raise RuntimeError(f'Untouched entry changed: {entry}')
    report = dict(project=project, output=str(destination), sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                  client_title=client_title, checked_payloads=len(files), changed_entries=changed, verified=True)
    destination.with_suffix('.verification.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('project', choices=['799x', 'solo', 'mini', 'ffa'])
    parser.add_argument('--name')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    build(args.project, args.name, args.verify_only)
