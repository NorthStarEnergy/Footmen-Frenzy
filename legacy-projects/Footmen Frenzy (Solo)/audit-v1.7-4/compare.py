from pathlib import Path
import sys,json,re,hashlib,html
root=Path(__file__).parent
sys.path.insert(0,str(root.parent/'.audit-deps'))
import mpyq
new=root.parent/'audit-v1.8-test07';new.mkdir(exist_ok=True)
source=Path(r'C:\Users\User\Documents\Warcraft III\Maps\Solo Foots\Solo Tests\Solo_Foots_v1.8_4P_PRELOAD_TEST07.w3x')
a=mpyq.MPQArchive(str(source),listfile=False)
for name in ['war3map.j','war3map.w3u','war3map.wts']:(new/name).write_bytes(a.read_file(name))
# Reuse the verified binary and scripted-stat readers, without its old-map report text.
code=(root/'analyze.py').read_text(encoding='utf8').split('headers=')[0].replace('encoding='+repr('utf-8-sig'), 'encoding='+repr('utf-8-sig')+',errors='+repr('replace'))
ns={'__file__':str(new/'analyze.py')};exec(compile(code,'stat-reader','exec'),ns)
old=json.loads((root/'spawn-stats.json').read_text(encoding='utf8')); fresh=ns['rows'];span=ns['span']
armor={'0':'light','1':'medium','2':'heavy','3':'fortified','4':'normal','5':'hero','6':'divine','7':'unarmored'}
fields=[('HP',lambda r:r['unit_HP']),('Armor',lambda r:r['unit_armor']),('Armor type',lambda r:armor[r['unit_armor_type']]),('Damage',lambda r:span(r,'unit_att_')),('Attack cooldown (s)',lambda r:r['unit_att_CD']),('Range',lambda r:r['unit_range']),('Level',lambda r:r['unit_level']),('Bounty',lambda r:span(r,'unit_bounty_')),('Spawn interval (s)',lambda r:r['interval']),('Move speed*',lambda r:r['object_overrides'].get('umvs','inherited')),('Attack type*',lambda r:r['object_overrides'].get('ua1t','inherited')),('Abilities*',lambda r:r['object_overrides'].get('uabi','inherited'))]
def equal(a,b):
    try:return float(a)==float(b)
    except (ValueError,TypeError):return a==b
def pair(a,b):return html.escape(str(a)) if equal(a,b) else '<b>'+html.escape(str(a))+' → '+html.escape(str(b))+'</b>'
trs=[];changes=[];data=[]
for before,after in zip(old,fresh):
    assert before['index']==after['index'] and before['spawn_unit']==after['spawn_unit']
    cells=[str(after['index']),html.escape(after['name']),after['spawn_unit']]
    record={'index':after['index'],'unit':after['name'],'id':after['spawn_unit'],'old':before,'new':after}
    data.append(record)
    for label,fn in fields:
        av,bv=fn(before),fn(after);cells.append(pair(av,bv))
        if not equal(av,bv):changes.append((after['index'],after['name'],label,av,bv))
    cells+=['<b>2 → 1</b>',pair(f'{120/before["interval"]:g}',f'{60/after["interval"]:g}')]
    trs.append('<tr>'+''.join('<td>'+v+'</td>' for v in cells)+'</tr>')
headers=['Index','Unit','Raw ID']+[x[0] for x in fields]+['Normal wave size','Units/min']
intro='''<h1>Solo v1.7-4 → v1.8 TEST07</h1><p>Comparison of the bot map Footmen_Frenzy_Solo_v1.7-4.w3x with the newest four-player solo test found: Solo_Foots_v1.8_4P_PRELOAD_TEST07.w3x. This does not refer to the separate 6- or 8-player FFA branches.</p>
<p><strong>Read each changed cell as old → new. A single value means unchanged.</strong> All 51 regular-production records are included, preserving alternate base paths. Damage and bounty include dice, before upgrades. The table can be searched by unit name or raw ID.</p>
<h2>Main findings</h2><ul><li>Normal wave size changes from 2 to 1. Actual spawn intervals remain 8, 5 and 7.5 seconds, so initial sustained normal production is halved across all units.</li><li>Burning Archer HP changes from 570 to 550 on both production paths. Its interval remains 5 seconds: initial production changes from 24/min to 12/min. It still produces 50% faster than Riflemen/Headhunters and 60% faster than Archers/Banshees.</li><li>Overdrive in TEST07 temporarily produces 2 per wave and resets only its owner to 1. In v1.7-4, an expiry can reduce other players to 1 too. Therefore the old 2-per-wave column describes initial production, not a guarantee for the entire game.</li><li>The active solo scheduler still uses fixed intervals. TEST07 contains a different FFGS interval table (e.g. 6.25 seconds for Burning Archer), but FFGS_SchedulerStart has no call site. Those settings are not the active spawn rates.</li><li>The normal unit cap remains 50 of the current spawned type. TEST07 clamps each wave to remaining capacity and counts the actual selected spawn type. The unused FFGS settings say 60; this does not change the active cap.</li></ul>
<p>Rates exclude initial mass, special waves, caps and production toggles. *Movement speed, attack type and abilities come from map object overrides; inherited fields require Warcraft base data and are not guessed. Ability IDs identify loadouts, not a complete comparison of individual spell effects. Hero, Colossal and summoned units are outside the regular-production table. Both maps' complete unit object overrides are available as JSON.</p>
<p>Static comparison of extracted compiled map data, not an in-game playtest. Script upgrade formulas are shown below the table.</p>
<input id="filter" placeholder="Filter units…" oninput="document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(this.value.toLowerCase()))">
'''
notes='''<h2>Upgrade formulas</h2><p>In both compiled solo spawn helpers, Rhme adds one attack die per level and Rhar adds 2 armor per level. Rhan adds 100 HP at level 1 then 45 per additional level; Robs adds the same HP plus 3 base damage at level 1 then 2 per additional level. R004 adds 100 range at level 1 then 55 per additional level. Rhan applies to indices 1,2,14,34,35,49 and Robs to 6,10,11,12,24,25,40,41,42,43 in both maps. R004 eligibility changes: old indices 3,4,5,15,32,33,46 become 4,5,15,32,33,46 in TEST07. Thus Archer index 3 loses this scripted range-upgrade bonus; alternate Archer index 31 was excluded in both. HP multiplier is 1.00 in both initializations. Mode-specific research/abilities may add other effects.</p>'''
style='body{font:15px system-ui;color:#172234;margin:28px}p,li{max-width:1150px;line-height:1.6}table{border-collapse:collapse;font-size:13px}td,th{padding:9px;border:1px solid #d6deea;white-space:nowrap}th{background:#182c45;color:white;position:sticky;top:0}tr:nth-child(even){background:#f3f6fa}td b{color:#934100;background:#fff2d3;padding:3px}input{padding:12px;margin:12px 0;width:300px}.wrap{overflow:auto;max-height:75vh}'
digest=hashlib.sha256(source.read_bytes()).hexdigest().upper()
doc='<!doctype html><meta charset="utf-8"><title>Solo unit comparison</title><style>'+style+'</style>'+intro+'<div class="wrap"><table><thead><tr>'+''.join('<th>'+html.escape(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join(trs)+'</tbody></table></div>'+notes+'<p>TEST07 SHA256: '+digest+'</p><p>v1.7-4 SHA256: BED87DA58BFC33AA38810C939661103DF81D8D413CE1E82E54D50E25D49685DF</p>'
(new/'unit-comparison.html').write_text(doc,encoding='utf8')
(new/'unit-comparison.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
print('51 rows compared. Changed displayed fields (excluding wave size/rate):')
for c in changes:print(c)
print('TEST07 SHA256:',digest)


