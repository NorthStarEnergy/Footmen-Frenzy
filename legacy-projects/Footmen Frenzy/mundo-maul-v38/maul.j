function MM_IsFlipTarget takes unit v returns boolean
    return IsUnitType(v, UNIT_TYPE_HERO) or GetPlayerId(GetOwningPlayer(v)) >= 12 or LoadBoolean(MD_Types, GetUnitTypeId(v), 1)
endfunction

function MM_CanFlip takes unit u, unit v returns boolean
    return v != null and MM_IsFlipTarget(v) and FS_Enemy(v, GetOwningPlayer(u)) and not IsUnitType(v, UNIT_TYPE_MECHANICAL) and not IsUnitHidden(v) and not IsUnitLoaded(v) and GetUnitAbilityLevel(v, 'A0IL') == 0 and not LoadBoolean(MU_Hash, GetHandleId(v), 39)
endfunction

function MM_CanCast takes unit u, unit v returns boolean
    if v == null or not FS_Alive(u) or IsUnitIllusion(u) then
        return false
    endif
    if LoadTimerHandle(MM_Hash, GetHandleId(u), 1) != null then
        return false
    endif
    if MM_IsFlipTarget(v) then
        return MM_CanFlip(u, v)
    endif
    return LoadUnitHandle(MD_Hash, GetHandleId(u), 1) == null and MD_Eligible(u, v)
endfunction

function MM_Timeout takes nothing returns nothing
    local timer t=GetExpiredTimer()
    local integer h=GetHandleId(t)
    local unit u=LoadUnitHandle(MM_Hash, h, 1)
    if LoadTimerHandle(MM_Hash, GetHandleId(u), 1) == t then
        call RemoveSavedHandle(MM_Hash, GetHandleId(u), 1)
        if GetUnitTypeId(u) != 0 then
            call BlzEndUnitAbilityCooldown(u, 'AMu3')
        endif
    endif
    call FlushChildHashtable(MM_Hash, h)
    call DestroyTimer(t)
    set u=null
    set t=null
endfunction

function MM_DevourReady takes unit u, unit v returns boolean
    local timer t=LoadTimerHandle(MM_Hash, GetHandleId(u), 1)
    local integer h=GetHandleId(t)
    local boolean ready=t != null and LoadUnitHandle(MM_Hash, h, 2) == v and LoadPlayerHandle(MM_Hash, h, 3) == GetOwningPlayer(u) and FS_Alive(u) and LoadUnitHandle(MD_Hash, GetHandleId(u), 1) == null and MD_Eligible(u, v)
    set t=null
    return ready
endfunction

function MM_ExecuteDevour takes nothing returns nothing
    local timer t=GetExpiredTimer()
    local integer h=GetHandleId(t)
    local unit u=LoadUnitHandle(MM_Hash, h, 1)
    local unit v=LoadUnitHandle(MM_Hash, h, 2)
    local integer rank=LoadInteger(MM_Hash, h, 4)
    if MM_DevourReady(u, v) then
        call UnitAddAbility(u, 'AMdv')
        call SetUnitAbilityLevel(u, 'AMdv', rank)
        call BlzUnitHideAbility(u, 'AMdv', true)
        call UnitAddAbility(u, 'AMdc')
        call SetUnitAbilityLevel(u, 'AMdc', rank)
        call BlzUnitHideAbility(u, 'AMdc', true)
        // Delay until the visible Channel effect has completed. Native Devour
        // remains on Mundo himself so cargo, kill credit and XP stay native.
        if IssueTargetOrder(u, "devour", v) then
            call TimerStart(t, 1.0, false, function MM_Timeout)
        else
            call MM_Timeout()
        endif
    else
        call MM_Timeout()
    endif
    set u=null
    set v=null
    set t=null
endfunction

function MM_Cast takes unit u, unit v, integer rank returns nothing
    local timer t
    local integer h
    if not MM_CanCast(u, v) then
        call MD_Reject(u)
        call BlzEndUnitAbilityCooldown(u, 'AMu3')
        return
    endif
    if MM_IsFlipTarget(v) then
        if not MU_Fling(u, v, rank) then
            call BlzEndUnitAbilityCooldown(u, 'AMu3')
        endif
    else
        set t=CreateTimer()
        set h=GetHandleId(t)
        call SaveTimerHandle(MM_Hash, GetHandleId(u), 1, t)
        call SaveUnitHandle(MM_Hash, h, 1, u)
        call SaveUnitHandle(MM_Hash, h, 2, v)
        call SavePlayerHandle(MM_Hash, h, 3, GetOwningPlayer(u))
        call SaveInteger(MM_Hash, h, 4, rank)
        call TimerStart(t, 0.0, false, function MM_ExecuteDevour)
    endif
    set t=null
endfunction
