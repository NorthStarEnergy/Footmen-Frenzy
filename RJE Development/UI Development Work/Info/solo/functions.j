function DPS_Field takes integer value returns string
    local string digits = I2S(value)
    return SubString("0000000000", 0, 10 - StringLength(digits)) + digits
endfunction

function DPS_Mask takes integer stat returns integer
    return BlzBitAnd(StringHash(DPS_ProfilePath + "/solo/v1/" + I2S(stat)), 2147483647)
endfunction

function DPS_Toggle takes nothing returns nothing
    local integer p = GetPlayerId(GetTriggerPlayer())
    // Only presentation changes are local: never create handles or change gameplay here.
    if GetLocalPlayer() == GetTriggerPlayer() then
        if BlzGetTriggerFrame() != DPS_Button then
            call SoloCloseProfile()
            return
        endif
        if PF_frozen then
            call PF_Open(true)
            return
        endif
        if spellKeysOpen then
            set spellKeysOpen = false
            set spellKeysEditing = -1
            call BlzFrameSetVisible(spellKeysPanel, false)
            set DPS_Open[p] = false
        else
            set DPS_Open[p] = not DPS_Open[p]
        endif
        call BlzFrameSetVisible(DPS_Panel, DPS_Open[p])
        call BlzFrameSetEnable(DPS_Button, false)
        call BlzFrameSetEnable(DPS_Button, true)
        call BlzFrameSetFocus(DPS_Button, false)
    endif
endfunction

function DPS_Create takes nothing returns nothing
    local framehandle ui = BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)
    local framehandle board = BlzGetFrameByName("Multiboard", 0)
    local framehandle f
    local trigger personal = CreateTrigger()
    local trigger click = CreateTrigger()
    local integer s = 1
    local integer row = 0
    local real y
    set DPS_Button = BlzCreateFrame("ScriptDialogButton", ui, 0, 0)
    call BlzFrameSetScale(DPS_Button, 1.0)
    call BlzFrameSetSize(DPS_Button, 0.066, 0.026)
    call BlzFrameSetPoint(DPS_Button, FRAMEPOINT_BOTTOM, BlzGetOriginFrame(ORIGIN_FRAME_MINIMAP, 0), FRAMEPOINT_TOP, 0.0, 0.003)
    call BlzFrameSetVisible(DPS_Button, true)
    call BlzFrameSetText(DPS_Button, "Info")
    call BlzFrameSetLevel(DPS_Button, 20)
    call BlzTriggerRegisterFrameEvent(click, DPS_Button, FRAMEEVENT_CONTROL_CLICK)
    call TriggerAddAction(click, function DPS_Toggle)
    set DPS_Panel = BlzCreateFrame("EscMenuBackdrop", ui, 0, 0)
    call BlzFrameSetSize(DPS_Panel, 0.650, 0.393)
    call BlzFrameSetAbsPoint(DPS_Panel, FRAMEPOINT_TOPLEFT, 0.075, 0.565)
    call BlzFrameSetLevel(DPS_Panel, 19)
    set f = DPS_Text("DPS_Player", 0.050, 0.046, 0.150, "|cffffcc00Player / Hero|r")
    set f = DPS_Text("DPS_K", 0.205, 0.046, 0.028, "|cffffcc00K|r")
    set f = DPS_Text("DPS_D", 0.236, 0.046, 0.028, "|cffffcc00D|r")
    set f = DPS_Text("DPS_A", 0.267, 0.046, 0.028, "|cffffcc00A|r")
    set f = DPS_Text("DPS_HK", 0.298, 0.046, 0.032, "|cffffcc00HKs|r")
    set f = DPS_Text("DPS_HD", 0.333, 0.046, 0.032, "|cffffcc00HDs|r")
    set f = DPS_Text("DPS_Hill", 0.370, 0.046, 0.055, "|cffffcc00Hill caps|r")
    set f = DPS_Text("DPS_Buildings", 0.430, 0.046, 0.060, "|cffffcc00Buildings|r")
    set f = DPS_Text("DPS_Xmutes", 0.495, 0.046, 0.060, "|cffffcc00Xmutes|r")
    set f = DPS_Text("DPS_Level", 0.565, 0.046, 0.055, "|cffffcc00Level|r")
    loop
        exitwhen s > 12
        if PF_SoloSeat(s) then
        set y = 0.072 + I2R(row) * 0.022 + I2R(row / 3) * 0.003
        set DPS_Icon[s] = BlzCreateFrameByType("BACKDROP", "DPS_HeroIcon", DPS_Panel, "", s)
        call BlzFrameSetPoint(DPS_Icon[s], FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, 0.026, -y)
        call BlzFrameSetSize(DPS_Icon[s], 0.018, 0.018)
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
        endif
        set s = s + 1
    endloop
    set f = BlzCreateFrame("ScriptDialogButton", DPS_Panel, 0, 0)
    call BlzFrameSetSize(f, 0.032, 0.026)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPRIGHT, DPS_Panel, FRAMEPOINT_TOPRIGHT, -0.022, -0.018)
    call BlzFrameSetLevel(f, 21)
    call BlzFrameSetText(f, "X")
    call BlzTriggerRegisterFrameEvent(click, f, FRAMEEVENT_CONTROL_CLICK)
    call BlzFrameSetVisible(DPS_Panel, false)
    set f = BlzCreateFrame("ScriptDialogButton",DPS_Panel,0,0)
    call BlzFrameSetSize(f,0.09,0.026)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPRIGHT,DPS_Panel,FRAMEPOINT_TOPRIGHT,-0.145,-0.012)
    set CasinoMenuButton = f
    call BlzFrameSetVisible(f,CasinoAdmin(GetPlayerId(GetLocalPlayer())+1))
    call BlzFrameSetText(f,"Casino")
    call BlzTriggerRegisterFrameEvent(SoloCasinoLaunch,f,FRAMEEVENT_CONTROL_CLICK)
    set f = BlzCreateFrame("ScriptDialogButton",DPS_Panel,0,0)
    call BlzFrameSetSize(f,0.100,0.026)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,DPS_Panel,FRAMEPOINT_TOPLEFT,0.025,-0.012)
    call BlzFrameSetText(f,"My Profile")
    call BlzTriggerRegisterFrameEvent(personal,f,FRAMEEVENT_CONTROL_CLICK)
    call TriggerAddAction(personal,function PF_SoloOpenProfile)
    set personal = null
    call PF_Create()
    set DPS_Ready = true
    set ui = null
    set board = null
    set f = null
    set click = null
    call FF_LinkProfile()
endfunction

function DPS_Refresh takes nothing returns nothing
    local integer s = 1
    local integer i
    local unit hero
    local string name
    if not DPS_Ready then
        call DPS_Create()
    endif
    loop
        exitwhen s > 12
        if PF_SoloSeat(s) then
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
        endif
        set s = s + 1
    endloop
    call PF_SoloPersonal()
    set PF_saveTick = PF_saveTick+1
    if not PF_careerReady or ModuloInteger(PF_saveTick,15) == 0 or (PF_frozen and not PF_shown) then
        call PF_UpdateCareer()
    endif
    call PF_SendHistory()
    call PF_SendHistory()
    if PF_frozen and not PF_shown then
        set PF_shown = true
        call SoloCloseProfile()
        call PF_Open(true)
    elseif PF_visible and not PF_results then
        call PF_Render()
    endif
    set hero = null
endfunction
