# Minimal WC3 object-data reader/writer that handles BOTH format versions.
# v1/v2 entries: oldId newId modCount   (no flags/extra)
# v3 single-set entries: oldId newId setsCount setFlag modCount
# Legacy dictionary names: flags=setsCount, extra=setFlag. This reader is
# retained for inspecting old malformed artifacts; dump refuses to emit them.
# Levelled files (.w3a .w3d .w3q) carry level+dataPtr on every mod.
import struct, sys, json

LEVELLED = ('.w3a', '.w3d', '.w3q')


def rc(b):
    return b.decode('latin-1')


def rcb(s):
    assert len(s) == 4, s
    return s.encode('latin-1')


class Reader:
    def __init__(self, data):
        self.d = data
        self.o = 0

    def i32(self):
        v = struct.unpack_from('<i', self.d, self.o)[0]
        self.o += 4
        return v

    def f32(self):
        v = struct.unpack_from('<f', self.d, self.o)[0]
        self.o += 4
        return v

    def raw(self, n):
        v = self.d[self.o:self.o + n]
        self.o += n
        return v

    def cstr(self):
        e = self.d.index(b'\x00', self.o)
        v = self.d[self.o:e]
        self.o = e + 1
        return v.decode('latin-1')


def load(path):
    ext = path[path.rfind('.'):].lower()
    lev = ext in LEVELLED
    d = open(path, 'rb').read()
    r = Reader(d)
    ver = r.i32()
    v3 = ver >= 3
    tables = []
    for t in range(2):
        n = r.i32()
        entries = []
        for _ in range(n):
            e = {'oldId': rc(r.raw(4)), 'newId': rc(r.raw(4))}
            if v3:
                e['flags'] = r.i32()
                e['extra'] = r.i32()
            mods = []
            for _ in range(r.i32()):
                m = {'id': rc(r.raw(4)), 'type': r.i32()}
                if lev:
                    m['level'] = r.i32()
                    m['ptr'] = r.i32()
                if m['type'] == 0:
                    m['value'] = r.i32()
                elif m['type'] in (1, 2):
                    m['value'] = r.f32()
                elif m['type'] == 3:
                    m['value'] = r.cstr()
                else:
                    raise ValueError('unknown mod type %r at %d' % (m['type'], r.o))
                m['end'] = r.raw(4).hex()
                mods.append(m)
            e['mods'] = mods
            entries.append(e)
        tables.append(entries)
    assert r.o == len(d), 'trailing bytes: %d of %d' % (r.o, len(d))
    return {'version': ver, 'levelled': lev, 'v3': v3, 'tables': tables}


def dump(obj):
    out = bytearray()
    out += struct.pack('<i', obj['version'])
    for entries in obj['tables']:
        out += struct.pack('<i', len(entries))
        for e in entries:
            out += rcb(e['oldId']) + rcb(e['newId'])
            if obj['v3']:
                if e['flags'] != 1:
                    raise ValueError('Single-set writer requires setsCount=1 for %r; legacy flags=%r'
                                     % (e['newId'], e['flags']))
                out += struct.pack('<ii', e['flags'], e['extra'])
            out += struct.pack('<i', len(e['mods']))
            for m in e['mods']:
                out += rcb(m['id']) + struct.pack('<i', m['type'])
                if obj['levelled']:
                    out += struct.pack('<ii', m['level'], m['ptr'])
                if m['type'] == 0:
                    out += struct.pack('<i', m['value'])
                elif m['type'] in (1, 2):
                    out += struct.pack('<f', m['value'])
                else:
                    out += m['value'].encode('latin-1') + b'\x00'
                out += bytes.fromhex(m['end'])
    return bytes(out)


if __name__ == '__main__':
    path = sys.argv[1]
    obj = load(path)
    # round-trip gate: refuse to trust the parser unless it is byte-exact
    assert dump(obj) == open(path, 'rb').read(), 'ROUND TRIP MISMATCH'
    if len(sys.argv) > 2 and sys.argv[2] == '--json':
        print(json.dumps(obj, indent=1))
    else:
        print('version=%d levelled=%s  table0=%d table1=%d  (round-trip ok)'
              % (obj['version'], obj['levelled'], len(obj['tables'][0]), len(obj['tables'][1])))
        for ti, entries in enumerate(obj['tables']):
            for e in entries:
                print('  T%d %s -> %s  (%d mods)' % (ti, e['oldId'], e['newId'], len(e['mods'])))
