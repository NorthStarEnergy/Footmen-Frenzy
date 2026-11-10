// AUTHORITATIVE EDITOR SOURCE - see READ FIRST in Trigger Editor and FF_MAINTENANCE.md.
// Keep JassHelper enabled. Never ship a war3map.j-only gameplay patch.
globals

    framehandle DPS_Panel = null
    framehandle DPS_Button = null
    framehandle array DPS_Cell
    framehandle array DPS_Icon
    boolean array DPS_Open
    integer array DPS_Assists
    integer array DPS_Caps
    integer array DPS_Buildings
    hashtable DPS_Damage = null
    timer DPS_Timer = null
    boolean DPS_Ready = false

    integer GTW_Count = 0
    unit array GTW_Caster
    real array GTW_X
    real array GTW_Y
    real array GTW_DX
    real array GTW_DY
    real array GTW_Left
    effect array GTW_FX
    group array GTW_Hit
    integer array GTW_Rank
    hashtable GTW_Marks = InitHashtable()
    group GTW_Enum = CreateGroup()
    timer GTW_Timer = CreateTimer()

    integer GPS_Count = 0
    unit array GPS_Caster
    real array GPS_X
    real array GPS_Y
    integer array GPS_Rank
    integer array GPS_Ticks
    effect array GPS_FX
    group GPS_Enum = CreateGroup()
    timer GPS_Timer = CreateTimer()
    hashtable GPS_Hits = InitHashtable()
    integer GPS_Step = 0

    hashtable GFB_Data = InitHashtable()
boolean FFR4Pro=false
boolean FFR4NoPool=true
    // Generated
trigger gg_trg_FF_Runtime= null

rect FF_Editor_Phoken=null
rect FF_Editor_HEROshowroom=null
boolean udg_FFCH_Mode=false
integer array udg_ArchvaultSkillBought
boolean udg_FFCH_Building=false
integer array udg_FFCH_Item
integer array udg_FFCH_Ability
integer array udg_FFCH_Slot
integer array udg_FFCH_Price
boolean array udg_FFCH_ZAoE
integer array udg_FFCH_TeamZAoE
integer array udg_FFCH_TeamAbil
integer array udg_FFCH_TeamAbilCount
string array udg_FFCH_Name
string array udg_FFCH_SlotName
integer array udg_FFCH_PlayerSlot
real array udg_FFCH_BuildX
real array udg_FFCH_BuildY
unit array udg_FFCH_Shop
unit array udg_FFCH_Hero
timer udg_FFCH_EndTimer=null
button array udg_dlg_btn_mode_ch
integer SafeRemoval_GraceTicks=0
//globals
// from Alloc:
constant boolean LIBRARY_Alloc=true
//endglobals
// from Alloc
//globals
// from CustomPathingPlacer:
constant boolean LIBRARY_CustomPathingPlacer=true
hashtable CPP_Hash= InitHashtable()
        //hashtable CPP_Hash_Debug = InitHashtable() // debug
//endglobals
// from CustomPathingPlacer
//globals
// from FileIO:
constant boolean LIBRARY_FileIO=true
        // Enable this if you want to allow the system to read files generated in patch 1.30 or below.
        // NOTE: For this to work properly you must edit the 'Amls' ability and change the levels to 2
        // as well as typing something in "Level 2 - Text - Tooltip - Normal" text field.
        //
        // Enabling this will also cause the system to treat files written with .write("") as empty files.
        //
        // This setting is really only intended for those who were already using the system in their map
        // prior to patch 1.31 and want to keep old files created with this system to still work.
constant boolean FileIO___BACKWARDS_COMPATABILITY= false
//endglobals
// from FileIO
//globals
// from GUISimpleTimers:
constant boolean LIBRARY_GUISimpleTimers=true
hashtable GST_Hash= InitHashtable()
integer GST_NewKey= 0
integer GST_Index= 0
//endglobals
// from GUISimpleTimers
//globals
// from MMD:
constant boolean LIBRARY_MMD=true
constant integer MMD_GOAL_NONE= 101
constant integer MMD_GOAL_HIGH= 102
constant integer MMD_GOAL_LOW= 103
        
constant integer MMD_TYPE_STRING= 101
constant integer MMD_TYPE_REAL= 102
constant integer MMD_TYPE_INT= 103

constant integer MMD_OP_ADD= 101
constant integer MMD_OP_SUB= 102
constant integer MMD_OP_SET= 103

constant integer MMD_SUGGEST_NONE= 101
constant integer MMD_SUGGEST_TRACK= 102
constant integer MMD_SUGGEST_LEADERBOARD= 103

constant integer MMD_FLAG_DRAWER= 101
constant integer MMD_FLAG_LOSER= 102
constant integer MMD_FLAG_WINNER= 103
constant integer MMD_FLAG_LEAVER= 104
constant integer MMD_FLAG_PRACTICING= 105
constant boolean MMD__SHOW_DEBUG_MESSAGES= true
        
constant string MMD__chars= "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-+= \\!@#$%^&*()/?>.<,;:'\"{}[]|`~"
constant integer MMD__num_chars= StringLength(MMD__chars)
string array MMD__flags
string array MMD__goals
string array MMD__ops
string array MMD__types
string array MMD__suggestions
boolean MMD__initialized= false
                
gamecache MMD__gc= null
constant string MMD__ESCAPED_CHARS= " \\"
        
constant integer MMD__CURRENT_VERSION= 1
constant integer MMD__MINIMUM_PARSER_VERSION= 1
constant string MMD__FILENAME= "MMD.Dat"
constant string MMD__M_KEY_VAL= "val:"
constant string MMD__M_KEY_CHK= "chk:"
constant integer MMD__NUM_SENDERS_NAIVE= 1
constant integer MMD__NUM_SENDERS_SAFE= 3
integer MMD__num_senders= MMD__NUM_SENDERS_NAIVE
integer MMD__num_msg= 0
        
timer MMD__clock= CreateTimer()
string array MMD__q_msg
real array MMD__q_time
integer array MMD__q_index
integer MMD__q_head= 0
integer MMD__q_tail= 0
//endglobals
// from MMD
//globals
// from TimerUtils:
constant boolean LIBRARY_TimerUtils=true
        //How to tweak timer utils:
        // USE_HASH_TABLE = true  (new blue)
        //  * SAFEST
        //  * SLOWEST (though hash tables are kind of fast)
        //
        // USE_HASH_TABLE = false, USE_FLEXIBLE_OFFSET = true  (orange)
        //  * kinda safe (except there is a limit in the number of timers)
        //  * ALMOST FAST
        //
        // USE_HASH_TABLE = false, USE_FLEXIBLE_OFFSET = false (red)
        //  * THE FASTEST (though is only  faster than the previous method
        //                  after using the optimizer on the map)
        //  * THE LEAST SAFE ( you may have to tweak OFSSET manually for it to
        //                     work)
        //
constant boolean TimerUtils___USE_HASH_TABLE= true
constant boolean TimerUtils___USE_FLEXIBLE_OFFSET= false

constant integer TimerUtils___OFFSET= 0x100000
integer TimerUtils___VOFFSET= TimerUtils___OFFSET
              
        //Timers to preload at map init:
constant integer TimerUtils___QUANTITY= 256
        
        //Changing this  to something big will allow you to keep recycling
        // timers even when there are already AN INCREDIBLE AMOUNT of timers in
        // the stack. But it will make things far slower so that's probably a bad idea...
constant integer TimerUtils___ARRAY_SIZE= 8190

// processed:         integer array TimerUtils___data[TimerUtils___ARRAY_SIZE]
hashtable TimerUtils___ht
// processed:         timer array TimerUtils___tT[TimerUtils___ARRAY_SIZE]
integer TimerUtils___tN= 0
constant integer TimerUtils___HELD=0x28829022
        //use a totally random number here, the more improbable someone uses it, the better.
        
boolean TimerUtils___didinit= false
//endglobals
// from TimerUtils
//globals
// from WorldBounds:
constant boolean LIBRARY_WorldBounds=true
//endglobals
// from WorldBounds
//globals
// from MissileEffect:
constant boolean LIBRARY_MissileEffect=true
//endglobals
// from MissileEffect
//globals
// from Missiles:
constant boolean LIBRARY_Missiles=true
        // The update period of the system
constant real Missiles_PERIOD= 1. / 40.
        // The max amount of Missiles processed in a PERIOD
        // You can play around with both these values to find
        // your sweet spot. If equal to 0, the system will
        // process all missiles at once every period.
constant real Missiles_SWEET_SPOT= 100
        // the avarage collision size compensation when detecting collisions
constant real Missiles___COLLISION_SIZE= 128.
        // item size used in z collision
constant real Missiles___ITEM_SIZE= 16.
        // Raw code of the dummy unit used for vision
constant integer Missiles___DUMMY= 'dumi'
        // Needed, don't touch.
location Missiles___LOC= Location(0., 0.)
//endglobals
// from Missiles
//globals
// from MissileUtils:
constant boolean LIBRARY_MissileUtils=true
//endglobals
// from MissileUtils
    // User-defined
unit array udg_casting_hero
integer udg_blocker_ID= 0
string array udg_wmd
string array udg_game_mode_substring
texttag udg_game_mode_floating_text= null
string array udg_game_mode_display
integer array udg_unit_deaths
location array udg_hellfire_point
integer udg_creep_gold_cost= 0
integer array udg_unit_spawnrate
boolean udg_disable_message= false
location array udg_colossal_point
string array udg_coloured_playername
boolean udg_scoreboard_on= false
timer array udg_timer_forked_fury
string array udg_colour
dialog udg_dlg_colossal= null
button udg_dlg_colossal_no= null
button udg_dlg_colossal_yes= null
boolean udg_colossal_on= false
integer array udg_colossal_dropped_item
integer udg_colossal_wave= 0
timer udg_timer_colossal= null
timerdialog udg_timer_window_colossal= null
location array udg_battle_point_mid
location array udg_battle_point
integer array udg_test_unit_ID
real array udg_unit_range_actual
boolean udg_host_verified= false
boolean udg_password_correct= false
timerdialog udg_timer_window_password= null
timer udg_timer_password= null
string udg_tournament_password
string udg_temp_string
boolean udg_version_tournament= false
integer array udg_dragon_bounty
integer array udg_dragon_att_base
integer array udg_dragon_hp
integer array udg_random_creep
integer udg_X_category= 0
group array udg_hero_category_group
timer array udg_timer_tower
integer udg_tower_ID= 0
texttag array udg_tower_timer_text
integer array udg_hero_category
integer udg_ap_number_of_heros= 0
unit udg_temp_casting_unit= null
button array udg_dlg_btn_downgrade_no
button array udg_dlg_btn_downgrade_yes
unit array udg_upgrading_tower
dialog array udg_dlg_downgrade
real array udg_unit_range
unit udg_temp_dying_unit= null
unit udg_temp_killing_unit= null
unit array udg_target
real udg_hero_bounty_multiplier= 0
integer array udg_hero_bounty_base
integer array udg_unit_bounty_dice_sides
integer array udg_unit_bounty_num_dice
integer array udg_unit_bounty_base
unit udg_temp_target= null
integer array udg_pool_threshold
dialog array udg_dlg_pool_th
button array udg_dlg_btn_pool_th_5
button array udg_dlg_btn_pool_th_4
button array udg_dlg_btn_pool_th_3
button array udg_dlg_btn_pool_th_2
button array udg_dlg_btn_pool_th_1
button array udg_dlg_btn_pool_cancel
integer array udg_temp_X
timer array udg_timer_ship
location array udg_ship_destination
unit array udg_dummy_ship
boolean udg_mode_set_by_host= false
dialog udg_dlg_vote_or_set= null
button array udg_dlg_btn_vote_or_set
unit udg_targeted_unit= null
integer array udg_unit_att_num_dice_actual
integer array udg_base_type
integer udg_X_base= 0
integer udg_X_playernumber= 0
integer array udg_X_array
timer array udg_wall_timer
integer udg_wall_ID= 0
texttag array udg_wall_timer_text
button array udg_dlg_btn_pubwall_cancel
button array udg_dlg_btn_pubwall_2
button array udg_dlg_btn_pubwall_1
dialog array udg_dlg_pubwall
timerdialog udg_timer_window_madness_random= null
timer udg_timer_madness_random= null
integer array udg_madness_playernumber
boolean udg_mode_madness= false
boolean udg_mode_promode= false
boolean udg_mode_777club= false
button array udg_dlg_btn_mode_11
button array udg_dlg_btn_mode_10
button array udg_dlg_btn_mode_09
button array udg_dlg_btn_mode_08
unit array udg_tower_2
unit array udg_tower_1
integer udg_temp_item_type= 0
item udg_temp_item= null
timer array udg_timer_overdrive_CD
timer array udg_timer_overdrive
integer array udg_number_of_spawned_units
boolean udg_version_test= false
location array udg_vengaence_point
effect array udg_temp_effect
unit udg_spirit= null
boolean array udg_charge_active
boolean array udg_bloodrush_on
timerdialog udg_timer_window_trading= null
timer udg_timer_trading= null
real udg_t_mass= 0
real udg_t_trading= 0
real udg_t_premass= 0
lightning array udg_drain
integer udg_temp_playernumber_ally_2= 0
integer udg_temp_playernumber_ally_1= 0
integer array udg_unit_HP_actual
integer array udg_unit_att_dice_sides_actual
real array udg_unit_armor_actual
integer array udg_unit_att_actual
integer array udg_Item
timerdialog udg_timer_window_mass= null
location array udg_HS
button array udg_dlg_votekick_btn_2
button array udg_dlg_votekick_btn_cancel
button array udg_dlg_votekick_btn_1
dialog array udg_dlg_votekick
real array udg_unit_armor
integer array udg_unit_armor_type
real array udg_unit_att_CD
integer array udg_unit_att_dice_sides
integer array udg_unit_att_num_dice
integer array udg_unit_att_base
unit array udg_spawned_unit
integer array udg_unit_HP
integer array udg_hero_killstreak
boolean udg_firstblood= false
timer udg_timer_mass= null
boolean udg_mass_active= false
boolean array udg_autosend
boolean udg_spawnprotection= false
integer udg_total_tips= 0
integer udg_guided_tip_number= 0
string array udg_guided_tip
button array udg_dlg_btn_mode_07
button array udg_dlg_btn_mode_06
integer udg_chance= 0
integer array udg_random_integer
integer udg_seconds= 0
button array udg_dlg_btn_guided_2
button array udg_dlg_btn_guided_1
dialog array udg_dlg_guided
boolean array udg_guided
boolean udg_autopoool_allowed= false
button array udg_dlg_btn_pool_3
button array udg_dlg_btn_pool_2
button array udg_dlg_btn_pool_1
dialog array udg_dlg_pool
hashtable T66_StockHash = InitHashtable()
integer array T66_RandomLeft
unit array T66_Buyer
unit array T66_CarryBuyer
unit T66_LastBuyer = null
boolean array T66_Archived
quest array T66_RecordQuest
string array T66_RecordText
string array T66_Offers
integer T66_ViewCount = 0
fogmodifier array T66_Views
boolean FFHire_Ready = false
hashtable FF_DebugHireHash = InitHashtable()
boolean udg_mode_debugmode= false
integer array udg_gold_gained
integer array udg_unit_kills
integer udg_pn_die= 0
integer udg_pn_killer= 0
integer array udg_base_kills
multiboard udg_multiboard_kills= null
unit udg_dummy_useable= null
integer udg_temp_level= 0
integer udg_count= 0
fogmodifier array udg_Tavern_Visibility
boolean udg_mode_selected= false
button array udg_dlg_btn_mode_05
button array udg_dlg_btn_kick
dialog udg_dlg_kick= null
player udg_Host= null
button array udg_dlg_btn_mode_04
button array udg_dlg_btn_mode_03
button array udg_dlg_btn_mode_02
button array udg_dlg_btn_mode_01
dialog array udg_dlg_mode
group array udg_temp_unitgroup_array
integer udg_tripple_level= 0
integer array udg_hero_deaths
integer array udg_hero_kills
integer array udg_picked_hero
integer array udg_hero_type
integer array udg_MH_player_clicks
integer udg_MH_security_lv= 0
integer array udg_teamnumber
integer array udg_frostbolt_upgrade_level
string array udg_new_name
boolean array udg_admin
dialog array udg_dlg_smurf
boolean array udg_smurfcheck
group array udg_waterfall_units
integer array udg_sinkhole_time
terraindeformation array udg_temp_verformung
boolean array udg_sinkhole_active
location array udg_waterfall_mid
group array udg_waterfall
real udg_temp_degree= 0
location array udg_waterfall_point
integer array udg_new_base
unit array udg_base
boolean udg_balanced= false
boolean udg_mode_no_tp= false
location array udg_SDtavern
unit array udg_mode_selector
boolean array udg_leave_or_votekick
real array udg_coords
boolean udg_mode_inhouse= false
button array udg_dlg_forfeit_btn_no
button array udg_dlg_forfeit_btn_yes
dialog array udg_dlg_forfeit
location array udg_safe_point
group udg_creep= null
player udg_temp_player= null
integer array udg_goldpool
timer udg_timer= null
timerdialog udg_timer_window_premass= null
timer udg_timer_premass= null
group udg_unitgroup_kill= null
player udg_MMD_FlagPlayer= null
player udg_MMD_FLAG_LOOSER= null
player udg_MMD_FLAG_WINNER= null
string array udg_SoundString
integer udg_I= 0
integer udg_IS= 0
integer udg_gametime_min= 0
integer udg_gametime_s= 0
group udg_temp_base= null
fogmodifier array udg_visi_base
group array udg_baseblockers
integer udg_temp_ability= 0
group udg_temp_unitgroup4= null
integer array udg_mh_cnt
group udg_realshops= null
location array udg_block_point
location udg_centermap= null
group udg_blockers= null
integer udg_abilitylevel= 0
group udg_temp_unitgroup3= null
integer udg_version= 0
timer udg_timer_rat2= null
location array udg_tavern
unit array udg_real_shop
unit array udg_fake_shop
string udg_hidden
group udg_temp_unitgroup2= null
integer udg_temp_int= 0
timerdialog udg_timer_window_repick= null
real udg_temp_real= 0
real udg_temp_AoE= 0
location udg_loc_tavern= null
integer udg_temp_playernumber= 0
group array udg_main
integer array udg_spawn_unit
unit udg_temp_unit= null
location udg_temp_point_caster= null
force udg_all_players= null
integer udg_X= 0
integer udg_activeplayersinteam= 0
boolean array udg_swapped
unit array udg_herO
integer array udg_swapto
button array udg_dlg_swap_btn_3
player array udg_ally2
player array udg_ally1
button array udg_dlg_swap_btn_2
button array udg_dlg_swap_btn_1
dialog array udg_dlg_swap
integer array udg_temp_unittype
force udg_temp_playergroup= null
group udg_temp_unitgroup= null
location udg_temp_point= null
boolean array udg_repicked
timer udg_timer_repick= null
timer udg_timer_unhide_cd= null
group udg_fakeshops= null
group udg_truesightunits= null
timer udg_timer_rat= null
integer array udg_leaving_xp
boolean array udg_force_defeat
unit udg_dummy= null
integer udg_DMG= 0
integer udg_AoE= 0
boolean udg_mh_status= false
integer udg_maxunitnumber= 0
string array udg_playerstatus
unit array udg_taverne
unit array udg_orb
integer array udg_autopoolto
string array udg_tp_kill_string
timerdialog udg_timer_window_tech_delay= null
timer udg_timer_tech_delay_t1= null
real udg_t_tech_delay= 0
timerdialog udg_timer_window_voting= null
boolean array udg_maphack
integer udg_selected_mode= 0
string array udg_orig_player_name
boolean array udg_tp_kill
integer array udg_hero
group udg_all_heros= null
boolean array udg_hero_picked_sd
integer udg_total_hero_count= 0
integer array udg_random_hero
timer udg_timer_voting= null
real udg_t_voting= 0
integer udg_SD_votes= 0
integer udg_AR_votes= 0
integer udg_AP_votes= 0
integer array udg_AP
integer array udg_AR
integer array udg_SD
boolean udg_voting= false
integer array udg_leaving_gold
group array udg_unit_group
integer udg_startgold= 0
force array udg_team
boolean array udg_player_active
boolean array udg_xmas
boolean udg_host_is_premium= false
boolean udg_classic54= false
texttag udg_wonky_mode_floating_text= null
unit array udg_dummy_shield
integer array udg_admin_level
location array udg_psionic_transfer_loc
timer array udg_timer_psionic_transfer
unit array udg_dummy_transfer
timer array udg_timer_meta_cd
integer udg_temp_int2= 0
integer array udg_holy_unity_unit_mulitiplier
integer array udg_holy_unity_hero_mulitiplier
integer udg_hero_base_str= 0
integer array udg_holy_unity_max_str
real array udg_mjolnir_degree
unit array udg_dummy_mjolnir
location array udg_mjolnir_location
group array udg_mjolnir_target
location array udg_mjolnir_start_location
boolean array udg_mjolnir_active
rect udg_temp_region= null
boolean udg_version_public= false
integer udg_numberofSDcategories= 0
boolean udg_weather_on= false
boolean udg_daytime= false
unit udg_dummy_gold_aura= null
location array udg_gold_point
effect array udg_gold_effect
string array udg_hure
real udg_t_colossal_reoccuring= 0
real udg_t_colossal_initial= 0
integer array udg_summon_hp
integer array udg_summon_bounty
integer array udg_summon_att_base
integer array udg_ward_hp
unit array udg_deathward
unit array udg_temp_chain_unit
integer array udg_chain_bounces
lightning array udg_chain_lightning
timer udg_timer_chain= null
boolean array udg_hero_is_alchi
integer array udg_colossal_unit_hp_base
real array udg_colossal_unit_hp_actual
real udg_colossal_difficulty= 0
integer array udg_colossal_unit_dmg_base
real array udg_colossal_unit_dmg_actual
unit array udg_waveplayer_shop
real array udg_hero_STR_base
real array udg_hero_STR_inc
real array udg_hero_INT_inc
real array udg_hero_INT_base
real array udg_hero_AGI_inc
real array udg_hero_AGI_base
boolean array udg_player_is_ai
boolean udg_AI_on= false
timer udg_timer_AI_hero_pick= null
real array udg_summon_scale
real array udg_summon_armor
dialog udg_dlg_pool_on_off= null
button udg_dlg_btn_pool_on= null
button udg_dlg_btn_pool_off= null
integer udg_name_length= 0
integer array udg_hashtag_position
integer array udg_player_name_length
boolean udg_eight_player_mode= false
boolean array udg_unit_production
unit array udg_waygate
location array udg_waygate_destination
location array udg_waygate_source
boolean udg_mode_6v6= false
real array udg_hero_move_base
real array udg_hero_turnrate
boolean udg_mode_pub= false
integer array udg_battletag
string array udg_playername
boolean array udg_b1ik
integer udg_creeplimit= 0
boolean array udg_draw
integer array udg_carryhero
integer array udg_carryhero2
timer array udg_timer_defile
location array udg_defile_point
boolean array udg_defile_active
dialog udg_dlg_colossal_amount= null
button array udg_dlg_btn_colossal_amount
integer udg_colossal_max_wave= 0
button array udg_dlg_btn_draw_yes
button array udg_dlg_btn_draw_no
dialog array udg_dlg_draw
integer array udg_colossal_wave_steps
integer array udg_carryhero3
real array udg_temp_AoE_array
group array udg_smite_heal_unitgroup
integer array udg_summon_mana
integer array udg_colossal_unit_bounty_base
real array udg_colossal_unit_bounty_actual
location array udg_prison_wall_point_1
unit array udg_prison_wall_1
unit array udg_prison_wall_2
unit array udg_prison_wall_3
unit array udg_prison_wall_4
timer array udg_prison_timer
location array udg_prison_wall_point_2
location array udg_prison_wall_point_3
location array udg_prison_wall_point_4
texttag array udg_prison_wall_text_1
texttag array udg_prison_wall_text_2
texttag array udg_prison_wall_text_3
texttag array udg_prison_wall_text_4
real array udg_prison_wall_duration
timer udg_timer_tech_delay_t3= null
real udg_colossal_aggro_range= 0
integer array udg_mm_hero_1
integer array udg_mm_hero_2
integer array udg_mm_hero_3
location array udg_prison_block_point_1
location array udg_prison_block_point_2
location array udg_prison_block_point_3
location array udg_prison_block_point_4
destructable array udg_prison_block_1
destructable array udg_prison_block_2
destructable array udg_prison_block_4
destructable array udg_prison_block_3
integer array udg_colossal_unit_type
boolean udg_mode_mirror= false
integer udg_mm_max= 0
boolean array udg_hook_send_active
location array udg_hook_location
location array udg_hook_start_location
group array udg_hook_target_group
real array udg_hook_degree
unit array udg_dummy_hook
boolean array udg_hook_return_active
boolean array udg_hook_target_aquired
unit array udg_hook_target
boolean array udg_hook_first
lightning array udg_hook_lightning
real array udg_hook_range
unit array udg_hook_caster
// Refund amount for a rejected Grappling Hook purchase. Keep in step with the
// igol field on item I0HK in war3map.w3t.
integer udg_hook_shop_cost= 750
integer udg_colossal_wave_id= 0
integer array udg_colossal_unit_mp_base
timer udg_timer_mm_autopick= null
integer udg_mm_combo_id= 0
boolean udg_autohost= false
integer array udg_skill
real array udg_colossal_unit_armor
boolean array udg_AI_player
integer array udg_colossal_unit_id
integer udg_X_colo= 0
unit udg_spawned_colo= null
integer array udg_colossal_number_of_units
integer array udg_colossal_min_wave
timer array udg_timer_spell_cd
real udg_hp_buff= 0
integer array udg_colossal_unit_armor_type
integer array udg_base_bounty
integer array udg_team_unit_kills
integer array udg_team_hero_kills
integer array udg_temp_int_array
real array udg_temp_real_array
integer array udg_unit_level
integer array udg_colossal_unit_level
integer array udg_uk_number
integer array udg_uk_reward
button array udg_dlg_votekick_btn_confirm
unit array udg_dummy_flag
timer udg_timer_tech_delay_t2= null
boolean udg_mode_koth= false
integer udg_mode_koth_current_wave= 0
integer array udg_mode_koth_gold_gain
location udg_mode_koth_point= null
integer array udg_mode_koth_gold_cap
integer udg_mode_koth_current_king= 0
integer udg_mode_koth_current_gold= 0
unit udg_mode_koth_current_tower= null
boolean udg_mode_1v1= false
location array udg_player_start
group array udg_projectile_target
location array udg_projectile_start_location
location array udg_projectile_location
real array udg_projectile_degree
boolean array udg_projectile_active
unit array udg_dummy_projectile
timer udg_timer_koth= null
real array udg_mode_koth_time
timerdialog udg_timer_window_koth= null
texttag udg_mode_koth_text= null
integer udg_mode_koth_max_wave= 0
timer array udg_timer_slap
integer udg_exp_sys_low= 0
integer udg_exp_sys_high= 0
integer udg_exp_sys_level= 0
boolean array udg_Suicide_Has_Started
boolean udg_Votekick_Is_Active= false
player udg_Votekick_Target_Player= null
dialog udg_Votekick_Dialog_Initiate= null
button udg_Votekick_Button_Ally1= null
button udg_Votekick_Button_Ally2= null
button udg_Votekick_Button_Cancel= null
timer udg_Votekick_Timer= null
player udg_Votekick_Start_Player= null
boolean array udg_Votekick_Player_Disabled
integer udg_Votekick_Allied_Votes= 0
integer udg_Votekick_Allied_Votes_Needed= 0
dialog udg_Votekick_Dialog_YesNo= null
button udg_Votekick_Button_Yes= null
button udg_Votekick_Button_No= null
boolean udg_Votekick_Defeat_Kicked_Player= false
unit array udg_Pub_Defenders
integer udg_Pub_Team_Number= 0
integer udg_Pub_Loop= 0
location array udg_Pub_Center_Points
boolean udg_Pub_Defenders_Remove= false
integer udg_Missile= 0
boolean udg_MissileDestroy= false
location udg_MissileStart= null
real udg_MissileStartZ= 0
location udg_MissileFinish= null
real udg_MissileFinishZ= 0
string udg_MissileModel
real udg_MissileScale= 0
real udg_MissileSpeed= 0
real udg_MissileDuration= 0
real udg_MissileArc= 0
real udg_MissileCurve= 0
real udg_MissileDamage= 0
real udg_MissileCollision= 0
real udg_MissileAcceleration= 0
real udg_MissileVision= 0
boolean udg_MissileCollideZ= false
unit udg_MissileSource= null
unit udg_MissileTarget= null
player udg_MissileOwner= null
boolean udg_MissileRoll= false
integer udg_MissileType= 0
integer udg_MissileData= 0
real udg_MissileTimeScale= 0
integer udg_MissileAlpha= 0
integer udg_MissilePlayerColor= 0
integer udg_MissileAnimation= 0
boolean udg_MissileRemoveLocations= false
boolean udg_MissilePaused= false
location udg_MissilePosition= null
real udg_MissileZ= 0
location udg_MissileLastPosition= null
real udg_MissilePrevZ= 0
location udg_MissileNextPosition= null
real udg_MissileNextZ= 0
real udg_MissileVelocity= 0
real udg_MissileTravelled= 0
location udg_MissileDeflectPosition= null
real udg_MissileDeflectZ= 0
unit udg_MissileDeflectTarget= null
integer udg_MissileGroup= 0
integer udg_MissileAt= 0
integer udg_MissileGroupAddGroup= 0
integer udg_MissileGroupRemoveGroup= 0
integer udg_MissileGroupSize= 0
location udg_MissileGroupLocation= null
rect udg_MissileGroupRect= null
real udg_MissileGroupRange= 0
player udg_MissileGroupPlayer= null
integer udg_MissileGroupType= 0
integer udg_MissileGroupCounted= 0
unit udg_MissileFlushUnit= null
unit udg_MissileHittedUnit= null
boolean udg_MissileHitted= false
string udg_MissileAttachModel
real udg_MissileAttachX= 0
real udg_MissileAttachY= 0
real udg_MissileAttachZ= 0
real udg_MissileAttachScale= 0
effect udg_MissileDetachEffect= null
integer udg_MissileRed= 0
integer udg_MissileGreen= 0
integer udg_MissileBlue= 0
trigger udg_Missile_onPeriod= null
trigger udg_Missile_onHit= null
trigger udg_Missile_onDestructable= null
trigger udg_Missile_onItem= null
trigger udg_Missile_onMissile= null
trigger udg_Missile_onCliff= null
trigger udg_Missile_onTerrain= null
trigger udg_Missile_onTileset= null
trigger udg_Missile_onFinish= null
trigger udg_Missile_onBoundaries= null
trigger udg_Missile_onPause= null
trigger udg_Missile_onResume= null
trigger udg_Missile_onRemove= null
integer udg_MissileEvent= 0
integer udg_MissileOnPeriod= 0
integer udg_MissileOnHit= 0
integer udg_MissileOnMissile= 0
integer udg_MissileOnDestructable= 0
integer udg_MissileOnItem= 0
integer udg_MissileOnTerrain= 0
integer udg_MissileOnFinish= 0
integer udg_MissileOnBoundaries= 0
integer udg_MissileOnPause= 0
integer udg_MissileOnResume= 0
integer udg_MissileOnRemove= 0
integer udg_MissileOnCliff= 0
integer udg_MissileOnTileset= 0
unit udg_MissileHitUnit= null
destructable udg_MissileHitDestructable= null
item udg_MissileHitItem= null
integer udg_MissileHitMissile= 0
integer udg_MissileTileset= 0
unit udg_KOTH_Hill= null
timer udg_KOTH_Setup_Timer= null
timer udg_KOTH_Income_Timer= null
timer udg_KOTH_Second_Hill_Timer= null
player udg_KOTH_Player= null
force udg_KOTH_Team= null
integer udg_KOTH_Team_Number= 0
integer udg_KOTH_Team_Size= 0
integer array udg_KOTH_Team_Gold_Earned_Reset
integer array udg_KOTH_Team_Gold_Earned_Total
integer udg_KOTH_Gold_To_Add= 0
integer udg_KOTH_Gold_Division_Bonus= 0
integer udg_KOTH_Gold_Division_To_Add= 0
integer udg_KOTH_Gold_Starting_Total= 0
integer udg_KOTH_Gold_Remaining= 0
integer udg_KOTH_Gold_Rewarded= 0
integer udg_KOTH_Gold_Reset_Amount= 0
integer udg_KOTH_Gold_Half_Remaining= 0
boolean udg_KOTH_Gold_Half_Reached= false
string udg_KOTH_Text
texttag udg_KOTH_Floating_Text= null
effect udg_KOTH_Regen_SFX= null
effect udg_KOTH_Hill_Glow_SFX= null
location udg_KOTH_Point= null
timerdialog udg_KOTH_Timer_Window= null
real udg_KOTH_Percentage= 0
boolean udg_KOTH_Should_Reset_Hill= false
boolean array udg_KOTH_25_Percent_Gold_Check
integer array udg_KOTH_25_Percent_Gold_Amount
boolean udg_UnitIndexerEnabled= false
integer udg_UDexGen= 0
integer udg_UDexRecycle= 0
unit array udg_UDexUnits
real udg_UnitIndexEvent= 0
boolean array udg_IsUnitPreplaced
integer array udg_UDexPrev
integer array udg_UDexNext
integer udg_UDex= 0
integer udg_UDexWasted= 0
real array udg_Avalanche_TS_Duration
real array udg_Avalanche_TS_Height
unit array udg_Avalanche_TS_Source
unit array udg_Avalanche_TS_Target
group udg_Avalanche_TS_Target_Group= null
group udg_Avalanche_TS_Nearby_Group= null
unit udg_Avalanche_TS_Picked_Unit= null
unit udg_Avalanche_TS_Closest_Unit= null
location array udg_Avalanche_TS_Point
integer udg_Avalanche_TS_CV= 0
real array udg_Avalanche_TS_Current_Time
real array udg_Avalanche_TS_Height_Rate
real array udg_Avalanche_TS_Height_Factor
real array udg_Avalanche_TS_Distance_Check
integer udg_Avalanche_TS_Target_Count= 0
real udg_Avalanche_TS_Remaining_Time= 0
real udg_Avalanche_TS_Speed= 0
real udg_Avalanche_TS_Interval= 0
real array udg_Avalanche_TS_Damage
integer array udg_Destroyer_Player_Number
integer array udg_hook_level
integer array udg_mjolnir_level_Copy
integer array udg_blocker_ID_Array
boolean array udg_Is_A_Spawn
unit array udg_Avalanche_TR_Caster
unit array udg_Avalanche_TR_Dummy
integer udg_Avalanche_TR_Index= 0
integer udg_Avalanche_TR_Loop= 0
integer array udg_Avalanche_TR_Duration
real array udg_Avalanche_TR_Angle
location array udg_Avalanche_TR_Point
item udg_CPP_Pathing_Checker= null
group udg_Avalanche_TR_Group= null
real array udg_Avalanche_TR_Damage
group array udg_Avalanche_TR_Group_Limit
unit udg_Avalanche_CE_Dummy= null
location array udg_Avalanche_CE_Point
unit udg_Avalanche_CE_Attacker= null
integer udg_Avalanche_CE_Level= 0
integer array udg_Avalanche_SF_Stacks
integer udg_Avalanche_CV= 0
boolean array udg_Avalanche_SF_Learned
unit udg_Avalanche= null
group udg_Avalanche_SF_Enemy_Group= null
unit udg_Avalanche_SF_Target= null
integer udg_Avalanche_SF_Stacks_Needed= 0
boolean array udg_Avalanche_SF_Is_Casting
group udg_Avalanche_SF_Caster_Group= null
integer array udg_Avalanche_SF_Duration
location array udg_Avalanche_SF_Point
real udg_DDE_Duration= 0
real array udg_Avalanche_SF_Damage
unit udg_Avalanche_SF_Dummy= null
location array udg_Akama_Point
unit udg_Akama= null
unit array udg_Akama_SC_Clone
integer udg_Akama_CV= 0
integer array udg_Akama_Integer
group udg_Akama_SC_Hero_Group= null
integer array udg_Akama_SC_Update
unit array udg_Akama_SC_Hero
real array udg_Akama_Real
location array udg_Akama_Blink_Point
effect array udg_Akama_Blink_Sfx
real array udg_Akama_SC_Duration
lightning udg_bill_lightning= null
unit udg_TheNook= null
unit array udg_TheNook_HK_Target
integer udg_TheNook_CV= 0
integer array udg_TheNook_HK_Duration
group udg_TheNook_HK_Group= null
location array udg_TheNook_Points
location array udg_TheNook_HK_Point
group udg_TheNook_Temp_Group= null
unit udg_TheNook_Target= null
unit udg_TheNook_Dummy= null
real array udg_TheNook_Real
integer array udg_TheNook_Integer
integer array udg_TheNook_BA_Stacks
unit udg_GST_Unit1= null
unit udg_GST_Unit2= null
unit udg_GST_Unit3= null
integer udg_GST_Integer1= 0
integer udg_GST_Integer2= 0
integer udg_GST_Integer3= 0
real udg_GST_Real1= 0
real udg_GST_Real2= 0
real udg_GST_Real3= 0
item udg_GST_Item1= null
trigger udg_GST_Trigger= null
integer udg_GST_RestartKey= 0
timer udg_GST_Timer= null
effect udg_GST_Effect1= null
real array udg_TheNook_BA_Value
group udg_TheNook_HS_Hero_Group= null
integer array udg_TheNook_HS_Duration
force udg_Floating_Text_PG= null
unit udg_SovietSniper= null
integer udg_SovietSniper_CV= 0
group udg_SovietSniper_GS_Caster_Group= null
integer array udg_SovietSniper_GS_Duration
boolean array udg_SovietSniper_GS_Is_Casting
location array udg_SovietSniper_GS_Point
integer array udg_SovietSniper_Integer
location array udg_SovietSniper_Point
real array udg_SovietSniper_Real
group array udg_SovietSniper_Group
unit array udg_SovietSniper_Unit
group udg_SovietSniper_RP_Caster_Group= null
boolean array udg_SovietSniper_RP_Atk_On
boolean array udg_SovietSniper_RS_Delay_Ration
group udg_SovietSniper_DB_Bomb_Group= null
integer array udg_SovietSniper_DB_Duration
unit array udg_SovietSniper_DB_Hero
real array udg_SovietSniper_DB_Damage_Per_Lvl
unit udg_Guardian= null
integer udg_Guardian_CV= 0
integer udg_Guardian_FF_Index= 0
integer udg_Guardian_FF_Loop= 0
location array udg_Guardian_Point
real array udg_Guardian_Real
integer array udg_Guardian_Integer
location array udg_Guardian_FF_Point
real array udg_Guardian_FF_Angle
boolean udg_DDE_Hide_Death_Animation= false
group array udg_Guardian_Group
unit array udg_Guardian_Unit
group udg_Guardian_PB_Group= null
unit array udg_Guardian_PB_Target
real array udg_Guardian_PB_Speed
integer array udg_Guardian_PB_Duration
real array udg_Guardian_PB_Damage
location array udg_Guardian_PB_Target_Point
integer udg_Guardian_EC_Ability= 0
group udg_Guardian_EC_Group= null
real array udg_Guardian_PW_Angle
real array udg_Guardian_PW_Damage
real array udg_Guardian_PW_Mana_Loss
group array udg_Guardian_PW_Hit_Group
integer udg_Guardian_PW_Index= 0
integer udg_Guardian_PW_Loop= 0
effect array udg_Guardian_PW_Missile
integer array udg_Guardian_PW_Duration
location array udg_Guardian_PW_Point
unit array udg_Guardian_PW_Hero
real array udg_Guardian_PB_Damage_Per_Lvl
real array udg_Guardian_FF_Duration
real array udg_Guardian_FF_Duration_Per_Lvl
real array udg_Guardian_PW_Damage_Per_Lvl
integer array udg_Guardian_FF_Level
unit array udg_Guardian_FF_Caster
integer array udg_Avalanche_TR_Animation
timer array udg_timer_interchange
group udg_Avatar_Sfx_Group= null
effect array udg_Avatar_Sfx_1
effect array udg_Guardian_PB_Targeting_Sfx
effect udg_DDE_Effect= null
real array udg_Avalanche_TR_Speed
real array udg_TheNook_R_Damage_Per_Lvl
timer udg_Pub_Mode_Creep_Timer= null
integer udg_MadWizard_CV= 0
unit udg_Wheelchair_Duplicate= null
timer udg_Fortification_Aura_Timer= null
unit udg_MadWizard= null
player udg_MadWizard_Player= null
group udg_MadWizard_Group= null
integer array udg_MadWizard_Bomb_Counter
unit udg_MadWizard_Bomb= null
unit udg_DummyNew= null
integer array udg_Avalanche_TR_Max_Duration
integer array udg_Avalanche_TR_Interval
location udg_ExpPoint= null
unit udg_ExpDeadUnit= null
unit udg_ExpKillingUnit= null
group udg_ExpGroup= null
player udg_ExpPlayer= null
integer array udg_ExpInt
unit udg_BountyHero= null
integer array udg_TeamUnitKills
integer udg_TeamNumber= 0
integer udg_Team1stPlace= 0
integer udg_Team2ndPlace= 0
real array udg_SovietSniper_DB_Damage
real array udg_SovietSniper_GS_Damage_Per_Lvl
real udg_Team1stPlaceBountyMultiplier= 0
real udg_Team2ndPlaceBountyMultiplier= 0
integer array udg_Vengeance_Counter
location array udg_MIC_Point
unit udg_MIC_Caster= null
unit array udg_MIC_Caster_Link
unit udg_MIC_Dummy= null
integer udg_MIC_CV= 0
integer udg_MIC_Loop= 0
integer udg_MIC_Level= 0
integer array udg_MIC_Illusion_Count
real udg_MIC_Angle= 0
group array udg_MIC_Illusions
integer udg_Guardian_FF_Detonate= 0
hashtable udg_Guardian_FF_Hash= null
integer array udg_Guardian_FF_Count
location udg_Rune_AMS_Point= null
unit udg_Rune_AMS_Dummy= null
integer udg_spawnCount= 0
timer udg_spawnTimer= null
group udg_RAA_Group= null
integer array udg_Summon_Dragons_Type_1
integer array udg_Summon_Dragons_Type_2
real array udg_Summon_Dragons_Duration
location array udg_Summon_Dragons_Point
integer udg_Summon_Dragons_Level= 0
timer udg_spawnMassTimer= null
timer udg_timer_premass_bonus= null
integer array udg_Mass_Bonus_Spawns
integer udg_Mass_Cycle= 0
boolean udg_Footmen_Is_Level_2= false
integer udg_BountyTaperOffCounter= 0
real array udg_Exp_Rate
integer udg_Exp_PN= 0
boolean array udg_Exp_Level_Was_Reached
integer udg_Exp_Level= 0
unit udg_NS_Target= null
real array udg_NS_Damage
location array udg_NS_Point
real udg_NS_Angle= 0
unit udg_NS_Dummy= null
group udg_HU_Group= null
unit udg_HU_Hero= null
integer array udg_HU_Duration
integer udg_HU_CV= 0
real array udg_WooJ_Shock_Damage
unit udg_col_dying_unit= null
unit udg_col_killing_unit= null
integer udg_col_dying_unit_type= 0
location udg_col_death_point= null
unit udg_col_picked_unit= null
group udg_col_picked_group= null
real array udg_HU_Damage_Per_Lvl
group udg_Defile_Group= null
unit udg_Defile_Caster= null
real array udg_Defile_Damage
integer udg_Defile_Level= 0
real udg_KOTH_Start_Delay= 0
boolean udg_mode_colo_frenzy= false
boolean udg_mode_overdrive= false
unit udg_NS_Target_Copy= null
real array udg_NS_Damage_Copy
real udg_NS_Angle_Copy= 0
location array udg_NS_Point_Copy
unit udg_NS_Dummy_Copy= null
group udg_HU_Group_Copy= null
unit udg_HU_Hero_Copy= null
integer array udg_HU_Duration_Copy
real array udg_HU_Damage_Per_Lvl_Copy
integer udg_HU_CV_Copy= 0
integer array udg_carryhero4
// CarryTav - second (carry) altar per team, hero categories 12-18
unit array CarryTav_shop
integer array CarryTav_hero
integer array CarryTav_count
boolean array CarryTav_locked
// OD_BonusTavern: peasant-built extra Carry Tavern, Overdrive mode only.
unit array OD_CarryTav_shop2
trigger gg_trg_OD_BonusTavern_Build= null
// Automatic hero assignment: remembers the heroes stocked in each team's taverns.
integer array FF_AutoPick_hero
integer array FF_AutoPick_category
integer array FF_AutoPick_count
timer FF_AutoPick_timer= null
integer udg_Guardian_PW_Loop_Copy= 0
boolean array udg_Jungle_active
real array udg_Jungle_degree
location array udg_Jungle_location
location array udg_Jungle_start_location
group array udg_Jungler_target
unit array udg_dummy_Jungle
boolean udg_mode_strong_mode= false
real array udg_glaive_degree
unit array udg_dummy_glaive
boolean array udg_glaive_active
location array udg_glaive_location
integer array udg_glaive_hops
real array udg_glaive_start_degree
unit udg_AkamaUlt= null
group udg_Wrath_Group= null
unit udg_Wrath_Caster= null
real array udg_Wrath_Damage
integer udg_Wrath_Level= 0
location array udg_wrath_point
boolean array udg_wrath_active
timer array udg_timer_wrath
group array udg_LS_Groups
integer udg_LS_GeneralInteger= 0
location array udg_LS_TempPoint
unit udg_LS_Dummy= null
boolean udg_KBA_DestroyTrees= false
boolean array udg_KB_DestroyTrees
unit array udg_KB_Casters
unit udg_KBA_Caster= null
string array udg_KB_Effects_2
string array udg_KB_Effects_1
string array udg_KBA_SpecialEffects
real udg_KBA_DistancePerLevel= 0
real udg_KBA_Speed= 0
integer udg_KBA_Level= 0
location udg_KBA_StartingPosition= null
unit udg_KBA_TargetUnit= null
real array udg_KB_SpecificSpeed
integer udg_KB_CountBuffs= 0
real udg_KB_ReducedReal= 0
real udg_KB_TempReal= 0
real array udg_KB_ReduceSpeedReal
integer array udg_KB_GeneralIntegers
location array udg_KB_TempPoint
real array udg_KB_ReachedDistance
real array udg_KB_Angle
real array udg_KB_MaxDistance
integer udg_KB_TotalKnockUnits= 0
integer array udg_KB_Levels
location array udg_KB_StartPositions
unit array udg_KB_Units
group udg_KB_KnockbackedUnits= null
location array udg_Creep_Point
integer udg_Temp_Integer= 0
timer array udg_timer_wrath_effect
boolean array udg_Wrath_Effect
group array udg_TemporaryGroup
location array udg_TemporaryPoint
integer udg_TemporaryKeySpell= 0
handle udg_TemporaryKeyTarget= null
integer udg_SpellMaximumNumberHits= 0
real udg_SpellBounceRange= 0
unit udg_TemporaryTarget= null
hashtable udg_PowerChainHash= null
real udg_SpellBounceSpeed= 0
group udg_PowerChainGroup= null
integer udg_SpellNumberBounces= 0
real udg_TemporaryReal= 0
real udg_TemporaryTime= 0
real udg_TemporaryAngle= 0
boolean udg_mode_no_mass= false
unit udg_Deadeye= null
integer array udg_Deadeye_GS_Duration
group udg_Deadeye_DB_Bomb_Group= null
real array udg_Deadeye_DB_Damage
real array udg_Deadeye_DB_Damage_Per_Lvl
unit array udg_Deadeye_DB_Hero
group array udg_Deadeye_Group
group udg_Deadeye_GS_Caster_Group= null
integer array udg_Deadeye_DB_Duration
real array udg_Deadeye_GS_Damage_Per_Lvl
boolean array udg_Deadeye_GS_Is_Casting
location array udg_Deadeye_GS_Point
integer array udg_Deadeye_Integer
location array udg_Deadeye_Point
real array udg_Deadeye_Real
boolean array udg_Deadeye_RP_Atk_On
group udg_Deadeye_RP_Caster_Group= null
boolean array udg_Deadeye_RS_Delay_Ration
unit array udg_Deadeye_Unit
integer udg_Deadeye_CV= 0
unit udg_KOTH_Dummy= null
real udg_HC_EffectScalingBlast= 0
real udg_HC_EffectZBlast= 0
player array udg_HC_OwningPlayer
real udg_HC_MagnetismCap= 0
real udg_HC_CurrentMagnetism= 0
real udg_HC_BlastCap= 0
boolean array udg_HC_ConditionConfig
real udg_HC_DummyExpirationTimers= 0
real udg_HC_ExplosionAOE= 0
real array udg_HC_MaxHeight
real array udg_HC_CurrentHeight
real array udg_HC_CurrentAngle
unit udg_HC_TempUnit2= null
real udg_HC_EffectZWind= 0
real udg_HC_EffectZOrbs= 0
real udg_HC_WindDistance= 0
real udg_HC_OrbDistance= 0
integer udg_HC_TempInteger2= 0
real array udg_HC_CurrentSunDistance
unit udg_HC_Caster= null
real udg_HC_BlastDistanceBase= 0
real udg_HC_EffectScalingWind= 0
real udg_HC_EffectScalingSun= 0
real udg_HC_EffectZSun= 0
integer udg_HC_WindCountPerLevel= 0
integer udg_HC_WindCountBase= 0
integer udg_HC_OrbCountPerLevel= 0
integer udg_HC_OrbCountBase= 0
string udg_HC_SunSFX
integer udg_HC_SecondaryIndex= 0
string udg_HC_BurnSFX
real udg_HC_WindSpinSpeed= 0
real udg_HC_FireOrbSpinSpeed= 0
real udg_HC_SunSpeed= 0
string udg_HC_WindSFX
string udg_HC_FireOrbSFX
real array udg_HC_CurrentBlastDistance
real udg_HC_BlastDistanceMultiplyer= 0
real array udg_HC_BlastDistance
real udg_HC_HeightMultiplyer= 0
real udg_HC_BlastSpeed= 0
real udg_HC_MagnetismDistanceMultiplyer= 0
real array udg_HC_MagnetismStrength
real udg_HC_MagnetismStrengthPerLevel= 0
real udg_HC_MagnetismStrengthBase= 0
real array udg_HC_Distance
effect array udg_HC_SpecialEffect
location udg_HC_TempPoint2= null
real udg_HC_TempZ= 0
unit array udg_HC_Core
real udg_HC_TempY= 0
real udg_HC_TempX= 0
unit array udg_HC_OriginalCaster
unit array udg_HC_UnitIndex
integer array udg_HC_StageID
real udg_HC_TempReal= 0
real array udg_HC_ExplosionDamage
real array udg_HC_Aoe
unit udg_HC_TempUnit= null
integer udg_HC_DummyType= 0
real udg_HC_EffectScalingOrbs= 0
integer udg_HC_MaxIndex= 0
string udg_HC_ExplosionSFX
integer udg_HC_TempInteger= 0
integer udg_HC_Index= 0
group udg_HC_TempGroup= null
group udg_HC_Targets= null
real udg_HC_Angle= 0
location udg_HC_TempPoint= null
integer udg_HC_Spell= 0
real udg_HC_AoePerLevel= 0
real udg_HC_AoeBase= 0
real udg_HC_ExplosionDamagePerLevel= 0
real udg_HC_ExplosionDamageBase= 0
real udg_CP_CageScale= 0
string udg_CP_PulseModel
string udg_CP_CageModel
string udg_CP_PortalModel
integer udg_CP_UHandleC2= 0
real udg_CP_TempY2= 0
real udg_CP_TempX2= 0
location udg_CP_TempPoint3= null
boolean udg_CP_TreeKill= false
real udg_CP_TreeAreaDestroy= 0
unit udg_CP_TreeChecker= null
real udg_CP_KnockbackStrengthDetriment= 0
integer udg_CP_CageProjectileFireRate= 0
real udg_CP_CageSpeed= 0
real udg_CP_CageSegmentAoe= 0
integer udg_CP_PulsesPerLevel= 0
integer udg_CP_PulsesBase= 0
real udg_CP_PortalMaxSize= 0
real udg_CP_PortalGrowthSpeed= 0
real udg_CP_PortalStartSize= 0
real udg_CP_KnockbackStrengthPerLevel= 0
integer udg_CP_TempInteger= 0
integer udg_CP_i= 0
real array udg_CP_RealCache
unit udg_CP_TempU2= null
group udg_CP_TempGroup= null
group udg_CP_PortalGroup= null
real udg_CP_TempReal= 0
real udg_CP_Angle= 0
integer udg_CP_UHandleC= 0
unit udg_CP_TempU= null
integer udg_CP_UHandle= 0
unit udg_CP_U= null
real udg_CP_KnockbackStrengthBase= 0
location udg_CP_TempPoint2= null
location udg_CP_TempPoint= null
integer udg_CP_Portal= 0
integer udg_CP_Spell= 0
real udg_CP_TempY= 0
real udg_CP_TempX= 0
real udg_CP_HeightMultiplyer= 0
real udg_CP_AoePerLevel= 0
real udg_CP_AoeBase= 0
real udg_CP_DamagePerLevel= 0
real udg_CP_DamageBase= 0
hashtable udg_CP_Hash= null
real array udg_AB_StartHeight
real array udg_AB_EndHeight
real udg_AB_L_PeriodicTimer= 0
real udg_AB_L_Height= 0
integer udg_AB_L_MaxIndex= 0
integer udg_AB_L_LoopInt= 0
integer udg_AB_L_ID= 0
integer udg_AB_L_RecycledSize= 0
integer array udg_AB_L_RecycledStack
integer array udg_AB_L_NodePrev
integer array udg_AB_L_NodeNext
integer udg_AB_L_Count= 0
real array udg_AB_L_Counter
lightning array udg_AB_L
real udg_AB_L_Alpha= 0
real udg_AB_L_Blue= 0
real udg_AB_L_Green= 0
real udg_AB_L_Red= 0
real udg_AB_L_Duration= 0
string udg_AB_L_SFX
string udg_AB_SFX_KillCountIndicator
boolean udg_Spell__StartDuration= false
real udg_Spell__DurationPerLevel= 0
real udg_Spell__LevelMultiplier= 0
boolean udg_Spell__Expired= false
real array udg_Spell_i_LastTime
real array udg_Spell_i_Duration
real udg_Spell__Duration= 0
unit array udg_Spell__InRangeUnits
integer udg_Spell__InRangeCount= 0
group array udg_Spell_i_GroupStack
integer udg_Spell_i_GroupN= 0
boolean array udg_Spell_i_Channeling
boolean udg_Spell__Channeling= false
boolean array udg_Spell_i_AllowLiving
boolean array udg_Spell_i_AllowStructure
boolean array udg_Spell_i_AllowNonHero
boolean array udg_Spell_i_AllowMechanical
boolean array udg_Spell_i_AllowMagicImmune
boolean array udg_Spell_i_AllowHero
boolean array udg_Spell_i_AllowFlying
boolean array udg_Spell_i_AllowEnemy
boolean array udg_Spell_i_AllowDead
boolean array udg_Spell_i_AllowAlly
location udg_Spell__InRangePoint= null
real udg_Spell__InRange= 0
group udg_Spell__InRangeGroup= null
integer udg_Spell__Ability= 0
unit udg_Spell_i_PreloadDummy= null
integer array udg_Spell_i_Head
integer array udg_Spell_i_RecycleList
integer array udg_Spell_i_Stack
integer array udg_Spell_i_StackRef
integer udg_Spell_i_StackN= 0
integer udg_Spell_i_Instances= 0
trigger array udg_Spell_i_OnCastStack
integer udg_Spell_i_Recycle= 0
trigger udg_Spell__Trigger_OnCast= null
trigger array udg_Spell_i_OnChannelStack
trigger udg_Spell__Trigger_OnChannel= null
trigger array udg_Spell_i_OnEffectStack
trigger udg_Spell__Trigger_OnEffect= null
trigger array udg_Spell_i_OnFinishStack
integer udg_Spell__Index= 0
trigger udg_Spell__Trigger_OnFinish= null
trigger array udg_Spell_i_OnLoopStack
hashtable udg_Spell__Hash= null
trigger udg_Spell__Trigger_OnLoop= null
boolean array udg_Spell_i_Linked
integer array udg_Spell_i_EventType
boolean array udg_Spell_i_Completed
boolean array udg_Spell_i_UseTG
timer udg_Spell_i_Timer= null
boolean udg_Spell__Completed= false
boolean udg_Spell__UseTargetGroup= false
boolean udg_Spell__Running= false
group udg_Spell__TargetGroup= null
group array udg_Spell_i_TargetGroup
unit array udg_Spell_i_Caster
unit array udg_Spell_i_Target
unit udg_Spell__Target= null
unit udg_Spell__Caster= null
location udg_Spell__TargetPoint= null
location udg_Spell__CastPoint= null
real array udg_Spell_i_TargetX
real array udg_Spell_i_TargetY
real array udg_Spell_i_Time
real udg_Spell__Time= 0
player udg_Spell__CasterOwner= null
integer udg_Spell__Level= 0
integer array udg_Spell_i_Level
boolean udg_Spell__WakeTargets= false
boolean udg_Spell__Filter_AllowMagicImmune= false
boolean udg_Spell__Filter_AllowStructure= false
boolean udg_Spell__Filter_AllowMechanical= false
boolean udg_Spell__Filter_AllowFlying= false
boolean udg_Spell__Filter_AllowDead= false
boolean udg_Spell__Filter_AllowAlly= false
boolean udg_Spell__Filter_AllowNonHero= false
boolean udg_Spell__Filter_AllowHero= false
boolean udg_Spell__Filter_AllowLiving= false
boolean udg_Spell__Filter_AllowEnemy= false
real udg_Spell__Interval= 0
player udg_Spell__DummyOwner= null
integer udg_Spell__DummyType= 0
location udg_Map_TempLoc= null
integer udg_Map_LoopInt= 0
group udg_Map_RandomGroup= null
real array udg_Map_FacingAngle
location array udg_Map_SpawnLoc
player array udg_Map_Owner
integer array udg_Map_UnitType
integer udg_Map_UnitID= 0
unit udg_Map_TempUnit= null
integer udg_Map_MaxInt= 0
group udg_Map_TempGroup= null
player udg_Map_Player= null
real udg_AB_SW_KBTime= 0
real udg_AB_SW_KBDistance= 0
real udg_AB_SW_AoE= 0
integer array udg_AB_RequiredKills
integer udg_LoopInt= 0
boolean udg_Knockback2DUnbiasedCollision= false
boolean array udg_K2DUnbiasedCollision
unit udg_Knockback2DSource= null
boolean udg_Knockback2DSimple= false
boolean array udg_K2DSimple
boolean array udg_K2DPause
boolean array udg_K2DOverride
trigger udg_Knockback2DOnImpact= null
real array udg_K2DFXTimeLeft
real array udg_K2DFXRate
string array udg_K2DFXModel
real udg_Knockback2DCollision= 0
real array udg_K2DCollision
boolean array udg_K2DBounce
boolean udg_Knockback2DAmphibious= false
boolean array udg_K2DAmphibious
real array udg_K2DDestRadius
boolean array udg_K2DKillTrees
real array udg_K2DVelocity
real array udg_K2DFriction
real array udg_K2DSinD2
real array udg_K2DCosD2
real array udg_K2DSinD1
real array udg_K2DCosD1
real array udg_K2DSinH
real array udg_K2DCosH
integer array udg_K2DRadius
boolean array udg_K2DFlying
real array udg_K2DSin
real array udg_K2DCos
real array udg_K2DLastY
real array udg_K2DLastX
real array udg_K2DHeightThreshold
real udg_Knockback2DHeight= 0
boolean udg_Knockback2DOverride= false
real array udg_K2DTimeLeft
real array udg_K2DDistanceLeft
real array udg_K2DAngle
unit array udg_K2DSource
trigger array udg_K2DImpact
boolean array udg_K2DFreeze
real array udg_K2DHeight
timer udg_K2DTimer= null
integer array udg_K2DNext
integer array udg_K2DPrev
boolean array udg_IsUnitBeingKnockedBack
boolean udg_K2DItemOffset= false
boolean udg_K2DItemsFound= false
real udg_K2DMaxDestRadius= 0
real udg_K2DMinY= 0
real udg_K2DMinX= 0
real udg_K2DMaxY= 0
real udg_K2DMaxX= 0
rect udg_K2DRegion= null
real udg_Radians_QuarterPi= 0
real udg_Radians_QuarterTurn= 0
real udg_Radians_Turn= 0
unit udg_K2DDebrisKiller= null
item udg_K2DItem= null
real udg_K2DY= 0
real udg_K2DX= 0
location udg_CenterPoint= null
real udg_Knockback2DFXRate= 0
real udg_Knockback2DDefaultFXRate= 0
string udg_Knockback2DDefaultFX
real udg_Knockback2DGravity= 0
real udg_Knockback2DDefaultGravity= 0
string udg_Knockback2DTreeOrDebris
real udg_Knockback2DDestRadius= 0
real udg_Knockback2DDefaultDestRadius= 0
boolean udg_Knockback2DKillTrees= false
boolean udg_Knockback2DDefaultKillTrees= false
boolean udg_Knockback2DPause= false
boolean udg_Knockback2DDefaultPause= false
boolean udg_Knockback2DBounces= false
boolean udg_Knockback2DDefaultBounce= false
real udg_Knockback2DFriction= 0
real udg_Knockback2DDefaultFriction= 0
integer udg_Knockback2DRobustPathing= 0
real udg_K2DTimeout= 0
integer udg_UDexWasted_Copy= 0
boolean udg_UnitIndexerEnabled_Copy= false
real udg_UnitIndexEvent_Copy= 0
integer array udg_UDexPrev_Copy
unit array udg_UDexUnits_Copy
integer udg_UDexGen_Copy= 0
integer array udg_UDexNext_Copy
integer udg_UDexRecycle_Copy= 0
integer udg_UDex_Copy= 0
string udg_AB_SFX_KB
real udg_AB_KBDistance= 0
real udg_AB_KBTime= 0
real udg_AB_KBAoE= 0
real udg_AB_HeightDifference= 0
real udg_AB_CurrentHeight= 0
real udg_Knockback2DTime= 0
real udg_Knockback2DDistance= 0
real udg_Knockback2DAngle= 0
unit udg_Knockback2DUnit= null
string udg_Knockback2DLoopFX
boolean array udg_AB_CheckPathing
real udg_AB_BounceAoE= 0
damagetype udg_AB_DamageType= null
attacktype udg_AB_AttackType= null
real array udg_AB_Damage
boolean udg_AB_SuccesfulBounce= false
string udg_AB_Order_ID
unit udg_AB_TempUnit= null
real udg_AB_TempReal= 0
real udg_AB_MinCastRange= 0
string udg_AB_SFXTail
string udg_AB_SFXExplode
integer array udg_AB_MaxBounce
boolean udg_CP_PointIsWalkable= false
location udg_CP_Point= null
item array udg_CP_HiddenItems
integer udg_CP_HiddenItemsIndex= 0
item udg_CP_Item= null
rect udg_CP_Rect= null
real udg_AB_Height= 0
real array udg_AB_MaxHeight
real udg_AB_PeriodicTimer= 0
integer udg_AB_MaxLevel= 0
integer udg_AB_TempInt= 0
real array udg_AB_Time
real udg_AB_Arc_Percent= 0
real udg_AB_JD_Percent= 0
real array udg_AB_MoveRate
real array udg_AB_Distance
real udg_AB_JumpDistance= 0
string udg_AB_SFXBounce
real array udg_AB_TravelTime
real udg_AB_Arc= 0
real array udg_AB_Direction
location udg_AB_BombLoc= null
real udg_AB_SpawnDistance= 0
effect array udg_AB_Bomb2_SFX
location udg_AB_TempLoc= null
integer array udg_AB_AbilityLvl
integer array udg_AB_CounterBounce
integer array udg_AB_CounterKills
real array udg_AB_DistanceTraveled
player array udg_AB_Owner
unit array udg_AB_Caster
string udg_AB_Attach_SFXBomb2
string udg_AB_Attach_SFXBomb
real udg_AB_Blue= 0
real udg_AB_Green= 0
real udg_AB_Red= 0
string udg_AB_SFXBomb2
integer udg_AB_Dummy= 0
effect array udg_AB_Bomb_SFX
unit array udg_AB_BombDummy
string udg_AB_SFXBomb
integer udg_AB_Ability= 0
integer udg_AB_LoopInt= 0
integer array udg_AB_NodePrev
integer array udg_AB_NodeNext
integer udg_AB_MaxIndex= 0
integer array udg_AB_RecycledStack
integer udg_AB_Spell_ID= 0
integer udg_AB_RecycledSize= 0
integer udg_AB_SpellCount= 0
unit udg_QS_Target= null
real array udg_QS_Damage
real udg_QS_Angle= 0
location array udg_QS_Point
unit udg_QS_Dummy= null
group udg_QS_Group= null
unit udg_QS_Hero= null
integer array udg_QS_Duration
real array udg_QS_Damage_Per_Lvl
integer udg_QS_CV= 0
timer udg_KOTH_Third_Hill_Timer= null
integer udg_KOTH_Level= 0
unit udg_Shadowstep_Caster= null
unit udg_Shadowstep_Target= null
integer udg_Shadowstep_Ability_Level= 0
location udg_Shadowstep_Location= null
location udg_Shadowstep_Location_2= null
integer udg_Shadowstep_Loop_Number= 0
real udg_Shadowstep_Base_Damage= 0
real udg_Shadowstep_Damage_Multiplier= 0
real udg_Shadowstep_Total_Damage= 0
real udg_Shadowstep_Calculation= 0
location udg_Shadowstep_Loop_Location= null
unit udg_Aqua_Burst_Caster= null
location udg_Aqua_Burst_Location= null
integer udg_Aqua_Burst_Ability_Level= 0
real udg_Aqua_Burst_Area_of_Effect= 0
real udg_Aqua_Burst_Base_Damage= 0
real udg_Aqua_Burst_Total_Damage= 0
group udg_Aqua_Burst_Damage_Group= null
unit udg_Toss_Dummy= null
damagetype array udg_SW_DamageType
attacktype array udg_SW_AttackType
boolean array udg_SW_ExtraEffectCheck
trigger array udg_SW_ExtraEffect
string udg_SW_Attachment
boolean array udg_SW_AffectEnemy
boolean array udg_SW_AffectAlly
trigger array udg_SW_ExtraEffectTarget
effect array udg_SW_Wave
string array udg_SW_WaveEffectEnd
boolean array udg_SW_AffectGround
boolean array udg_SW_OneInstance
boolean array udg_SW_AffectStructure
boolean array udg_SW_AffectAir
boolean array udg_SW_ExtraEffectTargetCheck
location array udg_SW_Point
unit udg_SW_HitUnit= null
group udg_SW_Group= null
real array udg_SW_SpeedX
real array udg_SW_DamageX
boolean array udg_SW_LoopingSfx
real array udg_SW_DistanceX
group array udg_SW_GroupDone
real array udg_SW_AreaGrowth
real array udg_SW_AreaCurrent
real array udg_SW_Distance
location array udg_SW_NextPoint
string array udg_SW_WaveEffectLoop
unit array udg_SW_Dummy
real array udg_SW_Speed
real array udg_SW_AreaFinal
real udg_SW_Angle= 0
string array udg_SW_WaveEffect
real array udg_SW_AreaInitial
real array udg_SW_Damage
integer array udg_SW_Lvl
integer udg_SW_Ability= 0
integer udg_SW_Loop= 0
integer udg_SW_Max= 0
unit array udg_SW_Caster
integer udg_CycloneShield= 0
group udg_Jaina_Group= null
real array udg_Jaina_Height
integer udg_Jaina_CV= 0
unit udg_Jaina_Target= null
real array udg_Jaina_Elapsed_Time
real array udg_Jaina_Rate
real array udg_Jaina_Factor
real array udg_Jaina_Duration
integer udg_Jaina_Target_Count= 0
real array udg_Jaina_Duration_Per_Level
real array udg_Jaina_Height_Per_Level
unit udg_UnitVarCaster4= null
unit udg_UnitVarTarget3= null
location udg_TempLoc13= null
unit array udg_UnitVarLast01
effect array udg_SpecialEffect2
location udg_TempLoc12= null
timer udg_KOTH_Fourth_Hill_Timer= null
integer udg_KOTH_HP= 0
unit udg_QS_Target_Copy= null
real array udg_QS_Damage_Copy
real udg_QS_Angle_Copy= 0
location array udg_QS_Point_Copy
unit udg_QS_Dummy_Copy= null
group udg_QS_Group_Copy= null
unit udg_QS_Hero_Copy= null
integer array udg_QS_Duration_Copy
real array udg_QS_Damage_Per_Lvl_Copy
integer udg_QS_CV_Copy= 0
real array udg_Zeus_Shock_Damage
timer udg_timer_tech_delay_Captains= null
integer udg_RG_ResourceTypeFood= 0
integer udg_RG_ResourceTypeLumber= 0
integer udg_RG_ResourceTypeGold= 0
integer udg_RG_MaxResource= 0
integer udg_RG_Building= 0
integer udg_RG_Income= 0
real udg_RG_DurationInterval= 0
integer udg_RG_ResourceType= 0
trigger array udg_RG_Triggers
string array udg_ResourceColor
real udg_RG_FloatingTextSpeed= 0
real udg_RG_FloatingTextLifeSpan= 0
real udg_RG_FloatingTextFadeTime= 0
real udg_RG_Interval= 0
boolean udg_RG_BooleanResourceBuilding= false
integer udg_RG_Key= 0
hashtable udg_RG_Hashtable= null
unit udg_TempUnit= null
integer udg_TempUnitType= 0
group udg_RG_Group= null
force udg_TempPlayerGroup= null
texttag udg_TempFloatingText= null
boolean array udg_PG_Active
force udg_Active_PlayGroup= null
integer udg_temp_level_team= 0
timer udg_timer_extrainvul= null
timer udg_timer_tech_delay_Captains_2= null
timer udg_timer_tech_delay_Captains_3= null
unit udg_Jungle_Target= null
real array udg_Jungle_Heal
real udg_Jungle_Angle= 0
location array udg_Jungle_Point
real array udg_HCr_Duration
real array udg_HCr_Angle
real array udg_HCr_Distance
real array udg_HCr_Height
unit array udg_HCr_Target
group udg_HCr_Caster_Group= null
group udg_HCr_Nearby_Group= null
unit udg_HCr_Caster= null
location array udg_HCr_Point
integer udg_HCr_CV= 0
integer array udg_HCr_Level
real array udg_HCr_Elapsed_Time
real array udg_HCr_Height_Rate
real array udg_HCr_Height_Factor
integer udg_HCr_Caster_Count= 0
real array udg_HCr_Speed
real array udg_HCr_Setup_Damage
real array udg_HCr_Setup_Heal
real udg_HCr_Setup_Min_Distance= 0
unit udg_KnockUp_Target= null
real udg_KnockUp_Height= 0
real udg_KnockUp_Duration= 0
group udg_KnockUp__Group= null
integer udg_KnockUp__CV= 0
integer udg_KnockUp__Group_Count= 0
real array udg_KnockUp__Height
real array udg_KnockUp__Duration
real array udg_KnockUp__Elapsed_Time
real array udg_KnockUp__Rate
real array udg_KnockUp__Factor
unit udg_Divine_target= null
unit udg_MonkeyKing= null
integer array udg_StaffJungle_level
boolean array udg_StaffJungle_active
location array udg_StaffJungle_start_location
group array udg_StaffJungle_target
location array udg_StaffJungle_location
unit array udg_StaffJungle_mjolnir
real array udg_StaffJungle_degree
group array udg_StaffJungle_target_damage
timer udg_timer_BountyIncrease= null
timer udg_timer_BountyIncrease2= null
integer udg_X_BountryIncrease= 0
real udg_BountyIncreaseMultiplier= 0
unit array udg_dummy_Jungle_1
unit udg_Jungle_dummy_stomp= null
real udg_t_colossal_initial_message= 0
real udg_t_colossal_reoccuring_message= 0
timer udg_timer_colossal_message= null
timer udg_timer_colossal_message_initial= null
unit udg_KOTH_Aura_dummy= null
timer udg_timer_OD_items= null
timer udg_timer_OD_pooling_ON= null
integer udg_exp_sys_high_Copy= 0
integer udg_exp_sys_level_Copy= 0
integer udg_exp_sys_low_Copy= 0
unit udg_ExpDeadUnit_Copy= null
group udg_ExpGroup_Copy= null
integer array udg_ExpInt_Copy
unit udg_ExpKillingUnit_Copy= null
player udg_ExpPlayer_Copy= null
location udg_ExpPoint_Copy= null
real array udg_Exp_Rate_Copy
integer udg_Exp_PN_Copy= 0
boolean array udg_Exp_Level_Was_Reached_Copy
integer udg_Exp_Level_Copy= 0
unit array udg_deathward_clap
effect udg_KOTH_Invul= null
timer udg_timer_level4_Summoner= null
timerdialog udg_timer_window_ODpooling= null
timer udg_timer_OD_pooling_OFF= null
timerdialog udg_timer_window_ODpooling_OFF= null
timer udg_timer_OD_pooling_ON_2= null
timer udg_timer_KOTH_Invul= null
integer udg_OD_Goldrate= 0
timer udg_timer_OD_Gold= null
timer udg_timer_OD_Gold_2= null
timer udg_timer_OD_Gold_3= null
integer udg_a= 0
integer array udg_SpellBookAbility
integer udg_max_SpellBookAbility= 0
integer udg_b= 0
integer array udg_RealAbility
integer udg_max_RealAbility= 0
integer udg_c= 0
integer array udg_ItemAbility
integer udg_max_ItemAbility= 0
integer array udg_Wrath_Counter
trigger udg_WRT_Trigger= null
location array udg_Monsoon_point
location udg_Monsoon_Target= null
player udg_col_killing_player= null
unit udg_ExpDeadUnit_Foot= null
unit udg_ExpKillingUnit_Foot= null
player udg_ExpPlayer_Foot= null
integer udg_exp_sys_high_Foot= 0
integer udg_exp_sys_level_Foot= 0
integer udg_exp_sys_low_Foot= 0
group udg_ExpGroup_Foot= null
integer array udg_ExpInt_Foot
location udg_ExpPoint_Foot= null
real udg_Rate= 0
player udg_Income_Player= null
timer udg_GoldCoin_Income_Timer= null
unit udg_GoldCoinHolderUnit= null
player udg_Mute_Player= null
integer udg_Mute_Player_Number= 0
string array udg_Mute_Player_Original_Name
boolean array udg_Mute_Is_Player_Muted
boolean udg_New_Kick_Is_Active= false
button array udg_New_Kick_Dialog_Buttons
integer udg_New_Kick_Current_Page= 0
button udg_New_Kick_Dialog_Next_Button= null
button udg_New_Kick_Dialog_Prev_Button= null
button udg_New_Kick_Dialog_Cancel_Button= null
dialog udg_New_Kick_Dialog= null
integer array udg_New_Kick_Int
player udg_New_Kick_Decider= null
integer udg_New_Kick_Total_Pages= 0
boolean udg_Host_Picked_A_Game_Mode= false
timer udg_Host_AFK_Timer= null
integer FFModeStage=0
boolean FFMode4K=false
boolean FFModePrivateVote=false
timer FFModeMenuTimer=null
integer udg_voting_mode= 0
timer udg_timer_tech_delay_Captains_4= null
timer udg_timer_foots_increase= null
real udg_footy_bounty_increase= 0
boolean udg_Footy_bounty_increasing= false
integer udg_KOTH_Killing_Bounty= 0
integer udg_KOTH_Gold_Bounty= 0
timer udg_timer_OD_items_restock= null
location udg_temp_point_overdrivefarm= null
boolean udg_TurtleLevel= false
boolean udg_TurtleLeveler= false
integer array udg_leadhero1
integer array udg_leadhero2
hashtable udg_RE_Knocktable= null
hashtable udg_KnockbackTable= null
unit udg_Beast_Attack_Caster= null
unit udg_Beast_Attack_Target= null
integer udg_Beast_Attack_Ability_Level= 0
location udg_Beast_Attack_Location= null
location udg_Beast_Attack_Location2= null
real udg_Beast_Attack_Max_Life= 0
integer udg_Beast_Attack_Damage_Splitter= 0
integer udg_Beast_Attack_Atribute= 0
real udg_Beast_Attack_Life_Damage= 0
real udg_Beast_Attack_Atribute_Damage= 0
real udg_Beast_Attack_Total_Damage= 0
real udg_KnockbackAngle= 0
real udg_KnockbackSpeed= 0
real udg_KnockbackDistance= 0
group udg_KnockbackUnits= null
unit udg_Knockback_Target= null
location udg_Knockback_Loc1= null
location udg_Knockback_Loc2= null
unit udg_Impale_Caster= null
integer udg_Impale_Level= 0
player udg_Impale_Owner= null
location udg_Impale_Target_Loc= null
location udg_Impale_Caster_Loc= null
integer udg_Impale_Dummy_AbilityI= 0
integer udg_Impale_Dummy_AbilityII= 0
real udg_Impale_Facing_Angle= 0
real udg_Impale_Dummy_Face= 0
real udg_Impale_Angle= 0
location udg_Impale_LocI= null
location udg_Impale_LocII= null
location udg_Impale_LocIII= null
unit udg_Fire_Wall_Caster= null
player udg_Fire_Wall_Owner= null
integer udg_Fire_Wall_Ability_Level= 0
location udg_Fire_Wall_Location= null
real udg_Fire_Wall_Duration= 0
real udg_Fire_Wall_Distance= 0
integer udg_Fire_Wall_Dummy_Ability= 0
location udg_Fire_Wall_Loop_Location= null
location udg_Fire_Wall_Loop_Location_2= null
integer udg_Beast_Attack_Ability_Multi= 0
unit udg_Caster= null
unit udg_Target= null
location udg_TempLoc= null
location udg_TempLoc2= null
group udg_TempGroup= null
real udg_TempReal= 0
integer udg_TempInt2= 0
integer udg_FAIndex= 0
integer udg_FALastRecycled= 0
integer array udg_FARecycledList
integer udg_FAMax= 0
boolean array udg_FAHas
unit array udg_FACaster
integer udg_FACount= 0
location array udg_FATargetPoint
real array udg_FATimer
real array udg_FADelay
integer udg_FAInteger= 0
integer udg_TempInt= 0
hashtable udg_SpellHash= null
integer array udg_MantleItem
integer udg_TeNe_A_Index= 0
integer udg_TeNe_A_Cast_LOOP= 0
group udg_TeNe_A_Temp_Group= null
player udg_guard= null
timer array udg_timer_purificationNova
unit udg_ExpDeadUnit_T2= null
group udg_ExpGroup_T2= null
integer array udg_ExpInt_T2
unit udg_ExpKillingUnit_T2= null
player udg_ExpPlayer_T2= null
location udg_ExpPoint_T2= null
integer udg_Exp_Level_T2= 0
boolean array udg_Exp_Level_Was_Reached_T2
integer udg_exp_sys_high_T2= 0
integer udg_exp_sys_level_T2= 0
integer udg_exp_sys_low_T2= 0
boolean udg_mode_tech= false
integer udg_UpgradeAmount= 0
timer udg_spawnTimer_aftermass= null
timer udg_timer_upgradedelay= null
timer udg_timer_tech_mode= null
timer udg_timer_upgradespub= null
location array udg_ship_destination_Copy
unit array udg_dummy_nova
real udg_forked_fury_cd= 0
integer array udg_death_ward_bounty
unit udg_u= null
location udg_TempLoc_NullRod= null
boolean udg_Racial_Mastery_Upgrade= false
integer udg_SeaGiantRemove= 0
integer udg_Timer_Minutes= 0
integer udg_Timer_Seconds= 0
string udg_Temp_Time_String

    // Generated
trigger gg_trg_Disable_Taverns_After_300s= null
trigger gg_trg_New_Shield_Spell= null
trigger gg_trg_Mute_Setup= null
trigger gg_trg_Mute_Player_Command= null
trigger gg_trg_Unit_Indexer= null
trigger gg_trg_MissileColor= null
trigger gg_trg_MissileCreate= null
trigger gg_trg_MissileBounce= null
trigger gg_trg_MissileDeflectTarget= null
trigger gg_trg_MissileDeflect= null
trigger gg_trg_MissileFlush= null
trigger gg_trg_MissileFlushAll= null
trigger gg_trg_MissileHitted= null
trigger gg_trg_MissilePause= null
trigger gg_trg_MissileResume= null
trigger gg_trg_MissileAttach= null
trigger gg_trg_MissileDetach= null
trigger gg_trg_PickedMissile= null
trigger gg_trg_MissilesInRange= null
trigger gg_trg_MissilesInRangeCounted= null
trigger gg_trg_MissilesInRangeOfLoc= null
trigger gg_trg_MissilesInRangeOfLocCounted= null
trigger gg_trg_MissilesInRect= null
trigger gg_trg_MissilesInRectCounted= null
trigger gg_trg_MissilesOfPlayer= null
trigger gg_trg_MissilesOfPlayerCounted= null
trigger gg_trg_MissilesOfType= null
trigger gg_trg_MissilesOfTypeCounted= null
trigger gg_trg_MissileGroupClear= null
trigger gg_trg_MissileGroupAdd= null
trigger gg_trg_MissileGroupRemove= null
trigger gg_trg_MissileGroupAddGroup= null
trigger gg_trg_MissileGroupRemoveGroup= null
trigger gg_trg_DestroyMissileGroup= null
trigger gg_trg_TimerUtils= null
trigger gg_trg_WorldBounds= null
trigger gg_trg_Alloc= null
trigger gg_trg_MissileEffect= null
trigger gg_trg_MissileUtils= null
trigger gg_trg_Missiles= null
trigger gg_trg_GST_Tutorial= null
trigger gg_trg_GST_Example_0= null
trigger gg_trg_GST_Example_0_Expire= null
trigger gg_trg_GST_Example_1= null
trigger gg_trg_GST_Example_1_Expire= null
trigger gg_trg_GST_Example_2= null
trigger gg_trg_GST_Example_2_Expire= null
trigger gg_trg_GST_Example_3= null
trigger gg_trg_GST_Example_3_Expire= null
trigger gg_trg_GST_Example_4= null
trigger gg_trg_GST_Example_4_Expire= null
trigger gg_trg_GST_Example_5= null
trigger gg_trg_GST_Example_5_Expire= null
trigger gg_trg_DDE_Destroy_Effect= null
trigger gg_trg_DDE_Destroy_Last_Created_Effect= null
trigger gg_trg_DDE_Expire= null
trigger gg_trg_DDE_Expire_Hide= null
trigger gg_trg_CPP_Create_Pathing_Checker= null
trigger gg_trg_KnockUp_Apply= null
trigger gg_trg_KnockUp_Loop= null
trigger gg_trg_W3MMD_Library= null
trigger gg_trg_init= null
trigger gg_trg_Remove_Obs_PauseSave= null
trigger gg_trg_init_JASS= null
trigger gg_trg_VERSION_CHECK= null
trigger gg_trg_newzoom= null
trigger gg_trg_fake_shops_insert= null
trigger gg_trg_minimap_correction= null
trigger gg_trg_set_hero_numbers= null
trigger gg_trg_set_hero_stats= null
trigger gg_trg_admin_level= null
trigger gg_trg_playernameandtag= null
trigger gg_trg_Quests_MAP_INFO= null
trigger gg_trg_Observer_Vision_Fix= null
trigger gg_trg_Camera_Zoom= null
trigger gg_trg_AFK_Host_Setup= null
trigger gg_trg_AFK_Host_Timer_Expires= null
trigger gg_trg_MODE_GUI_show= null
trigger gg_trg_MODE_GUI_execute= null
trigger gg_trg_MODE_set_pub_game_default= null
trigger gg_trg_MODE_set_pub_game_custom= null
trigger gg_trg_MODE_set_pro_mode= null
trigger gg_trg_MODE_set_inhouse= null
trigger gg_trg_MODE_colossal_GUI_execute= null
trigger gg_trg_MODE_colossal_amount_GUI_execute= null
trigger gg_trg_Default_KOTH_ON= null
trigger gg_trg_MODE_new= null
trigger gg_trg_MODE_set_standard_units= null
trigger gg_trg_MODE_set_bounties= null
trigger gg_trg_MODE_1v1_check= null
trigger gg_trg_MODE_1v1= null
trigger gg_trg_MODE_King_Of_The_Hill= null
trigger gg_trg_MODE_777= null
trigger gg_trg_Start_Vote= null
trigger gg_trg_Vote_SD_button= null
trigger gg_trg_Vote_AP_button= null
trigger gg_trg_Vote_AR_button= null
trigger gg_trg_Vote_Timer_Expires= null
trigger gg_trg_KOTH_Setup= null
trigger gg_trg_KOTH_Income= null
trigger gg_trg_KOTH_Hill_Dies= null
trigger gg_trg_KOTH_Gold_Depleted= null
trigger gg_trg_KOTH_Set_Neutral_Hill= null
trigger gg_trg_KOTH_Reset_Hill= null
trigger gg_trg_KOTH_Create_Hill_Glow= null
trigger gg_trg_KOTH_Update_Text= null
trigger gg_trg_KOTH_Update_Board_Gold= null
trigger gg_trg_KOTH_Second_Hill= null
trigger gg_trg_KOTH_Third_Hill= null
trigger gg_trg_KOTH_Fourth_Hill= null
trigger gg_trg_KOTH_Invul_Hill= null
trigger gg_trg_Pub_Defender_Setup= null
trigger gg_trg_Add_Creeps_To_Pub_Mode= null
trigger gg_trg_Disable_Fort_Aura= null
trigger gg_trg_Start_game= null
trigger gg_trg_Start_SD= null
trigger gg_trg_Start_AP= null
trigger gg_trg_Start_AR= null
trigger gg_trg_TP_hero= null
trigger gg_trg_FF_AutoPick_2m= null
trigger gg_trg_Hero_Skills= null
trigger gg_trg_Multiboard_Create= null
trigger gg_trg_Multiboard_Create_with_KOTH= null
trigger gg_trg_Multiboard_Show= null
trigger gg_trg_Multiboard_Update= null
trigger gg_trg_Update_Game_Time= null
trigger gg_trg_Footy_Bounty_Increase_Delay= null
trigger gg_trg_Unit_Experience_System= null
trigger gg_trg_Foot_Exp_system= null
trigger gg_trg_exp_system= null
trigger gg_trg_set_hero_bounty= null
trigger gg_trg_set_hero_bounty_update= null
trigger gg_trg_Set_Exp_Bonus_Rate_Variables= null
trigger gg_trg_Set_Exp_Bonus_Rate_Upon_Leveling= null
trigger gg_trg_MASS_timer= null
trigger gg_trg_keep_footy_in_base= null
trigger gg_trg_MASS_PRE_START_BONUS= null
trigger gg_trg_Mass_START= null
trigger gg_trg_Mass_END= null
trigger gg_trg_Remove_Invul_from_buildings= null
trigger gg_trg_GM_Command= null
trigger gg_trg_GM_execute= null
trigger gg_trg_GM_set_messages= null
trigger gg_trg_GM_info= null
trigger gg_trg_Phoken= null
trigger gg_trg_GM_send_messages= null
trigger gg_trg_block_from_shop_t1= null
trigger gg_trg_block_from_shop_t2= null
trigger gg_trg_block_from_shop_t3= null
trigger gg_trg_block_from_shop_t4= null
trigger gg_trg_kill_blink_shop_t1= null
trigger gg_trg_kill_blink_shop_t2= null
trigger gg_trg_kill_blink_shop_t3= null
trigger gg_trg_kill_blink_shop_t4= null
trigger gg_trg_MH_shop_redirect= null
trigger gg_trg_MH_shop_click= null
trigger gg_trg_MH_hide_fake_shop_rat= null
trigger gg_trg_MH_unhide_fake_shop_rat= null
trigger gg_trg_MH_truesight_add_units= null
trigger gg_trg_MH_truesight_remove_units= null
trigger gg_trg_MH_hide_fake_shop_truesight= null
trigger gg_trg_MH_uhide_fake_shop_truesight= null
trigger gg_trg_turn_off_mh= null
trigger gg_trg_turn_on_mh= null
trigger gg_trg_game_time= null
trigger gg_trg_page_system= null
trigger gg_trg_stop_TK= null
trigger gg_trg_restore_visibility_to_tavern= null
trigger gg_trg_move_unit_hero_showroom= null
trigger gg_trg_start_timers= null
trigger gg_trg_remove_timer_repick= null
trigger gg_trg_Tech_Delay_T1= null
trigger gg_trg_Tech_Delay_T2= null
trigger gg_trg_Tech_Delay_T3= null
trigger gg_trg_Overdrive= null
trigger gg_trg_Taunt_Turtle_Upgrade= null
trigger gg_trg_Turtle_Level_2_purchase= null
trigger gg_trg_turn_trading_ON= null
trigger gg_trg_Bounty_Timer_1= null
trigger gg_trg_autorevive= null
trigger gg_trg_change_Revive_time_based_on_level= null
trigger gg_trg_give_revived_hero_25_mana= null
trigger gg_trg_colossal_variables= null
trigger gg_trg_colossal_spawn_message= null
trigger gg_trg_colossal_stats= null
trigger gg_trg_colossal_spawn= null
trigger gg_trg_colossal_death= null
trigger gg_trg_colossal_command_ct= null
trigger gg_trg_colossal_command_next= null
trigger gg_trg_limit_amount_of_creeps= null
trigger gg_trg_phoenix_block= null
trigger gg_trg_Turtle_bounty= null
trigger gg_trg_Destroy_Triggers_1= null
trigger gg_trg_Destroy_Triggers_2= null
trigger gg_trg_Votekick_Initiate= null
trigger gg_trg_Votekick_Select_Ally_To_Kick= null
trigger gg_trg_Votekick_Show_Yes_and_No= null
trigger gg_trg_Votekick_Vote_Yes_or_No= null
trigger gg_trg_Votekick_Runs_Out_Of_Time= null
trigger gg_trg_Votekick_RESET= null
trigger gg_trg_suicide= null
trigger gg_trg_suicide_pressed= null
trigger gg_trg_suicide_after_10_seconds= null
trigger gg_trg_show_commands= null
trigger gg_trg_repick_command= null
trigger gg_trg_swap_command= null
trigger gg_trg_swap_execute= null
trigger gg_trg_autopool_command= null
trigger gg_trg_autopool_execute= null
trigger gg_trg_autopool_time= null
trigger gg_trg_autopool_th_execute= null
trigger gg_trg_show_players= null
trigger gg_trg_game_time_command= null
trigger gg_trg_KD= null
trigger gg_trg_Clear_Text_Setup= null
trigger gg_trg_draw= null
trigger gg_trg_draw_pressed= null
trigger gg_trg_KICK_command= null
trigger gg_trg_KICK_rebuild_dialog= null
trigger gg_trg_KICK_execute= null
trigger gg_trg_set_unit_info= null
trigger gg_trg_set_unit_scale= null
trigger gg_trg_set_unit_level= null
trigger gg_trg_skip_colo_wave= null
trigger gg_trg_debugmode= null
trigger gg_trg_debug= null
trigger gg_trg_spawn_killa= null
trigger gg_trg_debug_control= null
trigger gg_trg_debug_show_ability_name= null
trigger gg_trg_debug_show_order_ids= null
trigger gg_trg_summon_hero_for_player= null
trigger gg_trg_reveal= null
trigger gg_trg_fog= null
trigger gg_trg_status= null
trigger gg_trg_bounty= null
trigger gg_trg_test_message= null
trigger gg_trg_coords= null
trigger gg_trg_bounds= null
trigger gg_trg_setting_video_cam= null
trigger gg_trg_remove_showroom_heros= null
trigger gg_trg_Tentacle_Mass_Root= null
trigger gg_trg_Initialization= null
trigger gg_trg_Beast_Attack= null
trigger gg_trg_KnockbackUnits= null
trigger gg_trg_Parasite= null
trigger gg_trg_Fire_Wall_notused= null
trigger gg_trg_HERO_Throw_Glaive= null
trigger gg_trg_HERO_Throw_Glaive_Loop= null
trigger gg_trg_Zeus_Setup= null
trigger gg_trg_HERO_Shock_Zeus= null
trigger gg_trg_HERO_Zeus_Shock_Damage= null
trigger gg_trg_HERO_Queen_Spiderling_Swarm= null
trigger gg_trg_HERO_Queen_Web= null
trigger gg_trg_HERO_Witch_Doctor_Wards= null
trigger gg_trg_HERO_Shattering_Strike_Trigger= null
trigger gg_trg_HERO_Shattering_Strike_Effect= null
trigger gg_trg_HERO_Shattering_Strike_Action= null
trigger gg_trg_Cripple_Wave= null
trigger gg_trg_Cripple_Wave_OnHit= null
trigger gg_trg_HERO_Monkey_Staff_of_the_Jungle_Throw= null
trigger gg_trg_HERO_Monkey_Staff_of_the_Jungle_Loop= null
trigger gg_trg_Holy_Crash_Setup= null
trigger gg_trg_Holy_Crash_Cast= null
trigger gg_trg_Holy_Crash_Loop= null
trigger gg_trg_Pounce_Cast= null
trigger gg_trg_Pounce_Loop= null
trigger gg_trg_Staff_of_the_River= null
trigger gg_trg_Staff_of_the_River_OnHit= null
trigger gg_trg_Akama_Shadow_Clone_Cast= null
trigger gg_trg_Akama_Shadow_Clone_Loop= null
trigger gg_trg_Akama_Shadow_Clone_Mimic_Start= null
trigger gg_trg_Akama_Shadow_Clone_Mimic_Stop= null
trigger gg_trg_Akama_Shadow_Clone_Akama_Dies= null
trigger gg_trg_Akama_Shadow_Clone_Destroy_Clone= null
trigger gg_trg_Akama_Learn_Blink= null
trigger gg_trg_Akama_Blink_Start= null
trigger gg_trg_Akama_Blink_Return= null
trigger gg_trg_Avalanche_Toss_Setup= null
trigger gg_trg_Avalanche_Toss_Begin_Cast= null
trigger gg_trg_Avalanche_Toss_Start_Cast= null
trigger gg_trg_Avalanche_Toss_Loop= null
trigger gg_trg_Avalanche_Trample_Cast= null
trigger gg_trg_Avalanche_Trample_Loop= null
trigger gg_trg_Avalanche_Craggy_Exterior_Learn= null
trigger gg_trg_Avalanche_Craggy_Exterior_Stun= null
trigger gg_trg_Avalanche_Seismic_Fury_Learn= null
trigger gg_trg_Avalanche_Seismic_Fury_Enable= null
trigger gg_trg_Avalanche_Seismic_Fury_Begin_Cast= null
trigger gg_trg_Avalanche_Seismic_Fury_Start_Cast= null
trigger gg_trg_Avalanche_Seismic_Fury_Stop_Cast= null
trigger gg_trg_Avalanche_Seismic_Fury_Loop= null
trigger gg_trg_Avalanche_Seismic_Fury_Floating_Text= null
trigger gg_trg_Helios_Collision_Configuration= null
trigger gg_trg_Helios_Collision_Activation= null
trigger gg_trg_Helios_Collision_Loop= null
trigger gg_trg_Helios_Collision_Dummy_Removal= null
trigger gg_trg_Guardian_Force_Field_Learn= null
trigger gg_trg_Guardian_Force_Field_Detonate= null
trigger gg_trg_Guardian_Force_Field_Cast= null
trigger gg_trg_Guardian_Force_Field_Loop= null
trigger gg_trg_Guardian_Force_Field_Damage= null
trigger gg_trg_Guardian_Energy_Chamber_Ally_Cast= null
trigger gg_trg_Guardian_Energy_Chamber_Tome_Of_Retraining= null
trigger gg_trg_Guardian_Energy_Chamber_Learn= null
trigger gg_trg_Searing_Bullet= null
trigger gg_trg_Searing_Bullet_OnHit= null
trigger gg_trg_SovietSniper_Reposition_Cast= null
trigger gg_trg_SovietSniper_Reposition_Loop= null
trigger gg_trg_SovietSniper_Decoy_Bomb_Cast= null
trigger gg_trg_SovietSniper_Decoy_Bomb_Create_Bomb= null
trigger gg_trg_SovietSniper_Decoy_Bomb_Loop= null
trigger gg_trg_SovietSniper_Golovu_Shot_Begin_Cast= null
trigger gg_trg_SovietSniper_Golovu_Shot_Start_Cast= null
trigger gg_trg_SovietSniper_Golovu_Shot_Stop_Cast= null
trigger gg_trg_SovietSniper_Golovu_Shot_Loop= null
trigger gg_trg_TheNook_Hellseek_Cast= null
trigger gg_trg_TheNook_Hellseek_Loop= null
trigger gg_trg_TheNook_Reap_Cast= null
trigger gg_trg_Thunder_Axe= null
trigger gg_trg_Axe_OnHit= null
trigger gg_trg_Hammer_Cast= null
trigger gg_trg_Hammer_OnHit= null
trigger gg_trg_Hammer_Ulti_Cast= null
trigger gg_trg_Hammer_Ulti_Loop= null
trigger gg_trg_Dash_Wooj= null
trigger gg_trg_Summon_Dragons= null
trigger gg_trg_Avatar_Hydralisk= null
trigger gg_trg_Avatar_Yeti= null
trigger gg_trg_Avatar_Loop= null
trigger gg_trg_Avatar_Hydralisk_Loop= null
trigger gg_trg_Charge_Pos_2_and_Pos_3= null
trigger gg_trg_Rune_of_AMS= null
trigger gg_trg_Reptile_Acid_Armor_Cast= null
trigger gg_trg_Reptile_Acid_Armor_Loop= null
trigger gg_trg_Mirror_Image_Cast= null
trigger gg_trg_Mirror_Image_Create_Illusions= null
trigger gg_trg_Mirror_Image_Finish= null
trigger gg_trg_HERO_Dark_Ranger_Mass_Charm= null
trigger gg_trg_HERO_Sylvanus_Dark_Binding= null
trigger gg_trg_Medivh_Gust_Cast= null
trigger gg_trg_Medivh_Gust_Stun= null
trigger gg_trg_Medivh_Gust_Loop= null
trigger gg_trg_Shockwave_Cast= null
trigger gg_trg_Shockwave_Loop= null
trigger gg_trg_HERO_Swift_Strike= null
trigger gg_trg_HERO_Mass_Roots= null
trigger gg_trg_HERO_Metamorphosis_CD= null
trigger gg_trg_HERO_Alchemist_Chemical_Rage_Bounty= null
trigger gg_trg_HERO_Archangel_Smite= null
trigger gg_trg_HERO_Architect_Recruit= null
trigger gg_trg_HERO_Architect_tower_build= null
trigger gg_trg_HERO_Architect_tower_build_v2= null
trigger gg_trg_HERO_Architect_tower_countdown= null
trigger gg_trg_HERO_Architect_raise_morale= null
trigger gg_trg_HERO_Architect_tower_heal= null
trigger gg_trg_UNIT_Clockwerk_Goblin_Kaboom= null
trigger gg_trg_HERO_Bill_Ulti= null
trigger gg_trg_HERO_Blooddancer_Ancient_Ritual= null
trigger gg_trg_HERO_Blooddancer_Rejuvination= null
trigger gg_trg_HERO_Blooddancer_Bloodrush_ON= null
trigger gg_trg_HERO_Blooddancer_Bloodrush_periodic= null
trigger gg_trg_HERO_Blooddancer_Illusions_summon= null
trigger gg_trg_HERO_Blooddancer_Illusions_sacrifice= null
trigger gg_trg_HERO_Blooddancer_Illusions_die= null
trigger gg_trg_HERO_Blooddancer_Illusions_Warhymn= null
trigger gg_trg_HERO_BM_Illusion_Bounty_adjust= null
trigger gg_trg_HERO_Blademaster_Illusions= null
trigger gg_trg_HERO_Corruptor_Corruption_Mass_Curse= null
trigger gg_trg_HERO_Corruptor_Defile_Trigger= null
trigger gg_trg_HERO_Corruptor_Defile_Action= null
trigger gg_trg_HERO_Corruptor_Corrupted_Attack= null
trigger gg_trg_HERO_Dark_Necro_Summons= null
trigger gg_trg_HERO_Dark_Necro_Corrupted_Attack= null
trigger gg_trg_HERO_Death_Wards= null
trigger gg_trg_HERO_Dragon_Tamer_Deathwing_summon= null
trigger gg_trg_HERO_Dragon_Tamer_Deathwing_convert= null
trigger gg_trg_HERO_Summon_Brewer_Stats= null
trigger gg_trg_HERO_Absinthe= null
trigger gg_trg_HERO_Chaos_Bark= null
trigger gg_trg_HERO_Elemental_Hellfire= null
trigger gg_trg_HERO_Exophate_sleep= null
trigger gg_trg_HERO_Exophate_summon= null
trigger gg_trg_HERO_Footgirl_Interchange= null
trigger gg_trg_HERO_Grim_Ulti= null
trigger gg_trg_HERO_Guardian_Purification_Nova= null
trigger gg_trg_HERO_Guardian_Purification_Nova_Explode= null
trigger gg_trg_HERO_HdH_Ulti= null
trigger gg_trg_HERO_Jaina_Ulti= null
trigger gg_trg_HERO_Not_Guilty= null
trigger gg_trg_Objection= null
trigger gg_trg_HERO_Mad_Wizard_MassHex= null
trigger gg_trg_HERO_Mad_Wizard_Bomb_learn= null
trigger gg_trg_HERO_Mad_Wizard_Bomb_plant= null
trigger gg_trg_HERO_Mad_Wizard_Bomb_show= null
trigger gg_trg_HERO_Mad_Wizard_Bomb_detonate= null
trigger gg_trg_HERO_Mad_Wizard_Bomb_remove_bomb= null
trigger gg_trg_HERO_Mans_best_friend_Chaos_Bark= null
trigger gg_trg_HERO_Myrmidon_Sinkhole_start= null
trigger gg_trg_HERO_Myrmidon_Sinkhole_suck= null
trigger gg_trg_HERO_Myrmidon_Sinkhole_end= null
trigger gg_trg_HERO_Pandero_Preserve= null
trigger gg_trg_HERO_Pirate_Send_Ship= null
trigger gg_trg_HERO_Pirate_Explode_Ship= null
trigger gg_trg_HERO_POTM_Owls= null
trigger gg_trg_HERO_Reptile_Acid_Cloud= null
trigger gg_trg_HERO_Reptile_Acid_Cloud_New= null
trigger gg_trg_HERO_Reptile_Decapitate= null
trigger gg_trg_HERO_Santa_Snowball= null
trigger gg_trg_HERO_Ships_Doc_wards= null
trigger gg_trg_HERO_Tactician_Reinforcements= null
trigger gg_trg_HERO_Thor_Mjolnir_Throw= null
trigger gg_trg_HERO_Thor_Mjolnir_Loop= null
trigger gg_trg_HERO_Thor_Powerhit= null
trigger gg_trg_HERO_Prison= null
trigger gg_trg_HERO_Prison_Wall_countdown= null
trigger gg_trg_HERO_Hook_Throw= null
trigger gg_trg_HERO_Hook_Loop= null
trigger gg_trg_HERO_break_loop_if_tp= null
trigger gg_trg_HOOK_Merchant= null
trigger gg_trg_HERO_Warlock_Vengaence= null
trigger gg_trg_Warlock_Vengeance_Expire= null
trigger gg_trg_HERO_Wheelchair_Warlock_Duplicate= null
trigger gg_trg_HERO_Shock_Wooj= null
trigger gg_trg_Shock_Wooj_Damage= null
trigger gg_trg_HERO_Yeti_Hibernate= null
trigger gg_trg_Turn_on_Triggers_when_items_sold= null
trigger gg_trg_ITEM_limits= null
trigger gg_trg_ITEM_combo_limits= null
trigger gg_trg_ITEM_packhorse_pickup= null
trigger gg_trg_ITEM_packhorse_buy= null
trigger gg_trg_ITEM_tomes_on_lv18= null
trigger gg_trg_ITEM_Null_Rod= null
trigger gg_trg_ITEM_Thunderfury_Staff= null
trigger gg_trg_ITEM_Thunderfury_Shock_Damage= null
trigger gg_trg_ITEM_Scroll_of_Beast_start= null
trigger gg_trg_ITEM_Scroll_of_Invisibility= null
trigger gg_trg_ITEM_Scroll_of_Frenzy= null
trigger gg_trg_ITEM_Purge_the_Dead= null
trigger gg_trg_ITEM_Scroll_of_AntiMagic= null
trigger gg_trg_ITEM_Scroll_of_Inner_Fire= null
trigger gg_trg_ITEM_Rune_of_Inner_Fire= null
trigger gg_trg_ITEM_Scroll_of_Illusion= null
trigger gg_trg_ITEM_God_Wards= null
trigger gg_trg_ITEM_God_Wards_Copy= null
trigger gg_trg_ITEM_Interchange= null
trigger gg_trg_ITEM_Interchange_pickup= null
trigger gg_trg_ITEM_Forked_Fury_NEW= null
trigger gg_trg_ITEM_Orb_of_Frost= null
trigger gg_trg_ITEM_Wall_Convert_Press= null
trigger gg_trg_ITEM_Wall_Convert_execute= null
trigger gg_trg_ITEM_Wall= null
trigger gg_trg_ITEM_Wall_countdown= null
trigger gg_trg_ITEM_Wall_taunt= null
trigger gg_trg_ITEM_Illusion= null
trigger gg_trg_ITEM_Scepter= null
trigger gg_trg_UNIT_Crypt_Fiend_Unburrow= null
trigger gg_trg_Interchange_Visual_Pre_Cast= null
trigger gg_trg_UNIT_Interchange_Allies= null
trigger gg_trg_UNIT_Tower_of_Terror_Nuke= null
trigger gg_trg_UNIT_Moonwell_heal= null
trigger gg_trg_BASE_FullSend= null
trigger gg_trg_BASE__Overdrive_Start= null
trigger gg_trg_BASE__Overdrive_END= null
trigger gg_trg_BASE_production_ONOFF= null
trigger gg_trg_BASE_AutoSend_ONOFF= null
trigger gg_trg_BASE_collect_gold= null
trigger gg_trg_BASE_destroy= null
trigger gg_trg_SHOP_Redirect= null
trigger gg_trg_Base_to_Dummy= null
trigger gg_trg_Dummy_to_Base= null
trigger gg_trg_Upgrades_level= null
trigger gg_trg_Upgrade_after= null
trigger gg_trg_Update_base_variable= null
trigger gg_trg_Shared_Upgrades_Tech_Mode= null
trigger gg_trg_Racial_Mastery_upgrade= null
trigger gg_trg_Tower_downgrade_click= null
trigger gg_trg_Tower_downgrade_execute= null
trigger gg_trg_Multishot_Tower_doubleup= null
trigger gg_trg_Tower_of_Terror_Limit_1= null
trigger gg_trg_Arcane_Tower_limit_2= null
trigger gg_trg_Tree_Tower_Limit_2= null
trigger gg_trg_miRaculix_Amulett= null
trigger gg_trg_Druids_Amulet= null
trigger gg_trg_Amulet_of_Clarity= null
trigger gg_trg_Amulet_of_Vigor= null
trigger gg_trg_Guardian_Shield= null
trigger gg_trg_Fist_of_the_Titans= null
trigger gg_trg_Natures_Blessing= null
trigger gg_trg_Overdrive_Windwalk= null
trigger gg_trg_Ice_Claws= null
trigger gg_trg_Holy_Maiden= null
trigger gg_trg_LightSpeed_Shoes= null
trigger gg_trg_Night_Terror= null
trigger gg_trg_Ninja_Cloak= null
trigger gg_trg_Ring_of_Superiority= null
trigger gg_trg_Scepter_of_the_Archmage= null
trigger gg_trg_Staff_of_Sanctuary= null
trigger gg_trg_Demogorgons_Scepter= null
trigger gg_trg_Chaos_Cloak= null
trigger gg_trg_Amulet_of_the_Wind= null
trigger gg_trg_Forked_Fury= null
trigger gg_trg_Spawn_Unit_Is_Recycled= null
trigger gg_trg_set_spawn_variables= null
trigger gg_trg_set_spawn_rates= null
trigger gg_trg_set_base= null
trigger gg_trg_eight_start_timer= null
trigger gg_trg_eight= null
trigger gg_trg_eight_mass_bonus= null
trigger gg_trg_Footmen_Level_2= null
trigger gg_trg_five= null
trigger gg_trg_ten= null
trigger gg_trg_eight_new= null
trigger gg_trg_ten_new= null
trigger gg_trg_twelve_new= null
trigger gg_trg_No_double_tech= null
trigger gg_trg_check_if_team_active= null
trigger gg_trg_Kill_units_of_inactive_player= null
trigger gg_trg_player_leaves= null
trigger gg_trg_player_destroyed= null
trigger gg_trg_Visibility= null
trigger gg_trg_END= null
constant string zoom__gFileName= "FFR_Zoom.txt"
integer zoom__gMinDistance= 1400
integer zoom__gMaxDistance= 6000
constant real zoom__gFogZStart= 3000.00
constant real zoom__gFogZEnd= 5000.00
framehandle zoom__slider= null
framehandle zoom__sliderLabel= null
framehandle zoom__lockButton= null
framehandle zoom__lockLabel= null
boolean array zoom__sliderLocked

trigger l__library_init

//JASSHelper struct globals
//:
constant integer si__File=1
constant integer s__File_AbilityCount= 10
constant integer s__File_PreloadLimit= 200
integer s__File_Counter= 0
integer array s__File_List
integer array s__File_AbilityList
boolean s__File_ReadEnabled
string array s__File_filename
string array s__File_buffer
constant integer si__MMD__QueueNode=2
integer si__MMD__QueueNode_F=0
integer si__MMD__QueueNode_I=0
integer array si__MMD__QueueNode_V
real array s__MMD__QueueNode_timeout
string array s__MMD__QueueNode_msg
integer array s__MMD__QueueNode_checksum
string array s__MMD__QueueNode_key
integer array s__MMD__QueueNode_next
constant integer si__WorldBounds=3
integer s__WorldBounds_maxX
integer s__WorldBounds_maxY
integer s__WorldBounds_minX
integer s__WorldBounds_minY
integer s__WorldBounds_centerX
integer s__WorldBounds_centerY
rect s__WorldBounds_world
region s__WorldBounds_worldRegion
real s__WorldBounds_playMaxX
real s__WorldBounds_playMaxY
real s__WorldBounds_playMinX
real s__WorldBounds_playMinY
constant integer si__MissileEffect___Effect=4
integer array s__MissileEffect___Effect_next
integer array s__MissileEffect___Effect_prev
integer s__MissileEffect___Effect_Alloc__instanceCount= 0
integer array s__MissileEffect___Effect_Alloc__recycle
real array s__MissileEffect___Effect_x
real array s__MissileEffect___Effect_y
real array s__MissileEffect___Effect_z
real array s__MissileEffect___Effect_size
real array s__MissileEffect___Effect_yaw
real array s__MissileEffect___Effect_pitch
real array s__MissileEffect___Effect_roll
string array s__MissileEffect___Effect_path
effect array s__MissileEffect___Effect_effect
constant integer si__MissileEffect=5
integer si__MissileEffect_F=0
integer si__MissileEffect_I=0
integer array si__MissileEffect_V
real array s__MissileEffect_size
real array s__MissileEffect_yaw
real array s__MissileEffect_pitch
real array s__MissileEffect_roll
real array s__MissileEffect_time
integer array s__MissileEffect_transparency
integer array s__MissileEffect_animtype
integer array s__MissileEffect_playercolor
string array s__MissileEffect_path
effect array s__MissileEffect_effect
integer array s__MissileEffect_attachments
constant integer si__Missiles___Pool=6
integer si__Missiles___Pool_F=0
integer si__Missiles___Pool_I=0
integer array si__Missiles___Pool_V
player s__Missiles___Pool_player= Player(PLAYER_NEUTRAL_PASSIVE)
group s__Missiles___Pool_group= CreateGroup()
timer array s__Missiles___Pool_timer
unit array s__Missiles___Pool_unit
constant integer si__Missiles___Coordinates=7
integer si__Missiles___Coordinates_F=0
integer si__Missiles___Coordinates_I=0
integer array si__Missiles___Coordinates_V
real array s__Missiles___Coordinates_x
real array s__Missiles___Coordinates_y
real array s__Missiles___Coordinates_z
real array s__Missiles___Coordinates_angle
real array s__Missiles___Coordinates_distance
real array s__Missiles___Coordinates_square
real array s__Missiles___Coordinates_slope
real array s__Missiles___Coordinates_alpha
integer array s__Missiles___Coordinates_ref
constant integer si__Missiles=8
integer si__Missiles_F=0
integer si__Missiles_I=0
integer array si__Missiles_V
timer s__Missiles_timer= CreateTimer()
group s__Missiles_group= CreateGroup()
rect s__Missiles_rect= Rect(0., 0., 0., 0.)
hashtable s__Missiles_table= InitHashtable()
integer s__Missiles_last= 0
integer s__Missiles_temp= 0
integer s__Missiles_id= - 1
integer s__Missiles_pid= - 1
integer array s__Missiles_missiles
integer array s__Missiles_frozen
real s__Missiles_dilation= 1
integer array s__Missiles_collection
integer s__Missiles_count= - 1
real array s__Missiles_cA
real array s__Missiles_height
real array s__Missiles_open
real array s__Missiles_toZ
real array s__Missiles_time
real array s__Missiles_sight
unit array s__Missiles_dummy
integer array s__Missiles_pkey
integer array s__Missiles_index
integer array s__Missiles_impact
integer array s__Missiles_origin
integer array s__Missiles_effect
real array s__Missiles_x
real array s__Missiles_y
real array s__Missiles_z
real array s__Missiles_prevX
real array s__Missiles_prevY
real array s__Missiles_prevZ
real array s__Missiles_nextX
real array s__Missiles_nextY
real array s__Missiles_nextZ
real array s__Missiles_turn
real array s__Missiles_veloc
real array s__Missiles_travel
boolean array s__Missiles_launched
boolean array s__Missiles_allocated
boolean array s__Missiles_finished
boolean array s__Missiles_paused
integer array s__Missiles_tileset
unit array s__Missiles_source
unit array s__Missiles_target
player array s__Missiles_owner
boolean array s__Missiles_collideZ
real array s__Missiles_collision
real array s__Missiles_damage
real array s__Missiles_acceleration
integer array s__Missiles_data
integer array s__Missiles_type
boolean array s__Missiles_roll
trigger array s__Missiles_onPeriod
trigger array s__Missiles_onHit
trigger array s__Missiles_onMissile
trigger array s__Missiles_onItem
trigger array s__Missiles_onDestructable
trigger array s__Missiles_onCliff
trigger array s__Missiles_onTerrain
trigger array s__Missiles_onTileset
trigger array s__Missiles_onFinish
trigger array s__Missiles_onBoundaries
trigger array s__Missiles_onResume
trigger array s__Missiles_onPause
trigger array s__Missiles_onRemove
constant integer si__MissileUtils___MGroup=9
integer array s__MissileUtils___MGroup_next
integer array s__MissileUtils___MGroup_prev
integer s__MissileUtils___MGroup_Alloc__instanceCount= 0
integer array s__MissileUtils___MGroup_Alloc__recycle
integer array s__MissileUtils___MGroup_missile
constant integer si__MissileGroup=10
integer si__MissileGroup_F=0
integer si__MissileGroup_I=0
integer array si__MissileGroup_V
integer array s__MissileGroup_group
integer array s__MissileGroup_size
integer array s__TimerUtils___data
timer array s__TimerUtils___tT
trigger st__MMD__QueueNode_onDestroy
trigger st__Missiles_terminate
trigger st__Missiles_setup
trigger st__Missiles_update
trigger st__Missiles_reset
trigger st__Missiles_move
trigger array st___prototype4
integer f__arg_this

// === FF addons (injected by the build; sources: scripting/jass) ===
    // Never expires; only TimerGetElapsed is read off it, to timestamp log rows (mirrors the C#
    // systems' gameTimer). Started by FF_BootTick in 90-init.j.
timer FF_gameTimer= null
boolean FF_kl_dirty= false
integer array FF_kl_unitKills
integer array FF_kl_heroKills
integer array FF_kl_unitDeaths
integer array FF_kl_heroDeaths
    // The "who killed whom" feed; capped so the file stays constant-ish sized in marathon games.
string array FF_kl_feed
integer FF_kl_feedN= 0
    // Slots 1..12 (index 0 unused): ever-active participants, and who we already reported out.
boolean array FF_gr_participant
boolean array FF_gr_eliminated
    // Side index 1..4 (FFA) / 1..2 (6v6); the mode is fixed well before the first death.
boolean array FF_gr_sideDead
    // Sides in elimination order (first to die = last place).
integer array FF_gr_deathOrder
integer FF_gr_deathN= 0
string array FF_gr_events
integer FF_gr_eventN= 0
boolean FF_gr_ended= false
timer FF_gr_pollTimer= null
    // Collapsed-block result override; see FFEnd_Resolve. Latched so a second END execution
    // can never re-settle the match, and published so GameResult reports the same verdict.
boolean FFEnd_done= false
boolean FFEnd_settled= false
integer FFEnd_winnerSlot= 0
    // Player elimination order, so a collapsed-block game can still emit placements.
integer array FF_gr_outOrder
integer FF_gr_outN= 0
    // Per-observer state, indexed by 0-based player id.
integer array FF_oc_mode
integer array FF_oc_focus
integer array FF_oc_cycleTick
unit array FF_oc_followed
integer FF_oc_tick= 0
    // Shared hero-kill interrupt (one event for everyone; the camera lock itself stays per-player).
unit FF_oc_interruptUnit= null
integer FF_oc_interruptUntil= 0
    // -- SoloSub observer substitution state ------------------------------
integer array SoloSub_observerForPlayer
integer array SoloSub_playerForObserver
boolean array SoloSub_pendingPlayer
string array SoloSub_observerOriginalName
playercolor array SoloSub_savedColor
fogmodifier array SoloSub_observerFog
boolean array SoloSub_snapOut
boolean array SoloSub_snapIn
dialog SoloSub_chooseDialog= null
dialog SoloSub_confirmDialog= null
timer SoloSub_responseTimer= null
    // v60: substitute resource proxy. The canonical slot always holds the
    // real balance; the observer pool is a spendable mirror of it.
integer array SoloSub_goldShadow
    // v65: lumber needs the same shadow as gold. Without it the sync loop
    // restored whatever a substitute spent, so their purchases were free.
integer array SoloSub_lumberShadow
timer SoloSub_syncTimer= null
    // v61: the -sub pending window. A position is held for at most
    // SoloSub_PENDING_SECONDS; after that the stock leaver system runs.
integer SoloSub_PENDING_SECONDS= 120
integer array SoloSub_pendingTicks
integer SoloSub_abandonSlot= 0
timer SoloSub_pendingTimer= null
button array SoloSub_observerButton
button SoloSub_cancelButton= null
button SoloSub_nextButton= null
button SoloSub_prevButton= null
button SoloSub_yesButton= null
button SoloSub_noButton= null
player SoloSub_selector= null
integer SoloSub_targetPlayerNumber= 0
integer SoloSub_chosenObserverId= - 1
integer SoloSub_choosePage= 1
boolean SoloSub_flowActive= false
integer SoloSub_leaveInheritNumber= 0
//= FFGS-GLOBALS-BEGIN
    // ---- generated from src\config\gameplay_settings.csv ----
integer ffgs_unit_limit= 0
integer ffgs_unit_type_limit= 0
real ffgs_spawn_hp_multiplier= 0.0
real ffgs_premass_seconds= 0.0
real ffgs_premass_bonus_lead= 0.0
real ffgs_mass_bonus_interval= 0.0
real ffgs_mass_duration_normal= 0.0
real ffgs_mass_duration_special= 0.0
real ffgs_ai_hero_pick_seconds= 0.0
real ffgs_footmen_increase_seconds= 0.0
real ffgs_bounty_increase_seconds= 0.0
real ffgs_tech1_default_seconds= 0.0
real ffgs_tech1_alternate_seconds= 0.0
real ffgs_tech1_fast_seconds= 0.0
real ffgs_tech2_seconds= 0.0
real ffgs_tech3_seconds= 0.0
integer array ffgs_mass_bonus_spawns
real array ffgs_spawn_interval
boolean array ffgs_spawn_enabled
boolean array ffgs_spawn_enabled_player
boolean array ffgs_spawn_unlocked
integer array ffgs_spawn_unlock_phase
boolean ffgs_scheduler_enabled= false
boolean ffgs_legacy_triggers_disabled= false
boolean ffgs_mass_bonus_enabled= false
real ffgs_tick_seconds= 0.0
integer ffgs_player_batch= 0
boolean ffgs_unlock_free_running_phase= false
    // ---- scheduler internals (not user editable) ----
integer array ffgs_spawn_ticks
integer array ffgs_spawn_countdown
boolean array ffgs_xmas_enabled
boolean array ffgs_obs_enabled
boolean array ffgs_han_enabled
integer array ffgs_han_hp_per_level
boolean array ffgs_r004_enabled
boolean array ffgs_force_level_two
boolean array ffgs_footmen_rules
boolean array ffgs_autosend_enabled
unit array ffgs_new_unit
group ffgs_count_group= null
integer FFOD_live_research=0
timer ffgs_scheduler_timer= null
real ffgs_center_x= 0.0
real ffgs_center_y= 0.0
boolean ffgs_scheduler_started= false
boolean ffgs_mass_mode= false
integer ffgs_max_phase_unlocked= 0
integer ffgs_validation_errors= 0
//= FFGS-GLOBALS-END
//= BUT-GLOBALS-BEGIN
boolean array BUT_armed
integer array BUT_ticks
boolean array BUT_isAI
integer BUT_window= 15
timer BUT_tickTimer= null
boolean array BUT_quiet
    // v64: leaver-gold readout, addressed to the leaver's two allies only.
boolean array LGOLD_active
integer array LGOLD_ticks
integer LGOLD_PERIOD_SECONDS= 20
real LGOLD_SHOW_SECONDS= 10.00
timer LGOLD_timer= null
//= BUT-GLOBALS-END



//JASSHelper struct globals:

hashtable FFR7_MassSpeedHash= null
// Explicit SD random purchase; initial seeds stay excluded after purchases/repicks.
boolean array FFR_Seeded
boolean array FFR_Used
boolean array FFR_Locked
    constant integer OM_HERO = 'HOr1'
    constant integer OM_ATTACK = 'AOz1'
    constant integer OM_PULSE = 'AOz2'
    constant integer OM_PROTECT = 'AOz3'
    constant integer OM_SHOCK = 'AOz4'
    constant real OM_TICK = 0.03125
    constant real OM_SPEED = 1320.0
    constant real OM_LEASH = 1200.0
    location OM_VisualGround = Location(0.0, 0.0)
    hashtable OM_Hash = InitHashtable()
    group OM_Group = CreateGroup()
    timer OM_Timer = CreateTimer()
    real OM_Now = 0.0
    boolean OM_Started = false
    integer OM_Count = 0
    unit array OM_Hero
    unit array OM_Ball
    player array OM_Owner
    unit array OM_Carrier
    group array OM_Hit
    integer array OM_State
    real array OM_X
    real array OM_Y
    real array OM_TravelRadiusValue
    real array OM_ShockRadius
    real array OM_Damage
    real array OM_HealValue
    real array OM_Deadline
    real array OM_ShockDamage
    real array OM_ShockAt
    boolean array OM_WasDead
    constant real OM_HASTE_RADIUS = 200.0
    constant real OM_HASTE_DURATION = 2.0
    integer OM_Hastes = 0
    unit array OM_HUnit
    real array OM_HExpires
    integer OM_Pulls = 0
    unit array OM_PUnit
    real array OM_PX
    real array OM_PY
    real array OM_PLeft

    constant integer FS_HERO = 'HGr1'
    constant integer FS_Q = 'AGr1'
    constant integer FS_W = 'AGr2'
    constant integer FS_E = 'AGr3'
    constant integer FS_R = 'AGr4'
    constant integer FS_DUMMY = 'hgr1'
    constant integer FS_SLOW = 'AGr5'
    constant integer FS_STUN = 'AGr6'
    constant integer FS_STUN_BUFF = 'BGr2'
    constant integer FS_FLURRY = 'AGr7'
    constant boolean FS_LEE = false
    constant real FS_PERIOD = 0.03125
    constant string FS_BARREL = "FireKegMissle.mdx"
    integer FS_High = 0
    integer FS_CodeDepth = 0
    real FS_Now = 0.0
    hashtable FS_Hash = InitHashtable()
    timer FS_Timer = CreateTimer()
    location FS_Ground = Location(0.0, 0.0)
    integer array FS_Kind
    unit array FS_U
    unit array FS_Target
    player array FS_Owner
    effect array FS_DrinkFX
    effect array FS_FX
    real array FS_X
    real array FS_Y
    real array FS_TX
    real array FS_TY
    real array FS_Damage
    real array FS_Left
    real array FS_Expires
    real array FS_Shield
    real array FS_ShieldEnd
    real array FS_Rage
    real array FS_RageEnd
    real array FS_Armor
    real array FS_Heal
    real array FS_Empower
    real array FS_EmpowerEnd
    real array FS_FlurryEnd
    constant integer FS_DETONATE = 'AGr8'
    boolean array FS_Landed

    constant integer GD_ABILITY = 'AZd1'
    constant integer GD_SLOW = 'AZd2'
    constant real GD_PERIOD = 0.05
    hashtable GDV_Data = InitHashtable()
    group GDV_Units = CreateGroup()
    integer GDV_Step = 0
    group GDB_Enum = CreateGroup()
    location GDB_Loc = Location(0.0, 0.0)
    integer GD_Count = 0
    unit array GD_Caster
    effect array GD_Dome
    real array GD_Left
    hashtable GD_Data = InitHashtable()
    group GD_Enum = CreateGroup()
    timer GD_Timer = CreateTimer()
    location GD_Loc = Location(0.0, 0.0)


    unit array GSI_Source
    timer array GSI_Expiry
    rect GSI_Bounds = null


// RC6 bot reporting and host integration.
    string FF_gameToken = ""
    integer FF_PRELOAD_MAX = 240
    boolean FF_hostBotGame = false
    boolean FF_kl_done = false
    boolean FF_STATS_DAMAGE = true
    integer array FF_st_poolOut
    integer array FF_st_poolIn
    integer array FF_st_inhOut
    integer array FF_st_inhIn
    integer array FF_st_kothGold
    integer array FF_st_denyOwn
    integer array FF_st_denyAlly
    integer array FF_st_tmCasts
    integer array FF_st_tmHits
    integer array FF_st_tmDenied
    integer array FF_st_tmSaves
    integer array FF_st_creeps
    integer array FF_st_creepGold
    integer array FF_st_teamRes
    integer FF_ST_DMG_OUT = 0
    integer FF_ST_DMG_BLD = 1
    integer FF_ST_DMG_IN = 2
    integer array FF_st_dmg
    real array FF_st_dmgRem
    integer FF_ST_ALIVE = 0
    integer FF_ST_OUT = 1
    integer FF_ST_LEFT = 2
    integer array FF_st_state
    string array FF_st_leftT
    integer array FF_st_heroLvl
    string array FF_st_row
    string array FF_st_row2
    integer array FF_st_sig
    string array FF_st_key
    integer array FF_st_val
    integer FF_st_n = 0
    integer FF_st_split = 0
    real FF_ST_TM_WAIT = 4.0
    integer FF_ST_TM_MAX = 32
    unit array FF_st_tmCaster
    unit array FF_st_tmTarget
    integer array FF_st_tmSlot
    real array FF_st_tmUntil
    integer FF_st_tmN = 0
    hashtable FF_us_ht = InitHashtable()
    hashtable FF_us_learned = InitHashtable()
    integer FF_US_CHAT_BURST = 4
    integer FF_US_CMD_CAP = 999
    integer FF_US_ITEM = 1
    integer FF_US_UNIT = 2
    integer FF_US_TECH = 3
    integer FF_US_TOWER = 4
    integer FF_US_SPELL = 5
    integer FF_US_CMD = 6
    integer FF_US_CATS = 6
    integer FF_US_EVENT_MAX = 400
    integer FF_US_SOLD_MAX = 64
    integer FF_US_HERO_MAX = 16
    integer FF_US_SKILL_MAX = 64
    integer FF_US_BASE_TYPES = 50
    integer array FF_us_n
    string array FF_us_catName
    boolean array FF_us_dirty
    integer array FF_us_rowN
    integer array FF_us_heroN
    string array FF_us_events
    integer FF_us_eventN = 0
    boolean FF_us_sharedDirty = false
    unit array FF_us_heroSeen
    boolean array FF_us_hadHero
    boolean array FF_us_swapSeen
    unit array FF_us_sold
    unit array FF_us_seller
    integer array FF_us_soldCost
    integer FF_us_soldN = 0
    timer FF_us_soldTimer = null
    integer array FF_us_kothHold
    integer array FF_us_kothCaps
    player FF_us_kothLast = null
    string FF_us_modes = null
    trigger FF_us_modeHook = null
    string FF_us_modeExtra = ""
    string array FF_us_cmd
    integer FF_us_cmdN = 0
    integer array FF_us_chatBurst
    string FF_us_chars = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    integer FF_GR_EVENT_MAX = 200
    string FF_gr_gameendRow = null
    integer FF_bv_N = 9
    real FF_bv_SIGHT = 2000.0
    integer FF_bv_DUMMY = 'h055'
    integer FF_bv_DETECT_OWL = 'Adtg'
    integer FF_bv_DETECT_SENTRY = 'A05H'
    group FF_bv_units = null
string array FF_rxRosterName
    hashtable DK_Hash = null
    timer DK_Timer = null
    real DK_Now = 0.0
    integer DK_High = 0
    integer array DK_Kind
    unit array DK_Source
    unit array DK_Target
    player array DK_Owner
    effect array DK_FX
    group array DK_Hit
    group array DK_Pulled
    real array DK_X
    real array DK_Y
    real array DK_DX
    real array DK_DY
    real array DK_Left
    real array DK_End
    real array DK_Damage
    integer array DK_Stacks
    integer array DK_Parent
    boolean array DK_Return


hashtable MU_Hash = null
unit array MU_Hero
integer MU_Count = 0
timer MU_Timer = null
trigger MU_CleaverHit = null
real MU_Now = 0.0


    group FF_TestRecruited = CreateGroup()
hashtable TFP_Table___ht= InitHashtable()
constant integer TFP_tfConsts_CASTER_DUMMY_ID='htf2'
constant integer TFP_tfConsts_EYE_DUMMY_ID='htf3'
constant integer TFP_tfConsts_CARD_DUMMY_ID='htf1'
constant integer TFP_tfConsts_WILD_CARDS_ID='ATf1'
constant integer TFP_tfConsts_PICK_A_CARD_ID='ATf2'
constant integer TFP_tfConsts_BLUE_CARD_ID='ATf3'
constant integer TFP_tfConsts_RED_CARD_ID='ATf4'
constant integer TFP_tfConsts_GOLD_CARD_ID='ATf5'
constant integer TFP_tfConsts_DUMMY_SLOW_ID='ATf9'
constant integer TFP_tfConsts_DUMMY_STUN_ID='ATfa'
constant integer TFP_tfConsts_DESTINY_ID='ATfb'
constant integer TFP_tfConsts_GATE_ID='ATfc'
constant real TFP_tfConsts_FPS=1. / 30.
constant integer TFP_tfConsts_BLUE_CARD=0
constant integer TFP_tfConsts_RED_CARD=1
constant integer TFP_tfConsts_GOLD_CARD=2
integer TFP_tfConsts_hiddenCard
constant real TFP_wildCards___OFFSET_ANGLE=18. * bj_DEGTORAD
constant real TFP_wildCards___PROJECTILE_SPEED=1100.
constant real TFP_wildCards___ENUM_RADIUS=32.
constant real TFP_wildCards___TOTAL_DISTANCE=1450.
integer array TFP_wildCards___datDB
integer TFP_wildCards___dbIndex=- 1
timer TFP_wildCards___time=CreateTimer()
group TFP_wildCards___grp=CreateGroup()
integer TFP_wildCards___cdrTable
constant real TFP_pickACard___CYCLE_MAX_DURATION=6.
constant real TFP_pickACard___CARD_CYCLE_PERIOD=.6
constant real TFP_pickACard___RED_CARD_ENUM_RANGE=250.
constant string TFP_pickACard___TICKSOUND="Sound\\Interface\\MouseClick1.wav"
constant string TFP_pickACard___BLUEFX="Units\\NightElf\\Wisp\\WispExplode.mdl"
constant string TFP_pickACard___REDFX="Abilities\\Spells\\Human\\Feedback\\SpellBreakerAttack.mdl"
constant string TFP_pickACard___GOLDFX="Abilities\\Weapons\\Bolt\\BoltImpact.mdl"
integer TFP_pickACard___fromTimer
integer TFP_pickACard___fromFate
sound TFP_pickACard___snd
integer array TFP_pickACard___dummyDB
integer TFP_pickACard___dummyDBIndex=- 1
timer TFP_pickACard___dummyClock=CreateTimer()
constant string TFP_destiny___GATE_SOUND="Abilities\\Spells\\Human\\ThunderClap\\ThunderClapCaster.wav"
integer array TFP_destiny___destinyDB
timer TFP_destiny___time=CreateTimer()
integer TFP_destiny___dbIndex=- 1
group TFP_destiny___grp=CreateGroup()
integer TFP_destiny___attachments
integer TFP_destiny___cdrTable
integer TFP_si__Table___GTable_F=0
integer TFP_si__Table___GTable_I=0
integer array TFP_si__Table___GTable_V
integer TFP_si__wildCards___cardDat_F=0
integer TFP_si__wildCards___cardDat_I=0
integer array TFP_si__wildCards___cardDat_V
unit array TFP_s__wildCards___cardDat_caster
unit array TFP_s___wildCards___cardDat_cards
integer array TFP_s__wildCards___cardDat_cards
real array TFP_s___wildCards___cardDat_gradX
integer array TFP_s__wildCards___cardDat_gradX
real array TFP_s___wildCards___cardDat_gradY
integer array TFP_s__wildCards___cardDat_gradY
real array TFP_s__wildCards___cardDat_damage
real array TFP_s__wildCards___cardDat_traveled
group array TFP_s__wildCards___cardDat_struckUnits
integer TFP_si__pickACard___pickDat_F=0
integer TFP_si__pickACard___pickDat_I=0
integer array TFP_si__pickACard___pickDat_V
unit array TFP_s__pickACard___pickDat_fate
integer array TFP_s__pickACard___pickDat_revertAbilityLevel
real array TFP_s__pickACard___pickDat_elapsedTime
boolean array TFP_s__pickACard___pickDat_locked
boolean array TFP_s__pickACard___pickDat_thrown
integer TFP_si__pickACard___dummyCardDat_F=0
integer TFP_si__pickACard___dummyCardDat_I=0
integer array TFP_si__pickACard___dummyCardDat_V
unit array TFP_s__pickACard___dummyCardDat_dummy
unit array TFP_s__pickACard___dummyCardDat_fate
integer TFP_si__destiny___target_F=0
integer TFP_si__destiny___target_I=0
integer array TFP_si__destiny___target_V
unit array TFP_s__destiny___target_who
integer TFP_si__destiny___destinyDat_F=0
integer TFP_si__destiny___destinyDat_I=0
integer array TFP_si__destiny___destinyDat_V
unit array TFP_s__destiny___destinyDat_fate
group array TFP_s__destiny___destinyDat_visionDummies
real array TFP_s__destiny___destinyDat_elapsedTime
real array TFP_s__destiny___destinyDat_duration
integer array TFP_s__destiny___destinyDat_revertAbilityLevel
integer array TFP_s__tfConsts_CARD_ID
integer array TFP_si__Table___GTable_type
constant integer TFP_FFDP_ABIL_CAST   = 'ATfd' // "Dark Passage"  (target point, base Carrion Swarm)
constant integer TFP_FFDP_UNIT_LANTERN= 'htf4' // lantern dummy unit
constant integer TFP_FFDP_ABIL_CROW   = 'Amrf' // Crow Form, used to unlock SetUnitFlyHeight
constant real    TFP_FFDP_TICK        = 0.03
constant real    TFP_FFDP_CAST_RANGE  = 1000.0 // lantern is clamped to this from the caster
constant real    TFP_FFDP_THROW_SPEED = 1150.0 // lantern flight, units/sec
constant real    TFP_FFDP_THROW_ARC   = 300.0  // apex of the throw
constant real    TFP_FFDP_RIDE_SPEED  = 1400.0 // ally travel along the chain, units/sec
constant real    TFP_FFDP_RIDE_MAXTIME= 4.0    // hard stop on a ride that cannot converge
constant real    TFP_FFDP_GRAB_RADIUS = 130.0  // how close an ally must be to be offered the grab
constant real    TFP_FFDP_SHIELD_AOE  = 130.0  // allies shielded where the lantern lands
constant real    TFP_FFDP_LEASH       = 1500.0 // caster-to-lantern break distance
constant real    TFP_FFDP_REFRESH     = 0.03   // how often grab abilities are handed out / taken back
constant real    TFP_FFDP_ALIVE       = 0.405  // life above this == alive
constant string  TFP_FFDP_FX_LANTERN  = "Abilities\\Spells\\Human\\Brilliance\\Brilliance.mdl"
constant string  TFP_FFDP_FX_LAND     = "Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilMissile.mdl"
constant string  TFP_FFDP_FX_GRAB     = "Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilMissile.mdl"
constant string  TFP_FFDP_LIGHTNING   = "TFLN" // Custom Nether Chains by Pharaoh_ (Hive Workshop)
integer          TFP_FFDP_Count       = 0
integer array    TFP_FFDP_Phase
unit    array    TFP_FFDP_Caster
player  array    TFP_FFDP_Owner
unit    array    TFP_FFDP_Lantern
unit    array    TFP_FFDP_Rider
hashtable GL_Armor = InitHashtable()
location GTW_HeightLoc = Location(0.0, 0.0)
group array TFP_LinkInside
group array TFP_LanternInside
group array TFP_RideHit
group TFP_LinkEnum = CreateGroup()
group TFP_LinkNext = CreateGroup()
group TFP_LanternNext = CreateGroup()
group   array    TFP_FFDP_Track       // allies currently holding the grab ability
lightning array  TFP_FFDP_Chain
effect  array    TFP_FFDP_Fx          // glow attached to the lantern
integer array    TFP_FFDP_Level
real    array    TFP_FFDP_Mx          // lantern x/y while it flies
real    array    TFP_FFDP_My
real    array    TFP_FFDP_Tx          // throw destination
real    array    TFP_FFDP_Ty
real    array    TFP_FFDP_Total       // full length of the current move
real    array    TFP_FFDP_Left        // distance still to travel
real    array    TFP_FFDP_Time        // planted seconds left, or ride time spent
real    array    TFP_FFDP_Next        // seconds until the next grab-ability refresh
integer          TFP_FFDP_ShCount     = 0
unit    array    TFP_FFDP_ShUnit
real    array    TFP_FFDP_ShAmount
real    array    TFP_FFDP_ShTime
effect  array    TFP_FFDP_ShFx
code             TFP_FFDP_Callback    = null
integer          TFP_FFDP_Ticks       = 0
timer            TFP_FFDP_Clock       = null
group            TFP_FFDP_Cand        = null
group            TFP_FFDP_Keep        = null
boolexpr         TFP_FFDP_Filt        = null
location         TFP_FFDP_Loc         = null
player           TFP_FFDP_FilterOwner = null
unit             TFP_FFDP_FilterSkip  = null
hashtable TFP_FFDP_Refs = InitHashtable()
real array TFP_FFDP_Height
real array TFP_FFDP_StartX
real array TFP_FFDP_StartY
player array TFP_FFDP_RiderOwner
real array TFP_FFDP_LastX
real array TFP_FFDP_LastY
integer array TFP_FFDP_BlinkTicks
boolean array TFP_FFDP_OwnInvul
constant integer TFP_FFDP_TRAVEL_INVUL = 'ATfe'
constant real TFP_FFDP_JUMP_LIMIT = 128.0
effect array TFP_FFDP_GroundFx
boolean array TFP_TF_CardLocked
integer array TFP_TF_LockedThrow
hashtable MQ_Hash = InitHashtable()
trigger MQ_FinishTrigger = CreateTrigger()
trigger MQ_RemoveTrigger = CreateTrigger()
hashtable MD_Hash = InitHashtable()
hashtable MD_Types = InitHashtable()
hashtable TF33_H=InitHashtable()
hashtable TF33_G=InitHashtable()
    hashtable TF45_Gate=InitHashtable()
    hashtable TF46_H=InitHashtable()
    real array TF46_ZRange
group TF33_Heroes=CreateGroup()
    hashtable VG_Hash = null
    hashtable VG_PrevX = null
    hashtable VG_PrevY = null
    unit array VG_Hero
boolean F35_MassReleased=false
integer array F35_PlayerStaged
unit array F35_MassPool
integer F35_MassPoolCount=0
hashtable MM_Hash=InitHashtable()
integer array MDV_Code
boolean array MDV_Used
dialog FFStartDialog=null
button FFStartSD=null
button FFStartAR=null
button FFStartAP=null
integer array FFP_PairSent
constant real P67_POST7_RATE = 70.00
constant real P67_CATCHUP_RATE = 200.00
constant real P67_APPROACH6_RATE = 150.00
boolean P67_Running = false
boolean P67_Reached4 = false
boolean P67_Reached6 = false
boolean P78_Reached10 = false
constant real P78_BONUS_PER_LEVEL = 40.00
constant integer P78_XP_LEVEL7 = 2700
constant integer P78_XP_LEVEL8 = 3500
constant integer P78_XP_LEVEL9 = 4400
constant integer P78_XP_LEVEL10 = 5400
boolean P67_MassEnded = false
boolean P67_FirstColo = false
real array P67_Remainder
unit array P67_LastHero

// Final Spark: independent state per cast, never shared with another hero system.
constant integer LX_ABILITY = 'ALxR'
constant real LX_RANGE = 3400.0
constant real LX_HALF_WIDTH = 100.0
constant real LX_CHARGE = 1.0
constant real LX_TICK = 0.03125
constant integer LX_SEGMENTS = 8
hashtable LX_Hash = null
hashtable LX_Casters = null
unit array LX_Hero

    constant integer ST_UNIT = 'nStk'
    constant integer ST_BLINK = 'AStB'
    constant real ST_RANGE = 800.0
    constant real ST_COOLDOWN = 7.0
    constant real ST_REGEN_DELAY = 7.0
    constant real ST_MAX_SHIELD = 80.0
    hashtable ST_Hash = null
    group ST_Units = null
    group array ST_Selected
    real ST_Now = 0.0
    item ST_Probe = null
    real ST_LandX = 0.0
    real ST_LandY = 0.0

hashtable MW_Hash = null
endglobals
