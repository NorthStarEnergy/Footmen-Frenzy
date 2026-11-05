from pathlib import Path
import hashlib
import json
import shutil
import struct
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parent / 'hero-polish'))
from archive_helpers import archive, entries, storm, read_storm, c

manifest = json.loads((R / 'changes.json').read_text())
assert json.loads((R / 'checks.json').read_text())['passed']
for name in ['compiler.log', 'editor-compiler.log']:
    log = (R / name).read_text()
    assert 'Parse successful:' in log and 'Parse failed' not in log
assert (R / 'editor-compiled.j').is_file()
base = Path(manifest['base'])
stage = R / 'stage.w3x'
shutil.copy2(base, stage)
h = c.c_void_p()
assert storm.SFileOpenArchive(str(stage), 0, 0, c.byref(h))
changed = []
for f in sorted((R / 'src').iterdir()):
    assert f.name in ['war3map.j', 'war3map.wct', 'war3map.wts', 'FF_MAINTENANCE.md']
    assert storm.SFileAddFileEx(h, str(f), f.name.encode(), 0x80000200, 2, 2)
    changed.append(f.name)
assert storm.SFileCloseArchive(h)

# Compact using the established v66 archive writer; never modify the base map.
a = archive(stage)
hashes, blocks = list(a.hash_table), list(a.block_table)
attrs = a.get_hash_table_entry('(attributes)')
if attrs:
    idx = next(i for i, e in enumerate(hashes) if e == attrs)
    hashes[idx] = hashes[idx]._replace(block_table_index=0xfffffffe)
live = {e.block_table_index for e in hashes if e.block_table_index < len(blocks)}
assert not any(blocks[i].flags & 0x10000 for i in live)
out = R / 'release/FF799X_Rx_Pub_XP_v67.w3x'
out.parent.mkdir(exist_ok=True)
data = stage.read_bytes()
assert data[:4] == b'MPQ\x1a'

def encrypt(raw, key):
    seed1, seed2 = key, 0xEEEEEEEE
    result = bytearray()
    for (v,) in struct.iter_unpack('<I', raw):
        seed2 = (seed2 + a.encryption_table[0x400 + (seed1 & 255)]) & 0xffffffff
        result += struct.pack('<I', (v ^ (seed1 + seed2)) & 0xffffffff)
        seed1 = (((~seed1 << 21) + 0x11111111) | (seed1 >> 11)) & 0xffffffff
        seed2 = (v + seed2 + (seed2 << 5) + 3) & 0xffffffff
    return result

with out.open('wb') as f:
    f.write(b'\0' * 32)
    for i in sorted(live, key=lambda i: blocks[i].offset):
        b = blocks[i]
        off = f.tell()
        f.write(data[b.offset:b.offset + b.archived_size])
        blocks[i] = b._replace(offset=off)
    hp = f.tell()
    f.write(encrypt(b''.join(struct.pack('<2I2HI', *e) for e in hashes), a._hash('(hash table)', 'TABLE')))
    bp = f.tell()
    f.write(encrypt(b''.join(struct.pack('<4I', *e) for e in blocks), a._hash('(block table)', 'TABLE')))
    total = f.tell()
    f.seek(0)
    f.write(struct.pack('<4s2I2H4I', b'MPQ\x1a', 32, total, 0, a.header['sector_size_shift'], hp, bp, len(hashes), len(blocks)))

before_archive = archive(base)
before, after = entries(before_archive), entries(archive(out))
skip = set()
for name in changed + ['(attributes)', '(listfile)', '(signature)']:
    e = before_archive.get_hash_table_entry(name)
    if e:
        skip.add((e.hash_a, e.hash_b, e.locale, e.platform))
for k, value in before.items():
    if k not in skip:
        assert after.get(k) == value, ('unexpected archive change', k)
assert storm.SFileOpenArchive(str(out), 0, 0x100, c.byref(h))
for name in changed:
    assert read_storm(h, name) == (R / 'src' / name).read_bytes()
assert storm.SFileCloseArchive(h)
digest = hashlib.sha256(out.read_bytes()).hexdigest()
out.with_suffix('.sha256').write_text(digest + '  ' + out.name + '\n')
report = {
    'output': str(out), 'sha256': digest, 'base': str(base),
    'changed_payloads': changed, 'preserved_payloads': len(before.keys() - skip),
    'runtime_pjass': 'passed', 'editor_jasshelper_and_pjass': 'passed',
    'source_behavior_checks': 'passed', 'automatic_xp_or_level_grants_added': False,
    'engine_and_balance_playtest': 'pending', 'installed_or_deployed': False,
}
(R / 'verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
