import sys, re
sys.path.insert(0, r'C:\Users\Ryan1\Documents\Footmen Frenzy Development\tools')
import objdata_fieldmerge as obj

base = r'C:\Users\Ryan1\Documents\Footmen Frenzy Development\outputs\demonknight-soulhook-v70\verified'
expected = r'C:\Users\Ryan1\Documents\Footmen Frenzy Development\outputs\demonknight-soulhook-v70\edited'

def load(p, key):
    v, t, l = obj.parse(p)
    return next((e for tab in t for e in tab if e.key() == key), None)

def mods(e):
    d = {}
    for m in e.mods():
        d[(m.modid, m.level)] = m.value
    return d

fails = []
def check(cond, msg):
    if not cond:
        fails.append(msg)

# --- abilities from the packed map
for name in ('war3map.w3a', 'war3map.w3u'):
    check(open(base + '\\' + name, 'rb').read() == open(expected + '\\' + name, 'rb').read(), name + ' packed != edited')

hook = load(base + r'\war3map.w3a', 'ADk5')
check(hook is not None, 'ADk5 missing')
h = mods(hook)
check(h[('anam', 0)] == 'Soul Hook', 'ADk5 name %r' % h.get(('anam', 0)))
check(h[('ahky', 0)] == 'C', 'ADk5 hotkey %r' % h.get(('ahky', 0)))
check(h[('arhk', 0)] == 'E', 'ADk5 research hotkey %r' % h.get(('arhk', 0)))
check(h[('abpx', 0)] == 2 and h[('abpy', 0)] == 2, 'ADk5 button pos %r %r' % (h.get(('abpx', 0)), h.get(('abpy', 0))))
check(h[('alev', 0)] == 6, 'ADk5 levels %r' % h.get(('alev', 0)))
check(h[('areq', 0)] == '', 'ADk5 requirement %r' % h.get(('areq', 0)))
check(h[('aret', 0)] == 'Learn Soul Hook [|cffffcc00E|r]', 'ADk5 research tip %r' % h.get(('aret', 0)))
check(h[('Ncl6', 1)] == 'carrionswarm', 'ADk5 base order %r' % h.get(('Ncl6', 1)))
check(h[('aart', 0)] == 'ReplaceableTextures\\CommandButtons\\BTNChainLightning.blp', 'ADk5 icon')

want_mana = [60, 70, 80, 90, 100, 110]
want_cd = [12.0, 11.6, 11.2, 10.8, 10.4, 10.0]
for r in range(1, 7):
    check(h[('amcs', r)] == want_mana[r-1], 'ADk5 mana L%d %r' % (r, h.get(('amcs', r))))
    check(abs(h[('acdn', r)] - want_cd[r-1]) < 1e-6, 'ADk5 cd L%d %r' % (r, h.get(('acdn', r))))
    check(abs(h[('aran', r)] - 450.0) < 1e-6, 'ADk5 range L%d %r' % (r, h.get(('aran', r))))
    check(h[('atar', r)] == '', 'ADk5 target L%d %r' % (r, h.get(('atar', r))))
    tel = h[('atp1', r)]
    check(('Soul Hook' in tel) and ('C|r]' in tel), 'ADk5 tooltip L%d %r' % (r, tel))
    check('Blood Tithe' not in h[('aub1', r)], 'ADk5 desc still mentions Blood Tithe L%d' % r)
    check(str(80 + 40*r) in h[('aub1', r)], 'ADk5 desc damage L%d' % r)
check('Blood Tithe' not in h[('arut', 0)], 'ADk5 research desc mentions Blood Tithe')
check(h[('arut', 0)].startswith('|cffffcc00Requires hero level 1|r|n|n'), 'ADk5 research desc missing level prefix: %r' % h.get(('arut', 0), '')[:70])
check(not h[('aub1', 1)].startswith('|cffffcc00Requires hero level'), 'ADk5 learn desc should not carry the research prefix')

stun = load(base + r'\war3map.w3a', 'ADk6')
check(stun is not None, 'ADk6 missing')
s = mods(stun)
check(s[('anam', 0)] == 'Soul Hook stun', 'ADk6 name %r' % s.get(('anam', 0)))
check(s[('abuf', 1)] == 'BGr2', 'ADk6 buff %r' % s.get(('abuf', 1)))
check(s[('amsp', 0)] == 10000, 'ADk6 missile speed %r' % s.get(('amsp', 0)))
for r in range(1, 7):
    check(abs(s[('adur', r)] - (0.5 + 0.1*(r-1))) < 1e-6, 'ADk6 dur L%d %r' % (r, s.get(('adur', r))))
    check(s[('amcs', r)] == 0 and abs(s[('acdn', r)]) < 1e-6, 'ADk6 cost L%d' % r)
    check(s[('Htb1', r)] == 0.0, 'ADk6 damage L%d %r' % (r, s.get(('Htb1', r))))

# --- removed Blood Tithe wording from the surviving abilities
for k in ('ADk1', 'ADk2'):
    e = load(base + r'\war3map.w3a', k)
    for m in e.mods():
        if isinstance(m.value, str):
            check('Blood Tithe' not in m.value, '%s %s still mentions Blood Tithe' % (k, m.modid))

# --- hero
hero = load(base + r'\war3map.w3u', 'HDk1')
hd = mods(hero)
check(hd[('uhab', 0)] == 'ADk1,ADk2,ADk5,ADk4', 'HDk1 abilities %r' % hd.get(('uhab', 0)))
check('Blood Tithe' not in hd[('utub', 0)], 'HDk1 tooltip mentions Blood Tithe')
check('Soul Hook' in hd[('utub', 0)], 'HDk1 tooltip missing Soul Hook')

# --- no other hero references ADk5/ADk6
v, t, l = obj.parse(base + r'\war3map.w3u')
for tab in t:
    for e in tab:
        for m in e.mods():
            if isinstance(m.value, str) and m.modid == 'uhab' and e.key() != 'HDk1':
                check('ADk5' not in m.value and 'ADk6' not in m.value, 'unexpected ADk5/6 on %s' % e.key())

print('FAILURES:', len(fails))
for f in fails:
    print(' -', f)
print('ADk5 levels:', [h[('atp1', r)] for r in range(1, 7)])
print('ADk5 L6 desc:', h[('aub1', 6)])
