exec(compile(open('shared-sync-v85/inspect.py',encoding='utf8').read().split('selected=')[0],'setup','exec'))
for n in ['s__Missiles___Pool_onExpire','Trig_HERO_Grim_Ulti_Actions','Trig_HERO_Summon_Brewer_Stats_Actions','Trig_ITEM_limits_Actions','Trig_HERO_Blooddancer_Bloodrush_Actions','Trig_colossal_spawn_Actions']:
 if n in s and n in m:
  if n=='Trig_ITEM_limits_Actions':print(s[n]);continue
  if n=='Trig_colossal_spawn_Actions':continue
  print(n);print(''.join(difflib.unified_diff(m[n].splitlines(True),s[n].splitlines(True))))
