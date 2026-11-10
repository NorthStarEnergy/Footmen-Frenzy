from pathlib import Path
import copy
from guardian import put

def patch(s, abilities):
    s=s.replace('    integer GD_Count = 0','    group GDB_Enum = CreateGroup()\n    location GDB_Loc = Location(0.0, 0.0)\n    integer GD_Count = 0',1)
    pos=s.index('function GDV_Project ')
    s=s[:pos]+Path(__file__).with_name('guardian_bolts.j').read_text()+'\n'+s[pos:]
    s=s.replace('    call GDV_Project(GD_Caster[i], x, y)','    call GDV_Project(GD_Caster[i], x, y)\n    call GDB_Visual(GD_Caster[i])\n    if ModuloInteger(GDV_Step, 15) == 0 then\n        call GDB_Strike(GD_Caster[i], x, y)\n    endif',1)
    s=s.replace('function GDV_Stop takes unit caster returns nothing\n    local integer k = GetHandleId(caster)\n    local integer n = 0','function GDV_Stop takes unit caster returns nothing\n    local integer k = GetHandleId(caster)\n    local integer n = 0\n    call GDB_Clear(caster)',1)
    entries={e['newId']:e for t in abilities['tables'] for e in t}
    icons={'A0DL':'TimeWarp','AFg1':'ForceField','ATfd':'Lantern','AZd1':'GuardianShield'}
    for uid,name in icons.items():
        e=entries[uid]
        for field in ['aart','arar']:put(e,field,'ReplaceableTextures\\CommandButtons\\BTNGuardian'+name+'.blp')
        for m in e['mods']:
            if m['id'] in ['aran','aare','acdn','Ncl1','Ncl4','adur','ahdu'] and m['type']==1:m['type']=2
        if uid in ['A0DL','AFg1','ATfd']:
            for rank in range(1,7):
                put(e,'aran',{'A0DL':1200.,'AFg1':900.,'ATfd':1000.}[uid],rank)
                next(m for m in e['mods'] if m['id']=='aran' and m['level']==rank)['type']=2
    extra=' Every 0.75 seconds a random ally gains 25/30/35 HP, 10 mana and 10% movement speed for 1.5 seconds; a random enemy takes 25/30/35 magic damage, loses up to 10 mana and is slowed 15% for 1.5 seconds.'
    for m in entries['AZd1']['mods']:
        if m['id'] in ['aub1','arut']:m['value']+=extra
    for uid,base,positive in [('AGbs','Ablo',True),('AGbn','Aslo',False)]:
        e=copy.deepcopy(entries['ATfd']);e.update(newId=uid,oldId=base);e['mods']=[]
        # Seed a levelled entry for put().
        e['mods']=[dict(id='alev',type=0,level=0,ptr=0,value=1,end=uid.encode().hex())]
        for k,v in dict(anam='Guardian restoration surge' if positive else 'Guardian disruption',aher=0,aite=0,areq='',aart='',atat='').items():put(e,k,v)
        for k,v in dict(amcs=0,acdn=0.,aran=99999.,adur=1.5,ahdu=1.5,abuf='BGbs' if positive else 'BGbn',atar='friend,ground,air,organic,mechanical' if positive else 'enemy,ground,air,organic,mechanical').items():put(e,k,v,1)
        for field,value,ptr in ([('Blo1',0.,1),('Blo2',.1,2),('Blo3',0.,3)] if positive else [('Slo1',.15,1),('Slo2',0.,2),('Slo3',0,3)]):put(e,field,value,1,ptr)
        for m in e['mods']:
            if m['type']==1:m['type']=2
        abilities['tables'][1].append(e)
    return s,abilities

def buffs(data):
    for uid,base,name,description in [('BGbs','Bblo','Guardian Restoration','Restored by Guardian. Movement speed increased by 10% for 1.5 seconds.'),('BGbn','Bslo','Guardian Disruption','Struck by Guardian. Movement speed reduced by 15% for 1.5 seconds.')]:
        data['tables'][1].append(dict(oldId=base,newId=uid,flags=1,extra=0,mods=[dict(id=k,type=3,value=v,end=uid.encode().hex()) for k,v in [('fnam',name),('ftip',name),('fube',description),('fart','ReplaceableTextures\\CommandButtons\\BTNGuardianGuardianShield.blp'),('ftat','')]]))
    return data
