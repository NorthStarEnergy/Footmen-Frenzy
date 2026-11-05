exec(open('solo-v1.8-799x/compare.py').read().split('print(len(changed))')[0])
import difflib
names=['s__MissileEffect___Effect_allocate','s__MissileEffect___Effect_deallocate','s__MissileUtils___MGroup_allocate','Trig_HERO_Hook_Loop_Finish','Trig_HERO_Hook_Throw_Actions','Trig_Staff_of_the_River_OnHit_Actions','Trig_HERO_Architect_tower_countdown_Actions','Trig_ITEM_limits_Actions','FFGS_CountLivingOfType','Trig_HERO_Myrmidon_Sinkhole_end_Actions','Trig_Akama_Shadow_Clone_Cast_Actions']
for n in names:
 print('\n--- '+n);print('\n'.join(difflib.unified_diff(b[n].splitlines(),d[n].splitlines(),n=2))[:7000])
