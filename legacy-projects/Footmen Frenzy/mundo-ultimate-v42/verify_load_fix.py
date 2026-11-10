"""Prove v42a retains the successfully tested diagnostic's game payloads."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parent
W = R.parent
sys.path[:0] = [str(W/'hero-polish'), str(W/'mini-foots/tools')]
from archive_helpers import archive, entries, storm, read_storm, c
from validate_objdata import validate
import objdata


def read(path, name):
    handle = c.c_void_p()
    assert storm.SFileOpenArchive(str(path), 0, 0x100, c.byref(handle))
    try:
        return read_storm(handle, name)
    finally:
        assert storm.SFileCloseArchive(handle)


original = R/'release/FF799X_Rx_Consolidated_Undying_v42.w3x'
tested = R/'diagnostics/FF_v42_ability_flags_test.w3x'
release = R/'release/FF799X_Rx_Consolidated_Undying_v42a.w3x'
try:
    validate(read(original, 'war3map.w3a'), True)
except ValueError as error:
    rejected = str(error)
else:
    raise AssertionError('Regression: malformed original was accepted')

bad_path = R/'diagnostics/original-invalid.w3a'
bad_path.write_bytes(read(original, 'war3map.w3a'))
bad = objdata.load(str(bad_path))
try:
    objdata.dump(bad)
except ValueError:
    pass
else:
    raise AssertionError('Writer accepted a malformed v3 set count')
fixed = objdata.load(str(R/'src/war3map.w3a'))
changes = []
for before_table, after_table in zip(bad['tables'], fixed['tables']):
    assert len(before_table) == len(after_table)
    for before, after in zip(before_table, after_table):
        if before == after:
            continue
        assert before['newId'] == after['newId']
        assert before['flags'] == 0 and after['flags'] == 1
        expected = dict(before, flags=1)
        assert expected == after
        changes.append(after['newId'])
assert set(changes) == {f'mD{i:02X}' for i in range(256)}

left, right = archive(tested), archive(release)
le, re = entries(left), entries(right)
ignored = set()
for a in (left, right):
    for name in ('war3map.wts', '(listfile)', '(attributes)', '(signature)'):
        entry = a.get_hash_table_entry(name)
        if entry:
            ignored.add((entry.hash_a, entry.hash_b, entry.locale, entry.platform))
assert le.keys()-ignored == re.keys()-ignored
for key in le.keys()-ignored:
    assert le[key] == re[key], ('Game payload differs from tested map', key)
assert read(tested, 'war3map.wts').replace(
    b'v42 TEST ability flags', b'Consolidated Undying v42a'
) == read(release, 'war3map.wts')
assert read(original, 'war3map.j') == read(release, 'war3map.j')
assert read(tested, 'war3map.w3a') == read(release, 'war3map.w3a')

report = json.loads((R/'verification.json').read_text())
assert report['sha256'] == hashlib.sha256(release.read_bytes()).hexdigest()
report.update(
    load_fix='256 digestion indicator v3 modification-set counts corrected from 0 to 1',
    independent_format_validation='passed; original malformed data rejected',
    original_validation_error=rejected,
    live_test='User confirmed ability-flags diagnostic loads successfully; release game payloads match that diagnostic',
    tested_diagnostic_sha256=hashlib.sha256(tested.read_bytes()).hexdigest(),
    identical_tested_payloads=len(le.keys()-ignored),
    script_unchanged_from_compiled_v42=True,
)
(R/'verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
