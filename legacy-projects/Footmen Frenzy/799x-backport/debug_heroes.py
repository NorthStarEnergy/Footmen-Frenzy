"""Unlimited debug recruitment with level 18 assigned after hero initialization."""
import re


def patch(script):
    changed = []

    def edit(name, old, new):
        nonlocal script
        before = re.search(r'^function ' + name + r' takes .*?^endfunction', script, re.M | re.S)[0]
        assert old in before, (name, old)
        script = script.replace(before, before.replace(old, new), 1)
        if name not in changed: changed.append(name)

    script = script.replace('boolean udg_mode_debugmode= false',
                            'hashtable FF_DebugHireHash = InitHashtable()\nboolean udg_mode_debugmode= false', 1)
    helpers = '''function FF_DebugOpenHiring takes player p returns nothing
    local integer i = 1
    if not udg_mode_debugmode then
        return
    endif
    call SetPlayerMaxHeroesAllowed(-1, p)
    call SetPlayerState(p, PLAYER_STATE_FOOD_CAP_CEILING, 300)
    call SetPlayerState(p, PLAYER_STATE_RESOURCE_FOOD_CAP, 300)
    loop
        exitwhen i > udg_total_hero_count
        call SetPlayerTechMaxAllowed(p, udg_hero_type[i], -1)
        set i = i + 1
    endloop
endfunction

function FF_DebugHeroReady takes unit u returns nothing
    if not udg_mode_debugmode or u == null or GetUnitTypeId(u) == 0 or not IsUnitType(u, UNIT_TYPE_HERO) or GetPlayerId(GetOwningPlayer(u)) >= 12 then
        return
    endif
    // Extra heroes must not gradually consume the finite engine food ceiling.
    call SetUnitUseFood(u, false)
    if GetHeroLevel(u) < 18 then
        call SetHeroLevel(u, 18, false)
    endif
endfunction

function FF_DebugHireComplete takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer key = GetHandleId(t)
    local unit u = LoadUnitHandle(FF_DebugHireHash, key, 0)
    local unit shop = LoadUnitHandle(FF_DebugHireHash, key, 1)
    local integer kind = LoadInteger(FF_DebugHireHash, key, 2)
    if udg_mode_debugmode then
        // Run after sale/enter-region handlers and the engine's stock decrement.
        call FF_DebugHeroReady(u)
        if GetUnitTypeId(shop) != 0 then
            call RemoveUnitFromStock(shop, kind)
            call AddUnitToStock(shop, kind, 2, 2)
        endif
    endif
    call FlushChildHashtable(FF_DebugHireHash, key)
    call DestroyTimer(t)
    set u = null
    set shop = null
    set t = null
endfunction

function FF_DebugHeroSold takes nothing returns nothing
    local unit u = GetSoldUnit()
    local timer t
    local integer key
    if udg_mode_debugmode and IsUnitType(u, UNIT_TYPE_HERO) and GetPlayerId(GetOwningPlayer(u)) < 12 then
        set t = CreateTimer()
        set key = GetHandleId(t)
        call SaveUnitHandle(FF_DebugHireHash, key, 0, u)
        call SaveUnitHandle(FF_DebugHireHash, key, 1, GetSellingUnit())
        call SaveInteger(FF_DebugHireHash, key, 2, GetUnitTypeId(u))
        call TimerStart(t, 0.0, false, function FF_DebugHireComplete)
    endif
    set t = null
    set u = null
endfunction

'''
    script = script.replace('function FF_TestExtraHero takes', helpers + 'function FF_TestExtraHero takes', 1)
    edit('FF_TestExtraHero', '    call SelectUnitForPlayerSingle(u, p)',
         '    call SelectUnitForPlayerSingle(u, p)\n    call FF_DebugHeroReady(u)')
    edit('Trig_TP_hero_Actions', '    call RemoveLocation(udg_temp_point)\nendfunction',
         '    call RemoveLocation(udg_temp_point)\n    call FF_DebugHeroReady(udg_temp_unit)\nendfunction')
    edit('InitTrig_TP_hero', '    set gg_trg_TP_hero=CreateTrigger()', '''    local trigger debugSales = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(debugSales, EVENT_PLAYER_UNIT_SELL)
    call TriggerAddAction(debugSales, function FF_DebugHeroSold)
    set debugSales = null
    set gg_trg_TP_hero=CreateTrigger()''')
    edit('Trig_debugmode_Actions', '''        call SetPlayerMaxHeroesAllowed(-1, ConvertedPlayer(udg_X))
        // Each hero uses food; the normal 5-food cap otherwise blocks hero two.
        call SetPlayerState(ConvertedPlayer(udg_X), PLAYER_STATE_FOOD_CAP_CEILING, 300)
        call SetPlayerState(ConvertedPlayer(udg_X), PLAYER_STATE_RESOURCE_FOOD_CAP, 300)''',
         '        call FF_DebugOpenHiring(ConvertedPlayer(udg_X))')
    edit('FFRandom_Sold', 'and udg_herO[pn] == null then',
         'and (udg_herO[pn] == null or udg_mode_debugmode) then')
    return script, changed
