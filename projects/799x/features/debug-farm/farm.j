function FFBaseAngle takes integer pn returns real
    local integer start = GetPlayerStartLocation(ConvertedPlayer(pn))
    return Atan2(-256.0-GetStartLocationY(start), -GetStartLocationX(start))
endfunction

function FFBaseFrontX takes integer pn, real forward, real side returns real
    local real angle = FFBaseAngle(pn)
    return GetStartLocationX(GetPlayerStartLocation(ConvertedPlayer(pn)))+forward*Cos(angle)-side*Sin(angle)
endfunction

function FFBaseFrontY takes integer pn, real forward, real side returns real
    local real angle = FFBaseAngle(pn)
    return GetStartLocationY(GetPlayerStartLocation(ConvertedPlayer(pn)))+forward*Sin(angle)+side*Cos(angle)
endfunction

function FFFarmSetPage takes unit farm, integer pn, integer page returns nothing
    local integer i = 0
    local integer index
    loop
        exitwhen i >= 9
        set index = FFFarmPage[pn]*9+i
        if index < 26 then
            call UnitRemoveAbility(farm,FFFarmButton[index])
        endif
        set i = i+1
    endloop
    set FFFarmPage[pn] = page
    set i = page*9
    loop
        exitwhen i >= 26 or i >= (page+1)*9
        call UnitAddAbility(farm,FFFarmButton[i])
        set i = i+1
    endloop
    call BlzSetUnitName(farm,"Debug Farm  ("+I2S(page+1)+"/3)")
endfunction

function FFFarmCreate takes integer pn returns nothing
    local unit farm = CreateUnit(ConvertedPlayer(pn),'n034',FFBaseFrontX(pn,320.0,0.0),FFBaseFrontY(pn,320.0,0.0),270.0)
    call FFFarmSetPage(farm,pn,0)
    set farm = null
endfunction

function FFFarmSpawn takes integer pn, integer idx returns nothing
    local real angle = FFBaseAngle(pn)
    local real x = -680.0*Cos(angle)
    local real y = -256.0-680.0*Sin(angle)
    local integer variant = 26
    local unit u
    // Some bases produce a variant of the same rawcode with its own upgrade table.
    loop
        exitwhen variant > 50
        if udg_spawn_unit[variant] == udg_spawn_unit[idx] and udg_base_type[variant] == GetUnitTypeId(udg_base[pn]) then
            set idx = variant
            exitwhen true
        endif
        set variant = variant+1
    endloop
    set u = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE),udg_spawn_unit[idx],x,y,bj_RADTODEG*angle)
    if u != null then
        call FFGS_ComputeStats(idx,pn)
        call FFGS_ApplyUnit(u,idx,pn)
        if ffgs_footmen_rules[idx] and udg_spawnprotection then
            call UnitRemoveAbility(u,'Avul')
        endif
        call IssueImmediateOrder(u,"stop")
    endif
    set u = null
endfunction

function FFFarmCast takes nothing returns nothing
    local unit farm = GetTriggerUnit()
    local unit target = GetSpellTargetUnit()
    local integer pn = GetConvertedPlayerId(GetOwningPlayer(farm))
    local integer spellId = GetSpellAbilityId()
    local integer i
    if udg_mode_debugmode and pn >= 1 and pn <= 12 and GetUnitTypeId(farm) == 'n034' then
        if spellId == 'aFPg' then
            call FFFarmSetPage(farm,pn,ModuloInteger(FFFarmPage[pn]+1,3))
        elseif spellId == 'aFLu' or spellId == 'aFLd' then
            if target != null and IsUnitType(target,UNIT_TYPE_HERO) and GetWidgetLife(target) > 0.405 then
                if spellId == 'aFLu' then
                    call SetHeroLevel(target,GetHeroLevel(target)+1,false)
                elseif GetHeroLevel(target) > 1 then
                    call UnitStripHeroLevel(target,1)
                endif
            endif
        else
            set i = FFFarmPage[pn]*9
            loop
                exitwhen i >= 26 or i >= (FFFarmPage[pn]+1)*9
                if FFFarmButton[i] == spellId then
                    call FFFarmSpawn(pn,i)
                    exitwhen true
                endif
                set i = i+1
            endloop
        endif
    endif
    set farm = null
    set target = null
endfunction
