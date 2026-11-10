from pathlib import Path
p=Path('shared-sync-v85/check.py');s=p.read_text()
s=s.replace("'old':W/'consolidated-v84/release/FF799X_Rx_Consolidated_v84_TEST.w3x',", "'oldsolo':Path('C:/Users/User/Documents/Warcraft III/Maps/Solo Foots/Solo Tests/Solo_Foots_v1.8_4P_799X_UPDATE08.w3x'),'old':W/'consolidated-v84/release/FF799X_Rx_Consolidated_v84_TEST.w3x',")
s=s.replace("state['inventory'].remove(it)","state['inventory'][state['inventory'].index(it)]=None")
s=s.replace("if it[0]==t)","if it and it[0]==t)")
s=s.replace("DisplayTextToPlayer=lambda p,x,y,msg:state['messages'].append(msg),", "DisplayTextToPlayer=lambda p,x,y,msg:state['messages'].append(msg),SoloFootsDisplayMessageToPlayer=lambda p,x,y,msg:state['messages'].append(msg),")
anchor='# Creep caps preserve all 15 rawcodes and unrestricted fast path.'
s=s.replace(anchor,'''oldsolo,newsolo=item_env('oldsolo'),item_env('solo')
for t in rawcodes+['zzzz']:
 for h in heroes:
  for count in range(1,7):
   a,b=oldsolo(t,h,count),newsolo(t,h,count)
   if t=='I006' and count>2:a=(a[0],[msg.replace('Only 1x','Only 2x') for msg in a[1]])
   if t=='I009' and count>2:a=(['I009'],['|cffff0000Only 2x |rI009|cffff0000 per hero allowed!|r'])
   assert a==b,(t,h,count,a,b);cases+=1
check('Solo item rules preserved except correct 2x warning and non-destructive Shockwave overflow',True)
for n in fs['oldsolo']:
 if n.startswith(('SoloFoots','SoloCam_','Trig_MODE','InitTrig_MODE','Trig_KOTH','InitTrig_KOTH','OM_','FS_','FFGS_')) or n in ['InitCustomPlayerSlots','InitCustomTeams','Trig_Start_game_Actions','Trig_set_hero_stats_Actions','Trig_set_spawn_variables_Actions']:
  assert fs['oldsolo'][n]==fs['solo'][n],n
check('Solo slots, game modes, roster, Gragus/Guldan, camera and spawn systems preserved',True)
'''+anchor)
p.write_text(s)
