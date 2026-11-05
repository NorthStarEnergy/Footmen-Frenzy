from pathlib import Path
import sys,json,re,struct
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
from validate_objdata import validate
import objdata
base=W/'tf-raven-v45b/release/FF799X_Rx_Mundo_TF_Raven_v45b.w3x'
names=['war3map.j','war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3mapSkin.w3a','war3map.wts','war3map.imp']
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for n in names:(S/n).write_bytes(read_storm(h,n))
assert storm.SFileCloseArchive(h)
def put(e,k,v,t,lv=None):
 m=next((m for m in e['mods'] if m['id']==k and (lv is None or m.get('level')==lv)),None)
 if m:m.update(value=v,type=t)
 else:
  m=dict(id=k,value=v,type=t,end='00000000');e['mods'].append(m)
  if lv is not None:m.update(level=lv,ptr=0)
ranges=[1000,1025,1050,1075,1100,1150]
for n in names[1:5]:
 o=objdata.load(str(S/n))
 for table in o['tables']:
  for e in table:
   code=e['newId'] if e['newId']!='\0'*4 else e['oldId']
   if code=='htf1':put(e,'umdl','war3mapImported\\TFOrb.mdx',3)
   if code in ['ATf6','ATf7','ATf8']:
    for lv,r in enumerate(ranges,1):put(e,'aran',float(r),2,lv)
   if code in ['ATf1','ATf2','ATf3','ATf4','ATf5','ATf6','ATf7','ATf8']:
    for m in e['mods']:
     if m['type']==3 and m['id'] in ['aub1','arut']:
      m['value']=m['value'].replace('homing card','homing orb').replace('three piercing cards','three small piercing orbs with short trails')
      lv=max(1,m.get('level',1));m['value']=m['value'].replace('Range: 700.',f'Range: {ranges[lv-1]}.')
 data=objdata.dump(o);validate(data,n.endswith('.w3a'));(S/n).write_bytes(data)
s=(S/'war3map.j').read_text(encoding='utf-8-sig');before=s
for name in ['TF33_Cast','TF33_Close']:
 f=functions(s)[name]
 f='\n'.join(line for line in f.split('\n') if not any(x in line for x in ['local texttag tag','set tag=','SetTextTagPermanent','SaveTextTagHandle','DestroyTextTag']))
 s=s.replace(functions(s)[name],f,1)
f='''function TF33_Show takes unit c returns nothing
    local integer h=GetHandleId(c)
    local unit orb=LoadUnitHandle(TF33_H,h,2)
    call SetUnitX(orb,GetUnitX(c))
    call SetUnitY(orb,GetUnitY(c))
    call SetUnitFlyHeight(orb,GetUnitFlyHeight(c)+330.,0.)
    call SetUnitScale(orb,1.1,1.1,1.1)
    call TF33_Tint(orb,LoadInteger(TF33_H,h,4))
    set orb=null
endfunction'''
s=s.replace(functions(s)['TF33_Show'],f,1)
for lv,r in enumerate(ranges):
 s=re.sub(r'(BlzSetAbilityResearchExtendedTooltip\(\'ATf2\', ")(.*?)(", '+str(lv)+r'\))',lambda m:m[1]+m[2].replace('homing card','homing orb').replace('Range: 700.',f'Range: {r}.')+m[3],s)
(S/'war3map.j').write_text(s,encoding='utf8')
(S/'war3map.wts').write_bytes((S/'war3map.wts').read_bytes().replace(b'Mundo and Twisted Fate v45b',b'Mundo and Twisted Fate v45c'))
n='war3mapImported\\TFOrb.mdx';imp=(S/'war3map.imp').read_bytes();v,count=struct.unpack_from('<II',imp);(S/'war3map.imp').write_bytes(struct.pack('<II',v,count+1)+imp[8:]+b'\r'+n.encode()+b'\0');names.append(n)
bf,af=functions(before),functions(s)
(R/'changes.json').write_text(json.dumps(dict(base=str(base),payloads=names,changed_functions=[n for n in bf if bf[n]!=af[n]],ranges=ranges),indent=2))
print('Orb visuals, text-free overhead indicator and all 18 throw ranges updated.')
