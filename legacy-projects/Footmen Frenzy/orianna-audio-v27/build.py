"""Update Orianna sound, travel speed and Move cooldown in 799X only."""
from pathlib import Path
import sys,shutil,re,json,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import archive,storm,read_storm,c,functions
import objdata
base=R/'base.w3x';source=W/'799x-backport/release/FF799X_Rx_HeroPolish_v26.w3x'
if not base.exists():shutil.copy2(source,base)
O=R/'src';O.mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
a=archive(base);h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in ['war3map.j','war3map.w3a','war3map.wts']:(O/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
original=(O/'war3map.j').read_text(encoding='utf-8-sig');s=original
assert 'constant real OM_SPEED = 1200.0' in s
s=s.replace('constant real OM_SPEED = 1200.0','constant real OM_SPEED = 1320.0',1)
old=functions(s)['OM_CommandSound'];new=old
new=new.replace('    if kind == 2 then\n        set path = "Spells\\\\Orianna\\\\Feedback\\\\Attack.wav"\n        set duration = 750\n    elseif kind == 3 then','    if kind == 3 then',1)
new=new.replace('    set s = CreateSound(path, false, true, true, 0, 0, "SpellsEAX")\n    call SetSoundDuration(s, duration)', '''    if kind == 1 then
        // Native Faerie Dragon projectile cue when the ball is sent to a point.
        set s = CreateSoundFromLabel("FaerieDragonLaunch", false, true, true, 0, 0)
    elseif kind == 2 then
        // ASTS is the Death Alternate sound event in the Stasis Totem model.
        set s = CreateSoundFromLabel("StasisTotemDeath", false, true, true, 0, 0)
    else
        set s = CreateSound(path, false, true, true, 0, 0, "SpellsEAX")
        call SetSoundDuration(s, duration)
    endif''',1)
assert new!=old and 'StasisTotemDeath' in new and 'FaerieDragonLaunch' in new
s=s.replace(old,new,1)
old=functions(s)['FF_HeroTooltips_Init']
new=re.sub(r'^.*\x27AOz1\x27.*$',lambda m:m[0].replace('Cooldown: 8 seconds.','Cooldown: 6 seconds.'),old,flags=re.M)
assert old.count('Cooldown: 8 seconds.')-new.count('Cooldown: 8 seconds.')==6
s=s.replace(old,new,1).replace('FF799X - Hero Polish v26','FF799X - Orianna Audio v27')
(O/'war3map.j').write_text(s,encoding='utf8')
d=objdata.load(str(O/'war3map.w3a'));entry=next(e for t in d['tables'] for e in t if e['newId']=='AOz1')
for mod in entry['mods']:
 if mod['id']=='acdn':assert mod['value']>=2;mod['value']-=2
 if mod['id'] in ['arut','aub1']:mod['value']=mod['value'].replace('Cooldown: 8 seconds.','Cooldown: 6 seconds.')
assert sorted((m['level'],m['value']) for m in entry['mods'] if m['id']=='acdn')==[(i,6.0) for i in range(1,7)]
(O/'war3map.w3a').write_bytes(objdata.dump(d))
p=O/'war3map.wts';before=p.read_bytes();assert b'FF799X - Hero Polish v26' in before;p.write_bytes(before.replace(b'FF799X - Hero Polish v26',b'FF799X - Orianna Audio v27'))
bf,sf=functions(original),functions(s);changed=[n for n in bf if bf[n]!=sf[n]]
assert set(changed)=={'OM_CommandSound','FF_HeroTooltips_Init'},changed
(R/'changes.json').write_text(json.dumps(dict(base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),changed_functions=changed),indent=2))
print('799X v27 source prepared; six ranks now have 6-second Move cooldown.')
