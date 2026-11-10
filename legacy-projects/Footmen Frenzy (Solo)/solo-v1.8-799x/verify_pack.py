"""Verify the scoped merge, exercise key JASS helpers, then pack and compare every archive member."""
from pathlib import Path
import sys,re,json,hashlib,shutil,struct,ast,math
R=Path(__file__).resolve().parent; W=R.parent.parent/'Footmen Frenzy'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import archive,entries,functions as parse,storm,read_storm,c
import objdata
report=json.loads((R/'migration.json').read_text());base=Path(report['base']);donor=Path(report['donor']);O=R/'src'
s=(O/'war3map.j').read_text(encoding='utf8');d=(R/'donor/war3map.j').read_text(encoding='utf-8-sig');b=(R/'base/war3map.j').read_text(encoding='cp1252')
f=parse(s);df=parse(d);bf=parse(b);checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
check('Final runtime compiled', 'Parse successful:' in (R/'compiler.log').read_text(encoding='utf-8-sig') and 'Error' not in (R/'compiler.log').read_text(encoding='utf-8-sig'))
for n in f:
 if n.startswith(('OM_','FS_')):check('Latest donor implementation: '+n,f[n]==df[n])
for n in bf:
 if n not in report['changed_functions']:check('Preserved function: '+n,f[n]==bf[n])
for n in ['InitCustomPlayerSlots','InitCustomTeams','CreateRegions','SoloFootsStockTeamTaverns','SoloFootsMassPreload','Trig_Start_game_Actions','Trig_KOTH_Setup_Actions','Trig_ITEM_limits_Actions']:
 check('Solo contract: '+n,f[n]==bf[n])
check('Exactly one initialization per new subsystem',s.count('call OM_Init()')==1 and s.count('call FS_Init()')==1)
check('Roster expanded to 93', 'set udg_total_hero_count=93' in f['Trig_set_hero_numbers_Actions'])
for i,code in [(92,'HOr1'),(93,'HGr1')]:
 check('Selectable roster '+code,"set udg_hero_type[%d]='%s'"%(i,code) in s and 'set udg_hero_category[%d]=1'%i in s)
# Object tables must parse to their exact boundaries. Existing records remain equal.
key=lambda e:e['newId'] if e['newId']!='\0'*4 else e['oldId']
objects={}
for ext in ['w3u','w3a','w3h','w3t','w3q','w3b','w3d']:
 p=O/('war3map.'+ext)
 if not p.exists():p=R/'base'/p.name
 if not p.exists():continue
 data=objdata.load(str(p));objects[ext]={key(e):e for t in data['tables'] for e in t}
 before=objdata.load(str(R/'base'/p.name))
 for table in before['tables']:
  for e in table:
   if key(e) not in report['objects']:check('Preserved object '+ext+':'+key(e),objects[ext][key(e)]==e)
 check('Object boundary '+ext,True)
for rank in range(1,7):
 for raw in ['GF0'+str(rank),'BGf'+str(rank)]:check('Fortitude rank dependency '+raw,any(raw in t for t in objects.values()))
 armor=objects['w3a']['GF0'+str(rank)]
 check('Fortitude armor rank '+str(rank),next(m['value'] for m in armor['mods'] if m['id']=='Idef')==3+2*rank)
# Execute selected actual JASS bodies under native mocks.
tree=ast.parse((W/'799x-backport/check_runtime.py').read_text())
functions=dict(f)
for name in ['FS_ClearFortitude']:
 functions[name]=re.sub(r"'(.{4})'",lambda m:str(int.from_bytes(m[1].encode(),'big')),functions[name])
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('expression','translate')],type_ignores=[]),'<translator>','exec'))
env={};exec('\n\n'.join(translate(n) for n in ['MF_SetAttackRange','FS_ClearFortitude','FS_RankDamage','OM_MoveDamage','OM_AttackDamage','OM_AttackRadius','OM_ProtectHeal','OM_UltimateDamage']),env)
for desired in [100.,350.,650.,900.]:
 state={'primary':100.,'secondary':100.}
 def get(u,field,index):return state['primary' if index==0 else 'secondary']
 def setrange(u,field,index,value):
  state['primary']+=value-state['secondary'];state['secondary']=value
 env.update(BlzGetUnitWeaponRealField=get,BlzSetUnitWeaponRealField=setrange,UNIT_WEAPON_RF_ATTACK_RANGE=0)
 for _ in range(3):env['MF_SetAttackRange'](1,desired)
 check('Effective range repeated '+str(desired),state['primary']==desired)
for rank in range(1,7):
 abilities={int.from_bytes(('GF0'+str(rank)).encode(),'big'),int.from_bytes(('BGf'+str(rank)).encode(),'big')};destroyed=[]
 env.update(FS_U={1:1},FS_DrinkFX={1:100},FS_Armor={1:float(3+2*rank)},UnitRemoveAbility=lambda u,a:abilities.discard(a),DestroyEffect=lambda x:destroyed.append(x))
 env['FS_ClearFortitude'](1);env['FS_ClearFortitude'](1)
 check('Fortitude cleanup is repeat-safe rank '+str(rank),not abilities and destroyed==[100] and env['FS_Armor'][1]==0 and env['FS_DrinkFX'][1] is None)
for name in ['OM_MoveDamage','OM_AttackDamage','OM_AttackRadius','OM_ProtectHeal','OM_UltimateDamage']:
 values=[env[name](i) for i in range(1,4 if name=='OM_UltimateDamage' else 7)]
 check('Monotone positive ranks '+name,values==sorted(values) and min(values)>0)
check('Architect uses casting owner for upgrades', 'local player casterPlayer=GetOwningPlayer(GetSpellAbilityUnit())' in f['Trig_HERO_Architect_Recruit_Actions'] and 'ConvertedPlayer(udg_X_playernumber)' not in f['Trig_HERO_Architect_Recruit_Actions'])
# Runtime assets, including derived disabled icons and portraits, are donor-identical.
h=c.c_void_p();assert storm.SFileOpenArchive(str(donor),0,256,c.byref(h))
try:
 for p in O.rglob('*'):
  if p.is_file() and p.suffix.lower() in ['.mdx','.blp','.wav']:
   check('Exact donor asset '+p.name,p.read_bytes()==read_storm(h,str(p.relative_to(O))))
finally:storm.SFileCloseArchive(h)
release=R/'release';release.mkdir(exist_ok=True);out=release/'Solo_Foots_v1.8_4P_799X_UPDATE08.w3x';shutil.copy2(base,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
changed=[]
try:
 for p in sorted(O.rglob('*')):
  if p.is_file():
   name=str(p.relative_to(O));assert storm.SFileAddFileEx(h,str(p),name.encode(),0x80000200,2,2),name;changed.append(name)
finally:assert storm.SFileCloseArchive(h)
a0=archive(base);a1=archive(out);e0=entries(a0);e1=entries(a1);skip=set()
assert storm.SFileOpenArchive(str(out),0,256,c.byref(h))
try:
 for name in changed:
  check('Packed payload '+name,read_storm(h,name)==(O/name).read_bytes())
  entry=a0.get_hash_table_entry(name)
  if entry:skip.add((entry.hash_a,entry.hash_b,entry.locale,entry.platform))
finally:storm.SFileCloseArchive(h)
for name in ['(listfile)','(attributes)','(signature)']:
 entry=a0.get_hash_table_entry(name)
 if entry:skip.add((entry.hash_a,entry.hash_b,entry.locale,entry.platform))
for k,v in e0.items():
 if k not in skip:check('Preserved archive member '+str(k),e1.get(k)==v)
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
(R/'verification.json').write_text(json.dumps(dict(output=str(out),sha256=sha,checks=len(checks),preserved_archive_entries=len(e0.keys()-skip),changed_archive_payloads=changed,engine_playtest='Pending',results=checks),indent=2))
print(json.dumps(dict(output=str(out),sha256=sha,checks=len(checks),preserved_archive_entries=len(e0.keys()-skip)),indent=2))
