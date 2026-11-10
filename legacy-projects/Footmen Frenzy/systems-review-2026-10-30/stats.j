// Detailed player stats; frame creation is synchronized, visibility is local only.
function DPS_OnDamage takes nothing returns nothing
    local unit src = GetEventDamageSource()
    local unit dst = GetTriggerUnit()
    local integer s
    if src != null and GetEventDamage() > 0.0 and IsUnitType(dst, UNIT_TYPE_HERO) and not IsUnitIllusion(dst) and IsUnitEnemy(dst, GetOwningPlayer(src)) then
        set s = FF_st_Slot(GetOwningPlayer(src))
        if s >= 1 and s <= 12 then
            call SaveReal(DPS_Damage, GetHandleId(dst), s, TimerGetElapsed(FF_gameTimer))
        endif
    endif
    set src = null
    set dst = null
endfunction

function DPS_OnDeath takes nothing returns nothing
    local unit dst = GetTriggerUnit()
    local unit src = GetKillingUnit()
    local integer key = GetHandleId(dst)
    local integer ks = 0
    local integer s = 1
    local real now = TimerGetElapsed(FF_gameTimer)
    if src != null and not IsUnitIllusion(dst) and IsUnitEnemy(dst, GetOwningPlayer(src)) then
        set ks = FF_st_Slot(GetOwningPlayer(src))
        if ks >= 1 and ks <= 12 then
            if IsUnitType(dst, UNIT_TYPE_STRUCTURE) then
                set DPS_Buildings[ks] = DPS_Buildings[ks] + 1
            elseif IsUnitType(dst, UNIT_TYPE_HERO) then
                loop
                    exitwhen s > 12
                    if s != ks and IsPlayerAlly(Player(s - 1), GetOwningPlayer(src)) and IsUnitEnemy(dst, Player(s - 1)) and HaveSavedReal(DPS_Damage, key, s) then
                        if now - LoadReal(DPS_Damage, key, s) <= 10.0 then
                            set DPS_Assists[s] = DPS_Assists[s] + 1
                        endif
                    endif
                    set s = s + 1
                endloop
            endif
        endif
    endif
    call FlushChildHashtable(DPS_Damage, key)
    set dst = null
    set src = null
endfunction

function DPS_Text takes string name, real x, real y, real width, string value returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT", name, DPS_Panel, "", 0)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, x, -y)
    call BlzFrameSetSize(f, width, 0.018)
    call BlzFrameSetScale(f, 0.85)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_LEFT)
    call BlzFrameSetText(f, value)
    return f
endfunction

function DPS_Toggle takes nothing returns nothing
    local integer p = GetPlayerId(GetTriggerPlayer())
    // Only presentation changes are local: never create handles or change gameplay here.
    if GetLocalPlayer() == GetTriggerPlayer() then
        set DPS_Open[p] = not DPS_Open[p]
        call BlzFrameSetVisible(DPS_Panel, DPS_Open[p])
        if DPS_Open[p] then
            call BlzFrameSetText(DPS_Button, "Hide player stats")
        else
            call BlzFrameSetText(DPS_Button, "Player stats")
        endif
        call BlzFrameSetEnable(DPS_Button, false)
        call BlzFrameSetEnable(DPS_Button, true)
    endif
endfunction

function DPS_Create takes nothing returns nothing
    local framehandle ui = BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)
    local framehandle board = BlzGetFrameByName("Multiboard", 0)
    local framehandle f
    local trigger click = CreateTrigger()
    local integer s = 1
    local real y
    set DPS_Button = BlzCreateFrame("ScriptDialogButton", ui, 0, 0)
    call BlzFrameSetSize(DPS_Button, 0.125, 0.024)
    call BlzFrameSetPoint(DPS_Button, FRAMEPOINT_TOPRIGHT, board, FRAMEPOINT_BOTTOMRIGHT, 0.0, -0.002)
    call BlzFrameSetText(DPS_Button, "Player stats")
    call BlzFrameSetLevel(DPS_Button, 20)
    call BlzTriggerRegisterFrameEvent(click, DPS_Button, FRAMEEVENT_CONTROL_CLICK)
    call TriggerAddAction(click, function DPS_Toggle)
    set DPS_Panel = BlzCreateFrame("EscMenuBackdrop", ui, 0, 0)
    call BlzFrameSetSize(DPS_Panel, 0.765, 0.337)
    call BlzFrameSetPoint(DPS_Panel, FRAMEPOINT_TOPRIGHT, DPS_Button, FRAMEPOINT_BOTTOMRIGHT, 0.0, -0.002)
    call BlzFrameSetLevel(DPS_Panel, 19)
    set f = DPS_Text("DPS_Title", 0.014, 0.010, 0.72, "|cffffcc00PLAYER STATS|r")
    set f = DPS_Text("DPS_Player", 0.040, 0.035, 0.168, "|cffffcc00Player / Hero|r")
    set f = DPS_Text("DPS_K", 0.210, 0.035, 0.045, "|cffffcc00K|r")
    set f = DPS_Text("DPS_D", 0.250, 0.035, 0.040, "|cffffcc00D|r")
    set f = DPS_Text("DPS_A", 0.290, 0.035, 0.040, "|cffffcc00A|r")
    set f = DPS_Text("DPS_HK", 0.330, 0.035, 0.050, "|cffffcc00HKs|r")
    set f = DPS_Text("DPS_HD", 0.370, 0.035, 0.040, "|cffffcc00HDs|r")
    set f = DPS_Text("DPS_Hill", 0.415, 0.035, 0.070, "|cffffcc00Hill caps|r")
    set f = DPS_Text("DPS_Buildings", 0.480, 0.035, 0.085, "|cffffcc00Buildings|r")
    set f = DPS_Text("DPS_Xmutes", 0.565, 0.035, 0.085, "|cffffcc00Xmutes|r")
    set f = DPS_Text("DPS_Level", 0.675, 0.035, 0.065, "|cffffcc00Level|r")
    loop
        exitwhen s > 12
        set y = 0.059 + I2R(s - 1) * 0.021
        set DPS_Icon[s] = BlzCreateFrameByType("BACKDROP", "DPS_HeroIcon", DPS_Panel, "", s)
        call BlzFrameSetPoint(DPS_Icon[s], FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, 0.014, -y)
        call BlzFrameSetSize(DPS_Icon[s], 0.018, 0.018)
        set DPS_Cell[s * 10] = DPS_Text("DPS_Name", 0.040, y, 0.168, "")
        set DPS_Cell[s * 10 + 1] = DPS_Text("DPS_Kills", 0.210, y, 0.045, "0")
        set DPS_Cell[s * 10 + 2] = DPS_Text("DPS_Deaths", 0.250, y, 0.040, "0")
        set DPS_Cell[s * 10 + 3] = DPS_Text("DPS_Assists", 0.290, y, 0.040, "0")
        set DPS_Cell[s * 10 + 4] = DPS_Text("DPS_HeroKills", 0.330, y, 0.050, "0")
        set DPS_Cell[s * 10 + 9] = DPS_Text("DPS_HeroDeaths", 0.370, y, 0.040, "0")
        set DPS_Cell[s * 10 + 5] = DPS_Text("DPS_Captures", 0.415, y, 0.070, "0")
        set DPS_Cell[s * 10 + 6] = DPS_Text("DPS_Structures", 0.480, y, 0.085, "0")
        set DPS_Cell[s * 10 + 7] = DPS_Text("DPS_Landed", 0.565, y, 0.085, "0")
        set DPS_Cell[s * 10 + 8] = DPS_Text("DPS_CurrentLevel", 0.675, y, 0.065, "-")
        set s = s + 1
    endloop
    set f = DPS_Text("DPS_Legend", 0.014, 0.312, 0.737, "K: unit kills   D: units fed   A: hero assists (10s)   HKs / HDs: hero kills / deaths")
    call BlzFrameSetScale(f, 0.70)
    call BlzFrameSetVisible(DPS_Panel, false)
    set DPS_Ready = true
    set ui = null
    set board = null
    set f = null
    set click = null
endfunction

function DPS_Refresh takes nothing returns nothing
    local integer s = 1
    local integer i
    local unit hero
    local string name
    if not DPS_Ready then
        if udg_multiboard_kills == null or not IsMultiboardDisplayed(udg_multiboard_kills) then
            return
        endif
        call DPS_Create()
    endif
    loop
        exitwhen s > 12
        set i = s * 10
        set name = GetPlayerName(Player(s - 1))
        if udg_coloured_playername[s] != null and udg_coloured_playername[s] != "" then
            set name = udg_coloured_playername[s]
        endif
        if GetPlayerSlotState(Player(s - 1)) == PLAYER_SLOT_STATE_EMPTY then
            set name = "|cff808080Empty slot|r"
        elseif not udg_player_active[s] then
            set name = name + " |cff808080(out)|r"
        endif
        call BlzFrameSetText(DPS_Cell[i], name)
        call BlzFrameSetText(DPS_Cell[i + 1], I2S(udg_unit_kills[s]))
        call BlzFrameSetText(DPS_Cell[i + 2], I2S(udg_unit_deaths[s]))
        call BlzFrameSetText(DPS_Cell[i + 9], I2S(udg_hero_deaths[s]))
        call BlzFrameSetText(DPS_Cell[i + 3], I2S(DPS_Assists[s]))
        call BlzFrameSetText(DPS_Cell[i + 4], I2S(udg_hero_kills[s]))
        call BlzFrameSetText(DPS_Cell[i + 5], I2S(DPS_Caps[s]))
        call BlzFrameSetText(DPS_Cell[i + 6], I2S(DPS_Buildings[s]))
        call BlzFrameSetText(DPS_Cell[i + 7], I2S(FF_st_tmHits[s]))
        set hero = udg_herO[s]
        if hero != null and GetUnitTypeId(hero) != 0 then
            call BlzFrameSetTexture(DPS_Icon[s], BlzGetAbilityIcon(GetUnitTypeId(hero)), 0, true)
            call BlzFrameSetVisible(DPS_Icon[s], true)
            call BlzFrameSetText(DPS_Cell[i + 8], I2S(GetHeroLevel(hero)))
        else
            call BlzFrameSetVisible(DPS_Icon[s], false)
            call BlzFrameSetText(DPS_Cell[i + 8], "-")
        endif
        set s = s + 1
    endloop
    set hero = null
endfunction

function DPS_Init takes nothing returns nothing
    local trigger t = CreateTrigger()
    set DPS_Damage = InitHashtable()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DAMAGED)
    call TriggerAddAction(t, function DPS_OnDamage)
    set t = CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddAction(t, function DPS_OnDeath)
    set DPS_Timer = CreateTimer()
    call TimerStart(DPS_Timer, 1.0, true, function DPS_Refresh)
    set t = null
endfunction
