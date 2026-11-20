function FF_DebugTwistedFate takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer slot = GetPlayerId(p)
    local integer start = GetPlayerStartLocation(p)
    local unit hero
    if udg_mode_debugmode then
        set hero = FF_DebugFate[slot]
        if GetUnitTypeId(hero) == 0 then
            set hero = CreateUnit(p, 'HTf1', GetStartLocationX(start), GetStartLocationY(start), 270.0)
            set FF_DebugFate[slot] = hero
            call FF_TestExtraHero(hero)
        else
            if IsUnitType(hero, UNIT_TYPE_DEAD) then
                call ReviveHero(hero, GetStartLocationX(start), GetStartLocationY(start), true)
            endif
            call SelectUnitForPlayerSingle(hero, p)
        endif
    endif
    set hero = null
    set p = null
endfunction

function FF_InitDebugTwistedFate takes nothing returns nothing
    local trigger chat = CreateTrigger()
    local integer slot = 0
    loop
        exitwhen slot >= 12
        call TriggerRegisterPlayerChatEvent(chat, Player(slot), "-tf", true)
        set slot = slot + 1
    endloop
    call TriggerAddAction(chat, function FF_DebugTwistedFate)
    set chat = null
endfunction
