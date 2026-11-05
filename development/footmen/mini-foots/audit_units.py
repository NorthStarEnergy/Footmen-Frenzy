from pathlib import Path
import sys,re,json,csv,hashlib
R=Path(__file__).parent;sys.path.insert(0,str(R/'tools'))
import objdata,game_data as gd
O=R/'audit';O.mkdir(exist_ok=True);G=O/'game-data';G.mkdir(exist_ok=True)
B=R/'base/files';S=R/'src'
def source(name):return S/name if (S/name).exists() else B/name
s=source('war3map.j').read_text(encoding='utf-8-sig')
manifest=json.loads((R/'changes.json').read_text())
wts=dict(re.findall(r'STRING\s+(\d+)\s*\{\s*\n(.*?)\n\}',source('war3map.wts').read_text(encoding='utf-8-sig'),re.S))
def resolve(v):
 if isinstance(v,str) and v.startswith('TRIGSTR_'):return wts.get(str(int(v[8:])),v)
 return v
tables={};parents={};raw=[]
for kind,ext in [('unit','w3u'),('ability','w3a')]:
 tables[kind]={}
 for name in [f'war3map.{ext}',f'war3mapSkin.{ext}']:
  if not source(name).exists():continue
  for tab in objdata.load(str(source(name)))['tables']:
   for e in tab:
    uid=e['newId'] if e['newId']!='\0'*4 else e['oldId'];parents[kind,uid]=e['oldId']
    for m in e['mods']:
     tables[kind][uid,m['id'],m.get('level',0)]=(resolve(m['value']),name)
defaults={};profiles={};strings={}
files=['unitdata.slk','unitbalance.slk','unitweapons.slk','unitabilities.slk','unitui.slk','unitmetadata.slk','abilitydata.slk','abilitymetadata.slk']
files += [race+typ+'.txt' for race in ['human','orc','undead','nightelf','neutral','campaign','item','common'] for typ in ['unitfunc','unitstrings','abilityfunc','abilitystrings']]
for label,prefix in [('base','war3.w3mod:'),('custom','war3.w3mod:_balance\\custom_v1.w3mod:'),('locale','war3.w3mod:_locales\\enus.w3mod:')]:
 for name in files:
  cache=G/(label+'-'+name)
  data=(cache.read_bytes() if cache.exists() else None) if '--cached' in sys.argv else gd.game_read(prefix+'units\\'+name)
  if not data:continue
  fn=label+'-'+name;(G/fn).write_bytes(data)
  if name.endswith('.slk'):defaults[fn]=gd.slk(data)
  else:
   for uid,fields in gd.ini(data).items():
    for field,value in fields.items():profiles[label,uid,field]=(value,fn)
for name in ['ui\\worldeditstrings.txt','ui\\worldeditgamestrings.txt']:
 cache=G/Path(name.replace('\\','/')).name
 data=(cache.read_bytes() if cache.exists() else None) if '--cached' in sys.argv else (gd.game_read('war3.w3mod:_locales\\enus.w3mod:'+name) or gd.game_read('war3.w3mod:'+name))
 if data:
  (G/Path(name.replace('\\','/')).name).write_bytes(data)
  for fields in gd.ini(data).values():strings.update(fields)
um=defaults['base-unitmetadata.slk'];am=defaults['base-abilitymetadata.slk']
def val(kind,uid,field,level=0):
 hit=tables[kind].get((uid,field,level))
 if hit:return hit
 parent=parents.get((kind,uid),uid);meta=(um if kind=='unit' else am).get(field)
 if not meta:return ('unresolved','no field metadata')
 col=meta['field'];result=('unresolved','missing inherited field')
 if kind=='ability':
  if col=='Data':col+='ABCDEFGHIJKLMNOPQRSTUVWXYZ'[int(meta['data'])-1]
  if level>0 and meta.get('repeat','0')!='0' and meta['slk']!='Profile':col+=str(level)
 if meta['slk']=='Profile':
  for label in ['base','custom','locale']:
   if (label,parent,col) in profiles:
    value,fn=profiles[label,parent,col];idx=int(meta.get('index','-1'))
    if kind=='ability' and level>0 and meta.get('repeat','0')!='0':idx=level-1
    if idx>=0:
     parts=value.split(',');value=parts[idx] if len(parts)>idx else 'unresolved'
    result=(value,fn+' (inherited '+parent+')')
 else:
  for label in ['base','custom']:
   fn=label+'-'+meta['slk'].lower()+'.slk';row=defaults.get(fn,{}).get(parent,{})
   if col in row:result=(row[col],fn+' (inherited '+parent+')')
 return result
def value(kind,uid,field,level=0):return val(kind,uid,field,level)[0]
def plain(v):
 v=str(v);v=re.sub(r'\|c[0-9a-fA-F]{8}|\|r','',v).replace('|n',' / ')
 return v
def arr(name):
 return {int(i):v.strip().strip("'") for i,v in re.findall(r'set '+name+r'\[(\d+)\]=([^\r\n]+)',s)}
baseids=arr('udg_base_type');spawnids=arr('udg_spawn_unit');intervals=arr('ffgs_spawn_interval')
statnames=['HP','armor_type','armor','att_base','att_num_dice','att_dice_sides','att_CD','bounty_base','bounty_num_dice','bounty_dice_sides','range','level']
script={n:arr('udg_unit_'+n) for n in statnames}
units=[];details=[];abilityids=set()
fields={'udp1':'attack_point','ubs1':'attack_backswing','ucpt':'cast_point','ucbs':'cast_backswing','umvr':'turn_rate','ugol':'gold_cost','ulum':'lumber_cost','ubld':'build_time','ua1z':'projectile_speed','umvs':'movement_speed','uabi':'abilities','ua1t':'attack_type','ua1w':'weapon_type','ua1g':'targets','umvt':'movement_type','uhpr':'hp_regen','umpr':'mana_regen','umpm':'mana','uacq':'acquisition','ucol':'collision','uaen':'attacks_enabled','uhrt':'regen_type','ua1f':'splash_full','ua1h':'splash_medium','ua1q':'splash_small','uhd1':'splash_medium_factor','uqd1':'splash_small_factor','ua1p':'splash_targets','utar':'target_class','upgr':'affected_upgrades'}
for idx,base in baseids.items():
 if base not in manifest['allowed_bases']:continue
 uid=spawnids[idx];tier=0 if base=='hbar' else (1 if value('unit',base,'ureq')=='R00D' else 2)
 row={'index':idx,'tier':tier,'base':base,'unit':uid,'name':plain(value('unit',uid,'unam')),'base_name':plain(value('unit',base,'unam'))}
 for n in statnames:row[n]=float(script[n][idx])
 for field,label in fields.items():row[label]=value('unit',uid,field)
 row['interval_configured']=float(intervals[idx]);row['interval_actual']=int(float(intervals[idx])/.25+.5)*.25
 row['units_per_minute']=60/row['interval_actual'];row['base_gold']=value('unit',base,'ugol');row['base_time']=value('unit',base,'ubld')
 abilityids.update(a for a in str(row['abilities']).split(',') if len(a)==4)
 units.append(row)
 for field,meta in um.items():
  if meta.get('category') not in ['combat','move','stats','abil','tech']:continue
  v,origin=val('unit',uid,field);label=strings.get(meta.get('displayName'),meta.get('displayName',field))
  details.append({'kind':'unit','object':uid,'name':row['name'],'field':field,'label':label,'level':0,'value':v,'source':origin})
units.sort(key=lambda r:(r['tier'],r['index']))
abilityids.add('A0DD') # Conditional seasonal ability added by FFGS_ApplyUnit.
for uid in ['ucrm']:
 abilityids.update(a for a in str(value('unit',uid,'uabi')).split(',') if len(a)==4)
 for field,meta in um.items():
  if meta.get('category') not in ['combat','move','stats','abil','tech']:continue
  v,origin=val('unit',uid,field);label=strings.get(meta.get('displayName'),meta.get('displayName',field))
  details.append({'kind':'unit','object':uid,'name':plain(value('unit',uid,'unam')),'field':field,'label':label,'level':0,'value':v,'source':origin})
abilities=[]
for uid in sorted(abilityids):
 parent=parents.get(('ability',uid),uid)
 code=defaults['base-abilitydata.slk'].get(parent,{}).get('code',parent)
 row={'id':uid,'parent':parent,'name':plain(value('ability',uid,'anam')),'levels':value('ability',uid,'alev'),'values':[],'tooltip':plain(value('ability',uid,'aub1',1))}
 levels=int(row['levels']) if str(row['levels']).isdigit() else 1
 for field,meta in am.items():
  if meta.get('category') not in ['data','stats'] and field not in ['atar','abuf','aeff','areq','arqa']:continue
  use=meta.get('useSpecific','');exclude=meta.get('notSpecific','')
  if use and parent not in use.split(',') and code not in use.split(',') and not any(k[0]==uid and k[1]==field for k in tables['ability']):continue
  if exclude and parent in exclude.split(','):continue
  for level in (range(1,levels+1) if meta.get('repeat','0')!='0' else [0]):
   v,origin=val('ability',uid,field,level)
   if v=='unresolved':continue
   label=strings.get(meta.get('displayName'),meta.get('displayName',field))
   detail={'kind':'ability','object':uid,'name':row['name'],'field':field,'label':label,'level':level,'value':v,'source':origin}
   row['values'].append(detail);details.append(detail)
 abilities.append(row)
(O/'unit-audit.json').write_text(json.dumps({'units':units,'abilities':abilities,'fields':details},indent=2),encoding='utf-8')
with (O/'all-fields.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(details[0]));writer.writeheader();writer.writerows(details)
print(json.dumps({'units':units,'abilities':[{k:v for k,v in a.items() if k!='values'} for a in abilities]},indent=2))
