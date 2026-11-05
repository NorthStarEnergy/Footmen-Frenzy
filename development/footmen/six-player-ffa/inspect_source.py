from pathlib import Path
import re,struct,json,collections
R=Path(__file__).parent
s=(R/'base/war3map.j').read_text(encoding='utf-8-sig')
def function(name):return re.search(r'^function '+name+r'\b.*?^endfunction',s,re.M|re.S)[0]
names=['CreateAllUnits','Trig_init_Actions','SF_AcceptHero','Trig_TP_hero_Conditions','SF_OpenTaverns','Trig_player_destroyed_Actions','Trig_player_leaves_Actions','Trig_Foot_Spawn_Actions','Trig_Start_game_Actions']
(R/'source-functions.txt').write_text('\n\n'.join(function(n) for n in names),encoding='utf-8')
# Use the existing source's version-specific placed-unit reader.
code=Path(r'C:/Users/User/Documents/Codex/2026-10-28/thi/work/formats.py').read_text().split('u=units()')[0]
scope={};exec(code,scope);scope['P']=R/'base';units=scope['units']()
(R/'source-units.json').write_text(json.dumps(units,indent=2))
print('Units by owner',collections.Counter(u['owner'] for u in units))
print('West base',[(u['type'],u['xyz'][:2]) for u in units if u['owner']==9])
print('Neutral',[(u['type'],u['xyz'][:2]) for u in units if u['owner']>=12])
print('Initialization functions',re.findall(r'^function (Trig_init_\w+)',s,re.M))
b=(R/'base/war3map.w3e').read_bytes();print('Terrain',struct.unpack_from('<IIff',b,69),collections.Counter(b[92::8]));print('W3I',b'')
