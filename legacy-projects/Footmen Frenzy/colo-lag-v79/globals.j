constant real P79_LAG_SECONDS = 90.00
constant real P79_MIN_GAP = 1.00
constant real P79_BONUS_PER_LEVEL = 0.40
constant real P79_MAX_SHARE_BONUS = 1.00
constant real P79_WAVE_LEVEL_CAP = 0.50
timer P79_Clock = null
hashtable P79_Table = null
unit array P79_Hero
integer array P79_Target
boolean array P79_Waiting
boolean array P79_Active
real array P79_Since
integer array P79_WaveBonus
integer array P79_WaveCap
