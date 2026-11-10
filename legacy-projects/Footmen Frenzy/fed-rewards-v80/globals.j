constant real P80_FREE_LEAD = 1.00
constant real P80_REDUCTION_PER_LEVEL = 0.15
constant real P80_MAX_REDUCTION = 0.60
constant integer P80_MIN_LEVEL = 7
boolean P80_Running = false
boolean P80_Initialized = false
hashtable P80_Rewards = null
integer P80_Sequence = 0
boolean array P80_BountyWasOn
real array P80_GoldRemainder
real array P80_XPRemainder
unit array P80_LastHero
