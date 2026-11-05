from pathlib import Path
import sys,struct,re,json,ctypes as c,shutil,subprocess,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive
B=R/'base';O=R/'src'
for folder in [B,O,R/'release']:folder.mkdir(parents=True,exist_ok=True)
shutil.copyfile(W/'ffa-v9/release/Solo_Foots_8P_FFA_v9.w3x',R/'baseline.w3x')
archive.extract(R/'baseline.w3x',B)
s=(B/'war3map.j').read_text();pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
def put(n,t):
 global s
 s=s.replace(funcs(s)[n],t)
def inject(n,text,anchor=None):
 f=funcs(s)[n]
 if anchor is None:
  lines=f.splitlines();i=1
  while i<len(lines) and (lines[i].strip().startswith('local ') or not lines[i].strip()):i+=1
  lines.insert(i,text);put(n,'\n'.join(lines))
 else:put(n,f.replace(anchor,text+'\n'+anchor,1))
donor=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots\audit\solo-latest-test05\files\war3map.j').read_text()
df=funcs(donor)
globals_=re.findall(r'^(?:boolean|integer|real|unit|timer|button)(?: array)? SK[^\n]*',donor,re.M)
globals_+='''dialog SKModeDialog=null
button SKFfaButton=null
timer SKModeTimeout=null
player SKModeHost=null
boolean SKModeChosen=false
fogmodifier array SKBaseVision
fogmodifier array SF_EliminatedVision
'''.splitlines()
s=re.sub(r'^endglobals',lambda m:'\n'.join(globals_)+'\nendglobals',s,count=1,flags=re.M)
selected={n for n in df if n.startswith('SK')}
s+='\n'+'\n\n'.join(df[n] for n in df if n in selected)+'\n'+(R/'integration.j').read_text()
# Roster adapters keep base/player indices separate from kingdom membership.
put('SKActive','''function SKActive takes integer pn returns boolean
    if pn<1 or pn>12 then
        return false
    endif
    return F8_Team[pn-1]>0 and udg_player_active[pn]
endfunction''')
inject('SKMergeScore','''    set udg_KOTH_Team_Gold_Earned_Total[S8Team(newKing)]=udg_KOTH_Team_Gold_Earned_Total[S8Team(newKing)]+udg_KOTH_Team_Gold_Earned_Total[S8Team(oldKing)]
    set udg_KOTH_Team_Gold_Earned_Total[S8Team(oldKing)]=0''')
# Rebuild base controls using this branch's abilities, not the donor's absent helper.
put('SKRespawnTick',funcs(s)['SKRespawnTick'].replace('call FFOD_InstallSpawnToggles(pn)','call SKRestoreBaseControls(pn)'))
put('SKTick',funcs(s)['SKTick'].replace('call ExecuteFunc("SKRespawnTick")','call SKRespawnTick()'))
# Shared vision follows the current kingdom and is revoked when a player defects.
sync=funcs(s)['SKSync']
sync=sync.replace('    local group g','    local group g\n    local integer visionKey')
sync=sync.replace('                call SetPlayerAlliance(Player(pn-1), Player(other-1), ALLIANCE_PASSIVE, allied)', '''                set visionKey=pn*16+other
                if SKBaseVision[visionKey]!=null then
                    call FogModifierStop(SKBaseVision[visionKey])
                    call DestroyFogModifier(SKBaseVision[visionKey])
                    set SKBaseVision[visionKey]=null
                endif
                if allied then
                    set SKBaseVision[visionKey]=CreateFogModifierRadius(Player(pn-1),FOG_OF_WAR_VISIBLE,SF_BaseX[other],SF_BaseY[other],1150.,false,false)
                    call FogModifierStart(SKBaseVision[visionKey])
                endif
                call SetPlayerAlliance(Player(pn-1), Player(other-1), ALLIANCE_PASSIVE, allied)''')
sync=sync.replace('        set j=1','''        if SKActive(pn) and udg_autopoolto[pn]>0 then
            if not SKActive(udg_autopoolto[pn]) or SKKing[udg_autopoolto[pn]]!=SKKing[pn] then
                set udg_autopoolto[pn]=0
            endif
        endif
        set j=1''',1)
put('SKSync',sync)
# Keep kingdom scoring in the existing death trigger, before base capture changes alliances.
put('SKInit',funcs(s)['SKInit'].replace('    local trigger kills','').replace('    set kills=CreateTrigger()','').replace('    call TriggerRegisterAnyUnitEventBJ(kills, EVENT_PLAYER_UNIT_DEATH)','').replace('    call TriggerAddAction(kills, function SKCreditKill)','').replace('    set kills=null',''))
inject('Trig_Multiboard_Update_Actions','''    if SKEnabled then
        call SKCreditKill()
    endif''')
put('SKCreditKill',funcs(s)['SKCreditKill'].replace('and not IsUnitIllusion(dead) and IsUnitEnemy','and not IsUnitIllusion(dead) and GetUnitAbilityLevel(dead, \'Aloc\')==0 and IsUnitEnemy'))
# King mode's capture path must return before the FFA kill/defeat cleanup.
inject('Trig_player_destroyed_Actions','''    if SKEnabled then
        call SKOnBaseDeath()
        set defeatedPlayer=null
        return
    endif''')
inject('Trig_player_destroyed_Actions','    call SF_RevealEliminated(playerNumber)','    call ForceRemovePlayerSimple(defeatedPlayer, udg_Active_PlayGroup)')
inject('Trig_Update_base_variable_Actions','''    if SKEnabled and SKProtectUntil[udg_temp_playernumber]>SKClock then
        call SetUnitInvulnerable(udg_base[udg_temp_playernumber],true)
    endif''','    if ( Trig_Update_base_variable_Func004C() ) then')
inject('Trig_END_Actions','''    if SKEnabled then
        call SKCheckVictory()
        return
    endif''')
for name in ['Trig_player_leaves_Actions','Trig_KICK_execute_Actions']:
 f=funcs(s)[name]
 pn='playerNumber' if 'leaves' in name else 'udg_X'
 f=f.replace(f'if udg_mode_koth and udg_KOTH_Team_Number == udg_teamnumber[{pn}] then',f'if udg_mode_koth and udg_KOTH_Player==Player({pn}-1) then')
 f=f.replace(f'set udg_player_active[{pn}]=false',f'''set udg_player_active[{pn}]=false
                if SKEnabled then
                    set SKRespawnIn[{pn}]=0
                    call SKNormalize()
                    call SKSync()
                    call SKCheckVictory()
                endif''')
 put(name,f)
inject('SF_RestoreFFA','''    if SKEnabled then
        call SKSync()
        return
    endif''')
# Board updates have one owner in each mode. -kd retains individual K/D in both.
inject('F8_UpdateBoard','''    if SKEnabled then
        call SKBoard()
        return
    endif''')
inject('Trig_Multiboard_Create_with_KOTH_Actions','''    if SKEnabled then
        call SKCreateBoard()
        return
    endif''')
inject('SKCreateBoard','''    if udg_multiboard_kills!=null then
        call DestroyMultiboard(udg_multiboard_kills)
    endif''')
put('SKCreateBoard',funcs(s)['SKCreateBoard'].replace('CreateMultiboardBJ(6, 9','CreateMultiboardBJ(7, 9').replace('exitwhen col > 6','exitwhen col > 7').replace('    call SKBoard()','    call MultiboardSetItemValueBJ(udg_multiboard_kills,7,1,"Hill gold")\n    call SKBoard()\n    call MultiboardDisplay(udg_multiboard_kills,true)'))
board=funcs(s)['SKBoard'].replace('set status="Ready"','set status="King"\n            if king!=pn then\n                set status="Vassal: ready"\n            endif').replace('set status="Used"','set status="Used"')
board=board.replace('        set i=i+1','        call MultiboardSetItemValueBJ(udg_multiboard_kills,7,i+1,I2S(udg_KOTH_Team_Gold_Earned_Total[S8Team(king)]))\n        set i=i+1')
board=board.replace('            set status="Left"','''            set status="Left"
            call MultiboardSetItemValueBJ(udg_multiboard_kills,3,i+1,"-")
            call MultiboardSetItemValueBJ(udg_multiboard_kills,4,i+1,"-")
            call MultiboardSetItemValueBJ(udg_multiboard_kills,5,i+1,"-")''')
put('SKBoard',board)
# King mode uses the sovereign's force for hill rewards; preserve personal upgrade indices.
f=funcs(s)['Trig_KOTH_Hill_Dies_Actions'].replace('        set udg_KOTH_Team=udg_team[udg_KOTH_Team_Number]','''        if SKEnabled then
            set udg_KOTH_Team_Number=S8Team(SKKing[GetConvertedPlayerId(udg_KOTH_Player)])
        endif
        set udg_KOTH_Team=udg_team[udg_KOTH_Team_Number]''');put('Trig_KOTH_Hill_Dies_Actions',f)
inject('Trig_KOTH_Income_Actions','''    if SKEnabled then
        call SKHillIncome()
        return
    endif''')
inject('Trig_KOTH_Reset_Hill_Actions','''    if SKEnabled and not SKActive(GetPlayerId(udg_KOTH_Player)+1) then
        call PauseTimer(udg_KOTH_Income_Timer)
    endif''')
inject('Trig_MODE_set_pub_game_Actions','''    if SKEnabled then
        set udg_game_mode_display[1]=" King Mode"
    endif''', '    set udg_mode_pub=true')
# Startup mode choice precedes hero selection; game clocks restart after the choice.
put('SF_Initialize',funcs(s)['SF_Initialize'].replace('function SF_StartBaseSelection','function SKOpenMode').replace('    call TimerStart(CreateTimer(),1.20,false,function F8_Start)',''))
put('SF_StartBaseSelection',funcs(s)['SF_StartBaseSelection'].replace('    call DestroyTimer(startup)','    call TimerStart(CreateTimer(),.10,false,function F8_Start)\n    call DestroyTimer(startup)'))
inject('F8_Start','''    if SKEnabled then
        call SKSync()
    endif''','    call F8_InitVision()')
title='Solo Foots 8P FFA + King v10';s=re.sub(r'call SetMapName\("[^\"]+"\)',f'call SetMapName("{title}")',s)
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):]
tail=tail[:tail.index('# Terrain-derived BLP1 minimaps')]+tail[tail.index('work=Path('):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v10.w3x')
tail=tail.replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','king_functions=len(selected),')
report={};exec(tail)
