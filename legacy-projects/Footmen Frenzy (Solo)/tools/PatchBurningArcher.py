from pathlib import Path
import struct


def skip_value(data: bytes, offset: int, kind: int) -> int:
    return data.index(b'\0', offset) + 1 if kind == 3 else offset + 4


def object_end(data: bytes, start: int) -> tuple[int, int]:
    sets = struct.unpack_from('<I', data, start + 8)[0]
    cursor = start + 12
    total = 0
    for _ in range(sets):
        cursor += 4
        count_offset = cursor
        count = struct.unpack_from('<I', data, cursor)[0]
        cursor += 4
        if total == 0:
            first_count_offset = count_offset
        total += count
        for _ in range(count):
            cursor += 4
            kind = struct.unpack_from('<I', data, cursor)[0]
            cursor += 4
            cursor = skip_value(data, cursor, kind)
            cursor += 4
    return cursor, first_count_offset


def patch(data: bytes) -> bytes:
    cursor = 4
    for _ in range(2):
        total = struct.unpack_from('<I', data, cursor)[0]
        cursor += 4
        for _ in range(total):
            if data[cursor:cursor + 4] == b'nskf':
                end, count_offset = object_end(data, cursor)
                count = struct.unpack_from('<I', data, count_offset)[0]
                # uhpm, integer value 550, modification end marker.
                mod = b'uhpm' + struct.pack('<I', 0) + struct.pack('<i', 550) + struct.pack('<I', 0)
                return data[:end] + mod + data[end:], count_offset, count
            cursor, _ = object_end(data, cursor)
    raise ValueError('Burning Archer object nskf not found')


root = Path(__file__).resolve().parents[1]
target = root / 'src' / 'war3map.w3u'
data = target.read_bytes()
patched, count_offset, count = patch(data)
patched = bytearray(patched)
struct.pack_into('<I', patched, count_offset, count + 1)
target.write_bytes(patched)
print(f'Patched nskf Burning Archer HP to 550; {len(patched)} bytes written')
