// Per-spawn XP levels; base-pack targets exclude the separate center boss.
function C77_ColoLevel takes integer wave, integer slot, integer original returns integer
    if slot == 1 or slot == 2 then
        return 5 + (IMaxBJ(1, wave) - 1) / 2
    endif
    if wave == 3 then
        if slot == 5 then
            return 5
        endif
        if slot == 10 then
            return 4
        endif
        if slot == 15 then
            return 5
        endif
        if slot == 20 then
            return 7
        endif
        if slot == 23 then
            return 8
        endif
        if slot == 24 then
            return 7
        endif
    endif
    if wave == 4 then
        if slot == 6 then
            return 4
        endif
        if slot == 11 then
            return 5
        endif
        if slot == 16 then
            return 4
        endif
        if slot == 21 then
            return 5
        endif
        if slot == 23 then
            return 9
        endif
        if slot == 24 then
            return 7
        endif
        if slot == 25 then
            return 8
        endif
    endif
    if wave == 5 then
        if slot == 7 then
            return 4
        endif
        if slot == 12 then
            return 5
        endif
        if slot == 17 then
            return 6
        endif
        if slot == 22 then
            return 5
        endif
        if slot == 23 then
            return 10
        endif
        if slot == 24 then
            return 7
        endif
        if slot == 25 then
            return 7
        endif
    endif
    if wave == 6 then
        if slot == 3 then
            return 4
        endif
        if slot == 8 then
            return 7
        endif
        if slot == 13 then
            return 9
        endif
        if slot == 18 then
            return 5
        endif
        if slot == 23 then
            return 9
        endif
        if slot == 24 then
            return 6
        endif
        if slot == 25 then
            return 6
        endif
    endif
    if wave == 7 then
        if slot == 4 then
            return 5
        endif
        if slot == 9 then
            return 5
        endif
        if slot == 14 then
            return 5
        endif
        if slot == 19 then
            return 5
        endif
        if slot == 23 then
            return 10
        endif
        if slot == 24 then
            return 7
        endif
        if slot == 25 then
            return 8
        endif
    endif
    if wave == 8 then
        if slot == 5 then
            return 5
        endif
        if slot == 10 then
            return 5
        endif
        if slot == 15 then
            return 5
        endif
        if slot == 20 then
            return 6
        endif
        if slot == 23 then
            return 10
        endif
        if slot == 24 then
            return 8
        endif
        if slot == 25 then
            return 8
        endif
    endif
    if wave == 9 then
        if slot == 6 then
            return 5
        endif
        if slot == 11 then
            return 5
        endif
        if slot == 16 then
            return 5
        endif
        if slot == 21 then
            return 7
        endif
        if slot == 23 then
            return 10
        endif
        if slot == 24 then
            return 8
        endif
        if slot == 25 then
            return 9
        endif
    endif
    if wave == 10 then
        if slot == 7 then
            return 5
        endif
        if slot == 12 then
            return 5
        endif
        if slot == 17 then
            return 8
        endif
        if slot == 22 then
            return 5
        endif
        if slot == 23 then
            return 10
        endif
        if slot == 24 then
            return 9
        endif
        if slot == 25 then
            return 9
        endif
    endif
    return original
endfunction

function C77_ApplyColoLevel takes unit u, integer slot returns nothing
    if P67_Enabled() then
        call BlzSetUnitIntegerFieldBJ(u, UNIT_IF_LEVEL, C77_ColoLevel(udg_colossal_wave, slot, GetUnitLevel(u)))
    endif
endfunction
