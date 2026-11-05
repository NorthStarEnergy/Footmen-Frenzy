import json
from pathlib import Path
r=json.loads(Path('shared-sync-v85/systems-diffs.json').read_text())
for x in r:
 if x['lines']<=50:print(x['name']+'\n'+x['diff']+'\n')
