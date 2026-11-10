exec(open('solo-v1.8-799x/compare.py').read().split('print(len(changed))')[0])
import difflib
out=[]
for n in changed:
 if not n.startswith(('Trig_HERO_','Trig_ITEM_','Trig_UNIT_','Trig_Thunder','Trig_Axe','Trig_Hammer','Trig_Summon','Trig_Mirror','Trig_Medivh','Trig_Searing','Trig_Cripple')):continue
 diff=[x for x in difflib.ndiff(b[n].splitlines(),d[n].splitlines()) if x.startswith(('+ ','- '))]
 if len(diff)<16:out.append(n+'\n'+'\n'.join(diff))
print('\n\n'.join(out))
