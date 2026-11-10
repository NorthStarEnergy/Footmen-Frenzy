"""Keep World Editor custom script synchronized with the playable JASS."""
from pathlib import Path
import re,struct
R=Path(__file__).parent;O=R/'src'
s=(O/'war3map.j').read_text()
def remove(name):
    global s
    s=re.sub(r'^function '+re.escape(name)+r'\b.*?^endfunction\s*','',s,flags=re.M|re.S)
remove('config');remove('CreateRegions')
s=re.sub(r'^\s*rect\s+gg_rct_\w+\s*=\s*null\s*$', '',s,flags=re.M)
s=re.sub(r'    call (?:CreateRegions|InitBlizzard)\(\s*\)\n','',s)
for name in re.findall(r'^function (\w+)',s,re.M):
    if re.match(r'Create(BuildingsFor|UnitsFor|Neutral|Player)',name):remove(name)
for name in re.findall(r'^function (\w+)',s,re.M):
    if name in ['InitGlobals','InitSounds','CreateCameras','CreateAllUnits','InitCustomTriggers','RunInitializationTriggers','InitCustomPlayerSlots','InitCustomTeams','InitAllyPriorities','main'] or name.startswith('InitUpgrades'):
        s=re.sub(r'\b'+name+r'\b','SFMap_'+name,s)
s=re.sub(r'\bgg_unit_','sf_unit_',s);s=re.sub(r'\bgg_snd_','sf_snd_',s)
s=re.sub(r'^endglobals\s*$', '    group SF_BoundPlacements=null\nendglobals',s,count=1,flags=re.M)
lookup='''function SF_FindPlacement takes player owner, integer kind, real x, real y, real facing, integer skin returns unit
    local group candidates=CreateGroup()
    local unit u
    local unit best=null
    local real distance
    local real closest=1000000000.
    if SF_BoundPlacements==null then
        set SF_BoundPlacements=CreateGroup()
    endif
    call GroupEnumUnitsOfPlayer(candidates,owner,null)
    loop
        set u=FirstOfGroup(candidates)
        exitwhen u==null
        call GroupRemoveUnit(candidates,u)
        if GetUnitTypeId(u)==kind and not IsUnitInGroup(u,SF_BoundPlacements) then
            set distance=(GetUnitX(u)-x)*(GetUnitX(u)-x)+(GetUnitY(u)-y)*(GetUnitY(u)-y)
            if distance<closest then
                set closest=distance
                set best=u
            endif
        endif
    endloop
    call DestroyGroup(candidates)
    if best!=null then
        call GroupAddUnit(SF_BoundPlacements,best)
    endif
    set candidates=null
    set u=null
    return best
endfunction
'''
s=s.replace('function SFMap_CreateAllUnits takes',lookup+'\nfunction SFMap_CreateAllUnits takes',1)
m=re.search(r'^function SFMap_CreateAllUnits\b.*?^endfunction',s,re.M|re.S)
s=s[:m.start()]+m[0].replace('BlzCreateUnitWithSkin','SF_FindPlacement')+s[m.end():]
for k in range(1,13):
    s=re.sub(r'set SF_BaseX\['+str(k)+r'\]=[^\n]+',f'set SF_BaseX[{k}]=GetStartLocationX(GetPlayerStartLocation(Player({k-1})))',s)
    s=re.sub(r'set SF_BaseY\['+str(k)+r'\]=[^\n]+',f'set SF_BaseY[{k}]=GetStartLocationY(GetPlayerStartLocation(Player({k-1})))',s)
    s=re.sub(r'set SF_Angle\['+str(k)+r'\]=[^\n]+',f'set SF_Angle[{k}]=Atan2(SF_BaseY[{k}]+256.,SF_BaseX[{k}])',s)
trigger='''function InitTrig_SoloFootsRuntime takes nothing returns nothing
    set gg_trg_SoloFootsRuntime=CreateTrigger()
    call TriggerAddAction(gg_trg_SoloFootsRuntime,function SFMap_main)
endfunction
'''
def z(v):return v.encode()+b'\0'
def chunk(v):data=z(v);return struct.pack('<I',len(data))+data
wtg=b'WTG!'+struct.pack('<III',7,1,0)+z('Solo Foots Runtime')+struct.pack('<IIII',0,2,0,1)+z('SoloFootsRuntime')+z('Six-player FFA. Gameplay source is synchronized in the map Custom Script header.')+struct.pack('<7I',0,1,1,0,1,0,0)
(O/'war3map.wtg').write_bytes(wtg)
(O/'war3map.wct').write_bytes(struct.pack('<I',1)+z('Solo Foots 6 Player FFA v1 source. Terrain, units and start locations are editable.')+chunk(s)+struct.pack('<I',1)+chunk(trigger))
regions=sorted(set(re.findall(r'\bgg_rct_\w+\b',s)))
decl='    trigger gg_trg_SoloFootsRuntime=null\n'+''.join('    rect '+n+'=null\n' for n in regions)
wrapper=re.sub(r'^globals\s*$',lambda m:'globals\n'+decl,s,count=1,flags=re.M)+ '\n'+trigger+'''\nfunction main takes nothing returns nothing
    call InitBlizzard()
    call InitTrig_SoloFootsRuntime()
    call TriggerExecute(gg_trg_SoloFootsRuntime)
endfunction
function config takes nothing returns nothing
endfunction
'''
(R/'editor-validation.j').write_text(wrapper)
print('Synchronized World Editor script and triggers.')
