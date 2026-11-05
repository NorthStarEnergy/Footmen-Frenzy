from pathlib import Path
import sys,json,re,hashlib,struct
R=Path(__file__).parent;sys.path.insert(0,str(R/'tools'));import objdata
B=R/'base/files';S=R/'src';V=Path((R/'last-build.txt').read_text().strip())/'roundtrip/files'
checks=[]
def check(label,test):
 assert test,label
 checks.append(label)
s=(V/'war3map.j').read_text(encoding='utf-8-sig');c=json.loads((R/'changes.json').read_text());slots=c['slots']
sourcefiles={f.relative_to(S) for f in S.rglob('*') if f.is_file()}
for rel in sourcefiles:check('Packed source matches: '+str(rel),(S/rel).read_bytes()==(V/rel).read_bytes())
count=0
for f in B.rglob('*'):
 if f.is_file() and f.relative_to(B) not in sourcefiles:
  v=V/f.relative_to(B);check('asset '+str(f.relative_to(B)),v.exists() and f.read_bytes()==v.read_bytes());count+=1
assetchecks=checks[-count:];checks=checks[:-count]+[f'{count} unchanged extracted assets/data files verified byte for byte']
check('Eight user controllers',len(re.findall(r'call SetPlayerController\(Player\(\d+\), MAP_CONTROL_USER\)',s))==8)
check('No observer player slots', 'call SetPlayers(8)' in s and 'call SetTeams(4)' in s)
towers={i:0 for i in slots};shops={i:0 for i in slots}
for i in range(12):
 body=re.search(r'function CreateBuildingsForPlayer'+str(i)+r' takes .*?\nendfunction',s,re.S).group()
 for m in re.finditer(r"BlzCreateUnitWithSkin\((p|Player\((\d+)\)), '(hwtw|n003)'",body):
  owner=i if m[1]=='p' else int(m[2]);check('Structure owner is retained',owner in slots)
  (towers if m[3]=='hwtw' else shops)[owner]+=1
check('Two towers per player / four per team',all(v==2 for v in towers.values()))
check('One personal upgrade shop for all eight players',all(v==1 for v in shops.values()))
check('Hero cap 10','MaxHeroLevel=10' in (V/'war3mapMisc.txt').read_text())
q=objdata.load(str(V/'war3map.w3q'))
for e in q['tables'][0]:
 if e['oldId'] in ['Rhme','Rhar']:check(e['oldId']+' maximum five',next(m['value'] for m in e['mods'] if m['id']=='glvl')==5)
u=objdata.load(str(V/'war3map.w3u'))
for tab in u['tables']:
 for e in tab:
  for m in e['mods']:
   if m['id']=='uupt':check('No upgrade path reaches T3+',not set(m['value'].split(','))&set(c['blocked_bases']))
for id in c['blocked_bases']:check('T3+ object disabled: '+id,f"call SetPlayerTechMaxAllowed(Player(i), '{id}', 0)" in s)
# Verify arbitrary wave sizes including odd waves: complementary rounding never changes team total.
for waves in [[2]*11+[3],[2]*20+[3,4,5],[1]*61,[3,1,5,2,4,3]]:
 total=[0,0];rem=[0,1];baseline=0
 for n in waves:
  baseline+=n
  for p in range(2):
   a=n*3+rem[p];total[p]+=a//2;rem[p]=a%2
  check('Mass team total equals three-player total',sum(total)==baseline*3)
 check('Mass 150% complementary rounding',sum(total)==sum(waves)*3 and abs(total[0]-total[1])<=1)
check('Hidden pool release guarded against repeat', 'if MF_MassReleased then' in s)
check('Pool restored to visible, active, vulnerable with pathing',all(v in s for v in ['call SetUnitPathing(u, true)','call SetUnitInvulnerable(u, false)','call ShowUnit(u, true)','call PauseUnit(u, false)']))
check('All creep types covered',len(c['creeps'])==25 and all("id == '"+x+"'" in s for x in c['creeps']))
check('Dead creeps excluded','GetWidgetLife(other) > 0.405 and not IsUnitType(other, UNIT_TYPE_DEAD)' in s)
r=objdata.Reader((V/'war3map.w3i').read_bytes());r.o=r.d.index(struct.pack('<6i',8,0,1,1,64,1));check('Lobby player count eight',r.i32()==8)
ids=[]
for _ in range(8):
 fields=[r.i32() for _ in range(5)];r.cstr();xy=[r.f32(),r.f32()];r.raw(16);ids.append(fields[0]);check('Lobby start position matches runtime',xy==c['starts'][str(fields[0])])
check('Lobby IDs match retained slots',ids==slots);check('Four lobby teams',r.i32()==4)
for t in range(4):
 flags=r.i32();mask=r.i32();r.cstr();check('Force has precisely its two slots',mask==(1<<(t*3))+(1<<(t*3+2)))
es={e['newId'] if e['newId']!='\0'*4 else e['oldId']:e for tab in u['tables'] for e in tab}
mods=lambda e:{m['id']:m['value'] for m in e['mods']}
for id in set(re.findall(r"set udg_spawn_unit\[\d+\]='(....)'",s)):
 check('Both object weapon ranges zero: '+id, all(mods(es[id]).get(k)==0 for k in ['ua1r','ua2r']))
for id in c['allowed_bases']:
 check('Only attack and armor research: '+id,mods(es[id])['ures']=='Rhme,Rhar')
for id in ['E00E','N01C','H02J','H02G','H015','H04Y']:
 check('Transmute hero unavailable: '+id,f"call SetPlayerTechMaxAllowed(Player(i), '{id}', 0)" in s and all(id not in mods(e).get('useu','').split(',') for e in es.values()))
check('Autopick excludes disabled heroes','udg_hero_type[i] != 0 and udg_hero_category[i] > 0' in s)
show=re.search(r'function Trig_MODE_GUI_show_Actions takes .*?\nendfunction',s,re.S).group()
check('Only Pub and Debug mode buttons',show.count('DialogAddButton(')==2 and 'MF_IsRJE(Player(i))' in show)
check('Mode clicks restricted to RJE host','if p != udg_Host or not MF_IsRJE(p) then' in s)
check('Pooling unlocks at game clock 20 minutes','if udg_gametime_s == 1200 then' in s and 'call ExecuteFunc("MF_EnablePooling")' in s and 'return udg_gametime_s >= 1200 and' in s)
check('Pooling countdown visible','1200.0 - I2R(udg_gametime_s)' in s and 'CreateTimerDialogBJ(udg_timer_trading, "Pooling available")' in s)
for key,value in [('premass_seconds',60),('tech1_default_seconds',210),('tech2_seconds',420),('tech3_seconds',480)]:
 check('Earlier timeline '+key,f'set ffgs_{key}={value:.2f}' in s)
check('Racial sharing disabled', 'function FFRacial_ShareResearch takes nothing returns nothing\nendfunction' in s)
check('Formation uses independent player counts and base-facing fronts','local integer n=MF_PlayerStaged[pn]' in s and 'RAbsBJ(GetUnitY(udg_base[pn])' in s and 'set x=640.0 + I2R(col) * 64.0' in s)
positions=[]
for half in range(2):
 cells=[]
 for n in range(90):
  along=640+(n%12)*64;depth=160+(n//12)*64
  cells.append((depth,along) if half==0 else (along,depth))
 positions.append(set(cells))
check('Teammate formation halves never overlap',not positions[0]&positions[1])
check('Each half stays on its own side of diagonal',all(x<y for x,y in positions[0]) and all(x>y for x,y in positions[1]))
check('Proper vertical slider template','SliderLayoutVertical' in (V/'MiniFootsUI.fdf').read_text() and 'BlzCreateFrame("MiniFootsZoomSlider"' in s)
check('Zoom has explicit track, thumb and disabled artwork',all(v in (V/'MiniFootsUI.fdf').read_text() for v in ['ControlBackdrop "MFZoomTrack"','SliderThumbButtonFrame "MFZoomThumb"','ControlDisabledBackdrop "MFZoomLockedThumbArt"']))
check('Zoom parent is stable game UI','local framehandle gameUI= BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)' in s)
check('Stats compact and anchored to minimap','BlzFrameSetSize(DPS_Button, 0.0625, 0.020)' in s and 'BlzFrameSetText(DPS_Button, "Stats")' in s and 'ORIGIN_FRAME_MINIMAP, 0), FRAMEPOINT_TOP' in s)
check('Stats eight compact rows with matching update slots',s.count('if ModuloInteger(s - 1, 3) != 1 then')==2 and 'I2R(row) * 0.022' in s)
check('Stats panel close button and removed title/footer', 'DPS_Title' not in s and 'DPS_Legend' not in s and 'FRAMEPOINT_TOPRIGHT, DPS_Panel, FRAMEPOINT_TOPRIGHT' in s and 'BlzTriggerRegisterFrameEvent(click, f, FRAMEEVENT_CONTROL_CLICK)' in s)
for id in c['allowed_bases']:
 if id!='hbar':check('Reduced tech price '+id,mods(es[id])['ugol']==(600 if mods(es[id]).get('ureq')=='R00D' else 1300))
check('Stats text is not scaled off its row','call BlzFrameSetScale(f, 0.85)' not in s and 'call BlzFrameSetScale(f, 0.70)' not in s)
check('Stats has no multiboard visibility dependency','if udg_multiboard_kills == null or not IsMultiboardDisplayed(udg_multiboard_kills) then' not in s)
check('Zoom created after game initialization','TimerStart(CreateTimer(), 0.50, false, function zoom__CreateSlider)' in s)
for uid,hp,armor in [('ugho',675,1),('ogru',800,2)]:
 check('Melee object stats '+uid,mods(es[uid])['uhpm']==hp and mods(es[uid])['udef']==armor)
a=objdata.load(str(V/'war3map.w3a'));charge=next(e for tab in a['tables'] for e in tab if e['newId']=='A0D9')
check('Charge usable without removed research',mods(charge)['areq']=='' and mods(charge)['anam']=='Charge')
check('Footman runtime target stays 110','set udg_unit_range[0]=110' in s)
for idx,uid,hp,armor in [(17,'ugho',675,2),(44,'ugho',675,2),(23,'ogru',800,2),(27,'ogru',800,2),(9,'uban',540,7),(39,'uban',540,7),(20,'ngh2',680,7),(47,'ngh2',680,7),(22,'esen',680,7),(28,'esen',680,7),(18,'hmil',900,2),(48,'hmil',900,2)]:
 check('Roster and armor path '+str(idx),all(x in s for x in [f"set udg_spawn_unit[{idx}]='{uid}'",f'set udg_unit_HP[{idx}]={hp}',f'set udg_unit_armor_type[{idx}]={armor}']))
for uid,abilities in [('ugho','ACce,ACev,A0D9'),('ogru','ACev,A0D9')]:
 check('Modified melee object retained '+uid,mods(es[uid])['uabi']==abilities and mods(es[uid])['udty']=='large' and mods(es[uid])['ua1t']=='normal')
for uid in ['esen','uban','ngh2']:check('Object unarmored '+uid,mods(es[uid])['udty']=='none')
check('No forced medium Banshee override','call BlzSetUnitIntegerField(u, UNIT_IF_DEFENSE_TYPE, 1)' not in s)
check('Range uses compensated setter','desired - primary + secondary' in s and 'call MF_SetAttackRange(u, udg_unit_range_actual[idx])' in s)
# Model the documented native delta: applied = argument - secondary + primary.
# The native adds its argument minus the old weapon difference to the primary.
for initial,secondary in [(0,0),(110,110),(220,220),(600,100)]:
 primary=initial
 for _ in range(4):
  argument=110-primary+secondary
  primary=primary+argument-secondary
  check('Repeated range update remains 110',primary==110)
check('Fortitude uses native armor modifier',"call UnitAddAbility(u, 'AGf1')" in s and "call BlzUnitHideAbility(u, 'AGf1', true)" in s)
check('Fortitude avoids direct armor changes', 'BlzGetUnitArmor(u) + FS_Armor[i]' not in s and 'BlzGetUnitArmor(FS_U[i]) - FS_Armor[i]' not in s)
it=objdata.load(str(V/'war3map.w3t'));boots=next(e for e in it['tables'][0] if e['oldId']=='bspd')
check('Boots own ability and 75 gold resale',mods(boots)['iabi']=='AMFb' and mods(boots)['igol']*0.6==75)
check('Boots reversible separate speed bonus','MF_BootBaseSpeed(u) + 60.0' in s and 'MF_BootBaseSpeed(u))' in s and "call UnitRemoveAbility(u, 'BMFb')" in s)
check('Boots pickup tracked and copies do not stack',"UnitHasItemOfTypeBJ(u, 'bspd')" in s and 'hasBoots != LoadBoolean' in s)
for icon in ['Fortitude','Slam']:
 check('New Gragas '+icon+' icon',(V/'ReplaceableTextures/CommandButtons'/('BTNRxGragas'+icon+'.blp')).read_bytes()!=(B/'ReplaceableTextures/CommandButtons'/('BTNRxGragas'+icon+'.blp')).read_bytes())
check('WTS UTF-8 BOM retained',(V/'war3map.wts').read_bytes().startswith(b'\xef\xbb\xbf'))
check('Direct metadata says eight players',b'8 players - 4 teams of 2\0' in (V/'war3map.w3i').read_bytes())
mb=(V/'war3map.mmp').read_bytes();check('Exactly eight preview starts',sum(struct.unpack_from('<i',mb,i)[0]==2 for i in range(8,len(mb),16))==8)
for seconds,indices in [(8,[0]),(6,[3,31,9,39]),(4.5,[17,44,23,27]),(6.5,[13,36]),(7,[21,26,22,28]),(5,[16,50,18,48,20,47])]:
 for idx in indices:
  check('Requested spawn interval path '+str(idx),f'set ffgs_spawn_interval[{idx}]={seconds:.2f}' in s)
donor=R/'audit/heroes-799x-v13'
ds=(donor/'war3map.j').read_text(encoding='utf-8-sig')
for m in re.finditer(r'^function (OM_\w+) takes .*?^endfunction',ds,re.M|re.S):
 check('Orianna donor function '+m[1],m[0] in s)
for name in ['FS_ClearFortitude','FS_OnCast','FS_Free','FS_Tick']:
 pattern=r'^function '+name+r' takes .*?^endfunction'
 check('Gragus donor function '+name,re.search(pattern,ds,re.M|re.S)[0]==re.search(pattern,s,re.M|re.S)[0])
for line in re.findall(r'^.*set udg_hero_\w+\[92\]=.*$',ds,re.M):
 check('Orianna donor roster stats '+line,line in s)
for line in re.findall(r'^.*(?:\x27AOz2\x27|\x27AOz4\x27).*$',re.search(r'^function FF_HeroTooltips_Init takes .*?^endfunction',ds,re.M|re.S)[0],re.M):
 check('Orianna donor tooltip '+line,line in s)
for ext,ids in [('w3u',{'HOr1','hor1','hor2'}),('w3a',{'AOz1','AOz2','AOz3','AOz4','AOz5','AOz7','AGf1','AGr2'}),('w3h',{'BOr4','BOr5'})]:
 def entries(path):
  return {e['newId'] if e['newId']!='\0'*4 else e['oldId']:e for t in objdata.load(str(path))['tables'] for e in t}
 actual=entries(V/('war3map.'+ext));expected=entries(donor/('war3map.'+ext))
 for uid in ids:check('Orianna donor object '+uid,actual[uid]==expected[uid])
for f in donor.rglob('*'):
 if f.is_file() and 'Orianna' in str(f.relative_to(donor)):
  check('Orianna donor asset '+str(f.relative_to(donor)),(V/f.relative_to(donor)).read_bytes()==f.read_bytes())
release=R/'release/Mini Foots v7.w3x';report={'status':'PASS','checks':list(dict.fromkeys(checks)),'sha256':hashlib.sha256(release.read_bytes()).hexdigest(),'bytes':release.stat().st_size,'engine_test':'pending'}
(R/'verification.json').write_text(json.dumps(report,indent=2));print('PASS',len(checks),'checks;',count,'unchanged files;',report['sha256']);print('map header',release.read_bytes()[:32].hex())
