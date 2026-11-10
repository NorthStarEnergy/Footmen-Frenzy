from pathlib import Path
import sys, shutil, json, hashlib, subprocess, copy
R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm, read_storm, c, functions, archive, entries, work
import objdata
base=W/'799x-backport/release/FF799X_Rx_Mundo_v32.w3x'
outdir=R/'src';outdir.mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
names=['war3map.j','war3map.w3a','war3map.w3u','war3map.wts']
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in names:(outdir/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
s=(outdir/'war3map.j').read_text(encoding='utf-8-sig');original=s
assert 'VG_Init' not in s
s=s.replace('\nendglobals','\n    hashtable VG_Hash = null\n    hashtable VG_PrevX = null\n    hashtable VG_PrevY = null\n    unit array VG_Hero\nendglobals',1)
s=s.replace('function main takes nothing returns nothing',(R/'spells.j').read_text()+'\nfunction main takes nothing returns nothing',1)
f=functions(s)['main'];s=s.replace(f,f.replace('\nendfunction','\n    call VG_Init()\nendfunction'),1)

def field(e,key,val,level=0,typ=3,ptr=0,lev=True):
 e['mods']=[m for m in e['mods'] if not(m['id']==key and m.get('level',0)==level)]
 m=dict(id=key,type=typ,value=val,end=e['newId'].encode().hex())
 if lev:m.update(level=level,ptr=ptr)
 e['mods'].append(m)

d=objdata.load(str(outdir/'war3map.w3a'));es={e['newId']:e for t in d['tables'] for e in t}
for uid,name,key,order,icon,cooldown,mana,radius,desc in [
 ('AVge','Event Horizon','E','cloudoffog','BTNStasisTrap',18.,80,300.,'Creates a circular cage for 3 seconds. Enemies touching or crossing its edge are stunned for 1.5 seconds, once per cage. Units inside can move freely. Radius: 300. Excludes buildings and magic-immune units.'),
 ('AVgw','Dark Matter','W','flamestrike','BTNDeathAndDecay',10.,100,225.,'Marks an area. After 1.25 seconds, dark matter falls from above, dealing 300 magic damage to enemies in a 225 radius. Excludes buildings and magic-immune units.')]:
 assert uid not in es
 e=dict(oldId='ANcl',newId=uid,flags=1,extra=0,mods=[])
 for k,v in [('anam',name),('ahky',key),('aart','ReplaceableTextures\\CommandButtons\\'+icon+'.blp'),('aani','spell'),('atat',''),('acat',''),('aeat',''),('atp1',name+' [|cffffcc00'+key+'|r]'),('aub1',desc+'|n|nMana: '+str(mana)+'   Cooldown: '+str(int(cooldown))+' sec')]:field(e,k,v,1 if k in ('atp1','aub1') else 0)
 for k,v in [('alev',1),('aher',0),('aite',0),('abpx',0 if key=='E' else 1),('abpy',2)]:field(e,k,v,typ=0)
 for k,v in [('acdn',cooldown),('aran',900.),('aare',radius),('adur',0.),('ahdu',0.)]:field(e,k,v,1,1)
 field(e,'amcs',mana,1,0);field(e,'atar','',1)
 for k,v,typ,ptr in [('Ncl1',0.,1,1),('Ncl2',2,0,2),('Ncl3',3,0,3),('Ncl4',0.,1,4),('Ncl5',0,0,5),('Ncl6',order,3,6)]:field(e,k,v,1,typ,ptr)
 d['tables'][1].append(e)
e=copy.deepcopy(es['AGtz']);e['newId']='AVgs';e['mods']=[m for m in e['mods'] if m.get('level',0)<=1]
for m in e['mods']:m['end']=b'AVgs'.hex()
field(e,'alev',1,typ=0);field(e,'anam','Event Horizon stun')
for k in ('adur','ahdu'):field(e,k,1.5,1,2)
field(e,'amsp',0.,typ=1);field(e,'amat','');field(e,'abuf','BPSE',1)
assert 'AVgs' not in es;d['tables'][1].append(e)
(outdir/'war3map.w3a').write_bytes(objdata.dump(d))
u=objdata.load(str(outdir/'war3map.w3u'));assert not any(e['newId']=='HVg1' for t in u['tables'] for e in t)
e=dict(oldId='Ulic',newId='HVg1',flags=1,extra=0,mods=[])
for k,v in [('unam','Veigar (Dummy Hero)'),('upro','Veigar'),('uhab',''),('uabi','AInv,AVge,AVgw'),('upgr',''),('urac','creeps'),('utub','Prototype hero with Event Horizon and Dark Matter. Type -veigar to summon or select.')]:field(e,k,v,lev=False)
for k,v in [('ufoo',0),('umpm',1000),('umpi',1000),('uhpm',1000),('umvs',300),('upru',1)]:field(e,k,v,typ=0,lev=False)
field(e,'umpr',5.,typ=1,lev=False);u['tables'][1].append(e)
(outdir/'war3map.w3u').write_bytes(objdata.dump(u))
s=s.replace('FF799X - Mundo v32','FF799X - Veigar v33');(outdir/'war3map.j').write_text(s,encoding='utf8')
p=outdir/'war3map.wts';raw=p.read_bytes();assert b'FF799X - Mundo v32' in raw;p.write_bytes(raw.replace(b'FF799X - Mundo v32',b'FF799X - Veigar v33'))
run=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(outdir/'war3map.j')],capture_output=True,text=True)
(R/'audit/compiler.log').write_text(run.stdout+run.stderr)
assert run.returncode==0,(run.stdout+run.stderr)[:5000]
release=R/'release';release.mkdir(exist_ok=True);out=release/'FF799X_Rx_Veigar_v33.w3x';shutil.copy2(base,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for name in names: assert storm.SFileAddFileEx(h,str(outdir/name),name.encode(),0x80000200,2,2),name
assert storm.SFileCloseArchive(h)
before=archive(base);after=archive(out); oldentries,newentries=entries(before),entries(after);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name in names:
 assert read_storm(h,name)==(outdir/name).read_bytes()
 e=before.get_hash_table_entry(name);skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert storm.SFileCloseArchive(h)
for name in ['(listfile)','(attributes)','(signature)']:
 e=before.get_hash_table_entry(name)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in oldentries.items():
 if k not in skip:assert newentries.get(k)==v,k
digest=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(digest+'  '+out.name+'\n')
new_functions=functions(s)
report=dict(output=str(out),sha256=digest,preserved_archive_entries=len(oldentries.keys()-skip),changed_functions=[n for n,f in functions(original).items() if new_functions[n]!=f],live_test='Pending')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))


