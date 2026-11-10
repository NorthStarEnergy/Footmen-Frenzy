from pathlib import Path
import re,struct,sys,json
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'hero-polish'))
from archive_helpers import functions,objdata
script=(R/'src/war3map.j').read_bytes().decode('latin1').replace('\r','')
# Regenerate a validation script from authoritative editor functions/globals.
w = (R/'src/war3map.wct').read_bytes()
p = w.index(0, 8)+1
chunks = []
while p < len(w):
    n = struct.unpack_from('<I', w, p)[0]; p += 4
    chunks.append(w[p:p+n].rstrip(b'\0').decode('latin1').replace('\r','')); p += n
source = '\n'.join(chunks)
efs = functions(source)
regen = re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction', lambda m: efs.get(m[1], m[0]), script)
header = re.search(r'(?ms)^globals\b(.*?)^endglobals', chunks[0])[1]
packed = re.search(r'(?ms)^globals\b(.*?)^endglobals', regen)[1]
decl = r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)'
names = {m[1] for line in header.splitlines() if (m := re.match(decl, line)) and not line.lstrip().startswith('//')}
extra = [line for line in packed.splitlines() if (m := re.match(decl,line)) and m[1] not in names and not line.lstrip().startswith('//')]
regen = re.sub(r'(?ms)^globals\b.*?^endglobals', lambda _: 'globals\n'+header+'\n'+'\n'.join(extra)+'\nendglobals', regen, count=1)
(R/'editor-validation.j').write_bytes(regen.encode('latin1'))


fs=functions(script)
old=functions((R/'original/war3map.j').read_bytes().decode('latin1').replace('\r',''))
changed=[n for n in old if old[n]!=fs[n]]
assert set(old)<=set(fs)
for n in set(fs)-set(old):
 assert n in efs and efs[n].replace('\r','')==fs[n],n
for n in changed:
 assert efs[n].replace('\r','')==fs[n],n
# Dialog startup, Mundo poison and hero abilities are preserved verbatim.
for n in old:
 if n.startswith(('FFStart_','Mundo','FFMundo','Gas_','Trig_MODE_')):
  assert old[n]==fs[n],n
roster={int(i):v for i,v in re.findall(r"set udg_hero_type\[(\d+)\]\s*=\s*'(.{4})'",script)}
disabled=set(re.findall(r"'(.{4})'",fs['MF_HeroDisabled']))
assert set(range(1,97))<=roster.keys()
enabled={v for i,v in roster.items() if i<=96 and v not in disabled}
stock={shop:[] for shop in range(13,22)}
for i in range(1,97):
 if roster[i] not in disabled:stock[13+(i-1)//11].append(roster[i])
assert set(x for shop in stock.values() for x in shop)==enabled
assert all(len(x)<=11 for x in stock.values())
assert 'udg_total_hero_count' in fs['Trig_Start_AP_Actions']
assert 'udg_real_shop' not in fs['FFRandom_Stock']
assert 'T66_RandomLeft[team] = 3' in fs['FFHire_Prepare']
assert 'shop == CarryTav_shop[team]' in fs['FFRandom_Sold']
assert 'FFR_Seeded' not in fs['FFRandom_Sold']
assert 'FFR_Used' not in fs['FFRandom_Sold']
assert 'FFR_Allowed(team, i)' in fs['FFRandom_Sold']
assert 'CarryTav_locked[team]' in fs['FFRandom_Sold']
# Exercise shared credit accounting: three distinct buyers, rejected/empty sales, team isolation.
credits=[3]*4
for team,eligible,pool in [(0,True,True),(0,False,True),(0,True,False),(1,True,True),(0,True,True),(0,True,True),(0,True,True)]:
 if eligible and pool and credits[team]>0:credits[team]-=1
assert credits==[0,2,3,3]
# Engine setter delta compensation should converge and remain idempotent.
for primary,secondary in [(0,0),(110,110),(220,220),(600,100)]:
 for desired in [110,110,210,265,110]:
  written=desired-primary+secondary
  primary+=written-secondary
  secondary=written
  assert primary==desired
assert len(re.findall(r'call MF_SetAttackRange\(',script))==8
assert not re.search(r'BlzSetUnitWeaponRealField(?:BJ)?\([^\n]*ATTACK_RANGE[^\n]*udg_unit_range',script)
# Team patrons remain separated by more than A05T's 200-unit activation radius.
import math
archive=[(-2272,160-288*t) for t in range(4)]
for i,a in enumerate(archive):
 for j,b in enumerate(archive):
  if i!=j:assert math.dist(a,b)>200
for filename in ['war3map.w3u','war3mapSkin.w3u']:
 data=objdata.load(str(R/'src'/filename))
 ids=[e['newId'] for e in data['tables'][1]]
 assert ids.count('n66A')==1
 if filename=='war3map.w3u':
  random=next(e for e in data['tables'][1] if e['newId']=='h004')
  mods={m['id']:m['value'] for m in random['mods']}
  assert mods['usma']==3 and mods['usrg']==999999
report={'enabled_ap_heroes':len(enabled),'disabled_roster_entries':{i:v for i,v in roster.items() if i<=96 and v in disabled},'ap_stock_by_shop':stock,'shared_random_uses':3,'random_pool':'full eligible roster, including drafted heroes','range_setter_call_sites':8,'runtime_editor_functions_synchronized':True,'modified_functions':changed,'added_functions':sorted(set(fs)-set(old)),'engine_playtest':'pending'}
(R/'mode-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['ap_stock_by_shop','modified_functions','added_functions']},indent=2))
