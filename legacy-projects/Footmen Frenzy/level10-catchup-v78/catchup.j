// Percentage points added to the existing 70% rate. No XP is granted here.
function P78_Rate takes integer level, integer xp, boolean unlocked, real baseRate returns real
    local integer lower
    local integer upper
    local real progress
    if not unlocked or level < 7 or level >= 10 then
        return baseRate
    endif
    if level == 7 then
        set lower = P78_XP_LEVEL7
        set upper = P78_XP_LEVEL8
    else
        if level == 8 then
            set lower = P78_XP_LEVEL8
            set upper = P78_XP_LEVEL9
        else
            set lower = P78_XP_LEVEL9
            set upper = P78_XP_LEVEL10
        endif
    endif
    set progress = RMaxBJ(0.00, RMinBJ(1.00, I2R(xp - lower) / I2R(upper - lower)))
    return baseRate + P78_BONUS_PER_LEVEL * (10.00 - I2R(level) - progress)
endfunction
