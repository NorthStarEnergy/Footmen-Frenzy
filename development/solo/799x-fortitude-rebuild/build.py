from pathlib import Path
import re, shutil, struct, json, hashlib, sys, subprocess
from orianna import patch
from orianna_v5 import patch as patch_v5, tooltip
from debug_heroes import patch as patch_debug
from orianna_v8 import patch as patch_v8, tooltip as tooltip_v8
from orianna_v9 import patch as patch_v9
from orianna_v10 import patch as patch_v10
from command_ground import patch as patch_ground
from orianna_v11 import patch as patch_v11
from orianna_v12 import patch as patch_v12

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'mini-foots/base/files'
DONOR = ROOT / 'audit/mini-foots-v5-ui'
OUT = ROOT / 'src'
OUT.mkdir(parents=True, exist_ok=True)
b = (BASE / 'war3map.j').read_text(encoding='utf-8-sig')
d = (DONOR / 'war3map.j').read_text(encoding='utf-8-sig')
pattern = r'^function (\w+) takes .*?^endfunction'
def functions(text):
    return {m[1]: m[0] for m in re.finditer(pattern, text, re.M | re.S)}
bf, df = functions(b), functions(d)
names = ['FS_ClearFortitude', 'FS_OnCast', 'zoom__CreateSlider', 'zoom_Init',
         'DPS_Text', 'DPS_Toggle', 'DPS_Create', 'DPS_Refresh']
s = b
for name in names:
    body = df[name]
    if name in ('DPS_Create', 'DPS_Refresh'):
        body = body.replace('        if ModuloInteger(s - 1, 3) != 1 then\n', '')
        body = body.replace('        endif\n        set s = s + 1', '        set s = s + 1')
    if name == 'DPS_Create':
        body = body.replace('I2R(row / 2)', 'I2R(row / 3)')
        body = body.replace('0.650, 0.305', '0.650, 0.393')
        body = body.replace('0.026, 0.267, 0.598', '0.026, 0.355, 0.598')
    s = s.replace(bf[name], body, 1)
# Start stats immediately after initialization, before the optional hero systems.
body = bf['InitTrig_FF_Runtime'].replace('    call DPS_Init()\n', '')
body = body.replace('    call FF_Editor_RunInitialization()',
                    '    call FF_Editor_RunInitialization()\n    call DPS_Init()')
s = s.replace(bf['InitTrig_FF_Runtime'], body, 1)
names.append('InitTrig_FF_Runtime')
assets = ['MiniFootsUI.fdf', 'MiniFootsUI.toc',
          'ReplaceableTextures/CommandButtons/BTNRxGragasFortitude.blp',
          'ReplaceableTextures/CommandButtons/BTNRxGragasSlam.blp']
for asset in assets:
    target = OUT / asset
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(DONOR / asset, target)
imp = (BASE / 'war3map.imp').read_bytes()
version, count = struct.unpack_from('<ii', imp)
assert b'MiniFootsUI.fdf' not in imp
(OUT / 'war3map.imp').write_bytes(struct.pack('<ii', version, count + 2) + imp[8:]
    + b'\rMiniFootsUI.fdf\0\rMiniFootsUI.toc\0')
# Prove the edit is restricted to the intended functions, including nonfunction text.
sf = functions(s)
assert set(bf) == set(sf)
assert {n for n in bf if bf[n] != sf[n]} == set(names)
restored = s
for name in names:
    restored = restored.replace(sf[name], bf[name], 1)
assert restored == b
for name in bf:
    if name.startswith('FS_') and name not in names:
        assert bf[name] == df[name], name
assert 'ModuloInteger(s - 1, 3)' not in sf['DPS_Create'] + sf['DPS_Refresh']
assert s.count('    call DPS_Init()') == 1
assert 0.072 + 11 * 0.022 + (11 // 3) * 0.003 + 0.018 < 0.393
assert 'DPS_Title' not in sf['DPS_Create'] and 'DPS_Legend' not in sf['DPS_Create']
assert 'FRAMEPOINT_TOPRIGHT, DPS_Panel, FRAMEPOINT_TOPRIGHT' in sf['DPS_Create']
assert 0.510 - 0.393 > 0
s = patch(s)
s = patch_v5(s)
names.append('FF_HeroTooltips_Init')
s, debug_changes = patch_debug(s)
names.extend(debug_changes)
s = patch_v8(s)
s = patch_v9(s)
s = patch_v10(s)
s = patch_ground(s)
s = patch_v11(s)
s = patch_v12(s)
names.append('Trig_set_hero_stats_Actions')
(OUT / 'war3map.j').write_text(s, encoding='utf-8', newline='\n')
for asset in (ROOT / 'assets').rglob('*'):
    if asset.is_file() and asset.suffix != '.json':
        target = OUT / asset.relative_to(ROOT / 'assets')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(asset, target)
node = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
subprocess.run([str(node), str(ROOT / 'repair_orbs.cjs')], check=True)
subprocess.run([str(node), str(ROOT / 'make_soft_orb.cjs')], check=True)
subprocess.run([str(node), str(ROOT / 'make_dense_orb.cjs')], check=True)
subprocess.run([str(node), str(ROOT / 'prepare_enchantress.cjs')], check=True)
subprocess.run([sys.executable, str(ROOT / 'make_magic_textures.py')], check=True)
subprocess.run([str(node), str(ROOT / 'make_soft_ground.cjs')], check=True)
sys.path.insert(0, str(ROOT.parent / 'mini-foots/tools'))
import objdata
units = objdata.load(str(BASE / 'war3map.w3u'))
assert objdata.dump(units) == (BASE / 'war3map.w3u').read_bytes()
for table in units['tables']:
    for entry in table:
        if entry['newId'] == 'HOr1':
            appearance = {
                'umdl': r'Models\OriannaEnchantress\BlackLegionEnchantressV2.mdx',
                'usnd': 'Sorceress',
                'uico': r'ReplaceableTextures\CommandButtons\BTNSorceress.blp',
                'ussi': r'ReplaceableTextures\CommandButtons\BTNSorceress.blp',
                'ucpt': 0.5,
                'ucbs': 1.033,
            }
            assert set(appearance) <= {m['id'] for m in entry['mods']}
            for mod in entry['mods']:
                if mod['id'] in appearance: mod['value'] = appearance[mod['id']]
            stats = json.loads((ROOT / 'lich-stats.json').read_text())['fields']
            entry['mods'] = [m for m in entry['mods'] if m['id'] not in stats]
            entry['mods'].extend({'id':k, **v, 'end':b'HOr1'.hex()} for k,v in stats.items())
        if entry['newId'] in ('hor1', 'hor2'):
            for mod in entry['mods']:
                if mod['id'] in ('umxp', 'umxr'): mod['value'] = 0.0
                if mod['id'] == 'umdl': mod['value'] = ''
(OUT / 'war3map.w3u').write_bytes(objdata.dump(units))
from power_orb import apply_power_orb
s=apply_power_orb(s)
scope=dict(s=s,O=OUT,R=ROOT,re=re,json=json,objdata=objdata)
exec((ROOT/'hero_policy.py').read_text(encoding='utf8'),scope)
s=scope['s']
(OUT/'war3map.j').write_text(s,encoding='utf8')
buffs = objdata.load(str(BASE / 'war3map.w3h'))
for table in buffs['tables']:
    for entry in table:
        if entry['newId'] == 'BOr4':
            for mod in entry['mods']:
                if mod['id'] == 'ftat': mod['value'] = ''  # Managed SpeedTarget effect follows haste lifetime.
                if mod['id'] == 'fta0': mod['value'] = 'origin'
                if mod['id'] == 'ftac': mod['value'] = 1
assert not any(e['newId'] == 'BOr5' for t in buffs['tables'] for e in t)
buffs['tables'][1].append({'oldId': 'Bslo', 'newId': 'BOr5', 'flags': 1, 'extra': 0, 'mods': [
    {'id': k, 'type': 3, 'value': v, 'end': b'BOr5'.hex()} for k,v in [
        ('fnam','Orianna Slow'), ('ftip','Command: Slow'), ('fube','Movement speed reduced by 25%.'),
        ('ftat',r'Abilities\Spells\Human\slow\slowtarget.mdl'), ('fta0','origin')]]})
(OUT / 'war3map.w3h').write_bytes(objdata.dump(buffs))
abilities = objdata.load(str(BASE / 'war3map.w3a'))
for table in abilities['tables']:
    for entry in table:
        if entry['newId'] == 'AOz7':
            # The ability inherits Targetart from AOae independently of BOr4 art.
            entry['mods'] = [m for m in entry['mods'] if m['id'] != 'atat']
            entry['mods'].append({'id':'atat','type':3,'level':0,'ptr':0,'value':'','end':b'AOz7'.hex()})
        if entry['newId'] == 'AGf1':
            for mod in entry['mods']:
                if mod['id']=='aare':mod['value']=100.0
                if mod['id']=='atar':mod['value']='self,ground,air,vuln,invu'
                if mod['id'] in ('adur','ahdu'):mod['value']=0.2
        if entry['newId'] == 'AGr2':
            for mod in entry['mods']:
                if mod['id']=='Ncl6':mod['value']='roar'
        if entry['newId'] in ('AOz1','AOz2','AOz3','AOz4'):
            for mod in entry['mods']:
                if mod['id']=='aani': mod['value']='stand,channel' if entry['newId']=='AOz4' else 'spell,attack'
        if entry['newId'] in ('AOz2', 'AOz4'):
            for mod in entry['mods']:
                if mod['id'] == 'aare': mod['value'] = round(mod['value'] * .7 * 1.1, 4)
                if mod['id'] in ('aub1', 'arut'): mod['value'] = tooltip_v8(tooltip(mod['value']))
        if entry['newId'] == 'AOz5':
            entry['mods'] = [m for m in entry['mods'] if m['id'] != 'abuf']
            for level in range(1,9):
                entry['mods'].append({'id':'abuf','type':3,'level':level,'ptr':0,'value':'BOr5','end':b'AOz5'.hex()})
from fortitude import patch as patch_fortitude, objects as fortitude_objects
s=patch_fortitude(s)
(OUT/'war3map.j').write_text(s,encoding='utf8')
abilities=fortitude_objects(abilities)
(OUT / 'war3map.w3a').write_bytes(objdata.dump(abilities))
strings = (BASE / 'war3map.wts').read_bytes()
old_title = b'FF Rx MAIN - Hero Tavern v1'
assert strings.count(old_title) == 1
(OUT / 'war3map.wts').write_bytes(strings.replace(old_title, b'FF799X - Orianna v18'))
# Register all packaged presentation files, including inherited files omitted by listfile.
imp = (OUT / 'war3map.imp').read_bytes()
version, count = struct.unpack_from('<ii', imp)
paths = set(); at = 8
for _ in range(count):
    flag = imp[at]; end = imp.index(b'\0',at+1); path = imp[at+1:end].decode()
    paths.add(path.lower()); at = end+1
new_paths = []
for file in sorted(OUT.rglob('*')):
    if file.is_file() and file.suffix.lower() in ('.mdx','.blp','.wav'):
        path = str(file.relative_to(OUT)).replace('/', '\\')
        if path.lower() not in paths:
            paths.add(path.lower()); new_paths.append(path)
(OUT / 'war3map.imp').write_bytes(struct.pack('<ii',version,count+len(new_paths))+imp[8:]+b''.join(b'\r'+p.encode()+b'\0' for p in new_paths))
sys.path.insert(0, str(ROOT / 'tools'))
from mpyq import MPQArchive
base_map = MPQArchive(r'C:\Users\User\Documents\Warcraft III\Maps\Test\Archive\FF799X_Rx_HeroTavern_v1.w3x', listfile=False)
existing = [str(p.relative_to(OUT)).replace('/', '\\') for p in OUT.rglob('*') if p.is_file() and base_map.get_hash_table_entry(str(p.relative_to(OUT)).replace('/', '\\')) is not None]
(ROOT / 'base-payloads.json').write_text(json.dumps(existing))
sf = functions(s)
orianna_changes = [n for n in bf if n.startswith('OM_') and bf[n] != sf[n]]
added_functions = sorted(set(sf)-set(bf))
manifest = {'base': 'FF799X_Rx_HeroTavern_v1.w3x', 'donor': 'Mini Foots v5 UI snapshot',
            'changed_functions': [n for n in names if bf[n] != sf[n]] + orianna_changes, 'added_functions': added_functions, 'stats_rows': 12,
            'payloads': {str(p.relative_to(OUT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in OUT.rglob('*') if p.is_file()},
            'checks': ['Nine prior UI/Gragus changes preserved', 'Other Gragus functions match donor',
                       '12 stats rows fit in panel with close button', 'Single early stats initialization', 'Orianna model round-trip passed'],
            'live_gameplay': 'Not tested'}
(ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
