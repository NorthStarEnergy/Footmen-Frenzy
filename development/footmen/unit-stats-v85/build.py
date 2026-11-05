from pathlib import Path
import sys,re,json,ast,csv,hashlib,html
W=Path(__file__).resolve().parent.parent; O=W/'unit-stats-v85'
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c,objdata,functions,archive
env={'re':re}
tree=ast.parse((W/'mini-foots/tools/game_data.py').read_text())
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['slk','ini']:exec(compile(ast.Module(body=[node],type_ignores=[]),'parser','exec'),env)
G=W/'799x-backport/item-audit/game-data'; defaults={}; profiles={}; strings={}
for p in G.glob('*'):
 if p.suffix=='.slk':defaults[p.name]=env['slk'](p.read_bytes())
 elif p.suffix=='.txt':
  for uid,fields in env['ini'](p.read_bytes()).items():
   for field,value in fields.items():
    profiles[p.name.split('-')[0],uid,field]=(value,p.name)
    if p.name.startswith('worldedit'):strings[field]=value
um=defaults['base-unitmetadata.slk']
def clean(v):return re.sub(r'\|c[0-9a-fA-F]{8}|\|r','',str(v)).replace('|n',' / ')
def arr(s,name):
 out={}
 for i,v in re.findall(r'\bset\s+'+re.escape(name)+r'\[(\d+)\]\s*=\s*([^\r\n]+)',s):
  v=v.split('//')[0].strip().strip("'")
  try:v=float(v);v=int(v) if v.is_integer() else v
  except ValueError:pass
  out[int(i)]=v
 return out
result={}
for inst in json.loads((W/'shared-sync-v85/installation.json').read_text()):
 variant=inst['variant']; path=Path(inst['path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==inst['sha256'].lower()
 d=O/variant;d.mkdir(exist_ok=True);a=archive(path);h=c.c_void_p();assert storm.SFileOpenArchive(str(path),0,256,c.byref(h))
 names=['war3map.j','war3map.wts','war3map.w3u','war3mapSkin.w3u','war3mapMisc.txt']
 for name in names:
  if a.get_hash_table_entry(name):(d/name).write_bytes(read_storm(h,name))
 storm.SFileCloseArchive(h)
 s=(d/'war3map.j').read_text(encoding='utf-8-sig');fs=functions(s)
 assert s==(W/'shared-sync-v85'/variant/'src/war3map.j').read_text(encoding='utf-8-sig')
 wts=dict(re.findall(r'STRING\s+(\d+)[^\{]*\{\s*\n(.*?)\n\}',(d/'war3map.wts').read_text(encoding='utf-8-sig'),re.S))
 def resolve(v):return wts.get(str(int(v[8:])),v) if isinstance(v,str) and v.startswith('TRIGSTR_') else v
 mods={};parents={}
 for name in ['war3mapSkin.w3u','war3map.w3u']:
  if not (d/name).exists():continue
  for tab in objdata.load(str(d/name))['tables']:
   for e in tab:
    uid=e['newId'] if e['newId']!='\0'*4 else e['oldId'];parents[uid]=e['oldId']
    for m in e['mods']:mods[uid,m['id']]=(resolve(m['value']),name)
 def val(uid,field):
  if (uid,field) in mods:return mods[uid,field]
  meta=um.get(field)
  if not meta:return ('unresolved','no metadata')
  parent=parents.get(uid,uid);col=meta['field'];r=('unresolved','not present in cached defaults')
  if meta['slk']=='Profile':
   for label in ['base','custom','locale']:
    hit=profiles.get((label,parent,col))
    if hit:
     v,fn=hit;idx=int(meta.get('index','-1'));parts=next(csv.reader([v],skipinitialspace=True))
     if idx>=0:v=parts[idx] if len(parts)>idx else 'unresolved'
     r=(resolve(v),fn+' inherited '+parent)
  else:
   for label in ['base','custom']:
    fn=label+'-'+meta['slk'].lower()+'.slk';row=defaults.get(fn,{}).get(parent,{})
    if col in row:r=(row[col],fn+' inherited '+parent)
  return r
 def value(uid,f):return val(uid,f)[0]
 def unitname(uid):
  n=clean(value(uid,'unam'))
  return n if n else clean(value(parents.get(uid,uid),'unam'))+' (blank map display name)'
 init=fs['Trig_set_spawn_variables_Actions'];spawn=arr(init,'udg_spawn_unit');bases=arr(s,'udg_base_type')
 statnames=['HP','armor_type','armor','att_base','att_num_dice','att_dice_sides','att_CD','bounty_base','bounty_num_dice','bounty_dice_sides','range','level']
 stats={n:arr(init,'udg_unit_'+n) for n in statnames};intervals=arr(fs['FFGS_InitSettings'],'ffgs_spawn_interval')
 army=[]
 for idx,uid in sorted(spawn.items()):
  row={'index':idx,'id':uid,'name':unitname(uid),'base_id':bases[idx],'base_name':clean(value(bases[idx],'unam'))}
  for n in statnames:row[n]=stats[n][idx]
  row['damage_min']=row['att_base']+row['att_num_dice'];row['damage_max']=row['att_base']+row['att_num_dice']*row['att_dice_sides']
  row['nominal_DPS']=round((row['damage_min']+row['damage_max'])/2/row['att_CD'],2)
  row['bounty_min']=row['bounty_base']+row['bounty_num_dice'];row['bounty_max']=row['bounty_base']+row['bounty_num_dice']*row['bounty_dice_sides']
  row['spawn_seconds']=(8 if idx<=13 or 31<=idx<=43 else 7.5 if 21<=idx<=30 else 5) if variant=='solo' else intervals[idx]
  for field,label in {'umvs':'movement_speed','umvt':'movement_type','uhpr':'HP_regen','umpm':'mana','umpr':'mana_regen','ua1t':'attack_type','ua1w':'weapon_type','uabi':'abilities','ua1g':'targets','uacq':'acquisition','ucol':'collision','udp1':'attack_point','ubs1':'attack_backswing','ucpt':'cast_point','ucbs':'cast_backswing','umvr':'turn_rate','ugol':'unit_gold','ulum':'unit_lumber','ubld':'build_time','upgr':'upgrades'}.items():row[label]=value(uid,field)
  army.append(row)
 assert len(army)==51
 heroes=[];heroids=arr(fs['Trig_set_hero_numbers_Actions'],'udg_hero_type')
 for idx,uid in sorted(heroids.items()):
  row={'index':idx,'id':uid,'name':unitname(uid)}
  for name in sorted(set(re.findall(r'\bset (udg_hero_\w+)\[',fs['Trig_set_hero_stats_Actions']))):
   values=arr(fs['Trig_set_hero_stats_Actions'],name)
   if idx in values:row[name.removeprefix('udg_hero_')]=values[idx]
  heroes.append(row)
 catalog=[]
 for uid in sorted(set(parents)|set(spawn.values())|set(bases.values())|set(heroids.values())):
  fields=[]
  for field,meta in um.items():
   if meta.get('category') not in ['combat','move','stats','abil','tech']:continue
   v,origin=val(uid,field);label=strings.get(meta.get('displayName'),meta.get('displayName',field))
   fields.append({'field':field,'label':label,'value':v,'source':origin})
  catalog.append({'id':uid,'parent':parents.get(uid,uid),'name':unitname(uid),'fields':fields})
 runtime={n:body for n,body in fs.items() if n in ['FFGS_InitSettings','FFGS_InitBehaviourTables','FFGS_ApplyUnit','FFGS_ProcessIndex','SoloFootsSpawnPrepareStats','SoloFootsSpawnApplyStats','SoloFootsSpawnTick','SoloFootsSpawnUsesRhan','SoloFootsSpawnUsesRobs','SoloFootsSpawnUsesRangeUpgrade'] or ('udg_unit_HP_actual[' in body and 'GetPlayerTechCountSimple' in body)}
 result[variant]={'map':inst,'army':army,'heroes':heroes,'object_catalog':catalog,'runtime_reference':runtime}
differences=[]
for a,b in zip(result['solo']['army'],result['799x']['army']):
 assert a['index']==b['index']
 changed={k:{'solo':a[k],'799x':b[k]} for k in a if a[k]!=b[k]}
 if changed:differences.append({'index':a['index'],'name':a['name'],'changes':changed})
result['differences']=differences
(O/'unit-stats.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
payload=json.dumps(result,ensure_ascii=False).replace('</','<\\/')
page='''<!doctype html><html><meta charset="utf-8"><title>Solo and 799X unit stats</title><style>body{font:15px system-ui;margin:30px;background:#101725;color:#e7edf8}h1,h2{color:#8dd9ff}button,input,select{padding:10px;margin:5px;background:#233149;color:inherit;border:1px solid #53627a;border-radius:5px}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:8px;border:1px solid #354157;text-align:left}th{background:#233149;position:sticky;top:0}details{margin:10px 0;padding:10px;background:#192337}summary{cursor:pointer}p{max-width:1100px;line-height:1.6}.scroll{overflow:auto}pre{white-space:pre-wrap}small{color:#aabbd3}</style><h1>Solo UPDATE09 & 799X v85 — unit stats</h1><p>Extracted from the installed maps. Army tables use scripted spawn overrides at zero research, HP multiplier 1, without items, auras, temporary buffs or mode bonuses. Damage includes dice; nominal DPS is average damage ÷ attack cooldown before armor, attack speed bonuses and movement. Bounty includes dice. Spawn interval is the active scheduler's period, subject to unlocks, capacity and mass pauses.</p><p>Expand each army entry for every runtime baseline field. The object catalog includes combat, movement, stats, abilities and technology fields for map-defined units, buildings, heroes and helpers. Catalog fields are <b>object templates</b>, not final buffed or hero-attribute-adjusted values; army and hero script overrides take precedence. Inherited fields come from the project's cached Warcraft base/custom data, not a freshly queried game client. Missing values are marked unresolved. Ability and upgrade lists use raw IDs. Dynamic or scripted ability effects are not folded into static stats.</p><p>Research changes normal army dice (+1 per Rhme level) and armor (+2 per Rhar level). Applicable Rhan/Robs branches add HP; Robs also adds base damage; R004 increases selected ranged units' reach. HP multipliers, Overdrive, seasonal effects, temporary mass speed and experience can further change units. Exact branch conditions and formulas are included under Runtime source.</p><select id="map"><option value="solo">Solo UPDATE09</option><option value="799x">799X v85</option></select><select id="section"><option value="army">Army units — 51 spawn paths</option><option value="heroes">Hero roster — scripted base attributes</option><option value="object_catalog">Full object-stat catalog</option><option value="differences">Army differences — Solo vs 799X</option><option value="runtime_reference">Runtime source</option></select><input id="search" placeholder="Filter by name or raw ID"><div id="out"></div><script>const D=PAYLOAD;
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const table=(rows,cols)=>'<div class="scroll"><table><thead><tr>'+cols.map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>'<td>'+esc(typeof r[c]==='object'?JSON.stringify(r[c]):r[c])+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
function render(){const m=document.querySelector('#map').value,s=document.querySelector('#section').value,q=document.querySelector('#search').value.toLowerCase(),o=document.querySelector('#out');let rows=s==='differences'?D.differences:D[m][s];if(s==='runtime_reference'){o.innerHTML=Object.entries(rows).filter(([k,v])=>(k+v).toLowerCase().includes(q)).map(([k,v])=>'<details><summary>'+esc(k)+'</summary><pre>'+esc(v)+'</pre></details>').join('');return}rows=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q));let top='<p>'+rows.length+' entries shown</p>';if(s==='army')top+=table(rows,['index','name','base_name','HP','armor','armor_type','damage_min','damage_max','att_CD','nominal_DPS','range','movement_speed','spawn_seconds','bounty_min','bounty_max','level'])+'<p>Armor-type enum: 0 light, 1 medium, 2 heavy, 3 fortified, 4 normal, 5 hero, 6 divine, 7 unarmored. Level is the baseline table value; runtime experience/phase rules may override it.</p>';if(s==='heroes')top+=table(rows,[...new Set(rows.flatMap(Object.keys))]);o.innerHTML=top+rows.map(r=>'<details><summary>'+esc((r.index??'')+' '+r.name+' ['+(r.id??'comparison')+']')+'</summary>'+ (s==='object_catalog'?table(r.fields,['field','label','value','source']):table(Object.entries(s==='differences'?r.changes:r).map(([k,v])=>({field:k,value:v})),['field','value']))+'</details>').join('')}
document.querySelectorAll('select,input').forEach(x=>x.addEventListener('input',render));render();</script></html>'''.replace('PAYLOAD',payload)
(O/'unit-stats.html').write_text(page,encoding='utf8')
print(json.dumps({k:{'army':len(v['army']),'heroes':len(v['heroes']),'objects':len(v['object_catalog'])} for k,v in result.items() if k!='differences'}));print('Differing spawn entries:',len(differences))
print(json.dumps([{k:r[k] for k in ['index','name','HP','damage_min','damage_max','spawn_seconds']} for r in result['799x']['army']],ensure_ascii=False))
