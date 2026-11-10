def SF_CenterBaseCamera(p):
    x=SF_BaseX[p]
    y=SF_BaseY[p]
    if udg_base[p] != None:
        x=GetUnitX(udg_base[p])
        y=GetUnitY(udg_base[p])
    ResetToGameCameraForPlayer(Player(p - 1), 0.)
    zoom_RestoreFromCacheForPlayer(Player(p - 1))
    if GetLocalPlayer() == Player(p - 1):
        StopCamera()
        SetCameraPosition(x, y)

def SF_FlipRecipePage(shop,buyer):
    key=GetHandleId(shop)
    second=not LoadBoolean(GST_Hash, key, 104701)
    RemoveItemFromStock(shop, 'I00B')
    RemoveItemFromStock(shop, 'I02L')
    RemoveItemFromStock(shop, 'I00Z')
    RemoveItemFromStock(shop, 'I00L')
    RemoveItemFromStock(shop, 'I00M')
    RemoveItemFromStock(shop, 'I00Q')
    RemoveItemFromStock(shop, 'I00O')
    RemoveItemFromStock(shop, 'I00N')
    RemoveItemFromStock(shop, 'I02O')
    RemoveItemFromStock(shop, 'I02X')
    RemoveItemFromStock(shop, 'I03Z')
    RemoveItemFromStock(shop, 'I015')
    RemoveItemFromStock(shop, 'I04B')
    RemoveItemFromStock(shop, 'I00S')
    RemoveItemFromStock(shop, 'I00K')
    RemoveItemFromStock(shop, 'I01I')
    RemoveItemFromStock(shop, 'I01S')
    SaveBoolean(GST_Hash, key, 104701, second)
    if second:
        AddItemToStock(shop, 'I015', 1, 1)
        AddItemToStock(shop, 'I04B', 1, 1)
        AddItemToStock(shop, 'I00S', 1, 1)
        AddItemToStock(shop, 'I00K', 1, 1)
        AddItemToStock(shop, 'I01I', 1, 1)
        AddItemToStock(shop, 'I01S', 1, 1)
    else:
        AddItemToStock(shop, 'I00B', 1, 1)
        AddItemToStock(shop, 'I02L', 1, 1)
        AddItemToStock(shop, 'I00Z', 1, 1)
        AddItemToStock(shop, 'I00L', 1, 1)
        AddItemToStock(shop, 'I00M', 1, 1)
        AddItemToStock(shop, 'I00Q', 1, 1)
        AddItemToStock(shop, 'I00O', 1, 1)
        AddItemToStock(shop, 'I00N', 1, 1)
        AddItemToStock(shop, 'I02O', 1, 1)
        AddItemToStock(shop, 'I02X', 1, 1)
        AddItemToStock(shop, 'I03Z', 1, 1)
    SelectUnitForPlayerSingle(shop, buyer)

def SF_RefreshPage(p):
    i=1
    first=SF_Page[p] * 10 + 1
    last=first + 9
    while True:
        if i > SF_PoolCount[p]: break
        RemoveUnitFromStock(SF_Tavern[p], SF_Pool[p * 128 + i])
        i=i + 1
    RemoveUnitFromStock(SF_Tavern[p], 'hPgN')
    RemoveUnitFromStock(SF_Tavern[p], 'hPgP')
    i=first
    while True:
        if i > last or i > SF_PoolCount[p]: break
        AddUnitToStock(SF_Tavern[p], SF_Pool[p * 128 + i], 1, 1)
        i=i + 1
    AddUnitToStock(SF_Tavern[p], 'hPgN', 1, 1)

def SF_OpenTaverns():
    global SF_Opened,udg_numberofSDcategories
    p=1
    i=None
    h=None
    category=None
    a=None
    if SF_Opened:
        return
    SF_Opened=True
    udg_numberofSDcategories=11
    while True:
        if p > 12: break
        if udg_player_active[p]:
            a=SF_Angle[p]
            SF_Tavern[p]=CreateUnit(Player(p - 1), 'nFHT', SF_BaseX[p] + 320. * Cos(a) - 256. * Sin(a), SF_BaseY[p] + 320. * Sin(a) + 256. * Cos(a), Atan2(-256. - (SF_BaseY[p] + 320. * Sin(a) + 256. * Cos(a)), -(SF_BaseX[p] + 320. * Cos(a) - 256. * Sin(a))) * bj_RADTODEG)
            i=1
            while True:
                if i > udg_total_hero_count: break
                udg_solo_tavern_hero_used[p * 128 + i]=False
                i=i + 1
            category=1
            while True:
                if category > 11: break
                h=SoloFootsTakeTavernHero(p , category)
                if h != 0:
                    SF_PoolCount[p]=SF_PoolCount[p] + 1
                    SF_Pool[p * 128 + SF_PoolCount[p]]=udg_hero_type[h]
                category=category + 1
            while True:
                if SF_PoolCount[p] >= 24: break
                h=SoloFootsTakeTavernHero(p , 0)
                if h == 0: break
                SF_PoolCount[p]=SF_PoolCount[p] + 1
                SF_Pool[p * 128 + SF_PoolCount[p]]=udg_hero_type[h]
            SF_RefreshPage(p)
            SelectUnitForPlayerSingle(SF_Tavern[p], Player(p - 1))
            SF_CenterBaseCamera(p)
            DisplayTimedTextToPlayer(Player(p - 1), 0., 0., 15., "Choose a hero from your base tavern. Use Next page to cycle through all pages. Random hero at mass +15 seconds.")
        p=p + 1

def SF_OnSale():
    shop=GetSellingUnit()
    sold=GetSoldUnit()
    p=GetPlayerId(GetOwningPlayer(shop)) + 1
    id=GetUnitTypeId(sold)
    if GetUnitTypeId(shop) == 'n01Y' and id == 'h037':
        SF_FlipRecipePage(shop, GetOwningPlayer(sold))
        RemoveUnit(sold)
    elif p <= 12 and GetUnitTypeId(shop) == 'nFHT':
        if id == 'hPgN':
            RemoveUnit(sold)
            if SF_Tavern[p] != None and not SF_Picked[p]:
                SF_Page[p]=SF_Page[p] + 1
                if SF_Page[p] * 10 >= SF_PoolCount[p]:
                    SF_Page[p]=0
                SF_RefreshPage(p)
                SelectUnitForPlayerSingle(shop, Player(p - 1))
        elif IsUnitType(sold, UNIT_TYPE_HERO):
            SF_AcceptHero(sold)
    shop=None
    sold=None

def SF_StartBaseSelection():
    p=1
    startup=GetExpiredTimer()
    PauseTimer(udg_Host_AFK_Timer)
    ConditionalTriggerExecute(gg_trg_MODE_set_pub_game)
    while True:
        if p > 12: break
        if udg_player_active[p]:
            SF_CenterBaseCamera(p)
            if SF_Tavern[p] != None:
                SelectUnitForPlayerSingle(SF_Tavern[p], Player(p - 1))
        p=p + 1
    DestroyTimer(startup)
    startup=None

def SF_Initialize():
    global SF_Deadline,SF_GameClock
    p=1
    q=None
    t=CreateTrigger()
    startup=CreateTimer()
    SF_BaseX[10]=- 3635.200
    SF_BaseY[10]=- 256.000
    SF_Angle[10]=3.141592654
    SF_BaseX[12]=- 2570.475
    SF_BaseY[12]=- 2826.475
    SF_Angle[12]=- 2.356194490
    SF_BaseX[7]=- 0.000
    SF_BaseY[7]=- 3891.200
    SF_Angle[7]=- 1.570796327
    SF_BaseX[8]=2570.475
    SF_BaseY[8]=- 2826.475
    SF_Angle[8]=- 0.785398163
    SF_BaseX[4]=3635.200
    SF_BaseY[4]=- 256.000
    SF_Angle[4]=- 0.000000000
    SF_BaseX[5]=2570.475
    SF_BaseY[5]=2314.475
    SF_Angle[5]=0.785398163
    SF_BaseX[2]=0.000
    SF_BaseY[2]=3379.200
    SF_Angle[2]=1.570796327
    SF_BaseX[1]=- 2570.475
    SF_BaseY[1]=2314.475
    SF_Angle[1]=2.356194490
    SF_GameClock=CreateTimer()
    TimerStart(SF_GameClock, 86400., False, None)
    SF_Deadline=CreateTimer()
    while True:
        if p > 12: break
        udg_ally1[p]=Player(p - 1)
        udg_ally2[p]=Player(p - 1)
        q=1
        while True:
            if q > 12: break
            if p != q:
                SetPlayerAllianceStateBJ(Player(p - 1), Player(q - 1), bj_ALLIANCE_UNALLIED)
            q=q + 1
        if udg_player_active[p]:
            RemoveLocation(udg_safe_point[p])
            udg_safe_point[p]=Location(SF_BaseX[p], SF_BaseY[p])
            SetPlayerMaxHeroesAllowed(2, Player(p - 1))
            udg_mode_selector[p]=None
            PanCameraToTimedForPlayer(Player(p - 1), SF_BaseX[p], SF_BaseY[p], 0.)
        p=p + 1
    TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_UNIT_SELL)
    TriggerAddAction(t, SF_OnSale)
    DisableTrigger(gg_trg_AFK_Host_Setup)
    DisableTrigger(gg_trg_AFK_Host_Timer_Expires)
    DisableTrigger(gg_trg_MODE_GUI_show)
    DisableTrigger(gg_trg_MODE_GUI_execute)
    PauseTimer(udg_Host_AFK_Timer)
    TimerStart(startup, 1.10, False, SF_StartBaseSelection)
    startup=None
    t=None

def Trig_Start_game_Func024Func001A():
    SF_CenterBaseCamera(GetPlayerId(GetEnumPlayer()) + 1)

def Trig_Start_game_Func024Func002A():
    SF_CenterBaseCamera(GetPlayerId(GetEnumPlayer()) + 1)