// The extension is north of the original map. Match-wide searches keep their original extents.
function AR_MatchBounds takes nothing returns rect
    local rect r = GetWorldBounds()
    call SetRect(r,GetRectMinX(r),GetRectMinY(r),GetRectMaxX(r),GetRectMaxY(r)-4096.)
    return r
endfunction

function AR_Fighter takes unit u returns boolean
    if AR_state != 2 or u == null then
        return false
    endif
    return GetOwningPlayer(u) == AR_owner[0] or GetOwningPlayer(u) == AR_owner[1]
endfunction

function AR_BarDamage takes nothing returns nothing
    if AR_Fighter(GetEventDamageSource()) != AR_Fighter(GetTriggerUnit()) then
        call BlzSetEventDamage(0)
    endif
endfunction

function AR_BarOrder takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local boolean fighter = AR_Fighter(u)
    local boolean outside
    if GetTriggerEventId() == EVENT_PLAYER_UNIT_ISSUED_POINT_ORDER then
        set outside = fighter != RectContainsCoords(AR_floor,GetOrderPointX(),GetOrderPointY())
    else
        set outside = fighter != AR_Fighter(GetOrderTargetUnit())
        if GetOrderTargetUnit() == null then
            set outside = fighter != RectContainsCoords(AR_floor,GetWidgetX(GetOrderTarget()),GetWidgetY(GetOrderTarget()))
        endif
    endif
    if outside then
        call PauseUnit(u,true)
        call IssueImmediateOrder(u,"stop")
        call PauseUnit(u,false)
    endif
    set u = null
endfunction

function AR_BarEntry takes nothing returns nothing
    local unit u = GetEnteringUnit()
    local player p = GetOwningPlayer(u)
    if not AR_Fighter(u) then
        if GetPlayerId(p) < 12 then
            call SetUnitPosition(u,GetPlayerStartLocationX(p),GetPlayerStartLocationY(p))
        else
            call SetUnitPosition(u,0,-256)
        endif
        call IssueImmediateOrder(u,"stop")
    endif
    set u = null
endfunction

function AR_Init takes nothing returns nothing
    local trigger entry = CreateTrigger()
    set AR_floor = Rect(-1024,5376,1024,6912)
    set AR_clock = CreateTimer()
    set AR_damage = CreateTrigger()
    set AR_orders = CreateTrigger()
    call TriggerRegisterEnterRectSimple(entry,AR_floor)
    call TriggerAddAction(entry,function AR_BarEntry)
    call TriggerRegisterAnyUnitEventBJ(AR_damage,EVENT_PLAYER_UNIT_DAMAGING)
    call TriggerAddAction(AR_damage,function AR_BarDamage)
    call TriggerRegisterAnyUnitEventBJ(AR_orders,EVENT_PLAYER_UNIT_ISSUED_POINT_ORDER)
    call TriggerRegisterAnyUnitEventBJ(AR_orders,EVENT_PLAYER_UNIT_ISSUED_TARGET_ORDER)
    call TriggerAddAction(AR_orders,function AR_BarOrder)
    call DisableTrigger(AR_damage)
    call DisableTrigger(AR_orders)
    // Level-one arena pool. Each hero has a native combat skill and no spawned army.
    set AR_roster[0] = 'H00A'
    set AR_skill[0] = 'AHtb'
    set AR_roster[1] = 'E002'
    set AR_skill[1] = 'AEer'
    set AR_roster[2] = 'U003'
    set AR_skill[2] = 'A00P'
    set AR_roster[3] = 'U004'
    set AR_skill[3] = 'AUcs'
    set AR_roster[4] = 'E005'
    set AR_skill[4] = 'AEfk'
    set AR_roster[5] = 'O004'
    set AR_skill[5] = 'AOcl'
    set entry = null
endfunction
