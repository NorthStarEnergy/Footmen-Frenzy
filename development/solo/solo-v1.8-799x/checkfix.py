exec(open('solo-v1.8-799x/compare.py').read().split('print(len(changed))')[0])
import difflib
for n in ['MF_SetAttackRange','Trig_HERO_Architect_Recruit_Actions']:
 print(n);print(d[n] if n not in b else '\n'.join(difflib.unified_diff(b[n].splitlines(),d[n].splitlines(),n=2)))
