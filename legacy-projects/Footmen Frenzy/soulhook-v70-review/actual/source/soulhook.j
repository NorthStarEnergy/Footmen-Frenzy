// Soul Hook: short-range, fast hook that damages, stuns and drags every caught
// ground enemy partway back toward the caster instead of all the way.
// Reuses the Demon Knight state machine. Kind 11 = hook head, kind 12 = dragged victim.
// No new globals are declared; all scratch data lives in the existing DK_ arrays.
function DK_HookStun takes unit source, unit target, integer level returns nothing
    local unit dummy = CreateUnit(GetOwningPlayer(source), FS_DUMMY, GetUnitX(target), GetUnitY(target), 0.0)
    call UnitAddAbility(dummy, 'ADk6')
    call SetUnitAbilityLevel(dummy, 'ADk6', level)
    call IssueTargetOrder(dummy, "thunderbolt", target)
    call UnitApplyTimedLife(dummy, 'BTLF', 1.5)
    set dummy = null
endfunction

// Visual tether between the caster and the flying head. One handle per head.
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

// Each victim is caught once per head, damaged once, stunned briefly and then
// dragged by a fixed amount that is only a fraction of its distance to the caster.
function DK_HookCatch takes integer i returns nothing
    local group g = CreateGroup()
    local unit v
    local integer pull
    local real dx
    local real dy
    local real distance
    local real amount
    call GroupEnumUnitsInRange(g, DK_X[i], DK_Y[i], 150.0, null)
    loop
        set v = FirstOfGroup(g)
        exitwhen v == null or DK_Kind[i] != 11 or not FS_Alive(DK_Source[i])
        call GroupRemoveUnit(g, v)
        if FS_Enemy(v, DK_Owner[i]) and not IsUnitInGroup(v, DK_Hit[i]) and LoadInteger(DK_Hash, GetHandleId(v), -32) == 0 then
            call GroupAddUnit(DK_Hit[i], v)
            set dx = GetUnitX(DK_Source[i])-GetUnitX(v)
            set dy = GetUnitY(DK_Source[i])-GetUnitY(v)
            set distance = SquareRoot(dx*dx+dy*dy)
            set amount = RMaxBJ(150.0, RMinBJ(400.0, distance*0.45))
            set amount = RMinBJ(amount, RMaxBJ(0.0, distance-100.0))
            if amount > 1.0 then
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
