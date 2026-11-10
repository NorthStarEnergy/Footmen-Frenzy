exec(open('mini-foots/inspect_objects.py').read().split("for ext in")[0])
import json
d=objdata.load(str(root/'war3map.w3u'));es={e['newId'] if e['newId']!='\0'*4 else e['oldId']:e for t in d['tables'] for e in t}
for id in json.load(open('mini-foots/changes.json'))['creeps']:
 e=es.get(id,{});print(id,e.get('oldId'),[(m['id'],m['value']) for m in e.get('mods',[]) if m['id'] in ['ugol','ulum','ulbd','ulba','ulbs','ulpx']])
