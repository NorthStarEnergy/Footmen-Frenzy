"""Exercise the shipped draft and XP code with mocked Warcraft natives."""
import ast
import collections
import re
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[4]
src = root / 'build/799x-rc2/projects/799x/src'
s = (src / 'war3map.j').read_text(encoding='utf-8')

# Reuse the existing offline JASS translator and placement reader without
# executing their historical build entry points.
def definitions(path, names):
    tree = ast.parse((root / path).read_text(encoding='utf-8'))
    tree.body = [node for node in tree.body if getattr(node, 'name', None) in names]
    assert len(tree.body) == len(names)
    scope = dict(s=s, re=re, struct=struct)
    exec(compile(tree, path, 'exec'), scope)
    return scope

translate = definitions('development/solo/ffa-v4/verify_behavior.py', ['translate'])['translate']
placements = definitions('development/solo/ffa-v4/build.py', ['Reader', 'placements'])['placements']
units = placements((src / 'war3mapUnits.doo').read_bytes())
shops = [u for u in units if u['kind'] == 'n003']
assert sorted(u['owner'] for u in shops) == list(range(12))
assert len(set(u['id'] for u in units)) == len(units)
assert {(u['x'],u['y']) for u in shops if u['owner'] >= 9} == {(-3264.,-3008.)}

slots = range(1, 13)
teams = {pn: (pn-1)//3+1 for pn in slots}
e = dict(defaultdict=collections.defaultdict, IMinBJ=min, FFR_Index=lambda x:x,
         udg_teamnumber=teams, T66_RandomLeft={team:3 for team in range(1,5)},
         DraftShop={pn:{'hTNP'} for pn in slots}, DraftEligible=lambda team, kind:True,
         AddUnitToStock=lambda shop,kind,*unused:shop.add(kind),
         RemoveUnitFromStock=lambda shop,kind:shop.discard(kind))
for name in ['DraftCount','DraftPool','DraftPage','DraftTaken','DraftShown','udg_hero_category','udg_maphack']:
    e[name] = collections.defaultdict(int)
for team in range(1,5):
    e['DraftCount'][team] = 21
    for i in range(1,22):
        raw = team*100+i
        e['DraftPool'][team*256+i] = raw
        e['udg_hero_category'][raw] = 12 if i > 11 else 1
for name in ['DraftSD','DraftRefreshPub','DraftRefresh','DraftSale','P67_HeroRate']:
    code = re.sub(r'array (\w+)=None',r'\1=defaultdict(int)', translate(name))
    exec(code,e)

for mode in (2,3):
    e['udg_selected_mode'] = mode
    for pn in slots:
        e['DraftPage'][pn] = 0
        e['DraftRefresh'](pn)
    for pn in slots:
        before = {n:stock.copy() for n,stock in e['DraftShop'].items()}
        e.update(GetSellingUnit=lambda:e['DraftShop'][pn],GetSoldUnit=lambda:'hTNP',
                 GetUnitTypeId=lambda u:'nTDP' if isinstance(u,set) else u,
                 SoloSub_ReownToSlot=lambda u:None,GetOwningPlayer=lambda u:pn,
                 GetConvertedPlayerId=lambda p:p,DraftCanPick=lambda p:True,
                 RemoveUnit=lambda u:None,StartSoundForPlayerBJ=lambda *args:None,FF_DraftPageClick=0)
        e['DraftSale']()
        assert e['DraftPage'][pn] == 1 and e['DraftShop'][pn] != before[pn]
        assert all(e['DraftShop'][n] == before[n] for n in slots if n != pn)
        assert ('hTRZ' in e['DraftShop'][pn]) == (mode == 3)
        e['DraftSale']()
        if mode == 2:
            e['DraftSale']()
        assert e['DraftPage'][pn] == 0 and e['DraftShop'][pn] == before[pn]
e.update(GetHeroLevel=lambda u:u, GetPlayerId=lambda p:p, GetOwningPlayer=lambda u:0, P67_POST7_RATE=70)
assert [e['P67_HeroRate'](lvl) for lvl in range(1,19)] == [100]*6+[70]*12
e['udg_maphack'][1]=True
assert e['P67_HeroRate'](13)==25
print('Verified Team 4 editor placements, independent page purchases and wrapping for 12 slots in AP and SD, and XP rates at levels 1-18.')
