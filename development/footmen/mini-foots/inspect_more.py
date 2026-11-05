exec(open('mini-foots/inspect_objects.py').read().split("for ext in")[0])
d=objdata.load(str(root/'war3map.w3u'))
for tab in d['tables']:
 for e in tab:
  id=e['newId'] if e['newId']!='\0'*4 else e['oldId']
  if id in ['hbar','h013','h00O','h002','n003','n00R','n02U']: print(id,[(m['id'],text(m['value'])) for m in e['mods'] if m['type']==3])
