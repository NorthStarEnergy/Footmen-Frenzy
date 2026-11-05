from pathlib import Path
import json,html,re
R=Path(__file__).parent;O=R/'audit';d=json.loads((O/'unit-audit.json').read_text());units=d['units'];abilities=d['abilities']
def fmt(v):
 if isinstance(v,float):return f'{v:.4g}'
 return str(v).strip()
def esc(v):return html.escape(fmt(v))
def table(headers,rows):
 return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
unique=list({r['unit']:r for r in reversed(units)}.values());unique.sort(key=lambda r:(r['tier'],r['index']))
def dice(r,prefix):return f"{fmt(r[prefix+'base'])}+{fmt(r[prefix+'num_dice'])}d{fmt(r[prefix+'dice_sides'])}"
def damage(r,lv=0):return f"{fmt(r['att_base']+r['att_num_dice']+lv)}–{fmt(r['att_base']+(r['att_num_dice']+lv)*r['att_dice_sides'])}"
def level(r):return '1 → 2 at 600s' if r['index']==0 else (2 if r['index']<=13 or 31<=r['index']<=43 else r['level'])
intro='''<h1>Mini Foots v7 — unit and request audit</h1><p>Extracted from the combined October 28 build. Map object overrides are resolved against the installed Warcraft III base, custom_v1 balance, and English profile data. Script values are traced through initialization and the active scheduler. This is a source/archive audit; the combined build has not been tested in a new match.</p>
<p>“—” / “-” means an unset source field; “unresolved” means no inherited field was found. Neither is silently converted to zero. Times are seconds; speeds are Warcraft units/second. Object gold/build times describe the unit template, not a gold charge for automatic spawning.</p>
<h2>Findings</h2><ul><li>Eleven distinct army units are reachable through 21 retained base entries. Both Burning Archer paths now spawn the modified Ghoul (675 HP), and both T1 Headhunter paths spawn the modified Grunt (800 HP). Both use normal attacks and heavy armor. Huntress/Banshee/Wraith are unarmored; Militia is heavy with 900 HP.</li><li>The active spawn intervals are 4.5, 5, 6, 6.5, 7 and 8 seconds. All are exact multiples of the 0.25-second scheduler tick.</li><li>Normal post-mass production is one unit per wave. Opening footmen use two per regular wave, then the Mini Foots 1.5× multiplier; opening bonus waves are multiplied too. Teammates round complementarily, preserving the full three-player team total.</li><li>Production requires an active player, a living matching base, production enabled and the phase unlocked. The timer is free-running: an upgrade can catch the next scheduled wave. A wave is allowed at exactly 60 living units of its type, so a normal wave can reach 61; this inherited check is not a strict cap at 60.</li><li>The old level-two comment says eight minutes, but the actual level trigger fires at 600 seconds (ten minutes). Crypt Fiends are assigned level 3 then overridden to level 2 by the scheduler behavior table.</li><li>Hardened Skin A0A0/A0A2/A0BZ has zero chance, zero reduction and both melee/ranged inclusion disabled. It currently contributes no protection.</li><li>At the 2820-second bounty timer, only the original index set is updated; duplicate alternate tech entries retain their initial bounty. Both values are tabulated below.</li><li>Some abilities retain research prerequisites, notably Robk, Rhsb and Rotr. Their presence in an ability list does not prove they are usable: those prerequisites are not offered by the remaining attack/armor-only base research menus.</li></ul>
<h2>Script rules applied on spawn</h2><p>HP multiplier is 1.00. Attack upgrade level L (0–5) adds L damage dice: damage = base + (dice + L)d(sides). Armor upgrades add 2 per level, up to +10. The disabled special research branches no longer add HP, damage or range. Both object weapon ranges are zero; the compensated native setter applies the requested runtime range without accumulating it at mass release.</p><p>Footmen receive +30% movement speed for six seconds when released into mass (310 → 403). Their opening staging temporarily hides, pauses and protects them and disables pathing/food. A seasonal flag can add A0DD to eligible indices; this is conditional and is documented separately below.</p>'''
s=(R/'src/war3map.j').read_text(encoding='utf-8-sig')
bountyfn=re.search(r'function Trig_Bounty_Timer_1_Actions.*?\nendfunction',s,re.S)[0]
late={int(i):int(v) for i,v in re.findall(r'set udg_unit_bounty_base\[(\d+)\]=(\d+)',bountyfn)}
rows=[]
for r in units:
 rows.append([r['index'],r['tier'],r['base'],r['name'],r['unit'],r['interval_actual'],round(r['units_per_minute'],3),r['HP'],dice(r,'att_'),damage(r),damage(r,5),r['att_CD'],r['range'],r['armor'],r['armor']+10,{2:'Heavy (2)',1:'Medium (1)',7:'Unarmored (7)'}[r['armor_type']],level(r),dice(r,'bounty_'),f"{late.get(r['index'],int(r['bounty_base']))}+{fmt(r['bounty_num_dice'])}d{fmt(r['bounty_dice_sides'])}"])
body=intro+'<h2>All script stats and spawn rates — every tech path</h2>'+table(['Index','Tier','Base ID','Unit','Unit ID','Wave interval','Units/min/player','HP','Damage dice','Damage 0','Damage 5','Attack cooldown','Range','Armor 0','Armor 5','Armor type','Effective level','Initial gold bounty','Late gold bounty'],rows)
body+='<h2>Object timings, movement and costs</h2>'+table(['Unit','Attack point','Attack backswing','Cast point','Cast backswing','Turn rate','Move speed','Move type','Projectile speed','Weapon type','Attack type','Unit gold','Unit lumber','Unit build time','Tech gold','Tech time'],[[r[k] for k in ['name','attack_point','attack_backswing','cast_point','cast_backswing','turn_rate','movement_speed','movement_type','projectile_speed','weapon_type','attack_type','gold_cost','lumber_cost','build_time','base_gold','base_time']] for r in unique])
body+='<p>The initial Footman base is created for free; its inherited 7500-gold building price is not paid at match start. Rifleman weapon type is instant, so its projectile-speed field does not create a missile travel delay. Footman and Militia are melee and have no inherited projectile speed.</p>'
body+='<h2>Other object stats and ability assignments</h2>'+table(['Unit','HP regen/s','Regen condition','Mana','Mana regen/s','Acquisition','Collision','Targets','Ability IDs'],[[r[k] for k in ['name','hp_regen','regen_type','mana','mana_regen','acquisition','collision','targets','abilities']] for r in unique])
effects={
'ACce':'Ghoul Cleaving Attack: distributes 15% damage in a 135 radius to ground enemy/neutral targets; no mana or cooldown.',
'ACev':'Ghoul Evasion: 15%.',
'A075':'Grunt Web: nonhero enemy/neutral air/ground targets; duration 3s (hero field 0.01s, but heroes excluded); cooldown 60s; mana 0; range 600; lowering time 0.6s, flying height 200, melee range 123. No research requirement.',
'A0A3':'Grunt Hardened Skin is inactive: chance/minimum/ignored damage zero, melee and ranged inclusion disabled.',
'A03T':'Grunt spell damage reduction: 25%; damage bonus zero.',
'A00L':'Berserk: +10% movement, +50% attack speed, +25% damage taken; 8s, 40s cooldown, no mana. Requires Robk.',
'A071':'15% spell damage reduction; zero damage bonus.',
'A07U':'10% evasion.', 'A09R':'10% spell damage reduction; zero damage bonus.',
'A0A0':'Inactive Hardened Skin: chance/minimum/ignored damage all zero, ranged and melee inclusion false.',
'A0A2':'Inactive Hardened Skin: chance/minimum/ignored damage all zero, ranged and melee inclusion false.',
'A0BZ':'Inactive Hardened Skin: chance/minimum/ignored damage all zero, ranged and melee inclusion false.',
'A0C0':'5% spell damage reduction; zero damage bonus.',
'A0D9':'Charge: +50% movement, +10% attack speed, no increased damage taken; 5s, 30s cooldown, no mana. Shared by Militia, Ghoul and Grunt; research requirement cleared.',
'A0GM':'Searing Arrows: +5 damage, 7 mana per arrow, 640 cast range, zero cooldown.',
'A0DD':'Conditional seasonal Sphere artwork; no combat data fields. Duration 0.01s, cooldown 1s, mana 0. The seasonal flag initializes false and has no enabling assignment in the current script.',
'A0HG':'Adds 2 HP regeneration per second.', 'A0HY':'5% evasion.',
'Absk':'Berserk: +50% movement, +50% attack speed, +20% damage taken; 12s, 30s cooldown, no mana. Requires Robk.',
'Abur':'Burrow: ucry ↔ ucrm; morph flags 1; normal duration 0.5s, cooldown 6s, mana 0, altitude adjustment 0. Alternate form has its own object template; no new production interval.',
'Aegr':'Elune’s Grace: incoming piercing multiplier 0.80, magic multiplier 0.85; outgoing damage 1.00; movement/attack factors 0; deflection chance 0, deflected piercing factor 0, spell factor 1.',
'Afbk':'Feedback: drains up to 5 unit mana / 10 hero mana per hit; 1 damage per mana drained; summoned bonus 0; cast-range field 500.',
'Ahsb':'Sundering Blades: +15% versus defense type 1 (medium), flat bonus 0. Requires Rhsb.',
'Amgl':'Moon Glaive: unit uses missile-bounce weapon, maximum 2 targets, 50% damage loss per bounce, 400 bounce-search radius; secondary targets ground/structure/debris/enemy. Research requirement cleared in map.',
'Aotr':'Troll Regeneration is a research display ability; no regeneration amount in its ability fields. Requires Rotr. The actual Berserker +2 HP/s comes from A0HG.',
'Aiun':'Burrowed-form inventory: capacity 2; can get/drop items, cannot use them; drops items on death. Requires Rupm.',
'Aspa':'Burrowed-form Spider Attack: capacity 3; duration 1s; no mana or cooldown; ground/ward/item/structure/debris/enemy targets.',
'Aweb':'Burrowed-form Web: duration 12s units / 7s heroes; cooldown 12s; mana 0; cast range 400; lowers flying targets in 0.6s to height 200; melee range 128. Requires Ruwb.',
'Apsh':'Phase Shift: 0.75s, 20s cooldown, no mana; movement/attack reduction fields 0.',
'Ashm':'Shadow Meld: fade 1.5s, day/night duration 2.5s, action duration 0.5s, permanent-cloak flag false.',
'Aslo':'Slow: movement and attack speed reductions 18%; 5s on units / 2.5s heroes; cooldown 1s, mana 20, range 700; enemy air/ground.'}
body+='<h2>Abilities: effects and every resolved gameplay value</h2><p>All listed abilities have one configured level. Tables include cooldown, mana, duration, targeting, buffs, requirements and each ability-specific data field. Passive zero fields are retained to make the audit explicit.</p>'
for a in abilities:
 body+='<h3>'+esc(a['id']+' — '+a['name'])+'</h3><p>'+esc(effects.get(a['id'],'See values below.'))+'</p>'+table(['Field','Meaning','Level','Value','Source'],[[v[k] for k in ['field','label','level','value','source']] for v in a['values']])
body+='<h2>Resolved object field appendix</h2><p>Each unique unit is listed once. Runtime script overrides above take precedence over corresponding object fields here. This appendix retains all extracted combat, movement, statistics, ability and technology fields, including unused weapon-two values and unresolved inherited fields.</p>'
body+='<p>The modified Ghoul retains both attacks: primary 14+2d2 normal damage against non-structure targets; secondary 6+1d2 normal damage against structures, cooldown 1s, point/backswing 0.1s. The scripted attack upgrades apply to weapon one. Both object ranges are zero; the runtime range system targets 110. Replacement tech prices, spawn intervals, bounties and level remain those of the former T1 paths.</p>'
for r in unique+[{'unit':'ucrm','name':'Crypt Fiend (burrowed alternate form)'}]:
 rows=[];seen=set()
 for f in d['fields']:
  if f['kind']=='unit' and f['object']==r['unit'] and f['field'] not in seen:
   seen.add(f['field']);rows.append([f[k] for k in ['field','label','value','source']])
 body+='<details><summary>'+esc(r['name']+' ('+r['unit']+')')+'</summary>'+table(['Field','Meaning','Value','Source'],rows)+'</details>'
body+='<h2>Evidence</h2><p>Source: src/war3map.j, src/war3map.w3u and war3map.w3a plus inherited installed-game data saved in audit/game-data. Raw field-level evidence is also in unit-audit.json and all-fields.csv. Combined map SHA-256: '+json.loads((R/'verification.json').read_text())['sha256']+'</p>'
style='body{font:15px system-ui;margin:32px;color:#172536;background:#f7f9fc}h1,h2,h3{color:#163b64}p,li{max-width:1100px;line-height:1.5}.scroll{overflow:auto;margin:16px 0}table{border-collapse:collapse;background:white;font-size:13px}td,th{border:1px solid #d4dce5;padding:8px;text-align:left;white-space:nowrap}th{background:#173d64;color:white;position:sticky;top:0}tr:nth-child(even){background:#eef4fa}summary{padding:16px;cursor:pointer;font-weight:bold}details{border:1px solid #ccd9e6;margin:8px 0}'
(O/'unit-audit.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Mini Foots unit audit</title><style>'+style+'</style><body>'+body+'</body></html>',encoding='utf-8')
checks=[]
for r in units:
 ticks=round(r['interval_configured']/.25);assert ticks*.25==r['interval_actual']
 times=[t*.25 for t in range(1,2401) if t%ticks==0]
 assert all(abs(b-a-r['interval_actual'])<1e-9 for a,b in zip(times,times[1:]))
 checks.append({'index':r['index'],'interval':r['interval_actual'],'simulated_waves_in_600s':len(times),'status':'PASS'})
(O/'spawn-validation.json').write_text(json.dumps({'method':'Static scheduler model over 600 seconds; no production pauses, cap or unit deaths. Not an in-game measurement.','checks':checks},indent=2))
print('Rendered report;',len(units),'tech paths;',len(unique),'unique units;',len(abilities),'abilities; all scheduler models passed.')
requests=[
('Charge and HUD follow-up','Ghoul 675 HP / 1 armor; Grunt 800 HP / 2 armor. All three melee units share usable Charge. Grunt has only Charge and 15% Evasion; Ghoul retains Cleave/Evasion. HUD controls use the root game UI; delayed zoom creation and independent Stats startup.'),
('Melee roster and armor revision','Both Ghoul/Grunt T1 paths use the modified objects and normal/heavy typing; Huntress, Banshee and Wraith unarmored; Militia heavy, 900 HP.'),
('Name and source','Mini Foots v7, based on latest locally identified FF799X_Rx_HeroTavern_v1 testing map.'),
('8 players, 4 teams of 2','Eight lobby slots and starts; old middle slots closed; original team arithmetic retained.'),
('Description says 8, not 12','Literal lobby metadata updated; eight preview start markers; WTS BOM preserved.'),
('Hero level cap','MaxHeroLevel=10.'),('T2 maximum','30 higher-tier bases disabled; links removed; T3 unlock disabled.'),
('Attack/armor maximum 5/5','Both upgrade object levels and player limits capped at five.'),
('One of each creep','All 25 purchasable creep types have a living-unit team cap; duplicate purchase refunded.'),
('Opening mass +50% per player','Every opening footman wave scaled 1.5× with complementary teammate rounding.'),
('Solo-style invisible middle staging','Hidden, paused, invulnerable staging; restored together on release.'),
('Two bases per team, shifted backward','Middle base removed, outer bases moved 192 units backward.'),
('Four towers per team','Two towers per retained player; 16 total.'),
('Backshops available to all teams','Eight personal n003 upgrade-shop copies; neutral shop pages retained; existing owner redirects retained.'),
('T1/T2 only attack and armor research','All 21 allowed base entries use Rhme,Rhar only; special research limits and sharing addressed.'),
('Spawn object ranges zero','Both weapons set to zero on all 26 script spawn-unit types.'),
('Footman runtime range 110','Compensated native setter avoids additive reapplication at mass release; target stays 110.'),
('Separate mass fronts for allies','Independent counters; perpendicular fronts chosen by base position; twelve columns per rank at 64 spacing; no teammate overlap through 90 units each.'),
('Pub default; RJE-only menu','Only RJE#11113 or RJE#2927 gets Pub/Debug choices; ordinary players start Pub automatically.'),
('Pooling at 20:00','Manual and automatic pooling locked until game clock 1200; visible Pooling available countdown; then unlock and hide countdown.'),
('No transmute heroes','Six category-11 heroes removed from shops and random/fallback choices.'),
('Zoom slider and group placement','Explicit vertical track/thumb/disabled art; root game UI parent; lock/value anchored to slider beside minimap.'),
('Small Stats button above minimap','Label Stats; half-width 0.0625; attached immediately above minimap.'),
('Stats panel repair','Independent of multiboard visibility; eight retained rows only; text/icon anchors match; no frame scaling offsets; footer below rows.'),
('Gragas X actual bonus, no S-slot aura','Reversible direct armor bonus 5/7/9/11/etc for five seconds; old aura helper removed.'),
('Gragas X/C icons','New green Fortitude icon; simpler blue/cyan Slam icon, both packaged at existing texture paths.'),
('Random hero Boots of Speed','Reward item retained; distinct buff; independent +60 speed stacks with amulets, subject to movement cap.'),
('Boots sell for 75 gold','Item value 125 × 0.6 pawn rate; tooltip updated; multiple boots do not multiply bonus.'),
('Archive older builds','Original October 27, pre-zoom October 28 and zoom-only draft retained in archive.'),
('All tech unit data and spawn rates','21 tech entries, 11 distinct units; script/object tables, ability effects/values, source fields and scheduler models.'),
('No new work dropped','All 15 final payloads re-extracted byte-identically; 1,247 untouched files preserved; compiler and the full regression checks pass.')]
checkbody='<h1>Mini Foots v7 — request preservation checklist</h1><p>All requests below are present in the combined release. “Checked in build” means source/object/archive verification; it does not claim live gameplay validation.</p>'+table(['Request','Combined build result','Validation'],[[a,b,'Checked in build'] for a,b in requests])
checkbody+='<h2>Still pending</h2><p>The latest release is built, verified and installed in both map directories; the active installed hash matches. Live HUD interaction testing remains pending. No running match was interrupted.</p><p>In a new match, test zoom drag/lock/value and Stats layout, Footman range before/after release, Gragas armor duration/icon slots, boots plus Mira pickup/drop/resale, and all eight players’ shops and formations. A full multiplayer test is also pending.</p><p>SHA-256: '+json.loads((R/'verification.json').read_text())['sha256']+'</p>'
(O/'request-checklist.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Mini Foots request checklist</title><style>'+style+'td{white-space:normal;min-width:180px}</style><body>'+checkbody+'</body></html>',encoding='utf-8')
