// The dialog startup removes h01G/h03Y selectors. Neutral taverns still need
// a nearby owned unit, so supply inert buyers without restoring the old menu.
function FFHire_CreateBuyer takes player p, real x, real y returns nothing
    local unit buyer = CreateUnit(p, 'h01G', x, y, 0.0)
    call UnitRemoveAbility(buyer, 'A01R')
    call UnitRemoveAbility(buyer, 'A01F')
    call UnitRemoveAbility(buyer, 'A01T')
    call SetUnitUseFood(buyer, false)
    call SetUnitPathing(buyer, false)
    call SetUnitX(buyer, x)
    call SetUnitY(buyer, y)
    call SetUnitInvulnerable(buyer, true)
    call SetUnitScale(buyer, 0.01, 0.01, 0.01)
    call SetUnitVertexColor(buyer, 255, 255, 255, 0)
    call BlzSetUnitName(buyer, "Hero hiring access")
    // Keep it present: ShowUnit(false) or Locust can exclude a shop patron.
    set buyer = null
endfunction

function FFHire_Prepare takes nothing returns nothing
    local integer pn = 1
    local integer team
    local player p
    local unit shop
    if FFHire_Ready then
        return
    endif
    set FFHire_Ready = true
    loop
        exitwhen pn > 12
        set p = ConvertedPlayer(pn)
        if GetPlayerSlotState(p) == PLAYER_SLOT_STATE_PLAYING then
            if udg_selected_mode == 2 then
                // All nine AP taverns are within 240 units of this point.
                // Their native Select Hero ability has an 800-unit radius.
                call FFHire_CreateBuyer(p, -2688.0, -256.0)
            elseif udg_selected_mode == 3 then
                set team = udg_teamnumber[pn]
                if team >= 1 and team <= 4 then
                    set shop = udg_real_shop[team]
                    if shop != null then
                        call FFHire_CreateBuyer(p, GetUnitX(shop), GetUnitY(shop))
                    endif
                    set shop = CarryTav_shop[team]
                    if shop != null then
                        call FFHire_CreateBuyer(p, GetUnitX(shop), GetUnitY(shop))
                    endif
                    set shop = OD_CarryTav_shop2[team]
                    if shop != null then
                        call FFHire_CreateBuyer(p, GetUnitX(shop), GetUnitY(shop))
                    endif
                endif
            endif
            // AR (mode 1) assigns heroes directly, without a tavern purchase.
        endif
        set pn = pn + 1
    endloop
    set shop = null
    set p = null
endfunction
