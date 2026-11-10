from pathlib import Path
import struct


# Every modification in a .w3u is  id(4) type(4) value(4 or cstring) end-marker(4).
# Dropping the end marker desynchronises the walk and Warcraft III then fails to
# parse the object table, which shows up as a black screen before the loading bar.
def skip_value(data: bytes, offset: int, kind: int) -> int:
    if kind == 3:
        return data.index(b'\0', offset) + 1
    return offset + 4


def object_end(data: bytes, start: int) -> int:
    """Offset one past the last modification of the object starting at `start`."""
    cursor = start + 8
    sets = struct.unpack_from('<I', data, cursor)[0]
    cursor += 4
    if sets != 1:
        raise ValueError(f'expected a single modification set, found {sets}')
    cursor += 4  # set flags
    count = struct.unpack_from('<I', data, cursor)[0]
    cursor += 4
    for _ in range(count):
        cursor += 4
        kind = struct.unpack_from('<I', data, cursor)[0]
        cursor += 4
        cursor = skip_value(data, cursor, kind)
        cursor += 4  # end of modification
    return cursor


def patch_unit(data: bytes, unit_id: bytes) -> bytes:
    start = data.index(b'hfoo' + unit_id)
    count_offset = start + 16
    count = struct.unpack_from('<I', data, count_offset)[0]
    cursor = object_end(data, start)
    additions = b''.join([
        b'ubpx' + struct.pack('<I', 0) + struct.pack('<i', 2) + b'\0\0\0\0',
        b'ubpy' + struct.pack('<I', 0) + struct.pack('<i', 1) + b'\0\0\0\0',
        b'uhot' + struct.pack('<I', 3) + b'V\0' + b'\0\0\0\0',
    ])
    patched = bytearray(data[:cursor] + additions + data[cursor:])
    struct.pack_into('<I', patched, count_offset, count + 3)
    return bytes(patched)


def check(data: bytes) -> int:
    """Re-read the whole table so a desync fails here instead of in the game."""
    cursor = 4
    objects = 0
    for _ in range(2):
        total = struct.unpack_from('<I', data, cursor)[0]
        cursor += 4
        for _ in range(total):
            cursor = object_end(data, cursor)
            objects += 1
    if cursor != len(data):
        raise ValueError(f'{len(data) - cursor} trailing bytes after {objects} objects')
    return objects


root = Path(__file__).resolve().parents[1]
source = root / 'roundtrip' / 'SF_Test1.7_v73' / 'files' / 'war3map.w3u'
target = root / 'src' / 'war3map.w3u'
data = source.read_bytes()

for unit_id in (b'h02U', b'h02V'):
    data = patch_unit(data, unit_id)

objects = check(data)
target.write_bytes(data)
print(f'Patched page selectors ({objects} objects verified): {target}')
