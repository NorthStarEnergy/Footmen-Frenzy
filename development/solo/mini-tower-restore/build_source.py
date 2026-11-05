from pathlib import Path
import re,struct,json,sys
R=Path(__file__).parent
sys.path.insert(0,str(R/'tools'))
import objdata
B=R/'base/files'; O=R/'src';O.mkdir(exist_ok=True)
s=(B/'war3map.j').read_text(encoding='utf-8-sig')
def fn(name,body):
 global s
 pat=r'function '+re.escape(name)+r' takes .*?\nendfunction'
 s,n=re.subn(pat,lambda _:body.strip(),s,count=1,flags=re.S);assert n==1,name
def insert_before(name,txt):
 global s
 needle='function '+name+' takes';assert needle in s;s=s.replace(needle,txt+'\n\n'+needle,1)
slots=[0,2,3,5,6,8,9,11]
starts={0:(-1856,2240),2:(-2496,1600),3:(1856,2240),5:(2496,1600),6:(2496,-2112),8:(1856,-2752),9:(-2496,-2112),11:(-1856,-2752)}
# Retain original canonical team IDs so every existing three-slot team lookup stays valid.
slotbody='function InitCustomPlayerSlots takes nothing returns nothing\n'
for i in range(24):
 if i in slots:
  slotbody+=f'''    call SetPlayerStartLocation(Player({i}), {i})
    call ForcePlayerStartLocation(Player({i}), {i})
    call SetPlayerColor(Player({i}), ConvertPlayerColor({i}))
    call SetPlayerRacePreference(Player({i}), RACE_PREF_HUMAN)
    call SetPlayerRaceSelectable(Player({i}), false)
    call SetPlayerController(Player({i}), MAP_CONTROL_USER)
'''
 else: slotbody+=f'    call SetPlayerController(Player({i}), MAP_CONTROL_NONE)\n'
fn('InitCustomPlayerSlots',slotbody+'endfunction')
team='function InitCustomTeams takes nothing returns nothing\n'
for t in range(4):
 a,b=t*3,t*3+2
 for x,y in [(a,b),(b,a)]:
  team+=f'''    call SetPlayerTeam(Player({x}), {t})
    call SetPlayerState(Player({x}), PLAYER_STATE_ALLIED_VICTORY, 1)
    call SetPlayerAllianceStateAllyBJ(Player({x}), Player({y}), true)
    call SetPlayerAllianceStateVisionBJ(Player({x}), Player({y}), true)
'''
fn('InitCustomTeams',team+'endfunction')
fn('InitAllyPriorities','function InitAllyPriorities takes nothing returns nothing\nendfunction')
config='''function config takes nothing returns nothing
    call SetMapName("Mini Foots v7")
    call SetMapDescription("Four teams of two. Heroes level 10, tech T2, attack/defense 5/5, one of each creep per team. Full-team mass in the middle.")
    call SetPlayers(8)
    call SetTeams(4)
    call SetGamePlacement(MAP_PLACEMENT_TEAMS_TOGETHER)
'''
for i,(x,y) in starts.items():config+=f'    call DefineStartLocation({i}, {x}.0, {y}.0)\n'
config+='    call InitCustomPlayerSlots()\n    call InitCustomTeams()\nendfunction'
fn('config',config)
# Four original outer towers: move the removed slot's pair to its surviving captain.
# Delete all overlapping upgrade-shop instances, then add one per retained slot on every team.
for i in range(12):
 name=f'CreateBuildingsForPlayer{i}'
 m=re.search(r'function '+name+r' takes .*?\nendfunction',s,re.S); body=m.group()
 body=re.sub(r"^    set u=BlzCreateUnitWithSkin\(p, 'n003'.*\n    call SetUnitColor\(u, ConvertPlayerColor\(12\)\)\n",'',body,flags=re.M)
 if i%3==0:
  body=re.sub(r"^    set .*BlzCreateUnitWithSkin\(p, 'hwtw'.*\n",'',body,flags=re.M)
 elif i%3==1:
  body=re.sub(r"(BlzCreateUnitWithSkin)\(p, 'hwtw'",rf"\1(Player({i-1}), 'hwtw'",body)
 fn(name,body)
# Restored original edge tower pads from Mini Foots v2.
towercoords={0: [(-1728, 2752), (-1216, 2752)], 2: [(-3008, 960), (-3008, 1472)], 3: [(1728, 2752), (1216, 2752)], 5: [(3008, 960), (3008, 1472)], 6: [(3008, -1472), (3008, -1984)], 8: [(1728, -3264), (1216, -3264)], 9: [(-3008, -1984), (-3008, -1472)], 11: [(-1216, -3264), (-1728, -3264)]}
towerused={slot:0 for slot in slots}
for i in range(12):
 name=f'CreateBuildingsForPlayer{i}'
 body=re.search(r'function '+name+r' takes .*?\nendfunction',s,re.S).group()
 def place_tower(m):
  owner=i if m[1]=='p' else int(m[2])
  x,y=towercoords[owner][towerused[owner]];towerused[owner]+=1
  return f"BlzCreateUnitWithSkin({m[1]}, 'hwtw', {x}.0, {y}.0, 270.000, 'hwtw')"
 body=re.sub(r"BlzCreateUnitWithSkin\((p|Player\((\d+)\)), 'hwtw', [^\n]+?\)",place_tower,body)
 fn(name,body)
assert all(n==2 for n in towerused.values())
shopcoords=[(-2752,3008),(3264,2496),(2752,-3520),(-3264,-3008)]
for i in slots:
 x,y=shopcoords[i//3]
 name=f'CreateBuildingsForPlayer{i}'
 m=re.search(r'function '+name+r' takes .*?\nendfunction',s,re.S)
 body=m.group().replace('\nendfunction',f"\n    set u=BlzCreateUnitWithSkin(p, 'n003', {x}.0, {y}.0, 270.0, 'n003')\n    call SetUnitColor(u, ConvertPlayerColor(12))\nendfunction")
 fn(name,body)
# Keep the internal force roster at two members while retaining canonical slot numbering.
for removed in [1,4,7,10]:
 s=s.replace(f'    call ForceAddPlayerSimple(Player({removed}), udg_team[{removed//3+1}])\n','')
# Object tier closure and upgrade caps.
u=objdata.load(str(B/'war3map.w3u'));q=objdata.load(str(B/'war3map.w3q'))
es={e['newId'] if e['newId']!='\0'*4 else e['oldId']:e for tab in u['tables'] for e in tab}
mods=lambda e:{m['id']:m['value'] for m in e['mods']}
baseids=set(re.findall(r"set udg_base_type\[\d+\]='(....)'",s))
allowed={i for i in baseids if i=='hbar' or mods(es[i]).get('ureq') in ['R00D','R00G']}
blocked=baseids-allowed
for id in baseids:
 for m in es[id]['mods']:
  if m['id']=='uupt':m['value']=','.join(i for i in m['value'].split(',') if i not in blocked)
for tab in q['tables']:
 for e in tab:
  if e['oldId'] in ['Rhme','Rhar']:
   for m in e['mods']:
    if m['id']=='glvl':m['value']=5
(O/'war3map.w3u').write_bytes(objdata.dump(u));(O/'war3map.w3q').write_bytes(objdata.dump(q))
# Suppress the actual T3 grant, not just its research button.
fn('Trig_Tech_Delay_T3_Actions','function Trig_Tech_Delay_T3_Actions takes nothing returns nothing\n    call DestroyTrigger(GetTriggeringTrigger())\nendfunction')
fn('Trig_Tech_Delay_T3_Func003A','function Trig_Tech_Delay_T3_Func003A takes nothing returns nothing\nendfunction')
# Complete creep catalog: every purchasable nonhero, excluding page-navigation dummy units.
pageblock=s[s.index('function Trig_page_system_Func004'):s.index('function Trig_page_system_Actions')]
pages=set(re.findall(r"GetUnitTypeId\(udg_temp_unit\) == '(....)'",pageblock))
creeps=set()
for e in es.values():
 for id in mods(e).get('useu','').split(','):
  if len(id)==4 and id[0].islower() and id not in pages:creeps.add(id)
oldlimits=s[s.index('function Trig_limit_amount_of_creeps_Func011Func001Func001C'):s.index('function Trig_limit_amount_of_creeps_Func011C')]
creeps.update(re.findall(r"GetUnitTypeId\(udg_temp_unit\) == '(....)'",oldlimits))
creeps.discard('u01C')
insert_before('Trig_limit_amount_of_creeps_Actions','function MF_IsCreep takes integer id returns boolean\n    return '+' or '.join(f"id == '{c}'" for c in sorted(creeps))+'\nendfunction')
costs="function MF_CreepGold takes integer id returns integer\n"
for c in sorted(creeps):
 if c in es and 'ugol' in mods(es[c]):
  costs+=f"    if id == '{c}' then\n        return {mods(es[c])['ugol']}\n    endif\n"
costs+="    return 0\nendfunction"
insert_before('Trig_limit_amount_of_creeps_Actions',costs)
fn('Trig_limit_amount_of_creeps_Actions','''function Trig_limit_amount_of_creeps_Actions takes nothing returns nothing
    local unit bought=GetSoldUnit()
    local unit other
    local player buyer
    local group g
    local integer count=0
    local integer id=GetUnitTypeId(bought)
    local integer slot
    local integer cost
    local string name
    if not MF_IsCreep(id) then
        set bought=null
        return
    endif
    call SoloSub_ReownToSlot(bought)
    set buyer=GetOwningPlayer(bought)
    set slot=GetPlayerId(buyer)
    set cost=MF_CreepGold(id)
    if cost <= 0 then
        set cost=BlzGetUnitIntegerField(bought, UNIT_IF_LUMBER_BOUNTY_AWARDED_BASE)
    endif
    set udg_temp_unit=bought
    set udg_creep_gold_cost=cost
    call BlzSetUnitIntegerField(bought, UNIT_IF_LUMBER_BOUNTY_AWARDED_BASE, 0)
    // Enumerate both players explicitly: hidden, transported or distant creeps also count.
    set slot=(slot / 3) * 3
    set g=CreateGroup()
    call GroupEnumUnitsOfPlayer(g, Player(slot), null)
    loop
        set other=FirstOfGroup(g)
        exitwhen other == null
        call GroupRemoveUnit(g, other)
        if GetUnitTypeId(other) == id and GetWidgetLife(other) > 0.405 and not IsUnitType(other, UNIT_TYPE_DEAD) then
            set count=count + 1
        endif
    endloop
    call GroupEnumUnitsOfPlayer(g, Player(slot + 2), null)
    loop
        set other=FirstOfGroup(g)
        exitwhen other == null
        call GroupRemoveUnit(g, other)
        if GetUnitTypeId(other) == id and GetWidgetLife(other) > 0.405 and not IsUnitType(other, UNIT_TYPE_DEAD) then
            set count=count + 1
        endif
    endloop
    call DestroyGroup(g)
    if count > 1 then
        set name=GetUnitName(bought)
        call RemoveUnit(bought)
        call SetPlayerState(buyer, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(buyer, PLAYER_STATE_RESOURCE_GOLD) + cost)
        call DisplayTimedTextToPlayer(buyer, 0, 0, 8, "Mini Foots: one living " + name + " per team. Refunded " + I2S(cost) + " gold.")
    endif
    set bought=null
    set other=null
    set buyer=null
    set g=null
endfunction''')
# Globals and mass pool, populated on the unchanged pre-mass spawn schedule.
s=s.replace('\nendglobals','''\n// Mini Foots: invisible, paused middle formations released together.
boolean MF_MassReleased=false
integer array MF_MassRemainder
integer array MF_TeamStaged
unit array MF_MassPool
integer MF_MassPoolCount=0
endglobals''',1)
stage='''function MF_StageFootman takes unit u, integer pn returns nothing
    local integer team=(pn - 1) / 3
    local integer n=MF_TeamStaged[team]
    local real x=160.0 + I2R(ModuloInteger(n, 10)) * 72.0
    local real y=160.0 + I2R(n / 10) * 72.0
    if team == 0 or team == 3 then
        set x=-x
    endif
    if team == 2 or team == 3 then
        set y=-y
    endif
    call ShowUnit(u, false)
    call PauseUnit(u, true)
    call SetUnitInvulnerable(u, true)
    call SetUnitUseFood(u, false)
    call SetUnitPathing(u, false)
    call SetUnitX(u, ffgs_center_x + x)
    call SetUnitY(u, ffgs_center_y + y)
    set MF_TeamStaged[team]=n + 1
    set MF_MassPool[MF_MassPoolCount]=u
    set MF_MassPoolCount=MF_MassPoolCount + 1
endfunction

function MF_ReleaseMass takes nothing returns nothing
    local integer i=0
    local integer pn
    local unit u
    if MF_MassReleased then
        return
    endif
    set MF_MassReleased=true
    loop
        exitwhen i >= MF_MassPoolCount
        set u=MF_MassPool[i]
        set pn=GetPlayerId(GetOwningPlayer(u)) + 1
        if GetUnitTypeId(u) != 0 and GetWidgetLife(u) > 0.405 and udg_player_active[pn] then
            call FFGS_ComputeStats(0, pn)
            call FFGS_ApplyUnit(u, 0, pn)
            call SetUnitPathing(u, true)
            call SetUnitUseFood(u, true)
            call SetUnitInvulnerable(u, false)
            call UnitRemoveAbility(u, 'Avul')
            call ShowUnit(u, true)
            call FFR7_ApplyMassSpeed(u)
            call PauseUnit(u, false)
            if udg_autosend[pn] then
                call IssuePointOrder(u, "attack", ffgs_center_x, ffgs_center_y)
            endif
        else
            call RemoveUnit(u)
        endif
        set MF_MassPool[i]=null
        set i=i + 1
    endloop
    set MF_MassPoolCount=0
    set u=null
endfunction'''
insert_before('FFGS_SpawnForPlayer',stage)
fn('FFGS_SpawnForPlayer','''function FFGS_SpawnForPlayer takes integer idx, integer pn, integer count returns nothing
    local player p=ConvertedPlayer(pn)
    local real x=GetUnitX(udg_base[pn])
    local real y=GetUnitY(udg_base[pn])
    local integer i=1
    local integer scaled
    local boolean stage=(idx == 0 and not MF_MassReleased)
    if stage then
        // 3/2 per player. Complementary remainders give exactly three players' total per team.
        set scaled=count * 3 + MF_MassRemainder[pn]
        set count=scaled / 2
        set MF_MassRemainder[pn]=ModuloInteger(scaled, 2)
        set x=ffgs_center_x
        set y=ffgs_center_y
    endif
    loop
        exitwhen i > count
        set ffgs_new_unit[i]=CreateUnit(p, udg_spawn_unit[idx], x, y, bj_UNIT_FACING)
        if stage then
            call MF_StageFootman(ffgs_new_unit[i], pn)
        endif
        set i=i + 1
    endloop
    call FFGS_ComputeStats(idx, pn)
    set i=1
    loop
        exitwhen i > count
        call FFGS_ApplyUnit(ffgs_new_unit[i], idx, pn)
        set ffgs_new_unit[i]=null
        set i=i + 1
    endloop
    set p=null
endfunction''')
# Release AFTER original invulnerability/autosend passes so mass speed isn't applied twice.
# The inherited automatic roar must be cast in the formation, not at the now-empty bases.
point='function MF_MassPoint takes integer pn returns location\n'
for team in range(4):
 x=-484 if team in [0,3] else 484
 y=-412 if team in [2,3] else 412
 point+=f'    if (pn - 1) / 3 == {team} then\n        return Location(ffgs_center_x + {x}.0, ffgs_center_y + {y}.0)\n    endif\n'
point+='    return Location(ffgs_center_x, ffgs_center_y)\nendfunction'
insert_before('Trig_Mass_START_Actions',point)
m=re.search(r'function Trig_Mass_START_Actions takes .*?\nendfunction',s,re.S)
fn('Trig_Mass_START_Actions',m.group().replace('\nendfunction','\n    call MF_ReleaseMass()\nendfunction').replace('set udg_temp_point=udg_player_start[udg_X_playernumber]','set udg_temp_point=MF_MassPoint(udg_X_playernumber)').replace("call CreateNUnitsAtLoc(1, 'h01K', ConvertedPlayer(udg_X_playernumber), udg_temp_point, bj_UNIT_FACING)","call CreateNUnitsAtLoc(1, 'h01K', ConvertedPlayer(udg_X_playernumber), udg_temp_point, bj_UNIT_FACING)\n                call RemoveLocation(udg_temp_point)"))
# Original mass helper skips hidden units in GroupEnum; no stacking speed boosts on hidden pool.
s=s.replace("if u == null or not udg_mass_active or udg_mode_no_mass then","if u == null or not udg_mass_active or udg_mode_no_mass or IsUnitHidden(u) then",1)
# Apply limits before the game starts and prevent old base-confinement movement of the staged pool.
init='''function MF_Init takes nothing returns nothing
    local integer i=0
    call DisableTrigger(gg_trg_keep_footy_in_base)
    call DisableTrigger(gg_trg_Tech_Delay_T3)
    loop
        exitwhen i >= 12
        call SetPlayerTechMaxAllowed(Player(i), 'Rhme', 5)
        call SetPlayerTechMaxAllowed(Player(i), 'Rhar', 5)
        call SetPlayerTechMaxAllowed(Player(i), 'R00E', 0)
'''
for id in sorted(blocked):init+=f"        call SetPlayerTechMaxAllowed(Player(i), '{id}', 0)\n"
init+='''        // Captains round down, teammates round up when a wave contains an odd count.
        if ModuloInteger(i, 3) == 2 then
            set MF_MassRemainder[i + 1]=1
        endif
        set i=i + 1
    endloop
endfunction'''
insert_before('InitTrig_FF_Runtime',init)
s=s.replace('    call FF_Editor_RunInitialization()','    call FF_Editor_RunInitialization()\n    call MF_Init()',1)
s=s.replace('        // AUTO BEASTSCROLL', '        call MF_ReleaseMass()\n        // AUTO BEASTSCROLL', 1)
exec((R/'revise_gameplay.py').read_text(encoding='utf-8'))
exec((R/'port_orianna.py').read_text(encoding='utf-8'))
exec((R/'hero_policy.py').read_text(encoding='utf-8'))
(O/'war3map.j').write_text(s,encoding='utf-8',newline='\n')
misc=(B/'war3mapMisc.txt').read_bytes().decode('utf-8-sig').replace('MaxHeroLevel=18','MaxHeroLevel=10')
(O/'war3mapMisc.txt').write_text(misc,encoding='utf-8',newline='\n')
# Metadata: preserve unfamiliar v39 environment fields verbatim, parse player/force records exactly.
r=objdata.Reader((B/'war3map.w3i').read_bytes())
anchor=struct.pack('<6i',24,0,1,1,64,1);assert r.d.count(anchor)==1
r.o=r.d.index(anchor);head=r.d[:r.o];assert r.i32()==24
players=[]
for i in range(24):
 fields=[r.i32() for _ in range(5)];name=r.cstr();xy=[r.f32() for _ in range(2)];masks=[r.i32() for _ in range(4)]
 assert fields[0]==i
 if i in slots:
  xy=starts[i];ally=(i//3)*3+(2 if i%3==0 else 0)
  players.append(struct.pack('<5i',*fields)+name.encode()+b'\0'+struct.pack('<2f4i',*xy,0,1<<ally,0,0))
n=r.i32();assert n==5
forces=[]
for t in range(n):
 flags=r.i32();mask=r.i32();name=r.cstr()
 if t<4:forces.append(struct.pack('<ii',flags,(1<<(t*3))|(1<<(t*3+2)))+f'Team {t+1}'.encode()+b'\0')
tail=r.d[r.o:]
# Store descriptive metadata directly, avoiding stale localized string-table summaries.
head=head.replace(b'TRIGSTR_001\0',b'Mini Foots v7\0').replace(b'TRIGSTR_002\0',b'8 players - 4 teams of 2\0').replace(b'TRIGSTR_3435\0',b'Mini Foots v7 - 8 players, four teams of two. Heroes level 10; T2 maximum; attack/defense 5/5; one of each creep per team; four towers per team.\0')
(O/'war3map.w3i').write_bytes(head+struct.pack('<i',8)+b''.join(players)+struct.pack('<i',4)+b''.join(forces)+tail)
wts=(B/'war3map.wts').read_bytes().decode('utf-8-sig')
for key,value in [('001','Mini Foots v7'),('002','8 players - 4 teams of 2'),('3435','Mini Foots v7: 8 players, four teams of two. Heroes max level 10; tech max T2; attack/defense max 5/5. One living creep of each type per team. Four towers per team. Mass stages invisibly in the middle with 50% more starting footmen per player.')]:
 wts,n=re.subn(r'(STRING '+str(int(key))+r'\s*\{)\s*.*?\s*(\})',lambda m:m[1]+'\n'+value+'\n'+m[2],wts,count=1,flags=re.S);assert n==1
wts=wts.replace('Footmen Frenzy 7.9.9X','Mini Foots v7')
(O/'war3map.wts').write_bytes(wts.encode('utf-8-sig'))
# The inherited preview still advertised twelve starts. Keep only the eight playable markers.
minimap=(B/'war3map.mmp').read_bytes()
ver,num=struct.unpack_from('<2i',minimap);assert len(minimap)==8+num*16
rows=[struct.unpack_from('<3i4B',minimap,8+i*16) for i in range(num)]
oldxy={0:(29,30),2:(29,72),3:(226,30),5:(226,72),6:(226,224),8:(184,224),9:(29,224),11:(71,224)}
newrows=[row for row in rows if row[0]!=2]
for slot in slots:
 found=[row for row in rows if row[0]==2 and tuple(row[1:3])==oldxy[slot]]
 assert len(found)==1,(slot,found)
 x,y=starts[slot]
 # Same world-to-preview scale as the original playable rectangle.
 px=round(29+(x+2560)*197/5120);py=round(30+(2304-y)*194/5056)
 newrows.append((2,px,py,*found[0][3:]))
(O/'war3map.mmp').write_bytes(struct.pack('<2i',ver,len(newrows))+b''.join(struct.pack('<3i4B',*row) for row in newrows))
manifest={'name':'Mini Foots v7','base':'FF799X_Rx_HeroTavern_v1.w3x','mass_reference':'Solo_Foots_v1.8_4P_PRELOAD_TEST07.w3x','slots':slots,'starts':starts,'shops':{i:shopcoords[i//3] for i in slots},'allowed_bases':sorted(allowed),'blocked_bases':sorted(blocked),'creeps':sorted(creeps),'page_dummies_excluded':sorted(pages)}
(R/'changes.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))


