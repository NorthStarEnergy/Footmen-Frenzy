"""Source-based, reproducible item-stat replacement-cost model; no balance changes."""
import audit_core as c
import hero_core as h
import json,hashlib,re,base64
from pathlib import Path
from collections import defaultdict

dist=c.PROJECT/'item-wiki/dist';data=json.loads((dist/'data.json').read_text(encoding='utf-8'))
def stat(uid,field,scale=1):
 return sum(c.num('ability',a,field,1)*scale for a in c.abil_list(uid) if field in {f['raw'] for f in c.ability(a)['fields']})
def cost(uid):return c.num('item',uid,'igol')
rates=[]
def rate(key,label,unit,value,anchor,formula,kind='direct'):
 rates.append(dict(key=key,label=label,unit=unit,rate=value,anchor=anchor,formula=formula,kind=kind));return value
strength=rate('str','Strength','STR',cost('bgst')/stat('bgst','Istr'),'Belt of Giant Strength +10','250 / 10 = 25')
agi=rate('agi','Agility','AGI',cost('belv')/stat('belv','Iagi'),"Boots of Quel’Thalas +7",'300 / 7 = 42.857143')
intel=rate('int','Intelligence','INT',cost('ciri')/stat('ciri','Iint'),'Robe of the Magi +10','100 / (4 + 6) = 10')
hp=rate('hp','Maximum health','HP',cost('prvt')/stat('prvt','Ilif'),'Periapt of Vitality','500 / 400 = 1.25')
mana=rate('mana','Maximum mana','mana',cost('pmna')/stat('pmna','Iman'),'Pendant of Mana','300 / 300 = 1')
attack=rate('as','Attack speed','percentage point',cost('I03C')/stat('I03C','Isx1',100),'Gloves of Haste','250 / 20 = 12.5')
mr=rate('mr','Magic damage reduction','percentage point',cost('brac')/stat('brac','isr2',100),'Runed Bracers','1000 / 33 = 30.303030')
armor=rate('armor','Armor','armor',(cost('rde3')-stat('rde3','Istr')*strength)/stat('rde3','Idef'),'Ring of Protection +5','(200 − 4 STR × 25) / 5 armor = 20','derived')
hpr=rate('hpr','Health regeneration','HP/sec',cost('rlif')/stat('rlif','Ihpr'),'Ring of Regeneration','100 / 5 = 20')
mpr=rate('mpr','Percentage mana regeneration','percentage point',(cost('rwiz')-stat('rwiz','Iman')*mana)/stat('rwiz','Imrp',100),'Sobi Mask','(100 − 50 mana × 1) / 125 = 0.4','derived')
dmg=rate('damage','Flat attack damage','damage',cost('ratf')/stat('ratf','Iatt'),'Claws of Attack +25','300 / 25 = 12')
rate('evade','Evasion','percentage point',cost('evtl')/stat('evtl','Eev1',100),'Talisman of Evasion','350 / 25 = 14','secondary')
rate('leech','Personal lifesteal','percentage point',cost('modt')/stat('modt','Ivam',100),'Mask of Death','300 / 40 = 7.5','secondary')
rate('cleave','Cleave at 200 area','percentage point',cost('stwa')/stat('stwa','nca1',100),'Tusk of the Pitlord','800 / 60 = 13.333333; reference only at 200 area','secondary')
rate('mpflat','Flat mana-regeneration aura','mana/sec',(cost('crys')-stat('crys','Iman')*mana)/stat('crys','Hab1'),'Crystal Ball','(200 − 100 mana × 1) / 1.5 = 66.666667; aura benchmark','secondary-derived')
rate('damageAura','Attack-damage aura','percentage point',cost('ward')/stat('ward','Cac1',100),'Warsong Battle Drums','500 / 15 = 33.333333; melee-and-ranged aura benchmark','secondary')
R={r['key']:r for r in rates}
core_keys={'str','agi','int','hp','mana','as','mr','armor','hpr','mpr','damage'}
def extract(uid):
 terms=[];unpriced=[]
 def add(a,key,q,note=''):
  if q:terms.append(dict(key=key,label=R[key]['label'],quantity=round(q,6),rate=R[key]['rate'],gold=q*R[key]['rate'],ability=a,note=note,core=key in core_keys))
 for a in c.abil_list(uid):
  ab=c.ability(a);code=ab['code'];n=lambda field:c.num('ability',a,field,1);handled=True
  if code=='AIab':
   for k,f in [('str','Istr'),('agi','Iagi'),('int','Iint')]:add(a,k,n(f))
  elif code=='AIde':add(a,'armor',n('Idef'))
  elif code=='AIml':add(a,'hp',n('Ilif'))
  elif code=='AImm':add(a,'mana',n('Iman'))
  elif code=='AIas':add(a,'as',n('Isx1')*100)
  elif code=='Arel':add(a,'hpr',n('Ihpr'))
  elif code=='AIrm':add(a,'mpr',n('Imrp')*100)
  elif code=='AIat':add(a,'damage',n('Iatt'))
  elif code=='AIsr':add(a,'mr',n('isr2')*100)
  elif code=='AEev':add(a,'evade',n('Eev1')*100)
  elif code=='AIva':add(a,'leech',n('Ivam')*100)
  elif code=='ANca':
   area=n('aare')
   if area==200:add(a,'cleave',n('nca1')*100)
   else:unpriced.append(f'{a}: cleave area {area:g} differs from the 200-area benchmark.')
  elif code in ['AIob','AIpb','AIlb','AIcb']:
   add(a,'damage',n('Idic' if code=='AIcb' else 'Idam'));unpriced.append(f'{a}: on-hit orb effects, secondary air attack and target rules are not priced. Shared Idic/Idam data is counted once.')
  elif code=='AUav':add(a,'leech',n('Uav1')*100,'Proxy: personal lifesteal rate applied to carrier benefit; aura allies/range and melee restriction not priced.')
  elif code=='AHab':
   if n('Hab2')==0:add(a,'mpflat',n('Hab1'),'Flat aura benchmark; target count/radius and self-only penalty differences not priced.')
   else:unpriced.append(f'{a}: percentage mana aura has no independent baseline.')
  elif code=='AOae':
   add(a,'as',n('Oae2')*100,'Carrier-equivalent only; allied aura benefit not priced.');unpriced.append(f'{a}: movement aura {n("Oae1")*100:g}% and allied attack-speed coverage not priced.')
  elif code=='AUau':
   if n('Uau3')==0:add(a,'hpr',n('Uau2'),'Carrier-equivalent regeneration/penalty; allied coverage not priced.')
   unpriced.append(f'{a}: movement aura {n("Uau1")*100:g}% and allied regeneration coverage not priced.')
  elif code in ['AOac','AEar']:
   if n('Ear4')==0:add(a,'damageAura',n('Cac1' if code=='AOac' else 'Ear1')*100,'Aura proxy: range, eligible melee/ranged targets, stacking and army size differ.')
   else:unpriced.append(f'{a}: flat damage aura has no independent benchmark.')
  elif code=='AIms':unpriced.append(f'{a}: +{n("Imvb"):g} movement speed. No separately purchasable pure-speed item in the reachable shops establishes a clean gold rate.')
  else:handled=False
  if not handled:unpriced.append(f'{a} — {ab["name"]}: active, proc, summon or special effect; no defensible per-stat gold price.')
 return terms,unpriced

# Verify the latest map agrees with the audit before assigning values.
for item in data['items']:
 for field in ['igol','iabi','iuse']:assert str(c.value('item',item['id'],field))==str(h.value('item',item['id'],field))
 for a in c.abil_list(item['id']):
  old={f['raw']:f['value'] for f in c.ability(a)['fields']};new={f['raw']:f['value'] for f in h.ability(a)['fields']};assert old==new,(item['id'],a)
for r in json.loads((c.ROOT/'recipe-audit.json').read_text()):
 if r['recipe_id'] in {x['id'] for x in data['items']}:
  assert re.sub(r'\s+','',c.functions[r['function']]['text'])==re.sub(r'\s+','',h.functions[r['function']]['text']),r['function']

rows=[]
for x in data['items']:
 terms,unpriced=extract(x['id']) if x['category'] in ['Equipment','Crafted','Starting item','Recipe'] else ([],['Consumable, spell purchase or information entry: purchase funds its effect/access; no permanent held-stat valuation.'])
 if x['category']=='Recipe':unpriced.append('Recipe scroll purchase. These are its carried bonuses only; see the crafted result for complete cost and bonuses. A scroll is not a cheap copy of its result.')
 if x['category']=='Starting item':unpriced.append('Granted free; replacement-cost value is not a purchase price or sale value.')
 core=sum(t['gold'] for t in terms if t['core']);total=sum(t['gold'] for t in terms)
 row=dict(id=x['id'],name=x['name'],category=x['category'],cost=x['cost'],summary=x['summary'],icon=x.get('icon'),terms=terms,unpriced=unpriced,coreGold=core,referenceGold=total,residual=x['cost']-total,coveragePercent=total/x['cost']*100 if x['cost'] else None,details=x['details'],recipe=x.get('recipe'))
 if x['id']=='I001':row['summary']='+150 health, +100 mana and +60 movement speed. Starting amulet; not sold.'
 if x['id'] in ['I02N','I030','I03Y','I012','I04A']:row['unpriced'].append('Consumes starting amulet: +80 movement is +20 over its actual +60, not an additional +80. Full-stat subtotal includes the granted ingredient; compare incremental value separately.')
 rows.append(row)
byid={r['id']:r for r in rows}
for r in rows:
 if r['recipe'] and r['category']=='Crafted':
  r['ingredientReferenceGold']=sum(byid[i['id']]['referenceGold'] for i in r['recipe']['ingredients'])
  r['combineStatGainGold']=r['referenceGold']-r['ingredientReferenceGold']

notes=[
 'Gold values are replacement-cost benchmarks inferred from shop prices, not a claim of balanced prices or actual purchase-cost allocation. There is no unique true price for each stat in a mixed item.',
 'Every item has a row. Core stats and optional effect benchmarks are separated. Residual = purchase/complete crafting cost minus reference value; it is not an objective price for the remaining abilities. A negative residual means benchmark stats exceed price, not negative-priced spells.',
 'Attribute values already represent the attribute bundle. Do not also count the health, mana, armor, attack speed, regeneration or primary-attribute damage supplied by STR/AGI/INT. Only separate item ability bonuses are added.',
 'Percentages use percentage points: +20% attack speed is 20 × 12.5g. +125% mana regeneration is 125 × 0.4g, and is not +125 mana/sec. Flat mana/sec is a separate aura-derived benchmark.',
 'Armor has no pure baseline in these shops. Ring of Protection +5 gives +5 armor AND +4 STR: (200−4×25)/5=20g/armor. Medaillon of Glim instead implies 12.5g/armor after subtracting mana; inconsistent bundle pricing is real. Ring is the selected benchmark, and rates can be edited.',
 'Sobi Mask gives +50 mana alongside +125% regeneration. Its gross price is 0.8g per regeneration percentage point only if mana is ignored; subtracting 50g mana yields 0.4g. Neither rate is universal fair value.',
 'Core subtotal excludes movement, procs, spell block, immunity, invisibility, healing casts and summon damage. Secondary lifesteal, evasion, cleave and aura benchmarks are optional comparisons; target restrictions, aura coverage, diminishing returns, uptime and stacking are not priced.',
 'Recipe results use complete ingredient + scroll cost. Starting amulet costs 0g but has positive reference stats; replacing it is not the same as obtaining the entire result from nothing. Recipe-scroll rows value only their carried bonuses.',
 'Latest v37 item prices, attached ability fields and sold-recipe combination functions match the v10 audit. No balance/gameplay edits were made. Starting amulet movement was corrected in this analysis from the earlier summary’s +80 to the actual +60.',
]
hero=[]
for uid,aid in [('N02O','A05W'),('N00P','ANca'),('E00U','ANca'),('H02I','A08O'),('HDk1','ADrc'),('HMu1','AMuc')]:
 a=h.ability(aid,True);n=a['levels'];hero.append(dict(id=uid,name=h.name('unit',uid),ability=aid,cleave=[h.num('ability',aid,'nca1',i)*100 for i in range(1,n+1)],area=[h.num('ability',aid,'aare',i) for i in range(1,n+1)],temporary=uid in ['HDk1','HMu1'],raw=a))
heroNotes=[
 'Myrmidon reaches 190% cleave versus 80% for Pit Lord/Crazy Cat/Yeti. Its area unexpectedly drops from 225 at rank 2 to inherited 200 at rank 3; this is the actual object value.',
 'Pit Lord and Crazy Cat share ANca, so editing that ability changes both. Yeti has separate A08O with a maximum 400 area, versus 325 for ANca. All listed native cleaves target ground enemies/neutrals.',
 'Demon Knight and Dr. Mundo receive scripted cleave of 30/55/80% at area 250 during Demon Ascension/Undying. DR_Start also adds spell immunity, +60/80/100% attack speed and +25/30/35% movement for a scheduled 15/18/21-second state. Death-refusal mechanics can affect its end; raw duration is not a promise of indefinite survival.',
 'Yeti Transformation is native Avatar (A0B5): 50 seconds, 220-second cooldown; +500/750/1000 HP, +5/10/15 armor and +30/40/50 damage. This is an important durability pairing with its native cleave.',
 'Blooddancer (O00G) has Pulverize A0C6: 25% proc chance, 100/125/150/200/275/300 fixed damage; full area 250/275/300/350/350/350 and half-damage area 300/325/400/400/450/500. It is attack-triggered area damage, not percentage cleave; raw attack damage does not enter its fixed damage field.',
 'Demon Hunter/Fox transformed forms use missile splash rather than ANca. They are a separate attack-area family; they should not be treated as proof of melee-cleave or melee-lifesteal compatibility.',
 'Tusk adds a separate A07G native cleave (60%, area 200). No item-specific combination script changes the above native cleave fields. Source data alone does not prove the engine’s cleave stacking or lifesteal-on-secondary-target behavior; those require a live test.',
 'Crazy Cat is explicitly prohibited from carrying Amulet of the Wind (I04A) by the pickup-limit script; do not assume every problematic item is available to every cleaver.',
]
model=dict(sourceMap=h.MAP.name,sourceSha256=hashlib.sha256(h.MAP.read_bytes()).hexdigest(),rates=rates,items=rows,notes=notes,heroes=hero,heroNotes=heroNotes)
(dist/'item-value-model.json').write_text(json.dumps(model,indent=2),encoding='utf-8')
(c.ROOT/'item-value-model.json').write_text(json.dumps(model,indent=2),encoding='utf-8')
assert len(rows)==222
for anchor in ['bgst','belv','ciri','prvt','pmna','I03C','brac','rde3','rlif','rwiz','ratf','evtl','modt','stwa','crys','ward']:
 assert abs(byid[anchor]['referenceGold']-byid[anchor]['cost'])<.01,anchor
print('PASS: all 222 rows; 16 anchor prices reconstruct; latest item and recipe fields match.')
for uid in ['I00W','I00D','I00F','hval','I04A','clfm','I01R','I00V','stwa','I00X']:
 r=byid[uid];print(uid,r['name'],'cost',r['cost'],'core',round(r['coreGold'],2),'reference',round(r['referenceGold'],2),'residual',round(r['residual'],2))
