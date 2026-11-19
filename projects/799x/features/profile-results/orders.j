function PF_OrderEvent takes nothing returns nothing
    local eventid e = GetTriggerEventId()
    local integer s = GetPlayerId(GetTriggerPlayer())+1
    local integer id
    local unit u
    if s > 12 then
        return
    endif
    if e == EVENT_PLAYER_UNIT_RESEARCH_START then
        set id = GetResearched()
        call PF_Purchase(s,"research_start",id,PF_Price(id,1+GetPlayerTechCount(Player(s-1),id,true)))
    elseif e == EVENT_PLAYER_UNIT_RESEARCH_CANCEL then
        call PF_Log(s,"research_cancel",GetResearched(),-1,0)
    elseif e == EVENT_PLAYER_UNIT_TRAIN_FINISH then
        set u = GetTrainedUnit()
        if IsUnitType(u,UNIT_TYPE_HERO) then
            call PF_Hero(s,u)
        else
            call PF_Use(s,3,GetUnitTypeId(u),1)
            call PF_Appearance(s,u,1)
        endif
        call PF_Log(s,"train",GetUnitTypeId(u),-1,0)
    elseif e == EVENT_PLAYER_UNIT_TRAIN_START then
        set id = GetTrainedUnitType()
        call PF_Purchase(s,"train_start",id,PF_Price(id,1))
    elseif e == EVENT_PLAYER_UNIT_TRAIN_CANCEL then
        call PF_Log(s,"train_cancel",GetTrainedUnitType(),-1,0)
    elseif e == EVENT_PLAYER_UNIT_CONSTRUCT_START then
        set id = GetUnitTypeId(GetConstructingStructure())
        call PF_Purchase(s,"construct_start",id,PF_Price(id,1))
    elseif e == EVENT_PLAYER_UNIT_CONSTRUCT_CANCEL then
        call PF_Log(s,"construct_cancel",GetUnitTypeId(GetCancelledStructure()),-1,0)
    else
        call PF_Log(s,"construct",GetUnitTypeId(GetConstructedStructure()),-1,0)
    endif
    set u = null
endfunction

function PF_InitOrders takes nothing returns nothing
    local trigger t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_RESEARCH_START)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_RESEARCH_CANCEL)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_TRAIN_START)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_TRAIN_FINISH)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_TRAIN_CANCEL)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_CONSTRUCT_START)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_CONSTRUCT_CANCEL)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_CONSTRUCT_FINISH)
    call TriggerAddAction(t,function PF_OrderEvent)
    set t = null
endfunction
