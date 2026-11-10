from pathlib import Path
p=Path('shared-sync-v85/check.py');s=p.read_text().replace('import sys,re,ast,json,math','import sys,re,ast,json,math,itertools')
s=s.replace('def item_env(v):','def item_env(v,combo=False):')
s=s.replace("if n.startswith(('Trig_ITEM_limits','ItemLimit_'))", "if n.startswith(('Trig_ITEM_combo_limits','ItemCombo_','ItemLimit_') if combo else ('Trig_ITEM_limits','ItemLimit_'))")
s=s.replace('def run(t,h,count):','def run(t,h,count,inventory=None):').replace("inventory=[(t,i) for i in range(count)]","inventory=[(x,i) if x else None for i,x in enumerate(inventory)] if inventory is not None else [(t,i) for i in range(count)]")
s=s.replace("e['Trig_ITEM_limits_Actions']()","e['Trig_ITEM_combo_limits_Actions' if combo else 'Trig_ITEM_limits_Actions']()")
anchor='# Creep caps preserve all 15 rawcodes and unrestricted fast path.'
s=s.replace(anchor,'''oldcombo,newcombo=item_env('old',True),item_env('main',True)
for t in ['rag1','hval','evtl','zzzz']:
 for tail in itertools.product(['rag1','hval','evtl','zzzz',None],repeat=5):
  inv=[t]+list(tail)
  a,b=oldcombo(t,'H043',1,inv),newcombo(t,'H043',1,inv);assert a==b,(inv,a,b);cases+=1
check('Item combination rules match original for mixed six-slot inventories',True)
'''+anchor)
p.write_text(s)
