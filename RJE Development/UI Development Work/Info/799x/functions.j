function DPS_Current takes integer slot, integer stat returns integer
    if stat == 0 then
        return udg_unit_kills[slot]
    elseif stat == 1 then
        return udg_unit_deaths[slot]
    elseif stat == 2 then
        return DPS_Assists[slot]
    elseif stat == 3 then
        return udg_hero_kills[slot]
    elseif stat == 4 then
        return udg_hero_deaths[slot]
    elseif stat == 5 then
        return DPS_Caps[slot]
    elseif stat == 6 then
        return DPS_Buildings[slot]
    endif
    return FF_st_tmHits[slot]
endfunction

function DPS_Field takes integer value returns string
    local string digits = I2S(value)
    return SubString("0000000000", 0, 10 - StringLength(digits)) + digits
endfunction

function DPS_Mask takes integer stat returns integer
    return BlzBitAnd(StringHash(DPS_ProfilePath + "/799x/v1/" + I2S(stat)), 2147483647)
endfunction

function DPS_Flip takes nothing returns nothing
    if GetTriggerPlayer() == GetLocalPlayer() then
        call PF_UpdateCareer()
        call PF_Open(false)
    endif
endfunction

function DPS_Text takes string name, real x, real y, real width, string value returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT", name, DPS_Table, "", 0)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, x, -y)
    call BlzFrameSetSize(f, width, 0.018)
    call BlzFrameSetFont(f, "Fonts\\FRIZQT__.TTF", 0.009, 0)
    call BlzFrameSetEnable(f, false)
    call BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_LEFT)
    call BlzFrameSetText(f, value)
    return f
endfunction

function DPS_Toggle takes nothing returns nothing
    local integer p = GetPlayerId(GetTriggerPlayer())
    local framehandle clicked = BlzGetTriggerFrame()
    if GetLocalPlayer() == GetTriggerPlayer() then
        if BlzGetTriggerFrame() != DPS_Button then
            call FF_CloseProfilePanels()
            return
        endif
        if PF_frozen then
            call PF_Open(true)
            return
        endif
        set DPS_Open[p] = not DPS_Open[p]
        set spellKeysOpen = false
        set spellKeysEditing = -1
        call BlzFrameSetVisible(spellKeysPanel, false)
        if DPS_Open[p] then
            set DPS_Personal = false
            set CatalogKind = 0
            call BlzFrameSetVisible(CatalogPanel, false)
            call BlzFrameSetVisible(DPS_Table, true)
            call BlzFrameSetVisible(DPS_ProfileText, false)
            call BlzFrameSetVisible(DPS_PageButton, true)
            call BlzFrameSetText(DPS_PageButton, "Profile")
            call BlzFrameSetVisible(spellKeysToggle, true)
            call BlzFrameSetVisible(CatalogSkins, true)
            call BlzFrameSetVisible(CatalogCasino,CasinoAdmin(GetPlayerId(GetLocalPlayer())+1))
        endif
        call BlzFrameSetVisible(DPS_Panel, DPS_Open[p])
        call BlzFrameSetEnable(clicked, false)
        call BlzFrameSetEnable(clicked, true)
        call BlzFrameSetFocus(clicked, false)
    endif
    set clicked = null
endfunction

function DPS_Create takes nothing returns nothing
    local framehandle ui = FFUI_GetRoot()
    local framehandle board = BlzGetFrameByName("Multiboard", 0)
    local framehandle f
    local trigger click = CreateTrigger()
    local trigger pageClick
    local integer s = 1
    local integer row = 0
    local real y
    set DPS_Button = BlzCreateFrame("ScriptDialogButton", ui, 0, 0)
    call BlzFrameSetScale(DPS_Button, 1.0)
    call BlzFrameSetSize(DPS_Button, 0.066, 0.026)
    call BlzFrameSetPoint(DPS_Button, FRAMEPOINT_BOTTOM, BlzGetOriginFrame(ORIGIN_FRAME_MINIMAP, 0), FRAMEPOINT_TOP, 0.0, 0.002)
    call BlzFrameSetVisible(DPS_Button, true)
    call BlzFrameSetText(DPS_Button, "Info")
    call BlzFrameSetLevel(DPS_Button, 20)
    call BlzTriggerRegisterFrameEvent(click, DPS_Button, FRAMEEVENT_CONTROL_CLICK)
    call TriggerAddAction(click, function DPS_Toggle)
    set DPS_Panel = BlzCreateFrame("EscMenuBackdrop", ui, 0, 0)
    call BlzFrameSetSize(DPS_Panel, 0.715, 0.393)
    call BlzFrameSetAbsPoint(DPS_Panel, FRAMEPOINT_TOPLEFT, 0.0425, 0.526)
    call BlzFrameSetLevel(DPS_Panel, 19)
    set DPS_Table = BlzCreateFrameByType("FRAME", "DPS_Table", DPS_Panel, "", 0)
    call BlzFrameSetAllPoints(DPS_Table, DPS_Panel)
    set DPS_ProfileText = BlzCreateFrameByType("TEXT", "DPS_Profile", DPS_Panel, "", 0)
    call BlzFrameSetPoint(DPS_ProfileText, FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, 0.050, -0.060)
    call BlzFrameSetSize(DPS_ProfileText, 0.550, 0.290)
    call BlzFrameSetTextAlignment(DPS_ProfileText, TEXT_JUSTIFY_TOP, TEXT_JUSTIFY_LEFT)
    call BlzFrameSetVisible(DPS_ProfileText, false)
    set DPS_PageButton = BlzCreateFrame("ScriptDialogButton", DPS_Panel, 0, 0)
    call BlzFrameSetSize(DPS_PageButton, 0.110, 0.026)
    call BlzFrameSetPoint(DPS_PageButton, FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, 0.050, -0.018)
    call BlzFrameSetText(DPS_PageButton, "Profile")
    set pageClick = CreateTrigger()
    call BlzTriggerRegisterFrameEvent(pageClick, DPS_PageButton, FRAMEEVENT_CONTROL_CLICK)
    call TriggerAddAction(pageClick, function DPS_Flip)
    set pageClick = null
    set f = DPS_Text("DPS_Player", 0.050, 0.046, 0.150, "|cffffcc00Player / Hero|r")
    set f = DPS_Text("DPS_K", 0.205, 0.046, 0.028, "|cffffcc00K|r")
    set f = DPS_Text("DPS_D", 0.236, 0.046, 0.028, "|cffffcc00D|r")
    set f = DPS_Text("DPS_A", 0.267, 0.046, 0.028, "|cffffcc00A|r")
    set f = DPS_Text("DPS_HK", 0.298, 0.046, 0.032, "|cffffcc00HKs|r")
    set f = DPS_Text("DPS_HD", 0.333, 0.046, 0.032, "|cffffcc00HDs|r")
    set f = DPS_Text("DPS_Hill", 0.370, 0.046, 0.055, "|cffffcc00Hill caps|r")
    set f = DPS_Text("DPS_Buildings", 0.430, 0.046, 0.060, "|cffffcc00Buildings|r")
    set f = DPS_Text("DPS_Xmutes", 0.495, 0.046, 0.060, "|cffffcc00Xmutes|r")
    set f = DPS_Text("DPS_GoldHeader", 0.620, 0.046, 0.070, "|cffffcc00Wallet|r")
    set f = DPS_Text("DPS_Level", 0.565, 0.046, 0.055, "|cffffcc00Level|r")
    loop
        exitwhen s > 12
        set y = 0.072 + I2R(row) * 0.022 + I2R(row / 3) * 0.003
        set DPS_Icon[s] = BlzCreateFrameByType("BACKDROP", "DPS_HeroIcon", DPS_Table, "", s)
        call BlzFrameSetPoint(DPS_Icon[s], FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, 0.026, -y)
        call BlzFrameSetSize(DPS_Icon[s], 0.018, 0.018)
        set DPS_Gold[s] = DPS_Text("DPS_Gold", 0.620, y, 0.070, "-")
        call BlzFrameSetFont(DPS_Gold[s],"CasinoUI\\Bold.ttf",0.011,0)
        set DPS_Cell[s * 10] = DPS_Text("DPS_Name", 0.050, y, 0.150, "")
        set DPS_Cell[s * 10 + 1] = DPS_Text("DPS_Kills", 0.205, y, 0.028, "0")
        set DPS_Cell[s * 10 + 2] = DPS_Text("DPS_Deaths", 0.236, y, 0.028, "0")
        set DPS_Cell[s * 10 + 3] = DPS_Text("DPS_Assists", 0.267, y, 0.028, "0")
        set DPS_Cell[s * 10 + 4] = DPS_Text("DPS_HeroKills", 0.298, y, 0.032, "0")
        set DPS_Cell[s * 10 + 9] = DPS_Text("DPS_HeroDeaths", 0.333, y, 0.032, "0")
        set DPS_Cell[s * 10 + 5] = DPS_Text("DPS_Captures", 0.370, y, 0.055, "0")
        set DPS_Cell[s * 10 + 6] = DPS_Text("DPS_Structures", 0.430, y, 0.060, "0")
        set DPS_Cell[s * 10 + 7] = DPS_Text("DPS_Landed", 0.495, y, 0.060, "0")
        set DPS_Cell[s * 10 + 8] = DPS_Text("DPS_CurrentLevel", 0.565, y, 0.055, "-")
        set row = row + 1
        set s = s + 1
    endloop
    set f = BlzCreateFrame("ScriptDialogButton", DPS_Panel, 0, 0)
    call BlzFrameSetSize(f, 0.032, 0.026)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPRIGHT, DPS_Panel, FRAMEPOINT_TOPRIGHT, -0.022, -0.018)
    call BlzFrameSetLevel(f, 21)
    call BlzFrameSetText(f, "X")
    call BlzTriggerRegisterFrameEvent(click, f, FRAMEEVENT_CONTROL_CLICK)
    call BlzFrameSetVisible(DPS_Panel, false)
    call CatalogCreate()
    set pageClick = CreateTrigger()
    set spellKeysToggle = CatalogButton(DPS_Panel, pageClick, "Hotkeys", 0.290, 0.018)
    call BlzFrameSetSize(spellKeysToggle, 0.110, 0.026)
    call TriggerAddAction(pageClick, function SpellKeysClick)
    set pageClick = null
    call PF_Create()
    set DPS_Ready = true
    set ui = null
    set board = null
    set f = null
    set click = null
endfunction

function DPS_Refresh takes nothing returns nothing
    local integer walletId
    local integer s = 1
    local integer i
    local unit hero
    local string name
    call HUD_Refresh()
    if not DPS_Ready then
        call DPS_Create()
    endif
    loop
        exitwhen s > 12
        set i = s * 10
        set name = GetPlayerName(Player(s - 1))
        if udg_orig_player_name[s] != null and udg_orig_player_name[s] != "" then
            set name = udg_orig_player_name[s]
        endif
        if GetPlayerSlotState(Player(s - 1)) == PLAYER_SLOT_STATE_EMPTY then
            set name = "|cff808080Empty slot|r"
        elseif not udg_player_active[s] then
            set name = name + " |cff808080(out)|r"
        endif
        set walletId = s - 1
        if SoloSub_observerForPlayer[s] > 0 then
            set walletId = SoloSub_observerForPlayer[s] - 1
        endif
        if WalletKnown[walletId] then
            call BlzFrameSetText(DPS_Gold[s], I2S(WalletPublic[walletId]))
        else
            call BlzFrameSetText(DPS_Gold[s], "-")
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
    call DPS_ProfileUpdate()
    set PF_saveTick = PF_saveTick+1
    if not PF_careerReady or ModuloInteger(PF_saveTick,15) == 0 or (PF_frozen and not PF_shown) then
        call PF_UpdateCareer()
    endif
    call PF_SendHistory()
    call PF_SendHistory()
    if PF_frozen and not PF_shown then
        set PF_shown = true
        call FF_CloseProfilePanels()
        call PF_Open(true)
    elseif PF_visible and not PF_results then
        call PF_Render()
    endif
    if CatalogKind != 0 then
        call CatalogRefresh()
    endif
    set hero = null
endfunction

function DPS_Init takes nothing returns nothing
    local trigger t = CreateTrigger()
    local trigger PF_sync = CreateTrigger()
    local trigger sync = CreateTrigger()
    local integer id = 0
    loop
        exitwhen id >= bj_MAX_PLAYER_SLOTS
        call BlzTriggerRegisterPlayerSyncEvent(PF_sync,Player(id),"FFCareer22",false)
        call BlzTriggerRegisterPlayerSyncEvent(sync, Player(id), "FFWallet1", false)
        call BlzTriggerRegisterPlayerSyncEvent(sync, Player(id), "FFWalletNew", false)
        set id = id + 1
    endloop
    call TriggerAddAction(PF_sync,function PF_ReceiveHistory)
    set PF_sync = null
    call TriggerAddAction(sync, function WalletReceive)
    call HUD_Create()
    call TimerStart(CreateTimer(), 0.00, false, function WalletLoad)
    set sync = null
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
