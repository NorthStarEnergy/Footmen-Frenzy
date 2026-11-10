exec(compile(open('shared-sync-v85/inspect.py',encoding='utf8').read().split('selected=')[0],'setup','exec'))
for n in s:
 if n.startswith('SoloFoots') and 'Sinkhole' in n or n in ['Trig_HERO_Myrmidon_Sinkhole_start_Actions','Trig_HERO_Myrmidon_Sinkhole_suck_Actions','InitTrig_HERO_Myrmidon_Sinkhole_suck','Trig_HERO_Prison_Wall_countdown_Actions','SF_PageSelectFilter','SF_PageSelectEnum','SF_PageTargetForSelector','CreepLimit_CountLivingTeamCopies','CreepLimit_CountFilter']:
  print(s[n])
