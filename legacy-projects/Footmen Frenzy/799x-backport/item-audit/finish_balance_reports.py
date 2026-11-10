from pathlib import Path
import json,base64,copy
ROOT=Path(__file__).resolve().parents[2]
AUD=Path(__file__).parent
W=ROOT/'799x-backport/item-wiki'
D=W/'dist'
p=AUD/'build_static_report.py'
s=p.read_text(encoding='utf-8')
s=s.replace('(200g − 4 STR × 25g) ÷ 5 = <b>20g per armor','(225g − 4 STR × 27.5g) ÷ 5 = <b>23g per armor')
s=s.replace('160 damage × 12g = 1,920g; 20% attack speed × 12.5g = 250g; 60% lifesteal × 7.5g = 450g. Expanded subtotal: <b>2,620g</b>. Its frost effects and aura coverage remain unpriced. That does not establish that 4,000g','150 damage × 13g = 1,950g; 20% attack speed × 13.75g = 275g; 50% self-only lifesteal × 7.5g = 375g. Expanded subtotal: <b>2,600g</b>. Its frost effects remain unpriced. That does not establish that 4,500g')
s=s.replace("fields from '+e(model['sourceMap'])", "fields from '+e(model.get('heroSourceMap',model['sourceMap']))")
s=s.replace('Item stat values and sold-recipe functions were compared between the v10 audit and v37. This report makes no gameplay edits.','The v41 release applies the requested prices and Frosty damage/lifesteal changes to v40. All 1,333 unrelated archive members were preserved. Recipe totals and all 16 price benchmarks were checked. No live game playtest was performed.')
s=s.replace('This report corrects that description; it does not regenerate a map release.','The item data and prices in this report reflect the v41 map release. Hero findings retain their separately identified v37 source.')
marker="out.append('<div class=\"metrics\">'"
pos=s.index(marker)
section='''out.append('<section id="balance"><h2>Applied v41 balance changes</h2><p>Crafted totals include all ingredients and the recipe. Chaos Cloak is exactly +500g overall: gauntlets +250g, cloak +100g, recipe +150g. Frosty now gives +150 total damage and 50% self-only melee lifesteal. Blink scepter’s recipe rises by 500g, plus 25g from its belt ingredient.</p>')
crafted_ids={x['id'] for x in model['craftedCostChanges']}
out.append(table(['Shop item / recipe','Before','Now','Increase'],[(e(x['name']),f(x['before'])+'g',f(x['after'])+'g','+'+f(x['after']-x['before'])+'g') for x in model['balanceChanges'] if x['id'] not in crafted_ids]))
out.append('<h3>Complete crafted costs, including ingredient knock-ons</h3>'+table(['Crafted item','Before total','Now total','Increase','Recipe now'],[(e(by['name']),f(x['before'])+'g',f(x['after'])+'g','+'+f(x['after']-x['before'])+'g',f(x['recipeAfter'])+'g') for x in model['craftedCostChanges'] for by in [next(i for i in items if i['id']==x['id'])]])+'<p>The old Chaos Cloak result object listed 3,500g, but its actual component cost was 3,350g. Its new complete purchase cost is 3,850g.</p></section>')
'''
if 'id="balance"' not in s:s=s[:pos]+section+s[pos:]
p.write_text(s,encoding='utf-8')
model=json.loads((D/'item-value-model.json').read_text())
data=json.loads((D/'data.json').read_text())
changes=json.loads((AUD/'balance-v41/balance-changes.json').read_text())
validation={'map':changes['outputMap'],'sha256':changes['outputSha256'],'unchangedArchiveMembers':1333,'changedMembers':['war3map.w3t','war3mapSkin.w3t','war3map.w3a','war3mapSkin.w3a'],'checks':['Object round-trip and permitted field edits','All changed prices and complete recipe totals','Frosty damage 140 plus orb 10; dedicated lifesteal ability 50%; original shared ability 60%','16 baseline anchors reconstruct prices'],'livePlaytest':False}
(D/'validation.json').write_text(json.dumps(validation,indent=2))
data['meta']['validation']='v41: prices, recipe totals, Frosty actual ability values and preservation of 1333 unrelated archive members verified; no live playtest.'
(D/'data.json').write_text(json.dumps(data,indent=2))
(D/'data.js').write_text('window.WIKI_DATA='+json.dumps(data)+';',encoding='utf-8')
lines=['# 799X v41 complete cost-sorted item catalogue','','Crafted prices are full ingredient + recipe costs.','','| Gold | Item | Type | Abilities and stats |','|---:|---|---|---|']
for i in sorted(data['items'],key=lambda i:(i['cost'],i['name'])):lines.append('| '+str(i['cost'])+' | '+i['name']+' | '+i['category']+' | '+i['summary'].replace('|','/').replace('\n',' ')+' |')
(D/'complete-list.md').write_text('\n'.join(lines),encoding='utf-8')
t=W/'value-template.html';s=t.read_text(encoding='utf-8').replace('from the latest v37 map','from the separately dated v37 hero audit').replace('Local analysis only. No item prices, hero abilities or gameplay were changed.','Item values reflect the v41 balance release. Hero findings retain the v37 audit source.').replace(' · item prices and ability fields match the audited v10 inventory.',' · updated item prices, recipe totals and Frosty ability values.')
t.write_text(s,encoding='utf-8')
embed=copy.deepcopy(model)
for i in embed['items']:
 if i.get('icon') and not i['icon'].startswith('data:'):i['icon']='data:image/png;base64,'+base64.b64encode((D/i['icon']).read_bytes()).decode()
s=s.replace('/*MODEL*/','const MODEL='+json.dumps(embed).replace('</','<\\/')+';')
(W/'799X-Item-Value-Lab.html').write_text(s,encoding='utf-8');(D/'item-values.html').write_text(s,encoding='utf-8')
p=W/'verify-values.cjs';s=p.read_text().replace("includes('535')","includes('559')").replace("includes('250g')","includes('275g')").replace("includes('2,170')","includes('2,225')");p.write_text(s)
print('Report sources, value lab, catalogue and validation updated.')
