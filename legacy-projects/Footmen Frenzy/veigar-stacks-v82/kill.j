function VG_ClassicKill takes nothing returns nothing
    local unit u = GetKillingUnit()
    local unit victim = GetTriggerUnit()
    local integer gain = 1
    if GetUnitTypeId(u) == 'HVg1' and not IsUnitIllusion(u) and IsUnitEnemy(victim, GetOwningPlayer(u)) and not IsUnitIllusion(victim) and not IsUnitType(victim, UNIT_TYPE_STRUCTURE) then
        if IsUnitType(victim, UNIT_TYPE_HERO) then
            set gain = 5
        endif
        call SaveInteger(VG_Hash, GetHandleId(u), 702, LoadInteger(VG_Hash, GetHandleId(u), 702) + gain)
        call VG82_UpdateCounter(u)
    endif
    set u = null
    set victim = null
endfunction
