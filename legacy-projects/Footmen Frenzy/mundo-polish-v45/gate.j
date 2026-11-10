function TF45_GateClear takes unit u returns nothing
    local integer h=GetHandleId(u)
    local timer t=LoadTimerHandle(TF45_Gate,h,0)
    if t!=null then
        call DestroyEffect(LoadEffectHandle(TF45_Gate,h,1))
        call DestroyEffect(LoadEffectHandle(TF45_Gate,h,2))
        call DestroyEffect(LoadEffectHandle(TF45_Gate,h,3))
        call FlushChildHashtable(TF45_Gate,GetHandleId(t))
        call FlushChildHashtable(TF45_Gate,h)
        call PauseTimer(t)
        call DestroyTimer(t)
    endif
    set t=null
endfunction

function TF45_GateTick takes nothing returns nothing
    local timer t=GetExpiredTimer()
    local unit u=LoadUnitHandle(TF45_Gate,GetHandleId(t),0)
    local integer h=GetHandleId(u)
    local real age=LoadReal(TF45_Gate,h,4)+.03
    if not TFP_TF_Alive(u) or age>3. then
        call TF45_GateClear(u)
    else
        call SaveReal(TF45_Gate,h,4,age)
        call BlzSetSpecialEffectYaw(LoadEffectHandle(TF45_Gate,h,1),age*2.)
        call BlzSetSpecialEffectYaw(LoadEffectHandle(TF45_Gate,h,2),-age*2.)
    endif
    set t=null
    set u=null
endfunction

function TF45_GateStart takes nothing returns nothing
    local unit u=GetTriggerUnit()
    local integer h=GetHandleId(u)
    local timer t
    local real x=GetSpellTargetX()
    local real y=GetSpellTargetY()
    local real dx=x-GetUnitX(u)
    local real dy=y-GetUnitY(u)
    local real distance=SquareRoot(dx*dx+dy*dy)
    if GetSpellAbilityId()=='ATfc' then
        call TF45_GateClear(u)
        if distance>5500. then
            set x=GetUnitX(u)+5500.*dx/distance
            set y=GetUnitY(u)+5500.*dy/distance
        endif
        set t=CreateTimer()
        call SaveTimerHandle(TF45_Gate,h,0,t)
        call SaveUnitHandle(TF45_Gate,GetHandleId(t),0,u)
        call SaveEffectHandle(TF45_Gate,h,1,AddSpecialEffect("war3mapImported\\TFGateway.mdx",GetUnitX(u),GetUnitY(u)))
        call SaveEffectHandle(TF45_Gate,h,2,AddSpecialEffect("war3mapImported\\TFGateway.mdx",x,y))
        call SaveEffectHandle(TF45_Gate,h,3,AddSpecialEffectTarget("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportCaster.mdl",u,"origin"))
        call SetUnitAnimation(u,"spell")
        call TimerStart(t,.03,true,function TF45_GateTick)
    endif
    set t=null
    set u=null
endfunction

function TF45_GateEnd takes nothing returns nothing
    if GetSpellAbilityId()=='ATfc' then
        call TF45_GateClear(GetTriggerUnit())
    endif
endfunction

function TF45_GateInit takes nothing returns nothing
    local trigger t=CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SPELL_CHANNEL)
    call TriggerAddAction(t,function TF45_GateStart)
    set t=CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SPELL_ENDCAST)
    call TriggerAddAction(t,function TF45_GateEnd)
    set t=null
endfunction
