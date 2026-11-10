// Hero keys 24/25: activation time / last paid time. Cloud key 46: emitted DPS.
// Poison keys 50..53: strongest pending exposure for each half-second tick.
function MC_Now takes nothing returns real
    return MU_Now + TimerGetElapsed(MU_Timer)
endfunction

function MC_Heat takes unit u returns real
    if not LoadBoolean(MU_Hash, GetHandleId(u), 1) then
        return 0.0
    endif
    return RMaxBJ(0.0, RMinBJ(1.0, (MC_Now() - LoadReal(MU_Hash, GetHandleId(u), 24)) / 10.0))
endfunction

// Integral of the 1x -> 2x linear ramp, including its capped plateau.
function MC_Integral takes real age returns real
    local real ramp = RMaxBJ(0.0, RMinBJ(10.0, age))
    return RMaxBJ(0.0, age) + ramp * ramp * 0.05 + RMaxBJ(0.0, age - 10.0)
endfunction

function MC_Drain takes unit u, integer rank returns real
    local integer h = GetHandleId(u)
    local real started = LoadReal(MU_Hash, h, 24)
    local real previous = LoadReal(MU_Hash, h, 25)
    return (8.0 + 4.0 * rank) * (MC_Integral(MC_Now() - started) - MC_Integral(previous - started))
endfunction

function MC_Model takes real heat returns string
    return "Spells\\Mundo\\Cloud" + I2S(R2I(RMaxBJ(0.0, RMinBJ(1.0, heat)) * 20.0)) + ".mdx"
endfunction
