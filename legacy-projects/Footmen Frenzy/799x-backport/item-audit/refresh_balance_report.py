import balanced_core as c
import json,copy,re,shutil,base64
from pathlib import Path
DIST=c.PROJECT/'item-wiki/dist';OUT=c.ROOT/'balance-v41'
changes=json.loads((OUT/'balance-changes.json').read_text())
data=json.loads((DIST/'data.json').read_text(encoding='utf-8'));model=json.loads((DIST/'item-value-model.json').read_text(encoding='utf-8'))
for name in ['data.json','item-value-model.json']:
 if not (OUT/('report-before-'+name)).exists():shutil.copyfile(DIST/name,OUT/('report-before-'+name))
data=json.loads((OUT/'report-before-data.json').read_text(encoding='utf-8'));model=json.loads((OUT/'report-before-item-value-model.json').read_text(encoding='utf-8'))
P={x['id']:x for x in changes['prices']};C={x['id']:x for x in changes['craftedCosts']}
def fixtext(text):return text.replace('+160 attack damage (150 damage ability plus 10 from frost orb)','+150 attack damage (140 damage ability plus 10 from frost orb)').replace('60% melee life steal','50% melee life steal')
def update_item(i):
 uid=i['id']
 if uid in P:i['cost']=P[uid]['after']
 if uid in ['I00W','I00K']:
  i['summary']=fixtext(i['summary']);i['details']=[fixtext(t) for t in i.get('details',[])]
 if i.get('recipe'):
  r=i['recipe'];res=r['result']['id']
  for part in r['ingredients']:
   if part['id'] in P:part['cost']=P[part['id']]['after']
  if res in C:r['totalCost']=C[res]['after']
 if uid=='I00W':i.setdefault('details',[]).append('v41 balance: total cost 4500g, +150 attack damage and 50% self-only melee lifesteal. The separately attached frost orb still supplies +10 of that damage.')
 if uid in C:i.setdefault('details',[]).append(f"v41 complete acquisition cost: {C[uid]['before']}g to {C[uid]['after']}g; recipe {C[uid]['recipeBefore']}g to {C[uid]['recipeAfter']}g.")
for i in data['items']:
 update_item(i)
 if i['id']=='I00W':i['abilities']=[c.ability(a) for a in c.abil_list('I00W')]+[c.ability('A06R')]
 if i['id'] in P or (i.get('recipe') and i['recipe']['result']['id'] in C):
  ch=dict(id=i['id'],name=i['name'],before=c.plain(next((m['before'] for m in changes['edits'] if m['id']==i['id'] and m['field']=='utub'),i['summary'])),after=c.plain(c.value('item',i['id'],'utub')),reason='v41 user-requested balance changes; recipe and ingredient totals reconciled.')
  i.setdefault('changes',[]).append(ch);data['changes'].append(ch)
data['items'].sort(key=lambda i:(i['cost'],i['name'],i['id']))
data['meta'].update(sourceMap=c.MAP.name,sourceSha256=changes['outputSha256'],patchedMap=c.MAP.name,patchedSha256=changes['outputSha256'],balanceChanges=changes['prices'])
data['notes']=[n for n in data['notes'] if 'Only item text was changed' not in n]
data['notes'].append('v41 applies the requested item-price changes and Frosty damage/lifesteal nerfs on top of v40. Chaos Cloak rises by 500g in actual ingredient+recipe cost (3350g to 3850g); the old result object had a stale 3500g valuation. Other map archive members are preserved.')
newrates={'str':27.5,'as':13.75,'armor':23,'damage':13,'evade':16,'cleave':15}
formulas={'str':'275 / 10 = 27.5','as':'275 / 20 = 13.75','armor':'(225 − 4 STR × 27.5) / 5 armor = 23','damage':'325 / 25 = 13','evade':'400 / 25 = 16','cleave':'900 / 60 = 15; reference only at 200 area'}
for r in model['rates']:
 if r['key'] in newrates:r['rate']=newrates[r['key']];r['formula']=formulas[r['key']]
R={r['key']:r for r in model['rates']}
for i in model['items']:
 update_item(i)
 if i['id']=='I00W':
  for t in i['terms']:
   if t['ability']=='A0KF':t['quantity']=140
   if t['ability']=='A0B9':
    t.update(ability='AFv1',quantity=50,note='v41 self-only lifesteal; personal-lifesteal benchmark, melee eligibility retained.')
 for t in i['terms']:t['rate']=R[t['key']]['rate'];t['gold']=t['quantity']*t['rate']
 i['coreGold']=sum(t['gold'] for t in i['terms'] if t['core']);i['referenceGold']=sum(t['gold'] for t in i['terms']);i['residual']=i['cost']-i['referenceGold'];i['coveragePercent']=100*i['referenceGold']/i['cost'] if i['cost'] else None
byid={i['id']:i for i in model['items']}
for i in model['items']:
 if i.get('recipe') and i['category']=='Crafted':
  i['ingredientReferenceGold']=sum(byid[x['id']]['referenceGold'] for x in i['recipe']['ingredients']);i['combineStatGainGold']=i['referenceGold']-i['ingredientReferenceGold']
model['sourceMap']=c.MAP.name;model['sourceSha256']=changes['outputSha256'];model['heroSourceMap']='FF799X_Rx_Consolidated_StatsUI_v37.w3x'
model['notes']=[n for n in model['notes'] if 'Armor has no pure baseline' not in n and 'Latest v37 item prices' not in n]
model['notes']+=['v41 baseline prices updated: STR 27.5g, attack speed 13.75g per percentage point, armor 23g, flat damage 13g, evasion 16g per point, cleave 15g per point. Armor uses (225−4×27.5)/5; Medaillon still implies 12.5g per armor.',data['notes'][-1],'Hero cleave findings remain the separately dated v37 audit. This report update concerns v41 item prices and Frosty; it does not re-audit later hero changes.']
model['balanceChanges']=changes['prices'];model['craftedCostChanges']=changes['craftedCosts']
for name,obj in [('data.json',data),('item-value-model.json',model)]: (DIST/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
(DIST/'data.js').write_text('window.WIKI_DATA='+json.dumps(data)+';',encoding='utf-8')
(c.ROOT/'item-value-model.json').write_text(json.dumps(model,indent=2),encoding='utf-8')
shutil.copyfile(c.MAP,DIST/c.MAP.name)
shutil.copyfile(OUT/'balance-changes.json',DIST/'balance-changes.json')
index=DIST/'index.html';html=index.read_text(encoding='utf-8');html=re.sub(r'href="FF799X_[^"]+\.w3x"',f'href="{c.MAP.name}"',html);index.write_text(html,encoding='utf-8')
embedded=copy.deepcopy(data)
for i in embedded['items']:
 if i.get('icon'):i['icon']='data:image/png;base64,'+base64.b64encode((DIST/i['icon']).read_bytes()).decode()
html=html.replace('<link rel="stylesheet" href="styles.css">','<style>'+(DIST/'styles.css').read_text(encoding='utf-8')+'</style>').replace('<script defer src="data.js"></script>','').replace('<script defer src="app.js"></script>','')
html=html.replace('</body>','<script>window.WIKI_DATA='+json.dumps(embedded).replace('</','<\\/')+';</script><script>'+(DIST/'app.js').read_text(encoding='utf-8')+'</script></body>')
html=html.replace(f'href="{c.MAP.name}"',f'href="../release/{c.MAP.name}"').replace('href="item-values.html"','href="799X-Item-Value-Lab.html"')
for fn in ['complete-list.md','data.json','validation.json']:html=html.replace(f'href="{fn}"',f'href="dist/{fn}"')
(c.PROJECT/'item-wiki/Footmen-Frenzy-799X-Item-Wiki.html').write_text(html,encoding='utf-8')
assert c.num('ability','A0KF','Iatt',1)==140
assert c.num('ability','AFv1','Uav1',1)==.5
assert abs(c.num('ability','A0B9','Uav1',1)-.6)<.00001
for p in changes['prices']:assert c.num('item',p['id'],'igol')==p['after']
for r in changes['craftedCosts']:
 assert byid[r['id']]['cost']==r['after']
 assert sum(x['cost'] for x in byid[r['id']]['recipe']['ingredients'])==r['after']
for uid in ['bgst','belv','ciri','prvt','pmna','I03C','brac','rde3','rlif','rwiz','ratf','evtl','modt','stwa','crys','ward']:assert abs(byid[uid]['referenceGold']-byid[uid]['cost'])<.01,uid
print('PASS: patched archive prices/abilities, complete crafted totals, 16 re-priced model anchors; 222 report entries updated.')
