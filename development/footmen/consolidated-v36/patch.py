import merge
from merge import R,W,functions,objdata,objects,snapshots,log
import re,json,copy
s=merge.s
def edit(n,old,new):
    global s
    f=functions(s)[n];assert old in f,(n,old)
    s=s.replace(f,f.replace(old,new,1),1)
def insert(n,body):
    global s
    f=functions(s)[n];s=s.replace(f,body+'\n\n'+f,1)
# Preserve gas branch's playable Mundo and colored, persistent trail while keeping
# the later Devour/Undying kit, cleaver pickup and poison resistance.
edit('MF_InitHeroPolicy',"        call SetPlayerTechMaxAllowed(Player(i), 'HMu1', 0)\n",'')
edit('MF_HeroDisabled'," or id == 'HMu1'",'')
assert 'set udg_hero_category[95]=0' in s
s=s.replace('set udg_hero_category[95]=0','set udg_hero_category[95]=15',1)
gas=functions((W/'mundo-gas/abilities.j').read_text())
insert('MU_OnCast',gas['MU_GasExpire']+'\n\n'+gas['MU_GasSpawn'])
edit('MU_OnCast','            call SaveEffectHandle(MU_Hash, h, 6, AddSpecialEffectTarget("Abilities\\\\Spells\\\\Undead\\\\PlagueCloud\\\\PlagueCloudCaster.mdl", u, "chest"))',
     '            call SaveReal(MU_Hash, h, 20, MU_Now + 0.5)\n            call MU_GasSpawn(u, rank)')
f=functions(s)['MU_TickHero'];start=f.index('                set targets = CreateGroup()');end=f.index('                call DestroyGroup(targets)',start)+len('                call DestroyGroup(targets)')
s=s.replace(f,f[:start]+'''                if LoadReal(MU_Hash, h, 20) <= MU_Now then
                    call MU_GasSpawn(u, rank)
                    call SaveReal(MU_Hash, h, 20, MU_Now + 0.5)
                endif'''+f[end:],1)
cloud=next(e for t in objdata.load(str(snapshots['gas']/'war3map.w3a'))['tables'] for e in t if e['newId']=='AMug')
objects['w3a']['tables'][1].append(copy.deepcopy(cloud))
# Keep the kit's controls and resistance text; clarify the restored trail behavior.
for e in objects['w3a']['tables'][1]:
    if e['newId']=='AMu2':
        for m in e['mods']:
            if m['id'] in ('aub1','arut'):
                m['value']+='|nLeaves rank-colored poison clouds for 3 seconds; poison lingers for 2 seconds.'
f=functions(s)['MU_Init']
f2=re.sub(r'(call BlzSetAbilityResearchExtendedTooltip\(\x27AMu2\x27, ")(.*?)(", \d+\))',lambda m:m[1]+m[2]+'|nLeaves rank-colored poison clouds for 3 seconds; poison lingers for 2 seconds.'+m[3],f)
s=s.replace(f,f2,1)
# Twelve-player port: normal wave counts and 90-second countdown are retained.
s=s.replace('\nendglobals','''
boolean F35_MassReleased=false
integer array F35_PlayerStaged
unit array F35_MassPool
integer F35_MassPoolCount=0
endglobals''',1)
mf=functions((R/'mass.j').read_text())
insert('FFGS_SpawnForPlayer',mf['F35_MassEnabled']+'\n\n'+mf['F35_StageFootman']+'\n\n'+mf['F35_ReleaseMass'])
edit('FFGS_SpawnForPlayer','    local integer i = 1','    local integer i = 1\n    local boolean stage=idx == 0 and not F35_MassReleased and F35_MassEnabled()')
edit('FFGS_SpawnForPlayer','        set ffgs_new_unit[i] = CreateUnit(p, udg_spawn_unit[idx], x, y, bj_UNIT_FACING)',
     '        set ffgs_new_unit[i] = CreateUnit(p, udg_spawn_unit[idx], x, y, bj_UNIT_FACING)\n        if stage then\n            call F35_StageFootman(ffgs_new_unit[i], pn)\n        endif')
edit('FFR7_ApplyMassSpeed','or udg_mode_no_mass then','or udg_mode_no_mass or IsUnitHidden(u) then')
# Count hidden staged units regardless of native enumeration behavior, without double counting.
edit('FFGS_CountLivingOfType','    local integer n','    local integer n\n    local integer i=0\n    local unit u')
edit('FFGS_CountLivingOfType','    call GroupClear(ffgs_count_group)', '''    loop
        exitwhen i >= F35_MassPoolCount
        set u=F35_MassPool[i]
        if GetUnitTypeId(u) == unitId and GetWidgetLife(u) > 0.405 and GetOwningPlayer(u) == whichPlayer and not IsUnitInGroup(u, ffgs_count_group) then
            set n=n + 1
        endif
        set i=i + 1
    endloop
    set u=null
    call GroupClear(ffgs_count_group)''')
edit('Trig_keep_footy_in_base_Conditions','    if ( not ( TimerGetRemaining', '''    if F35_MassEnabled() and IsUnitHidden(GetTriggerUnit()) then
        return false
    endif
    if ( not ( TimerGetRemaining''')
insert('Trig_Mass_START_Actions',mf['F35_MassPoint'])
edit('Trig_Mass_START_Actions','        // AUTO BEASTSCROLL','        call F35_ReleaseMass()\n        // AUTO BEASTSCROLL')
edit('Trig_Mass_START_Actions','                set udg_temp_point=udg_player_start[udg_X_playernumber]','                set udg_temp_point=F35_MassPoint(udg_X_playernumber)')
edit('Trig_Mass_START_Actions',"                call CreateNUnitsAtLoc(1, 'h01K', ConvertedPlayer(udg_X_playernumber), udg_temp_point, bj_UNIT_FACING)","                call CreateNUnitsAtLoc(1, 'h01K', ConvertedPlayer(udg_X_playernumber), udg_temp_point, bj_UNIT_FACING)\n                call RemoveLocation(udg_temp_point)")
edit('Trig_Mass_START_Actions','\nendfunction','\n    call F35_ReleaseMass()\nendfunction')
s=re.sub(r'FF799X - Twisted Fate v33','FF799X - Consolidated InstaMass v36',s)
(R/'src/war3map.j').write_text(s,encoding='utf8')
for ext,d in objects.items():(R/'src'/('war3map.'+ext)).write_bytes(objdata.dump(d))
p=R/'src/war3map.wts';b=p.read_bytes();assert b'Twisted Fate v33' in b;p.write_bytes(b.replace(b'Twisted Fate v33',b'Consolidated InstaMass v36'))
print('Merged script and Pub insta-mass prepared.')
