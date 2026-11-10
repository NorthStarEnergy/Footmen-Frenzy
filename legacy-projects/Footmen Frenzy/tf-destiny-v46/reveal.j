function TF46_RevealEnd takes nothing returns nothing
    local timer t=GetExpiredTimer()
    local integer h=GetHandleId(t)
    local unit c=LoadUnitHandle(TF46_H,h,0)
    local group g=LoadGroupHandle(TF46_H,h,1)
    local fogmodifier fog=LoadFogModifierHandle(TF46_H,h,2)
    local unit u
    loop
        set u=FirstOfGroup(g)
        exitwhen u==null
        call GroupRemoveUnit(g,u)
        call RemoveUnit(u)
    endloop
    call DestroyGroup(g)
    call FogModifierStop(fog)
    call DestroyFogModifier(fog)
    call UnitRemoveAbility(c,'ATfc')
    call BlzUnitHideAbility(c,'ATfb',false)
    call RemoveSavedHandle(TF46_H,GetHandleId(c),0)
    call FlushChildHashtable(TF46_H,h)
    call DestroyTimer(t)
    set c=null
    set g=null
    set fog=null
    set t=null
    set u=null
endfunction

function TFP_destiny___c takes nothing returns boolean
    local unit c=GetTriggerUnit()
    local unit u
    local player p=GetOwningPlayer(c)
    local integer rank=GetUnitAbilityLevel(c,'ATfb')
    local real duration=10.
    local rect bounds
    local real x
    local real y
    local timer t
    local integer h
    local group g
    local fogmodifier fog
    if GetSpellAbilityId()=='ATfb' and not HaveSavedHandle(TF46_H,GetHandleId(c),0) then
        if rank==2 then
            set duration=13.
        elseif rank>=3 then
            set duration=15.
        endif
        set bounds=GetWorldBounds()
        set t=CreateTimer()
        set h=GetHandleId(t)
        set g=CreateGroup()
        set fog=CreateFogModifierRect(p,FOG_OF_WAR_VISIBLE,bounds,true,false)
        call FogModifierStart(fog)
        set x=GetRectMinX(bounds)+900.
        loop
            exitwhen x>GetRectMaxX(bounds)+900.
            set y=GetRectMinY(bounds)+900.
            loop
                exitwhen y>GetRectMaxY(bounds)+900.
                set u=CreateUnit(p,'ht46',x,y,0.)
                call GroupAddUnit(g,u)
                set y=y+1800.
            endloop
            set x=x+1800.
        endloop
        call SaveUnitHandle(TF46_H,h,0,c)
        call SaveGroupHandle(TF46_H,h,1,g)
        call SaveFogModifierHandle(TF46_H,h,2,fog)
        call SaveTimerHandle(TF46_H,GetHandleId(c),0,t)
        call BlzUnitHideAbility(c,'ATfb',true)
        call UnitAddAbility(c,'ATfc')
        call TimerStart(t,duration,false,function TF46_RevealEnd)
        call RemoveRect(bounds)
    endif
    set c=null
    set u=null
    set p=null
    set bounds=null
    set t=null
    set g=null
    set fog=null
    return false
endfunction

function TFP_destiny___gateC takes nothing returns boolean
    local unit c=GetTriggerUnit()
    local integer h=GetHandleId(c)
    local real x=LoadReal(TF45_Gate,h,5)
    local real y=LoadReal(TF45_Gate,h,6)
    if GetSpellAbilityId()=='ATfc' and HaveSavedHandle(TF45_Gate,h,0) and TFP_TF_Alive(c) then
        if not IsTerrainPathable(x,y,PATHING_TYPE_WALKABILITY) then
            call SetUnitPosition(c,x,y)
            call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl",GetUnitX(c),GetUnitY(c)))
            call UnitRemoveAbility(c,'ATfc')
            call BlzUnitHideAbility(c,'ATfb',false)
        else
            call DisplayTextToPlayer(GetOwningPlayer(c),0.,0.,"Gate requires a walkable destination.")
        endif
    endif
    set c=null
    return false
endfunction
