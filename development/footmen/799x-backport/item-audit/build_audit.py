import audit_core as c
from consumables import SUMMARIES, REASONS
import json,copy,re,hashlib,io,base64
from PIL import Image

def read(n):return json.loads((c.ROOT/n).read_text(encoding='utf-8'))
reach=read('shop-reachability.json'); scripts=read('script-audit.json')
equip={x['id']:x for x in read('equipment-audit.json')}
shops=[dict(id=s['id'],name=s['name']+' ('+s['id']+')',items=[i for i in s['stock'] if i not in s['invalid_ids']]) for s in reach['shops'] if s['reachable']]
live=set(i for s in shops for i in s['items'])
recipes={x['recipe_id']:x for x in read('recipe-audit.json') if x['recipe_id'] in live}
results={r['result']['id']:r for r in recipes.values()}
script_items={x['id']:x for x in scripts['items']}
limits={x['id']:x for x in scripts['pickup_limits']}
assert len(live)==108 and len(recipes)==17
assert live==set(equip)|set(SUMMARIES)|set(recipes)|{'I013','I014','I016'},live-(set(equip)|set(SUMMARIES)|set(recipes))
dist=c.PROJECT/'item-wiki/dist';(dist/'icons').mkdir(exist_ok=True)
items=[];changes=[];patches={};icon_errors=[]
def restrictions(uid):
 out=[];x=limits.get(uid,{})
 if x.get('maximum_copies'):out.append('Maximum '+str(x['maximum_copies'])+' per hero.')
 if x.get('prohibited_unit_ids'):out.append('Cannot be carried by: '+', '.join(c.name('unit',u)+' ('+u+')' for u in x['prohibited_unit_ids'])+'.')
 if uid in scripts['mutually_exclusive_items']:out.append('Cannot be combined with '+', '.join(c.name('item',u) for u in scripts['mutually_exclusive_items'] if u!=uid)+'.')
 return out
def row(uid,category,summary,cost=None):
 return dict(id=uid,name=c.name('item',uid),cost=c.num('item',uid,'igol') if cost is None else cost,lumber=c.num('item',uid,'ilum'),category=category,shops=[s['id'] for s in shops if uid in s['items']],summary=c.plain(summary),details=[],abilities=[c.ability(a) for a in c.abil_list(uid)],evidence=['war3map.w3t + war3mapSkin.w3t: '+uid+'; war3map.w3a + war3mapSkin.w3a; inherited custom_v1 game data.'])
def finish(x,tip,reason):
 uid=x['id'];extra=restrictions(uid);x['details']+=extra;tip+='|n|n'+' '.join(extra) if extra else ''
 sx=script_items.get(uid)
 if sx:
  x['details']+=sx['effects']
  if sx.get('qualification'):x['details'].append(sx['qualification'])
  x['evidence'] += ['source.j:'+str(e['line'])+' '+e['function'] for e in sx['evidence']]
  existing={a['id'] for a in x['abilities']}
  x['abilities'] += [c.ability(a,all_levels=(a=='A06B')) for a in sx['abilities'] if a not in existing]
  # Full scripted behavior also belongs on the actual item tooltip.
  tip+='|n|nScripted effects: '+' '.join(sx['effects'])
  if sx.get('qualification'):tip+='|n'+sx['qualification']
 if tip:
  tip=tip.replace('\n','|n').encode('ascii','replace').decode()
  patches[uid]={'utub':tip,'ides':tip}
  ch=dict(id=uid,name=x['name'],before=c.plain(c.value('item',uid,'utub') or ''),after=c.plain(tip),reason=reason)
  changes.append(ch);x['changes']=[ch]
 art=c.value('item',uid,'iico')
 if x['category']=='Spell purchase':art=c.value('ability',x['abilities'][0]['id'],'aart')
 if art:
  art=art.split(',')[0].strip('"')
  try:
   data=c.archive(art) or c.gd.game_read('war3.w3mod:'+art)
   im=Image.open(io.BytesIO(data)).convert('RGBA');im.thumbnail((96,96));im.save(dist/'icons'/f'{uid}.png');x['icon']=f'icons/{uid}.png'
  except Exception as e:icon_errors.append([uid,art,str(e)])
 items.append(x)
for uid in sorted(live):
 if uid in equip:
  e=equip[uid];summary=e['summary']
  if uid=='oven':summary='+10 attack damage. '+summary
  x=row(uid,'Equipment',summary)
  reasons=[s for s in e['mismatches'] if 'parser' not in s.lower()]
  finish(x,summary,' '.join(reasons) or 'Verified numerical description and actual pickup restrictions.')
 elif uid in SUMMARIES:
  x=row(uid,'Equipment' if uid in ['stel','desc'] else 'Consumable',SUMMARIES[uid]);parts=[]
  charges=c.num('item',uid,'iuse')
  parts.append(f'{int(charges)} charge(s).' if charges else 'Reusable; no charge consumption.')
  for a in c.abil_list(uid):
   cd=c.num('ability',a,'acdn',1);mana=c.num('ability',a,'amcs',1)
   if cd or mana:parts.append(f'{c.name("ability",a)}: cooldown {cd:g} seconds; mana cost {mana:g}.')
  x['details']+=parts
  finish(x,SUMMARIES[uid]+'|n'+' '.join(parts),REASONS.get(uid,'Verified actual ability values, charges and scripted behavior.'))
 elif uid in recipes:
  r=recipes[uid];x=row(uid,'Recipe','Recipe for '+r['result_name']+'. '+r['recipe_passive']+' Crafted result: '+r['summary'])
  x['recipe']=dict(ingredients=[dict(id=i['id'],name=i['name'],cost=i['gold']) for i in r['ingredient_list']],result=dict(id=r['result']['id'],name=r['result_name']),totalCost=r['total_gold'])
  x['evidence']+=r['evidence'];finish(x,r['suggested_recipe_tooltip'],' '.join(r['mismatches']) or 'Verified recipe components, complete acquisition cost and crafted abilities.')
 else:
  x=row(uid,'Information',c.plain(c.value('item',uid,'utub') or 'Map information entry.'))
  x['details'].append('Information/menu item, not combat equipment.');items.append(x)
for uid,r in results.items():
 x=row(uid,'Crafted',r['summary'],r['total_gold']);x['details'].append('Crafted result; displayed cost is total recipe plus ingredient acquisition cost. Not sold directly.');x['evidence']+=r['evidence']
 x['recipe']=dict(ingredients=[dict(id=i['id'],name=i['name'],cost=i['gold']) for i in r['ingredient_list']]+[dict(id=r['recipe_id'],name=r['recipe_name'],cost=r['recipe_gold'])],result=dict(id=uid,name=r['result_name']),totalCost=r['total_gold'])
 finish(x,r['suggested_result_tooltip'],' '.join(r['mismatches']) or 'Verified crafted result abilities and script.')
x=row('I001','Starting item','+150 health, +100 mana and +80 movement speed.',0);x['details'].append('Granted starting amulet; not a shop purchase. Included because recipes consume it.');finish(x,x['summary'],'Made starting recipe ingredient bonuses explicit.')
skip={'aher','aite','arac','apri','alev','arlv','alsk','alcp','abuf','aeff','areq'}
for t in reach['dynamic']['tokens']:
 a=c.ability(t['ability']);fields=[f for f in a['fields'] if f['raw'] not in skip]
 desc='; '.join(f['label']+': '+str(round(f['value'],6) if isinstance(f['value'],float) else f['value']) for f in fields)+'.'
 summary=f"Teaches {a['name']} ({a['id']}) at level 1 in slot {t['slot_name']}. "+desc
 x=row(t['id'],'Spell purchase',summary);x['abilities']=[a];x['shops']=['CH'+str(t['shop_slot'])];x['details']+=reach['dynamic']['rules']
 x['evidence']+=['source.j: FFCH_InitCatalog, FFCH_BuildArea and FFCH_OnSell; level 1 only.']
 finish(x,summary+'|nCustom Hero mode only. Buy within 45 seconds. One ability per slot; one copy of each ability per team.'+(' Only one Z AoE per team.' if t['z_aoe'] else ''),'Replaced inherited mana-potion description with the purchased spell and its level-1 values.')
 patches[t['id']]['utip']='Learn '+x['name']+' ['+t['slot_name']+']'
for n in range(1,9):shops.append(dict(id='CH'+str(n),name='Custom Hero spell shop '+str(n),items=[t['id'] for t in reach['dynamic']['tokens'] if t['shop_slot']==n]))
notes=['Complete static audit of the original v10 map: 108 unique fixed-stock entries (including 3 information entries), 96 mode-specific spell purchases, 17 crafted results and 1 starting ingredient. Sorted by gold; crafted entries show complete acquisition cost.',
 'Truth sources are attached abilities, numeric object fields, custom_v1 inherited game data and JASS handlers. Original tooltip text is comparison material only. Ability field tables preserve raw IDs, levels and provenance; fractions in raw fields are engine values (for example 0.2 = 20%).',
 'All 17 sold recipes were traced through their combination triggers. The starting amulet is free; recipe cost is distinguished from complete component cost.',
 'Seven dormant shop types and undefined stock ID I032 are excluded from sold inventory. Hidden Ninja recipe I00P and inactive Guardian recipe I02W are not sold by reachable shops.',
 'Custom Hero shops exist for 45 seconds with 1000 starting gold. Their 96 script-added tokens are listed; n000 also retains its 11 normal stock entries. In-game command-card visibility requires playtesting.',
 'Static source verification is complete; no Warcraft match was run. Engine stacking, movement-speed caps and runtime command-card behavior are not experimentally verified. Purification corpse-removal has a documented script bug; gameplay was preserved.',
 'Only item text was changed in the patched map. Numerical abilities, recipes, prices, triggers, terrain and units are unchanged. The change log includes expanded/normalized descriptions as well as factual corrections.']
items.sort(key=lambda x:(x['cost'],x['name'],x['id']))
data=dict(meta=dict(title='799X Item Wiki',sourceMap=c.MAP.name,sourceSha256=hashlib.sha256(c.MAP.read_bytes()).hexdigest(),summary=notes[0]),items=items,shops=shops,changes=changes,notes=notes)
assert len(items)==222 and len({x['id'] for x in items})==222
(dist/'data.json').write_text(json.dumps(data,indent=2,ensure_ascii=True),encoding='utf-8')
(dist/'data.js').write_text('window.WIKI_DATA = '+json.dumps(data,ensure_ascii=True)+';',encoding='utf-8')
lines=['# 799X complete cost-sorted item list','',*notes,'','| Gold | Item | Type | Actual stats and abilities |','|---:|---|---|---|']
for x in items:lines.append('| '+str(int(x['cost']))+' | '+x['name']+' ('+x['id']+') | '+x['category']+' | '+(x['summary']+' '+' '.join(x['details'])).replace('|','/').replace('\n',' ')+' |')
(dist/'complete-list.md').write_text('\n'.join(lines),encoding='utf-8')
# Patch both layers where a text field already exists, and the skin layer for all new text.
out=c.ROOT/'final';out.mkdir(exist_ok=True)
diff=[]
for fn in ['war3map.w3t','war3mapSkin.w3t']:
 original=c.objdata.load(str(c.ROOT/('extracted'+fn[len('war3map'):])));obj=copy.deepcopy(original)
 index={(e['newId'] if e['newId']!='\0'*4 else e['oldId']):e for tab in obj['tables'] for e in tab}
 for uid,fields in patches.items():
  e=index.get(uid)
  if e is None and 'Skin' not in fn:continue
  if e is None:
   parent=c.parents.get(('item',uid),uid);custom=parent!=uid
   e=dict(oldId=parent,newId=uid if custom else '\0'*4,flags=1,extra=0,mods=[]);obj['tables'][int(custom)].append(e)
  for field,value in fields.items():
   m=next((m for m in e['mods'] if m['id']==field),None)
   if m is None and 'Skin' not in fn:continue
   before=m['value'] if m else None
   if m:m['value']=value
   else:e['mods'].append(dict(id=field,type=3,value=value,end=uid.encode('latin1').hex()))
   if before!=value:diff.append(dict(file=fn,id=uid,field=field,before=before,after=value))
 payload=c.objdata.dump(obj);(out/fn).write_bytes(payload);assert c.objdata.dump(c.objdata.load(str(out/fn)))==payload
 # Independent normalized comparison proves every preexisting non-text field is identical.
 def nontext(o):return {(e['oldId'],e['newId'],m['id']):m for tab in o['tables'] for e in tab for m in e['mods'] if m['id'] not in ['utub','ides','utip']}
 assert nontext(original)==nontext(obj)
(out/'text-changes.json').write_text(json.dumps(diff,indent=2),encoding='utf-8')
(out/'build-summary.json').write_text(json.dumps(dict(entries=len(items),fixedShopEntries=len(live),recipes=len(recipes),dynamicSpells=96,itemsWithTextUpdates=len(patches),textFieldsUpdated=len(diff),icons=len(items)-len(icon_errors)-3,iconErrors=icon_errors),indent=2),encoding='utf-8')
print((out/'build-summary.json').read_text())
