from pathlib import Path
import sys,struct,math,re,json,copy,ctypes as c,shutil,subprocess,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive
B=R/'base';O=R/'src';archive.extract(R/'baseline.w3x',B)
donorroot=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy')
D=R/'donor';archive.extract(donorroot/'hero-polish/release/Solo Foots 6 Player FFA v3.w3x',D)
s=(B/'war3map.j').read_text();ds=(D/'war3map.j').read_text()
pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
def put(n,t):
 global s
 s=s.replace(funcs(s)[n],t)
report={}
# Reuse the complete, previously packaged hero migration, with its polished assets.
migration=json.loads((donorroot/'hero-sync/solo/migration.json').read_text())
polish=json.loads((donorroot/'hero-polish/solo/changes.json').read_text())
selected=set(migration['hero_functions'])|set(polish['added_functions'])
df=funcs(ds);sf=funcs(s)
def globals_of(t):
 result={}
 for line in t[t.index('globals')+7:re.search(r'^endglobals',t,re.M).start()].splitlines():
  m=re.match(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)\s*(?:=.*)?$',line.split('//')[0])
  if m:result[m[1]]=line
 return result
dg=globals_of(ds);sg=globals_of(s)
body='\n'.join(df[n] for n in selected)
needed=set(re.findall(r'\b\w+\b',body))&dg.keys()
while True:
 extra=set(re.findall(r'\b\w+\b','\n'.join(dg[n] for n in needed)))&dg.keys()-needed
 if not extra:break
 needed|=extra
for n in needed&sg.keys():
 if n.startswith(('OM_','FS_','GD_','GDV_','GDB_','GFW_','GFB_','GTW_','TFP_FFDP_')):s=s.replace(sg[n],dg[n],1)
s=re.sub(r'^endglobals',lambda m:'\n'.join(dg[n] for n in dg if n in needed and n not in sg)+'\nendglobals',s,count=1,flags=re.M)
for n in selected&sf.keys():put(n,df[n])
s+='\n\n'+'\n\n'.join(df[n] for n in df if n in selected and n not in sf)+'\n'
for name in ['Trig_set_hero_numbers_Actions','Trig_set_hero_stats_Actions']:
 # These donor functions contain only hero roster/stat initialization.
 put(name,df[name])
main=funcs(s)['main'];main=main.replace('    call SF_Initialize()', '\n'.join('    call '+n+'()' for n in ['OM_Init','FS_Init','GD_Init','GTW_Init','TFP_InitTrig_FFDP_DarkPassage'])+'\n    call SF_Initialize()');put('main',main)
ids=set(migration['objects'])
for filename,levels in [('war3map.w3u',False),('war3map.w3a',True),('war3map.w3h',False),('war3mapSkin.w3u',False)]:
 target=Obj(B/filename,levels);donor=Obj(D/filename,levels)
 for i,table in enumerate(donor.tables):
  for record in table:
   key=(record['new'] if record['new']!=bytes(4) else record['old']).decode()
   if key in ids:
    for t in target.tables:t[:]=[r for r in t if (r['new'] if r['new']!=bytes(4) else r['old']).decode()!=key]
    target.tables[i].append(copy.deepcopy(record))
 if filename=='war3map.w3u':
  # Give the tavern the same proven Spirit Lodge artwork as the visible recipe shop.
  tav=target.find('nFHT');tav['old']=b'nmrk'
  for key,val in {'umdl':r'buildings\orc\SpiritLodge\SpiritLodge.mdl','usca':0.75,'uclr':255,'uclg':255,'uclb':255,'ubdg':1,'uabi':'Asud,Avul','useu':'','unam':'Hero Tavern','upat':'','ucol':0.0}.items():target.set('nFHT',key,val)
 if filename=='war3mapSkin.w3u':
  for key,val in {'umdl':r'buildings\orc\SpiritLodge\SpiritLodge.mdl','usca':0.75,'uclr':255,'uclg':255,'uclb':255}.items():target.set('nFHT',key,val)
 target.save(O/filename)
# Copy packaged hero resources (excluding all layout and script files).
for folder in [donorroot/'hero-sync/solo/src',donorroot/'hero-polish/solo/src']:
 for p in folder.rglob('*'):
  if p.is_file() and not p.name.startswith('war3map'):
   rel=p.relative_to(folder);out=O/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out)
shutil.copyfile(D/'war3map.imp',O/'war3map.imp')

# Shared radial layout transformation: compact center, fixed outer walls.
def radius(r):
 if r<=2600:return r*.85
 if r<3600:return r-390*(3600-r)/1000
 return r
def inverse(r):
 if r<=2210:return r/.85
 if r<3600:return (r+1404)/1.39
 return r
def transform(x,y):
 r=math.hypot(x,y+256);q=radius(r)/r if r else 1
 return x*q,-256+(y+256)*q
terrain=(B/'war3map.w3e').read_bytes();N=81;ox=-5120;oy=-5376
def tile(x,y):
 i=max(0,min(80,round((x-ox)/128)));j=max(0,min(80,round((y-oy)/128)))
 return bytearray(terrain[85+(j*N+i)*8:85+(j*N+i+1)*8])
ground=tile(0,-256);raw=bytearray(terrain[:85]);levels=[]
for j in range(N):
 for i in range(N):
  x=ox+i*128;y=oy+j*128;r=math.hypot(x,y+256);q=inverse(r)/r if r else 1
  t=tile(x*q,-256+(y+256)*q)
  # Trim the innermost cliff tips by roughly one terrain cell.
  if r<2220 and (t[7]&15)>9:t=bytearray(ground)
  level=t[7]&15
  if level==9 and r>2220+64*math.sin(math.atan2(y+256,x)*24):
   flags=struct.unpack_from('<H',t,4)[0];struct.pack_into('<H',t,4,(flags&~63)|7)
  raw.extend(t);levels.append(level)
(O/'war3map.w3e').write_bytes(raw)
# Pathing follows the resampled terrain; keep special original restrictions outside the trimmed tips.
pb=(B/'war3map.wpm').read_bytes();pw,ph=struct.unpack_from('<II',pb,8);path=bytearray(pb[:16])
for j in range(ph):
 for i in range(pw):
  x=ox+(i+.5)*32;y=oy+(j+.5)*32;r=math.hypot(x,y+256);q=inverse(r)/r if r else 1
  u=int((x*q-ox)/32);v=int((-256+(y+256)*q-oy)/32)
  value=pb[16+v*pw+u] if 0<=u<pw and 0<=v<ph else 254
  ti=i//4;tj=j//4;ls=[levels[(tj+dy)*N+ti+dx] for dx,dy in [(0,0),(1,0),(0,1),(1,1)]]
  if r<2220 and max(ls)==9:value=0
  if max(ls)!=min(ls):value|=2
  path.append(value)
(O/'war3map.wpm').write_bytes(path);(O/'war3map.shd').write_bytes(bytes(pw*ph))
# Parse placements with the already verified modern record reader.
source=(W/'ffa-v4/build.py').read_text();exec(source[source.index('class Reader:'):source.index('shop_types=')])
ub=(B/'war3mapUnits.doo').read_bytes();units=placements(ub)
starts={u['owner']:(u['x'],u['y']) for u in units if u['kind']=='sloc'}
def walkable(x,y,clearance=32):
 for dx,dy in [(0,0),(clearance,0),(-clearance,0),(0,clearance),(0,-clearance)]:
  i=int((x+dx-ox)/32);j=int((y+dy-oy)/32)
  if not (0<=i<pw and 0<=j<ph) or path[16+j*pw+i]&2:return False
 return True
newstarts={};changes=[];records=[]
for u in units:
 x,y=u['x'],u['y'];a=math.atan2(y+256,x);kind=u['kind']
 if kind=='sloc':x+=96*math.cos(a);y+=96*math.sin(a);newstarts[u['owner']]=(x,y)
 elif kind=='hwtw':
  bx,by=starts[u['owner']];a=math.atan2(by+256,bx);t=-x*math.sin(a)+(y+256)*math.cos(a);side=1 if t>0 else -1
  x-=side*64*math.sin(a);y+=side*64*math.cos(a)
  assert walkable(x,y,32),('tower pathing',x,y)
 elif kind in ['n01B','n004']:
  x,y=transform(x,y)
  # Seat the shop on reachable ground beside the new cliff tip, leaving the center approach open.
  candidates=[(x+dx,y+dy) for dx in range(-192,193,32) for dy in range(-192,193,32) if walkable(x+dx,y+dy,64)]
  assert candidates,'No shop seat'
  x,y=min(candidates,key=lambda p:math.hypot(p[0]-x,p[1]-y))
 a=math.atan2(-256-y,-x) if math.hypot(x,y+256)>1 else u['angle']
 record=bytearray(ub[u['start']:u['end']]);struct.pack_into('<ff',record,8,x,y)
 if kind in ['n01B','n004']:struct.pack_into('<f',record,20,a)
 records.append(record);changes.append(dict(kind=kind,old=[u['x'],u['y']],new=[x,y],owner=u['owner']))
(O/'war3mapUnits.doo').write_bytes(ub[:16]+b''.join(records))
creation=funcs(s)['CreateAllUnits']
for ch in changes:
 if ch['old']==ch['new'] or ch['kind']=='sloc':continue
 def replace(m):
  x=float(m[2].replace(' ',''));y=float(m[3].replace(' ',''))
  if math.hypot(x-ch['old'][0],y-ch['old'][1])>.02:return m[0]
  nx,ny=ch['new'];face=math.degrees(math.atan2(-256-ny,-nx)) if ch['kind'] in ['n01B','n004'] else float(m[4].replace(' ',''))
  return m[1]+f'{nx:.3f}, {ny:.3f}, {face:.3f}'+m[5]
 creation=re.sub(r"(BlzCreateUnitWithSkin\(Player\(\d+\), '"+ch['kind']+r"', )([\d. -]+), ([\d. -]+), ([\d. -]+)(, '....'\))",replace,creation)
put('CreateAllUnits',creation)
for owner,(x,y) in newstarts.items():
 slot=[0,4,7,11,1,3,6,9].index(owner)
 s=re.sub(r'(call DefineStartLocation\(\s*'+str(slot)+r',)[^\n]+',lambda m:m[1]+f' {x:.3f}, {y:.3f} )',s)
 for axis,val in [('X',x),('Y',y)]:s=re.sub(r'(set SF_Base'+axis+r'\['+str(owner+1)+r'\]=)[^\n]+',lambda m:m[1]+f'{val:.3f}',s)
info=(B/'war3map.w3i').read_bytes()
for owner,old in starts.items():info=info.replace(struct.pack('<ff',*old),struct.pack('<ff',*newstarts[owner]))
# Move decor/pathing blockers with the terrain; remove blockers from shortened tips.
db=(B/'war3map.doo').read_bytes();reader=Reader(db);reader.o=12;count=reader.get('I');decor=[]
for _ in range(count):
 st=reader.o;kind=reader.get('4s');reader.skip(4);x,y,z=reader.get('3f');reader.skip(4+12+4+4+2+4)
 for _ in range(reader.get('I')):reader.skip(reader.get('I')*8)
 reader.skip(4+4+12);rec=bytearray(db[st:reader.o]);nx,ny=transform(x,y)
 if math.hypot(nx,ny+256)<2220:continue
 struct.pack_into('<ff',rec,8,nx,ny);decor.append(rec)
assert db[reader.o:]==bytes(8)
(O/'war3map.doo').write_bytes(db[:12]+struct.pack('<I',len(decor))+b''.join(decor)+bytes(8))
# First page: ten distinct SD categories; subsequent choices are randomized.
openfn=funcs(s)['SF_OpenTaverns'].replace('exitwhen category > 11','exitwhen category > 10')
put('SF_OpenTaverns',openfn)
assert "udg_hero_type[92]='HOr1'" in s and "udg_hero_type[93]='HGr1'" in s
title='Solo Foots 8 Player FFA v7';s=re.sub(r'call SetMapName\("[^"]+"\)',f'call SetMapName("{title}")',s)
end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
# Order declarations before their callers after importing the hero systems.
ff=funcs(s);done=set();active=set();ordered=[]
def visit(n):
 if n in done:return
 if n in active:raise AssertionError('Cycle '+n)
 active.add(n);clean=re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*','',ff[n]);refs=set(re.findall(r'\b(\w+)\s*\(',clean))|set(re.findall(r'\bfunction\s+(\w+)',clean))
 for dep in ff:
  if dep!=n and dep in refs:visit(dep)
 active.remove(n);done.add(n);ordered.append(ff[n])
for n in ff:visit(n)
s=s[:re.search(pat,s,re.M|re.S).start()]+'\n\n'.join(ordered)+'\n';(O/'war3map.j').write_text(s)
# Rebuild custom editor wrapper from the exact final runtime.
ed=s
for name in ['config','CreateRegions']:ed=ed.replace(funcs(ed)[name],'')
ed=re.sub(r'^\s*rect\s+gg_rct_\w+\s*=\s*null\s*$','',ed,flags=re.M)
ed=re.sub(r'\s*call (CreateRegions|InitBlizzard)\(\s*\)','',ed)
for name in list(funcs(ed)):
 if name in ['InitGlobals','InitSounds','CreateCameras','CreateAllUnits','InitCustomTriggers','RunInitializationTriggers','InitCustomPlayerSlots','InitCustomTeams','InitAllyPriorities','main'] or name.startswith('InitUpgrades'):ed=re.sub(r'\b'+name+r'\b','SFMap_'+name,ed)
ed=ed.replace('gg_unit_','sf_unit_').replace('gg_snd_','sf_snd_')
oldwct=(B/'war3map.wct').read_bytes();at=oldwct.index(0,4)+1;n=struct.unpack_from('<I',oldwct,at)[0];olded=oldwct[at+4:at+4+n].rstrip(b'\0').decode()
lookup=funcs(olded)['SF_FindPlacement'];ed=re.sub(r'^endglobals','    group SF_BoundPlacements=null\nendglobals',ed,count=1,flags=re.M)
ed=ed.replace('function SFMap_CreateAllUnits takes',lookup+'\nfunction SFMap_CreateAllUnits takes')
old=funcs(ed)['SFMap_CreateAllUnits'];ed=ed.replace(old,old.replace('BlzCreateUnitWithSkin','SF_FindPlacement'))
payload=ed.encode()+b'\0';(O/'war3map.wct').write_bytes(oldwct[:at]+struct.pack('<I',len(payload))+payload+oldwct[at+4+n:])
regions=sorted(set(re.findall(r'\bgg_rct_\w+\b',ed)))
wrapper='globals\n'+''.join('rect '+n+'=null\n' for n in regions)+'endglobals\n'+ed+'\nfunction main takes nothing returns nothing\ncall InitBlizzard()\ncall SFMap_main()\nendfunction\nfunction config takes nothing returns nothing\nendfunction\n'
(R/'editor-validation.j').write_text(wrapper)
# Terrain-derived BLP1 minimaps, preserving WC3-compatible encoding.
colors=[(106,91,69),(115,103,83),(80,80,79),(124,121,111),(125,124,111),(147,145,134),(66,94,38),(67,103,45),(180,179,160),(139,136,123)]
im=Image.new('RGB',(N,N))
for j in range(N):
 for i in range(N):
  t=raw[85+(j*N+i)*8:85+(j*N+i+1)*8];color=colors[(struct.unpack_from('<H',t,4)[0]&63)%10]
  if t[7]&15>9:color=tuple(int(v*.55) for v in color)
  im.putpixel((i,N-1-j),color)
mini=im.resize((256,256)).quantize(colors=256)
for name in ['war3mapMap.blp','war3mapMap_ingame.blp']:mini.save(O/name,blp_version='BLP1')
preview=im.resize((810,810));draw=ImageDraw.Draw(preview)
for u in changes:
 if u['kind'] in ['sloc','hwtw','n01B','n004']:
  x,y=u['new'];px=(x-ox)/128*10;py=(80-(y-oy)/128)*10;color='red' if u['kind']=='hwtw' else 'yellow' if u['kind']=='sloc' else 'cyan';draw.ellipse((px-4,py-4,px+4,py+4),fill=color)
preview.save(R/'layout-preview.png')
(R/'layout.json').write_text(json.dumps(changes,indent=2))
work=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work');compiler=W/'ffa-v4/tools/jasshelper'
commands=[([str(compiler/'clijasshelper.exe'),'--scriptonly','--nooptimize',str(work/'common.j'),str(work/'Blizzard.j'),str(R/'editor-validation.j'),str(R/'editor-compiled.j')],'editor-preprocess'),([str(compiler/'pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(O/'war3map.j')],'runtime'),([str(compiler/'pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(R/'editor-compiled.j')],'editor')]
for command,label in commands:
 result=subprocess.run(command,cwd=R,capture_output=True,text=True);(R/(label+'.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,(label,result.stdout[-4500:])
out=R/'release/Solo_Foots_8P_FFA_v7.w3x';shutil.copyfile(R/'baseline.w3x',out);handle=c.c_void_p();assert archive.s.SFileOpenArchive(str(out),0,0,c.byref(handle))
for file in O.rglob('*'):
 if file.is_file():assert archive.s.SFileAddFileEx(handle,str(file),str(file.relative_to(O)).replace('/','\\').encode(),0x80000200,2,2),str(file)
assert archive.s.SFileCloseArchive(handle)
data=out.read_bytes();header=b'HM3W'+bytes(4)+title.encode()+b'\0'+struct.pack('<II',196218,8);out.write_bytes(header+bytes(512-len(header))+data[512:])
names=archive.extract(out,R/'roundtrip')
for name in names:
 if name in ['(attributes)','(listfile)','(signature)']:continue
 expected=O/name if (O/name).exists() else B/name
 assert expected.read_bytes()==(R/'roundtrip'/name).read_bytes(),name
for file,levels in [('war3map.w3u',False),('war3mapSkin.w3u',False),('war3map.w3a',True),('war3map.w3h',False),('war3map.w3t',False),('war3map.w3q',True)]:Obj(R/'roundtrip'/file,levels)
report.update(output=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),verified_entries=len(names),hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,live_test='Pending')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
