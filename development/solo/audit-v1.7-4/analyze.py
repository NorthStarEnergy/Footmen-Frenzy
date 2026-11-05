from pathlib import Path
import re, struct, json, html
p=Path(__file__).parent
s=(p/'war3map.j').read_text(encoding='utf-8-sig')
wts=dict(re.findall(r'STRING (\d+)\s*\{\r?\n(.*?)\r?\n\}',(p/'war3map.wts').read_text(encoding='utf-8-sig'),re.S))
def resolve(v):
    return wts.get(v[8:],v) if isinstance(v,str) and v.startswith('TRIGSTR_') else v
d=(p/'war3map.w3u').read_bytes(); pos=0
def integer():
    global pos
    v=struct.unpack_from('<i',d,pos)[0];pos+=4;return v
def raw():
    global pos
    v=d[pos:pos+4].decode('latin1');pos+=4;return v
version=integer(); objects={}
for table in range(2):
    for _ in range(integer()):
        base,new=raw(),raw(); fields={}
        sets=integer() if version>=3 else 1
        for _ in range(sets):
            if version>=3: integer()
            for _ in range(integer()):
                key=raw();typ=integer()
                if typ==3:
                    end=d.index(0,pos); value=d[pos:end].decode('utf-8',errors='replace');pos=end+1
                elif typ==0:value=integer()
                else:value=struct.unpack_from('<f',d,pos)[0];pos+=4
                raw();fields[key]=resolve(value)
        objects[new if new!='\0'*4 else base]={'base':base,'fields':fields}
assert pos==len(d),(pos,len(d))
(p/'all-unit-object-overrides.json').write_text(json.dumps(objects,indent=2,ensure_ascii=False),encoding='utf8')
block=s.split('function Trig_set_spawn_variables_Actions')[1].split('endfunction')[0]
rows=[]
for comment,chunk in re.findall(r'// ([^\n]+)\n(.*?)(?=\n//|\Z)',block,re.S):
    vals={k:v.strip().strip("'") for k,i,v in re.findall(r'set udg_(\w+)\[(\d+)\]\s*=([^\n]+)',chunk)}
    if 'spawn_unit' not in vals:continue
    idx=int(re.search(r'udg_spawn_unit\[(\d+)\]',chunk)[1]); vals['index']=idx
    vals['name']=re.sub(r'^\[\d+\] | \(from \d+\)$','',comment).strip()
    vals['interval']=8 if idx<=13 or 31<=idx<=43 else 5 if 14<=idx<=20 or idx>=44 else 7.5
    fields=objects.get(vals['spawn_unit'],{}).get('fields',{})
    vals['object_overrides']=fields
    rows.append(vals)
assert len(rows)==51,len(rows)
(p/'spawn-stats.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
def span(r,prefix):
    b=int(r[prefix+'base']);n=int(r[prefix+'num_dice']);sides=int(r[prefix+'dice_sides']);return f'{b+n}–{b+n*sides}'
headers=['Index','Unit','ID','HP','Armor / type','Damage','Cooldown','Range','Level','Bounty','Spawn seconds','Units/min (2 per wave)','Move speed*','Attack type*','Abilities*']
lines=[]
for r in rows:
    f=r['object_overrides']; vals=[r['index'],r['name'],r['spawn_unit'],r['unit_HP'],r['unit_armor']+' / '+{'0':'light','1':'medium','2':'heavy','3':'fortified','4':'normal','5':'hero','6':'divine','7':'unarmored'}.get(r['unit_armor_type'],'?'),span(r,'unit_att_'),r['unit_att_CD'],r['unit_range'],r['unit_level'],span(r,'unit_bounty_'),r['interval'],f"{120/r['interval']:g}",f.get('umvs','inherited'),f.get('ua1t','inherited'),f.get('uabi','inherited')]
    lines.append('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in vals)+'</tr>')
intro='''<h1>Footmen Frenzy Solo v1.7-4: spawn audit and unit stats</h1>
<p>Exact map SHA256: BED87DA58BFC33AA38810C939661103DF81D8D413CE1E82E54D50E25D49685DF. Static audit of the extracted compiled script and object data; no Warcraft III playtest performed.</p>
<h2>Spawn findings</h2><ul>
<li><b>50-unit cap overshoot:</b> the scheduler allows spawning at count &lt;=50, then creates an entire wave. Two-unit waves can reach 52 of a type. It counts only the current spawn type, not the whole army.</li>
<li><b>Overdrive Undead cap bypass:</b> index 0 checks hfoo counts but FFOD_SpawnType creates ugho for Undead in Overdrive. The generated Ghouls do not count toward that check.</li>
<li><b>Opening mass imbalance:</b> slots 1 and 5 get 85 Footmen each; slots 8 and 12 get 81 each. The first batch is 13 versus 9; all later batches match. This is a definite count difference; whether deliberate balance compensation is unknown.</li>
<li><b>Spawn amount can drop for other players:</b> initialization sets two units per wave. An Overdrive timer expiry loops through all 12 players and sets every player with no remaining Overdrive time to one unit per wave, including other players whose timers were never started.</li>
<li><b>Missing upgrade coverage:</b> SoloFootsSpawnUsesRobs omits indices 29 and 30 (alternate Tauren/Dark Tauren), although the parallel FFGS behavior table includes them. These paths miss the scripted Robs HP/damage bonus.</li>
<li><b>Timing table mismatch:</b> udg_unit_spawnrate is not read by the active solo scheduler. Actual intervals are 8, 5 and 7.5 seconds. FFGS scheduler is disabled and has no startup call; old eight/five/ten triggers have no actions attached. No evidence of duplicate regular spawn timers.</li></ul>
<h2>How to read the stats</h2><p>All 51 regular production records are listed, including duplicate unit IDs in alternate base trees. Base stats before upgrades; damage/bounty include dice. Two units per wave initially: 15/min at 8 seconds, 24/min at 5 seconds, 16/min at 7.5 seconds. If wave size becomes one, halve these rates. Rates exclude caps, production toggles, initial mass and special waves.</p>
<p>Only player slots 1, 5, 8 and 12 run in this scheduler. First eight-second-band deadlines are 6.50, 6.75, 7.00 and 7.25 seconds of the active spawn clock. Other bands unlock through Tech Delay T1, then stagger by 0.25–1.00 seconds. The clock advances only once mass is active. A separate one-time wave at game-time counter 70 adds 15 Footmen per living base at 405 movement speed, without the normal production/cap gate.</p>
<p>Attack upgrade Rhme adds one damage die per level; armor upgrade Rhar adds 2 armor per level. Rhan on indices 1,2,14,34,35,49 adds 100 HP at level 1, then 45 per additional level. Robs on 6,10,11,12,24,25,40,41,42,43 adds the same HP plus 3 damage at level 1 and 2 per additional level. R004 on 3,4,5,15,32,33,46 adds 100 range at level 1, then 55 per additional level. Additional Overdrive-specific abilities/research may alter combat behavior.</p>
<p>*Movement, attack type and abilities show map object overrides. “Inherited” means the map does not supply that field; the installed Warcraft base data supplies it. Range and cooldown are script-configured values. No inherited values have been guessed. all-unit-object-overrides.json includes every field stored for every unit/hero/building object in this map; spawn-stats.json preserves all scripted spawn fields. Hero, summoned and Colossal units are outside this regular-production table.</p>'''
(p/'unit-stats.html').write_text('<!doctype html><meta charset="utf-8"><title>Solo v1.7-4 unit audit</title><style>body{font:15px system-ui;margin:32px;color:#172234}p,li{max-width:1100px;line-height:1.6}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #cdd4df;text-align:left}th{background:#e7edf5;position:sticky;top:0}tr:nth-child(even){background:#f4f6f9}</style>'+intro+'<table><thead><tr>'+''.join('<th>'+h+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join(lines)+'</tbody></table>',encoding='utf8')
print('Parsed',len(objects),'unit objects;',len(rows),'spawn records')
for r in rows[:26]: print(r['name'],r['unit_HP'],r['unit_armor'],span(r,'unit_att_'),r['unit_att_CD'],r['unit_range'],r['interval'])
