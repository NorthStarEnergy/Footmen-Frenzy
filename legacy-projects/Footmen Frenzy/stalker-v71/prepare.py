from pathlib import Path
import sys,re,struct,json
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
BASE=W/'lux-final-spark/release/FF799X_Rx_Lux_FinalSpark_v70.w3x'
O=R/'src';O.mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(BASE),0,0x100,c.byref(h))
names=['war3map.j','war3map.wct','war3map.w3a','war3map.w3u','war3map.wts','war3map.imp','FF_MAINTENANCE.md']
original={n:read_storm(h,n) for n in names};assert storm.SFileCloseArchive(h)
module=(R/'stalker.j').read_text();decl=(R/'globals.j').read_text();anchor='function InitTrig_FF_Runtime takes nothing returns nothing'
def patch(s):
    s=s.replace('\r','');assert 'function ST_Init ' not in s
    f=functions(s)['InitTrig_FF_Runtime']
    s=s.replace(f,f.replace('\nendfunction','\n    call ST_Init()\nendfunction'),1)
    assert s.count(anchor)==1
    return s.replace(anchor,module+'\n'+anchor,1)
runtime=patch(original['war3map.j'].decode('utf-8-sig')).replace('\nendglobals','\n'+decl+'\nendglobals',1)
(O/'war3map.j').write_text(runtime,encoding='utf8')
w=original['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[];counts=[0,0]
while p<len(w):
    n=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+n];p+=n
    t=b.rstrip(b'\0').decode('utf-8-sig').replace('\r','');edited=False
    if anchor in t:t=patch(t);counts[0]+=1;edited=True
    if re.search(r'^globals\b',t,re.M):t=t.replace('\nendglobals','\n'+decl+'\nendglobals',1);counts[1]+=1;edited=True
    chunks.append(t.encode('utf8')+(b'\0' if b.endswith(b'\0') else b'') if edited else b)
assert p==len(w) and counts==[1,1]
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(b.rstrip(b'\0').decode('utf8').replace('\r','') for b in chunks)
efs=functions(editor);rfs=functions(runtime)
for name in list(functions(module))+['InitTrig_FF_Runtime']:assert efs[name]==rfs[name],name
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1]
packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
gnames=lambda s:set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',s,re.M))
source_names=gnames(header);extras=[]
for line in packed.splitlines():
    m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
    if m and m[1] not in source_names and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:efs.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')
def field(e,key,val,level=0,typ=None,ptr=0,lev=True):
    if typ is None:typ=3 if isinstance(val,str) else 0 if isinstance(val,int) else 1
    m=dict(id=key,type=typ,value=val,end=e['newId'].encode().hex())
    if lev:m.update(level=level,ptr=ptr)
    e['mods'].append(m)
def entry(old,new):return dict(oldId=old,newId=new,flags=1,extra=0,mods=[])
for n in ['war3map.w3a','war3map.w3u']:(O/n).write_bytes(original[n]);(R/('base-'+n)).write_bytes(original[n])
a=objdata.load(str(O/'war3map.w3a'));assert objdata.dump(a)==original['war3map.w3a']
assert not any(e['newId'] in ['AStB','AStS'] for t in a['tables'] for e in t)
e=entry('ANcl','AStB')
for k,v in dict(anam='Blink',ahky='B',aart='ReplaceableTextures\\CommandButtons\\BTNBlink.blp',aani='stand',atat='',acat='',aeat='',arac='',areq='',alev=1,aher=0,aite=0,abpx=0,abpy=2).items():field(e,k,v)
for k,v in dict(atp1='Blink [|cffffcc00B|r]',aub1='Teleport selected, nearby owned Stalkers together, preserving their formation where possible.|n|nRange: 800. Cooldown: 7 seconds per unit. Requires visible, walkable landing space. Blocked units stay behind without spending cooldown. Other players, unselected Stalkers, disabled units and units already cooling down are excluded. No mana cost.',acdn=7.0,aran=99999.0,aare=0.0,acas=0.0,adur=0.0,ahdu=0.0,amcs=0,atar='').items():field(e,k,v,1)
for k,v,ptr in [('Ncl1',0.0,1),('Ncl2',2,2),('Ncl3',17,3),('Ncl4',0.0,4),('Ncl5',0,5),('Ncl6','blink',6)]:field(e,k,v,1,ptr=ptr)
a['tables'][1].append(e)
e=entry('Agyb','AStS')
for k,v in dict(anam='Protoss Shields',aart='ReplaceableTextures\\CommandButtons\\BTNDefend.blp',aher=0,aite=0,alev=1,abpx=1,abpy=2).items():field(e,k,v)
for k,v in dict(atp1='Protoss Shields',aub1='The blue mana bar represents 80 shields. Shields absorb incoming damage before health and regenerate 2 points per second after 7 seconds without taking damage.|n|nParticle Disruptor: 13 damage (+5 against Warcraft heavy/fortified armor), ground and air. Mechanical, Armored.').items():field(e,k,v,1)
a['tables'][1].append(e);(O/'war3map.w3a').write_bytes(objdata.dump(a))
u=objdata.load(str(O/'war3map.w3u'));assert objdata.dump(u)==original['war3map.w3u'];assert not any(e['newId']=='nStk' for t in u['tables'] for e in t)
e=entry('hfoo','nStk')
values=dict(unam='Stalker',utip='Train Stalker',utub='Agile Protoss ranged walker. Attacks ground and air with its central particle disruptor. B Blinks the selected squad. The blue bar is shields. Model by Fingolfin (Hive Workshop).',uabi='AStB,AStS',uhab='',umdl='Units\\Stalker\\Stalker.mdl',uico='ReplaceableTextures\\CommandButtons\\BTNFacelessOne.blp',ussi='ReplaceableTextures\\CommandButtons\\BTNFacelessOne.blp',usnd='CryptFiend',urac='creeps',utyp='mechanical',utar='ground',upgr='',ureq='',uhrt='none',umvt='foot',ua1m='Units\\Stalker\\Disruptor.mdl',ua1t='chaos',ua1w='missile',ua1g='ground,air,structure,debris,ward,item',udty='large',ufoo=2,ugol=125,ulum=50,ubld=30,uhpm=80,uhpr=0.0,umpm=80,umpi=80,umpr=0.0,udef=1,umvs=300,umvr=0.8,ucol=32.0,usca=1.0,ussc=1.2,uaen=1,ua1b=12,ua1d=1,ua1s=1,ua1c=1.34,ua1r=600,ua1z=1800,uma1=0.0,umh1=1,uacq=650.0,udp1=0.1,ubs1=0.3,ucpt=0.0,ucbs=0.0,ulpx=0.0,ulpy=12.0,ulpz=69.0,uimz=50.0,udea=0,udtm=5.7,ubba=25,ufle=0)
for k,v in values.items():field(e,k,v,lev=False)
for mod in e['mods']:
    if mod['id'] in ['uico','ussi']:mod['value']='Units\\Stalker\\BTNStalker.blp'
field(e,'ucs1','',lev=False)
u['tables'][1].append(e);(O/'war3map.w3u').write_bytes(objdata.dump(u))
wts=original['war3map.wts'].decode('utf-8-sig')
for n,t in {1:'Footmen Frenzy 799X v71 - Stalker Test',997:'799X v71 - Stalker',998:'Stalker prototype - October 30, 2026',999:'v70 plus Stalker test squad. Debug or solo: -stalkers. B casts formation Blink. Shields and central plasma attack. Existing heroes and Lux retained.'}.items():
    wts,nm=re.subn(r'(STRING '+str(n)+r'\s*\{).*?(\})',lambda m:m[1]+'\n'+t+'\n'+m[2],wts,flags=re.S);assert nm==1
(O/'war3map.wts').write_text(wts,encoding='utf8')
credit='\n\nv71 Stalker test: nStk, AStB, AStS. Model Stalker by Fingolfin, https://www.hiveworkshop.com/threads/stalker.171022/ ; custom mesh/texture used with required author credit. Adaptation adds attachment points, repairs bounds, repaths texture and removes unfinished Spell sequence. ST_ module preserves selected-unit formation Blink with per-unit cooldown, pathability/visibility/collision checks, shields on mana bar, +5 vs heavy/fortified. Debug/solo -stalkers summons eight test units. Not added to production roster. WC3 movement/combat/armor scale is an adaptation. Original SC2 audio and icons are not included. Engine playtest pending.\n'
(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+credit.encode())
added=['Units\\Stalker\\'+n for n in ['Stalker.mdx','Stalker.blp','Disruptor.mdx','Plasma.blp','BTNStalker.blp']]+['ReplaceableTextures\\CommandButtonsDisabled\\DISBTNStalker.blp']
imp=original['war3map.imp'];version,count=struct.unpack_from('<II',imp)
assert all(n.encode()+b'\0' not in imp for n in added)
(O/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(added))+imp[8:]+b''.join(b'\r'+n.encode()+b'\0' for n in added))
(R/'changes.json').write_text(json.dumps(dict(base=str(BASE),changed_functions=['InitTrig_FF_Runtime'],new_functions=sorted(functions(module)),unit='nStk',abilities=['AStB','AStS'],runtime_editor_synchronized=True,imports=added),indent=2))
print('Prepared additive Stalker integration on v70; original records and editor source retained.')
