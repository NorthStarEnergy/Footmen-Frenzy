from pathlib import Path
import sys, shutil, json, hashlib, subprocess
R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm, read_storm, c, functions, archive, entries, work
import objdata
base=W/'799x-backport/release/FF799X_Rx_Mundo_v32.w3x'
O=R/'src';O.mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
names=['war3map.j','war3map.w3a','war3map.wts']
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in names:(O/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
s=(O/'war3map.j').read_text(encoding='utf-8-sig');original=s

def edit(name,old,new):
 global s
 f=functions(s)[name];assert old in f,(name,old)
 s=s.replace(f,f.replace(old,new,1),1)

# Let native Channel hold the caster. Pausing inside SPELL_EFFECT freezes the
# native cast before it completes and can resume/re-enter it during cleanup.
edit('DK_OnCast','''        set i = DK_New(4, source)''','''        // One scripted channel per caster, even if an effect event repeats.
        if LoadInteger(DK_Hash, GetHandleId(source), -2) != 0 then
            set source = null
            return
        endif
        set i = DK_New(4, source)''')
edit('DK_OnCast','            call PauseUnit(source, true)\n','')
edit('DK_Free','            call PauseUnit(DK_Source[i], false)\n','')
# Reject stale/repeated completion before enumerating targets or causing damage.
edit('DK_EndRequiem','''    if strike then
        call GroupEnumUnitsInRect''','''    if i == 0 or DK_Kind[i] != 4 then
        call DestroyGroup(targets)
        call DestroyGroup(allHeroes)
        set targets = null
        set allHeroes = null
        set source = null
        set owner = null
        return
    endif
    if strike then
        call GroupEnumUnitsInRect''')
# Stop after detaching on cancellation as well (e.g. ownership change).
edit('DK_EndRequiem','''    if strike then
        if FS_Alive(source) and GetUnitCurrentOrder(source) == OrderId("channel") then
            call IssueImmediateOrder(source, "stop")
        endif
        call DK_Flash''','''    if FS_Alive(source) and GetUnitCurrentOrder(source) == OrderId("channel") then
        call IssueImmediateOrder(source, "stop")
    endif
    if strike then
        call DK_Flash''')
d=objdata.load(str(O/'war3map.w3a'))
e=next(e for t in d['tables'] for e in t if e['newId']=='ADk4')
for rank in range(1,4):
 m=next(m for m in e['mods'] if m['id']=='Ncl1' and m['level']==rank)
 assert abs(m['value']-.001)<.00001
 # Native channel outlives the scripted 3-second impact, which issues stop.
 m['value']=3.25
(O/'war3map.w3a').write_bytes(objdata.dump(d))
s=s.replace('FF799X - Mundo v32','FF799X - Requiem Fix v33')
(O/'war3map.j').write_text(s,encoding='utf8')
p=O/'war3map.wts';p.write_bytes(p.read_bytes().replace(b'FF799X - Mundo v32',b'FF799X - Requiem Fix v33'))
updated=functions(s)
changed=[n for n,f in functions(original).items() if updated[n]!=f]
assert changed==['DK_Free','DK_EndRequiem','DK_OnCast'],changed
assert 'PauseUnit' not in functions(s)['DK_OnCast']+functions(s)['DK_Free']
end=functions(s)['DK_EndRequiem']
assert end.index('call DK_Free(i)') < end.index('call IssueImmediateOrder') < end.index('call FS_Hit')
run=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(O/'war3map.j')],capture_output=True,text=True)
(R/'audit/compiler.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
release=R/'release';release.mkdir(exist_ok=True);out=release/'FF799X_Rx_RequiemFix_v33.w3x';shutil.copy2(base,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for name in names:assert storm.SFileAddFileEx(h,str(O/name),name.encode(),0x80000200,2,2)
assert storm.SFileCloseArchive(h)
before=archive(base);after=archive(out);oldentries,newentries=entries(before),entries(after);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name in names:
 assert read_storm(h,name)==(O/name).read_bytes()
 e=before.get_hash_table_entry(name);skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert storm.SFileCloseArchive(h)
for name in ['(listfile)','(attributes)','(signature)']:
 e=before.get_hash_table_entry(name)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in oldentries.items():
 if k not in skip:assert newentries.get(k)==v,k
# Confirm ability data outside the three follow-through values is identical.
a=objdata.load(str(W/'mundo-gas/src/war3map.w3a'))
for t in d['tables']:
 for e in t:
  if e['newId']=='ADk4':
   for m in e['mods']:
    if m['id']=='Ncl1':m['value']=next(m0['value'] for t0 in a['tables'] for e0 in t0 if e0['newId']=='ADk4' for m0 in e0['mods'] if m0['id']=='Ncl1' and m0['level']==m['level'])
assert d==a
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
for p in [out,out.with_suffix('.sha256')]:shutil.copy2(p,W/'799x-backport/release'/p.name)
report=dict(output=str(out),sha256=sha,changed_functions=changed,preserved_archive_entries=len(oldentries.keys()-skip),compiler='passed',live_test='Pending Warcraft III playtest')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

