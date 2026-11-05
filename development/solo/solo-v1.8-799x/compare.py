import sys,re,collections,json
from pathlib import Path
sys.path.insert(0,'../Footmen Frenzy/hero-polish')
from archive_helpers import functions
r=Path('solo-v1.8-799x'); b=functions((r/'base/war3map.j').read_text(encoding='cp1252'));d=functions((r/'donor/war3map.j').read_text(encoding='utf-8-sig'))
norm=lambda x:re.sub(r'\s+','',re.sub(r'//[^\n]*','',x))
changed=[n for n in b if n in d and norm(b[n])!=norm(d[n])]
(r/'shared-differences.json').write_text(json.dumps(changed,indent=2))
print(len(changed));print('\n'.join(changed))
for n in ['FF_HeroTooltips_Init','FF_CompactHeroTooltips_Init']: print(d[n][:3000])
