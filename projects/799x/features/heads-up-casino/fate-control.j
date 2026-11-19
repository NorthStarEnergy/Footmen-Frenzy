// Capture instant card casts on effect, and swap the command card only once
// Warcraft has released the casting order. Spell effects may be interrupted
// after committing, so both completion and cancellation end at SPELL_ENDCAST.
function TF_IsCardOrder takes integer id returns boolean
    return id == 'ATf2' or id == 'ATf3' or id == 'ATf4' or id == 'ATf5' or id == 'ATf6' or id == 'ATf7' or id == 'ATf8'
endfunction

function TF_CardChannel takes nothing returns nothing
    if TF_IsCardOrder(GetSpellAbilityId()) then
        call SaveInteger(TF_PendingCard,GetHandleId(GetTriggerUnit()),3,GetSpellAbilityId())
    endif
endfunction

function TF_CardEffect takes nothing returns nothing
    local unit c = GetTriggerUnit()
    local integer id = GetSpellAbilityId()
    local integer k = GetHandleId(c)
    if TF_IsCardOrder(id) then
        call SaveInteger(TF_PendingCard,k,0,id)
        call SaveUnitHandle(TF_PendingCard,k,1,GetSpellTargetUnit())
    endif
    set c = null
endfunction

function TF_ApplyCardCast takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer k = GetHandleId(t)
    local unit c = LoadUnitHandle(TF_PendingCard,k,0)
    local unit target = LoadUnitHandle(TF_PendingCard,k,1)
    local integer id = LoadInteger(TF_PendingCard,k,2)
    call FlushChildHashtable(TF_PendingCard,k)
    call RemoveSavedBoolean(TF_PendingCard,GetHandleId(c),2)
    call DestroyTimer(t)
    if TFP_TF_Alive(c) then
        call TF33_Cast(c,target,id)
    endif
    set c = null
    set target = null
    set t = null
endfunction

function TF_CardEnd takes nothing returns nothing
    local unit c = GetTriggerUnit()
    local integer k = GetHandleId(c)
    local integer id = GetSpellAbilityId()
    local timer t
    local integer key
    if id != 0 and LoadInteger(TF_PendingCard,k,3) == id then
        call RemoveSavedInteger(TF_PendingCard,k,3)
    endif
    if id != 0 and LoadInteger(TF_PendingCard,k,0) == id then
        set t = CreateTimer()
        set key = GetHandleId(t)
        call SaveUnitHandle(TF_PendingCard,key,0,c)
        call SaveUnitHandle(TF_PendingCard,key,1,LoadUnitHandle(TF_PendingCard,k,1))
        call SaveInteger(TF_PendingCard,key,2,id)
        call FlushChildHashtable(TF_PendingCard,k)
        call SaveBoolean(TF_PendingCard,k,2,true)
        call TimerStart(t,0.0,false,function TF_ApplyCardCast)
    endif
    set t = null
    set c = null
endfunction
