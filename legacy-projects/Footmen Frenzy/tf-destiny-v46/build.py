from pathlib import Path
import sys,json,re,struct,copy
from PIL import Image,ImageDraw,ImageEnhance
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
from validate_objdata import validate
import objdata
base=W/'tf-orbs-v45c/release/FF799X_Rx_TF_Orbs_v45c.w3x'
names=['war3map.j','war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3mapSkin.w3a','war3map.wts','war3map.imp']
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for n in names:(S/n).write_bytes(read_storm(h,n))
assert storm.SFileCloseArchive(h)
def put(e,k,v,t,lv=None,ptr=0):
 m=next((m for m in e['mods'] if m['id']==k and (lv is None or m.get('level')==lv)),None)
 if m:m.update(value=v,type=t)
 else:
  m=dict(id=k,value=v,type=t,end='00000000');e['mods'].append(m)
  if lv is not None:m.update(level=lv,ptr=ptr)
def index(o):return {(e['newId'] if e['newId']!='\0'*4 else e['oldId']):e for t in o['tables'] for e in t}
objects={n:objdata.load(str(S/n)) for n in names[1:5]}
for n,o in objects.items():
 idx=index(o)
 for code in ['ATf6','ATf7','ATf8']:
  if code in idx:
   for lv in range(1,7):put(idx[code],'aran',float(650+50*lv),2,lv)
 if 'ATf1' in idx:
  for lv in range(1,7):put(idx['ATf1'],'aran',float(1400+50*lv),2,lv)
 for code in ['ATf1','ATf2','ATf6','ATf7','ATf8']:
  if code in idx:
   for m in idx[code]['mods']:
    if m['id'] in ['aub1','arut']:
     lv=max(1,m.get('level',1));r=1400+50*lv if code=='ATf1' else 650+50*lv
     m['value']=re.sub(r'Range: \d+\.',f'Range: {r}.',m['value'])
     if code=='ATf1':m['value']=m['value'].replace('1450 range',f'{r} range')
 if 'ATfg' in idx:
  for key in ['aart','arar']:put(idx['ATfg'],key,'ReplaceableTextures\\CommandButtons\\BTNLoadedDice.tga',3,0)
 if 'ATfb' in idx:
  for lv,duration in enumerate([10,13,15],1):put(idx['ATfb'],'aub1',f'Reveal the entire map and invisible units for {duration} seconds. Gate may teleport once during this time after a 2-second channel. Teleporting does not end the reveal. Cooldown: {165-15*lv} sec.',3,lv)
 if 'ATfc' in idx:
  e=idx['ATfc'];e['oldId']='ANcl';e['mods']=[m for m in e['mods'] if not m['id'].startswith('Ebl')]
  for k,v,t in [('aani','spell',3),('acat','',3),('atat','',3),('aeat','',3),('acap','',3)]:put(e,k,v,t,0)
  for k,v,t,ptr in [('Ncl1',2.,2,1),('Ncl2',2,0,2),('Ncl3',1,0,3),('Ncl4',2.,2,4),('Ncl5',0,0,5),('Ncl6','blink',3,6),('aran',5500.,2,0),('acas',0.,2,0)]:put(e,k,v,t,1,ptr)
  put(e,'aub1','Channel visibly for 2 seconds, then teleport once to a walkable destination within 5500 range. Destiny remains on cooldown; its full-map reveal and detection continue for the full 10/13/15 seconds.',3,1)
# Dedicated invisible, invulnerable detection dummies; do not modify existing Atru.
units=objects['war3map.w3u'];u=copy.deepcopy(index(units)['htf3']);u['newId']='ht46'
for m in u['mods']:m['end']='00000000'
for k,v,t in [('uabi','At46,Aloc,Avul',3),('umdl','',3),('usid',0,0),('usin',0,0),('umvh',0.,2),('umvf',0.,2),('unam','Destiny Detection',3)]:put(u,k,v,t)
units['tables'][1].append(u)
ab=objects['war3map.w3a'];e=dict(oldId='Atru',newId='At46',flags=1,extra=0,mods=[])
for k,v,t,lv,ptr in [('anam','Destiny Detection',3,0,0),('aare',1400.,2,1,0),('Det1',1,0,1,1),('atar','air,ground,enemy,neutral,invulnerable,vulnerable',3,1,0)]:put(e,k,v,t,lv,ptr)
ab['tables'][1].append(e)
for n,o in objects.items():data=objdata.dump(o);validate(data,n.endswith('.w3a'));(S/n).write_bytes(data)
s=(S/'war3map.j').read_text(encoding='utf-8-sig');before=s
s=s.replace('hashtable TF45_Gate=InitHashtable()','hashtable TF45_Gate=InitHashtable()\n    hashtable TF46_H=InitHashtable()\n    real array TF46_ZRange')
def replace(n,f):
 global s
 s=s.replace(functions(s)[n],f,1)
f=functions(s)['TFP_wildCards___c'].replace('            set owner=GetOwningPlayer(tU)','            set owner=GetOwningPlayer(tU)')
anchor='            set tempDat=TFP_s__wildCards___cardDat__allocate()'
f=f.replace(anchor,anchor+"\n            set TF46_ZRange[tempDat]=1400.+50.*I2R(GetUnitAbilityLevel(tU,'ATf1'))")
replace('TFP_wildCards___c',f)
replace('TFP_wildCards___p',functions(s)['TFP_wildCards___p'].replace('>= TFP_wildCards___TOTAL_DISTANCE','>= TF46_ZRange[tempDat]'))
new=functions((R/'reveal.j').read_text())
replace('TFP_destiny___c',new['TF46_RevealEnd']+'\n\n'+new['TFP_destiny___c'])
replace('TFP_destiny___gateC',new['TFP_destiny___gateC'])
f=functions(s)['TF45_GateStart'].replace('        set t=CreateTimer()','        call SaveReal(TF45_Gate,h,5,x)\n        call SaveReal(TF45_Gate,h,6,y)\n        set t=CreateTimer()')
f=f.replace('        call SetUnitAnimation(u,"spell")','        call SetUnitAnimation(u,"spell")\n        call QueueUnitAnimation(u,"spell")')
replace('TF45_GateStart',f)
for code in ['ATf1','ATf2']:
 for lv in range(6):
  r=1450+50*lv if code=='ATf1' else 700+50*lv
  pattern=r'(BlzSetAbilityResearchExtendedTooltip\(\''+code+r"', \")(.*?)(\", "+str(lv)+r'\))'
  s=re.sub(pattern,lambda m:m[1]+re.sub(r'Range: \d+\.',f'Range: {r}.',m[2]).replace('1450 range',f'{r} range')+m[3],s)
for lv,d in enumerate([10,13,15]):
 s=re.sub(r'(BlzSetAbilityResearchExtendedTooltip\(\'ATfb\', ")[^"]*(", '+str(lv)+r'\))',lambda m:m[1]+f'Reveal the entire map, including invisible units, for {d} seconds. Gate teleports once after a 2-second channel. Reveal continues after teleport. Cooldown: {150-15*lv} sec.'+m[2],s)
(S/'war3map.j').write_text(s,encoding='utf8')
(S/'war3map.wts').write_bytes((S/'war3map.wts').read_bytes().replace(b'Mundo and Twisted Fate v45c',b'Mundo and Twisted Fate v46'))
assets=[]
for name,folder in [('BTNLoadedDice','CommandButtons'),('DISBTNLoadedDice','CommandButtonsDisabled')]:
 p=S/f'ReplaceableTextures/{folder}/{name}.tga';p.parent.mkdir(parents=True,exist_ok=True)
 icon=Image.open(W/'mundo-polish-v45/assets/loaded-dice.png').convert('RGBA').resize((64,64),Image.Resampling.LANCZOS)
 draw=ImageDraw.Draw(icon);draw.rectangle((0,0,63,63),outline=(15,15,15,255),width=2);draw.rectangle((2,2,61,61),outline=(150,135,100,255),width=1)
 if name.startswith('DIS'):icon=ImageEnhance.Brightness(icon).enhance(.4)
 icon.save(p,compression=None)
 icon.save(R/(name+'.png'))
 assets.append(str(p.relative_to(S)).replace('/','\\'))
imp=(S/'war3map.imp').read_bytes();v,count=struct.unpack_from('<II',imp)
(S/'war3map.imp').write_bytes(struct.pack('<II',v,count+len(assets))+imp[8:]+b''.join(b'\r'+n.encode()+b'\0' for n in assets));names+=assets
bf,af=functions(before),functions(s)
(R/'changes.json').write_text(json.dumps(dict(base=str(base),payloads=names,changed_functions=[n for n in bf if bf[n]!=af[n]],ranges=[700,750,800,850,900,950]),indent=2))
print('v46 prepared: ranges, TGA icons, independent reveal and real channel.')
