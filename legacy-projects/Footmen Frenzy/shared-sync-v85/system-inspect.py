exec(compile(open('shared-sync-v85/inspect.py',encoding='utf8').read().split('selected=')[0],'setup','exec'))
def clean(x):
 return re.sub(r'\s+','',re.sub(r'//[^\n]*','',x))
out=[]
for n in m:
 if n in s and clean(m[n])!=clean(s[n]) and (n.startswith(('Trig_HERO_','Trig_ITEM_','Trig_UNIT_','Trig_Architect','Trig_Thunder','Trig_Hammer','Trig_Mirror','Trig_Searing','Trig_Cripple','Trig_Staff')) or re.search(r'stale|captured up front|across.*wait|locals.*wait|snapshot',m[n],re.I)):
  diff=[l for l in difflib.ndiff(m[n].splitlines(),s[n].splitlines()) if l.startswith(('+ ','- '))]
  out.append({'name':n,'lines':len(diff),'main_locals':len(re.findall(r'\blocal ',m[n])),'solo_locals':len(re.findall(r'\blocal ',s[n])),'diff':'\n'.join(diff)})
(R/'systems-diffs.json').write_text(json.dumps(out,indent=2));print('\n'.join(f"{o['name']} lines={o['lines']} locals 799X={o['main_locals']} Solo={o['solo_locals']}" for o in out))
