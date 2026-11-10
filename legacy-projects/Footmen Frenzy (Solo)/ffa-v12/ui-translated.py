def DPS_Create():
    global DPS_Button,DPS_Panel,DPS_Ready
    ui = BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)
    board = BlzGetFrameByName("Multiboard", 0)
    f=None
    click = CreateTrigger()
    s=None
    row = 0
    y=None
    DPS_Button = BlzCreateFrame("ScriptDialogButton", ui, 0, 0)
    BlzFrameSetSize(DPS_Button, 0.075, 0.028)
    BlzFrameSetPoint(DPS_Button, FRAMEPOINT_BOTTOM, BlzGetOriginFrame(ORIGIN_FRAME_MINIMAP, 0), FRAMEPOINT_TOP, 0.0, 0.004)
    BlzFrameSetVisible(DPS_Button, True)
    BlzFrameSetText(DPS_Button, "Stats")
    BlzFrameSetLevel(DPS_Button, 20)
    BlzTriggerRegisterFrameEvent(click, DPS_Button, FRAMEEVENT_CONTROL_CLICK)
    TriggerAddAction(click, DPS_Toggle)
    DPS_Panel = BlzCreateFrame("EscMenuBackdrop", ui, 0, 0)
    BlzFrameSetSize(DPS_Panel, 0.650, 0.295)
    BlzFrameSetAbsPoint(DPS_Panel, FRAMEPOINT_TOPLEFT, 0.075, 0.565)
    BlzFrameSetLevel(DPS_Panel, 19)
    f = DPS_Text("DPS_Title",0.026,0.016,0.52,"|cffffcc00Player stats|r   K/D: units   HK/HD: heroes")
    f = DPS_Text("DPS_Player", 0.050, 0.046, 0.150, "|cffffcc00Player / Hero|r")
    f = DPS_Text("DPS_K", 0.205, 0.046, 0.028, "|cffffcc00K|r")
    f = DPS_Text("DPS_D", 0.236, 0.046, 0.028, "|cffffcc00D|r")
    f = DPS_Text("DPS_A", 0.267, 0.046, 0.028, "|cffffcc00A|r")
    f = DPS_Text("DPS_HK", 0.298, 0.046, 0.032, "|cffffcc00HKs|r")
    f = DPS_Text("DPS_HD", 0.333, 0.046, 0.032, "|cffffcc00HDs|r")
    f = DPS_Text("DPS_Hill", 0.370, 0.046, 0.055, "|cffffcc00Hill caps|r")
    f = DPS_Text("DPS_Buildings", 0.430, 0.046, 0.060, "|cffffcc00Buildings|r")
    f = DPS_Text("DPS_Xmutes", 0.495, 0.046, 0.060, "|cffffcc00Xmutes|r")
    f = DPS_Text("DPS_Level", 0.565, 0.046, 0.055, "|cffffcc00Level|r")
    while True:
        if row >= 8: break
        s=F8_Slot[row+1]+1
        y = 0.072 + I2R(row) * 0.024
        DPS_Icon[s] = BlzCreateFrameByType("BACKDROP", "DPS_HeroIcon", DPS_Panel, "", s)
        BlzFrameSetPoint(DPS_Icon[s], FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, 0.026, -y)
        BlzFrameSetSize(DPS_Icon[s], 0.018, 0.018)
        DPS_Cell[s * 10] = DPS_Text("DPS_Name", 0.050, y, 0.150, "")
        DPS_Cell[s * 10 + 1] = DPS_Text("DPS_Kills", 0.205, y, 0.028, "0")
        DPS_Cell[s * 10 + 2] = DPS_Text("DPS_Deaths", 0.236, y, 0.028, "0")
        DPS_Cell[s * 10 + 3] = DPS_Text("DPS_Assists", 0.267, y, 0.028, "0")
        DPS_Cell[s * 10 + 4] = DPS_Text("DPS_HeroKills", 0.298, y, 0.032, "0")
        DPS_Cell[s * 10 + 9] = DPS_Text("DPS_HeroDeaths", 0.333, y, 0.032, "0")
        DPS_Cell[s * 10 + 5] = DPS_Text("DPS_Captures", 0.370, y, 0.055, "0")
        DPS_Cell[s * 10 + 6] = DPS_Text("DPS_Structures", 0.430, y, 0.060, "0")
        DPS_Cell[s * 10 + 7] = DPS_Text("DPS_Landed", 0.495, y, 0.060, "0")
        DPS_Cell[s * 10 + 8] = DPS_Text("DPS_CurrentLevel", 0.565, y, 0.055, "-")
        row = row + 1
    f = BlzCreateFrame("ScriptDialogButton", DPS_Panel, 0, 0)
    BlzFrameSetSize(f, 0.032, 0.026)
    BlzFrameSetPoint(f, FRAMEPOINT_TOPRIGHT, DPS_Panel, FRAMEPOINT_TOPRIGHT, -0.022, -0.018)
    BlzFrameSetLevel(f, 21)
    BlzFrameSetText(f, "X")
    BlzTriggerRegisterFrameEvent(click, f, FRAMEEVENT_CONTROL_CLICK)
    BlzFrameSetVisible(DPS_Panel, False)
    DPS_Ready = True
    ui = None
    board = None
    f = None
    click = None

def DPS_Init():
    global DPS_Clock,DPS_Damage,DPS_Timer
    t = CreateTrigger()
    DPS_Damage = InitHashtable()
    DPS_Clock=CreateTimer()
    TimerStart(DPS_Clock,1000000.,False,None)
    TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DAMAGED)
    TriggerAddAction(t, DPS_OnDamage)
    t = CreateTrigger()
    TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_DEATH)
    TriggerAddAction(t, DPS_OnDeath)
    TriggerAddAction(t, FF_st_OnDeath)
    t=CreateTrigger()
    TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SPELL_EFFECT)
    TriggerAddAction(t,FF_st_OnSpell)
    DPS_Timer = CreateTimer()
    TimerStart(DPS_Timer, 1.0, True, DPS_Refresh)
    t = None

def DPS_OnDamage():
    src = GetEventDamageSource()
    dst = GetTriggerUnit()
    s=None
    if src != None and GetEventDamage() > 0.0 and IsUnitType(dst, UNIT_TYPE_HERO) and not IsUnitIllusion(dst) and IsUnitEnemy(dst, GetOwningPlayer(src)):
        s = FF_st_Slot(GetOwningPlayer(src))
        if s >= 1 and s <= 12:
            SaveReal(DPS_Damage, GetHandleId(dst), s, TimerGetElapsed(DPS_Clock))
    src = None
    dst = None

def DPS_OnDeath():
    dst = GetTriggerUnit()
    src = GetKillingUnit()
    key = GetHandleId(dst)
    ks = 0
    s = 1
    now = TimerGetElapsed(DPS_Clock)
    if src != None and not IsUnitIllusion(dst) and IsUnitEnemy(dst, GetOwningPlayer(src)):
        ks = FF_st_Slot(GetOwningPlayer(src))
        if ks >= 1 and ks <= 12:
            if IsUnitType(dst, UNIT_TYPE_STRUCTURE):
                DPS_Buildings[ks] = DPS_Buildings[ks] + 1
            elif IsUnitType(dst, UNIT_TYPE_HERO):
                while True:
                    if s > 12: break
                    if F8_Team[s-1]>0 and F8_Participant[s] and s != ks and IsPlayerAlly(Player(s - 1), GetOwningPlayer(src)) and IsUnitEnemy(dst, Player(s - 1)) and HaveSavedReal(DPS_Damage, key, s):
                        if now - LoadReal(DPS_Damage, key, s) <= 10.0:
                            DPS_Assists[s] = DPS_Assists[s] + 1
                    s = s + 1
    FlushChildHashtable(DPS_Damage, key)
    dst = None
    src = None

def DPS_Refresh():
    s=None
    row=1
    i=None
    hero=None
    name=None
    if not DPS_Ready:
        DPS_Create()
    while True:
        if row > 8: break
        s=F8_Slot[row]+1
        i = s * 10
        name = GetPlayerName(Player(s - 1))
        if udg_orig_player_name[s] != None and udg_orig_player_name[s] != "":
            name = udg_orig_player_name[s]
        if GetPlayerSlotState(Player(s - 1)) == PLAYER_SLOT_STATE_EMPTY:
            name = "|cff808080Empty slot|r"
        elif not udg_player_active[s]:
            name = name + " |cff808080(out)|r"
        BlzFrameSetText(DPS_Cell[i], name)
        BlzFrameSetText(DPS_Cell[i + 1], I2S(udg_unit_kills[s]))
        BlzFrameSetText(DPS_Cell[i + 2], I2S(udg_unit_deaths[s]))
        BlzFrameSetText(DPS_Cell[i + 9], I2S(udg_hero_deaths[s]))
        BlzFrameSetText(DPS_Cell[i + 3], I2S(DPS_Assists[s]))
        BlzFrameSetText(DPS_Cell[i + 4], I2S(udg_hero_kills[s]))
        BlzFrameSetText(DPS_Cell[i + 5], I2S(DPS_Caps[s]))
        BlzFrameSetText(DPS_Cell[i + 6], I2S(DPS_Buildings[s]))
        BlzFrameSetText(DPS_Cell[i + 7], I2S(FF_st_tmHits[s]))
        hero = udg_herO[s]
        if hero != None and GetUnitTypeId(hero) != 0:
            BlzFrameSetTexture(DPS_Icon[s], BlzGetAbilityIcon(GetUnitTypeId(hero)), 0, True)
            BlzFrameSetVisible(DPS_Icon[s], True)
            BlzFrameSetText(DPS_Cell[i + 8], I2S(GetHeroLevel(hero)))
        else:
            BlzFrameSetVisible(DPS_Icon[s], False)
            BlzFrameSetText(DPS_Cell[i + 8], "-")
        row=row+1
    hero = None

def DPS_Text(name,x,y,width,value):
    f = BlzCreateFrameByType("TEXT", name, DPS_Panel, "", 0)
    BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, x, -y)
    BlzFrameSetSize(f, width, 0.018)
    BlzFrameSetFont(f, "Fonts\\FRIZQT__.TTF", 0.009, 0)
    BlzFrameSetEnable(f, False)
    BlzFrameSetTextAlignment(f, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_LEFT)
    BlzFrameSetText(f, value)
    return f

def DPS_Toggle():
    p = GetPlayerId(GetTriggerPlayer())
    if GetLocalPlayer() == GetTriggerPlayer():
        DPS_Open[p] = not DPS_Open[p]
        BlzFrameSetVisible(DPS_Panel, DPS_Open[p])
        if DPS_Open[p]:
            BlzFrameSetVisible(DPS_Button, True)
            BlzFrameSetText(DPS_Button, "Stats")
        else:
            BlzFrameSetVisible(DPS_Button, True)
            BlzFrameSetText(DPS_Button, "Stats")
        BlzFrameSetEnable(DPS_Button, False)
        BlzFrameSetEnable(DPS_Button, True)

def FF_st_OnDeath():
    victim = GetTriggerUnit()
    killer = GetKillingUnit()
    vp = GetOwningPlayer(victim)
    kp = None
    ks = 0
    i = FF_st_tmN - 1
    if killer != None:
        kp = GetOwningPlayer(killer)
        ks = FF_st_Slot(kp)
    while True:
        if i < 0: break
        if FF_st_tmTarget[i] == victim:
            if killer != None and killer == FF_st_tmCaster[i]:
                FF_st_tmHits[FF_st_tmSlot[i]] = FF_st_tmHits[FF_st_tmSlot[i]] + 1
            else:
                FF_st_tmDenied[FF_st_tmSlot[i]] = FF_st_tmDenied[FF_st_tmSlot[i]] + 1
                if ks > 0 and (kp == vp or IsPlayerAlly(kp, vp)):
                    FF_st_tmSaves[ks] = FF_st_tmSaves[ks] + 1
            FF_st_TmDrop(i)
        i = i - 1
    victim = None
    killer = None
    vp = None
    kp = None

def FF_st_OnSpell():
    global FF_st_tmN
    id = GetSpellAbilityId()
    s=None
    if (id == 'ANtm' or id == 'A0G0') and FF_st_tmN < FF_ST_TM_MAX:
        s = FF_st_Slot(GetOwningPlayer(GetTriggerUnit()))
        if s > 0 and GetSpellTargetUnit() != None:
            FF_st_tmCasts[s] = FF_st_tmCasts[s] + 1
            FF_st_tmCaster[FF_st_tmN] = GetTriggerUnit()
            FF_st_tmTarget[FF_st_tmN] = GetSpellTargetUnit()
            FF_st_tmSlot[FF_st_tmN] = s
            FF_st_tmUntil[FF_st_tmN] = TimerGetElapsed(DPS_Clock) + FF_ST_TM_WAIT
            FF_st_tmN = FF_st_tmN + 1

def FF_st_Slot(p):
    pn=GetPlayerId(p)+1
    if pn>=1 and pn<=12:
        if F8_Team[pn-1]>0 and F8_Participant[pn]:
            return pn
    return 0

def FF_st_TmDrop(i):
    global FF_st_tmN
    FF_st_tmN = FF_st_tmN - 1
    FF_st_tmCaster[i] = FF_st_tmCaster[FF_st_tmN]
    FF_st_tmTarget[i] = FF_st_tmTarget[FF_st_tmN]
    FF_st_tmSlot[i] = FF_st_tmSlot[FF_st_tmN]
    FF_st_tmUntil[i] = FF_st_tmUntil[FF_st_tmN]
    FF_st_tmCaster[FF_st_tmN] = None
    FF_st_tmTarget[FF_st_tmN] = None

def FF_st_TmExpire():
    now = TimerGetElapsed(DPS_Clock)
    i = FF_st_tmN - 1
    while True:
        if i < 0: break
        if now > FF_st_tmUntil[i]:
            FF_st_TmDrop(i)
        i = i - 1

def zoom_Init():
    i= 0
    setTrigger= CreateTrigger()
    infoTrigger= CreateTrigger()
    while True:
        if i >= 24: break
        TriggerRegisterPlayerChatEvent(setTrigger, Player(i), "-zoom ", False)
        TriggerRegisterPlayerChatEvent(setTrigger, Player(i), "-z ", False)
        TriggerRegisterPlayerChatEvent(infoTrigger, Player(i), "-zoom", True)
        TriggerRegisterPlayerChatEvent(infoTrigger, Player(i), "-z", True)
        i=i + 1
    TriggerAddAction(setTrigger, zoom__handleChatCommand)
    TriggerAddAction(infoTrigger, zoom__handleInfoChatCommand)
    zoom__ApplyFog(R2I(GetCameraField(CAMERA_FIELD_TARGET_DISTANCE)))
    zoom_RestoreForAllPlayersFromCache()
    TimerStart(CreateTimer(), 0.50, False, zoom__CreateSlider)

def zoom_RestoreForAllPlayersFromCache():
    i= 0
    while True:
        if i >= 24: break
        if ( GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING ):
            if ( GetLocalPlayer() == Player(i) ):
                zoom__RestoreFromFile()
        i=i + 1

def zoom_RestoreFromCacheForPlayer(p):
    if ( GetLocalPlayer() == p ):
        zoom__RestoreFromFile()

def zoom__ApplyFog(cameraDistance):
    SetCameraField(CAMERA_FIELD_FARZ, 10000.00, 0.00)
    SetTerrainFogEx(0, 10000.00, 11000.00, 0.00, 0.00, 0.00, 0.00)

def zoom__CreateSlider():
    global zoom__lockButton,zoom__lockLabel,zoom__slider,zoom__sliderLabel
    gameUI= BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)
    minimap=BlzGetOriginFrame(ORIGIN_FRAME_MINIMAP, 0)
    sliderTrigger= CreateTrigger()
    lockTrigger= CreateTrigger()
    if ( not BlzLoadTOCFile("war3mapImported\\templates.toc") ):
        BJDebugMsg("|cffff0000Zoom UI failed to load templates.toc.|r")
    BlzLoadTOCFile("MiniFootsUI.toc")
    zoom__slider=BlzCreateFrame("MiniFootsZoomSlider", gameUI, 0, 0)
    zoom__sliderLabel=BlzCreateFrame("EscMenuLabelTextTemplate", zoom__slider, 0, 0)
    BlzFrameClearAllPoints(zoom__slider)
    BlzFrameSetPoint(zoom__slider, FRAMEPOINT_LEFT, minimap, FRAMEPOINT_RIGHT, 0.033, 0.0)
    BlzFrameSetSize(zoom__slider, 0.012, 0.095)
    BlzFrameSetLevel(zoom__slider, 20)
    BlzFrameSetPoint(zoom__sliderLabel, FRAMEPOINT_TOP, zoom__slider, FRAMEPOINT_BOTTOM, 0.0, -0.003)
    BlzFrameSetEnable(zoom__sliderLabel, False)
    BlzFrameSetTextColor(zoom__sliderLabel, 0xFFFFCC00)
    BlzFrameSetFont(zoom__sliderLabel, "Fonts\\FRIZQT__.TTF", 0.009, 0)
    BlzFrameSetSize(zoom__sliderLabel, 0.035, 0.012)
    BlzFrameSetMinMaxValue(zoom__slider, I2R(zoom__gMinDistance), I2R(zoom__gMaxDistance))
    BlzFrameSetStepSize(zoom__slider, 1.00)
    BlzFrameSetEnable(zoom__slider, True)
    BlzFrameSetVisible(zoom__slider, True)
    zoom__lockButton=BlzCreateFrame("ScriptDialogButton", gameUI, 0, 0)
    BlzFrameSetPoint(zoom__lockButton, FRAMEPOINT_BOTTOM, zoom__slider, FRAMEPOINT_TOP, 0.0, 0.003)
    BlzFrameSetSize(zoom__lockButton, 0.025, 0.020)
    BlzFrameSetLevel(zoom__lockButton, 21)
    BlzFrameSetVisible(zoom__lockButton, True)
    BlzFrameSetText(zoom__lockButton, "")
    zoom__lockLabel=BlzCreateFrameByType("TEXT", "", zoom__lockButton, "", 0)
    BlzFrameSetPoint(zoom__lockLabel, FRAMEPOINT_CENTER, zoom__lockButton, FRAMEPOINT_CENTER, 0.0, 0.0)
    BlzFrameSetEnable(zoom__lockLabel, False)
    BlzFrameSetSize(zoom__lockLabel, 0.010, 0.010)
    BlzFrameSetTextAlignment(zoom__lockLabel, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    BlzFrameSetScale(zoom__lockLabel, 0.55)
    BlzFrameSetLevel(zoom__lockLabel, 11)
    BlzFrameSetText(zoom__lockLabel, "|cffffffffX|r")
    BlzTriggerRegisterFrameEvent(sliderTrigger, zoom__slider, FRAMEEVENT_SLIDER_VALUE_CHANGED)
    TriggerAddAction(sliderTrigger, zoom__handleSegment)
    BlzTriggerRegisterFrameEvent(lockTrigger, zoom__lockButton, FRAMEEVENT_CONTROL_CLICK)
    TriggerAddAction(lockTrigger, zoom__handleLockButton)
    BlzFrameSetValue(zoom__slider, GetCameraField(CAMERA_FIELD_TARGET_DISTANCE))
    zoom__UpdateSliderLabel(R2I(GetCameraField(CAMERA_FIELD_TARGET_DISTANCE)))
    minimap=None
    gameUI=None
    sliderTrigger=None
    lockTrigger=None

def zoom__RestoreFromFile():
    file= s__File_open(zoom__gFileName)
    input= ( s__File_readEx(( file ) , False) )
    cameraDistance= S2I(SubString(input, 0, 4))
    s__File_close(file)
    if ( cameraDistance > 0 ):
        cameraDistance=zoom__Zoom(cameraDistance , False)
        if zoom__slider!=None:
            BlzFrameSetValue(zoom__slider,I2R(cameraDistance))
            zoom__UpdateSliderLabel(cameraDistance)

def zoom__Save(cameraDistance):
    file= s__File_open(zoom__gFileName)
    s__File_write(file , I2S(cameraDistance))
    s__File_close(file)

def zoom__UpdateLockButton(p):
    playerId= GetPlayerId(p)
    if ( GetLocalPlayer() == p ):
        BlzFrameSetEnable(zoom__slider, not zoom__sliderLocked[playerId])
        if ( zoom__sliderLocked[playerId] ):
            BlzFrameSetText(zoom__lockLabel, "|cffff3030X|r")
        else:
            BlzFrameSetText(zoom__lockLabel, "|cffffffffX|r")

def zoom__UpdateSliderLabel(cameraDistance):
    BlzFrameSetText(zoom__sliderLabel, I2S(cameraDistance))

def zoom__Zoom(cameraDistance,withMessaging):
    wasValid= False
    previousCameraDistance= R2I(GetCameraField(CAMERA_FIELD_TARGET_DISTANCE))
    if ( previousCameraDistance == cameraDistance ):
        if ( withMessaging ):
            DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "Already at target zoom level")
    else:
        if ( cameraDistance > zoom__gMaxDistance ):
            cameraDistance=zoom__gMaxDistance
        elif ( cameraDistance < zoom__gMinDistance ):
            cameraDistance=zoom__gMinDistance
        else:
            wasValid=True
        if ( withMessaging and not ( wasValid ) ):
            DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "Valid zoom range: " + I2S(zoom__gMinDistance) + " up to " + I2S(zoom__gMaxDistance))
        if ( withMessaging ):
            DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "New zoom level: " + I2S(cameraDistance))
        SetCameraField(CAMERA_FIELD_TARGET_DISTANCE, cameraDistance, 0.00)
    zoom__ApplyFog(cameraDistance)
    return cameraDistance

def zoom__handleChatCommand():
    commandText= GetEventPlayerChatString()
    cameraDistanceStr=None
    cameraDistance= 0
    if ( SubString(commandText, 0, 3) == "-z " ):
        cameraDistanceStr=SubString(commandText, 3, StringLength(commandText))
    else:
        cameraDistanceStr=SubString(commandText, 6, StringLength(commandText))
    if ( GetLocalPlayer() == GetTriggerPlayer() ):
        if ( cameraDistanceStr != " " ):
            cameraDistance=S2I(cameraDistanceStr)
        if ( cameraDistance == 0 ):
            DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "Invalid zoom command usage. Example: \"-z 2500\" or \"-zoom 2500\"")
        else:
            cameraDistance=zoom__Zoom(cameraDistance , True)
            BlzFrameSetValue(zoom__slider, I2R(cameraDistance))
            zoom__UpdateSliderLabel(cameraDistance)
            zoom__Save(cameraDistance)

def zoom__handleInfoChatCommand():
    if ( GetLocalPlayer() == GetTriggerPlayer() ):
        DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "Current zoom level: " + I2S(R2I(GetCameraField(CAMERA_FIELD_TARGET_DISTANCE))))

def zoom__handleLockButton():
    p= GetTriggerPlayer()
    playerId= GetPlayerId(p)
    zoom__sliderLocked[playerId]=not zoom__sliderLocked[playerId]
    zoom__UpdateLockButton(p)
    if ( GetLocalPlayer() == p ):
        BlzFrameSetEnable(zoom__lockButton, False)
        BlzFrameSetEnable(zoom__lockButton, True)
    p=None

def zoom__handleSegment():
    p= GetTriggerPlayer()
    playerId= GetPlayerId(p)
    cameraDistance=None
    if ( GetLocalPlayer() == p and not zoom__sliderLocked[playerId] ):
        cameraDistance=R2I(BlzGetTriggerFrameValue())
        cameraDistance=zoom__Zoom(cameraDistance , False)
        zoom__UpdateSliderLabel(cameraDistance)
        zoom__Save(cameraDistance)
    p=None