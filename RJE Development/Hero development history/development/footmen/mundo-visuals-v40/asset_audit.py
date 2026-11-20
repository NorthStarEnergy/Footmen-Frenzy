from pathlib import Path
import sys,re,json,struct
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'mini-foots/tools'),str(W/'hero-polish')]
from game_data import game_read,chunks
from archive_helpers import storm,read_storm,c
import objdata
paths=[r'Abilities\Spells\Undead\UnholyFrenzy\UnholyFrenzyTarget.mdx',r'Objects\Spawnmodels\Human\HumanBlood\HumanBloodLarge0.mdx',r'Abilities\Spells\Undead\DeathCoil\DeathCoilSpecialArt.mdx',r'Abilities\Spells\Orc\Bloodlust\BloodlustTarget.mdx',r'buildings\other\CircleOfPower\CircleOfPower.mdx']
for p in paths:
 data=game_read('war3.w3mod:'+p);assert data and data[:4]==b'MDLX',p
 print(p,len(data))
h=c.c_void_p();assert storm.SFileOpenArchive(str(W/'799x-backport/release/FF799X_Rx_Consolidated_Clean_v39.w3x'),0,0x100,c.byref(h))
model=read_storm(h,r'war3mapImported\HeroAbomination.mdx');print('Mundo attachments:',re.findall(rb'(?:hand|chest|origin|head)[^\0]{0,24}',model))
p=R/'base.w3u';p.write_bytes(read_storm(h,'war3map.w3u'));assert storm.SFileCloseArchive(h)
u=objdata.load(str(p));e=next(e for t in u['tables'] for e in t if e['newId']=='HMu1');print('Mundo abilities:',[(m['id'],m['value']) for m in e['mods'] if m['id'] in ['uabi','uhab']])
a=objdata.load(str(R/'src/war3map.w3a'))
print('Existing Mundo positions:',{e['newId']:{m['id']:m['value'] for m in e['mods'] if m['id'] in ['abpx','abpy','ahky']} for t in a['tables'] for e in t if e['newId'].startswith('AMu')})
(R/'assets/asset-verification.json').write_text(json.dumps(dict(built_in_models_verified=paths,custom_model_search='Igneous Cleaver by Solu9 / Epimetheus found at https://www.hiveworkshop.com/threads/igneous-cleaver.274500/ ; download blocked by Cloudflare. Existing Axe Missile-Small retained and enlarged.',icons='Generated via imagegen; standard Button Manager active/disabled frames; BLP1 mipmaps.'),indent=2))

