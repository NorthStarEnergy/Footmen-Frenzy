from pathlib import Path
import sys, shutil, json, hashlib, subprocess, struct, copy
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions,archive,entries,work
from game_data import chunks,game_read,ini
import objdata
base=W/'799x-backport/release/FF799X_Rx_RequiemFix_v33.w3x'
O=R/'src';O.mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
names=['war3map.j','war3map.w3u','war3map.w3a','war3map.wts','war3map.imp']
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in names:(O/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
model=(R/'assets/Guldan.mdx').read_bytes();ch=chunks(model)
seq=ch['SEQS'];animations={seq[i:i+80].split(b'\0')[0].decode():i//132 for i in range(0,len(seq),132)}
assert all(animations[n]==i for n,i in [('Spell One',10),('Spell Two',11),('Spell Throw',12)])
assert ch.get('CAMS') and 'Portrait Talk - 1' in animations
# Validate all referenced textures, including native dependencies.
textures=[]
for i in range(0,len(ch['TEXS']),268):
 name=ch['TEXS'][i+4:i+264].split(b'\0')[0].decode()
 if name:
  assert (R/'assets'/name).exists() or game_read('war3.w3mod:'+name) or game_read('war3.w3mod:'+name[:-4]+'.dds'),name
  textures.append(name)
voice=ini(game_read('war3.w3mod:units\\unitskin.txt'))['Ogld']['unitSound']
assert voice=='PitLord'
s=(O/'war3map.j').read_text(encoding='utf-8-sig');original=s
f=functions(s)['OM_OnCastAnimation']
new=f.replace('''        if a == OM_ATTACK or a == OM_PULSE or a == OM_PROTECT then
            call SetUnitAnimationByIndex(u, 1)
        elseif a == OM_SHOCK then
            call SetUnitAnimationByIndex(u, 9)''','''        // Tauer Guldan: Z/C = Spell Throw, X = Spell One, V = Spell Two.
        if a == OM_ATTACK or a == OM_PROTECT then
            call SetUnitAnimationByIndex(u, 12)
        elseif a == OM_PULSE then
            call SetUnitAnimationByIndex(u, 10)
        elseif a == OM_SHOCK then
            call SetUnitAnimationByIndex(u, 11)''')
assert new!=f;s=s.replace(f,new,1)
f=functions(s)['OM_WindupFX']
new=f.replace('''    // Native channel cast transitions into the pack's Spell Attack sequence.
    // Its release gesture lands 0.5 seconds later, exactly at Shockwave impact.
    call SetUnitAnimationByIndex(OM_Hero[i], 1)''','''    // Keep the requested Guldan Spell Two sequence during Shockwave windup.
    call SetUnitAnimationByIndex(OM_Hero[i], 11)''')
assert new!=f;s=s.replace(f,new,1)
s=s.replace('FF799X - Requiem Fix v33','FF799X - Orianna Guldan v34')
(O/'war3map.j').write_text(s,encoding='utf8')
p=O/'war3map.wts';raw=p.read_bytes();assert b'FF799X - Requiem Fix v33' in raw;p.write_bytes(raw.replace(b'FF799X - Requiem Fix v33',b'FF799X - Orianna Guldan v34'))
u=objdata.load(str(O/'war3map.w3u'));old_u=copy.deepcopy(u)
hero=next(e for t in u['tables'] for e in t if e['newId']=='HOr1')
changes={'umdl':'Models\\OriannaGuldan\\Guldan.mdx','usnd':voice,'uico':'ReplaceableTextures\\CommandButtons\\BTNGuldan.blp','ussi':'ReplaceableTextures\\CommandButtons\\BTNGuldan.blp'}
for key,val in changes.items():
 m=next(m for m in hero['mods'] if m['id']==key);m['value']=val
(O/'war3map.w3u').write_bytes(objdata.dump(u))
a=objdata.load(str(O/'war3map.w3a'));old_a=copy.deepcopy(a)
anims={'AOz1':'spell,throw','AOz2':'spell,one','AOz3':'spell,throw','AOz4':'spell,two'}
for t in a['tables']:
 for e in t:
  if e['newId'] in anims:
   mods=[m for m in e['mods'] if m['id']=='aani'];assert len(mods)==1
   mods[0]['value']=anims[e['newId']]
(O/'war3map.w3a').write_bytes(objdata.dump(a))
imports={'Models\\OriannaGuldan\\Guldan.mdx':R/'assets/Guldan.mdx','Guldan.blp':R/'assets/Guldan.blp'}
p=O/'war3map.imp';raw=p.read_bytes();version,count=struct.unpack_from('<II',raw)
for name in imports:
 assert name.encode()+b'\0' not in raw
 raw+=b'\x0d'+name.encode()+b'\0'
p.write_bytes(struct.pack('<II',version,count+len(imports))+raw[8:])
# Only presentation fields and the two animation functions may change.
for table,oldtable in zip(u['tables'],old_u['tables']):
 for e,old in zip(table,oldtable):
  if e['newId']!='HOr1':assert e==old
  else:
   for m,m0 in zip(e['mods'],old['mods']):
    if m['id'] not in changes:assert m==m0
for table,oldtable in zip(a['tables'],old_a['tables']):
 for e,old in zip(table,oldtable):
  if e['newId'] not in anims:assert e==old
  else:
   for m,m0 in zip(e['mods'],old['mods']):
    if m['id']!='aani':assert m==m0
bf,sf=functions(original),functions(s);changed=[n for n in bf if bf[n]!=sf[n]]
assert set(changed)=={'OM_OnCastAnimation','OM_WindupFX'}
run=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(O/'war3map.j')],capture_output=True,text=True)
(R/'audit/compiler.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
release=R/'release';release.mkdir(exist_ok=True);out=release/'FF799X_Rx_OriannaGuldan_v34.w3x';shutil.copy2(base,out)
files={name:O/name for name in names};files.update(imports)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for name,path in files.items():assert storm.SFileAddFileEx(h,str(path),name.encode(),0x80000200,2,2),name
assert storm.SFileCloseArchive(h)
before=archive(base);after=archive(out);oldentries,newentries=entries(before),entries(after);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name,path in files.items():
 assert read_storm(h,name)==path.read_bytes(),name
 e=before.get_hash_table_entry(name)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert storm.SFileCloseArchive(h)
for name in ['(listfile)','(attributes)','(signature)']:
 e=before.get_hash_table_entry(name)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in oldentries.items():
 if k not in skip:assert newentries.get(k)==v,k
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
for p in [out,out.with_suffix('.sha256')]:shutil.copy2(p,W/'799x-backport/release'/p.name)
report=dict(output=str(out),sha256=sha,model_author='Tauer',model_source='https://www.hiveworkshop.com/threads/guldan.295598/',voice=voice,animations={'Z':'Spell Throw (12)','X':'Spell One (10)','C':'Spell Throw (12)','V':'Spell Two (11)'},changed_functions=changed,preserved_archive_entries=len(oldentries.keys()-skip),texture_dependencies=textures,portrait='Embedded camera and talking sequences',compiler='passed',live_test='Pending Warcraft III playtest')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
(R/'CREDITS.txt').write_text('Guldan model and texture by Tauer\nhttps://www.hiveworkshop.com/threads/guldan.295598/\nImported original model/texture, including embedded portrait.\nVoice: native PitLord, matching Warcraft III Guldan unit definition.\n')

