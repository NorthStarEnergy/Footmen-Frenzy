from pathlib import Path
import sys,shutil,re,json,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import archive,storm,read_storm,c,functions
import objdata
base=R/'base.w3x';source=W/'799x-backport/release/FF799X_Rx_OriannaAudio_v27.w3x'
if not base.exists():shutil.copy2(source,base)
O=R/'src';O.mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in ['war3map.j','war3map.w3a','war3map.wts']:(O/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
original=(O/'war3map.j').read_text(encoding='utf-8-sig');s=original
def edit(name,old,new):
 global s
 f=functions(s)[name];assert old in f,name;s=s.replace(f,f.replace(old,new,1),1)
edit('Trig_Guardian_Force_Field_Learn_Actions',"    set udg_Guardian_FF_Detonate='AFFD'\n    call UnitAddAbilityBJ(udg_Guardian_FF_Detonate, GetTriggerUnit())\n    call UnitMakeAbilityPermanent(GetTriggerUnit(), true, udg_Guardian_FF_Detonate)\n    call BlzUnitDisableAbility(GetTriggerUnit(), udg_Guardian_FF_Detonate, true, false)\n",'')
edit('Trig_Guardian_Force_Field_Cast_Actions',"    if ( Trig_Guardian_Force_Field_Cast_Func031C() ) then\n        call BlzUnitDisableAbility(udg_Guardian, 'AFFD', false, false)\n    else\n    endif\n",'')
edit('Trig_Guardian_Force_Field_Loop_Actions',"            if ( Trig_Guardian_Force_Field_Loop_Func001Func003Func003C() ) then\n                call BlzUnitDisableAbility(udg_Guardian_FF_Caster[udg_Guardian_FF_Loop], 'AFFD', true, false)\n            else\n            endif\n",'')
edit('FF_Editor_InitTriggers','    call InitTrig_Guardian_Force_Field_Detonate()\n','')
s=s.replace('FF799X - Orianna Audio v27','FF799X - Guardian v28')
(O/'war3map.j').write_text(s,encoding='utf8')
d=objdata.load(str(O/'war3map.w3a'));e=next(e for t in d['tables'] for e in t if e['newId']=='AFg1')
for m in e['mods']:
 if m['id'] in ['arut','aub1']:
  assert 'use Detonate to clear it early' in m['value'];m['value']=m['value'].replace('; use Detonate to clear it early',' and expires on its own')
(O/'war3map.w3a').write_bytes(objdata.dump(d))
p=O/'war3map.wts';raw=p.read_bytes();assert b'FF799X - Orianna Audio v27' in raw;p.write_bytes(raw.replace(b'FF799X - Orianna Audio v27',b'FF799X - Guardian v28'))
bf,sf=functions(original),functions(s);changed=[n for n in bf if bf[n]!=sf[n]]
assert set(changed)=={'Trig_Guardian_Force_Field_Learn_Actions','Trig_Guardian_Force_Field_Cast_Actions','Trig_Guardian_Force_Field_Loop_Actions','FF_Editor_InitTriggers'},changed
(R/'changes.json').write_text(json.dumps(dict(base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),changed_functions=changed),indent=2))
print('Guardian detonate button removed; fields continue to expire normally.')
