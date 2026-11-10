from pathlib import Path
import sys,re,json,functools,hashlib,csv
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
sys.path[:0]=[str(PROJECT/'tools'),str(PROJECT.parent/'mini-foots/tools')]
import objdata,game_data as gd
from mpyq import MPQArchive
MAP=PROJECT/'release/FF799X_Rx_Orianna_v10.w3x'
mpq=MPQArchive(str(MAP),listfile=False)
CACHE=ROOT/'game-data';CACHE.mkdir(exist_ok=True)
def archive(name):return mpq.read_file(name)
wts_text=archive('war3map.wts').decode('utf-8-sig',errors='replace')
wts=dict(re.findall(r'STRING\s+(\d+)\s*(?://[^\n]*\n)?\s*\{\s*(.*?)\s*\}',wts_text,re.S))
def resolve(v):
 if isinstance(v,str) and v.startswith('TRIGSTR_'):return wts.get(str(int(v[8:])),v)
 return v
def plain(v):return re.sub(r'\|c[0-9a-fA-F]{8}|\|r','',str(v)).replace('|n','\n').replace('|N','\n')
script=archive('war3map.j').decode('utf-8-sig')
functions={m[1]:{'text':m[0],'line':script[:m.start()].count('\n')+1} for m in re.finditer(r'^function (\w+) takes .*?^endfunction',script,re.M|re.S)}
tables={};parents={};objects={}
for kind,ext in [('item','w3t'),('unit','w3u'),('ability','w3a'),('buff','w3h')]:
 tables[kind]={};objects[kind]={}
 # Gameplay overrides take precedence if both files explicitly define a field.
 for name in [f'war3mapSkin.{ext}',f'war3map.{ext}']:
  data=archive(name)
  if not data:continue
  path=ROOT/(name.replace('war3map','extracted'));path.write_bytes(data)
  obj=objdata.load(str(path));assert objdata.dump(obj)==data
  for tab in obj['tables']:
   for e in tab:
    uid=e['newId'] if e['newId']!='\0'*4 else e['oldId'];parents[kind,uid]=e['oldId'];objects[kind][uid]=e
    for m in e['mods']:tables[kind][uid,m['id'],m.get('level',0)]=(resolve(m['value']),name)
defaults={};profiles={};profile_parts={};strings={}
files=['unitdata.slk','unitbalance.slk','unitweapons.slk','unitabilities.slk','unitui.slk','unitmetadata.slk','abilitydata.slk','abilitymetadata.slk','itemdata.slk','abilitybuffdata.slk']
files += [race+typ+'.txt' for race in ['human','orc','undead','nightelf','neutral','campaign','item','common'] for typ in ['unitfunc','unitstrings','abilityfunc','abilitystrings']]
files += ['itemfunc.txt','itemstrings.txt','unitskin.txt','itemskin.txt']
for label,prefix in [('base','war3.w3mod:'),('custom','war3.w3mod:_balance\\custom_v1.w3mod:'),('locale','war3.w3mod:_locales\\enus.w3mod:')]:
 for name in files:
  path=CACHE/(label+'-'+name)
  data=path.read_bytes() if path.exists() else gd.game_read(prefix+'units\\'+name)
  if not data:continue
  path.write_bytes(data)
  if name.endswith('.slk'):defaults[label+'-'+name]=gd.slk(data)
  else:
   section=None
   for line in data.decode('utf-8-sig',errors='replace').splitlines():
    line=line.strip()
    if line.startswith('[') and line.endswith(']'):section=line[1:-1]
    elif section and '=' in line and not line.startswith('//'):
     field,v=line.split('=',1)
     try:parts=next(csv.reader([v],skipinitialspace=True))
     except csv.Error:parts=[v.strip('"')]
     profiles[label,section,field]=(v.strip('"'),label+'-'+name)
     profile_parts[label,section,field]=parts
for name in ['ui\\worldeditstrings.txt','ui\\worldeditgamestrings.txt']:
 path=CACHE/Path(name.replace('\\','/')).name
 data=path.read_bytes() if path.exists() else gd.game_read('war3.w3mod:_locales\\enus.w3mod:'+name)
 if data:
  path.write_bytes(data)
  for fields in gd.ini(data).values():strings.update(fields)
um=defaults['base-unitmetadata.slk'];am=defaults['base-abilitymetadata.slk']
def data_slot(meta,level):
 col=meta['field']
 if col=='Data':col+='ABCDEFGHIJKLMNOPQRSTUVWXYZ'[int(meta['data'])-1]
 return (col,level if meta.get('repeat','0')!='0' else 0)
alias_overrides={}
for (uid,field,level),hit in tables['ability'].items():
 m=am.get(field)
 if m and m.get('slk')=='AbilityData':alias_overrides[uid,*data_slot(m,level)]=(hit[0],hit[1],field)
@functools.lru_cache(maxsize=10000)
def val(kind,uid,field,level=0):
 meta=(am if kind=='ability' else um).get(field)
 if kind=='ability' and meta and meta.get('slk')=='AbilityData':
  slot=alias_overrides.get((uid,*data_slot(meta,level)))
  if slot:return slot[0],slot[1]+(' (via '+slot[2]+' shared data field)' if slot[2]!=field else '')
 hit=tables[kind].get((uid,field,level))
 if hit:return hit
 parent=parents.get((kind,uid),uid)
 if not meta:return (None,'no field metadata')
 col=meta['field'];result=(None,'missing inherited field')
 if kind=='ability':
  if col=='Data':col+='ABCDEFGHIJKLMNOPQRSTUVWXYZ'[int(meta['data'])-1]
  if level>0 and meta.get('repeat','0')!='0' and meta['slk']!='Profile':col+=str(level)
 if meta['slk']=='Profile':
  for label in ['base','custom','locale']:
   if (label,parent,col) in profiles:
    v,fn=profiles[label,parent,col];idx=int(meta.get('index','-1'))
    if kind=='ability' and level>0 and meta.get('repeat','0')!='0':idx=level-1
    if idx>=0:
     parts=profile_parts[label,parent,col];v=parts[idx] if len(parts)>idx else None
    result=(v,fn+' (inherited '+parent+')')
 else:
  for label in ['base','custom']:
   fn=label+'-'+meta['slk'].lower()+'.slk';row=defaults.get(fn,{}).get(parent,{})
   if col in row:result=(row[col],fn+' (inherited '+parent+')')
 return result
def value(kind,uid,field,level=0):return val(kind,uid,field,level)[0]
def num(kind,uid,field,level=0,default=0):
 try:return float(value(kind,uid,field,level))
 except (ValueError,TypeError):return default
def name(kind,uid):return plain(value(kind,uid,'anam' if kind=='ability' else 'unam') or uid)
def abil_list(uid):return [a for a in str(value('item',uid,'iabi') or '').split(',') if len(a)==4]
def ability(uid,all_levels=False):
 parent=parents.get(('ability',uid),uid);code=defaults['base-abilitydata.slk'].get(parent,{}).get('code',parent)
 n=max(1,int(num('ability',uid,'alev',default=1)));levels=range(1,n+1) if all_levels else [1]
 explicit={k[1] for k in tables['ability'] if k[0]==uid}
 fields=[]
 for field,m in am.items():
  if m.get('category') not in ['data','stats'] and field not in ['atar','abuf','aeff','areq']:continue
  use=m.get('useSpecific','');exclude=m.get('notSpecific','')
  if use and parent not in use.split(',') and code not in use.split(',') and field not in explicit:continue
  if exclude and (parent in exclude.split(',') or code in exclude.split(',')):continue
  for lev in (levels if m.get('repeat','0')!='0' else [0]):
   v,origin=val('ability',uid,field,lev)
   if v is None or v in ('-',' - ','_',''):continue
   if isinstance(v,float):v=round(v,6)
   fields.append({'label':strings.get(m.get('displayName'),m.get('displayName',field)),'value':v,'raw':field,'level':lev,'source':origin})
 return {'id':uid,'name':name('ability',uid),'base':parent,'code':code,'levels':n,'fields':fields}
def text_references(uid):
 return [{'function':n,'line':f['line']} for n,f in functions.items() if "'"+uid+"'" in f['text']]
if __name__=='__main__':
 print('items',len(objects['item']),'strings',len(wts),'game strings',len(strings))
 print('AIcb armor',value('ability','AIcb','Iarp',1),'fields',ability('AIcb'))
