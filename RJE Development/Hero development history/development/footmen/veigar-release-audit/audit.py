from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent; W=R.parent; (R/'src').mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c
import objdata
base=W/'Transfer/Veigar_Visuals_v81/FF799X_Rx_Veigar_Visuals_v81_TEST.w3x'
assert hashlib.sha256(base.read_bytes()).hexdigest()==json.loads((W/'veigar-visuals-v81/verification.json').read_text())['sha256']
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,256,c.byref(h))
for n in ['war3map.j','war3map.w3a','war3map.w3u']:(R/'src'/n).write_bytes(read_storm(h,n))
assert storm.SFileCloseArchive(h)
# Reuse existing behavioral tests against the current delivered artifact and current ranges.
suite=(W/'veigar-repair-v73/checks.py').read_text()
suite=suite.replace('from game_data import game_read,slk','')
suite=suite.replace(";meta=slk(game_read(r'war3.w3mod:units\\abilitymetadata.slk'))",'')
suite=suite.replace(" check(name+' fields match Warcraft metadata types',all(m['type']==expected.get(meta.get(m['id'],{}).get('type'),m['type']) for m in ability['mods']))"," pass # Metadata DLL unavailable; do not count this historical check as rerun.")
suite=suite.replace("('AVgq',6,700),('AVgw',6,900),('AVge',6,900),('AVgr',3,650)","('AVgq',6,900),('AVgw',6,1100),('AVge',6,1100),('AVgr',3,850)")
env={'__file__':str(R/'checks.py'),'__name__':'__main__'}
exec(compile(suite,'current-artifact-checks','exec'),env)
additional=[]
def check(name,value):
 assert value,name
 additional.append(name)
e,u,s,t=env['setup']()
e.update(GetKillingUnit=lambda:1,GetTriggerUnit=lambda:2,GetOwningPlayer=lambda x:u[x]['owner'],
 GetUnitTypeId=lambda x:u.get(x,{}).get('kind',0),IsUnitIllusion=lambda x:u[x].get('illusion',False),
 GetHeroInt=lambda x,bonus:u[x]['int'],SetHeroInt=lambda x,v,b:u[x].update(int=v),
 UNIT_TYPE_HERO='hero',UNIT_TYPE_SUMMONED='summoned')
exec(env['translate']('VG_ClassicKill'),e)
for rank in range(1,7):
 for hero,q,expected in [(False,True,1),(False,False,0),(True,False,rank),(True,True,rank+1)]:
  u[1].update(kind='HVg1',AVgq=rank,int=20);u[2].update(hero=hero)
  t['VG_Hash'][1,701]=2 if q else None
  e['VG_ClassicKill']();check(f'rank {rank} hero={hero} Q-last-hit={q} stack gain',u[1]['int']==20+expected)
for flag in ['illusion','summoned','structure']:
 u[1]['int']=20;u[2][flag]=True;e['VG_ClassicKill']()
 check(flag+' victim grants no INT',u[1]['int']==20);u[2][flag]=False
u[1].update(int=20,illusion=True);e['VG_ClassicKill']();check('illusion caster grants no INT',u[1]['int']==20);u[1]['illusion']=False
u[1]['AVgq']=0;e['VG_ClassicKill']();check('unlearned Q grants no INT',u[1]['int']==20)
u[1].update(kind='HVg1',mana=50.,maximum=100.)
e.update(CreateGroup=lambda:99,DestroyGroup=lambda g:s['groups'].pop(g,None),
 UNIT_STATE_MAX_MANA='maximum',UNIT_STATE_MANA='mana',
 GetUnitState=lambda x,k:u[x][k],SetUnitState=lambda x,k,v:u[x].update({k:v}))
exec(env['translate']('VG_Equilibrium'),e)
for mana,expected in [(0.,2.),(50.,51.),(100.,100.)]:
 s['groups'][99]=[];u[1]['mana']=mana;e['VG_Equilibrium']();check(f'Equilibrium at {mana}% mana',u[1]['mana']==expected)
# Reproduce the geometric discontinuity: no teleport distinction exists in the scanner.
e,u,s,t=env['setup']();u[2].update(x=-500.);e['VG_CageScan'](50)
u[2]['x']=500.;e['VG_CageScan'](50)
check('outside-to-outside teleport across cage is treated as crossing',len(s['stuns'])==1)
(R/'additional-checks.json').write_text(json.dumps({'passed':len(additional),'checks':additional,'scope':'Mocked native behavior; teleport case records current behavior, not release approval.'},indent=2))
print(len(additional),'additional checks passed')
records={}
for name,ids in [('war3map.w3a',['AVgq','AVgw','AVge','AVgr','AVgp','AVgs']),('war3map.w3u',['HVg1','hgr1'])]:
 data=objdata.load(str(R/'src'/name))
 for entry in sum(data['tables'],[]):
  if entry['newId'] in ids:records[entry['newId']]=entry
(R/'objects.json').write_text(json.dumps(records,indent=2))
for key,entry in records.items():
 print(key,entry['oldId'])
 print([(m['id'],m.get('level'),m['value']) for m in entry['mods'] if m['id'] in ['atar','Ncl2','Ncl3','Ncl6','ahky','arhk','anam','aher','alev','abuf','adur','ahdu','aran','ucam','umdl','ua1r','uhab','uabi','ustr','uagi','uint','ustp','uagp','uinp','umvs','uhpm']])
# Verify actual stock texture references against the installed game's data.
textures=sorted(set(t for m in json.loads((W/'veigar-visuals-v81/model-checks.json').read_text())['models'] for t in m['textures']))
texture_checks={t:'Not revalidated: historical CascLib DLL is missing' for t in textures}
(R/'textures.json').write_text(json.dumps(texture_checks,indent=2)); print('Textures:',texture_checks)
