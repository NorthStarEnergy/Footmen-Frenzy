def SF_RemoveTavern(p):
    if SF_Tavern[p] != None:
        RemoveUnit(SF_Tavern[p])
        SF_Tavern[p]=None

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
    AddUnitToStock(SF_Tavern[p], 'hPgP', 1, 1)
    AddUnitToStock(SF_Tavern[p], 'hPgN', 1, 1)

def SF_OpenTaverns():
    global SF_Opened,udg_numberofSDcategories
    p=1
    i=None
    h=None
    category=None
    a=None
    if SF_Opened or SF_SelectionClosed:
        return
    SF_Opened=True
    udg_numberofSDcategories=11
    while True:
        if p > 12: break
        if udg_player_active[p] and not SF_Picked[p]:
            a=SF_Angle[p]
            SF_Tavern[p]=CreateUnit(Player(p - 1), 'nFHT', SF_BaseX[p] + -200. * Cos(a) + 560. * Sin(a), SF_BaseY[p] + -200. * Sin(a) - 560. * Cos(a), a * bj_RADTODEG + 180.)
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
            PanCameraToTimedForPlayer(Player(p - 1), SF_BaseX[p], SF_BaseY[p], 0.)
            DisplayTimedTextToPlayer(Player(p - 1), 0., 0., 15., "Choose a hero from your base tavern. Use Next / Previous to browse. Random hero at mass +15 seconds.")
        p=p + 1

def SF_AcceptHero(hero):
    global udg_X,udg_hero_bounty_multiplier,udg_numberofSDcategories,udg_temp_level,udg_temp_playernumber,udg_temp_point,udg_temp_real,udg_temp_unit
    ownerId=GetPlayerId(GetOwningPlayer(hero)) + 1
    rosterIndex=1
    knownHero=False
    if hero==None or IsUnitIllusion(hero) or not IsUnitType(hero, UNIT_TYPE_HERO):
        return
    while True:
        if rosterIndex>udg_total_hero_count: break
        if GetUnitTypeId(hero)==udg_hero_type[rosterIndex]:
            knownHero=True
        rosterIndex=rosterIndex+1
    if not knownHero:
        return
    if ownerId > 12 or not udg_player_active[ownerId] or SF_Picked[ownerId]:
        return
    SF_Picked[ownerId]=True
    SF_HeroCount[ownerId]=1
    udg_temp_unit=hero
    udg_temp_playernumber=GetConvertedPlayerId(GetOwningPlayer(udg_temp_unit))
    udg_temp_point=GetPlayerStartLocationLoc(GetOwningPlayer(udg_temp_unit))
    if True:
        udg_tp_kill[udg_temp_playernumber]=True
        udg_herO[udg_temp_playernumber]=udg_temp_unit
        SetUnitPositionLoc(udg_temp_unit, udg_temp_point)
        UnitAddItemByIdSwapped('stwp', udg_temp_unit)
        UnitAddItemByIdSwapped('I001', udg_temp_unit)
        UnitAddItemByIdSwapped('pinv', udg_temp_unit)
        UnitAddItemByIdSwapped('hslv', udg_temp_unit)
        UnitAddItemByIdSwapped('I01C', udg_temp_unit)
        PanCameraToTimedLocForPlayer(ConvertedPlayer(udg_temp_playernumber), udg_temp_point, 1.00)
        zoom_RestoreFromCacheForPlayer(Player(udg_temp_playernumber - 1))
        SetPlayerName(ConvertedPlayer(udg_temp_playernumber), ( ( "(" + ( GetUnitName(udg_temp_unit) + ") " ) ) + udg_orig_player_name[udg_temp_playernumber] ))
        udg_coloured_playername[udg_temp_playernumber]=( udg_colour[udg_temp_playernumber] + ( GetPlayerName(ConvertedPlayer(udg_temp_playernumber)) + "|r" ) )
        udg_X=1
        while True:
            if udg_X > udg_total_hero_count: break
            if ( Trig_TP_hero_Func006Func017Func001C() ):
                udg_picked_hero[udg_temp_playernumber]=udg_X
                if ( Trig_TP_hero_Func006Func017Func001Func003C() ):
                    BlzSetUnitIntegerFieldBJ(udg_temp_unit, UNIT_IF_STRENGTH, ( R2I(udg_hero_STR_base[udg_X]) + ( R2I(udg_hero_STR_inc[udg_X]) * 5 ) ))
                    BlzSetUnitIntegerFieldBJ(udg_temp_unit, UNIT_IF_INTELLIGENCE, ( R2I(udg_hero_INT_base[udg_X]) + ( R2I(udg_hero_INT_inc[udg_X]) * 5 ) ))
                    BlzSetUnitIntegerFieldBJ(udg_temp_unit, UNIT_IF_AGILITY, ( R2I(udg_hero_AGI_base[udg_X]) + ( R2I(udg_hero_AGI_inc[udg_X]) * 5 ) ))
                    BlzSetUnitRealFieldBJ(udg_temp_unit, UNIT_RF_STRENGTH_PER_LEVEL, udg_hero_STR_inc[udg_X])
                    BlzSetUnitRealFieldBJ(udg_temp_unit, UNIT_RF_AGILITY_PER_LEVEL, udg_hero_AGI_inc[udg_X])
                    BlzSetUnitRealFieldBJ(udg_temp_unit, UNIT_RF_INTELLIGENCE_PER_LEVEL, udg_hero_INT_inc[udg_X])
                    SetUnitMoveSpeed(udg_temp_unit, udg_hero_move_base[udg_X])
                    BlzSetUnitRealFieldBJ(udg_temp_unit, UNIT_RF_TURN_RATE, udg_hero_turnrate[udg_X])
                else:
                    BlzSetUnitIntegerFieldBJ(udg_temp_unit, UNIT_IF_STRENGTH, R2I(udg_hero_STR_base[udg_X]))
                    BlzSetUnitIntegerFieldBJ(udg_temp_unit, UNIT_IF_AGILITY, R2I(udg_hero_AGI_base[udg_X]))
                    BlzSetUnitIntegerFieldBJ(udg_temp_unit, UNIT_IF_INTELLIGENCE, R2I(udg_hero_INT_base[udg_X]))
                    BlzSetUnitRealFieldBJ(udg_temp_unit, UNIT_RF_STRENGTH_PER_LEVEL, udg_hero_STR_inc[udg_X])
                    BlzSetUnitRealFieldBJ(udg_temp_unit, UNIT_RF_AGILITY_PER_LEVEL, udg_hero_AGI_inc[udg_X])
                    BlzSetUnitRealFieldBJ(udg_temp_unit, UNIT_RF_INTELLIGENCE_PER_LEVEL, udg_hero_INT_inc[udg_X])
                    SetUnitMoveSpeed(udg_temp_unit, udg_hero_move_base[udg_X])
                    BlzSetUnitRealFieldBJ(udg_temp_unit, UNIT_RF_TURN_RATE, udg_hero_turnrate[udg_X])
            else:
                DoNothing()
            udg_X=udg_X + 1
    else:
        DoNothing()
    udg_X=udg_temp_playernumber
    udg_temp_level=1
    udg_hero_bounty_multiplier=1.00
    if ( Trig_TP_hero_Func010001() ):
        udg_hero_bounty_multiplier=0.50
    else:
        DoNothing()
    if ( Trig_TP_hero_Func011001() ):
        udg_hero_bounty_multiplier=1.50
    else:
        DoNothing()
    if ( Trig_TP_hero_Func012001() ):
        udg_hero_bounty_multiplier=1.25
    else:
        DoNothing()
    if ( Trig_TP_hero_Func013001() ):
        udg_hero_bounty_multiplier=1.10
    else:
        DoNothing()
    if ( Trig_TP_hero_Func014001() ):
        udg_hero_bounty_multiplier=1.25
    else:
        DoNothing()
    if ( Trig_TP_hero_Func015001() ):
        udg_hero_bounty_multiplier=1.00
    else:
        DoNothing()
    udg_temp_real=( I2R(udg_hero_bounty_base[udg_temp_level]) * udg_hero_bounty_multiplier )
    BlzSetUnitIntegerFieldBJ(udg_herO[udg_X], UNIT_IF_GOLD_BOUNTY_AWARDED_BASE, R2I(udg_temp_real))
    BlzSetUnitIntegerFieldBJ(udg_herO[udg_X], UNIT_IF_GOLD_BOUNTY_AWARDED_NUMBER_OF_DICE, 0)
    BlzSetUnitIntegerFieldBJ(udg_herO[udg_X], UNIT_IF_GOLD_BOUNTY_AWARDED_SIDES_PER_DIE, 0)
    if ( Trig_TP_hero_Func020C() ):
        udg_numberofSDcategories=6
    else:
        udg_numberofSDcategories=11
    RemoveLocation(udg_temp_point)
    SF_RemoveTavern(ownerId)
    SelectUnitForPlayerSingle(hero, Player(ownerId - 1))

def SF_OnSale():
    shop=GetSellingUnit()
    sold=GetSoldUnit()
    p=GetPlayerId(GetOwningPlayer(shop)) + 1
    id=GetUnitTypeId(sold)
    if p <= 12 and GetUnitTypeId(shop) == 'nFHT':
        if id == 'hPgN' or id == 'hPgP':
            RemoveUnit(sold)
            if SF_Tavern[p] != None and not SF_Picked[p]:
                if id == 'hPgN':
                    SF_Page[p]=SF_Page[p] + 1
                    if SF_Page[p] * 10 >= SF_PoolCount[p]:
                        SF_Page[p]=0
                else:
                    SF_Page[p]=SF_Page[p] - 1
                    if SF_Page[p] < 0:
                        SF_Page[p]=( SF_PoolCount[p] - 1 ) / 10
                SF_RefreshPage(p)
                SelectUnitForPlayerSingle(shop, Player(p - 1))
        elif IsUnitType(sold, UNIT_TYPE_HERO):
            SF_AcceptHero(sold)
    shop=None
    sold=None

def SF_AssignUnpicked():
    global SF_SelectionClosed
    p=1
    id=None
    hero=None
    SF_SelectionClosed=True
    while True:
        if p > 12: break
        if udg_player_active[p] and not SF_Picked[p] and udg_herO[p] == None:
            if SF_PoolCount[p] > 0:
                id=SF_Pool[p * 128 + GetRandomInt(1, SF_PoolCount[p])]
            else:
                id=udg_hero_type[1]
            hero=CreateUnit(Player(p - 1), id, SF_BaseX[p] - 192. * Cos(SF_Angle[p]), SF_BaseY[p] - 192. * Sin(SF_Angle[p]), SF_Angle[p] * bj_RADTODEG + 180.)
            SF_AcceptHero(hero)
            DisplayTimedTextToPlayer(Player(p - 1), 0., 0., 8., "Hero selection closed: you received " + GetUnitName(hero) + ".")
        SF_RemoveTavern(p)
        p=p + 1
    hero=None

def SF_StartDeadline():
    global SF_DeadlineStarted
    if not SF_DeadlineStarted:
        SF_DeadlineStarted=True
        SF_OpenTaverns()
        TimerStart(SF_Deadline, 15., False, SF_AssignUnpicked)