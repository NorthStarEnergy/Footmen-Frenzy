from pathlib import Path
import re,sys,json,html,collections
R=Path(__file__).resolve().parent;W=R.parent;B=R/'roundtrip'
sys.path.insert(0,str(W/'ffa-v4/tools'));from objectio import Obj
s=(B/'war3map.j').read_text();u=Obj(B/'war3map.w3u');skin=Obj(B/'war3mapSkin.w3u')
G=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots\audit\game-data')
def slk(path):
 cells={};x=y=1
 for line in path.read_text().splitlines():
  if not line.startswith('C;'):continue
  for k in line.split(';')[1:]:
   if k.startswith('X'):x=int(k[1:])
   elif k.startswith('Y'):y=int(k[1:])
   elif k.startswith('K'):cells[x,y]=k[1:].strip('"')
 headers={x:v for (x,y),v in cells.items() if y==1}
 return {cells[1,y]:{headers[x]:v for (x,yy),v in cells.items() if yy==y and x in headers} for y in sorted({y for x,y in cells}) if y>1 and (1,y) in cells}
def ini(path):
 result={};section=None
 for line in path.read_text(errors='replace').splitlines():
  line=line.strip()
  if line.startswith('['):section=line.strip('[]');result.setdefault(section,{})
  elif section and '=' in line and not line.startswith('//'):
   k,v=line.split('=',1);result[section][k]=v.strip('"')
 return result
base=collections.defaultdict(dict)
for prefix in ['base','custom']:
 for name in ['unitbalance','unitweapons','unitdata','unitui','unitabilities']:
  for id,p in slk(G/(prefix+'-'+name+'.slk')).items():base[id].update(p)
 for path in G.glob(prefix+'-*unitfunc.txt'):
  for id,p in ini(path).items():base[id].update(p)
st={int(k):v for k,v in re.findall(r'STRING (\d+)[^{]*\{\s*(.*?)\s*\}',(B/'war3map.wts').read_text(),re.S)}
def resolve(v):return st.get(int(v[8:]),v) if isinstance(v,str) and v.startswith('TRIGSTR_') else v
def props(o,id):return {m[0].decode():resolve(m[4]) for m in (o.find(id) or {}).get('mods',[])}
def field(id,key,defaultkey,default=None):
 p=props(u,id)|props(skin,id)
 obj=u.find(id);original=obj['old'].decode() if obj else id
 return p.get(key,base[original].get(defaultkey,default))
def num(v):
 try:return round(float(v),4)
 except:return v
rows=[]
for m in re.finditer(r"// ([^\n]+)\nset udg_spawn_unit\[(\d+)\]='(....)'(.*?)(?=//|endfunction)",s,re.S):
 i=int(m[2]);id=m[3];stats={k:num(v) for k,v in re.findall(r'set udg_unit_(\w+)\[\d+\]=([\d.]+)',m[4])}
 baseid=re.search(r"set udg_base_type\["+str(i)+r"\]='(....)'",s)[1]
 basename=field(baseid,'unam','Name','');tier=re.search(r'(.*?) Tier (\d)',basename)
 if i<=25:
  race=tier[1] if tier else 'Shared';t=int(tier[2]) if tier else 0
 else:race='Swap';t=0
 interval=6.666667 if i<=13 or 31<=i<=43 else 5 if 14<=i<=20 or 44<=i<=50 else 7.5
 damage_min=stats['att_base']+stats['att_num_dice'];damage_max=stats['att_base']+stats['att_num_dice']*stats['att_dice_sides'];avg=(damage_min+damage_max)/2
 weapon=field(id,'ua1w','weapTp1','unknown')
 row=dict(race=race,tier=t,name=({'Milita':'Militia','Mortat Bombers':'Mortar Bombers'}.get(m[1],m[1])) if i<=25 else field(id,'unam','Name',m[1]),id=id,base_id=baseid,index=i,hp=stats['HP'],armor=stats['armor'],armor_type={0:'Light',1:'Medium',2:'Heavy',3:'Fortified',4:'Normal',5:'Hero',6:'Divine',7:'Unarmored'}[int(stats['armor_type'])],damage=f'{damage_min:g}–{damage_max:g}',attack_type=field(id,'ua1t','atkType1'),cooldown=stats['att_CD'],raw_dps=round(avg/stats['att_CD'],2),range=stats['range'],movement=num(field(id,'umvs','spd')),turn_rate=num(field(id,'umvr','turnRate')),projectile_speed=num(field(id,'ua1z','Missilespeed','N/A')) if weapon not in ['normal','instant','_',''] else 'N/A',weapon=weapon,damage_point=num(field(id,'udp1','dmgpt1')),backswing=num(field(id,'ubs1','backSw1')),move_type=field(id,'umvt','movetp'),collision=num(field(id,'ucol','collision')),hp_regen=num(field(id,'uhpr','regenHP')),mana=num(field(id,'umpm','manaN')),mana_regen=num(field(id,'umpr','regenMana')),sight_day=num(field(id,'usid','sight')),sight_night=num(field(id,'usin','nsight')),spawn_interval=round(interval,6),units_per_wave=1,units_per_minute=round(60/interval,2),overdrive_per_minute=round(120/interval,2),unit_level=stats['level'],bounty=f"{stats['bounty_base']+stats['bounty_num_dice']:g}–{stats['bounty_base']+stats['bounty_num_dice']*stats['bounty_dice_sides']:g}",abilities=field(id,'uabi','abilList',''),upgrade_cost=num(field(baseid,'ugol','goldcost')))
 rows.append(row)
assert len(rows)==51
main=sorted([r for r in rows if r['index']<=25],key=lambda r:({'Shared':0,'Human':1,'Orc':2,'Night Elf':3,'Undead':4,'Elintian':5}.get(r['race'],9),r['tier']))
assert len(main)==26 and len({r['race'] for r in main})==6
for r in main:assert isinstance(r['movement'],(int,float)) and isinstance(r['turn_rate'],(int,float)),r
(R/'unit-reference.json').write_text(json.dumps(rows,indent=2))
columns=[('tier','Tier'),('name','Unit'),('hp','HP'),('armor','Armor'),('armor_type','Armor type'),('damage','Damage'),('attack_type','Attack type'),('cooldown','Attack sec'),('raw_dps','Raw DPS'),('range','Range'),('projectile_speed','Projectile speed'),('movement','Move speed'),('turn_rate','Turn rate'),('spawn_interval','Spawn sec'),('units_per_minute','Units/min'),('bounty','Gold bounty')]
def table(data,cols):
 return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+label+'</th>' for key,label in cols)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(r[key]))+'</td>' for key,label in cols)+'</tr>' for r in data)+'</tbody></table></div>'
notes='''<p>v17 • Overdrive research: <strong>250 gold</strong>. All five races: five tiers each, plus shared starting Footmen. Values are unupgraded troop stats, before auras, items, research, buffs and armor mitigation. Range/movement/projectile values are Warcraft world units; movement/projectiles are per second. Turn rate is the raw Warcraft object field, not degrees/second. N/A projectiles mean melee/instant delivery. Raw DPS is average primary attack damage divided by cooldown, before armor, animation delays or splash.</p><p>Steady production is one unit per wave; Overdrive produces two. Shared timer first fires after 5.416667 seconds, then every 6.666667. Other active production timers are 5 and 7.5 seconds and become enabled after mass ends. Startup initializes the wave count to two; it returns to one after an Overdrive expiration. The cap check uses ≤50 living units of the current troop type, so a wave can briefly exceed 50. The unused unit_spawnrate array is excluded.</p><p><strong>Audit findings:</strong> v14's 20% spawn increase changed only the shared timer, not the 5/7.5-second timers. Same-tier swaps can therefore change a unit's spawn interval: the complete swap table is below. Overdrive's activation tooltip says 45 seconds/80-second cooldown, research tooltip says 60/90, while the script tracks 45/110. These existing discrepancies are reported here; v17 changes only its research price. T1–T3 native XP levels 2/3 give 38/57, plus any eligible 95%-scaled scripted bonus. Footmen are level 1 (25 native XP) and receive separate scripted bonuses; a timed trigger can later change their level.</p>'''
body='<!doctype html><html><meta charset="utf-8"><title>Solo Foots v17 unit reference</title><style>body{font:15px system-ui;background:#111823;color:#e6edf5;margin:32px}h1,h2{color:#8ed5f5}p{max-width:1150px;line-height:1.55}.scroll{overflow:auto;margin-bottom:32px}table{border-collapse:collapse;white-space:nowrap;font-size:13px}th,td{padding:10px;border:1px solid #344256;text-align:right}th{background:#26364d;position:sticky;top:0}td:nth-child(2){text-align:left}tr:nth-child(even){background:#182333}input{padding:12px;width:340px;background:#26364d;color:white;border:1px solid #68788d}summary{cursor:pointer;color:#8ed5f5}a{color:#8ed5f5}</style><h1>Solo Foots v17 — unit reference</h1>'+notes+'<p><input id="search" placeholder="Filter by unit, race or stat…"></p>'
for race in dict.fromkeys(r['race'] for r in main):body+='<section><h2>'+race+'</h2>'+table([r for r in main if r['race']==race],columns)+'</section>'
extra=[('race','Race'),('name','Unit'),('id','ID'),('move_type','Movement'),('damage_point','Damage point'),('backswing','Backswing'),('collision','Collision'),('hp_regen','HP regen/s'),('mana','Mana'),('mana_regen','Mana regen/s'),('sight_day','Day sight'),('sight_night','Night sight'),('abilities','Ability IDs')]
body+='<h2>Additional unit stats</h2>'+table(main,extra)+'<h2>Same-tier swap variants</h2><p>Same-tier swaps are alternative base types, not additional unique troops. This table records their actual production timers.</p>'+table(rows[26:],[('base_id','Base ID'),('name','Unit'),('id','Unit ID'),('upgrade_cost','Swap gold'),('spawn_interval','Spawn seconds'),('units_per_minute','Units/min'),('overdrive_per_minute','Overdrive units/min')])
body+='<p>Source: packaged v17 war3map.j stat assignments and active spawn triggers; unit/skin object overrides; local Warcraft base/custom SLK and UnitFunc data for inherited fields. Secondary attacks and ability effects are not included in primary-attack DPS. Map compiled and archive verified; values have not been measured in a live game.</p><script>document.querySelector("#search").oninput=e=>{let q=e.target.value.toLowerCase();document.querySelectorAll("tbody tr").forEach(r=>r.hidden=!(r.textContent+ (r.closest("section")?.querySelector("h2")?.textContent||"")).toLowerCase().includes(q))}</script></html>'
(R/'unit-reference.html').write_text(body,encoding='utf-8')
print(json.dumps(main,indent=2))

