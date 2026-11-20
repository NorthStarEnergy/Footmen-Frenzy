function DR_Stop takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer immunity = 'ADri'
    local integer haste = 'ADrh'
    local integer cleave = 'ADrc'
    local integer refusal = 'ADrd'
    local integer buffId = 'BDrh'
    if GetUnitTypeId(u) == 'HMu1' then
        set immunity = 'AMui'
        set haste = 'AMuh'
        set cleave = 'AMuc'
        set refusal = 'AMud'
        set buffId = 'BMuh'
    endif
    call UnitRemoveAbility(u, immunity)
    call UnitRemoveAbility(u, haste)
    call UnitRemoveAbility(u, cleave)
    call UnitRemoveAbility(u, refusal)
    call UnitRemoveAbility(u, buffId)
    call SetUnitScale(u, 1.0, 1.0, 1.0)
    call SetUnitVertexColor(u, 255, 255, 255, 255)
    call RemoveSavedInteger(DK_Hash, h, -40)
endfunction

function DR_Start takes unit u, integer rank returns nothing
    local integer i = LoadInteger(DK_Hash, GetHandleId(u), -40)
    local integer immunity = 'ADri'
    local integer haste = 'ADrh'
    local integer cleave = 'ADrc'
    local integer refusal = 'ADrd'
    local integer buffId = 'BDrh'
    if GetUnitTypeId(u) == 'HMu1' then
        set immunity = 'AMui'
        set haste = 'AMuh'
        set cleave = 'AMuc'
        set refusal = 'AMud'
        set buffId = 'BMuh'
    endif
    // Never refresh or escape an already-triggered death sentence.
    if i != 0 then
        return
    endif
    set i = DK_New(10, u)
    if i == 0 then
        return
    endif
    call SaveInteger(DK_Hash, GetHandleId(u), -40, i)
    set DK_End[i] = DK_Now+12.0+3.0*rank
    set DK_Damage[i] = 0.02+0.01*rank
    set DK_Stacks[i] = 0
    call UnitAddAbility(u, immunity)
    call UnitAddAbility(u, haste)
    call UnitAddAbility(u, cleave)
    call UnitAddAbility(u, refusal)
    call SetUnitAbilityLevel(u, haste, rank)
    call SetUnitAbilityLevel(u, cleave, rank)
    call BlzUnitHideAbility(u, immunity, true)
    call BlzUnitHideAbility(u, haste, true)
    call BlzUnitHideAbility(u, cleave, true)
    call SetUnitScale(u, 1.4, 1.4, 1.4)
    call SetUnitVertexColor(u, 255, 65, 65, 255)
    set DK_FX[i] = AddSpecialEffectTarget("Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl", u, "origin")
endfunction

function FF_LearnTip_AMu3 takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'AMu3')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 1|nFlip heroes and creeps behind you for 50 damage, or swallow a lesser unit. Digestion heals you and restores 200 health to nearby allies when it finishes.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 4|nFlip heroes and creeps behind you for 80 damage, or swallow a lesser unit. Digestion heals you and restores 250 health to nearby allies when it finishes.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 7|nFlip heroes and creeps behind you for 110 damage, or swallow a lesser unit. Digestion heals you and restores 300 health to nearby allies when it finishes.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 10|nFlip heroes and creeps behind you for 140 damage, or swallow a lesser unit. Digestion heals you and restores 350 health to nearby allies when it finishes.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 13|nFlip heroes and creeps behind you for 170 damage, or swallow a lesser unit. Digestion heals you and restores 400 health to nearby allies when it finishes.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 16|nFlip heroes and creeps behind you for 200 damage, or swallow a lesser unit. Digestion heals you and restores 450 health to nearby allies when it finishes.", 0)
    endif
endfunction

function FF_LearnTip_AMu1 takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'AMu1')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 80 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 120 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 160 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 200 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 240 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 280 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 0)
    endif
endfunction

function FF_LearnTip_AMu2 takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'AMu2')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 35-70 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 50-100 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 65-130 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 80-160 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 95-190 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 110-220 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 0)
    endif
endfunction

function FF_LearnTip_AMu4 takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'AMu4')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('AMu4', "Learn Undying - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu4', "Spend 20% of current health. Transform for 15s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('AMu4', "Learn Undying - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu4', "Spend 20% of current health. Transform for 18s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 0)
    elseif rank >= 2 then
        call BlzSetAbilityResearchTooltip('AMu4', "Learn Undying - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('AMu4', "Spend 20% of current health. Transform for 21s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 0)
    endif
endfunction

function MQ_Land takes integer i, real x, real y returns nothing
    local unit u = LoadUnitHandle(MQ_Hash, i, 1)
    local effect fx
    local effect ring
    if FS_Alive(u) and GetOwningPlayer(u) == LoadPlayerHandle(MQ_Hash, i, 7) and LoadInteger(MU_Hash, GetHandleId(u), 20) == i and not LoadBoolean(MQ_Hash, i, 8) then
        call SaveBoolean(MQ_Hash, i, 8, true)
        call SaveReal(MQ_Hash, i, 4, 3.0)
        call SaveReal(MQ_Hash, i, 5, x)
        call SaveReal(MQ_Hash, i, 6, y)
        set fx = AddSpecialEffect("war3mapImported\\Axe Missile-Small.mdx", x, y)
        call BlzSetSpecialEffectScale(fx, 3.5)
        call BlzSetSpecialEffectZ(fx, DK_GroundZ(x, y)+55.0)
        call BlzSetSpecialEffectTimeScale(fx, 0.0)
        call SaveEffectHandle(MQ_Hash, i, 3, fx)
        set ring = AddSpecialEffect("buildings\\other\\CircleOfPower\\CircleOfPower.mdl", x, y)
        call BlzSetSpecialEffectScale(ring, 0.8)
        if LoadBoolean(MQ_Hash, i, 11) then
            call BlzSetSpecialEffectColor(fx, 255, 65, 45)
            call BlzSetSpecialEffectColor(ring, 255, 40, 25)
        else
            call BlzSetSpecialEffectColor(ring, 255, 210, 70)
        endif
        call SaveEffectHandle(MQ_Hash, i, 13, ring)
    endif
    set ring = null
    set fx = null
    set u = null
endfunction

function MQ_Finish takes nothing returns nothing
    call MQ_Land(udg_MissileData, GetLocationX(udg_MissilePosition), GetLocationY(udg_MissilePosition))
    set udg_MissileDestroy = true
endfunction

function MQ_Free takes integer i returns nothing
    local unit u = LoadUnitHandle(MQ_Hash, i, 1)
    local timer t = LoadTimerHandle(MQ_Hash, i, 2)
    if LoadInteger(MU_Hash, GetHandleId(u), 20) == i then
        call RemoveSavedInteger(MU_Hash, GetHandleId(u), 20)
    endif
    call DestroyEffect(LoadEffectHandle(MQ_Hash, i, 3))
    call DestroyEffect(LoadEffectHandle(MQ_Hash, i, 13))
    call PauseTimer(t)
    call DestroyTimer(t)
    call FlushChildHashtable(MQ_Hash, i)
    set t = null
    set u = null
endfunction

function MQ_ClearLoaded takes unit u returns nothing
    local integer h = GetHandleId(u)
    call DestroyEffect(LoadEffectHandle(MU_Hash, h, 61))
    call RemoveSavedHandle(MU_Hash, h, 61)
    call RemoveSavedBoolean(MU_Hash, h, 60)
endfunction

function MQ_LoadBloodied takes unit u returns nothing
    local integer h = GetHandleId(u)
    local effect fx
    call MQ_ClearLoaded(u)
    call SaveBoolean(MU_Hash, h, 60, true)
    set fx = AddSpecialEffectTarget("Abilities\\Spells\\Orc\\Bloodlust\\BloodlustTarget.mdl", u, "weapon right")
    call BlzSetSpecialEffectScale(fx, 1.4)
    call BlzSetSpecialEffectColor(fx, 255, 50, 35)
    call SaveEffectHandle(MU_Hash, h, 61, fx)
    call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Items\\AIhe\\AIheTarget.mdl", u, "origin"))
    set fx = null
endfunction

function MQ_GroundTick takes nothing returns nothing
    local integer i = GetHandleId(GetExpiredTimer())
    local unit u = LoadUnitHandle(MQ_Hash, i, 1)
    local real life = LoadReal(MQ_Hash, i, 4) - 0.03125
    local real x = LoadReal(MQ_Hash, i, 5)
    local real y = LoadReal(MQ_Hash, i, 6)
    if life <= 0.0 or not FS_Alive(u) or GetOwningPlayer(u) != LoadPlayerHandle(MQ_Hash, i, 7) or LoadInteger(MU_Hash, GetHandleId(u), 20) != i then
        call MQ_Free(i)
    elseif Pow(GetUnitX(u)-x, 2.0)+Pow(GetUnitY(u)-y, 2.0) <= 10000.0 then
        if LoadBoolean(MQ_Hash, i, 11) then
            call MQ_LoadBloodied(u)
        endif
        call BlzEndUnitAbilityCooldown(u, 'AMu1')
        call SaveReal(MU_Hash, GetHandleId(u), 21, MU_Now+2.0)
        call UnitAddAbility(u, 'AMqh')
        call BlzUnitHideAbility(u, 'AMqh', true)
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Items\\AIhe\\AIheTarget.mdl", u, "origin"))
        call MQ_Free(i)
    else
        call BlzSetSpecialEffectZ(LoadEffectHandle(MQ_Hash, i, 3), DK_GroundZ(x, y)+55.0+12.0*Sin(life*6.0))
        call SaveReal(MQ_Hash, i, 4, life)
    endif
    set u = null
endfunction

function MQ_Remove takes nothing returns nothing
    local integer i = udg_MissileData
    if LoadBoolean(MQ_Hash, i, 8) then
        call TimerStart(LoadTimerHandle(MQ_Hash, i, 2), 0.03125, true, function MQ_GroundTick)
    else
        call MQ_Free(i)
    endif
endfunction

function MU_CleaverFilter takes nothing returns boolean
    return FS_Enemy(udg_MissileHitUnit, udg_MissileOwner) and not IsUnitType(udg_MissileHitUnit, UNIT_TYPE_FLYING) and not IsUnitType(udg_MissileHitUnit, UNIT_TYPE_MECHANICAL) and IsUnitVisible(udg_MissileHitUnit, udg_MissileOwner)
endfunction

function MC_Now takes nothing returns real
    return MU_Now + TimerGetElapsed(MU_Timer)
endfunction

function MD_Resistant takes unit v returns boolean
    if GetUnitAbilityLevel(v, 'A038') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A03T') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A04O') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A04P') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A04X') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A071') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A09R') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A09Z') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0C0') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0F9') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0FA') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0FB') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0GF') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0JT') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0JU') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0K8') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0MK') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0QT') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0T0') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0US') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0UT') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'A0WD') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'AIsr') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'AMur') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'Aegr') > 0 then
        return true
    endif
    if GetUnitAbilityLevel(v, 'Arsk') > 0 then
        return true
    endif
    return false
endfunction

function MD_Eligible takes unit u, unit v returns boolean
    if v == null or v == u or not FS_Alive(v) or IsUnitHidden(v) or IsUnitLoaded(v) or IsUnitIllusion(v) or BlzIsUnitInvulnerable(v) then
        return false
    endif
    if IsUnitType(v, UNIT_TYPE_HERO) or IsUnitType(v, UNIT_TYPE_STRUCTURE) or IsUnitType(v, UNIT_TYPE_FLYING) or IsUnitType(v, UNIT_TYPE_MECHANICAL) or IsUnitType(v, UNIT_TYPE_MAGIC_IMMUNE) or IsUnitType(v, UNIT_TYPE_RESISTANT) then
        return false
    endif
    if GetPlayerId(GetOwningPlayer(v)) >= 12 or LoadBoolean(MD_Types, GetUnitTypeId(v), 1) or GetUnitAbilityLevel(v, 'A0IL') > 0 or GetUnitAbilityLevel(v, 'Aloc') > 0 then
        return false
    endif
    return not MD_Resistant(v)
endfunction

function MD_Reject takes unit u returns nothing
    call IssueImmediateOrder(u, "stop")
    call DisplayTimedTextToPlayer(GetOwningPlayer(u), 0.0, 0.0, 2.0, "|cffff6060Maul: flip an eligible enemy hero or creep, or devour an eligible organic ground unit. Finish your meal before eating another unit. Cannot affect Colossals, flying, mechanical, magic-immune or invulnerable targets; spell-resistant units cannot be eaten.|r")
endfunction

function MD_Start takes unit u, unit v, integer rank returns nothing
    local integer h = GetHandleId(u)
    if LoadUnitHandle(MD_Hash, h, 1) != null or v == null then
        call MD_Reject(u)
        call BlzEndUnitAbilityCooldown(u, 'AMu3')
        return
    endif
    call SaveReal(MD_Hash, h, 26, 35.0+15.0*rank)
    call SaveUnitHandle(MD_Hash, h, 1, v)
    call SaveInteger(MD_Hash, h, 2, rank)
    call SavePlayerHandle(MD_Hash, h, 3, GetOwningPlayer(u))
    call SaveReal(MD_Hash, h, 4, MU_Now+1.0)
    call SaveUnitHandle(MD_Hash, GetHandleId(v), 10, u)
endfunction

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

function MM_DevourReady takes unit u, unit v returns boolean
    local timer t=LoadTimerHandle(MM_Hash, GetHandleId(u), 1)
    local integer h=GetHandleId(t)
    local boolean ready=t != null and LoadUnitHandle(MM_Hash, h, 2) == v and LoadPlayerHandle(MM_Hash, h, 3) == GetOwningPlayer(u) and FS_Alive(u) and LoadUnitHandle(MD_Hash, GetHandleId(u), 1) == null and MD_Eligible(u, v)
    set t=null
    return ready
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

function MM_ExecuteDevour takes nothing returns nothing
    local timer t=GetExpiredTimer()
    local integer h=GetHandleId(t)
    local unit u=LoadUnitHandle(MM_Hash, h, 1)
    local unit v=LoadUnitHandle(MM_Hash, h, 2)
    local integer rank=LoadInteger(MM_Hash, h, 4)
    if MM_DevourReady(u, v) then
        call UnitAddAbility(u, 'AMdv')
        call SetUnitAbilityLevel(u, 'AMdv', rank)
        call BlzEndUnitAbilityCooldown(u, 'AMdv')
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

function MU_FlingSafe takes real x, real y, integer cliff, real radius returns boolean
    local integer i = 0
    local real px
    local real py
    if x-radius < GetRectMinX(bj_mapInitialPlayableArea) or x+radius > GetRectMaxX(bj_mapInitialPlayableArea) or y-radius < GetRectMinY(bj_mapInitialPlayableArea) or y+radius > GetRectMaxY(bj_mapInitialPlayableArea) then
        return false
    endif
    if GetTerrainCliffLevel(x, y) != cliff or IsTerrainPathable(x, y, PATHING_TYPE_WALKABILITY) then
        return false
    endif
    loop
        exitwhen i >= 8
        set px = x + radius*Cos(I2R(i)*bj_PI/4.0)
        set py = y + radius*Sin(I2R(i)*bj_PI/4.0)
        if GetTerrainCliffLevel(px, py) != cliff or IsTerrainPathable(px, py, PATHING_TYPE_WALKABILITY) then
            return false
        endif
        set i = i + 1
    endloop
    return true
endfunction

function MU_FlingTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit target = LoadUnitHandle(MU_Hash, h, 31)
    local unit caster = LoadUnitHandle(MU_Hash, h, 32)
    local real p = RMinBJ(1.0, LoadReal(MU_Hash, h, 33) + 0.0625)
    local real x = LoadReal(MU_Hash, h, 34) + p * LoadReal(MU_Hash, h, 36)
    local real y = LoadReal(MU_Hash, h, 35) + p * LoadReal(MU_Hash, h, 37)
    local boolean alive = FS_Alive(target) and FS_Alive(caster)
    local boolean safe = alive and MU_FlingSafe(x, y, LoadInteger(MU_Hash, h, 41), LoadReal(MU_Hash, h, 42))
    if safe then
        call SetUnitX(target, x)
        call SetUnitY(target, y)
        call SetUnitFlyHeight(target, LoadReal(MU_Hash, h, 38) + 840.0*p*(1.0-p), 0.0)
    endif
    if not alive or not safe or p >= 1.0 then
        if target != null and GetUnitTypeId(target) != 0 then
            call SetUnitFlyHeight(target, LoadReal(MU_Hash, h, 38), 0.0)
            call BlzPauseUnitEx(target, false)
            call RemoveSavedBoolean(MU_Hash, GetHandleId(target), 39)
            if alive then
                call FS_Hit(caster, target, LoadReal(MU_Hash, h, 40))
                call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Orc\\WarStomp\\WarStompTarget.mdl", target, "origin"))
                call DestroyEffect(AddSpecialEffectTarget("Objects\\Spawnmodels\\Human\\HumanBlood\\HumanBloodLarge0.mdl", target, "chest"))
            endif
        endif
        call FlushChildHashtable(MU_Hash, h)
        call DestroyTimer(t)
    else
        call SaveReal(MU_Hash, h, 33, p)
    endif
    set target = null
    set caster = null
    set t = null
endfunction

function MU_Fling takes unit caster, unit target, integer rank returns boolean
    local real x
    local real y
    local real angle
    local real dx
    local real dy
    local real distance
    local real step
    local real progress
    local real safeProgress = 0.0
    local real radius
    local integer cliff
    local timer t
    local integer h
    if target == null or not FS_Enemy(target, GetOwningPlayer(caster)) or IsUnitType(target, UNIT_TYPE_FLYING) or IsUnitType(target, UNIT_TYPE_MECHANICAL) or LoadBoolean(MU_Hash, GetHandleId(target), 39) then
        return false
    endif
    set x = GetUnitX(target)
    set y = GetUnitY(target)
    set cliff = GetTerrainCliffLevel(x, y)
    set radius = RMaxBJ(16.0, BlzGetUnitCollisionSize(target))
    set angle = Atan2(y - GetUnitY(caster), x - GetUnitX(caster))
    set distance = 200.0 + 30.0*I2R(IMaxBJ(1, IMinBJ(6, rank))-1)
    set dx = GetUnitX(caster) - distance*Cos(angle) - x
    set dy = GetUnitY(caster) - distance*Sin(angle) - y
    set distance = SquareRoot(dx*dx+dy*dy)
    if distance < 1.0 or not MU_FlingSafe(x, y, cliff, radius) then
        return false
    endif
    // 16-unit sampling prevents skipping a 32-unit wall/pathing cell.
    set step = 16.0/distance
    set progress = RMinBJ(1.0, step)
    loop
        exitwhen not MU_FlingSafe(x+progress*dx, y+progress*dy, cliff, radius)
        set safeProgress = progress
        exitwhen progress >= 1.0
        set progress = RMinBJ(1.0, progress+step)
    endloop
    if safeProgress*distance < 16.0 then
        return false
    endif
    set t = CreateTimer()
    set h = GetHandleId(t)
    call SaveUnitHandle(MU_Hash, h, 31, target)
    call SaveUnitHandle(MU_Hash, h, 32, caster)
    call SaveReal(MU_Hash, h, 33, 0.0)
    call SaveReal(MU_Hash, h, 34, x)
    call SaveReal(MU_Hash, h, 35, y)
    call SaveReal(MU_Hash, h, 36, dx*safeProgress)
    call SaveReal(MU_Hash, h, 37, dy*safeProgress)
    call SaveReal(MU_Hash, h, 38, GetUnitFlyHeight(target))
    call SaveReal(MU_Hash, h, 40, 50.0+30.0*(rank-1))
    call SaveInteger(MU_Hash, h, 41, cliff)
    call SaveReal(MU_Hash, h, 42, radius)
    call SaveBoolean(MU_Hash, GetHandleId(target), 39, true)
    if GetUnitAbilityLevel(target, 'Amrf') == 0 then
        call UnitAddAbility(target, 'Amrf')
        call UnitRemoveAbility(target, 'Amrf')
    endif
    call BlzPauseUnitEx(target, true)
    call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilSpecialArt.mdl", target, "chest"))
    call TimerStart(t, 0.03125/1.05, true, function MU_FlingTick)
    set t = null
    return true
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

function MU_ClearFX takes integer h, integer key returns nothing
    if HaveSavedHandle(MU_Hash, h, key) then
        call DestroyEffect(LoadEffectHandle(MU_Hash, h, key))
        call RemoveSavedHandle(MU_Hash, h, key)
    endif
endfunction

function MU_BurnOff takes unit u returns nothing
    local integer h = GetHandleId(u)
    call SaveBoolean(MU_Hash, h, 1, false)
    call RemoveSavedReal(MU_Hash, h, 24)
    call RemoveSavedReal(MU_Hash, h, 25)
    call RemoveSavedReal(MU_Hash, h, 23)
    call UnitRemoveAbility(u, 'AMur')
    call MU_ClearFX(h, 6)
endfunction

function MC_Heat takes unit u returns real
    if not LoadBoolean(MU_Hash, GetHandleId(u), 1) then
        return 0.0
    endif
    return RMaxBJ(0.0, RMinBJ(1.0, (MC_Now() - LoadReal(MU_Hash, GetHandleId(u), 24)) / 10.0))
endfunction

function MC_Model takes real heat returns string
    return "Spells\\Mundo\\Cloud" + I2S(R2I(RMaxBJ(0.0, RMinBJ(1.0, heat)) * 20.0)) + ".mdx"
endfunction

function MU_PoisonTick takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit source = LoadUnitHandle(MU_Hash, h, 40)
    local unit victim = LoadUnitHandle(MU_Hash, h, 41)
    local integer left = LoadInteger(MU_Hash, h, 42)
    local integer rank = LoadInteger(MU_Hash, h, 43)
    if left > 0 and GetUnitTypeId(source) != 0 and FS_Alive(victim) and IsUnitEnemy(victim, GetOwningPlayer(source)) then
        call UnitDamageTarget(source, victim, LoadReal(MU_Hash, h, 50) * 0.5, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
        call SaveInteger(MU_Hash, h, 42, left - 1)
        call SaveReal(MU_Hash, h, 50, LoadReal(MU_Hash, h, 51))
        call SaveReal(MU_Hash, h, 51, LoadReal(MU_Hash, h, 52))
        call SaveReal(MU_Hash, h, 52, LoadReal(MU_Hash, h, 53))
        call SaveReal(MU_Hash, h, 53, 0.0)
    else
        if LoadTimerHandle(MU_Hash, GetHandleId(source), -GetHandleId(victim)) == t then
            call RemoveSavedHandle(MU_Hash, GetHandleId(source), -GetHandleId(victim))
        endif
        call FlushChildHashtable(MU_Hash, h)
        call DestroyTimer(t)
    endif
    set source = null
    set victim = null
    set t = null
endfunction

function MU_GasExpire takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer h = GetHandleId(t)
    local unit source = LoadUnitHandle(MU_Hash, h, 40)
    local unit victim
    local timer poison
    local integer rank = LoadInteger(MU_Hash, h, 43)
    local real damage = LoadReal(MU_Hash, h, 46)
    local integer slot
    local integer left = LoadInteger(MU_Hash, h, 42)
    local group g = CreateGroup()
    if left > 0 and GetUnitTypeId(source) != 0 then
        call GroupEnumUnitsInRange(g, LoadReal(MU_Hash, h, 44), LoadReal(MU_Hash, h, 45), 250.0, null)
        loop
            set victim = FirstOfGroup(g)
            exitwhen victim == null
            call GroupRemoveUnit(g, victim)
            if FS_Alive(victim) and IsUnitEnemy(victim, GetOwningPlayer(source)) and not IsUnitType(victim, UNIT_TYPE_FLYING) and not IsUnitType(victim, UNIT_TYPE_MECHANICAL) and not IsUnitType(victim, UNIT_TYPE_STRUCTURE) and not IsUnitType(victim, UNIT_TYPE_MAGIC_IMMUNE) then
                set poison = LoadTimerHandle(MU_Hash, GetHandleId(source), -GetHandleId(victim))
                if poison == null then
                    set poison = CreateTimer()
                    call SaveTimerHandle(MU_Hash, GetHandleId(source), -GetHandleId(victim), poison)
                    call SaveUnitHandle(MU_Hash, GetHandleId(poison), 40, source)
                    call SaveUnitHandle(MU_Hash, GetHandleId(poison), 41, victim)
                    call UnitDamageTarget(source, victim, damage * 0.5, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)
                    call TimerStart(poison, 0.5, true, function MU_PoisonTick)
                endif
                call SaveInteger(MU_Hash, GetHandleId(poison), 42, 4)
                call SaveInteger(MU_Hash, GetHandleId(poison), 43, rank)
                // Four pending half-second doses: strongest exposure wins each slot.
                // Weaker old clouds cannot overwrite a stronger dose or extend it forever.
                set slot = 50
                loop
                    exitwhen slot > 53
                    call SaveReal(MU_Hash, GetHandleId(poison), slot, RMaxBJ(damage, LoadReal(MU_Hash, GetHandleId(poison), slot)))
                    set slot = slot + 1
                endloop
            endif
        endloop
        call SaveInteger(MU_Hash, h, 42, left - 1)
    else
        call DestroyEffect(LoadEffectHandle(MU_Hash, h, 30))
        call DestroyEffect(LoadEffectHandle(MU_Hash, h, 31))
        call DestroyEffect(LoadEffectHandle(MU_Hash, h, 32))
        call FlushChildHashtable(MU_Hash, h)
        call DestroyTimer(t)
    endif
    call DestroyGroup(g)
    set g = null
    set source = null
    set victim = null
    set poison = null
    set t = null
endfunction

function MU_GasSpawn takes unit u, integer rank returns nothing
    local real heat = MC_Heat(u)
    local string model = MC_Model(heat)
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    local timer t = CreateTimer()
    local integer h = GetHandleId(t)
    local effect fx = AddSpecialEffect(model, x, y)
    call BlzSetSpecialEffectScale(fx, 1.5)
    call SaveEffectHandle(MU_Hash, h, 30, fx)
    set fx = AddSpecialEffect(model, x + 70.0, y)
    call BlzSetSpecialEffectScale(fx, 1.3)
    call SaveEffectHandle(MU_Hash, h, 31, fx)
    set fx = AddSpecialEffect(model, x - 70.0, y)
    call BlzSetSpecialEffectScale(fx, 1.3)
    call SaveEffectHandle(MU_Hash, h, 32, fx)
    call SaveUnitHandle(MU_Hash, h, 40, u)
    call SaveInteger(MU_Hash, h, 42, 6)
    call SaveInteger(MU_Hash, h, 43, rank)
    call SaveReal(MU_Hash, h, 46, (35.0 + 15.0 * (rank - 1)) * (1.0 + heat))
    call SaveReal(MU_Hash, h, 44, x)
    call SaveReal(MU_Hash, h, 45, y)
    call TimerStart(t, 0.5, true, function MU_GasExpire)
    set fx = null
    set t = null
endfunction

function MU_Launch takes unit u, integer rank, real tx, real ty returns nothing
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    local real angle = Atan2(ty-y, tx-x)
    local integer old = LoadInteger(MU_Hash, GetHandleId(u), 20)
    local timer t = CreateTimer()
    local integer i = GetHandleId(t)
    if old != 0 and LoadBoolean(MQ_Hash, old, 8) then
        call MQ_Free(old)
    endif
    call SaveBoolean(MQ_Hash, i, 12, LoadBoolean(MU_Hash, GetHandleId(u), 60))
    call MQ_ClearLoaded(u)
    call SaveInteger(MU_Hash, GetHandleId(u), 20, i)
    call SaveUnitHandle(MQ_Hash, i, 1, u)
    call SaveTimerHandle(MQ_Hash, i, 2, t)
    call SavePlayerHandle(MQ_Hash, i, 7, GetOwningPlayer(u))
    call SaveInteger(MQ_Hash, i, 9, rank)
    call SaveReal(MQ_Hash, i, 10, LoadReal(MU_Hash, GetHandleId(u), 22))
    if Pow(tx-x, 2.0)+Pow(ty-y, 2.0) < 1.0 then
        set angle = GetUnitFacing(u)*bj_DEGTORAD
    endif
    // Identical flight properties to Troll's Thunder Axe.
    set udg_MissileSource = u
    set udg_MissileOwner = GetOwningPlayer(u)
    set udg_MissileStart = Location(x, y)
    set udg_MissileFinish = Location(x+1100.0*Cos(angle), y+1100.0*Sin(angle))
    set udg_MissileModel = "war3mapImported\\Axe Missile-Small.mdx"
    set udg_MissileScale = 3.0
    set udg_MissileCollision = 75.0
    set udg_MissileStartZ = 90.0
    set udg_MissileFinishZ = 90.0
    set udg_MissileSpeed = 1100.0
    set udg_MissileVision = 300.0
    set udg_MissileData = i
    set udg_Missile_onHit = MU_CleaverHit
    set udg_Missile_onFinish = MQ_FinishTrigger
    set udg_Missile_onRemove = MQ_RemoveTrigger
    call TriggerExecute(gg_trg_MissileCreate)
    set t = null
endfunction

function MU_Pay takes unit u, real cost, integer spell returns boolean
    if GetWidgetLife(u) <= cost + 0.405 then
        call BlzEndUnitAbilityCooldown(u, spell)
        call DisplayTextToPlayer(GetOwningPlayer(u), 0.0, 0.0, "|cffff6060Mundo needs more health!|r")
        return false
    endif
    call SetWidgetLife(u, GetWidgetLife(u) - cost)
    return true
endfunction

function MU_ZeroResources takes unit u returns nothing
    local integer i = 0
    local integer id
    local integer amount
    local integer bit = 1
    if GetHeroInt(u,false) == 0 and GetHeroInt(u,true) == 0 and BlzGetUnitMaxMana(u) == 0 then
        return
    endif
    loop
        exitwhen i == 20
        if i < 10 then
            set id = 'AMi0' + i
        else
            set id = 'AMj0' + i - 10
        endif
        call UnitRemoveAbility(u, id)
        set i = i + 1
    endloop
    call SetHeroInt(u, 0, true)
    set amount = GetHeroInt(u, true)
    set i = 0
    loop
        exitwhen i == 20
        if ModuloInteger(amount / bit, 2) == 1 then
            if i < 10 then
                set id = 'AMi0' + i
            else
                set id = 'AMj0' + i - 10
            endif
            call UnitAddAbility(u, id)
            call BlzUnitHideAbility(u, id, true)
        endif
        set bit = bit * 2
        set i = i + 1
    endloop
    if BlzGetUnitMaxMana(u) != 0 then
        call BlzSetUnitMaxMana(u, 0)
    endif
    call SetUnitState(u, UNIT_STATE_MANA, 0.0)
endfunction

function MU_Register takes unit u returns nothing
    if GetUnitTypeId(u) == 'HMu1' and not IsUnitIllusion(u) and not HaveSavedInteger(MU_Hash, GetHandleId(u), 9) and MU_Count < 8190 then
        call MU_ZeroResources(u)
        call BlzUnitHideAbility(u, 'AMup', true)
        call UnitAddAbility(u, 'AMdc')
        call BlzUnitHideAbility(u, 'AMdc', true)
        set MU_Count = MU_Count + 1
        set MU_Hero[MU_Count] = u
        call SaveInteger(MU_Hash, GetHandleId(u), 9, GetPlayerId(GetOwningPlayer(u)))
    endif
endfunction

function MU_OnCast takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local integer spell = GetSpellAbilityId()
    local integer h = GetHandleId(u)
    local integer rank = GetUnitAbilityLevel(u, spell)
    if GetUnitTypeId(u) != 'HMu1' or IsUnitIllusion(u) or not FS_Alive(u) then
        set u = null
        return
    endif
    call MU_Register(u)
    if spell == 'AMu1' then
        call SaveReal(MU_Hash, h, 22, RMaxBJ(0.0, RMinBJ(1.0, 1.0-GetWidgetLife(u)/GetUnitState(u, UNIT_STATE_MAX_LIFE))))
        if MU_Pay(u, 50.0 + 10.0 * (rank - 1), spell) then
            call MU_Launch(u, rank, GetSpellTargetX(), GetSpellTargetY())
        endif
    elseif spell == 'AMu2' then
        if LoadBoolean(MU_Hash, h, 1) then
            call MU_BurnOff(u)
        elseif GetWidgetLife(u) > (8.0 + 4.0 * rank) * 0.25 + 0.405 then
            call SaveBoolean(MU_Hash, h, 1, true)
            call SaveReal(MU_Hash, h, 24, MC_Now())
            call SaveReal(MU_Hash, h, 25, MC_Now())
            call UnitAddAbility(u, 'AMur')
            call SetUnitAbilityLevel(u, 'AMur', rank)
            call BlzUnitHideAbility(u, 'AMur', true)
            call SaveReal(MU_Hash, h, 23, MC_Now() + 0.5)
            call MU_GasSpawn(u, rank)
        else
            call MU_Pay(u, GetWidgetLife(u), spell)
        endif
    elseif spell == 'AMu3' then
        call MM_Cast(u, GetSpellTargetUnit(), rank)
    elseif spell == 'AMdv' then
        if LoadTimerHandle(MM_Hash,h,1) != null and LoadUnitHandle(MM_Hash,GetHandleId(LoadTimerHandle(MM_Hash,h,1)),2) == GetSpellTargetUnit() then
            call RemoveSavedHandle(MM_Hash, h, 1)
            call MD_Start(u, GetSpellTargetUnit(), rank)
        endif
    elseif spell == 'AMu4' then
        if LoadInteger(DK_Hash, h, -40) == 0 and MU_Pay(u, GetWidgetLife(u)*0.20, spell) then
            call DR_Start(u, rank)
        endif
    endif
    set u = null
endfunction

function MU_Heal takes unit u, real amount returns nothing
    if FS_Alive(u) and not IsUnitIllusion(u) then
        call SetWidgetLife(u, RMinBJ(GetUnitState(u, UNIT_STATE_MAX_LIFE), GetWidgetLife(u) + amount))
    endif
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

function MU_OnCleaverHit takes nothing returns nothing
    local integer i = udg_MissileData
    local unit source = udg_MissileSource
    local unit target = udg_MissileHitUnit
    local player owner = udg_MissileOwner
    local integer rank = LoadInteger(MQ_Hash, i, 9)
    local real fraction = RMaxBJ(0.0, RMinBJ(1.0, udg_MissileTravelled/1100.0))
    local real damage = (40.0+40.0*rank)*(1.0+fraction)*(1.0+LoadReal(MQ_Hash, i, 10))
    local real refund = (40.0+10.0*rank)*(0.5+fraction)
    if LoadBoolean(MQ_Hash, i, 12) then
        set damage = damage * 1.5
        set refund = refund * 1.5
    endif
    call SaveBoolean(MQ_Hash, i, 11, true)
    set udg_MissileDestroy = true
    call MQ_Land(i, GetUnitX(target), GetUnitY(target))
    call MW_Impact(target)
    call FS_Hit(source, target, damage)
    if FS_Alive(target) then
        call MW_Start(source, target)
    endif
    if GetOwningPlayer(source) == owner then
        call MU_Heal(source, refund)
    endif
    set source = null
    set target = null
    set owner = null
endfunction

function MDV_Clear takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer slot = LoadInteger(MD_Hash, h, 21)
    if slot > 0 then
        call UnitRemoveAbility(u, MDV_Code[slot])
        set MDV_Used[slot] = false
    endif
    call DestroyEffect(LoadEffectHandle(MD_Hash, h, 22))
endfunction

function MD_Clear takes unit u returns nothing
    local integer h = GetHandleId(u)
    local unit v = LoadUnitHandle(MD_Hash, h, 1)
    if LoadUnitHandle(MD_Hash, GetHandleId(v), 10) == u then
        call RemoveSavedHandle(MD_Hash, GetHandleId(v), 10)
    endif
    call MDV_Clear(u)
    call FlushChildHashtable(MD_Hash, h)
    set v = null
endfunction

function MU_EOff takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer delta = LoadInteger(MU_Hash, h, 3)
    if delta != 0 and GetUnitTypeId(u) != 0 then
        call BlzSetUnitBaseDamage(u, BlzGetUnitBaseDamage(u, 0) - delta, 0)
    endif
    call RemoveSavedInteger(MU_Hash, h, 3)
    call RemoveSavedReal(MU_Hash, h, 2)
    call MU_ClearFX(h, 7)
endfunction

function MU_ROff takes unit u returns nothing
    local integer h = GetHandleId(u)
    call DK_Free(LoadInteger(DK_Hash, h, -40))
    call UnitRemoveAbility(u, 'AMuv')
    call UnitRemoveAbility(u, 'BMuv')
    call RemoveSavedReal(MU_Hash, h, 4)
    call RemoveSavedInteger(MU_Hash, h, 5)
    call MU_ClearFX(h, 8)
endfunction

function MU_Clear takes unit u returns nothing
    call MQ_ClearLoaded(u)
    call UnitRemoveAbility(u, 'AMqh')
    call UnitRemoveAbility(u, 'BMqh')
    call RemoveSavedReal(MU_Hash, GetHandleId(u), 21)
    call RemoveSavedInteger(MU_Hash, GetHandleId(u), 20)
    call MD_Clear(u)
    call MU_BurnOff(u)
    call MU_EOff(u)
    call MU_ROff(u)
endfunction

function MU_OnDeath takes nothing returns nothing
    if GetUnitTypeId(GetTriggerUnit()) == 'HMu1' then
        call MU_Clear(GetTriggerUnit())
    endif
endfunction

function MU_OnEnter takes nothing returns nothing
    call MU_Register(GetTriggerUnit())
endfunction

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

function MDV_Update takes unit u, unit v returns nothing
    local integer h = GetHandleId(u)
    local integer slot = LoadInteger(MD_Hash, h, 21)
    local integer abilityId
    local real left = GetWidgetLife(v)/RMaxBJ(1.0, LoadReal(MD_Hash, h, 26))
    local effect fx
    local string icon
    if slot == 0 then
        set slot = 1
        loop
            exitwhen slot > 256 or not MDV_Used[slot]
            set slot = slot + 1
        endloop
        if slot > 256 then
            return
        endif
        set MDV_Used[slot] = true
        call SaveInteger(MD_Hash, h, 21, slot)
        set abilityId = MDV_Code[slot]
        set icon = BlzGetAbilityIcon(GetUnitTypeId(v))
        if icon == "" or icon == null then
            set icon = "ReplaceableTextures\\CommandButtons\\BTNMundoMaul.blp"
        endif
        call BlzSetAbilityIcon(abilityId, icon)
        call BlzSetAbilityTooltip(abilityId, "Digesting: " + GetUnitName(v), 0)
        call UnitAddAbility(u, abilityId)
        call BlzSetUnitAbilityCooldown(u, abilityId, 0, RMaxBJ(1.0, left))
        set fx = AddSpecialEffectTarget("Abilities\\Spells\\Undead\\UnholyFrenzy\\UnholyFrenzyTarget.mdl", u, "chest")
        call BlzSetSpecialEffectScale(fx, 1.6)
        call SaveEffectHandle(MD_Hash, h, 22, fx)
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Orc\\WarStomp\\WarStompTarget.mdl", u, "origin"))
        call DestroyEffect(AddSpecialEffectTarget("Objects\\Spawnmodels\\Human\\HumanBlood\\HumanBloodLarge0.mdl", u, "chest"))
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilSpecialArt.mdl", u, "chest"))
    endif
    set abilityId = MDV_Code[slot]
    call BlzSetAbilityExtendedTooltip(abilityId, "Inside Mundo: " + GetUnitName(v) + "|nRemaining health: " + I2S(R2I(GetWidgetLife(v))) + "|nEstimated digestion time: " + I2S(R2I(left + 0.99)) + " sec.", 0)
    call BlzStartUnitAbilityCooldown(u, abilityId, RMaxBJ(0.25, left))
    set fx = null
endfunction

function MD_Tick takes unit u returns nothing
    local integer h = GetHandleId(u)
    local unit v = LoadUnitHandle(MD_Hash, h, 1)
    if v != null then
        if not FS_Alive(u) or GetUnitTypeId(v) == 0 or GetOwningPlayer(u) != LoadPlayerHandle(MD_Hash, h, 3) then
            call MD_Clear(u)
        elseif IsUnitInTransport(v, u) then
            call SaveBoolean(MD_Hash, h, 5, true)
            call MDV_Update(u, v)
        elseif LoadBoolean(MD_Hash, h, 5) or MU_Now >= LoadReal(MD_Hash, h, 4) then
            // Interrupted/failed swallowing or a released meal never grants a burst.
            call MD_Clear(u)
        endif
    endif
    set v = null
endfunction

function MU_RefreshE takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer rank = GetUnitAbilityLevel(u, 'AMu3')
    local real missing = 1.0 - GetWidgetLife(u) / GetUnitState(u, UNIT_STATE_MAX_LIFE)
    local integer delta = R2I((30.0 + 10.0 * rank) * (1.0 + missing))
    call BlzSetUnitBaseDamage(u, BlzGetUnitBaseDamage(u, 0) - LoadInteger(MU_Hash, h, 3) + delta, 0)
    call SaveInteger(MU_Hash, h, 3, delta)
endfunction

function MU_TickHero takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer rank
    local real cost
    local real heal
    local real remaining
    local group targets
    local unit target
    if GetUnitTypeId(u) != 0 and not IsUnitIllusion(u) then
        call MU_ZeroResources(u)
    endif
    if GetUnitTypeId(u) == 0 or IsUnitIllusion(u) then
        call MU_Clear(u)
        call FlushChildHashtable(MU_Hash, h)
    elseif not FS_Alive(u) or LoadInteger(MU_Hash, h, 9) != GetPlayerId(GetOwningPlayer(u)) then
        call MU_Clear(u)
        call SaveInteger(MU_Hash, h, 9, GetPlayerId(GetOwningPlayer(u)))
    elseif GetPlayerId(GetOwningPlayer(u)) < 12 then
        call MD_Tick(u)
        set heal = GetUnitState(u, UNIT_STATE_MAX_LIFE) * 0.003 * 0.25
        // Integrate the final fractional tick, then remove the speed and visual.
        set remaining = LoadReal(MU_Hash, h, 4) - (MU_Now - 0.25)
        if remaining > 0.0 then
            set rank = LoadInteger(MU_Hash, h, 5)
            set heal = heal + GetUnitState(u, UNIT_STATE_MAX_LIFE) * (0.30 + 0.10 * rank) / 12.0 * RMinBJ(0.25, remaining)
        endif
        set remaining = LoadReal(MU_Hash, h, 21)-(MU_Now-0.25)
        if remaining > 0.0 then
            set heal = heal + GetUnitState(u, UNIT_STATE_MAX_LIFE)*0.02*RMinBJ(0.25, remaining)
        endif
        if LoadReal(MU_Hash, h, 21) <= MU_Now then
            call UnitRemoveAbility(u, 'AMqh')
            call UnitRemoveAbility(u, 'BMqh')
        endif
        call MU_Heal(u, heal)
        if LoadReal(MU_Hash, h, 4) <= MU_Now and HaveSavedReal(MU_Hash, h, 4) then
            call MU_ROff(u)
        endif
        if LoadBoolean(MU_Hash, h, 1) then
            set rank = GetUnitAbilityLevel(u, 'AMu2')
            set cost = MC_Drain(u, rank)
            if rank == 0 or GetWidgetLife(u) <= cost + 0.405 then
                call MU_BurnOff(u)
            else
                call SetWidgetLife(u, GetWidgetLife(u) - cost)
                call SaveReal(MU_Hash, h, 25, MC_Now())
                call SetUnitAbilityLevel(u, 'AMur', rank)
                if LoadReal(MU_Hash, h, 23) <= MC_Now() then
                    call MU_GasSpawn(u, rank)
                    call SaveReal(MU_Hash, h, 23, MC_Now() + 0.5)
                endif
            endif
        endif
        if FS_Alive(u) and LoadReal(MU_Hash, h, 2) > MU_Now and GetUnitAbilityLevel(u, 'AMu3') > 0 then
            call MU_RefreshE(u)
        elseif HaveSavedReal(MU_Hash, h, 2) then
            call MU_EOff(u)
        endif
    endif
    set target = null
    set targets = null
endfunction

function MU_Tick takes nothing returns nothing
    local integer i = 1
    local unit u
    set MU_Now = MU_Now + 0.25
    loop
        exitwhen i > MU_Count
        set u = MU_Hero[i]
        call MU_TickHero(u)
        if GetUnitTypeId(u) == 0 or IsUnitIllusion(u) then
            set MU_Hero[i] = MU_Hero[MU_Count]
            set MU_Hero[MU_Count] = null
            set MU_Count = MU_Count - 1
        else
            set i = i + 1
        endif
    endloop
    set u = null
endfunction

function MD_InitTypes takes nothing returns nothing
    call SaveBoolean(MD_Types, 'E002', 1, true)
    call SaveBoolean(MD_Types, 'E003', 1, true)
    call SaveBoolean(MD_Types, 'E005', 1, true)
    call SaveBoolean(MD_Types, 'E00F', 1, true)
    call SaveBoolean(MD_Types, 'E00V', 1, true)
    call SaveBoolean(MD_Types, 'E011', 1, true)
    call SaveBoolean(MD_Types, 'E018', 1, true)
    call SaveBoolean(MD_Types, 'H005', 1, true)
    call SaveBoolean(MD_Types, 'H008', 1, true)
    call SaveBoolean(MD_Types, 'H009', 1, true)
    call SaveBoolean(MD_Types, 'H00A', 1, true)
    call SaveBoolean(MD_Types, 'H01Q', 1, true)
    call SaveBoolean(MD_Types, 'H01R', 1, true)
    call SaveBoolean(MD_Types, 'H04F', 1, true)
    call SaveBoolean(MD_Types, 'H04W', 1, true)
    call SaveBoolean(MD_Types, 'H0R0', 1, true)
    call SaveBoolean(MD_Types, 'N00C', 1, true)
    call SaveBoolean(MD_Types, 'N00D', 1, true)
    call SaveBoolean(MD_Types, 'N00H', 1, true)
    call SaveBoolean(MD_Types, 'N00I', 1, true)
    call SaveBoolean(MD_Types, 'N00N', 1, true)
    call SaveBoolean(MD_Types, 'N00O', 1, true)
    call SaveBoolean(MD_Types, 'N00P', 1, true)
    call SaveBoolean(MD_Types, 'N00Z', 1, true)
    call SaveBoolean(MD_Types, 'N017', 1, true)
    call SaveBoolean(MD_Types, 'N018', 1, true)
    call SaveBoolean(MD_Types, 'N01C', 1, true)
    call SaveBoolean(MD_Types, 'N01D', 1, true)
    call SaveBoolean(MD_Types, 'N01G', 1, true)
    call SaveBoolean(MD_Types, 'N01H', 1, true)
    call SaveBoolean(MD_Types, 'N01I', 1, true)
    call SaveBoolean(MD_Types, 'N035', 1, true)
    call SaveBoolean(MD_Types, 'N03B', 1, true)
    call SaveBoolean(MD_Types, 'N03J', 1, true)
    call SaveBoolean(MD_Types, 'N05H', 1, true)
    call SaveBoolean(MD_Types, 'Naka', 1, true)
    call SaveBoolean(MD_Types, 'Nal2', 1, true)
    call SaveBoolean(MD_Types, 'Nal3', 1, true)
    call SaveBoolean(MD_Types, 'Nalc', 1, true)
    call SaveBoolean(MD_Types, 'Nalm', 1, true)
    call SaveBoolean(MD_Types, 'Nbrn', 1, true)
    call SaveBoolean(MD_Types, 'Nbst', 1, true)
    call SaveBoolean(MD_Types, 'Nfir', 1, true)
    call SaveBoolean(MD_Types, 'Nglx', 1, true)
    call SaveBoolean(MD_Types, 'Nmsr', 1, true)
    call SaveBoolean(MD_Types, 'Nngs', 1, true)
    call SaveBoolean(MD_Types, 'Npal', 1, true)
    call SaveBoolean(MD_Types, 'Npbm', 1, true)
    call SaveBoolean(MD_Types, 'Nplh', 1, true)
    call SaveBoolean(MD_Types, 'Nrob', 1, true)
    call SaveBoolean(MD_Types, 'Nswt', 1, true)
    call SaveBoolean(MD_Types, 'Ntin', 1, true)
    call SaveBoolean(MD_Types, 'O003', 1, true)
    call SaveBoolean(MD_Types, 'O004', 1, true)
    call SaveBoolean(MD_Types, 'O005', 1, true)
    call SaveBoolean(MD_Types, 'O006', 1, true)
    call SaveBoolean(MD_Types, 'O016', 1, true)
    call SaveBoolean(MD_Types, 'U002', 1, true)
    call SaveBoolean(MD_Types, 'U003', 1, true)
    call SaveBoolean(MD_Types, 'U004', 1, true)
    call SaveBoolean(MD_Types, 'U005', 1, true)
    call SaveBoolean(MD_Types, 'U00R', 1, true)
    call SaveBoolean(MD_Types, 'n001', 1, true)
    call SaveBoolean(MD_Types, 'n005', 1, true)
    call SaveBoolean(MD_Types, 'n00A', 1, true)
    call SaveBoolean(MD_Types, 'n00J', 1, true)
    call SaveBoolean(MD_Types, 'n00L', 1, true)
    call SaveBoolean(MD_Types, 'n00Q', 1, true)
    call SaveBoolean(MD_Types, 'n00S', 1, true)
    call SaveBoolean(MD_Types, 'n00T', 1, true)
    call SaveBoolean(MD_Types, 'n00U', 1, true)
    call SaveBoolean(MD_Types, 'n00Y', 1, true)
    call SaveBoolean(MD_Types, 'n010', 1, true)
    call SaveBoolean(MD_Types, 'n011', 1, true)
    call SaveBoolean(MD_Types, 'n014', 1, true)
    call SaveBoolean(MD_Types, 'n01P', 1, true)
    call SaveBoolean(MD_Types, 'n01R', 1, true)
    call SaveBoolean(MD_Types, 'n02Q', 1, true)
    call SaveBoolean(MD_Types, 'n02R', 1, true)
    call SaveBoolean(MD_Types, 'n02T', 1, true)
    call SaveBoolean(MD_Types, 'n033', 1, true)
    call SaveBoolean(MD_Types, 'n03M', 1, true)
    call SaveBoolean(MD_Types, 'n03O', 1, true)
    call SaveBoolean(MD_Types, 'n03P', 1, true)
    call SaveBoolean(MD_Types, 'n03W', 1, true)
    call SaveBoolean(MD_Types, 'n040', 1, true)
    call SaveBoolean(MD_Types, 'n042', 1, true)
    call SaveBoolean(MD_Types, 'n043', 1, true)
    call SaveBoolean(MD_Types, 'n044', 1, true)
    call SaveBoolean(MD_Types, 'n052', 1, true)
    call SaveBoolean(MD_Types, 'n053', 1, true)
    call SaveBoolean(MD_Types, 'n054', 1, true)
    call SaveBoolean(MD_Types, 'n055', 1, true)
    call SaveBoolean(MD_Types, 'n056', 1, true)
    call SaveBoolean(MD_Types, 'n057', 1, true)
    call SaveBoolean(MD_Types, 'n058', 1, true)
    call SaveBoolean(MD_Types, 'n05G', 1, true)
    call SaveBoolean(MD_Types, 'n05L', 1, true)
    call SaveBoolean(MD_Types, 'n05N', 1, true)
    call SaveBoolean(MD_Types, 'n05O', 1, true)
    call SaveBoolean(MD_Types, 'n05Q', 1, true)
    call SaveBoolean(MD_Types, 'n05X', 1, true)
    call SaveBoolean(MD_Types, 'n05Y', 1, true)
    call SaveBoolean(MD_Types, 'n061', 1, true)
    call SaveBoolean(MD_Types, 'nadk', 1, true)
    call SaveBoolean(MD_Types, 'nadr', 1, true)
    call SaveBoolean(MD_Types, 'nadw', 1, true)
    call SaveBoolean(MD_Types, 'nahy', 1, true)
    call SaveBoolean(MD_Types, 'nanb', 1, true)
    call SaveBoolean(MD_Types, 'nanc', 1, true)
    call SaveBoolean(MD_Types, 'nane', 1, true)
    call SaveBoolean(MD_Types, 'nanm', 1, true)
    call SaveBoolean(MD_Types, 'nano', 1, true)
    call SaveBoolean(MD_Types, 'nanw', 1, true)
    call SaveBoolean(MD_Types, 'narg', 1, true)
    call SaveBoolean(MD_Types, 'nass', 1, true)
    call SaveBoolean(MD_Types, 'nban', 1, true)
    call SaveBoolean(MD_Types, 'nbda', 1, true)
    call SaveBoolean(MD_Types, 'nbdk', 1, true)
    call SaveBoolean(MD_Types, 'nbdm', 1, true)
    call SaveBoolean(MD_Types, 'nbdo', 1, true)
    call SaveBoolean(MD_Types, 'nbdr', 1, true)
    call SaveBoolean(MD_Types, 'nbds', 1, true)
    call SaveBoolean(MD_Types, 'nbdw', 1, true)
    call SaveBoolean(MD_Types, 'nbld', 1, true)
    call SaveBoolean(MD_Types, 'nbnb', 1, true)
    call SaveBoolean(MD_Types, 'nbot', 1, true)
    call SaveBoolean(MD_Types, 'nbrg', 1, true)
    call SaveBoolean(MD_Types, 'nbwm', 1, true)
    call SaveBoolean(MD_Types, 'nbzd', 1, true)
    call SaveBoolean(MD_Types, 'nbzk', 1, true)
    call SaveBoolean(MD_Types, 'nbzw', 1, true)
    call SaveBoolean(MD_Types, 'ncat', 1, true)
    call SaveBoolean(MD_Types, 'ncea', 1, true)
    call SaveBoolean(MD_Types, 'ncen', 1, true)
    call SaveBoolean(MD_Types, 'ncer', 1, true)
    call SaveBoolean(MD_Types, 'ncfs', 1, true)
    call SaveBoolean(MD_Types, 'ncim', 1, true)
    call SaveBoolean(MD_Types, 'ncks', 1, true)
    call SaveBoolean(MD_Types, 'ncnk', 1, true)
    call SaveBoolean(MD_Types, 'ndmu', 1, true)
    call SaveBoolean(MD_Types, 'ndqn', 1, true)
    call SaveBoolean(MD_Types, 'ndqp', 1, true)
    call SaveBoolean(MD_Types, 'ndqs', 1, true)
    call SaveBoolean(MD_Types, 'ndqt', 1, true)
    call SaveBoolean(MD_Types, 'ndqv', 1, true)
    call SaveBoolean(MD_Types, 'ndrd', 1, true)
    call SaveBoolean(MD_Types, 'ndrf', 1, true)
    call SaveBoolean(MD_Types, 'ndrh', 1, true)
    call SaveBoolean(MD_Types, 'ndrj', 1, true)
    call SaveBoolean(MD_Types, 'ndrl', 1, true)
    call SaveBoolean(MD_Types, 'ndrm', 1, true)
    call SaveBoolean(MD_Types, 'ndrn', 1, true)
    call SaveBoolean(MD_Types, 'ndrp', 1, true)
    call SaveBoolean(MD_Types, 'ndrs', 1, true)
    call SaveBoolean(MD_Types, 'ndrt', 1, true)
    call SaveBoolean(MD_Types, 'ndrv', 1, true)
    call SaveBoolean(MD_Types, 'ndrw', 1, true)
    call SaveBoolean(MD_Types, 'ndsa', 1, true)
    call SaveBoolean(MD_Types, 'ndtb', 1, true)
    call SaveBoolean(MD_Types, 'ndth', 1, true)
    call SaveBoolean(MD_Types, 'ndtp', 1, true)
    call SaveBoolean(MD_Types, 'ndtr', 1, true)
    call SaveBoolean(MD_Types, 'ndtt', 1, true)
    call SaveBoolean(MD_Types, 'ndtw', 1, true)
    call SaveBoolean(MD_Types, 'nehy', 1, true)
    call SaveBoolean(MD_Types, 'nelb', 1, true)
    call SaveBoolean(MD_Types, 'nele', 1, true)
    call SaveBoolean(MD_Types, 'nenc', 1, true)
    call SaveBoolean(MD_Types, 'nenf', 1, true)
    call SaveBoolean(MD_Types, 'nenp', 1, true)
    call SaveBoolean(MD_Types, 'nepl', 1, true)
    call SaveBoolean(MD_Types, 'nerd', 1, true)
    call SaveBoolean(MD_Types, 'ners', 1, true)
    call SaveBoolean(MD_Types, 'nerw', 1, true)
    call SaveBoolean(MD_Types, 'nfgb', 1, true)
    call SaveBoolean(MD_Types, 'nfgl', 1, true)
    call SaveBoolean(MD_Types, 'nfgo', 1, true)
    call SaveBoolean(MD_Types, 'nfgt', 1, true)
    call SaveBoolean(MD_Types, 'nfgu', 1, true)
    call SaveBoolean(MD_Types, 'nfod', 1, true)
    call SaveBoolean(MD_Types, 'nfor', 1, true)
    call SaveBoolean(MD_Types, 'nfot', 1, true)
    call SaveBoolean(MD_Types, 'nfov', 1, true)
    call SaveBoolean(MD_Types, 'nfpc', 1, true)
    call SaveBoolean(MD_Types, 'nfpe', 1, true)
    call SaveBoolean(MD_Types, 'nfpl', 1, true)
    call SaveBoolean(MD_Types, 'nfps', 1, true)
    call SaveBoolean(MD_Types, 'nfpt', 1, true)
    call SaveBoolean(MD_Types, 'nfpu', 1, true)
    call SaveBoolean(MD_Types, 'nfra', 1, true)
    call SaveBoolean(MD_Types, 'nfrb', 1, true)
    call SaveBoolean(MD_Types, 'nfre', 1, true)
    call SaveBoolean(MD_Types, 'nfrg', 1, true)
    call SaveBoolean(MD_Types, 'nfrl', 1, true)
    call SaveBoolean(MD_Types, 'nfrp', 1, true)
    call SaveBoolean(MD_Types, 'nfrs', 1, true)
    call SaveBoolean(MD_Types, 'nfsh', 1, true)
    call SaveBoolean(MD_Types, 'nfsp', 1, true)
    call SaveBoolean(MD_Types, 'nftb', 1, true)
    call SaveBoolean(MD_Types, 'nftk', 1, true)
    call SaveBoolean(MD_Types, 'nftr', 1, true)
    call SaveBoolean(MD_Types, 'nftt', 1, true)
    call SaveBoolean(MD_Types, 'ngdk', 1, true)
    call SaveBoolean(MD_Types, 'nggd', 1, true)
    call SaveBoolean(MD_Types, 'nggg', 1, true)
    call SaveBoolean(MD_Types, 'nggm', 1, true)
    call SaveBoolean(MD_Types, 'nggr', 1, true)
    call SaveBoolean(MD_Types, 'ngh1', 1, true)
    call SaveBoolean(MD_Types, 'ngir', 1, true)
    call SaveBoolean(MD_Types, 'nglm', 1, true)
    call SaveBoolean(MD_Types, 'ngna', 1, true)
    call SaveBoolean(MD_Types, 'ngnb', 1, true)
    call SaveBoolean(MD_Types, 'ngno', 1, true)
    call SaveBoolean(MD_Types, 'ngns', 1, true)
    call SaveBoolean(MD_Types, 'ngnv', 1, true)
    call SaveBoolean(MD_Types, 'ngnw', 1, true)
    call SaveBoolean(MD_Types, 'ngos', 1, true)
    call SaveBoolean(MD_Types, 'ngow', 1, true)
    call SaveBoolean(MD_Types, 'ngrd', 1, true)
    call SaveBoolean(MD_Types, 'ngrk', 1, true)
    call SaveBoolean(MD_Types, 'ngrw', 1, true)
    call SaveBoolean(MD_Types, 'ngsp', 1, true)
    call SaveBoolean(MD_Types, 'ngst', 1, true)
    call SaveBoolean(MD_Types, 'ngz1', 1, true)
    call SaveBoolean(MD_Types, 'ngz2', 1, true)
    call SaveBoolean(MD_Types, 'ngz3', 1, true)
    call SaveBoolean(MD_Types, 'nhar', 1, true)
    call SaveBoolean(MD_Types, 'nhdc', 1, true)
    call SaveBoolean(MD_Types, 'nhfp', 1, true)
    call SaveBoolean(MD_Types, 'nhhr', 1, true)
    call SaveBoolean(MD_Types, 'nhrh', 1, true)
    call SaveBoolean(MD_Types, 'nhrq', 1, true)
    call SaveBoolean(MD_Types, 'nhrr', 1, true)
    call SaveBoolean(MD_Types, 'nhrw', 1, true)
    call SaveBoolean(MD_Types, 'nhyd', 1, true)
    call SaveBoolean(MD_Types, 'nhyh', 1, true)
    call SaveBoolean(MD_Types, 'nina', 1, true)
    call SaveBoolean(MD_Types, 'ninc', 1, true)
    call SaveBoolean(MD_Types, 'ninm', 1, true)
    call SaveBoolean(MD_Types, 'nith', 1, true)
    call SaveBoolean(MD_Types, 'nitp', 1, true)
    call SaveBoolean(MD_Types, 'nitr', 1, true)
    call SaveBoolean(MD_Types, 'nits', 1, true)
    call SaveBoolean(MD_Types, 'nitt', 1, true)
    call SaveBoolean(MD_Types, 'nitw', 1, true)
    call SaveBoolean(MD_Types, 'njg1', 1, true)
    call SaveBoolean(MD_Types, 'njga', 1, true)
    call SaveBoolean(MD_Types, 'njgb', 1, true)
    call SaveBoolean(MD_Types, 'nkob', 1, true)
    call SaveBoolean(MD_Types, 'nkog', 1, true)
    call SaveBoolean(MD_Types, 'nkol', 1, true)
    call SaveBoolean(MD_Types, 'nkot', 1, true)
    call SaveBoolean(MD_Types, 'nlds', 1, true)
    call SaveBoolean(MD_Types, 'nlkl', 1, true)
    call SaveBoolean(MD_Types, 'nlpd', 1, true)
    call SaveBoolean(MD_Types, 'nlpr', 1, true)
    call SaveBoolean(MD_Types, 'nlps', 1, true)
    call SaveBoolean(MD_Types, 'nlrv', 1, true)
    call SaveBoolean(MD_Types, 'nlsn', 1, true)
    call SaveBoolean(MD_Types, 'nltc', 1, true)
    call SaveBoolean(MD_Types, 'nltl', 1, true)
    call SaveBoolean(MD_Types, 'nlur', 1, true)
    call SaveBoolean(MD_Types, 'nmam', 1, true)
    call SaveBoolean(MD_Types, 'nmbg', 1, true)
    call SaveBoolean(MD_Types, 'nmcf', 1, true)
    call SaveBoolean(MD_Types, 'nmdr', 1, true)
    call SaveBoolean(MD_Types, 'nmfs', 1, true)
    call SaveBoolean(MD_Types, 'nmgd', 1, true)
    call SaveBoolean(MD_Types, 'nmgr', 1, true)
    call SaveBoolean(MD_Types, 'nmgw', 1, true)
    call SaveBoolean(MD_Types, 'nmit', 1, true)
    call SaveBoolean(MD_Types, 'nmmu', 1, true)
    call SaveBoolean(MD_Types, 'nmpg', 1, true)
    call SaveBoolean(MD_Types, 'nmrl', 1, true)
    call SaveBoolean(MD_Types, 'nmrm', 1, true)
    call SaveBoolean(MD_Types, 'nmrr', 1, true)
    call SaveBoolean(MD_Types, 'nmrv', 1, true)
    call SaveBoolean(MD_Types, 'nmsc', 1, true)
    call SaveBoolean(MD_Types, 'nmsn', 1, true)
    call SaveBoolean(MD_Types, 'nmtw', 1, true)
    call SaveBoolean(MD_Types, 'nndk', 1, true)
    call SaveBoolean(MD_Types, 'nndr', 1, true)
    call SaveBoolean(MD_Types, 'nnht', 1, true)
    call SaveBoolean(MD_Types, 'nnwa', 1, true)
    call SaveBoolean(MD_Types, 'nnwl', 1, true)
    call SaveBoolean(MD_Types, 'nnwq', 1, true)
    call SaveBoolean(MD_Types, 'nnwr', 1, true)
    call SaveBoolean(MD_Types, 'nnws', 1, true)
    call SaveBoolean(MD_Types, 'noga', 1, true)
    call SaveBoolean(MD_Types, 'nogl', 1, true)
    call SaveBoolean(MD_Types, 'nogm', 1, true)
    call SaveBoolean(MD_Types, 'nogn', 1, true)
    call SaveBoolean(MD_Types, 'nogo', 1, true)
    call SaveBoolean(MD_Types, 'nogr', 1, true)
    call SaveBoolean(MD_Types, 'nomg', 1, true)
    call SaveBoolean(MD_Types, 'nowb', 1, true)
    call SaveBoolean(MD_Types, 'nowe', 1, true)
    call SaveBoolean(MD_Types, 'nowk', 1, true)
    call SaveBoolean(MD_Types, 'npfl', 1, true)
    call SaveBoolean(MD_Types, 'npfm', 1, true)
    call SaveBoolean(MD_Types, 'nplb', 1, true)
    call SaveBoolean(MD_Types, 'nplg', 1, true)
    call SaveBoolean(MD_Types, 'npn1', 1, true)
    call SaveBoolean(MD_Types, 'npn2', 1, true)
    call SaveBoolean(MD_Types, 'npn3', 1, true)
    call SaveBoolean(MD_Types, 'npn4', 1, true)
    call SaveBoolean(MD_Types, 'npn5', 1, true)
    call SaveBoolean(MD_Types, 'npn6', 1, true)
    call SaveBoolean(MD_Types, 'nqbh', 1, true)
    call SaveBoolean(MD_Types, 'nrdk', 1, true)
    call SaveBoolean(MD_Types, 'nrdr', 1, true)
    call SaveBoolean(MD_Types, 'nrel', 1, true)
    call SaveBoolean(MD_Types, 'nrog', 1, true)
    call SaveBoolean(MD_Types, 'nrvd', 1, true)
    call SaveBoolean(MD_Types, 'nrvf', 1, true)
    call SaveBoolean(MD_Types, 'nrvi', 1, true)
    call SaveBoolean(MD_Types, 'nrvl', 1, true)
    call SaveBoolean(MD_Types, 'nrvs', 1, true)
    call SaveBoolean(MD_Types, 'nrwm', 1, true)
    call SaveBoolean(MD_Types, 'nrzb', 1, true)
    call SaveBoolean(MD_Types, 'nrzg', 1, true)
    call SaveBoolean(MD_Types, 'nrzm', 1, true)
    call SaveBoolean(MD_Types, 'nrzs', 1, true)
    call SaveBoolean(MD_Types, 'nrzt', 1, true)
    call SaveBoolean(MD_Types, 'nsat', 1, true)
    call SaveBoolean(MD_Types, 'nsbm', 1, true)
    call SaveBoolean(MD_Types, 'nsc2', 1, true)
    call SaveBoolean(MD_Types, 'nsc3', 1, true)
    call SaveBoolean(MD_Types, 'nsca', 1, true)
    call SaveBoolean(MD_Types, 'nscb', 1, true)
    call SaveBoolean(MD_Types, 'nsce', 1, true)
    call SaveBoolean(MD_Types, 'nsel', 1, true)
    call SaveBoolean(MD_Types, 'nsgb', 1, true)
    call SaveBoolean(MD_Types, 'nsgg', 1, true)
    call SaveBoolean(MD_Types, 'nsgh', 1, true)
    call SaveBoolean(MD_Types, 'nsgn', 1, true)
    call SaveBoolean(MD_Types, 'nsgt', 1, true)
    call SaveBoolean(MD_Types, 'nska', 1, true)
    call SaveBoolean(MD_Types, 'nskg', 1, true)
    call SaveBoolean(MD_Types, 'nskm', 1, true)
    call SaveBoolean(MD_Types, 'nsko', 1, true)
    call SaveBoolean(MD_Types, 'nslf', 1, true)
    call SaveBoolean(MD_Types, 'nslh', 1, true)
    call SaveBoolean(MD_Types, 'nsll', 1, true)
    call SaveBoolean(MD_Types, 'nslm', 1, true)
    call SaveBoolean(MD_Types, 'nsln', 1, true)
    call SaveBoolean(MD_Types, 'nslr', 1, true)
    call SaveBoolean(MD_Types, 'nslv', 1, true)
    call SaveBoolean(MD_Types, 'nsns', 1, true)
    call SaveBoolean(MD_Types, 'nsoc', 1, true)
    call SaveBoolean(MD_Types, 'nsog', 1, true)
    call SaveBoolean(MD_Types, 'nspb', 1, true)
    call SaveBoolean(MD_Types, 'nspd', 1, true)
    call SaveBoolean(MD_Types, 'nspg', 1, true)
    call SaveBoolean(MD_Types, 'nspp', 1, true)
    call SaveBoolean(MD_Types, 'nspr', 1, true)
    call SaveBoolean(MD_Types, 'nsqa', 1, true)
    call SaveBoolean(MD_Types, 'nsqe', 1, true)
    call SaveBoolean(MD_Types, 'nsqo', 1, true)
    call SaveBoolean(MD_Types, 'nsqt', 1, true)
    call SaveBoolean(MD_Types, 'nsra', 1, true)
    call SaveBoolean(MD_Types, 'nsrh', 1, true)
    call SaveBoolean(MD_Types, 'nsrn', 1, true)
    call SaveBoolean(MD_Types, 'nsrv', 1, true)
    call SaveBoolean(MD_Types, 'nsrw', 1, true)
    call SaveBoolean(MD_Types, 'nssp', 1, true)
    call SaveBoolean(MD_Types, 'nsth', 1, true)
    call SaveBoolean(MD_Types, 'nstl', 1, true)
    call SaveBoolean(MD_Types, 'nsts', 1, true)
    call SaveBoolean(MD_Types, 'nstw', 1, true)
    call SaveBoolean(MD_Types, 'nsty', 1, true)
    call SaveBoolean(MD_Types, 'nsw1', 1, true)
    call SaveBoolean(MD_Types, 'nsw2', 1, true)
    call SaveBoolean(MD_Types, 'nsw3', 1, true)
    call SaveBoolean(MD_Types, 'nthl', 1, true)
    call SaveBoolean(MD_Types, 'ntka', 1, true)
    call SaveBoolean(MD_Types, 'ntkc', 1, true)
    call SaveBoolean(MD_Types, 'ntkf', 1, true)
    call SaveBoolean(MD_Types, 'ntkh', 1, true)
    call SaveBoolean(MD_Types, 'ntks', 1, true)
    call SaveBoolean(MD_Types, 'ntkt', 1, true)
    call SaveBoolean(MD_Types, 'ntkw', 1, true)
    call SaveBoolean(MD_Types, 'ntrd', 1, true)
    call SaveBoolean(MD_Types, 'ntrg', 1, true)
    call SaveBoolean(MD_Types, 'ntrh', 1, true)
    call SaveBoolean(MD_Types, 'ntrs', 1, true)
    call SaveBoolean(MD_Types, 'ntrt', 1, true)
    call SaveBoolean(MD_Types, 'ntrv', 1, true)
    call SaveBoolean(MD_Types, 'ntws', 1, true)
    call SaveBoolean(MD_Types, 'nubk', 1, true)
    call SaveBoolean(MD_Types, 'nubr', 1, true)
    call SaveBoolean(MD_Types, 'nubw', 1, true)
    call SaveBoolean(MD_Types, 'nvde', 1, true)
    call SaveBoolean(MD_Types, 'nvdg', 1, true)
    call SaveBoolean(MD_Types, 'nvdl', 1, true)
    call SaveBoolean(MD_Types, 'nvdw', 1, true)
    call SaveBoolean(MD_Types, 'nwen', 1, true)
    call SaveBoolean(MD_Types, 'nwiz', 1, true)
    call SaveBoolean(MD_Types, 'nwld', 1, true)
    call SaveBoolean(MD_Types, 'nwlg', 1, true)
    call SaveBoolean(MD_Types, 'nwlt', 1, true)
    call SaveBoolean(MD_Types, 'nwna', 1, true)
    call SaveBoolean(MD_Types, 'nwnr', 1, true)
    call SaveBoolean(MD_Types, 'nwns', 1, true)
    call SaveBoolean(MD_Types, 'nwrg', 1, true)
    call SaveBoolean(MD_Types, 'nwwd', 1, true)
    call SaveBoolean(MD_Types, 'nwwf', 1, true)
    call SaveBoolean(MD_Types, 'nwwg', 1, true)
    call SaveBoolean(MD_Types, 'nwzd', 1, true)
    call SaveBoolean(MD_Types, 'nwzg', 1, true)
    call SaveBoolean(MD_Types, 'nwzr', 1, true)
    call SaveBoolean(MD_Types, 'nwzw', 1, true)
    call SaveBoolean(MD_Types, 'nzep', 1, true)
    call SaveBoolean(MD_Types, 'o00A', 1, true)
    call SaveBoolean(MD_Types, 'o00H', 1, true)
    call SaveBoolean(MD_Types, 'o00K', 1, true)
    call SaveBoolean(MD_Types, 'o00U', 1, true)
    call SaveBoolean(MD_Types, 'o00W', 1, true)
    call SaveBoolean(MD_Types, 'o011', 1, true)
    call SaveBoolean(MD_Types, 'o01C', 1, true)
    call SaveBoolean(MD_Types, 'o01H', 1, true)
    call SaveBoolean(MD_Types, 'o01I', 1, true)
    call SaveBoolean(MD_Types, 'ohwd', 1, true)
    call SaveBoolean(MD_Types, 'z007', 1, true)
    call SaveBoolean(MD_Types, 'z008', 1, true)
    call SaveBoolean(MD_Types, 'z009', 1, true)
    call SaveBoolean(MD_Types, 'z00A', 1, true)
    call SaveBoolean(MD_Types, 'z00B', 1, true)
endfunction

function MD_OnOrder takes nothing returns nothing
    local unit u=GetTriggerUnit()
    if GetUnitTypeId(u) == 'HMu1' and GetIssuedOrderId() == OrderId("devour") then
        if not MM_DevourReady(u, GetOrderTargetUnit()) then
            call MD_Reject(u)
        endif
    endif
    set u=null
endfunction

function MD_OnChannel takes nothing returns nothing
    local unit u=GetTriggerUnit()
    local integer a=GetSpellAbilityId()
    if GetUnitTypeId(u) == 'HMu1' then
        if a == 'AMu3' then
            if not MM_CanCast(u, GetSpellTargetUnit()) then
                call MD_Reject(u)
            endif
        elseif a == 'AMdv' then
            if not MM_DevourReady(u, GetSpellTargetUnit()) then
                call MD_Reject(u)
            endif
        endif
    endif
    set u=null
endfunction

function MD_OnDamage takes nothing returns nothing
    local unit v = GetTriggerUnit()
    local unit u = LoadUnitHandle(MD_Hash, GetHandleId(v), 10)
    local integer rank
    local real amount
    if u != null and FS_Alive(u) and GetEventDamageSource() == u and IsUnitInTransport(v, u) and GetOwningPlayer(u) == LoadPlayerHandle(MD_Hash, GetHandleId(u), 3) then
        // Position the hidden passenger before lethal damage, so native XP and
        // the map's later death handlers both use the current digestion location.
        call SetUnitX(v, GetUnitX(u))
        call SetUnitY(v, GetUnitY(u))
        set rank = LoadInteger(MD_Hash, GetHandleId(u), 2)
        if HaveSavedReal(MD_Hash, GetHandleId(u), 25) and MU_Now > LoadReal(MD_Hash, GetHandleId(u), 25) and GetEventDamage() > 0.0 then
            call SaveReal(MD_Hash, GetHandleId(u), 26, GetEventDamage()/(MU_Now-LoadReal(MD_Hash, GetHandleId(u), 25)))
        endif
        call SaveReal(MD_Hash, GetHandleId(u), 25, MU_Now)
        set amount = RMinBJ(GetWidgetLife(v), RMaxBJ(0.0, GetEventDamage()))
        call MU_Heal(u, amount*(0.20+0.05*rank))
    endif
    set u = null
    set v = null
endfunction

function MD_Burst takes unit u, integer rank returns nothing
    local group g = CreateGroup()
    local unit v
    local real amount = 150.0+50.0*rank
    local sound burp = CreateSoundFromLabel("Devour", false, true, true, 10, 10)
    call SetSoundPosition(burp, GetUnitX(u), GetUnitY(u), DK_GroundZ(GetUnitX(u), GetUnitY(u))+80.0)
    call StartSound(burp)
    call KillSoundWhenDone(burp)
    call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\HolyBolt\\HolyBoltSpecialArt.mdl", u, "origin"))
    call GroupEnumUnitsInRange(g, GetUnitX(u), GetUnitY(u), 250.0+50.0*rank, null)
    loop
        set v = FirstOfGroup(g)
        exitwhen v == null
        call GroupRemoveUnit(g, v)
        if FS_Alive(v) and IsUnitAlly(v, GetOwningPlayer(u)) and not IsUnitType(v, UNIT_TYPE_STRUCTURE) and not IsUnitHidden(v) and GetUnitAbilityLevel(v, 'Aloc') == 0 then
            call SetWidgetLife(v, RMinBJ(GetUnitState(v, UNIT_STATE_MAX_LIFE), GetWidgetLife(v)+amount))
            call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Items\\AIhe\\AIheTarget.mdl", v, "origin"))
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    set v = null
    set burp = null
endfunction

function MD_OnDeath takes nothing returns nothing
    local unit v = GetTriggerUnit()
    local unit u = LoadUnitHandle(MD_Hash, GetHandleId(v), 10)
    local integer rank
    if u != null then
        if FS_Alive(u) and GetKillingUnit() == u and GetOwningPlayer(u) == LoadPlayerHandle(MD_Hash, GetHandleId(u), 3) and (IsUnitHidden(v) or IsUnitInTransport(v, u) or LoadBoolean(MD_Hash, GetHandleId(u), 5)) then
            set rank = LoadInteger(MD_Hash, GetHandleId(u), 2)
            // This handler precedes the map's XP handlers. Share at Mundo's current location.
            call SetUnitX(v, GetUnitX(u))
            call SetUnitY(v, GetUnitY(u))
            call MD_Clear(u)
            call MD_Burst(u, rank)
        else
            call MD_Clear(u)
        endif
    endif
    if GetUnitTypeId(v) == 'HMu1' then
        call MD_Clear(v)
    endif
    set u = null
    set v = null
endfunction

function MD_Init takes nothing returns nothing
    local trigger t = CreateTrigger()
    set MDV_Code[1] = 'mD00'
    set MDV_Code[2] = 'mD01'
    set MDV_Code[3] = 'mD02'
    set MDV_Code[4] = 'mD03'
    set MDV_Code[5] = 'mD04'
    set MDV_Code[6] = 'mD05'
    set MDV_Code[7] = 'mD06'
    set MDV_Code[8] = 'mD07'
    set MDV_Code[9] = 'mD08'
    set MDV_Code[10] = 'mD09'
    set MDV_Code[11] = 'mD0A'
    set MDV_Code[12] = 'mD0B'
    set MDV_Code[13] = 'mD0C'
    set MDV_Code[14] = 'mD0D'
    set MDV_Code[15] = 'mD0E'
    set MDV_Code[16] = 'mD0F'
    set MDV_Code[17] = 'mD10'
    set MDV_Code[18] = 'mD11'
    set MDV_Code[19] = 'mD12'
    set MDV_Code[20] = 'mD13'
    set MDV_Code[21] = 'mD14'
    set MDV_Code[22] = 'mD15'
    set MDV_Code[23] = 'mD16'
    set MDV_Code[24] = 'mD17'
    set MDV_Code[25] = 'mD18'
    set MDV_Code[26] = 'mD19'
    set MDV_Code[27] = 'mD1A'
    set MDV_Code[28] = 'mD1B'
    set MDV_Code[29] = 'mD1C'
    set MDV_Code[30] = 'mD1D'
    set MDV_Code[31] = 'mD1E'
    set MDV_Code[32] = 'mD1F'
    set MDV_Code[33] = 'mD20'
    set MDV_Code[34] = 'mD21'
    set MDV_Code[35] = 'mD22'
    set MDV_Code[36] = 'mD23'
    set MDV_Code[37] = 'mD24'
    set MDV_Code[38] = 'mD25'
    set MDV_Code[39] = 'mD26'
    set MDV_Code[40] = 'mD27'
    set MDV_Code[41] = 'mD28'
    set MDV_Code[42] = 'mD29'
    set MDV_Code[43] = 'mD2A'
    set MDV_Code[44] = 'mD2B'
    set MDV_Code[45] = 'mD2C'
    set MDV_Code[46] = 'mD2D'
    set MDV_Code[47] = 'mD2E'
    set MDV_Code[48] = 'mD2F'
    set MDV_Code[49] = 'mD30'
    set MDV_Code[50] = 'mD31'
    set MDV_Code[51] = 'mD32'
    set MDV_Code[52] = 'mD33'
    set MDV_Code[53] = 'mD34'
    set MDV_Code[54] = 'mD35'
    set MDV_Code[55] = 'mD36'
    set MDV_Code[56] = 'mD37'
    set MDV_Code[57] = 'mD38'
    set MDV_Code[58] = 'mD39'
    set MDV_Code[59] = 'mD3A'
    set MDV_Code[60] = 'mD3B'
    set MDV_Code[61] = 'mD3C'
    set MDV_Code[62] = 'mD3D'
    set MDV_Code[63] = 'mD3E'
    set MDV_Code[64] = 'mD3F'
    set MDV_Code[65] = 'mD40'
    set MDV_Code[66] = 'mD41'
    set MDV_Code[67] = 'mD42'
    set MDV_Code[68] = 'mD43'
    set MDV_Code[69] = 'mD44'
    set MDV_Code[70] = 'mD45'
    set MDV_Code[71] = 'mD46'
    set MDV_Code[72] = 'mD47'
    set MDV_Code[73] = 'mD48'
    set MDV_Code[74] = 'mD49'
    set MDV_Code[75] = 'mD4A'
    set MDV_Code[76] = 'mD4B'
    set MDV_Code[77] = 'mD4C'
    set MDV_Code[78] = 'mD4D'
    set MDV_Code[79] = 'mD4E'
    set MDV_Code[80] = 'mD4F'
    set MDV_Code[81] = 'mD50'
    set MDV_Code[82] = 'mD51'
    set MDV_Code[83] = 'mD52'
    set MDV_Code[84] = 'mD53'
    set MDV_Code[85] = 'mD54'
    set MDV_Code[86] = 'mD55'
    set MDV_Code[87] = 'mD56'
    set MDV_Code[88] = 'mD57'
    set MDV_Code[89] = 'mD58'
    set MDV_Code[90] = 'mD59'
    set MDV_Code[91] = 'mD5A'
    set MDV_Code[92] = 'mD5B'
    set MDV_Code[93] = 'mD5C'
    set MDV_Code[94] = 'mD5D'
    set MDV_Code[95] = 'mD5E'
    set MDV_Code[96] = 'mD5F'
    set MDV_Code[97] = 'mD60'
    set MDV_Code[98] = 'mD61'
    set MDV_Code[99] = 'mD62'
    set MDV_Code[100] = 'mD63'
    set MDV_Code[101] = 'mD64'
    set MDV_Code[102] = 'mD65'
    set MDV_Code[103] = 'mD66'
    set MDV_Code[104] = 'mD67'
    set MDV_Code[105] = 'mD68'
    set MDV_Code[106] = 'mD69'
    set MDV_Code[107] = 'mD6A'
    set MDV_Code[108] = 'mD6B'
    set MDV_Code[109] = 'mD6C'
    set MDV_Code[110] = 'mD6D'
    set MDV_Code[111] = 'mD6E'
    set MDV_Code[112] = 'mD6F'
    set MDV_Code[113] = 'mD70'
    set MDV_Code[114] = 'mD71'
    set MDV_Code[115] = 'mD72'
    set MDV_Code[116] = 'mD73'
    set MDV_Code[117] = 'mD74'
    set MDV_Code[118] = 'mD75'
    set MDV_Code[119] = 'mD76'
    set MDV_Code[120] = 'mD77'
    set MDV_Code[121] = 'mD78'
    set MDV_Code[122] = 'mD79'
    set MDV_Code[123] = 'mD7A'
    set MDV_Code[124] = 'mD7B'
    set MDV_Code[125] = 'mD7C'
    set MDV_Code[126] = 'mD7D'
    set MDV_Code[127] = 'mD7E'
    set MDV_Code[128] = 'mD7F'
    set MDV_Code[129] = 'mD80'
    set MDV_Code[130] = 'mD81'
    set MDV_Code[131] = 'mD82'
    set MDV_Code[132] = 'mD83'
    set MDV_Code[133] = 'mD84'
    set MDV_Code[134] = 'mD85'
    set MDV_Code[135] = 'mD86'
    set MDV_Code[136] = 'mD87'
    set MDV_Code[137] = 'mD88'
    set MDV_Code[138] = 'mD89'
    set MDV_Code[139] = 'mD8A'
    set MDV_Code[140] = 'mD8B'
    set MDV_Code[141] = 'mD8C'
    set MDV_Code[142] = 'mD8D'
    set MDV_Code[143] = 'mD8E'
    set MDV_Code[144] = 'mD8F'
    set MDV_Code[145] = 'mD90'
    set MDV_Code[146] = 'mD91'
    set MDV_Code[147] = 'mD92'
    set MDV_Code[148] = 'mD93'
    set MDV_Code[149] = 'mD94'
    set MDV_Code[150] = 'mD95'
    set MDV_Code[151] = 'mD96'
    set MDV_Code[152] = 'mD97'
    set MDV_Code[153] = 'mD98'
    set MDV_Code[154] = 'mD99'
    set MDV_Code[155] = 'mD9A'
    set MDV_Code[156] = 'mD9B'
    set MDV_Code[157] = 'mD9C'
    set MDV_Code[158] = 'mD9D'
    set MDV_Code[159] = 'mD9E'
    set MDV_Code[160] = 'mD9F'
    set MDV_Code[161] = 'mDA0'
    set MDV_Code[162] = 'mDA1'
    set MDV_Code[163] = 'mDA2'
    set MDV_Code[164] = 'mDA3'
    set MDV_Code[165] = 'mDA4'
    set MDV_Code[166] = 'mDA5'
    set MDV_Code[167] = 'mDA6'
    set MDV_Code[168] = 'mDA7'
    set MDV_Code[169] = 'mDA8'
    set MDV_Code[170] = 'mDA9'
    set MDV_Code[171] = 'mDAA'
    set MDV_Code[172] = 'mDAB'
    set MDV_Code[173] = 'mDAC'
    set MDV_Code[174] = 'mDAD'
    set MDV_Code[175] = 'mDAE'
    set MDV_Code[176] = 'mDAF'
    set MDV_Code[177] = 'mDB0'
    set MDV_Code[178] = 'mDB1'
    set MDV_Code[179] = 'mDB2'
    set MDV_Code[180] = 'mDB3'
    set MDV_Code[181] = 'mDB4'
    set MDV_Code[182] = 'mDB5'
    set MDV_Code[183] = 'mDB6'
    set MDV_Code[184] = 'mDB7'
    set MDV_Code[185] = 'mDB8'
    set MDV_Code[186] = 'mDB9'
    set MDV_Code[187] = 'mDBA'
    set MDV_Code[188] = 'mDBB'
    set MDV_Code[189] = 'mDBC'
    set MDV_Code[190] = 'mDBD'
    set MDV_Code[191] = 'mDBE'
    set MDV_Code[192] = 'mDBF'
    set MDV_Code[193] = 'mDC0'
    set MDV_Code[194] = 'mDC1'
    set MDV_Code[195] = 'mDC2'
    set MDV_Code[196] = 'mDC3'
    set MDV_Code[197] = 'mDC4'
    set MDV_Code[198] = 'mDC5'
    set MDV_Code[199] = 'mDC6'
    set MDV_Code[200] = 'mDC7'
    set MDV_Code[201] = 'mDC8'
    set MDV_Code[202] = 'mDC9'
    set MDV_Code[203] = 'mDCA'
    set MDV_Code[204] = 'mDCB'
    set MDV_Code[205] = 'mDCC'
    set MDV_Code[206] = 'mDCD'
    set MDV_Code[207] = 'mDCE'
    set MDV_Code[208] = 'mDCF'
    set MDV_Code[209] = 'mDD0'
    set MDV_Code[210] = 'mDD1'
    set MDV_Code[211] = 'mDD2'
    set MDV_Code[212] = 'mDD3'
    set MDV_Code[213] = 'mDD4'
    set MDV_Code[214] = 'mDD5'
    set MDV_Code[215] = 'mDD6'
    set MDV_Code[216] = 'mDD7'
    set MDV_Code[217] = 'mDD8'
    set MDV_Code[218] = 'mDD9'
    set MDV_Code[219] = 'mDDA'
    set MDV_Code[220] = 'mDDB'
    set MDV_Code[221] = 'mDDC'
    set MDV_Code[222] = 'mDDD'
    set MDV_Code[223] = 'mDDE'
    set MDV_Code[224] = 'mDDF'
    set MDV_Code[225] = 'mDE0'
    set MDV_Code[226] = 'mDE1'
    set MDV_Code[227] = 'mDE2'
    set MDV_Code[228] = 'mDE3'
    set MDV_Code[229] = 'mDE4'
    set MDV_Code[230] = 'mDE5'
    set MDV_Code[231] = 'mDE6'
    set MDV_Code[232] = 'mDE7'
    set MDV_Code[233] = 'mDE8'
    set MDV_Code[234] = 'mDE9'
    set MDV_Code[235] = 'mDEA'
    set MDV_Code[236] = 'mDEB'
    set MDV_Code[237] = 'mDEC'
    set MDV_Code[238] = 'mDED'
    set MDV_Code[239] = 'mDEE'
    set MDV_Code[240] = 'mDEF'
    set MDV_Code[241] = 'mDF0'
    set MDV_Code[242] = 'mDF1'
    set MDV_Code[243] = 'mDF2'
    set MDV_Code[244] = 'mDF3'
    set MDV_Code[245] = 'mDF4'
    set MDV_Code[246] = 'mDF5'
    set MDV_Code[247] = 'mDF6'
    set MDV_Code[248] = 'mDF7'
    set MDV_Code[249] = 'mDF8'
    set MDV_Code[250] = 'mDF9'
    set MDV_Code[251] = 'mDFA'
    set MDV_Code[252] = 'mDFB'
    set MDV_Code[253] = 'mDFC'
    set MDV_Code[254] = 'mDFD'
    set MDV_Code[255] = 'mDFE'
    set MDV_Code[256] = 'mDFF'
    call MD_InitTypes()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddAction(t, function MD_OnDeath)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DAMAGED)
    call TriggerAddAction(t, function MD_OnDamage)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_ISSUED_TARGET_ORDER)
    call TriggerAddAction(t, function MD_OnOrder)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SPELL_CHANNEL)
    call TriggerAddAction(t, function MD_OnChannel)
    set t = null
endfunction

function MU_Init takes nothing returns nothing
    local trigger cast = CreateTrigger()
    local trigger death = CreateTrigger()
    local trigger enter = CreateTrigger()
    local region world = CreateRegion()
    local rect bounds = AR_MatchBounds()
    local group existing = CreateGroup()
    local unit u
    call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 1", 0)
    call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 1|nFlip heroes and creeps behind you for 50 damage, or swallow a lesser unit. Digestion heals you and restores 200 health to nearby allies when it finishes.", 0)
    call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 2", 1)
    call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 4|nFlip heroes and creeps behind you for 80 damage, or swallow a lesser unit. Digestion heals you and restores 250 health to nearby allies when it finishes.", 1)
    call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 3", 2)
    call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 7|nFlip heroes and creeps behind you for 110 damage, or swallow a lesser unit. Digestion heals you and restores 300 health to nearby allies when it finishes.", 2)
    call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 4", 3)
    call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 10|nFlip heroes and creeps behind you for 140 damage, or swallow a lesser unit. Digestion heals you and restores 350 health to nearby allies when it finishes.", 3)
    call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 5", 4)
    call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 13|nFlip heroes and creeps behind you for 170 damage, or swallow a lesser unit. Digestion heals you and restores 400 health to nearby allies when it finishes.", 4)
    call BlzSetAbilityResearchTooltip('AMu3', "Learn Maul [|cffffcc00E|r] - Level 6", 5)
    call BlzSetAbilityResearchExtendedTooltip('AMu3', "Requires hero level 16|nFlip heroes and creeps behind you for 200 damage, or swallow a lesser unit. Digestion heals you and restores 450 health to nearby allies when it finishes.", 5)
    set MW_Hash = InitHashtable()
    set MU_Hash = InitHashtable()
    set MU_Timer = CreateTimer()
    set MU_CleaverHit = CreateTrigger()
    call TriggerAddCondition(MU_CleaverHit, Condition(function MU_CleaverFilter))
    call TriggerAddAction(MU_CleaverHit, function MU_OnCleaverHit)
    call TriggerAddAction(MQ_FinishTrigger, function MQ_Finish)
    call TriggerAddAction(MQ_RemoveTrigger, function MQ_Remove)
    call TriggerRegisterAnyUnitEventBJ(cast, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddAction(cast, function MU_OnCast)
    call TriggerRegisterAnyUnitEventBJ(death, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddAction(death, function MU_OnDeath)
    call RegionAddRect(world, bounds)
    call TriggerRegisterEnterRegion(enter, world, null)
    call TriggerAddAction(enter, function MU_OnEnter)
    call GroupEnumUnitsInRect(existing, bounds, null)
    loop
        set u = FirstOfGroup(existing)
        exitwhen u == null
        call GroupRemoveUnit(existing, u)
        call MU_Register(u)
    endloop
    call DestroyGroup(existing)
    call RemoveRect(bounds)
    call TimerStart(MU_Timer, 0.25, true, function MU_Tick)
    call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 1", 0)
    call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 80 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 0)
    call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 2", 1)
    call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 120 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 1)
    call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 3", 2)
    call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 160 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 2)
    call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 4", 3)
    call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 200 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 3)
    call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 5", 4)
    call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 240 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 4)
    call BlzSetAbilityResearchTooltip('AMu1', "Learn Infected Cleaver [|cffffcc00Q|r] - Level 6", 5)
    call BlzSetAbilityResearchExtendedTooltip('AMu1', "Throw a cleaver for 280 base damage and a slow. Distance and missing health increase damage. Retrieve it to throw again. Recovering a bloodied blade empowers the next hit.", 5)
    call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 1", 0)
    call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 35-70 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 0)
    call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 2", 1)
    call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 50-100 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 1)
    call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 3", 2)
    call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 65-130 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 2)
    call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 4", 3)
    call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 80-160 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 3)
    call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 5", 4)
    call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 95-190 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 4)
    call BlzSetAbilityResearchTooltip('AMu2', "Learn Poison Gas - Level 6", 5)
    call BlzSetAbilityResearchExtendedTooltip('AMu2', "Drain your health to poison nearby enemies for 110-220 damage per second. The cloud grows stronger over 10 seconds and grants spell resistance.", 5)
    call BlzSetAbilityResearchTooltip('AMu4', "Learn Undying - Level 1", 0)
    call BlzSetAbilityResearchExtendedTooltip('AMu4', "Spend 20% of current health. Transform for 15s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 0)
    call BlzSetAbilityResearchTooltip('AMu4', "Learn Undying - Level 2", 1)
    call BlzSetAbilityResearchExtendedTooltip('AMu4', "Spend 20% of current health. Transform for 18s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 1)
    call BlzSetAbilityResearchTooltip('AMu4', "Learn Undying - Level 3", 2)
    call BlzSetAbilityResearchExtendedTooltip('AMu4', "Spend 20% of current health. Transform for 21s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 2)
    set cast = null
    set death = null
    set enter = null
    set world = null
    set bounds = null
    set existing = null
    set u = null
endfunction

function DR_Damage takes nothing returns nothing
    local unit u = GetTriggerUnit()
    local integer i = LoadInteger(DK_Hash, GetHandleId(u), -40)
    local real damage = GetEventDamage()
    if i != 0 and DK_Kind[i] == 10 and FS_Alive(u) and DK_End[i] > DK_Now and GetOwningPlayer(u) == DK_Owner[i] and damage > 0.0 then
        if damage >= GetWidgetLife(u)-1.0 then
            if DK_Stacks[i] == 0 then
                set DK_Stacks[i] = 1
                set DK_End[i] = DK_Now+10.0
                call DK_Text(u, GetOwningPlayer(u), "Refuse Death: 10 seconds", 255, 50, 50)
            endif
            call BlzSetEventDamage(RMaxBJ(0.0, GetWidgetLife(u)-1.0))
        endif
    endif
    set u = null
endfunction

function DR_Init takes nothing returns nothing
    local trigger t = CreateTrigger()
    // Register after shield/resistance handlers so only remaining lethal damage counts.
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DAMAGED)
    call TriggerAddAction(t, function DR_Damage)
    set t = null
endfunction

function MQ_Control takes unit source, unit target, integer abilityId, string order returns nothing
    local unit dummy = CreateUnit(GetOwningPlayer(source), 'dmmy', GetUnitX(target), GetUnitY(target), 0.0)
    call UnitAddAbility(dummy, abilityId)
    call IssueTargetOrder(dummy, order, target)
    call UnitApplyTimedLife(dummy, 'BTLF', 1.5)
    set dummy = null
endfunction
