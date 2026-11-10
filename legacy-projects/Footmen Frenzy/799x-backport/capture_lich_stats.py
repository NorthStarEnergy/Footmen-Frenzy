"""Freeze the map's Lich combat defaults plus scripted attribute overrides."""
from pathlib import Path
import sys,json,re
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'mini-foots/tools'))
from game_data import game_read,slk,ini
import objdata
meta=slk(game_read('war3.w3mod:units/unitmetadata.slk'))
tables={name:slk(game_read('war3.w3mod:units/'+name.lower()+'.slk'))['Ulic'] for name in ['UnitBalance','UnitWeapons','UnitData']}
profile=ini(game_read('war3.w3mod:units/undeadunitfunc.txt'))
lich=next(e for t in objdata.load(str(ROOT.parent/'mini-foots/base/files/war3map.w3u'))['tables'] for e in t if e['newId']=='U003')
overrides={m['id']:m for m in lich['mods']}
fields='ustr ustp uagi uagp uint uinp upra uhpm uhpr uhrt umpm umpi umpr udef udup udty umvs umvr usid usin ua1b ua1d ua1s ua1c ua1r ua1t ua1w ua1g uaen udp1 ubs1 uacq ua1z'.split()
result={}
for field in fields:
    m=meta[field]
    if field in overrides:
        result[field]={k:overrides[field][k] for k in ['type','value']};continue
    raw=profile['Ulic'][m['field']] if m['slk']=='Profile' else tables[m['slk']][m['field']]
    typ={'int':0,'real':1,'unreal':2,'bool':0,'attackBits':0}.get(m['type'],3)
    result[field]={'type':typ,'value':int(raw) if typ==0 else float(raw) if typ in (1,2) else raw}
source=(ROOT.parent/'mini-foots/base/files/war3map.j').read_text(encoding='utf-8-sig')
runtime={name:float(value) for name,value in re.findall(r'set udg_hero_(STR_base|STR_inc|AGI_base|AGI_inc|INT_base|INT_inc|move_base|turnrate)\[10\]=([0-9.]+)',source)}
for field,name in dict(ustr='STR_base',ustp='STR_inc',uagi='AGI_base',uagp='AGI_inc',uint='INT_base',uinp='INT_inc',umvs='move_base',umvr='turnrate').items():
    result[field]['value']=int(runtime[name]) if result[field]['type']==0 else runtime[name]
projectile=profile['unec']['Missileart']
assert game_read('war3.w3mod:'+projectile.replace('.mdl','.mdx'))
result['ua1m']={'type':3,'value':projectile}
for path in [r'Abilities\Spells\Undead\FrostNova\FrostNovaTarget.mdx',r'Abilities\Spells\Other\Monsoon\MonsoonBoltTarget.mdx']:
    assert game_read('war3.w3mod:'+path),path
(ROOT/'lich-stats.json').write_text(json.dumps({'reference':'U003 (map Lich, roster index 10)','runtime':runtime,'fields':result},indent=2))
print(json.dumps(result,indent=2))
