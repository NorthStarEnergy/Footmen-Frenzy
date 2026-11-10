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
