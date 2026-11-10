"""
objdata_fieldmerge.py - field-level merge of World-Editor-saved object data.

WHY THIS EXISTS
---------------
Substituting a World-Editor-saved .w3u/.w3t/.w3a wholesale loses data. Measured
on the v66 EDITME round trip, the editor silently DROPPED 445 fields it was
never asked to touch:

    war3map.w3t   97 unam, 97 utip, 1 utub, 96 ifil, 6 igol, 1 ilum
    war3map.w3u   1 unam, 1 utip, 1 utub
    war3map.w3a   78 anam/aart/atp1/aub1/ahky, 56 acdn, 50 Ncl2/amcs/aare,
                  78 abpx/abpy, 28 alev

That is every item name, every item tooltip, 96 item icons and six item gold
costs - none of which were edits, all of which would ship as regressions.

So instead of swapping files, this takes the TARGET's object data as the base
and applies ONLY the fields whose values the user actually changed, plus any
brand-new entries. Anything the editor dropped simply stays as the target had it.

SAFETY
------
The serialiser is gated on round-trip fidelity: serialise(parse(x)) must equal x
byte-for-byte for every input file before any merge is attempted. Modification
end-tokens are carried verbatim rather than assumed to be four NULs, because
this map family does not use a uniform token.

USAGE
-----
    python objdata_fieldmerge.py <targetDir> <editedDir> <outDir>

Prints the applied change set and exits non-zero on any inconsistency.
"""

import os
import struct
import sys

# .w3a (abilities), .w3q (upgrades) and .w3d (doodads) carry a level/variation
# and a data-pointer on every modification; the others do not.
LEVELLED = {'.w3a', '.w3q', '.w3d'}


class Mod(object):
    __slots__ = ('modid', 'vartype', 'level', 'pointer', 'value', 'endtoken')

    def __init__(self, modid, vartype, level, pointer, value, endtoken):
        self.modid = modid
        self.vartype = vartype
        self.level = level
        self.pointer = pointer
        self.value = value
        self.endtoken = endtoken

    def key(self):
        return (self.modid, self.level)


class Entry(object):
    __slots__ = ('oldid', 'newid', 'sets')

    def __init__(self, oldid, newid, sets):
        self.oldid = oldid
        self.newid = newid
        self.sets = sets          # list of (mode_or_None, [Mod, ...])

    def key(self):
        return self.newid if self.newid.strip('\x00') else self.oldid

    def mods(self):
        for mode, mods in self.sets:
            for m in mods:
                yield m


def parse(path):
    levelled = os.path.splitext(path)[1].lower() in LEVELLED
    b = open(path, 'rb').read()
    o = 0
    ver = struct.unpack_from('<i', b, o)[0]
    o += 4
    tables = []
    for _t in range(2):
        count = struct.unpack_from('<i', b, o)[0]
        o += 4
        entries = []
        for _e in range(count):
            oldid = b[o:o + 4].decode('latin-1')
            newid = b[o + 4:o + 8].decode('latin-1')
            o += 8
            nsets = 1
            if ver >= 3:
                nsets = struct.unpack_from('<i', b, o)[0]
                o += 4
            sets = []
            for _s in range(nsets):
                mode = None
                if ver >= 3:
                    mode = struct.unpack_from('<i', b, o)[0]
                    o += 4
                nmods = struct.unpack_from('<i', b, o)[0]
                o += 4
                mods = []
                for _m in range(nmods):
                    modid = b[o:o + 4].decode('latin-1')
                    o += 4
                    vartype = struct.unpack_from('<i', b, o)[0]
                    o += 4
                    level = pointer = 0
                    if levelled:
                        level = struct.unpack_from('<i', b, o)[0]
                        pointer = struct.unpack_from('<i', b, o + 4)[0]
                        o += 8
                    if vartype == 3:
                        e = b.index(b'\x00', o)
                        value = b[o:e].decode('latin-1')
                        o = e + 1
                    elif vartype == 0:
                        value = struct.unpack_from('<i', b, o)[0]
                        o += 4
                    else:
                        value = struct.unpack_from('<f', b, o)[0]
                        o += 4
                    endtoken = b[o:o + 4]          # verbatim, never assumed
                    o += 4
                    mods.append(Mod(modid, vartype, level, pointer, value, endtoken))
                sets.append((mode, mods))
            entries.append(Entry(oldid, newid, sets))
        tables.append(entries)
    if o != len(b):
        raise ValueError('%s: %d trailing bytes after parse' % (path, len(b) - o))
    return ver, tables, levelled


def serialise(ver, tables, levelled):
    out = [struct.pack('<i', ver)]
    for entries in tables:
        out.append(struct.pack('<i', len(entries)))
        for e in entries:
            out.append(e.oldid.encode('latin-1'))
            out.append(e.newid.encode('latin-1'))
            if ver >= 3:
                out.append(struct.pack('<i', len(e.sets)))
            for mode, mods in e.sets:
                if ver >= 3:
                    out.append(struct.pack('<i', mode))
                out.append(struct.pack('<i', len(mods)))
                for m in mods:
                    out.append(m.modid.encode('latin-1'))
                    out.append(struct.pack('<i', m.vartype))
                    if levelled:
                        out.append(struct.pack('<i', m.level))
                        out.append(struct.pack('<i', m.pointer))
                    if m.vartype == 3:
                        out.append(m.value.encode('latin-1') + b'\x00')
                    elif m.vartype == 0:
                        out.append(struct.pack('<i', m.value))
                    else:
                        out.append(struct.pack('<f', m.value))
                    out.append(m.endtoken)
    return b''.join(out)


def roundtrip_ok(path):
    ver, tables, lev = parse(path)
    return serialise(ver, tables, lev) == open(path, 'rb').read()


def index(tables):
    out = {}
    for entries in tables:
        for e in entries:
            out.setdefault(e.key(), []).append(e)
    return out


def merge(target_path, edited_path, out_path):
    name = os.path.basename(target_path)

    for p in (target_path, edited_path):
        if not roundtrip_ok(p):
            raise SystemExit('FATAL round-trip mismatch, refusing to merge: %s' % p)

    tver, ttab, tlev = parse(target_path)
    ever, etab, elev = parse(edited_path)
    if tver != ever:
        raise SystemExit('%s: version %d vs %d' % (name, tver, ever))

    tidx, eidx = index(ttab), index(etab)

    changed, added_entries, added_fields = [], [], []

    # 1. values the user actually changed on entries that exist in both
    for key, tents in tidx.items():
        eents = eidx.get(key)
        if not eents:
            continue
        evals = {}
        for e in eents:
            for m in e.mods():
                evals[m.key()] = m
        for te in tents:
            for tm in te.mods():
                em = evals.get(tm.key())
                if em is None:
                    continue                       # editor dropped it: keep target's
                same = (em.vartype == tm.vartype and (
                    em.value == tm.value if tm.vartype in (0, 3)
                    else abs(em.value - tm.value) < 1e-6))
                if not same:
                    changed.append((key, tm.modid, tm.level, tm.value, em.value))
                    tm.value = em.value
                    tm.vartype = em.vartype

    # 2. fields the user ADDED to an existing entry
    for key, eents in eidx.items():
        tents = tidx.get(key)
        if not tents:
            continue
        tkeys = set()
        for te in tents:
            for tm in te.mods():
                tkeys.add(tm.key())
        for ee in eents:
            for em in ee.mods():
                if em.key() not in tkeys:
                    tents[0].sets[0][1].append(em)
                    added_fields.append((key, em.modid, em.level, em.value))
                    tkeys.add(em.key())

    # 3. brand-new entries the user created
    for key, eents in eidx.items():
        if key in tidx:
            continue
        for ee in eents:
            # custom table is index 1; new objects always live there
            ttab[1].append(ee)
            added_entries.append((key, ee.oldid, sum(1 for _ in ee.mods())))

    data = serialise(tver, ttab, tlev)
    open(out_path, 'wb').write(data)

    print('--- %s' % name)
    print('    %d changed, %d fields added, %d new entries' %
          (len(changed), len(added_fields), len(added_entries)))
    for k, mid, lv, old, new in changed:
        lvs = '' if lv == 0 else ' L%d' % lv
        print('      %s %s%s: %r -> %r' % (k, mid, lvs, old, new))
    for k, mid, lv, val in added_fields:
        lvs = '' if lv == 0 else ' L%d' % lv
        print('      + %s %s%s = %r' % (k, mid, lvs, val))
    for k, base, n in added_entries:
        print('      + NEW ENTRY %s (from %s, %d fields)' % (k, base, n))
    return len(changed) + len(added_fields) + len(added_entries)


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    tdir, edir, odir = sys.argv[1:4]
    if not os.path.isdir(odir):
        os.makedirs(odir)
    total = 0
    for name in ('war3map.w3u', 'war3map.w3t', 'war3map.w3a',
                 'war3map.w3h', 'war3map.w3q', 'war3map.w3b', 'war3map.w3d'):
        t = os.path.join(tdir, name)
        e = os.path.join(edir, name)
        if not (os.path.exists(t) and os.path.exists(e)):
            continue
        total += merge(t, e, os.path.join(odir, name))
    print('\nTOTAL applied: %d' % total)
    if total == 0:
        raise SystemExit('nothing to merge')


if __name__ == '__main__':
    main()
