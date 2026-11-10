"""Verify the displayed rank values and the final runtime tooltip overrides."""
from pathlib import Path
import sys,re,ast
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'mini-foots/tools'));import objdata
s=(R/'src/war3map.j').read_text(encoding='utf8');funcs={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
a={e['newId']:e for t in objdata.load(str(R/'src/war3map.w3a'))['tables'] for e in t}
ids=['A0DL','AFg1','ATfd','AZd1','AOz1','AOz2','AOz3','AOz4','AGr1','AGr2','AGr3','AGr4']
def v(e,k,l=0):return next(m['value'] for m in e['mods'] if m['id']==k and m['level']==l)
def plain(s):return re.sub(r'\|c[0-9a-fA-F]{8}|\|r','',s).replace('|n','\n')
runtime=funcs['FF_CompactHeroTooltips_Init'];init=funcs['InitTrig_FF_Runtime'];assert init.index('call OM_Init()')<init.index('call TFP_Init()')<init.index('call FF_CompactHeroTooltips_Init()')
expected_names=['BlzSetAbilityExtendedTooltip','BlzSetAbilityTooltip','BlzSetAbilityResearchExtendedTooltip','BlzSetAbilityResearchTooltip']
for uid in ids:
 e=a[uid];ranks=v(e,'alev');hotkey=v(e,'ahky');learnkey=v(e,'arhk')
 for rank in range(1,ranks+1):
  text=v(e,'aub1',rank);title=v(e,'atp1',rank)
  assert text.count('|c')==text.count('|r') and len(text)<900,(uid,rank)
  assert '|cffffcc00' in text and '|cff80dfff' in text
  assert '['+hotkey+']' in plain(title) and 'Level '+str(rank) in plain(title)
  for name in expected_names:
   lines=[x for x in runtime.splitlines() if name+"('"+uid+"'" in x and x.endswith(', '+str(rank-1)+')')]
   assert len(lines)==1,(uid,rank,name)
  active=next(x for x in runtime.splitlines() if "BlzSetAbilityExtendedTooltip('"+uid+"'" in x and x.endswith(', '+str(rank-1)+')'))
  research=next(x for x in runtime.splitlines() if "BlzSetAbilityResearchExtendedTooltip('"+uid+"'" in x and x.endswith(', '+str(rank-1)+')'))
  assert '"'+text+'"' in active and text in research
  assert 'Requires hero level '+str(v(e,'arlv')+(rank-1)*v(e,'alsk')) in research
  if uid not in ['AFg1','AZd1']:
   assert 'Mana: '+str(v(e,'amcs',rank)) in plain(text),(uid,rank,'mana')
   cd=v(e,'acdn',rank);expected=str(int(cd)) if cd==int(cd) else str(cd)
   assert 'Cooldown: '+expected+' sec' in plain(text),(uid,rank,'cooldown')
 assert '['+learnkey+']' in plain(v(e,'aret'))
 assert plain(v(e,'arut')).startswith('Requires hero level ')
# Compute the gameplay rank values directly from the map's functions, not the tooltip templates.
namespace=dict(re=re,functions=funcs)
for node in ast.parse((W/'799x-backport/check_runtime.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'),namespace)
for name in ['OM_MoveDamage','OM_AttackDamage','OM_ProtectDamage','OM_ProtectHeal','FS_RankDamage','OM_UltimateDamage']:
 exec(namespace['translate'](name),namespace)
for rank in range(1,7):
 for uid,func,label,extra in [('AOz1','OM_MoveDamage','Damage: ',()),('AOz2','OM_AttackDamage','Damage: ',()),('AOz3','OM_ProtectDamage','Travel damage: ',()),('AOz3','OM_ProtectHeal','Arrival heal: ',()),('AGr1','FS_RankDamage','Damage: ',(False,)),('AGr3','FS_RankDamage','Damage: ',(True,))]:
  value=namespace[func](rank,*extra);assert label+str(int(value)) in plain(v(a[uid],'aub1',rank)),(uid,rank,label,value)
 assert 'Damage: '+str(20+10*rank) in plain(v(a['A0DL'],'aub1',rank))
 assert 'Stun: '+format(.25+.25*rank,'g')+' sec' in plain(v(a['A0DL'],'aub1',rank))
 assert 'Shield: '+str(60+40*rank) in plain(v(a['ATfd'],'aub1',rank))
for rank in range(1,4):assert 'Damage: '+str(int(namespace['OM_UltimateDamage'](rank))) in plain(v(a['AOz4'],'aub1',rank))
assert 'Guardian:' in plain(v(a['ATfd'],'aub1',1)) and 'slowed 20% for 1 sec' in plain(v(a['ATfd'],'aub1',1))
assert 'Ramp: +5% power/sec, up to 2x' in plain(v(a['AZd1'],'aub1',1)) and '30 mana/sec' in plain(v(a['AZd1'],'aub1',1))
assert 'Detonate the active barrel' in plain(v(a['AGr8'],'aub1',1))
print('63 active and research ranks, hotkeys, color codes, initialization order, mana/cooldowns and runtime damage/heal values verified.')
