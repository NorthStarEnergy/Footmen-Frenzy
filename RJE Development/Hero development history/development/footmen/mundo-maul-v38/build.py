from pathlib import Path
import sys,re,json,copy,hashlib,shutil
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions,archive,entries
import objdata
base=W/'799x-backport/release/FF799X_Rx_Consolidated_StatsUI_v37.w3x'
O=R/'src';O.mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for n in ['war3map.j','war3map.w3a','war3map.w3u','war3map.wts']:(O/n).write_bytes(read_storm(h,n))
assert storm.SFileCloseArchive(h)
s=(O/'war3map.j').read_text(encoding='utf-8-sig');original=s
def replace(n,new):
    global s
    s=s.replace(functions(s)[n],new,1)
def edit(n,old,new):
    f=functions(s)[n];assert old in f,(n,old);replace(n,f.replace(old,new,1))
s=s.replace('\nendglobals','\nhashtable MM_Hash=InitHashtable()\nendglobals',1)
fling=functions((W/'mundo-gas/abilities.j').read_text())
# Helpers precede the pre-cast guards. The original fling implementation is reused.
anchor=functions(s)['MD_OnOrder']
s=s.replace(anchor,fling['MU_FlingTick']+'\n\n'+fling['MU_Fling']+'\n\n'+(R/'maul.j').read_text()+'\n\n'+anchor,1)
edit('MD_Reject','Devour: finish your current meal first. Target a non-hero organic ground unit; creeps, Colossals, magic-immune and spell-resistant units cannot be eaten.','Maul: flip an eligible enemy hero or creep, or devour an eligible organic ground unit. Finish your meal before eating another unit. Cannot affect Colossals, flying, mechanical, magic-immune or invulnerable targets; spell-resistant units cannot be eaten.')
replace('MD_OnOrder','''function MD_OnOrder takes nothing returns nothing
    local unit u=GetTriggerUnit()
    if GetUnitTypeId(u) == 'HMu1' and GetIssuedOrderId() == OrderId("devour") then
        if not MM_DevourReady(u, GetOrderTargetUnit()) then
            call MD_Reject(u)
        endif
    endif
    set u=null
endfunction''')
replace('MD_OnChannel','''function MD_OnChannel takes nothing returns nothing
    local unit u=GetTriggerUnit()
    local integer a=GetSpellAbilityId()
    if GetUnitTypeId(u) == 'HMu1' then
        if a == 'AMu3' then
            if not MM_CanCast(u, GetSpellTargetUnit()) then
                call MD_Reject(u)
            endif
        elseif a == 'AMdv' then
            if not MM_DevourReady(u, GetSpellTargetUnit()) then
                call MD_Reject(u)
            endif
        endif
    endif
    set u=null
endfunction''')
edit('MU_OnCast',"        call MD_Start(u, GetSpellTargetUnit(), rank)","        call MM_Cast(u, GetSpellTargetUnit(), rank)\n    elseif spell == 'AMdv' then\n        if MM_DevourReady(u, GetSpellTargetUnit()) then\n            call RemoveSavedHandle(MM_Hash, h, 1)\n            call MD_Start(u, GetSpellTargetUnit(), rank)\n        endif")
a=objdata.load(str(O/'war3map.w3a'));es={e['newId']:e for t in a['tables'] for e in t}
def field(e,key,value,lv=0,ptr=0):
    e['mods']=[m for m in e['mods'] if (m['id'],m.get('level',0))!=(key,lv)]
    e['mods'].append(dict(id=key,type=3 if isinstance(value,str) else 0 if isinstance(value,int) else 1,level=lv,ptr=ptr,value=value,end=e['newId'].encode().hex()))
assert 'AMdv' not in es
proxy=copy.deepcopy(es['AMu3']);proxy['newId']='AMdv'
for m in proxy['mods']:m['end']=b'AMdv'.hex()
for key,val in [('anam','Maul native digestion'),('aher',0),('ahky',''),('arhk',''),('aart',''),('arar','')]:field(proxy,key,val)
for lv in range(1,7):
    field(proxy,'acdn',0.,lv);field(proxy,'aran',250.,lv)
a['tables'][1].append(proxy)
main=es['AMu3'];main['oldId']='ANcl';main['mods']=[m for m in main['mods'] if not m['id'].startswith('Dev')]
field(main,'anam','Maul');field(main,'aani','spell');field(main,'ahky','C')
calls=[]
for lv in range(1,7):
    for k,v in [('amcs',0),('acdn',20.),('aran',250.),('atar','ground,organic,enemy,friend,neutral'),('abuf',''),('adur',0.),('ahdu',0.)]:field(main,k,v,lv)
    for k,v,p in [('Ncl1',0.,1),('Ncl2',1,2),('Ncl3',1,3),('Ncl4',0.,4),('Ncl5',0,5),('Ncl6','acidbomb',6)]:field(main,k,v,lv,p)
    text=f'Enemy heroes and creeps: flip the target behind Mundo, dealing {50+30*(lv-1)} magic damage. Can flip while digesting.|nOther eligible units: swallow one unit; digest for {35+15*lv} damage/sec, healing Mundo for {20+5*lv}% of actual digestion damage. On completion, burp and heal Mundo and nearby allies for {150+50*lv} HP in {250+50*lv} radius. Enemy meals grant normal bounty and shared XP. Allies can be eaten but give no kill rewards.|nCannot affect Colossals, flying, mechanical, magic-immune or invulnerable units. Spell-resistant units cannot be eaten. One meal at a time; unfinished meals are released if Mundo dies.|nMana: 0. Cooldown: 20 sec. Range: 250.'
    title=f'Maul [|cffffcc00C|r] - Level {lv}';learn=f'Learn Maul [|cffffcc00E|r] - Level {lv}'
    research=f'|cffffcc00Requires hero level {1+3*(lv-1)}|r|n|n'+text
    field(main,'atp1',title,lv);field(main,'aub1',text,lv)
    if lv==1:field(main,'aret',learn);field(main,'arut',research)
    calls += [f'    call BlzSetAbilityResearchTooltip(\'AMu3\', "{learn}", {lv-1})',f'    call BlzSetAbilityResearchExtendedTooltip(\'AMu3\', "{research}", {lv-1})']
f=functions(s)['MU_Init'];f=re.sub(r'^.*BlzSetAbilityResearch(?:Extended)?Tooltip\(\x27AMu3\x27.*\n','',f,flags=re.M)
f=f.replace('    set MU_Hash = InitHashtable()','\n'.join(calls)+'\n    set MU_Hash = InitHashtable()',1);replace('MU_Init',f)
(O/'war3map.w3a').write_bytes(objdata.dump(a))
u=objdata.load(str(O/'war3map.w3u'))
for t in u['tables']:
    for e in t:
        if e['newId']=='HMu1':
            for m in e['mods']:
                if isinstance(m['value'],str):m['value']=m['value'].replace('Devour','Maul').replace('devour','maul')
(O/'war3map.w3u').write_bytes(objdata.dump(u));(O/'war3map.j').write_text(s,encoding='utf8')
p=O/'war3map.wts';p.write_bytes(p.read_bytes().replace(b'Consolidated Stats UI v37',b'Consolidated Maul v38'))
af=functions(s);bf=functions(original);changed=[n for n in bf if bf[n]!=af[n]]
assert set(changed)=={'MD_Reject','MD_OnOrder','MD_OnChannel','MU_OnCast','MU_Init'},changed
metadata=dict(base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),changed_functions=changed,added_functions=sorted(af.keys()-bf.keys()))
(R/'changes.json').write_text(json.dumps(metadata,indent=2))
print('Prepared Maul; 5 existing functions changed, native digestion retained.')
