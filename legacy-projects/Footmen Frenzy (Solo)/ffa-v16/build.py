from pathlib import Path
import sys,struct,re,json,ctypes as c,shutil,subprocess,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive
B=R/'base';O=R/'src'
for d in [B,O,R/'release']:d.mkdir(exist_ok=True)
shutil.copyfile(W/'ffa-v15/release/Solo_Foots_8P_FFA_v15.w3x',R/'baseline.w3x');archive.extract(R/'baseline.w3x',B)
s=(B/'war3map.j').read_text();pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
# Stock GrantNormalXP: 25,40,60,85; subsequent values follow the unchanged recurrence.
# Explicit fourth entry prevents the lower preceding entries reducing tier-four rewards.
misc=(B/'war3mapMisc.txt').read_text();assert 'GrantNormalXP=' not in misc
misc=misc.replace('[Misc]','[Misc]\nGrantNormalXP=25,38,57,85',1);(O/'war3mapMisc.txt').write_text(misc)
s=re.sub(r'^endglobals','hashtable F16_XP=null\nendglobals',s,count=1,flags=re.M)
s+='''
function F16_BonusXP takes unit hero,integer amount returns integer
    local integer key=GetHandleId(hero)
    local integer total
    local integer earned
    if F16_XP==null then
        set F16_XP=InitHashtable()
    endif
    // Integer hundredths avoid repeated floating-point rounding on small awards.
    set total=LoadInteger(F16_XP,key,0)+amount*95
    set earned=total/100
    call SaveInteger(F16_XP,key,0,total-earned*100)
    return earned
endfunction
'''
for suffix,arr,high,low in [('004','udg_ExpInt_Copy','udg_exp_sys_high_Copy','udg_exp_sys_low_Copy'),('005','udg_ExpInt','udg_exp_sys_high','udg_exp_sys_low'),('006','udg_ExpInt_T2','udg_exp_sys_high_T2','udg_exp_sys_low_T2')]:
 name='Trig_Unit_Experience_System_Func'+suffix+'Func012A';old=funcs(s)[name]
 expr=f'( ( {high} - {low} ) / {arr}[0] )'
 assert expr in old;s=s.replace(old,old.replace(expr,'F16_BonusXP(GetEnumUnit(), '+expr+')'))
# Audit authored troop stats; no combat or bounty edits.
rows=[]
for m in re.finditer(r"// ([^\n]+)\nset udg_spawn_unit\[(\d+)\]='(....)'(.*?)(?=//|endfunction)",s,re.S):
 if int(m[2])>25:continue
 stats={k:float(v) for k,v in re.findall(r'set udg_unit_(\w+)\[\d+\]=([\d.]+)',m[4])}
 if stats['level'] not in [2,3]:continue
 rows.append(dict(name=m[1],id=m[3],stats=stats,old_base_xp=40 if stats['level']==2 else 60,new_base_xp=38 if stats['level']==2 else 57))
(R/'unit-stats.json').write_text(json.dumps(rows,indent=2))
title='Solo Foots 8P FFA + King v16';s=re.sub(r'call SetMapName\("[^\"]+"\)',f'call SetMapName("{title}")',s)
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):];tail=tail[:tail.index('# Terrain-derived BLP1 minimaps')]+tail[tail.index('work=Path('):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v16.w3x').replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','')
report={'normal_xp_levels_1_to_4':[25,38,57,85],'affected_troop_types':len(rows),'bonus_multiplier':.95};exec(tail)
for file in ['war3map.w3u','war3map.w3a','war3map.w3t','war3mapUnits.doo','war3map.w3e','war3map.wpm']:
 assert (R/'roundtrip'/file).read_bytes()==(B/file).read_bytes(),file
# Validate exact fractional bonus accumulation across consecutive small kills and multiple heroes.
s=(R/'roundtrip/war3map.j').read_text();helper=(W/'ffa-v4/verify_behavior.py').read_text();exec(helper[helper.index('def translate('):helper.index("translated='")])
code=translate('F16_BonusXP').replace('total/100','total//100');h={};e=dict(F16_XP=None,GetHandleId=lambda u:u,InitHashtable=lambda:h,LoadInteger=lambda h,k,c:h.get((k,c),0),SaveInteger=lambda h,k,c,v:h.__setitem__((k,c),v));exec(code,e)
for hero,amount in enumerate([1,2,4,6,9,18]):
 total=sum(e['F16_BonusXP'](hero,amount) for _ in range(100));assert total==amount*95
assert funcs(s)['Trig_set_spawn_variables_Actions']==funcs((B/'war3map.j').read_text())['Trig_set_spawn_variables_Actions']
assert funcs(s)['Trig_Foot_Exp_system_Actions']==funcs((B/'war3map.j').read_text())['Trig_Foot_Exp_system_Actions']
print('PASS: 5% lower level-2/3 base XP; exact cumulative 95% scripted bonuses; footmen, combat stats, bounty, layouts and object data unchanged.')
