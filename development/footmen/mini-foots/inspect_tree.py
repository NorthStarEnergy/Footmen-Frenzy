exec(open('mini-foots/inspect_objects.py').read().split("for ext in")[0])
d=objdata.load(str(root/'war3map.w3u')); es={e['newId'] if e['newId']!='\0'*4 else e['oldId']:e for t in d['tables'] for e in t}
seen=set()
def walk(id,depth):
 if id in seen:return
 seen.add(id);m={m['id']:text(m['value']) for m in es[id]['mods']}
 print(' '*depth,id,'req',m.get('ureq'),'to',m.get('uupt'))
 for c in m.get('uupt','').split(','):
  if c in es:walk(c,depth+1)
walk('hbar',0)
