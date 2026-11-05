from pathlib import Path
p=Path('mini-foots/build_source.py');s=p.read_text()
s=s.replace("fn('Trig_limit_amount_of_creeps_Actions','''",'''costs="function MF_CreepGold takes integer id returns integer\\n"
for c in sorted(creeps):
 if c in es and 'ugol' in mods(es[c]):
  costs+=f"    if id == '{c}' then\\n        return {mods(es[c])['ugol']}\\n    endif\\n"
costs+="    return 0\\nendfunction"
insert_before('Trig_limit_amount_of_creeps_Actions',costs)
fn('Trig_limit_amount_of_creeps_Actions',\'\'\'''' )
s=s.replace('set cost=BlzGetUnitIntegerField(bought, UNIT_IF_LUMBER_BOUNTY_AWARDED_BASE)','set cost=MF_CreepGold(id)').replace('set cost=BlzGetUnitIntegerField(bought, UNIT_IF_GOLD_COST)','set cost=BlzGetUnitIntegerField(bought, UNIT_IF_LUMBER_BOUNTY_AWARDED_BASE)')
p.write_text(s)
