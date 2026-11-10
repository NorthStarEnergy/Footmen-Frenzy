// Pub early progression. All rewards still originate from kills.
function P67_Enabled takes nothing returns boolean
    return udg_mode_pub and not FFR4Pro and not udg_mode_promode and not FFMode4K and not FFModePrivateVote and not udg_mode_inhouse and not udg_mode_debugmode and not udg_mode_overdrive and not udg_FFCH_Mode and not udg_mode_no_mass and udg_colossal_on
endfunction

function P67_ValidHero takes unit u returns boolean
    local integer pn
    if u == null or GetUnitTypeId(u) == 0 or not IsUnitType(u, UNIT_TYPE_HERO) or IsUnitIllusion(u) then
        return false
    endif
    set pn = GetPlayerId(GetOwningPlayer(u)) + 1
    if pn < 1 or pn > 12 then
        return false
    endif
    return udg_player_active[pn] and udg_herO[pn] == u
endfunction

// Percent, not a multiplier. Kept pure for boundary tests and tuning.
function P67_Rate takes integer level, boolean reached4, boolean reached6, boolean massEnded, boolean firstColo returns real
    if level >= 7 then
        return P67_POST7_RATE
    endif
    if firstColo or (level < 4 and reached4) then
        return P67_CATCHUP_RATE
    endif
    if level < 6 and (massEnded or reached6) then
        return P67_APPROACH6_RATE
    endif
    return 100.00
endfunction

function P67_HeroRate takes unit u returns real
    local integer pn = GetPlayerId(GetOwningPlayer(u)) + 1
    // Keep the existing anti-cheat XP penalty authoritative.
    if udg_maphack[pn] then
        return 25.00
    endif
    return P67_Rate(GetHeroLevel(u), P67_Reached4, P67_Reached6, P67_MassEnded, P67_FirstColo)
endfunction

function P67_Refresh takes nothing returns nothing
    local integer pn = 1
    local unit u
    if not P67_Running or not P67_Enabled() then
        return
    endif
    // Discover both milestones before calculating anyone's rate. Slot order
    // must not affect catch-up, and a skipped level must still unlock it.
    loop
        exitwhen pn > 12
        set u = udg_herO[pn]
        if P67_ValidHero(u) then
            if GetHeroLevel(u) >= 4 then
                set P67_Reached4 = true
            endif
            if GetHeroLevel(u) >= 6 then
                set P67_Reached6 = true
            endif
        endif
        set pn = pn + 1
    endloop
    set pn = 1
    loop
        exitwhen pn > 12
        set u = udg_herO[pn]
        if P67_ValidHero(u) then
            call SetPlayerHandicapXPBJ(Player(pn - 1), P67_HeroRate(u))
        endif
        set pn = pn + 1
    endloop
    set u = null
endfunction

function P67_OnLevel takes nothing returns nothing
    if P67_ValidHero(GetTriggerUnit()) then
        call P67_Refresh()
    endif
endfunction

function P67_AddSupplement takes unit u, real amount returns nothing
    local integer pn
    local integer earned
    local real total
    if not P67_ValidHero(u) or amount <= 0.00 then
        return
    endif
    set pn = GetPlayerId(GetOwningPlayer(u)) + 1
    if P67_LastHero[pn] != u then
        set P67_LastHero[pn] = u
        set P67_Remainder[pn] = 0.00
    endif
    // These scripted supplements use SetHeroXP, so native handicap alone
    // cannot slow them. Preserve fractional XP from sharing and scaling.
    set total = P67_Remainder[pn] + amount * P67_HeroRate(u) * 0.01
    set earned = R2I(total)
    set P67_Remainder[pn] = total - I2R(earned)
    if earned > 0 then
        call SetHeroXP(u, GetHeroXP(u) + earned, true)
    endif
endfunction

function P67_MassFinished takes nothing returns nothing
    if P67_Enabled() then
        set P67_MassEnded = true
        call P67_Refresh()
    endif
endfunction

function P67_ColoSpawn takes nothing returns nothing
    if P67_Enabled() and udg_colossal_wave == 1 then
        // Activate before any of the first wave's kills can award XP.
        set P67_FirstColo = true
        call P67_Refresh()
    endif
endfunction

function P67_Start takes nothing returns nothing
    if P67_Running or not P67_Enabled() then
        return
    endif
    set P67_Running = true
    call P67_Refresh()
    // Covers hiring, repicks, substitutions and revives. This only sets the
    // rate: no timer, milestone or wave event awards any experience.
    call TimerStart(CreateTimer(), 1.00, true, function P67_Refresh)
    call DisplayTextToForce(GetPlayersAll(), "|cff00ffffPub XP:|r Earn boosted kill XP while catching up to level 7. From level 7 onward, kill XP is 70%.")
endfunction
