// Per-target wound ownership. No PauseUnit, forced orders, position correction,
// broad dispel, or shared stock net buff. 40 Hz gives exact 0.20 / 2.20 timings.
function MW_Clear takes timer t returns nothing
    local integer h = GetHandleId(t)
    local unit u = LoadUnitHandle(MW_Hash, h, 0)
    local unit dummy = LoadUnitHandle(MW_Hash, h, 4)
    if LoadTimerHandle(MW_Hash, GetHandleId(u), 0) == t then
        call RemoveSavedHandle(MW_Hash, GetHandleId(u), 0)
        call UnitRemoveAbility(u, 'BMwR')
        call UnitRemoveAbility(u, 'BMwS')
    endif
    if dummy != null then
        call RemoveUnit(dummy)
    endif
    set dummy = LoadUnitHandle(MW_Hash, h, 5)
    if dummy != null then
        call RemoveUnit(dummy)
    endif
    call FlushChildHashtable(MW_Hash, h)
    call PauseTimer(t)
    call DestroyTimer(t)
    set dummy = null
    set u = null
endfunction

function MW_Tick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit u = LoadUnitHandle(MW_Hash, h, 0)
    local integer ticks = LoadInteger(MW_Hash, h, 2) + 1
    local unit dummy
    if not FS_Alive(u) or GetOwningPlayer(u) != LoadPlayerHandle(MW_Hash, h, 1) or IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) or BlzIsUnitInvulnerable(u) or LoadTimerHandle(MW_Hash, GetHandleId(u), 0) != t then
        call MW_Clear(t)
    elseif ticks >= 88 then
        call MW_Clear(t)
    elseif ticks >= 4 and GetUnitAbilityLevel(u, 'BMwS') == 0 then
        // A genuine dispel cleanses the wound; haste itself is not a dispel.
        // Allow four ticks for the initial native instant cast to complete.
        call MW_Clear(t)
    else
        call SaveInteger(MW_Hash, h, 2, ticks)
        // Restrict this to the speed-scroll buff; preserve Bloodlust and others.
        call UnitRemoveAbility(u, 'Bspe')
        if ticks == 8 then
            set dummy = LoadUnitHandle(MW_Hash, h, 4)
            if dummy != null then
                call RemoveUnit(dummy)
                call RemoveSavedHandle(MW_Hash, h, 4)
            endif
            call UnitRemoveAbility(u, 'BMwR')
        endif
    endif
    set dummy = null
    set u = null
    set t = null
endfunction

function MW_Control takes unit source, unit target, integer abilityId, string order returns unit
    local unit dummy = CreateUnit(GetOwningPlayer(source), 'dmmy', GetUnitX(target), GetUnitY(target), 0.0)
    local unit result
    call BlzSetUnitRealField(dummy, UNIT_RF_CAST_POINT, 0.0)
    call BlzSetUnitRealField(dummy, UNIT_RF_CAST_BACK_SWING, 0.0)
    call UnitAddAbility(dummy, abilityId)
    if IssueTargetOrder(dummy, order, target) then
        call UnitApplyTimedLife(dummy, 'BTLF', 3.0)
        set result = dummy
    else
        call RemoveUnit(dummy)
        set result = null
    endif
    set dummy = null
    return result
endfunction

function MW_Start takes unit source, unit target returns nothing
    local timer t = LoadTimerHandle(MW_Hash, GetHandleId(target), 0)
    local integer h
    local unit slow
    local unit root
    if t != null then
        call MW_Clear(t)
    endif
    // A fresh hit refreshes one wound instead of stacking slows or timers.
    call UnitRemoveAbility(target, 'Bspe')
    set slow = MW_Control(source, target, 'AMwS', "slow")
    if slow != null then
        set root = MW_Control(source, target, 'AMwR', "ensnare")
        set t = CreateTimer()
        set h = GetHandleId(t)
        call SaveTimerHandle(MW_Hash, GetHandleId(target), 0, t)
        call SaveUnitHandle(MW_Hash, h, 0, target)
        call SavePlayerHandle(MW_Hash, h, 1, GetOwningPlayer(target))
        call SaveInteger(MW_Hash, h, 2, 0)
        call SaveUnitHandle(MW_Hash, h, 4, root)
        call SaveUnitHandle(MW_Hash, h, 5, slow)
        call TimerStart(t, 0.025, true, function MW_Tick)
    endif
    set root = null
    set slow = null
    set t = null
endfunction

function MW_Impact takes unit target returns nothing
    local sound hit = CreateSoundFromLabel("MetalMediumChopFlesh", false, true, true, 0, 0)
    local effect blood = AddSpecialEffectTarget("Objects\\Spawnmodels\\Human\\HumanBlood\\HumanBloodLarge0.mdl", target, "chest")
    call BlzSetSpecialEffectScale(blood, 0.65)
    call DestroyEffect(blood)
    call SetSoundChannel(hit, 5)
    call SetSoundVolume(hit, 115)
    call SetSoundDistances(hit, 300.0, 1800.0)
    call SetSoundDistanceCutoff(hit, 2200.0)
    call SetSoundPosition(hit, GetUnitX(target), GetUnitY(target), DK_GroundZ(GetUnitX(target), GetUnitY(target)) + 70.0)
    call StartSound(hit)
    call KillSoundWhenDone(hit)
    set blood = null
    set hit = null
endfunction
