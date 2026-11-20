from pathlib import Path
import sys, re, json, copy, ast, hashlib
R=Path(__file__).resolve().parent; W=R.parent; S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm, read_storm, c, functions
from validate_objdata import validate
import objdata
base=W/'799x-backport/release/FF799X_Rx_Myrmidon_Cleave_v44.w3x'
names=['war3map.j','war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3mapSkin.w3a','war3map.wts']
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for n in names:(S/n).write_bytes(read_storm(h,n))
assert storm.SFileCloseArchive(h)
objects={n:objdata.load(str(S/n)) for n in names if n.endswith(('.w3u','.w3a'))}
def index(o):return {(e['newId'] if e['newId']!='\0'*4 else e['oldId']):e for t in o['tables'] for e in t}
def put(e,key,value,typ,level=None,ptr=0):
 m=next((m for m in e['mods'] if m['id']==key and (level is None or m.get('level')==level)),None)
 if m is None:
  m=dict(id=key,type=typ,value=value,end='00000000');e['mods'].append(m)
  if level is not None:m.update(level=level,ptr=ptr)
 else:m.update(type=typ,value=value)

a=index(objects['war3map.w3a']); skin=index(objects['war3mapSkin.w3a'])
for i in range(256):
 e=a[f'mD{i:02X}'];assert e['extra']==0;e['flags']=1
for code,hotkey,research,x in [('AMu1','Z','Q',0),('AMu2','X','W',1)]:
 for idx in (a,skin):
  if code not in idx:continue
  e=idx[code]
  for k,v,t in [('ahky',hotkey,3),('arhk',research,3),('abpx',x,0),('arpx',x,0)]:put(e,k,v,t,0)
  for m in e['mods']:
   if m['id'] in ('atp1','aub1'):m['value']=re.sub(r'\|cffffcc00[QWZX]\|r',f'|cffffcc00{hotkey}|r',m['value'])
   elif m['id'] in ('aret','arut'):m['value']=re.sub(r'\|cffffcc00[QWZX]\|r',f'|cffffcc00{research}|r',m['value'])
for idx in (a,skin):
 if 'AMu1' not in idx:continue
 for lv in range(1,7):put(idx['AMu1'],'aran',1100.0,2,lv)

# Resolve Strongest Man's inherited stats as well as explicit object edits.
source=(W/'mini-foots/tools/game_data.py').read_text()
exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='slk'],type_ignores=[]),'slk','exec'))
cache=W/'799x-backport/item-audit/game-data'
meta=slk((cache/'base-unitmetadata.slk').read_bytes())
tables={}
for table in ['UnitBalance','UnitData','UnitWeapons']:
 rows={}
 for layer in ['base','custom']:
  p=cache/f'{layer}-{table.lower()}.slk'
  if p.exists():
   for uid,fields in slk(p.read_bytes()).items():rows.setdefault(uid,{}).update(fields)
 tables[table]=rows
units=index(objects['war3map.w3u']); unit_skin=index(objects['war3mapSkin.w3u'])
ref=units['H00T'];mundo=units['HMu1'];refmods={m['id']:m for m in unit_skin['H00T']['mods']}
refmods.update({m['id']:m for m in ref['mods']})
stats={}
fields='ustr ustp uagi uagp uint uinp upra uhpm uhpr uhrt umpm umpi umpr ua1c ua1b ua1d ua1s ua1r ua1t ua1w uaen uacq udef udty umvs umvr umvt ucol usid usin ulev ufoo ubba udp1 ubs1 ucpt ucbs'.split()
for key in fields:
 if key in refmods:mod=refmods[key];value=mod['value'];typ=mod['type']
 else:
  md=meta[key];value=tables[md['slk']][ref['oldId']][md['field']]
  typ=0 if md['type'] in ['int','attackBits'] else 2 if md['type'] in ['real','unreal'] else 3
  if typ==0:value=int(float(value))
  elif typ==2:value=float(value)
 put(mundo,key,value,typ);stats[key]=value
 if 'HMu1' in unit_skin:put(unit_skin['HMu1'],key,value,typ)

s=(S/'war3map.j').read_text(encoding='utf-8-sig');before=s
def replace(name,new):
 global s
 old=functions(s)[name];assert s.count(old)==1;s=s.replace(old,new,1)
for field in ['STR_base','STR_inc','AGI_base','AGI_inc','INT_base','INT_inc','move_base','turnrate']:
 value=re.search(r'set udg_hero_'+field+r'\[37\]=([^\r\n]+)',s)[1]
 s,n=re.subn(r'(set udg_hero_'+field+r'\[95\]=)[^\r\n]+',lambda m:m[1]+value,s);assert n==1

# Circle and floating blade only: retain the bloodied pickup mechanic.
for name in ['MQ_Land','MQ_GroundTick','MQ_Free']:
 f=functions(s)[name]
 f='\n'.join(line for line in f.split('\n') if not any(x in line for x in [
  'local lightning beam','local texttag label','set beam =','set label =','SetTextTag','SetLightningColor','SaveLightningHandle','SaveTextTagHandle',
  'DestroyLightning','DestroyTextTag','MoveLightningEx']))
 f=f.replace('call BlzSetSpecialEffectScale(ring, 0.65)','call BlzSetSpecialEffectScale(ring, 0.8)')
 # Removed text-only conditionals in the countdown update.
 f=f.replace('        if LoadBoolean(MQ_Hash, i, 11) then\n        else\n        endif\n','')
 replace(name,f)
fling=functions((R/'fling.j').read_text())
replace('MU_FlingTick',fling['MU_FlingSafe']+'\n\n'+fling['MU_FlingTick'])
replace('MU_Fling',fling['MU_Fling'])
# Add dramatic effects only after native cargo confirms a successful swallow.
f=functions(s)['MDV_Update']
anchor='        call SaveEffectHandle(MD_Hash, h, 22, fx)'
assert anchor in f
f=f.replace(anchor,anchor+'\n        call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Orc\\\\WarStomp\\\\WarStompTarget.mdl", u, "origin"))')
replace('MDV_Update',f)

def tip(text,code,rank=1):
 if code=='AMu1':
  text=text.replace('Walk within 100','Walk into the circle within 100')
  if 'Cooldown: 4 sec.' in text:text=text.replace('Cooldown: 4 sec.','Cooldown: 4 sec. Cast range: 1100.')
 if code=='AMu3':text=text.replace('flip the target behind Mundo,',f'flip the target up to {200+30*(rank-1)} units behind Mundo (shortened by walls, cliffs or map edges),')
 return text
for code in ['AMu1','AMu3']:
 for idx in (a,skin):
  if code not in idx:continue
  for m in idx[code]['mods']:
   if m['id'] in ['aub1','arut']:m['value']=tip(m['value'],code,max(1,m.get('level',1)))
f=functions(s)['MU_Init']
for code,key in [('AMu1','Q'),('AMu2','W')]:
 f=re.sub(r"(BlzSetAbilityResearchTooltip\('"+code+r"', \"[^\"]*\|cffffcc00)[QW](\|r)",lambda m:m[1]+key+m[2],f)
for code in ['AMu1','AMu3']:
 pattern=r"(BlzSetAbilityResearchExtendedTooltip\('"+code+r"', \"[^\"]*)(\", (\d)\))"
 f=re.sub(pattern,lambda m:tip(m[1],code,int(m[3])+1)+m[2],f)
replace('MU_Init',f)
(S/'war3map.j').write_text(s,encoding='utf8')
for n,o in objects.items():
 data=objdata.dump(o);validate(data,n.endswith('.w3a'));(S/n).write_bytes(data)
wts=(S/'war3map.wts').read_bytes()
assert b'Consolidated Undying v42' in wts
(S/'war3map.wts').write_bytes(wts.replace(b'Consolidated Undying v42',b'Consolidated Mundo Polish v45'))
bf,af=functions(before),functions(s)
report=dict(base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),payloads=names,stats_reference='H00T',stats=stats,changed_functions=[n for n in bf if bf[n]!=af[n]],added_functions=sorted(af.keys()-bf.keys()))
(R/'changes.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
