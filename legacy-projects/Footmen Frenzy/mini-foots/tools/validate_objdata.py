"""Validate actual object-data set framing independently of legacy objdata.

Format reference:
https://github.com/stijnherfst/HiveWE/wiki/war3map(skin).w3*-Modifications
"""
import struct


def validate(data, levelled):
    pos = 0

    def take(n):
        nonlocal pos
        if n < 0 or pos + n > len(data):
            raise ValueError(f'Truncated object data at {pos}')
        result = data[pos:pos+n]
        pos += n
        return result

    def integer():
        return struct.unpack('<I', take(4))[0]

    def count(label):
        n = integer()
        if n > (len(data)-pos)//4:
            raise ValueError(f'Invalid {label} count {n} at {pos-4}')
        return n

    version = integer()
    if version not in (1, 2, 3):
        raise ValueError(f'Unsupported version {version}')
    objects = 0
    for _ in range(2):
        for _ in range(count('object')):
            take(8)
            objects += 1
            sets = count('set') if version >= 3 else 1
            for _ in range(sets):
                if version >= 3:
                    integer()
                for _ in range(count('modification')):
                    take(4)
                    kind = integer()
                    if levelled:
                        take(8)
                    if kind in (0, 1, 2):
                        take(4)
                    elif kind == 3:
                        end = data.find(b'\0', pos)
                        if end < 0:
                            raise ValueError('Unterminated object string')
                        take(end-pos+1)
                    else:
                        raise ValueError(f'Invalid modification type {kind} at {pos}')
                    take(4)
    if pos != len(data):
        raise ValueError(f'Trailing object data: {len(data)-pos} bytes')
    return objects
