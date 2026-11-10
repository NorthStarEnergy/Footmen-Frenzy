"""Scoped hero migration from the frozen v25 release to Solo and Mini."""
from pathlib import Path
import sys,re,io,json,copy,struct,hashlib
R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'799x-backport/tools'),str(W/'mini-foots/tools')]
from mpyq import MPQArchive
import objdata
def archive(path):
 data=path.read_bytes();return MPQArchive(io.BytesIO(data[512:] if data[:4]==b'HM3W' else data),listfile=False)
DONOR=W/'799x-backport/release/FF799X_Rx_WC3Icons_v25.w3x'
da=archive(DONOR);D=R/'donor/base';ds=(D/'war3map.j').read_text(encoding='utf-8-sig')
pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def functions(s):return {m[1]:m[0] for m in re.finditer(pat,s,re.M|re.S)}
df=functions(ds)
def globals_of(s):
 block=s[:re.search(r'^endglobals',s,re.M).start()]
 result={}
 for line in block.splitlines():
  m=re.match(r'^[ \t]*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)\s*(?:=.*)?$',line.split('//')[0])
  if m:result[m[1]]=line
 return result
dg=globals_of(ds)
def key(e):return e['newId'] if e['newId']!='\0'*4 else e['oldId']
sources={ext:objdata.load(str(D/('war3map.'+ext))) for ext in ['w3u','w3a','w3h']}
di={key(e):(ext,i,e) for ext,data in sources.items() for i,t in enumerate(data['tables']) for e in t}
strings={int(m[1]):m[2] for m in re.finditer(r'STRING (\d+)\s*\{\s*\n(.*?)\n\}',(D/'war3map.wts').read_text(encoding='utf-8-sig'),re.S)}
configs={'mini':(R/'mini/base-v8.w3x','Mini Foots v9','Mini Foots v8'), 'solo':(R/'solo/base-v1.w3x','Solo Foots 6 Player FFA v2','Solo Foots 6 Player FFA v1')}
for variant,(base,title,oldtitle) in configs.items():
 B=R/variant/'base';O=R/variant/'src';O.mkdir(parents=True,exist_ok=True)
 ba=archive(base);original=(B/'war3map.j').read_text(encoding='utf-8-sig');s=original;sf=functions(s);sg=globals_of(s)
 selected={n for n in df if n.startswith(('OM_','FS_','GD_','GDV_','GDB_','GFW_','GFB_','GTW_')) or 'Guardian_Force_Field' in n or n in ['FF_HeroTooltips_Init','Trig_HERO_Guardian_Purification_Nova_Actions','Trig_HERO_Guardian_Purification_Nova_Explode_Actions']}
 # Mini already has the complete lantern runtime; Solo needs just Dark Passage.
 selected|={n for n in df if n.startswith('TFP_FFDP_') or n=='TFP_InitTrig_FFDP_DarkPassage'}
 while True:
  text='\n'.join(df[n] for n in selected)
  extra={word for word in re.findall(r'\b\w+\b',text) if word in df and word not in sf}-selected
  if not extra:break
  selected|=extra
 body='\n\n'.join(df[n] for n in df if n in selected)
 needglobals={word for word in re.findall(r'\b\w+\b',body) if word in dg}
 while True:
  extra={word for n in needglobals for word in re.findall(r'\b\w+\b',dg[n]) if word in dg}-needglobals
  if not extra:break
  needglobals|=extra
 for n in needglobals & sg.keys():
  if n.startswith(('OM_','FS_','GD_','GDV_','GDB_','GFW_','GFB_','GTW_','TFP_FFDP_')):s=s.replace(sg[n],dg[n],1)
 addedglobals=[dg[n] for n in dg if n in needglobals and n not in sg]
 s=re.sub(r'^endglobals',lambda m:'\n'.join(addedglobals)+'\nendglobals',s,count=1,flags=re.M)
 # Replace/import hero bodies, then dependency-order functions without changing any unrelated body.
 for n in selected & sf.keys():s=s.replace(sf[n],df[n],1)
 missing='\n\n'.join(df[n] for n in df if n in selected and n not in sf)
 pos=re.search(r'^function main\b',s,re.M).start();s=s[:pos]+missing+'\n\n'+s[pos:]
 if variant=='solo':
  init='\n'.join('    call '+n+'()' for n in ['OM_Init','FS_Init','GD_Init','GTW_Init','TFP_InitTrig_FFDP_DarkPassage'])
  s=s.replace('    call SF_Initialize()',init+'\n    call SF_Initialize()',1)
  s=s.replace('set udg_total_hero_count=91','set udg_total_hero_count=93')
  # The six-player tavern supports eleven categories; place the two new heroes in its first category.
  rows=[x for x in ds.splitlines() if re.match(r'\s*set udg_hero_\w+\[(92|93)\]=',x)]
  rows=[re.sub(r'(udg_hero_category\[\d+\]=)15',r'\g<1>1',x) for x in rows]
  stats=functions(s)['Trig_set_hero_stats_Actions'];s=s.replace(stats,stats.replace('endfunction','\n'.join(rows)+'\nendfunction'))
 # Update Guardian/Orianna balance rows and make Guardian available under each recipient's policy.
 for idx in [72,92]:
  for line in re.findall(r'^.*set udg_hero_\w+\['+str(idx)+r'\]=.*$',ds,re.M):
   field=re.search(r'udg_hero_\w+',line)[0]
   if field=='udg_hero_type' or (variant=='solo' and field=='udg_hero_category' and idx==92):continue
   s=re.sub(r'^.*set '+field+r'\['+str(idx)+r'\]=.*$',lambda m:line,s,flags=re.M)
 if variant=='mini':
  s=s.replace(" or id == 'H043'",'').replace("id == 'H043' or ",'')
  s=re.sub(r"^.*call SetPlayerTechMaxAllowed\(Player\(i\), 'H043', 0\)\s*\n",'',s,flags=re.M)
 # Preserve level-cap and rank progression rules; no balance redesign is bundled into this port.
 s=s.replace(oldtitle,title).replace('Solo Foots v1.8 - 6 Player FFA v1','Solo Foots v1.8 - 6 Player FFA v2')
 # Stable dependency ordering: retain original bodies verbatim, move declarations before callers as required by JASS.
 ff=functions(s);done=set();active=set();ordered=[]
 def visit(n):
  if n in done:return
  if n in active:raise AssertionError('Recursive dependency '+n)
  active.add(n)
  clean=re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*','',ff[n])
  refs=set(re.findall(r'\b(\w+)\s*\(',clean))|set(re.findall(r'\bfunction\s+(\w+)',clean))
  for dep in ff:
   if dep!=n and dep in refs:visit(dep)
  active.remove(n);done.add(n);ordered.append(ff[n])
 for n in ff:visit(n)
 first=re.search(pat,s,re.M|re.S).start();last=list(re.finditer(pat,s,re.M|re.S))[-1].end()
 s=s[:first]+'\n\n'.join(ordered)+s[last:]
 (O/'war3map.j').write_text(s,encoding='utf8')
 data={ext:objdata.load(str(B/('war3map.'+ext))) for ext in sources}
 ti={key(e):e for v in data.values() for t in v['tables'] for e in t}
 ids={'H043','HOr1','HGr1','hor1','hor2','hor3','hgr1','A0DL','AFg1','AZd1','AZd2','AFFD','ATfd','AGbs','AGbn','BGbs','BGbn'}
 ids|={k for k in di if k.startswith(('AOz','AGr','AGf','BOr','BGr','GF0')) or k=='GFbf'}
 ids|={k for k in re.findall(r"'(.{4})'",body+'\n'.join(dg[n] for n in needglobals)) if k in di and k not in ti}
 while True:
  refs=set()
  for k in ids:
   if k not in di:continue
   for m in di[k][2]['mods']:
    if isinstance(m['value'],str):refs.update(m['value'].split(','))
  extra={k for k in refs if k in di and k not in ti}-ids
  if not extra:break
  ids|=extra
 assets=set();copied={}
 for k in sorted(ids):
  if k not in di:continue
  ext,index,entry=di[k];e=copy.deepcopy(entry)
  for m in e['mods']:
   if isinstance(m['value'],str):
    m['value']=re.sub(r'TRIGSTR_(\d+)',lambda q:strings[int(q[1])],m['value'])
    assets.update(re.findall(r'[^,\n|]+\.(?:mdx|mdl|blp|wav)',m['value'],re.I))
  data[ext]['tables'][index]=[old for old in data[ext]['tables'][index] if key(old)!=k]+[e]
  copied[k]=ext
 for ext,v in data.items():(O/('war3map.'+ext)).write_bytes(objdata.dump(v))
 # Merge hero skin records rather than importing a map-wide skin table.
 skinfile=B/'war3mapSkin.w3u'
 skin=objdata.load(str(skinfile)) if skinfile.exists() else {'version':3,'v3':True,'levelled':False,'tables':[[],[]]}
 dskin=objdata.load(str(D/'war3mapSkin.w3u'))
 for i,t in enumerate(dskin['tables']):
  for e in t:
   if key(e) in {'H043','HOr1','HGr1'}:
    skin['tables'][i]=[old for old in skin['tables'][i] if key(old)!=key(e)]+[copy.deepcopy(e)]
 if skinfile.exists() or any(skin['tables']):(O/'war3mapSkin.w3u').write_bytes(objdata.dump(skin))
 assets.update(x.replace('\\\\','\\') for x in re.findall(r'"([^"\n]+\.(?:mdx|mdl|wav|blp))"',body+'\n'.join(dg[n] for n in needglobals),re.I))
 # All 12 active and disabled button pairs plus the presentation model/audio bundle.
 for f in (W/'799x-backport/src').rglob('*'):
  if f.is_file() and f.suffix.lower() in ['.mdx','.blp','.wav']:
   assets.add(str(f.relative_to(W/'799x-backport/src')).replace('/','\\'))
 # Lantern's custom lightning row is a separate data dependency, not a model.
 lightning='Splats\\LightningData.slk'
 dl=da.read_file(lightning).decode()
 tl=ba.read_file(lightning).decode() if ba.get_hash_table_entry(lightning) else dl[:dl.index('C;X1;Y2;')]+ 'E\n'
 row=re.search(r'C;X1;Y\d+;K"TFLN".*?(?=\nC;X1;Y|\nE)',dl,re.S)[0]
 existing=re.search(r'C;X1;Y\d+;K"TFLN".*?(?=\nC;X1;Y|\nE)',tl,re.S)
 if existing:tl=tl.replace(existing[0],row.replace(re.search(r'Y\d+',row)[0],re.search(r'Y\d+',existing[0])[0],1))
 else:
  last=max(map(int,re.findall(r';Y(\d+)',tl)))+1
  tl=re.sub(r'(B;X\d+;Y)\d+',lambda m:m[1]+str(last),tl)
  tl=re.sub(r'^E\s*$',lambda m:re.sub(r'Y\d+', 'Y'+str(last),row,count=1)+'\nE',tl,flags=re.M)
 if not ba.get_hash_table_entry(lightning) or tl.encode()!=ba.read_file(lightning):
  (O/'Splats').mkdir(exist_ok=True);(O/lightning).write_bytes(tl.encode())
 assets.add('Spells\\TwistedFate\\Chains.blp')
 packaged=set();checked=set()
 while assets:
  path=assets.pop().strip();path=path.replace('\\\\','\\')
  if path.lower() in checked:continue
  checked.add(path.lower())
  if not da.get_hash_table_entry(path) and path.lower().endswith('.mdl'):path=path[:-4]+'.mdx'
  if not da.get_hash_table_entry(path):continue # Native game asset.
  raw=da.read_file(path);out=O/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);packaged.add(path)
  if raw[:4]==b'MDLX':
   at=4
   while at<len(raw):
    tag=raw[at:at+4];size=struct.unpack_from('<I',raw,at+4)[0]
    if tag==b'TEXS':
     for p in range(at+8,at+8+size,268):
      tex=raw[p+4:p+264].split(b'\0')[0].decode()
      if tex:assets.add(tex)
    at+=8+size
 imp=(B/'war3map.imp').read_bytes();ver,count=struct.unpack_from('<ii',imp);at=8;registered=set()
 for _ in range(count):end=imp.index(0,at+1);registered.add(imp[at+1:end].decode().lower());at=end+1
 new=sorted(p for p in packaged if p.lower() not in registered)
 (O/'war3map.imp').write_bytes(struct.pack('<ii',ver,count+len(new))+imp[8:]+b''.join(b'\r'+p.encode()+b'\0' for p in new))
 for name in ['war3map.wts','war3map.w3i']:
  raw=(B/name).read_bytes().replace(oldtitle.encode(),title.encode()).replace(b'Solo Foots v1.8 - 6 Player FFA v1',b'Solo Foots v1.8 - 6 Player FFA v2');(O/name).write_bytes(raw)
 finalfuncs=functions(s)
 report=dict(base=str(base),title=title,donor=str(DONOR),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),donor_sha256=hashlib.sha256(DONOR.read_bytes()).hexdigest(),hero_functions=sorted(selected),objects=copied,added_globals=sorted(needglobals-sg.keys()),changed_functions=sorted(n for n in sf if sf[n]!=finalfuncs[n]),added_functions=sorted(finalfuncs.keys()-sf.keys()))
 (R/variant/'migration.json').write_text(json.dumps(report,indent=2))
 print(variant,len(selected),'hero functions,',len(copied),'objects,',len(packaged),'assets;',len(report['changed_functions']),'changed functions')
