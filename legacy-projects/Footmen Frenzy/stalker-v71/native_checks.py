from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'mini-foots/tools'))
import game_data
assets=json.loads((R/'asset-checks.json').read_text())
paths=assets['native_texture_dependencies']+['Abilities\\Spells\\Items\\SpellShieldAmulet\\SpellShieldCaster.mdx','Abilities\\Spells\\NightElf\\Blink\\BlinkCaster.mdx','Abilities\\Spells\\NightElf\\Blink\\BlinkTarget.mdx','ReplaceableTextures\\CommandButtons\\BTNDefend.blp','ReplaceableTextures\\CommandButtons\\BTNBlink.blp']
report={}
for path in paths:
    candidates=[path]
    if path.endswith('.blp'):candidates.append(path[:-4]+'.dds')
    found=next((p for p in candidates if game_data.game_read('war3.w3mod:'+p)),None)
    assert found,('Missing native dependency',path)
    report[path]=found
(R/'native-checks.json').write_text(json.dumps(report,indent=2));print(f'{len(report)} native dependencies verified in the installed game storage.')
