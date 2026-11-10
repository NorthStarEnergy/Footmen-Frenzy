// Unique rawcodes keep each Mundo's meal icon/tooltip/cooldown independent.
function MDV_Clear takes unit u returns nothing
    local integer h = GetHandleId(u)
    local integer slot = LoadInteger(MD_Hash, h, 21)
    if slot > 0 then
        call UnitRemoveAbility(u, MDV_Code[slot])
        set MDV_Used[slot] = false
    endif
    call DestroyEffect(LoadEffectHandle(MD_Hash, h, 22))
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
        call DestroyEffect(AddSpecialEffectTarget("Objects\\Spawnmodels\\Human\\HumanBlood\\HumanBloodLarge0.mdl", u, "chest"))
        call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilSpecialArt.mdl", u, "chest"))
    endif
    set abilityId = MDV_Code[slot]
    call BlzSetAbilityExtendedTooltip(abilityId, "Inside Mundo: " + GetUnitName(v) + "|nRemaining health: " + I2S(R2I(GetWidgetLife(v))) + "|nEstimated digestion time: " + I2S(R2I(left + 0.99)) + " sec.|nThe cooldown shows the estimate, updated from actual digestion damage. This is a status indicator; the meal cannot be released manually.", 0)
    call BlzStartUnitAbilityCooldown(u, abilityId, RMaxBJ(0.25, left))
    set fx = null
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


