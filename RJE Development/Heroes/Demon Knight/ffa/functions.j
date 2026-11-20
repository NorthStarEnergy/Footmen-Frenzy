function DK_GroundZ takes real x, real y returns real
    local location p = Location(x, y)
    local real z = GetLocationZ(p)
    call RemoveLocation(p)
    set p = null
    return z
endfunction

function DK_New takes integer kind, unit source returns integer
    local integer i = 1
    loop
        exitwhen i > DK_High or DK_Kind[i] == 0
        set i = i + 1
    endloop
    if i > 8190 then
        return 0
    endif
    set DK_High = IMaxBJ(DK_High, i)
    set DK_Kind[i] = kind
    set DK_Source[i] = source
    set DK_Owner[i] = GetOwningPlayer(source)
    set DK_End[i] = DK_Now + 5.0
    set DK_Stacks[i] = 0
    set DK_Parent[i] = 0
    set DK_Return[i] = false
    return i
endfunction

function DK_Beam takes unit source, real x, real y, boolean zap returns nothing
    local integer i = DK_New(9, source)
    local lightning beam
    local real z = DK_GroundZ(x, y)+90.0
    if i == 0 then
        return
    endif
    if zap then
        set beam = AddLightningEx("CLPB", true, x, y, z+1000.0, x, y, z)
    else
        set beam = AddLightningEx("DRAL", true, x, y, z, GetUnitX(source), GetUnitY(source), DK_GroundZ(GetUnitX(source), GetUnitY(source))+130.0)
    endif
    call SetLightningColor(beam, 1.0, 0.18, 0.18, 1.0)
    call SaveLightningHandle(DK_Hash, i, -30, beam)
    set DK_End[i] = DK_Now+0.65
    set beam = null
endfunction

function DK_Flash takes unit source, string model, real x, real y, real scale returns nothing
    local integer i = DK_New(7, source)
    if i != 0 then
        set DK_FX[i] = AddSpecialEffect(model, x, y)
        call BlzSetSpecialEffectScale(DK_FX[i], scale)
        call BlzSetSpecialEffectColor(DK_FX[i], 255, 70, 55)
        set DK_End[i] = DK_Now + 0.75
    endif
endfunction

function DK_Blast takes unit source, real x, real y, real radius returns nothing
    local integer i = DK_New(7, source)
    if i != 0 then
        set DK_FX[i] = AddSpecialEffect("Spells\\Orianna\\Feedback\\AttackRing.mdx", x, y)
        call BlzSetSpecialEffectZ(DK_FX[i], DK_GroundZ(x, y)+16.0)
        call BlzSetSpecialEffectScale(DK_FX[i], radius)
        call BlzPlaySpecialEffect(DK_FX[i], ANIM_TYPE_STAND)
        set DK_End[i] = DK_Now+1.5
    endif
    call DK_Flash(source, "Abilities\\Spells\\Other\\Doom\\DoomDeath.mdl", x, y, 2.0)
endfunction

function DK_Free takes integer i returns nothing
    if i == 0 or DK_Kind[i] == 0 then
        return
    endif
    if DK_Kind[i] == 10 then
        call DR_Stop(DK_Source[i])
    elseif DK_Kind[i] == 3 then
        if LoadTextTagHandle(DK_Hash, i, -20) != null then
            call DestroyTextTag(LoadTextTagHandle(DK_Hash, i, -20))
            call RemoveSavedHandle(DK_Hash, i, -20)
        endif
        call RemoveSavedInteger(DK_Hash, GetHandleId(DK_Source[i]), GetHandleId(DK_Target[i]))
    elseif DK_Kind[i] == 2 then
        if LoadInteger(DK_Hash, GetHandleId(DK_Target[i]), -3) == i then
            call RemoveSavedInteger(DK_Hash, GetHandleId(DK_Target[i]), -3)
        endif
    elseif DK_Kind[i] == 4 then
        call RemoveSavedInteger(DK_Hash, GetHandleId(DK_Source[i]), -2)
        if GetUnitTypeId(DK_Source[i]) != 0 then
            if FS_Alive(DK_Source[i]) then
                call ResetUnitAnimation(DK_Source[i])
            endif
        endif
    elseif DK_Kind[i] == 9 then
        call DestroyLightning(LoadLightningHandle(DK_Hash, i, -30))
        call RemoveSavedHandle(DK_Hash, i, -30)
    elseif DK_Kind[i] == 11 then
        if LoadLightningHandle(DK_Hash, i, -31) != null then
            call DestroyLightning(LoadLightningHandle(DK_Hash, i, -31))
            call RemoveSavedHandle(DK_Hash, i, -31)
        endif
    elseif DK_Kind[i] == 12 then
        if LoadInteger(DK_Hash, GetHandleId(DK_Target[i]), -32) == i then
            call RemoveSavedInteger(DK_Hash, GetHandleId(DK_Target[i]), -32)
        endif
    endif
    if DK_FX[i] != null then
        call DestroyEffect(DK_FX[i])
    endif
    if DK_Hit[i] != null then
        call DestroyGroup(DK_Hit[i])
    endif
    if DK_Pulled[i] != null then
        call DestroyGroup(DK_Pulled[i])
    endif
    set DK_FX[i] = null
    set DK_Hit[i] = null
    set DK_Pulled[i] = null
    set DK_Source[i] = null
    set DK_Target[i] = null
    set DK_Owner[i] = null
    set DK_Kind[i] = 0
    loop
        exitwhen DK_High == 0 or DK_Kind[DK_High] != 0
        set DK_High = DK_High - 1
    endloop
endfunction

function DK_UltHero takes unit u, player owner returns boolean
    return FS_Alive(u) and GetPlayerId(GetOwningPlayer(u)) < 12 and IsUnitEnemy(u, owner) and IsUnitType(u, UNIT_TYPE_HERO) and not IsUnitIllusion(u) and GetUnitAbilityLevel(u, 'Aloc') == 0
endfunction

function DK_EndRequiem takes integer i, boolean strike returns nothing
    local integer n = 1
    local unit source = DK_Source[i]
    local player owner = DK_Owner[i]
    local real damage = DK_Damage[i]
    local group targets = CreateGroup()
    local group allHeroes = CreateGroup()
    local unit v
    if i == 0 or DK_Kind[i] != 4 then
        call DestroyGroup(targets)
        call DestroyGroup(allHeroes)
        set targets = null
        set allHeroes = null
        set source = null
        set owner = null
        return
    endif
    if strike then
        call GroupEnumUnitsInRect(allHeroes, bj_mapInitialPlayableArea, null)
        loop
            set v = FirstOfGroup(allHeroes)
            exitwhen v == null
            call GroupRemoveUnit(allHeroes, v)
            if DK_UltHero(v, owner) and not IsUnitType(v, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(v) then
                call GroupAddUnit(targets, v)
            endif
        endloop
    endif
    call DestroyGroup(allHeroes)
    set allHeroes = null
    // Snapshot and detach the complete impact before damage callbacks can kill the caster.
    loop
        exitwhen n > DK_High
        if DK_Kind[n] == 5 and DK_Parent[n] == i then
            set v = DK_Target[n]
            call DK_Free(n)
        endif
        set n = n + 1
    endloop
    call DK_Free(i)
    if FS_Alive(source) and GetUnitCurrentOrder(source) == OrderId("channel") then
        call IssueImmediateOrder(source, "stop")
    endif
    if strike then
        call DK_Flash(source, "Abilities\\Spells\\Undead\\DeathPact\\DeathPactCaster.mdl", GetUnitX(source), GetUnitY(source), 1.3)
    endif
    loop
        set v = FirstOfGroup(targets)
        exitwhen v == null
        call GroupRemoveUnit(targets, v)
        call DK_Flash(source, "Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilSpecialArt.mdl", GetUnitX(v), GetUnitY(v), 1.15)
        call DK_Beam(source, GetUnitX(v), GetUnitY(v), true)
        call DK_Blast(source, GetUnitX(v), GetUnitY(v), 200.0)
        call FS_Hit(source, v, damage)
    endloop
    call DestroyGroup(targets)
    set targets = null
    set source = null
    set owner = null
    set v = null
endfunction

function DK_ChannelOrders takes nothing returns nothing
    local integer i = LoadInteger(DK_Hash, GetHandleId(GetTriggerUnit()), -2)
    // Ignore engine orders generated while entering the scripted channel.
    if i != 0 and DK_Kind[i] == 4 and DK_End[i]-DK_Now < 2.9375 then
        call DK_EndRequiem(i, false)
    endif
endfunction

function DK_BloodHit takes unit source, unit target returns nothing
    local integer i = DK_New(7, source)
    if i != 0 then
        set DK_FX[i] = AddSpecialEffectTarget("Objects\\Spawnmodels\\Human\\HumanBlood\\HumanBloodFootman.mdl", target, "chest")
        call BlzSetSpecialEffectScale(DK_FX[i], 1.5)
        set DK_End[i] = DK_Now+1.0
    endif
endfunction

function DK_PullLimit takes integer level returns real
    if level == 1 then
        return 100.0
    elseif level == 2 then
        return 150.0
    elseif level == 3 then
        return 200.0
    elseif level == 4 then
        return 350.0
    elseif level == 5 then
        return 450.0
    endif
    return 550.0
endfunction

function DK_MarkLabel takes integer i returns nothing
    local texttag tag = LoadTextTagHandle(DK_Hash, i, -20)
    if tag == null then
        set tag = CreateTextTag()
        call SaveTextTagHandle(DK_Hash, i, -20, tag)
        call SetTextTagPermanent(tag, true)
        call SetTextTagColor(tag, 255, 130, 130, 255)
    endif
    call SetTextTagText(tag, "Blood "+I2S(DK_Stacks[i])+"/6", 0.024)
    call SetTextTagPosUnit(tag, DK_Target[i], 160.0)
    call SetTextTagVisibility(tag, IsPlayerAlly(DK_Owner[i], GetLocalPlayer()) and IsUnitVisible(DK_Target[i], GetLocalPlayer()))
    set tag = null
endfunction

function DK_Mark takes unit source, unit target returns nothing
    local integer i
    local integer oldStacks
    if GetUnitAbilityLevel(source, 'ADk3') == 0 or not FS_Enemy(target, GetOwningPlayer(source)) then
        return
    endif
    set i = LoadInteger(DK_Hash, GetHandleId(source), GetHandleId(target))
    if i != 0 and DK_End[i] <= DK_Now then
        call DK_Free(i)
        set i = 0
    endif
    if i == 0 then
        set i = DK_New(3, source)
        if i == 0 then
            return
        endif
        set DK_Target[i] = target
        call SaveInteger(DK_Hash, GetHandleId(source), GetHandleId(target), i)
        set DK_FX[i] = AddSpecialEffectTarget("Abilities\\Spells\\Other\\HowlOfTerror\\HowlTarget.mdl", target, "overhead")
    endif
    set oldStacks = DK_Stacks[i]
    set DK_Stacks[i] = IMinBJ(6, oldStacks + 1)
    set DK_End[i] = DK_Now + 12.0
    call BlzSetSpecialEffectColor(DK_FX[i], 255, 40, 40)
    call BlzSetSpecialEffectScale(DK_FX[i], 1.1 + 0.12*DK_Stacks[i])
    call DK_MarkLabel(i)
endfunction

function DK_Strike takes unit source, unit target, real damage returns nothing
    call FS_Hit(source, target, damage)
    if FS_Alive(source) then
        call DK_Mark(source, target)
    endif
endfunction

function DK_AxeArea takes integer i, real ox, real oy returns nothing
    local group g = CreateGroup()
    local unit v
    local integer pull
    local real angle
    local real dx = DK_X[i]-ox
    local real dy = DK_Y[i]-oy
    local real length2 = dx*dx+dy*dy
    local real projection
    local real vx
    local real vy
    call GroupEnumUnitsInRange(g, (ox+DK_X[i])*0.5, (oy+DK_Y[i])*0.5, 180.0+SquareRoot(length2)*0.5, null)
    loop
        set v = FirstOfGroup(g)
        exitwhen v == null or DK_Kind[i] != 1 or not FS_Alive(DK_Source[i])
        call GroupRemoveUnit(g, v)
        set projection = 0.0
        if length2 > 0.01 then
            set projection = RMaxBJ(0.0, RMinBJ(1.0, ((GetUnitX(v)-ox)*dx+(GetUnitY(v)-oy)*dy)/length2))
        endif
        set vx = GetUnitX(v)-(ox+projection*dx)
        set vy = GetUnitY(v)-(oy+projection*dy)
        if vx*vx+vy*vy <= 32400.0 and FS_Enemy(v, DK_Owner[i]) then
            if not IsUnitInGroup(v, DK_Hit[i]) then
                call GroupAddUnit(DK_Hit[i], v)
                call DK_BloodHit(DK_Source[i], v)
                call DK_Strike(DK_Source[i], v, DK_Damage[i])
            endif
            if DK_Kind[i] == 1 and FS_Alive(DK_Source[i]) and DK_Return[i] and FS_Enemy(v, DK_Owner[i]) and not IsUnitInGroup(v, DK_Pulled[i]) then
                call GroupAddUnit(DK_Pulled[i], v)
                call DK_Free(LoadInteger(DK_Hash, GetHandleId(v), -3))
                call DK_Free(LoadInteger(DK_Hash, GetHandleId(v), -32))
                set pull = DK_New(2, DK_Source[i])
                if pull != 0 then
                    set DK_Target[pull] = v
                    call SaveInteger(DK_Hash, GetHandleId(v), -3, pull)
                    set angle = Atan2(GetUnitY(DK_Source[i])-GetUnitY(v), GetUnitX(DK_Source[i])-GetUnitX(v))
                    set DK_DX[pull] = Cos(angle)
                    set DK_DY[pull] = Sin(angle)
                    set DK_Left[pull] = DK_PullLimit(DK_Stacks[i])
                    set DK_Parent[pull] = i
                    set DK_X[pull] = DK_X[i]
                    set DK_Y[pull] = DK_Y[i]
                endif
            endif
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    set v = null
endfunction

function DK_Devour takes unit source, real x, real y, real scale returns nothing
    local integer i = DK_New(7, source)
    if i != 0 then
        set DK_FX[i] = AddSpecialEffect("Abilities\\Spells\\Undead\\DevourMagic\\DevourMagicBirthMissile.mdl", x, y)
        call BlzSetSpecialEffectScale(DK_FX[i], scale)
        call BlzSetSpecialEffectColor(DK_FX[i], 255, 150, 150)
        call BlzSetSpecialEffectHeight(DK_FX[i], 80.0)
        set DK_End[i] = DK_Now + 1.25
    endif
endfunction

function DK_Refund takes unit source, integer abilityId, integer level, string message returns nothing
    local integer i = DK_New(8, source)
    if i != 0 then
        set DK_Parent[i] = abilityId
        set DK_Damage[i] = I2R(BlzGetUnitAbilityManaCost(source, abilityId, level-1))
    endif
    call DisplayTimedTextToPlayer(GetOwningPlayer(source), 0.0, 0.0, 2.0, message)
endfunction

function DK_Text takes unit u, player viewer, string text, integer r, integer g, integer b returns nothing
    local texttag tag = CreateTextTag()
    call SetTextTagText(tag, text, 0.020)
    call SetTextTagPosUnit(tag, u, 110.0)
    call SetTextTagColor(tag, r, g, b, 255)
    call SetTextTagVelocity(tag, 0.0, 0.018)
    call SetTextTagPermanent(tag, false)
    call SetTextTagLifespan(tag, 0.9)
    call SetTextTagFadepoint(tag, 0.55)
    call SetTextTagVisibility(tag, IsPlayerAlly(viewer, GetLocalPlayer()) and IsUnitVisible(u, GetLocalPlayer()))
    set tag = null
endfunction

function DK_TitheEnemy takes unit u, player owner returns boolean
    return FS_Alive(u) and IsUnitEnemy(u, owner) and not IsUnitType(u, UNIT_TYPE_STRUCTURE) and not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) and GetUnitAbilityLevel(u, 'Aloc') == 0
endfunction

function DK_BloodTithe takes unit source, integer level returns nothing
    local integer i = 1
    local integer stacks = 0
    local integer count
    local unit v
    local group targets = CreateGroup()
    local integer key = GetHandleId(targets)
    local real damage = 15.0 + 10.0*level
    local real heal = 4.0 + 3.0*level
    local real life = GetWidgetLife(source)
    call SetUnitAnimation(source, "spell")
    call DK_Devour(source, GetUnitX(source), GetUnitY(source), 4.0)
    call DK_Blast(source, GetUnitX(source), GetUnitY(source), 450.0)
    // Consume all eligible stacks first: reflection cannot erase half of the payoff.
    loop
        exitwhen i > DK_High
        if DK_Kind[i] == 3 and DK_Source[i] == source then
            set v = DK_Target[i]
            set count = DK_Stacks[i]
            if DK_End[i] > DK_Now and DK_TitheEnemy(v, GetOwningPlayer(source)) then
                call SaveInteger(DK_Hash, key, GetHandleId(v), count)
                call GroupAddUnit(targets, v)
                set stacks = stacks + count
                call DK_Free(i)
            elseif DK_End[i] <= DK_Now or not FS_Alive(v) then
                call DK_Free(i)
            endif
        endif
        set i = i + 1
    endloop
    if stacks == 0 then
        call DK_Refund(source, 'ADk3', level, "|cffffcc00Blood Tithe: no marks to consume.|r")
    else
        loop
            set v = FirstOfGroup(targets)
            exitwhen v == null
            call GroupRemoveUnit(targets, v)
            set count = LoadInteger(DK_Hash, key, GetHandleId(v))
            call DK_Devour(source, GetUnitX(v), GetUnitY(v), 2.0+0.25*count)
            call DK_Beam(source, GetUnitX(v), GetUnitY(v), false)
            call DK_BloodHit(source, v)
            call FS_Hit(source, v, damage*count)
        endloop
        if FS_Alive(source) then
            set life = GetWidgetLife(source)
            call SetWidgetLife(source, RMinBJ(I2R(BlzGetUnitMaxHP(source)), life+heal*stacks))
            if GetWidgetLife(source) > life then
                call DK_Text(source, GetOwningPlayer(source), "+"+I2S(R2I(GetWidgetLife(source)-life)), 110, 255, 140)
            endif
            call DK_Devour(source, GetUnitX(source), GetUnitY(source), 3.0)
        endif
    endif
    call FlushChildHashtable(DK_Hash, key)
    call DestroyGroup(targets)
    set targets = null
    set v = null
endfunction

function DK_HookChain takes integer i returns nothing
    local unit source = DK_Source[i]
    local lightning chain = LoadLightningHandle(DK_Hash, i, -31)
    local real sx = GetUnitX(source)
    local real sy = GetUnitY(source)
    if chain == null then
        set chain = AddLightningEx("LEAS", true, sx, sy, DK_GroundZ(sx, sy)+110.0, DK_X[i], DK_Y[i], DK_GroundZ(DK_X[i], DK_Y[i])+90.0)
        call SaveLightningHandle(DK_Hash, i, -31, chain)
    else
        call MoveLightningEx(chain, true, sx, sy, DK_GroundZ(sx, sy)+110.0, DK_X[i], DK_Y[i], DK_GroundZ(DK_X[i], DK_Y[i])+90.0)
    endif
    call SetLightningColor(chain, 1.0, 0.18, 0.18, 1.0)
    set chain = null
    set source = null
endfunction

function DK_HookCast takes unit source, integer level returns nothing
    local integer i = DK_New(11, source)
    local real angle
    if i == 0 then
        return
    endif
    set angle = Atan2(GetSpellTargetY()-GetUnitY(source), GetSpellTargetX()-GetUnitX(source))
    if Pow(GetSpellTargetX()-GetUnitX(source), 2.0)+Pow(GetSpellTargetY()-GetUnitY(source), 2.0) < 64.0 then
        set angle = GetUnitFacing(source)*bj_DEGTORAD
    endif
    set DK_X[i] = GetUnitX(source)
    set DK_Y[i] = GetUnitY(source)
    set DK_DX[i] = Cos(angle)
    set DK_DY[i] = Sin(angle)
    set DK_Left[i] = 450.0
    set DK_Stacks[i] = level
    set DK_Damage[i] = 80.0+40.0*level
    set DK_End[i] = DK_Now+1.5
    set DK_Hit[i] = CreateGroup()
    set DK_FX[i] = AddSpecialEffect("Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilMissile.mdl", DK_X[i], DK_Y[i])
    call BlzSetSpecialEffectScale(DK_FX[i], 2.2)
    call BlzSetSpecialEffectColor(DK_FX[i], 255, 60, 60)
    call BlzSetSpecialEffectHeight(DK_FX[i], 90.0)
    call SetUnitAnimation(source, "spell")
    call DK_HookChain(i)
endfunction

function DK_OnCast takes nothing returns nothing
    local unit source = GetTriggerUnit()
    local integer abilityId = GetSpellAbilityId()
    local integer level = GetUnitAbilityLevel(source, abilityId)
    local integer i
    local integer n
    local integer count = 0
    local real angle
    local group g
    local unit v
    if GetUnitTypeId(source) != 'HDk1' or IsUnitIllusion(source) or not FS_Alive(source) then
        set source = null
        return
    endif
    if abilityId == 'ADk1' then
        set i = DK_New(1, source)
        if i != 0 then
            set angle = Atan2(GetSpellTargetY()-GetUnitY(source), GetSpellTargetX()-GetUnitX(source))
            if Pow(GetSpellTargetX()-GetUnitX(source), 2.0)+Pow(GetSpellTargetY()-GetUnitY(source), 2.0) < 64.0 then
                set angle = GetUnitFacing(source)*bj_DEGTORAD
            endif
            set DK_X[i] = GetUnitX(source)
            set DK_Y[i] = GetUnitY(source)
            set DK_DX[i] = Cos(angle)
            set DK_DY[i] = Sin(angle)
            set DK_Left[i] = 1200.0
            set DK_Stacks[i] = level
            set DK_Damage[i] = 70.0+40.0*level
            set DK_Hit[i] = CreateGroup()
            set DK_Pulled[i] = CreateGroup()
            set DK_FX[i] = AddSpecialEffect("Abilities\\Weapons\\RexxarMissile\\RexxarMissile.mdl", DK_X[i], DK_Y[i])
            call BlzSetSpecialEffectScale(DK_FX[i], 2.8)
            call BlzSetSpecialEffectColor(DK_FX[i], 255, 175, 150)
            call BlzSetSpecialEffectHeight(DK_FX[i], 100.0)
            call DK_AxeArea(i, DK_X[i], DK_Y[i])
        endif
    elseif abilityId == 'ADk5' then
        call DK_HookCast(source, level)
    elseif abilityId == 'ADk3' then
        call DK_BloodTithe(source, level)
    elseif abilityId == 'ADk4' then
        call DR_Start(source, level)
    endif
    set source = null
    set v = null
endfunction

function DK_OnDamage takes nothing returns nothing
    local unit source = GetEventDamageSource()
    local unit victim = GetTriggerUnit()
    local integer level = GetUnitAbilityLevel(source, 'ADk2')
    local integer i
    if level > 0 and GetUnitTypeId(source) == 'HDk1' and not IsUnitIllusion(source) and FS_Alive(source) and FS_CodeDepth == 0 and BlzGetEventIsAttack() and GetEventDamage() > 0.0 and GetUnitTypeId(victim) != 0 and IsUnitEnemy(victim, GetOwningPlayer(source)) and not IsUnitType(victim, UNIT_TYPE_STRUCTURE) and not IsUnitType(victim, UNIT_TYPE_FLYING) and not IsUnitType(victim, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(victim) and GetUnitAbilityLevel(victim, 'Aloc') == 0 and LoadReal(DK_Hash, GetHandleId(source), -1) <= DK_Now then
        if GetRandomInt(1, 100) <= 25 then
            set i = DK_New(6, source)
            if i != 0 then
                call SaveReal(DK_Hash, GetHandleId(source), -1, DK_Now+2.0)
                call BlzStartUnitAbilityCooldown(source, 'ADk2', 2.0)
                set DK_X[i] = GetUnitX(victim)
                set DK_Y[i] = GetUnitY(victim)
                set DK_Damage[i] = 30.0+25.0*level
            endif
        endif
    endif
    set source = null
    set victim = null
endfunction

function DK_OnDeath takes nothing returns nothing
    local unit dead = GetTriggerUnit()
    local integer i = 1
    local real cooldown = LoadReal(DK_Hash, GetHandleId(dead), -1)
    loop
        exitwhen i > DK_High
        if DK_Kind[i] != 0 and DK_Kind[i] != 7 and DK_Kind[i] != 8 and DK_Kind[i] != 9 then
            if DK_Source[i] == dead then
                if DK_Kind[i] == 4 then
                    call DK_EndRequiem(i, false)
                else
                    call DK_Free(i)
                endif
            elseif DK_Target[i] == dead then
                call DK_Free(i)
            endif
        endif
        set i = i + 1
    endloop
    call FlushChildHashtable(DK_Hash, GetHandleId(dead))
    if cooldown > DK_Now then
        call SaveReal(DK_Hash, GetHandleId(dead), -1, cooldown)
    endif
    set dead = null
endfunction

function DK_OnFinish takes nothing returns nothing
    local integer i = LoadInteger(DK_Hash, GetHandleId(GetTriggerUnit()), -2)
    // Native completion can reset the pose but cannot release the scripted channel.
    if i != 0 and DK_Kind[i] == 4 then
        call SetUnitAnimationByIndex(DK_Source[i], 7)
    endif
endfunction

function DK_OnEndCast takes nothing returns nothing
    call DK_OnFinish()
endfunction

function DK_Countdown takes integer i returns nothing
    local integer n = 1
    local string text = I2S(DK_Stacks[i])
    call SetUnitAnimationByIndex(DK_Source[i], 7)
    call DK_Text(DK_Source[i], DK_Owner[i], "Requiem: "+text, 255, 110, 85)
    loop
        exitwhen n > DK_High
        if DK_Kind[n] == 5 and DK_Parent[n] == i and FS_Alive(DK_Target[n]) then
            call DK_Text(DK_Target[n], GetOwningPlayer(DK_Target[n]), text, 255, 80, 60)
        endif
        set n = n + 1
    endloop
endfunction

function DK_HookStun takes unit source, unit target, integer level returns nothing
    local unit dummy = CreateUnit(GetOwningPlayer(source), FS_DUMMY, GetUnitX(target), GetUnitY(target), 0.0)
    call UnitAddAbility(dummy, 'ADk6')
    call SetUnitAbilityLevel(dummy, 'ADk6', level)
    call IssueTargetOrder(dummy, "thunderbolt", target)
    call UnitApplyTimedLife(dummy, 'BTLF', 1.5)
    set dummy = null
endfunction

function DK_HookCatch takes integer i, real ox, real oy returns nothing
    local group g = CreateGroup()
    local unit v
    local integer pull
    local real dx
    local real sx = DK_X[i]-ox
    local real sy = DK_Y[i]-oy
    local real length2 = sx*sx+sy*sy
    local real projection
    local real vx
    local real vy
    local real dy
    local real distance
    local real amount
    call GroupEnumUnitsInRange(g, (ox+DK_X[i])*0.5, (oy+DK_Y[i])*0.5, 150.0+SquareRoot(length2)*0.5, null)
    loop
        set v = FirstOfGroup(g)
        exitwhen v == null or DK_Kind[i] != 11 or not FS_Alive(DK_Source[i])
        call GroupRemoveUnit(g, v)
        set projection = 0.0
        if length2 > 0.01 then
            set projection = RMaxBJ(0.0, RMinBJ(1.0, ((GetUnitX(v)-ox)*sx+(GetUnitY(v)-oy)*sy)/length2))
        endif
        set vx = GetUnitX(v)-(ox+projection*sx)
        set vy = GetUnitY(v)-(oy+projection*sy)
        if vx*vx+vy*vy <= 22500.0 and FS_Enemy(v, DK_Owner[i]) and not IsUnitInGroup(v, DK_Hit[i]) then
            call GroupAddUnit(DK_Hit[i], v)
            set dx = GetUnitX(DK_Source[i])-GetUnitX(v)
            set dy = GetUnitY(DK_Source[i])-GetUnitY(v)
            set distance = SquareRoot(dx*dx+dy*dy)
            set amount = RMaxBJ(150.0, RMinBJ(400.0, distance*0.45))
            set amount = RMinBJ(amount, RMaxBJ(0.0, distance-100.0))
            if amount > 1.0 then
                // Most recent Demon Knight pull wins; each hook still deals its own hit.
                call DK_Free(LoadInteger(DK_Hash, GetHandleId(v), -3))
                call DK_Free(LoadInteger(DK_Hash, GetHandleId(v), -32))
                set pull = DK_New(12, DK_Source[i])
                if pull != 0 then
                    set DK_Target[pull] = v
                    set DK_Owner[pull] = DK_Owner[i]
                    set DK_Left[pull] = amount
                    set DK_Damage[pull] = DK_Damage[i]
                    set DK_Stacks[pull] = DK_Stacks[i]
                    set DK_Parent[pull] = i
                    call SaveInteger(DK_Hash, GetHandleId(v), -32, pull)
                endif
            endif
            call DK_Flash(DK_Source[i], "Abilities\\Spells\\Undead\\DeathCoil\\DeathCoilSpecialArt.mdl", GetUnitX(v), GetUnitY(v), 1.1)
            call DK_HookStun(DK_Source[i], v, DK_Stacks[i])
            call FS_Hit(DK_Source[i], v, DK_Damage[i])
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    set v = null
endfunction

function DK_PullStep takes unit u, real x, real y returns boolean
    local real ox = GetUnitX(u)
    local real oy = GetUnitY(u)
    if not FS_CanMove(u, x, y) then
        return false
    endif
    call SetUnitPosition(u, x, y)
    if (GetUnitX(u)-x)*(GetUnitX(u)-x)+(GetUnitY(u)-y)*(GetUnitY(u)-y) > 64.0 then
        call SetUnitX(u, ox)
        call SetUnitY(u, oy)
        return false
    endif
    return true
endfunction

function DK_Pulverize takes integer i returns nothing
    local unit source = DK_Source[i]
    local player owner = DK_Owner[i]
    local real damage = DK_Damage[i]
    local real x = DK_X[i]
    local real y = DK_Y[i]
    local group g = CreateGroup()
    local unit v
    // Once the shockwave is released, reflected damage cannot truncate its area.
    call DK_Free(i)
    call DK_Flash(source, "Abilities\\Spells\\Orc\\WarStomp\\WarStompCaster.mdl", x, y, 1.0)
    call GroupEnumUnitsInRange(g, x, y, 250.0, null)
    loop
        set v = FirstOfGroup(g)
        exitwhen v == null
        call GroupRemoveUnit(g, v)
        if FS_Enemy(v, owner) then
            call DK_Strike(source, v, damage)
        endif
    endloop
    call DestroyGroup(g)
    set g = null
    set v = null
    set source = null
    set owner = null
endfunction

function DK_Tick takes nothing returns nothing
    local integer i = 1
    local integer limit = DK_High
    local integer kind
    local real dx
    local real dy
    local real distance
    local real step
    local real ox
    local real oy
    local unit v
    set DK_Now = DK_Now + 0.03125
    loop
        exitwhen i > limit
        set kind = DK_Kind[i]
        if kind != 0 then
            if kind == 7 or kind == 9 then
                if DK_End[i] <= DK_Now then
                    call DK_Free(i)
                endif
            elseif kind == 5 then
                if DK_Kind[DK_Parent[i]] != 4 or not FS_Alive(DK_Target[i]) then
                    call DK_Free(i)
                else
                    call BlzSetSpecialEffectScale(DK_FX[i], 1.0+0.6*RMaxBJ(0.0, RMinBJ(1.0, (3.0-DK_End[DK_Parent[i]]+DK_Now)/3.0)))
                endif
            elseif kind == 8 then
                if GetUnitTypeId(DK_Source[i]) != 0 then
                    call SetUnitState(DK_Source[i], UNIT_STATE_MANA, RMinBJ(GetUnitState(DK_Source[i], UNIT_STATE_MAX_MANA), GetUnitState(DK_Source[i], UNIT_STATE_MANA)+DK_Damage[i]))
                    call BlzEndUnitAbilityCooldown(DK_Source[i], DK_Parent[i])
                    if DK_Parent[i] == 'ADk4' and GetUnitCurrentOrder(DK_Source[i]) == OrderId("channel") then
                        call IssueImmediateOrder(DK_Source[i], "stop")
                    endif
                endif
                call DK_Free(i)
            elseif not FS_Alive(DK_Source[i]) or GetOwningPlayer(DK_Source[i]) != DK_Owner[i] then
                if kind == 4 then
                    call DK_EndRequiem(i, false)
                else
                    call DK_Free(i)
                endif
            elseif kind == 10 then
                if DK_End[i] <= DK_Now then
                    set v = DK_Source[i]
                    set kind = DK_Stacks[i]
                    call DK_Free(i)
                    if kind == 1 then
                        call KillUnit(v)
                    endif
                else
                    call SetWidgetLife(DK_Source[i], RMinBJ(GetUnitState(DK_Source[i], UNIT_STATE_MAX_LIFE), GetWidgetLife(DK_Source[i])+GetUnitState(DK_Source[i], UNIT_STATE_MAX_LIFE)*DK_Damage[i]*0.03125))
                endif
            elseif kind == 1 then
                if DK_Now >= DK_End[i] then
                    call DK_Free(i)
                else
                    if DK_Return[i] then
                        set dx = GetUnitX(DK_Source[i])-DK_X[i]
                        set dy = GetUnitY(DK_Source[i])-DK_Y[i]
                        set distance = SquareRoot(dx*dx+dy*dy)
                        if distance > 0.01 then
                            set DK_DX[i] = dx/distance
                            set DK_DY[i] = dy/distance
                        endif
                        set step = RMinBJ(28.125, distance)
                    else
                        set step = RMinBJ(50.0, DK_Left[i])
                        set DK_Left[i] = DK_Left[i]-step
                    endif
                    set ox = DK_X[i]
                    set oy = DK_Y[i]
                    set DK_X[i] = RMaxBJ(GetRectMinX(bj_mapInitialPlayableArea)+16.0, RMinBJ(GetRectMaxX(bj_mapInitialPlayableArea)-16.0, ox+DK_DX[i]*step))
                    set DK_Y[i] = RMaxBJ(GetRectMinY(bj_mapInitialPlayableArea)+16.0, RMinBJ(GetRectMaxY(bj_mapInitialPlayableArea)-16.0, oy+DK_DY[i]*step))
                    if not DK_Return[i] and (RAbsBJ(DK_X[i]-(ox+DK_DX[i]*step)) > 0.01 or RAbsBJ(DK_Y[i]-(oy+DK_DY[i]*step)) > 0.01) then
                        set DK_Left[i] = 0.0
                    endif
                    call BlzSetSpecialEffectX(DK_FX[i], DK_X[i])
                    call BlzSetSpecialEffectY(DK_FX[i], DK_Y[i])
                    call BlzSetSpecialEffectHeight(DK_FX[i], 100.0)
                    call BlzSetSpecialEffectYaw(DK_FX[i], DK_Now*20.0)
                    call DK_AxeArea(i, ox, oy)
                    if DK_Kind[i] != 1 then
                        // Source may have died to reflected damage inside the area hit.
                    elseif DK_Return[i] and distance <= 28.125 then
                        call DK_Free(i)
                    elseif not DK_Return[i] and DK_Left[i] <= 0.0 then
                        set DK_Return[i] = true
                        call GroupClear(DK_Hit[i])
                        call BlzSetSpecialEffectColor(DK_FX[i], 255, 75, 45)
                        call BlzSetSpecialEffectScale(DK_FX[i], 3.1)
                    endif
                endif
            elseif kind == 2 then
                set v = DK_Target[i]
                // Share the returning axe's displacement, preserving the contact offset.
                if DK_Kind[DK_Parent[i]] != 1 or not DK_Return[DK_Parent[i]] or DK_Source[DK_Parent[i]] != DK_Source[i] or not FS_Enemy(v, DK_Owner[i]) or DK_Left[i] <= 0.0 then
                    call DK_Free(i)
                else
                    set dx = GetUnitX(DK_Source[i])-GetUnitX(v)
                    set dy = GetUnitY(DK_Source[i])-GetUnitY(v)
                    set DK_X[i] = DK_X[DK_Parent[i]]
                    set DK_Y[i] = DK_Y[DK_Parent[i]]
                    set distance = SquareRoot(dx*dx+dy*dy)
                    set step = RMinBJ(28.125, RMinBJ(distance, DK_Left[i]))
                    set step = RMinBJ(step, RMaxBJ(0.0, SquareRoot(Pow(GetUnitX(DK_Source[i])-GetUnitX(v), 2.0)+Pow(GetUnitY(DK_Source[i])-GetUnitY(v), 2.0))-100.0))
                    if distance > 0.01 and step > 0.0 then
                        if DK_PullStep(v, GetUnitX(v)+dx/distance*step, GetUnitY(v)+dy/distance*step) then
                            set DK_Left[i] = DK_Left[i]-step
                        else
                            call DK_Free(i)
                        endif
                    elseif distance > 0.01 then
                        call DK_Free(i)
                    endif
                endif
            elseif kind == 11 then
                if DK_End[i] <= DK_Now then
                    call DK_Free(i)
                else
                    if DK_Return[i] then
                        set dx = GetUnitX(DK_Source[i])-DK_X[i]
                        set dy = GetUnitY(DK_Source[i])-DK_Y[i]
                        set distance = SquareRoot(dx*dx+dy*dy)
                        if distance > 0.01 then
                            set DK_DX[i] = dx/distance
                            set DK_DY[i] = dy/distance
                        endif
                        set step = RMinBJ(84.375, distance)
                    else
                        set step = RMinBJ(56.25, DK_Left[i])
                        set DK_Left[i] = DK_Left[i]-step
                    endif
                    set ox = DK_X[i]
                    set oy = DK_Y[i]
                    set DK_X[i] = DK_X[i]+DK_DX[i]*step
                    set DK_Y[i] = DK_Y[i]+DK_DY[i]*step
                    call BlzSetSpecialEffectX(DK_FX[i], DK_X[i])
                    call BlzSetSpecialEffectY(DK_FX[i], DK_Y[i])
                    call DK_HookChain(i)
                    if not DK_Return[i] then
                        call DK_HookCatch(i, ox, oy)
                    endif
                    if DK_Kind[i] != 11 then
                        // Reflected damage may have freed the head inside the catch.
                    elseif DK_Return[i] then
                        if distance <= 84.375 then
                            call DK_Free(i)
                        endif
                    elseif DK_Left[i] <= 0.0 then
                        set DK_Return[i] = true
                    endif
                endif
            elseif kind == 12 then
                set v = DK_Target[i]
                if not FS_Alive(v) or not FS_Enemy(v, DK_Owner[i]) or DK_Left[i] <= 0.0 then
                    call DK_Free(i)
                else
                    set dx = GetUnitX(DK_Source[i])-GetUnitX(v)
                    set dy = GetUnitY(DK_Source[i])-GetUnitY(v)
                    set distance = SquareRoot(dx*dx+dy*dy)
                    set step = RMinBJ(40.0, RMinBJ(distance-100.0, DK_Left[i]))
                    if distance > 100.0 and step > 0.0 then
                        if DK_PullStep(v, GetUnitX(v)+dx/distance*step, GetUnitY(v)+dy/distance*step) then
                            set DK_Left[i] = DK_Left[i]-step
                        else
                            call DK_Free(i)
                        endif
                    else
                        call DK_Free(i)
                    endif
                endif
            elseif kind == 3 then
                if DK_End[i] <= DK_Now or not FS_Alive(DK_Target[i]) or not IsUnitEnemy(DK_Target[i], DK_Owner[i]) then
                    call DK_Free(i)
                else
                    call DK_MarkLabel(i)
                endif
            elseif kind == 4 then
                if DK_End[i] <= DK_Now then
                    call DK_EndRequiem(i, true)
                elseif DK_Stacks[i] > 1 and DK_End[i]-DK_Now <= I2R(DK_Stacks[i]-1) then
                    set DK_Stacks[i] = DK_Stacks[i]-1
                    call DK_Countdown(i)
                endif
            elseif kind == 6 then
                call DK_Pulverize(i)
            endif
        endif
        set i = i + 1
    endloop
    set v = null
endfunction

function DK_Init takes nothing returns nothing
    local trigger cast = CreateTrigger()
    local trigger damage = CreateTrigger()
    local trigger stop = CreateTrigger()
    local trigger finish = CreateTrigger()
    local trigger orders = CreateTrigger()
    local trigger death = CreateTrigger()
    call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 1", 0)
    call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 110 damage each way and pulls enemies toward you on its return.", 0)
    call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 2", 1)
    call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 150 damage each way and pulls enemies toward you on its return.", 1)
    call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 3", 2)
    call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 190 damage each way and pulls enemies toward you on its return.", 2)
    call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 4", 3)
    call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 230 damage each way and pulls enemies toward you on its return.", 3)
    call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 5", 4)
    call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 270 damage each way and pulls enemies toward you on its return.", 4)
    call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 6", 5)
    call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 310 damage each way and pulls enemies toward you on its return.", 5)
    call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 1", 0)
    call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 1|nAttacks have a 25% chance to deal 55 magic damage to ground enemies around the target.", 0)
    call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 2", 1)
    call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 4|nAttacks have a 25% chance to deal 80 magic damage to ground enemies around the target.", 1)
    call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 3", 2)
    call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 7|nAttacks have a 25% chance to deal 105 magic damage to ground enemies around the target.", 2)
    call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 4", 3)
    call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 10|nAttacks have a 25% chance to deal 130 magic damage to ground enemies around the target.", 3)
    call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 5", 4)
    call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 13|nAttacks have a 25% chance to deal 155 magic damage to ground enemies around the target.", 4)
    call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 6", 5)
    call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 16|nAttacks have a 25% chance to deal 180 magic damage to ground enemies around the target.", 5)
    call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 1", 0)
    call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 1|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 25 damage and healing you for 7 per mark.", 0)
    call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 2", 1)
    call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 4|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 35 damage and healing you for 10 per mark.", 1)
    call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 3", 2)
    call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 7|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 45 damage and healing you for 13 per mark.", 2)
    call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 4", 3)
    call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 10|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 55 damage and healing you for 16 per mark.", 3)
    call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 5", 4)
    call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 13|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 65 damage and healing you for 19 per mark.", 4)
    call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 6", 5)
    call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 16|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 75 damage and healing you for 22 per mark.", 5)
    call BlzSetAbilityResearchTooltip('ADk4', "Learn Demon Ascension [|cffffcc00R|r] - Level 1", 0)
    call BlzSetAbilityResearchExtendedTooltip('ADk4', "Transform for 15s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 0)
    call BlzSetAbilityResearchTooltip('ADk4', "Learn Demon Ascension [|cffffcc00R|r] - Level 2", 1)
    call BlzSetAbilityResearchExtendedTooltip('ADk4', "Transform for 18s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 1)
    call BlzSetAbilityResearchTooltip('ADk4', "Learn Demon Ascension [|cffffcc00R|r] - Level 3", 2)
    call BlzSetAbilityResearchExtendedTooltip('ADk4', "Transform for 21s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 2)
    call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 1", 0)
    call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 1|nHook enemies in a line for 120 damage, briefly stunning and dragging them toward you.", 0)
    call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 2", 1)
    call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 4|nHook enemies in a line for 160 damage, briefly stunning and dragging them toward you.", 1)
    call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 3", 2)
    call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 7|nHook enemies in a line for 200 damage, briefly stunning and dragging them toward you.", 2)
    call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 4", 3)
    call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 10|nHook enemies in a line for 240 damage, briefly stunning and dragging them toward you.", 3)
    call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 5", 4)
    call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 13|nHook enemies in a line for 280 damage, briefly stunning and dragging them toward you.", 4)
    call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 6", 5)
    call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 16|nHook enemies in a line for 320 damage, briefly stunning and dragging them toward you.", 5)
    set DK_Hash = InitHashtable()
    set DK_Timer = CreateTimer()
    call TriggerRegisterAnyUnitEventBJ(cast, EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddAction(cast, function DK_OnCast)
    call TriggerRegisterAnyUnitEventBJ(damage, EVENT_PLAYER_UNIT_DAMAGED)
    call TriggerAddAction(damage, function DK_OnDamage)
    call TriggerRegisterAnyUnitEventBJ(stop, EVENT_PLAYER_UNIT_SPELL_ENDCAST)
    call TriggerAddAction(stop, function DK_OnEndCast)
    call TriggerRegisterAnyUnitEventBJ(finish, EVENT_PLAYER_UNIT_SPELL_FINISH)
    call TriggerAddAction(finish, function DK_OnFinish)
    call TriggerRegisterAnyUnitEventBJ(death, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddAction(death, function DK_OnDeath)
    call TimerStart(DK_Timer, 0.03125, true, function DK_Tick)
    set cast = null
    set damage = null
    set stop = null
    call TriggerRegisterAnyUnitEventBJ(orders, EVENT_PLAYER_UNIT_ISSUED_ORDER)
    call TriggerRegisterAnyUnitEventBJ(orders, EVENT_PLAYER_UNIT_ISSUED_POINT_ORDER)
    call TriggerRegisterAnyUnitEventBJ(orders, EVENT_PLAYER_UNIT_ISSUED_TARGET_ORDER)
    call TriggerAddAction(orders, function DK_ChannelOrders)
    set orders = null
    set finish = null
    set death = null
endfunction

function FF_LearnTip_ADk1 takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'ADk1')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 110 damage each way and pulls enemies toward you on its return.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 150 damage each way and pulls enemies toward you on its return.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 190 damage each way and pulls enemies toward you on its return.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 230 damage each way and pulls enemies toward you on its return.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 270 damage each way and pulls enemies toward you on its return.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('ADk1', "Learn Reaping Axe [|cffffcc00Q|r] - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk1', "Throw a returning axe that deals 310 damage each way and pulls enemies toward you on its return.", 0)
    endif
endfunction

function FF_LearnTip_ADk2 takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'ADk2')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 1|nAttacks have a 25% chance to deal 55 magic damage to ground enemies around the target.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 4|nAttacks have a 25% chance to deal 80 magic damage to ground enemies around the target.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 7|nAttacks have a 25% chance to deal 105 magic damage to ground enemies around the target.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 10|nAttacks have a 25% chance to deal 130 magic damage to ground enemies around the target.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 13|nAttacks have a 25% chance to deal 155 magic damage to ground enemies around the target.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('ADk2', "Learn Pulverize [|cffffcc00W|r] - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk2', "Requires hero level 16|nAttacks have a 25% chance to deal 180 magic damage to ground enemies around the target.", 0)
    endif
endfunction

function FF_LearnTip_ADk3 takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'ADk3')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 1|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 25 damage and healing you for 7 per mark.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 4|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 35 damage and healing you for 10 per mark.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 7|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 45 damage and healing you for 13 per mark.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 10|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 55 damage and healing you for 16 per mark.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 13|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 65 damage and healing you for 19 per mark.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('ADk3', "Learn Blood Tithe [|cffffcc00E|r] - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk3', "Requires hero level 16|nReaping Axe and Pulverize mark enemies. Consume up to 6 marks per enemy, dealing 75 damage and healing you for 22 per mark.", 0)
    endif
endfunction

function FF_LearnTip_ADk4 takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'ADk4')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('ADk4', "Learn Demon Ascension [|cffffcc00R|r] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk4', "Transform for 15s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('ADk4', "Learn Demon Ascension [|cffffcc00R|r] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk4', "Transform for 18s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 0)
    elseif rank >= 2 then
        call BlzSetAbilityResearchTooltip('ADk4', "Learn Demon Ascension [|cffffcc00R|r] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk4', "Transform for 21s, gaining spell immunity, regeneration, cleave, and faster attacks and movement. Lethal damage grants 10 final seconds of life.", 0)
    endif
endfunction

function FF_LearnTip_ADk5 takes unit hero returns nothing
    local integer rank = GetUnitAbilityLevel(hero, 'ADk5')
    if rank == 0 then
        call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 1", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 1|nHook enemies in a line for 120 damage, briefly stunning and dragging them toward you.", 0)
    elseif rank == 1 then
        call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 2", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 4|nHook enemies in a line for 160 damage, briefly stunning and dragging them toward you.", 0)
    elseif rank == 2 then
        call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 3", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 7|nHook enemies in a line for 200 damage, briefly stunning and dragging them toward you.", 0)
    elseif rank == 3 then
        call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 4", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 10|nHook enemies in a line for 240 damage, briefly stunning and dragging them toward you.", 0)
    elseif rank == 4 then
        call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 5", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 13|nHook enemies in a line for 280 damage, briefly stunning and dragging them toward you.", 0)
    elseif rank >= 5 then
        call BlzSetAbilityResearchTooltip('ADk5', "Learn Soul Hook [|cffffcc00E|r] - Level 6", 0)
        call BlzSetAbilityResearchExtendedTooltip('ADk5', "Requires hero level 16|nHook enemies in a line for 320 damage, briefly stunning and dragging them toward you.", 0)
    endif
endfunction
