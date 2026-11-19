"""Prepare an isolated current-map build restoring rc6 item display text only."""
import argparse
import copy
import hashlib
import json
import re
import shutil
import struct
from pathlib import Path
from map_archive import Archive

TEXT_FIELDS = {b'inam', b'ides', b'utip', b'utub'}


def parse(data, extended=False):
    pos = 4
    tables = []
    def integer():
        nonlocal pos
        value = struct.unpack_from('<i', data, pos)[0]
        pos += 4
        return value
    for _ in range(2):
        entries = []
        for _ in range(integer()):
            ids = data[pos:pos + 8]
            pos += 8
            if struct.unpack('<i', data[:4])[0] >= 3:
                start = pos
                count = integer()
                pos += count * 4
                ids += data[start:pos]
            mods = []
            for _ in range(integer()):
                field = data[pos:pos + 4]
                pos += 4
                kind = integer()
                start = pos
                if extended:
                    pos += 8  # Level and data pointer in an ability or upgrade modification.
                end = data.index(b'\0', pos) + 1 if kind == 3 else pos + 4
                value = data[start:end]
                pos = end
                suffix = data[pos:pos + 4]
                pos += 4
                mods.append([field, kind, value, suffix])
            entries.append([ids, mods])
        tables.append(entries)
    assert pos == len(data), (pos, len(data))
    return [data[:4], tables]


def dump(obj):
    result = bytearray(obj[0])
    for table in obj[1]:
        result += struct.pack('<i', len(table))
        for ids, mods in table:
            result += ids + struct.pack('<i', len(mods))
            for field, kind, value, suffix in mods:
                result += field + struct.pack('<i', kind) + value + suffix
    return bytes(result)


def strings(data):
    return {int(k): v.encode('utf-8') for k, v in re.findall(
        r'STRING\s+(\d+)[^\{]*\{\r?\n(.*?)\r?\n\}', data.decode('utf-8-sig'), re.S)}


def resolved(value, wts):
    raw = value.rstrip(b'\0')
    return wts[int(raw[8:])] + b'\0' if raw.startswith(b'TRIGSTR_') else value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('current', type=Path)
    parser.add_argument('reference', type=Path)
    parser.add_argument('workspace', type=Path)
    parser.add_argument('--project', choices=['799x', 'solo', 'mini', 'ffa', 'casino'], default='799x')
    parser.add_argument('--title', default='|cffffcc00Reforged|r Footmen 7.9.9X-T39 - RJE')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / 'tools.local.json').read_text())
    work = args.workspace
    work.mkdir(parents=True, exist_ok=False)
    families = {'799x': '799X', 'solo': 'Solo Foots', 'mini': 'Mini Foots', 'ffa': 'FFA Foots', 'casino': '799-CASINO'}
    project = work / 'projects' / args.project
    src = project / 'src'
    release = project / 'release'
    release.mkdir(parents=True)
    shutil.copy2(args.current, release / args.current.name)
    (project / 'project.json').write_text(json.dumps(dict(map_type=families[args.project], release=args.current.name,
        sha256=hashlib.sha256(args.current.read_bytes()).hexdigest())))
    shutil.copy2(root / 'Build-Map.ps1', work)
    shutil.copy2(root / 'tools.local.json', work)
    shutil.copytree(root / 'tools', work / 'tools', ignore=shutil.ignore_patterns('__pycache__'))
    # Keep the optional pre-MPQ map-list title consistent with the internal title.
    builder = work / 'tools/build_map.py'
    hook = '''    with destination.open('r+b') as stream:
        header = stream.read(512)
        if header.startswith(b'HM3W'):
            end = header.index(b'\\0', 8)
            assert not any(header[end + 9:])
            updated = header[:8] + TITLE_BYTES + b'\\0' + header[end + 1:end + 9]
            assert len(updated) <= 512
            stream.seek(0)
            stream.write(updated.ljust(512, b'\\0'))
'''.replace('TITLE_BYTES', repr(args.title.encode('utf-8')))
    builder.write_text(builder.read_text().replace('    with Archive(dll, baseline) as before,', hook + '    with Archive(dll, baseline) as before,'))
    if args.project == 'casino':
        for path in [work / 'Build-Map.ps1', work / 'tools/build_map.py']:
            path.write_text(path.read_text().replace("'mini','ffa'", "'mini','ffa','casino'").replace("'mini', 'ffa'", "'mini', 'ffa', 'casino'"))
    changes = []
    with Archive(config['stormlib'], args.current) as current, Archive(config['stormlib'], args.reference) as reference:
        known_src = root / 'projects' / ('799x' if args.project == 'casino' else args.project) / 'src'
        candidates = [str(p.relative_to(known_src)).replace('/', '\\')
                      for p in known_src.rglob('*') if p.is_file()]
        current.extract(src, candidates)
        old_wts = strings(reference.read('war3map.wts'))
        new_wts = strings(current.read('war3map.wts'))
        for name in ['war3map.w3t', 'war3mapSkin.w3t']:
            try:
                raw = current.read(name)
            except KeyError:
                continue
            old = parse(reference.read(name))
            old_entries = {ids: mods for table in old[1] for ids, mods in table}
            obj = parse(raw)
            assert dump(obj) == raw
            original = copy.deepcopy(obj)
            for table in obj[1]:
                for ids, mods in table:
                    if ids not in old_entries:
                        continue
                    prior = {m[0]: m for m in old_entries[ids] if m[0] in TEXT_FIELDS}
                    for field in TEXT_FIELDS:
                        existing = next((m for m in mods if m[0] == field), None)
                        target = prior.get(field)
                        if target:
                            target = copy.deepcopy(target)
                            target[2] = resolved(target[2], old_wts)
                            if existing and resolved(existing[2], new_wts) == target[2]:
                                continue
                        elif existing is None:
                            continue
                        if existing:
                            mods.remove(existing)
                        if target:
                            mods.append(target)
                        changes.append(dict(file=name, item=ids[:8].decode('latin1'), field=field.decode(),
                            before=resolved(existing[2], new_wts).decode('utf-8').rstrip('\0') if existing else None,
                            after=target[2].decode('utf-8').rstrip('\0') if target else None))
            # Every non-text modifier and object identity must remain identical.
            def mechanics(value):
                return [[(ids, [m for m in mods if m[0] not in TEXT_FIELDS]) for ids, mods in t] for t in value[1]]
            assert mechanics(obj) == mechanics(original)
            for table in obj[1]:
                for ids, mods in table:
                    if ids in old_entries:
                        actual = {m[0]: resolved(m[2], new_wts) for m in mods if m[0] in TEXT_FIELDS}
                        expected = {m[0]: resolved(m[2], old_wts) for m in old_entries[ids] if m[0] in TEXT_FIELDS}
                        assert actual == expected
            (src / name).write_bytes(dump(obj))
        assert (src / 'war3map.j').read_bytes() == current.read('war3map.j')
        assert (src / 'war3map.w3i').read_bytes() == current.read('war3map.w3i')
        # Restore original miRaculix references in shared strings, including item abilities.
        wts_text = current.read('war3map.wts').decode('utf-8-sig')
        def restore_string(match):
            key = int(match[2])
            body = match[3]
            if key == 1:
                body = args.title
            elif key in old_wts and b'miraculix' in old_wts[key].lower() and 'RJE' in body:
                body = old_wts[key].decode('utf-8')
            return match[1] + body + match[4]
        wts_text = re.sub(r'(STRING\s+(\d+)[^\{]*\{\r?\n)(.*?)(\r?\n\})', restore_string, wts_text, flags=re.S)
        (src / 'war3map.wts').write_bytes(wts_text.encode('utf-8'))
        info = current.read('war3map.w3i')
        assert int.from_bytes(info[:4], 'little') in (33, 39)
        end = info.index(b'\0', 28)
        if not info[28:end].startswith(b'TRIGSTR_'):
            (src / 'war3map.w3i').write_bytes(info[:28] + args.title.encode('utf-8') + info[end:])
        jass = current.read('war3map.j')
        jass = re.sub(rb'call SetMapName\("(?!TRIGSTR_)[^"\r\n]*"\)',
                      lambda m: b'call SetMapName("' + args.title.encode('utf-8') + b'")', jass)
        (src / 'war3map.j').write_bytes(jass)
    (work / 'item-text-changes.json').write_text(json.dumps(changes, indent=2))
    print(json.dumps(dict(workspace=str(work), changed_fields=len(changes), changed_items=len({c['item'] for c in changes}))))


if __name__ == '__main__':
    main()
