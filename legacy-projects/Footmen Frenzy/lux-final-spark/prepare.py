from pathlib import Path
import sys, re, struct, json, wave, math, random, array

R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm, read_storm, c, functions
import objdata

BASE=W/'combined-v68/release/FF799X_Rx_Veigar_Classic_v68.w3x'
O=R/'src';O.mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,0x100,c.byref(h))
names=['war3map.j','war3map.wct','war3map.w3a','war3map.w3u','war3map.wts','war3map.imp','FF_MAINTENANCE.md']
original={n:read_storm(h,n) for n in names};assert storm.SFileCloseArchive(h)
module=(R/'spell.j').read_text();decl=(R/'globals.j').read_text()
anchor='function InitTrig_FF_Runtime takes nothing returns nothing'
def patch_runtime(s):
    s=s.replace('\r',''); assert 'function LX_Init ' not in s
    f=functions(s)['InitTrig_FF_Runtime']
    s=s.replace(f,f.replace('\nendfunction','\n    call LX_Init()\nendfunction'),1)
    assert s.count(anchor)==1
    return s.replace(anchor,module+'\n'+anchor,1)
runtime=patch_runtime(original['war3map.j'].decode('utf-8-sig'))
runtime=runtime.replace('\nendglobals','\n'+decl+'\nendglobals',1)
(O/'war3map.j').write_text(runtime,encoding='utf8')

# Keep the editor's authoritative WCT source synchronized, so saving preserves it.
w=original['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[];counts=[0,0]
while p<len(w):
    n=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+n];p+=n
    t=b.rstrip(b'\0').decode('utf-8-sig').replace('\r','')
    edited=False
    if anchor in t:t=patch_runtime(t);counts[0]+=1;edited=True
    if re.search(r'^globals\b',t,re.M):
        t=t.replace('\nendglobals','\n'+decl+'\nendglobals',1);counts[1]+=1;edited=True
    chunks.append(t.encode('utf8')+(b'\0' if b.endswith(b'\0') else b'') if edited else b)
assert p==len(w) and counts==[1,1],counts
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(b.rstrip(b'\0').decode('utf8').replace('\r','') for b in chunks)
efs=functions(editor);rfs=functions(runtime)
for name in list(functions(module))+['InitTrig_FF_Runtime']:
    assert efs[name]==rfs[name],name
changed=[n for n,f in functions(original['war3map.j'].decode('utf-8-sig').replace('\r','')).items() if rfs[n]!=f]
assert changed==['InitTrig_FF_Runtime'],changed

# Reconstruct compiled editor validation with the authoritative WCT declarations.
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1]
packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
def gnames(s):return set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',s,re.M))
source_names=gnames(header)
extras=[]
for line in packed.splitlines():
    m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
    if m and m[1] not in source_names and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:efs.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')

def field(e,key,val,level=0,typ=3,ptr=0,lev=True):
    e['mods']=[m for m in e['mods'] if not(m['id']==key and m.get('level',0)==level)]
    m=dict(id=key,type=typ,value=val,end=e['newId'].encode().hex())
    if lev:m.update(level=level,ptr=ptr)
    e['mods'].append(m)

for n in ['war3map.w3a','war3map.w3u']:(O/n).write_bytes(original[n])
d=objdata.load(str(O/'war3map.w3a'));assert objdata.dump(d)==original['war3map.w3a']
assert not any(e['newId']=='ALxR' for t in d['tables'] for e in t)
e=dict(oldId='ANcl',newId='ALxR',flags=1,extra=0,mods=[])
for k,v in [('anam','Final Spark'),('ahky','V'),('aart','ReplaceableTextures\\CommandButtons\\BTNResurrection.blp'),('aani','spell'),('atat',''),('acat',''),('aeat',''),('arac',''),('areq','')]:field(e,k,v)
for k,v in [('alev',3),('aher',0),('aite',0),('abpx',3),('abpy',2)]:field(e,k,v,typ=0)
for rank in range(1,4):
    damage=150+250*rank;mana=50+50*rank;cd=80-10*rank
    desc=f'Lock your aim and gather light for 1 second. A faint line intensifies, then erupts into a brilliant beam, dealing {damage} + Intelligence magic damage to all enemies in its path.|n|nRange: 3400. Width: 200. Hits ground and air once, through units and terrain. Excludes allies, buildings, invulnerable and magic-immune units. The caster cannot act while charging; death cancels the cast.|n|nMana: {mana}   Cooldown: {cd} sec'
    field(e,'atp1',f'Final Spark [|cffffcc00V|r] - Rank {rank}',rank)
    field(e,'aub1',desc,rank)
    for k,v in [('acdn',float(cd)),('aran',3400.),('aare',0.),('acas',0.),('adur',0.),('ahdu',0.)]:field(e,k,v,rank,1)
    field(e,'amcs',mana,rank,0);field(e,'atar','',rank)
    for k,v,typ,ptr in [('Ncl1',0.,1,1),('Ncl2',2,0,2),('Ncl3',1,0,3),('Ncl4',0.,1,4),('Ncl5',0,0,5),('Ncl6','channel',3,6)]:field(e,k,v,rank,typ,ptr)
d['tables'][1].append(e);(O/'war3map.w3a').write_bytes(objdata.dump(d))

u=objdata.load(str(O/'war3map.w3u'));assert objdata.dump(u)==original['war3map.w3u']
assert not any(e['newId']=='HLx1' for t in u['tables'] for e in t)
e=dict(oldId='Hblm',newId='HLx1',flags=1,extra=0,mods=[])
for k,v in [('unam','Lux (Spell Test)'),('upro','Lux'),('uhab',''),('uabi','AInv,ALxR'),('umdl','units\\human\\Sorceress\\Sorceress.mdl'),('uico','ReplaceableTextures\\CommandButtons\\BTNSorceress.blp'),('ussi','ReplaceableTextures\\CommandButtons\\BTNSorceress.blp'),('usnd','Sorceress'),('upgr',''),('urac','human'),('ua1m','Abilities\\Weapons\\PriestMissile\\PriestMissile.mdl'),('utub','Final Spark test caster. Type -lux, -lux2, or -lux3 in Debug or solo play.')]:field(e,k,v,lev=False)
for k,v in [('ufoo',0),('umpm',1500),('umpi',1500),('uhpm',1200),('umvs',300),('upru',1),('ustr',18),('uagi',16),('uint',20)]:field(e,k,v,typ=0,lev=False)
for k,v in [('umpr',8.),('ustp',1.5),('uagp',1.5),('uinp',3.)]:field(e,k,v,typ=1,lev=False)
field(e,'upra','INT',lev=False)
field(e,'usca',1.15,typ=1,lev=False)
u['tables'][1].append(e);(O/'war3map.w3u').write_bytes(objdata.dump(u))

wts=original['war3map.wts'].decode('utf-8-sig')
for n,text in {1:'Footmen Frenzy 799X v70 - Lux Final Spark',997:'799X v70 - Lux Laser Test',998:'Spell test - October 30, 2026',999:'v68 baseline plus Final Spark. Debug or solo: -lux, -lux2, -lux3. V casts a charged long-range laser. All prior heroes and gameplay retained.'}.items():
    wts,count=re.subn(r'(STRING '+str(n)+r'\s*\{).*?(\})',lambda m:m[1]+'\n'+text+'\n'+m[2],wts,flags=re.S);assert count==1
(O/'war3map.wts').write_text(wts,encoding='utf8')
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\n\nv70 Lux Final Spark test: ALxR; standalone LX_ module in FF_Runtime and synchronized WCT globals. HLx1 is an extra test caster, outside draft/taverns. Debug/solo -lux/-lux2/-lux3. Charge 1 sec, 3400 range, 200 width, 400/650/900 + INT magic damage, 100/150/200 mana, 70/60/50 sec cooldown. PauseUnitEx lock is released once. New procedural models/textures/sounds in Spells\\Lux. Compiler and mocked-native checks required; engine playtest pending.\n')

# Two self-authored mono PCM sounds: rising charge and a short harmonic blast.
sounddir=O/'Spells/Lux';sounddir.mkdir(parents=True,exist_ok=True)
rate=22050;rng=random.Random(731)
for name,duration in [('FinalSparkCharge',1.0),('FinalSparkBlast',0.65)]:
    samples=array.array('h');phase=0.;filtered=0.
    for i in range(round(rate*duration)):
        t=i/rate;q=t/duration
        if 'Charge' in name:
            phase+=2*math.pi*(230+630*q*q)/rate
            envelope=(.1+.9*q*q)*min(1,t/.03)*min(1,(duration-t)/.025)
            value=(math.sin(phase)*.42+math.sin(phase*2.003)*.17+math.sin(phase*4.01)*.08)*envelope
        else:
            phase+=2*math.pi*(145+850*math.exp(-t*15))/rate
            filtered=.65*filtered+.35*(rng.random()*2-1)
            envelope=min(1,t/.004)*math.exp(-t*6)*min(1,(duration-t)/.08)
            value=(filtered*.65+math.sin(phase)*.48+math.sin(phase*2.01)*.15)*envelope
        samples.append(round(max(-.95,min(.95,value))*26000))
    with wave.open(str(sounddir/(name+'.wav')),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(samples.tobytes())

# Import table retains every original byte and adds exact full paths.
imp=original['war3map.imp'];version,count=struct.unpack_from('<II',imp)
added=['Spells\\Lux\\'+n for n in ['FinalSparkBeam.mdx','FinalSparkBeam.blp','FinalSparkFlare.mdx','FinalSparkFlare.blp','FinalSparkCharge.wav','FinalSparkBlast.wav']]
assert all(n.encode()+b'\0' not in imp for n in added)
(O/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(added))+imp[8:]+b''.join(b'\r'+n.encode()+b'\0' for n in added))
(R/'changes.json').write_text(json.dumps({'base':str(BASE),'changed_functions':changed,'new_functions':sorted(functions(module)),'spell':'ALxR','test_hero':'HLx1','runtime_editor_synchronized':True,'imports':added},indent=2))
print('Prepared runtime, editor source, additive object records, import manifest, and positional audio.')
