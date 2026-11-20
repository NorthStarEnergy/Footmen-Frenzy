function CatalogRefresh takes nothing returns nothing
    local string unitName
    local string skin
    local string texture
    if CatalogUnitIndex == 0 then
        set unitName = "Footman"
        if CatalogVariant == 0 then
            set skin = "Footman"
            set texture = "BTNFootman"
        else
            set skin = "Captain"
            set texture = "BTNTheCaptain"
        endif
    else
        set unitName = "Archer"
        if CatalogVariant == 0 then
            set skin = "Night Elf Archer"
            set texture = "BTNArcher"
        else
            set skin = "High Elf Archer"
            set texture = "BTNHighElvenArcher"
        endif
    endif
    call BlzFrameSetText(CatalogTitle, "|cffffcc00Skins|r   " + WalletText())
    call BlzFrameSetText(CatalogUnit, "Unit: " + unitName)
    call BlzFrameSetText(CatalogChoice, skin + "   (Preview)")
    call BlzFrameSetTexture(CatalogPreview, "ReplaceableTextures\\CommandButtons\\" + texture + ".blp", 0, true)
endfunction

function CatalogClick takes nothing returns nothing
    local framehandle f = BlzGetTriggerFrame()
    if f == CatalogCasino then
        if PK_Eligible(GetPlayerId(GetTriggerPlayer())) then
            set CasinoLauncherSlot = GetPlayerId(GetTriggerPlayer())+1
            call TriggerExecute(CasinoOpen)
        else
            call DisplayTimedTextToPlayer(GetTriggerPlayer(), 0, 0, 3.0, "Casino is unavailable for this player.")
        endif
        set f = null
        return
    endif
    if GetTriggerPlayer() == GetLocalPlayer() then
        if f == CatalogBack then
            set CatalogKind = 0
        elseif f == CatalogUnit then
            set CatalogUnitIndex = 1 - CatalogUnitIndex
            set CatalogVariant = 0
        elseif f == CatalogNext then
            set CatalogVariant = 1 - CatalogVariant
        elseif f == CatalogSkins then
            set CatalogKind = 1
        else
            set f = null
            return
        endif
        call BlzFrameSetVisible(CatalogPanel, CatalogKind != 0)
        call BlzFrameSetVisible(DPS_Table, CatalogKind == 0 and not DPS_Personal)
        call BlzFrameSetVisible(DPS_ProfileText, CatalogKind == 0 and DPS_Personal)
        call BlzFrameSetVisible(DPS_PageButton, CatalogKind == 0)
        call BlzFrameSetVisible(spellKeysToggle, CatalogKind == 0)
        call BlzFrameSetVisible(CatalogSkins, CatalogKind == 0)
        call BlzFrameSetVisible(CatalogCasino,CasinoAdmin(GetPlayerId(GetLocalPlayer())+1) and CatalogKind == 0)
        if CatalogKind != 0 then
            call CatalogRefresh()
        endif
    endif
    set f = null
endfunction

function CatalogButton takes framehandle parent, trigger click, string title, real x, real y returns framehandle
    local framehandle f = BlzCreateFrame("ScriptDialogButton", parent, 0, 0)
    call BlzFrameSetSize(f, 0.110, 0.026)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, parent, FRAMEPOINT_TOPLEFT, x, -y)
    call BlzFrameSetText(f, title)
    call BlzTriggerRegisterFrameEvent(click, f, FRAMEEVENT_CONTROL_CLICK)
    return f
endfunction

function CatalogCreate takes nothing returns nothing
    local trigger click = CreateTrigger()
    call TriggerAddAction(click, function CatalogClick)
    set CatalogSkins = CatalogButton(DPS_Panel, click, "Skins", 0.170, 0.018)
    set CatalogCasino = BlzCreateFrame("ScriptDialogButton",DPS_Panel,0,0)
    call BlzFrameSetSize(CatalogCasino,0.11,0.026)
    call BlzFrameSetPoint(CatalogCasino,FRAMEPOINT_TOPLEFT,DPS_Panel,FRAMEPOINT_TOPLEFT,0.410,-0.018)
    call BlzFrameSetText(CatalogCasino,"Casino")
    call BlzTriggerRegisterFrameEvent(click,CatalogCasino,FRAMEEVENT_CONTROL_CLICK)
    call BlzFrameSetVisible(CatalogCasino,CasinoAdmin(GetPlayerId(GetLocalPlayer())+1))
    set CatalogPanel = BlzCreateFrameByType("FRAME", "WalletCatalog", DPS_Panel, "", 0)
    call BlzFrameSetAllPoints(CatalogPanel, DPS_Panel)
    set CatalogTitle = BlzCreateFrameByType("TEXT", "WalletCatalogTitle", CatalogPanel, "", 0)
    call BlzFrameSetPoint(CatalogTitle, FRAMEPOINT_TOPLEFT, CatalogPanel, FRAMEPOINT_TOPLEFT, 0.05, -0.055)
    set CatalogPreview = BlzCreateFrameByType("BACKDROP", "WalletSkinIcon", CatalogPanel, "", 0)
    call BlzFrameSetSize(CatalogPreview, 0.068, 0.068)
    call BlzFrameSetPoint(CatalogPreview, FRAMEPOINT_TOPLEFT, CatalogPanel, FRAMEPOINT_TOPLEFT, 0.05, -0.130)
    set CatalogChoice = BlzCreateFrameByType("TEXT", "WalletSkinName", CatalogPanel, "", 0)
    call BlzFrameSetPoint(CatalogChoice, FRAMEPOINT_LEFT, CatalogPreview, FRAMEPOINT_RIGHT, 0.015, 0.)
    set CatalogUnit = CatalogButton(CatalogPanel, click, "Unit", 0.050, 0.220)
    set CatalogNext = CatalogButton(CatalogPanel, click, "Next skin", 0.170, 0.220)
    set CatalogBack = CatalogButton(CatalogPanel, click, "Back to Stats", 0.050, 0.300)
    call BlzFrameSetVisible(CatalogPanel, false)
    set click = null
endfunction
