// Multiplicative reward factor. Fractional levels make the transition smooth.
function P80_Curve takes real ownLevel, real opposingLevel returns real
    if ownLevel < I2R(P80_MIN_LEVEL) or opposingLevel <= 0.00 then
        return 1.00
    endif
    return 1.00 - RMinBJ(P80_MAX_REDUCTION, RMaxBJ(0.00, ownLevel - opposingLevel - P80_FREE_LEAD) * P80_REDUCTION_PER_LEVEL)
endfunction

function P80_TeamLevel takes integer team returns real
    local integer pn = 1
    local integer count = 0
    local real total = 0.00
    if team < 1 or team > 4 then
        return 0.00
    endif
    loop
        exitwhen pn > 12
        // Dead heroes count: dying must not lower the team's protection baseline.
        if udg_teamnumber[pn] == team and P67_ValidHero(udg_herO[pn]) then
            set total = total + P79_FractionalLevel(udg_herO[pn])
            set count = count + 1
        endif
        set pn = pn + 1
    endloop
    if count == 0 then
        return 0.00
    endif
    return total / I2R(count)
endfunction

function P80_Factor takes unit hero, unit victim returns real
    local integer pn
    local real baseline
    if not P67_Enabled() or not P67_ValidHero(hero) or victim == null then
        return 1.00
    endif
    set pn = GetPlayerId(GetOwningPlayer(victim)) + 1
    if pn < 1 or pn > 12 or not IsUnitEnemy(victim, GetOwningPlayer(hero)) or IsUnitType(victim, UNIT_TYPE_STRUCTURE) then
        return 1.00
    endif
    set baseline = P80_TeamLevel(udg_teamnumber[pn])
    if baseline <= 0.00 then
        return 1.00
    endif
    if IsUnitType(victim, UNIT_TYPE_HERO) then
        set baseline = RMaxBJ(baseline, P79_FractionalLevel(victim))
    endif
    return P80_Curve(P79_FractionalLevel(hero), baseline)
endfunction

function P80_Gold takes player recipient, unit victim, integer amount returns integer
    local integer pn = GetPlayerId(recipient) + 1
    local real total
    local integer earned
    if pn < 1 or pn > 12 or amount <= 0 or not P80_Running or not P67_Enabled() then
        return amount
    endif
    set total = I2R(amount) * P80_Factor(udg_herO[pn], victim) + P80_GoldRemainder[pn]
    set earned = R2I(total)
    set P80_GoldRemainder[pn] = total - I2R(earned)
    return earned
endfunction

// Map's GrantHeroXP table and native GrantNormalXP recurrence.
function P80_BaseXP takes integer level, boolean hero returns integer
    if level < 1 then
        return 0
    endif
    if not hero then
        return (5 * level * level + 15 * level + 30) / 2
    endif
    if level == 1 then
        return 100
    endif
    if level == 2 then
        return 120
    endif
    if level == 3 then
        return 160
    endif
    if level == 4 then
        return 220
    endif
    if level == 5 then
        return 300
    endif
    if level <= 14 then
        return (level - 2) * 100
    endif
    if level == 15 then
        return 1400
    endif
    if level == 16 then
        return 1800
    endif
    if level == 17 then
        return 2000
    endif
    return 2200
endfunction

function P80_Receiver takes unit hero, player killer returns boolean
    return P67_ValidHero(hero) and IsUnitAliveBJ(hero) and GetHeroLevel(hero) < 18 and not IsSuspendedXP(hero) and IsUnitAlly(hero, killer)
endfunction

// Native XP is replaced in normal Pub so the discount is applied BEFORE XP
// can level a hero. No post-kill XP removal or skill-point rollback.
function P80_OnDeath takes nothing returns nothing
    local unit victim = GetTriggerUnit()
    local unit killer = GetKillingUnit()
    local player owner
    local integer vp
    local integer kp
    local integer pn = 1
    local integer count = 0
    local integer nearby = 0
    local integer id
    local integer bounty
    local integer dice
    local integer sides
    local real baseXP
    local real amount
    local real total
    local integer earned
    local real dx
    local real dy
    local unit hero
    local texttag tag
    if not P80_Running or not P67_Enabled() or killer == null or IsUnitIllusion(victim) then
        set victim = null
        set killer = null
        return
    endif
    set owner = GetOwningPlayer(killer)
    set kp = GetPlayerId(owner) + 1
    set vp = GetPlayerId(GetOwningPlayer(victim)) + 1
    if kp < 1 or kp > 12 or not IsUnitEnemy(victim, owner) then
        set victim = null
        set killer = null
        set owner = null
        return
    endif
    // Neutral bounty stays native. Player victims use the same authored dice.
    if vp >= 1 and vp <= 12 and P80_BountyWasOn[vp] then
        set bounty = BlzGetUnitIntegerField(victim, UNIT_IF_GOLD_BOUNTY_AWARDED_BASE)
        set dice = BlzGetUnitIntegerField(victim, UNIT_IF_GOLD_BOUNTY_AWARDED_NUMBER_OF_DICE)
        set sides = BlzGetUnitIntegerField(victim, UNIT_IF_GOLD_BOUNTY_AWARDED_SIDES_PER_DIE)
        loop
            exitwhen dice <= 0 or sides <= 0
            set bounty = bounty + GetRandomInt(1, sides)
            set dice = dice - 1
        endloop
        set bounty = P80_Gold(owner, victim, bounty)
        if bounty > 0 then
            call SetPlayerState(owner, PLAYER_STATE_RESOURCE_GOLD, GetPlayerState(owner, PLAYER_STATE_RESOURCE_GOLD) + bounty)
            set tag = CreateTextTag()
            call SetTextTagText(tag, "+" + I2S(bounty), 0.024)
            call SetTextTagPosUnit(tag, victim, 0.00)
            call SetTextTagColor(tag, 255, 220, 0, 255)
            call SetTextTagVelocity(tag, 0.00, 0.03)
            call SetTextTagPermanent(tag, false)
            call SetTextTagLifespan(tag, 2.00)
            call SetTextTagFadepoint(tag, 1.50)
            call SetTextTagVisibility(tag, GetLocalPlayer() == owner)
            set tag = null
        endif
    endif
    set baseXP = I2R(P80_BaseXP(GetUnitLevel(victim), IsUnitType(victim, UNIT_TYPE_HERO)))
    if IsUnitType(killer, UNIT_TYPE_STRUCTURE) or (IsUnitType(victim, UNIT_TYPE_STRUCTURE) and not BlzGetUnitWeaponBooleanField(victim, UNIT_WEAPON_BF_ATTACKS_ENABLED, 0) and not BlzGetUnitWeaponBooleanField(victim, UNIT_WEAPON_BF_ATTACKS_ENABLED, 1)) or GetUnitAbilityLevel(victim, 'Aloc') > 0 then
        set baseXP = 0.00
    endif
    if IsUnitType(victim, UNIT_TYPE_SUMMONED) then
        set baseXP = baseXP * 0.75
    endif
    set P80_Sequence = P80_Sequence + 1
    set id = P80_Sequence
    // Snapshot recipients, rates and penalties before any level-up callbacks.
    loop
        exitwhen pn > 12
        set hero = udg_herO[pn]
        if baseXP > 0.00 and P80_Receiver(hero, owner) then
            set dx = GetUnitX(hero) - GetUnitX(victim)
            set dy = GetUnitY(hero) - GetUnitY(victim)
            if dx * dx + dy * dy <= 1440000.00 then
                call SaveBoolean(P80_Rewards, id, pn + 24, true)
                set nearby = nearby + 1
            endif
            call SaveUnitHandle(P80_Rewards, id, pn, hero)
            call SaveReal(P80_Rewards, id, pn + 12, baseXP * P67_HeroRate(hero) * 0.01 * P80_Factor(hero, victim))
            set count = count + 1
        endif
        set pn = pn + 1
    endloop
    if nearby > 0 then
        set count = nearby
    endif
    set pn = 1
    loop
        exitwhen pn > 12
        set hero = LoadUnitHandle(P80_Rewards, id, pn)
        if hero != null and count > 0 and (nearby == 0 or LoadBoolean(P80_Rewards, id, pn + 24)) then
            if P80_LastHero[pn] != hero then
                set P80_LastHero[pn] = hero
                set P80_XPRemainder[pn] = 0.00
            endif
            set amount = LoadReal(P80_Rewards, id, pn + 12) / I2R(count)
            set total = P80_XPRemainder[pn] + amount
            set earned = R2I(total)
            set P80_XPRemainder[pn] = total - I2R(earned)
            if earned > 0 then
                call SetHeroXP(hero, GetHeroXP(hero) + earned, true)
            endif
        endif
        set pn = pn + 1
    endloop
    call FlushChildHashtable(P80_Rewards, id)
    set victim = null
    set killer = null
    set owner = null
    set hero = null
endfunction

function P80_Init takes nothing returns nothing
    local trigger death
    if not P80_Initialized then
        set P80_Initialized = true
        set P80_Rewards = InitHashtable()
        set death = CreateTrigger()
        call TriggerRegisterAnyUnitEventBJ(death, EVENT_PLAYER_UNIT_DEATH)
        call TriggerAddAction(death, function P80_OnDeath)
    endif
    set death = null
endfunction

function P80_Start takes nothing returns nothing
    local integer pn = 1
    if P80_Running or not P67_Enabled() then
        return
    endif
    call P80_Init()
    set P80_Running = true
    loop
        exitwhen pn > 12
        set P80_BountyWasOn[pn] = GetPlayerState(Player(pn - 1), PLAYER_STATE_GIVES_BOUNTY) != 0
        call SetPlayerState(Player(pn - 1), PLAYER_STATE_GIVES_BOUNTY, 0)
        call SetPlayerHandicapXPBJ(Player(pn - 1), 0.00)
        set pn = pn + 1
    endloop
endfunction

function P80_Sync takes nothing returns nothing
    local integer pn = 1
    if P67_Enabled() then
        call P80_Start()
    elseif P80_Running then
        set P80_Running = false
        loop
            exitwhen pn > 12
            if P80_BountyWasOn[pn] then
                call SetPlayerState(Player(pn - 1), PLAYER_STATE_GIVES_BOUNTY, 1)
            endif
            if udg_maphack[pn] then
                call SetPlayerHandicapXPBJ(Player(pn - 1), 25.00)
            else
                call SetPlayerHandicapXPBJ(Player(pn - 1), 100.00)
            endif
            set pn = pn + 1
        endloop
    endif
endfunction
