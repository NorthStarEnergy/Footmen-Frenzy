"""Guardian v19: aimed burst barriers, lantern and learnable dome."""
import re, copy

def put(e, key, value, level=0, ptr=0):
    e['mods']=[m for m in e['mods'] if (m['id'],m.get('level',0))!=(key,level)]
    m=dict(id=key,type=3 if isinstance(value,str) else 1 if isinstance(value,float) else 0,value=value,end=e['newId'].encode().hex())
    if level or 'level' in e['mods'][0]:m.update(level=level,ptr=ptr)
    e['mods'].append(m)

def patch(s, abilities, units):
    def replace(name, body):
        nonlocal s
        s,n=re.subn(r'^function '+name+r' takes .*?^endfunction',lambda _:body,s,flags=re.M|re.S)
        assert n==1,name
    s=s.replace("'AFOR'", "'AFg1'")
    # Keep the short deferred cooldown reset, but give each placement a clear
    # 0.10s interval; the window timer and last placement both start recovery.
    start=s.index('function GFB_End ');end=s.index('function GFW_Count ',start)
    block=s[start:end].replace('12.0','30.0').replace('set n = 3','set n = 5').replace('TimerStart(t, 2.0','TimerStart(t, 4.0')
    block=block.replace("call BlzEndUnitAbilityCooldown(u, 'AFg1')","call BlzStartUnitAbilityCooldown(u, 'AFg1', 0.10)")
    s=s[:start]+block+s[end:]
    replace('GFW_Count','function GFW_Count takes integer rank returns integer\n    return 1\nendfunction')
    # One round field per click, not a rank-dependent mini-wall.
    start=s.index('function GFW_Create ');end=s.index('function InitTrig_Guardian_Force_Field_Loop ',start)
    block=s[start:end].replace('32.0, PATHING_TYPE_ANY','72.0, PATHING_TYPE_ANY').replace('), 0.30)', '), 0.675)')
    block=block.replace('    call GFB_Cast(GetTriggerUnit())','    call RemoveLocation(udg_Guardian_Point[0])\n    set udg_Guardian_Point[0] = null\n    call GFB_Cast(GetTriggerUnit())')
    # Initialize on cast as well as learn (debug/spawn paths can grant abilities).
    block=block.replace('    set udg_Guardian=GetTriggerUnit()', '    if udg_Guardian_FF_Hash == null then\n        set udg_Guardian_FF_Hash = InitHashtable()\n    endif\n    set udg_Guardian=GetTriggerUnit()',1)
    s=s[:start]+block+s[end:]
    a={e['newId']:e for t in abilities['tables'] for e in t}
    field=copy.deepcopy(a['A0DL']);field['newId']='AFg1'
    field['mods']=[m for m in field['mods'] if m['id'] not in ('atp1','aub1','arut')]
    description='Place up to five individually aimed forcefields within 4 seconds. Recast after 0.1 seconds to draw a line. After the fifth placement or the window expires, recover for 30 seconds. Each field blocks movement; use Detonate to clear it early. Costs 25 mana per field.'
    for k,v in dict(anam='Force Field',ahky='X',arhk='W',abpx=1,arpx=1,aret='Learn Force Field [W]',arut=description,aart=r'ReplaceableTextures\CommandButtons\BTNForceField.blp',arar=r'ReplaceableTextures\CommandButtons\BTNForceField.blp').items():put(field,k,v)
    for level,duration in enumerate([3,3,3.5,4,5,5],1):
        for k,v in dict(amcs=25,acdn=30.0,aran=900.0,atp1=f'Force Field [X] - Level {level}',aub1=description+f' Field duration: {duration} seconds.').items():put(field,k,v,level)
        put(field,'Ncl6','forceofnature',level,6)
    abilities['tables'][1].append(field)
    dome=a['AZd1']
    desc='A moving Guardian Shield dome lasts 15 seconds in a 600 radius. Allies recover 100 HP and 10 mana per second. Enemies are slowed 60% and lose up to 20 mana per second, taking equal spell damage. Magic-immune enemies are unaffected. Does not block projectiles.'
    levelmods=[copy.deepcopy(m) for m in dome['mods'] if m.get('level')==1]
    for level in [2,3]:
        for m in levelmods:m=copy.deepcopy(m);m['level']=level;dome['mods'].append(m)
    for k,v in dict(anam='Guardian Shield',aher=1,alev=3,arlv=6,alsk=5,ahky='V',arhk='R',abpx=3,abpy=2,arpx=3,arpy=0,aret='Learn Guardian Shield [R]',arut=desc+' Cooldown: 60/45/30 seconds.',arar=r'ReplaceableTextures\CommandButtons\BTNDivineIntervention.blp').items():put(dome,k,v)
    for level,cd in enumerate([60.,45.,30.],1):
        put(dome,'acdn',cd,level);put(dome,'atp1',f'Guardian Shield [V] - Level {level}',level);put(dome,'aub1',desc+f' Mana: 100. Cooldown: {int(cd)} seconds.',level)
    for t in units['tables']:
        for e in t:
            if e['newId']=='H043':
                put(e,'uhab','A0DL,AFg1,ATfd,AZd1');put(e,'uabi','AInv');put(e,'ucpt',0.05);put(e,'ucbs',0.05)
    return s, abilities, units
