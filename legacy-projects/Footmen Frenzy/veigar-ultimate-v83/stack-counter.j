function VG82_UpdateCounter takes unit u returns nothing
    local ability a = BlzGetUnitAbility(u, 'AVgq')
    local integer stacks = LoadInteger(VG_Hash, GetHandleId(u), 702)
    local integer i = 0
    if a != null then
        loop
            exitwhen i >= 6
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL, i, "Baleful Strike [|cffffcc00Z|r] - |cff80dfff+" + I2S(stacks) + " damage|r")
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL_EXTENDED, i, "Deals " + I2S(150 + 70 * i) + " + 60% Intelligence + |cff80dfff" + I2S(stacks) + " permanent bonus|r magic damage.|n|nEvery enemy unit killed by Veigar grants +1 Z damage. Enemy heroes grant +5 instead. Attacks and all spells count. Illusions and structures do not count.|nStacks never reset, including on death.|n|nCurrent permanent bonus: |cff80dfff+" + I2S(stacks) + " damage|r")
            set i = i + 1
        endloop
    endif
    set a = BlzGetUnitAbility(u, 'AVgr')
    set stacks = LoadInteger(VG_Hash, GetHandleId(u), 703)
    set i = 0
    if a != null then
        loop
            exitwhen i >= 3
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL, i, "Primordial Burst [|cffffcc00V|r] - |cff80dfff+" + I2S(stacks) + " damage|r")
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL_EXTENDED, i, "Deals " + I2S(550 + 300 * i) + " + 120% Intelligence + 80% target Intelligence + |cff80dfff" + I2S(stacks) + " permanent bonus|r magic damage to an enemy hero.|n|nKills with Baleful Strike (Z) permanently grant +1 ultimate damage per enemy unit, or +5 per enemy hero. Other kill sources do not grant ultimate stacks. Illusions and structures do not count.|nStacks never reset, including on death.|n|nCurrent permanent bonus: |cff80dfff+" + I2S(stacks) + " damage|r")
            set i = i + 1
        endloop
    endif
    set a = null
endfunction
