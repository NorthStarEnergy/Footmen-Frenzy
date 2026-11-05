from pathlib import Path
import sys,re
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
base=W/'tf-destiny-v46/release/FF799X_Rx_TF_Destiny_v46.w3x'
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for n in ['war3map.j','war3map.w3a','war3mapSkin.w3a']:(S/n).write_bytes(read_storm(h,n))
assert storm.SFileCloseArchive(h)
s=(S/'war3map.j').read_text(encoding='utf-8-sig')
def edit(name,a,b):
 global s
 f=functions(s)[name];assert a in f,(name,a);s=s.replace(f,f.replace(a,b,1),1)
edit('TFP_wildCards___setCardRandHue','0.85,0.85,0.85','1.35,1.35,1.35')
edit('TF33_Show','1.1,1.1,1.1','1.8,1.8,1.8')
helper='''function TF47_Lock takes unit c, integer color returns nothing
    local integer h=GetHandleId(c)
    local integer id
    call UnitRemoveAbility(c,TFP_s__tfConsts_CARD_ID[LoadInteger(TF33_H,h,4)])
    call SaveInteger(TF33_H,h,4,color)
    call SaveBoolean(TF33_H,h,5,true)
    call SaveInteger(TF33_H,h,6,0)
    if color==0 then
        set id='ATf6'
    elseif color==1 then
        set id='ATf7'
    else
        set id='ATf8'
    endif
    call UnitAddAbility(c,id)
    call SetUnitAbilityLevel(c,id,GetUnitAbilityLevel(c,'ATf2'))
    call TF33_Show(c)
endfunction

'''
s=s.replace('function TF33_SelectTick takes',helper+'function TF33_SelectTick takes',1)
edit('TF33_SelectTick',' or (not LoadBoolean(TF33_H,h,5) and ticks>=120)','')
edit('TF33_SelectTick','''        if not LoadBoolean(TF33_H,h,5) and ModuloInteger(ticks,12)==0 then''','''        if not LoadBoolean(TF33_H,h,5) and ticks>=100 then
            call TF47_Lock(c,GetRandomInt(0,2))
        elseif not LoadBoolean(TF33_H,h,5) and ModuloInteger(ticks,12)==0 then''')
old='''            call SaveBoolean(TF33_H,h,5,true)
            call SaveInteger(TF33_H,h,6,0)
            call UnitRemoveAbility(c,id)
            if color==0 then
                set id='ATf6'
            elseif color==1 then
                set id='ATf7'
            else
                set id='ATf8'
            endif
            call UnitAddAbility(c,id)
            call SetUnitAbilityLevel(c,id,rank)
            call TF33_Show(c)'''
edit('TF33_Cast',old,'            call TF47_Lock(c,color)')
# Explain the selection behavior in the runtime research tooltip.
f=functions(s)['TFP_Init'];f2=re.sub(r'(^.*BlzSetAbilityResearchExtendedTooltip\(\'ATf2\', ")(.*?)(", \d+\).*$)',lambda m:m[1]+m[2]+' If you do not choose within 5 seconds, a random orb locks in.'+m[3],f,flags=re.M);s=s.replace(f,f2,1)
(S/'war3map.j').write_text(s,encoding='utf8')
for n in ['war3map.w3a','war3mapSkin.w3a']:
 o=objdata.load(str(S/n))
 for table in o['tables']:
  for e in table:
   code=e['newId'] if e['newId']!='\0'*4 else e['oldId']
   if code=='ATfg':
    for m in e['mods']:
     if m['id'] in ('aart','arar'):m['value']='ReplaceableTextures\\CommandButtons\\BTNGoldMine.blp'
   if code=='ATf2':
    for m in e['mods']:
     if m['id'] in ('aub1','arut'):m['value']+=' If you do not choose within 5 seconds, a random orb locks in.'
 (S/n).write_bytes(objdata.dump(o))
print('Twisted Fate source, object data, and orb prepared')
