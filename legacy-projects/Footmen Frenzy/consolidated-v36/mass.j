function F35_MassEnabled takes nothing returns boolean
    return udg_mode_pub and not udg_mode_inhouse and not udg_mode_no_mass
endfunction

function F35_StageFootman takes unit u, integer pn returns nothing
    local integer team=(pn - 1) / 3
    local integer slot=ModuloInteger(pn - 1, 3)
    local integer n=F35_PlayerStaged[pn]
    local real along=I2R(slot * 7 + ModuloInteger(n, 7)) * 48.0
    local real depth=I2R(n / 7) * 32.0
    local real x=128.0 + along + depth
    local real y=1088.0 - along + depth
    if team == 0 or team == 3 then
        set x=-x
    endif
    if team == 2 or team == 3 then
        set y=-y
    endif
    call ShowUnit(u, false)
    call PauseUnit(u, true)
    call SetUnitInvulnerable(u, true)
    call SetUnitUseFood(u, false)
    call SetUnitPathing(u, false)
    call SetUnitX(u, ffgs_center_x + x)
    call SetUnitY(u, ffgs_center_y + y)
    set F35_PlayerStaged[pn]=n + 1
    set F35_MassPool[F35_MassPoolCount]=u
    set F35_MassPoolCount=F35_MassPoolCount + 1
endfunction

function F35_ReleaseMass takes nothing returns nothing
    local integer i=0
    local integer pn
    local unit u
    if F35_MassReleased then
        return
    endif
    set F35_MassReleased=true
    loop
        exitwhen i >= F35_MassPoolCount
        set u=F35_MassPool[i]
        set pn=GetPlayerId(GetOwningPlayer(u)) + 1
        if GetUnitTypeId(u) != 0 and GetWidgetLife(u) > 0.405 and pn >= 1 and pn <= 12 and udg_player_active[pn] and IsUnitAliveBJ(udg_base[pn]) then
            call FFGS_ComputeStats(0, pn)
            call FFGS_ApplyUnit(u, 0, pn)
            call SetUnitPathing(u, true)
            call SetUnitUseFood(u, true)
            call SetUnitInvulnerable(u, false)
            call UnitRemoveAbility(u, 'Avul')
            call ShowUnit(u, true)
            call FFR7_ApplyMassSpeed(u)
            call PauseUnit(u, false)
            if udg_autosend[pn] then
                call IssuePointOrder(u, "attack", ffgs_center_x, ffgs_center_y)
            endif
        else
            call RemoveUnit(u)
        endif
        set F35_MassPool[i]=null
        set i=i + 1
    endloop
    set F35_MassPoolCount=0
    set u=null
endfunction

function F35_MassPoint takes integer pn returns location
    local integer team=(pn - 1) / 3
    local integer slot=ModuloInteger(pn - 1, 3)
    local real x=400.0 + I2R(slot) * 336.0
    local real y=1072.0 - I2R(slot) * 336.0
    if not F35_MassEnabled() then
        return Location(GetLocationX(udg_player_start[pn]), GetLocationY(udg_player_start[pn]))
    endif
    if team == 0 or team == 3 then
        set x=-x
    endif
    if team == 2 or team == 3 then
        set y=-y
    endif
    return Location(ffgs_center_x + x, ffgs_center_y + y)
endfunction
