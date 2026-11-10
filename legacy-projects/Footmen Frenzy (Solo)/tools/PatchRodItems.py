from pathlib import Path
import struct


def skip_value(data: bytes, offset: int, kind: int) -> int:
    if kind == 3:
        return data.index(b'\0', offset) + 1
    return offset + 4


def field_value_offset(data: bytes, base_id: bytes, new_id: bytes, field: bytes) -> int:
    """Offset of `field`'s value inside the object identified by (base_id, new_id).

    Searching for the raw field id instead would run past the end of the object and
    silently reprice whichever object happens to come next.
    """
    cursor = data.index(base_id + new_id) + 8
    sets = struct.unpack_from('<I', data, cursor)[0]
    cursor += 4
    if sets != 1:
        raise ValueError(f'{base_id}/{new_id}: expected a single modification set, found {sets}')
    cursor += 4  # set flags
    count = struct.unpack_from('<I', data, cursor)[0]
    cursor += 4
    for _ in range(count):
        mod_id = bytes(data[cursor:cursor + 4])
        cursor += 4
        kind = struct.unpack_from('<I', data, cursor)[0]
        cursor += 4
        if mod_id == field:
            return cursor
        cursor = skip_value(data, cursor, kind)
        cursor += 4  # end of modification
    raise ValueError(f'{base_id}/{new_id} has no {field} modification')


root = Path(__file__).resolve().parents[1]
source = root / 'roundtrip' / 'SF_Test1.7_v73' / 'files' / 'war3map.w3t'
target = root / 'src' / 'war3map.w3t'
data = bytearray(source.read_bytes())

# Only the custom items are repriced.  The original-table entries they derive from
# ('nspi', 'rat9', 'stwa') keep their stock cost.
for base_id, new_id, cost in (
    (b'wneg', b'I004', 2500),
    (b'wneg', b'I00H', 2000),
    (b'nspi', b'I049', 15000),
    (b'rde3', b'I01Z', 11000),
    (b'rde3', b'I048', 11000),
):
    struct.pack_into('<I', data, field_value_offset(data, base_id, new_id, b'igol'), cost)

# Ring of J33Bus: replace item-granted invulnerability with magic immunity.
old_ring_abilities = b'A02E,Avul,A01G'
new_ring_abilities = b'A02E,AImz,A01G'
if data.count(old_ring_abilities) != 1:
    raise ValueError('Expected exactly one Ring of J33Bus ability list')
data[data.index(old_ring_abilities):data.index(old_ring_abilities) + len(old_ring_abilities)] = new_ring_abilities

target.write_bytes(data)
print(f'Patched rod costs and Ring of J33Bus immunity: {target}')
