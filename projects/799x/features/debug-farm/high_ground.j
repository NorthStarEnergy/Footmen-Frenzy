function FFDebugTaverns takes nothing returns nothing
    local integer i = 0
    local integer pn = 1
    local integer page
    local integer id
    local integer slot
    local real cx = GetRectCenterX(gg_rct_TAVERN_AREA)
    local real cy = GetRectCenterY(gg_rct_TAVERN_AREA)
    local unit shop = null
    local player p
    if FFDebugShopsReady then
        return
    endif
    set FFDebugShopsReady = true
    loop
        exitwhen i >= FFDebugHeroCount
        set page = i/10
        if ModuloInteger(i,10) == 0 then
            set shop = CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE),'nDbT',cx+(I2R(ModuloInteger(page,4))-1.5)*176.,cy+(1.5-I2R(page/4))*160.,270.)
            set FFDebugShops[page] = shop
            call BlzSetUnitName(shop,"Hero Tavern "+I2S(page+1))
            call SetUnitScale(shop,0.70,0.70,0.70)
            call BlzSetUnitRealField(shop,UNIT_RF_SELECTION_SCALE,0.90*BlzGetUnitRealField(shop,UNIT_RF_SELECTION_SCALE))
            call SetUnitTypeSlots(shop,12)
        endif
        call SaveInteger(DraftStock,GetHandleId(shop),FFDebugHireButton[i],FFDebugHero[i])
        call AddUnitToStock(shop,FFDebugHireButton[i],2,2)
        set i = i+1
    endloop
    set i = 13
    loop
        exitwhen i > 21
        if udg_real_shop[i] != null then
            call ShowUnit(udg_real_shop[i],false)
        endif
        set i = i+1
    endloop
    loop
        exitwhen pn > 12
        if udg_player_active[pn] then
            set p = ConvertedPlayer(pn)
            call FF_DebugOpenHiring(p)
            set slot = 0
            loop
                exitwhen slot >= FFDebugHeroCount
                set id = FFDebugHero[slot]
                call SetPlayerTechMaxAllowed(p,id,-1)
                set slot = slot+1
            endloop
            call FFHire_CreateBuyer(p,cx,cy)
            call FogModifierStart(CreateFogModifierRect(p,FOG_OF_WAR_VISIBLE,gg_rct_TAVERN_AREA,true,false))
            call SelectUnitForPlayerSingle(FFDebugShops[0],p)
            call PanCameraToTimedForPlayer(p,cx,cy,0.25)
        endif
        set pn = pn+1
    endloop
    set p = null
    set shop = null
endfunction
