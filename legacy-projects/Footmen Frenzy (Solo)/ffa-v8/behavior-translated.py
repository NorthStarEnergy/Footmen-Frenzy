def SF_Initialize():
    global SF_Deadline,SF_GameClock
    p=1
    q=None
    t=CreateTrigger()
    startup=CreateTimer()
    F8_Slot[1]=0
    F8_Team[0]=1
    udg_teamnumber[1]=1
    F8_Participant[1]=udg_player_active[1]
    F8_Slot[2]=4
    F8_Team[4]=2
    udg_teamnumber[5]=2
    F8_Participant[5]=udg_player_active[5]
    F8_Slot[3]=7
    F8_Team[7]=3
    udg_teamnumber[8]=3
    F8_Participant[8]=udg_player_active[8]
    F8_Slot[4]=11
    F8_Team[11]=4
    udg_teamnumber[12]=4
    F8_Participant[12]=udg_player_active[12]
    F8_Slot[5]=1
    F8_Team[1]=5
    udg_teamnumber[2]=5
    F8_Participant[2]=udg_player_active[2]
    F8_Slot[6]=3
    F8_Team[3]=6
    udg_teamnumber[4]=6
    F8_Participant[4]=udg_player_active[4]
    F8_Slot[7]=6
    F8_Team[6]=7
    udg_teamnumber[7]=7
    F8_Participant[7]=udg_player_active[7]
    F8_Slot[8]=9
    F8_Team[9]=8
    udg_teamnumber[10]=8
    F8_Participant[10]=udg_player_active[10]
    q=1
    while True:
        if q>9: break
        if udg_team[q]!=None:
            DestroyForce(udg_team[q])
        udg_team[q]=CreateForce()
        if q<=8:
            ForceAddPlayer(udg_team[q],Player(F8_Slot[q]))
        q=q+1
    q=12
    while True:
        if q>=24: break
        ForceAddPlayer(udg_team[9],Player(q))
        udg_teamnumber[q+1]=9
        q=q+1
    SF_BaseX[10]=-3731.200
    SF_BaseY[10]=-256.000
    SF_Angle[10]=3.141592654
    SF_BaseX[12]=-2638.357
    SF_BaseY[12]=-2894.357
    SF_Angle[12]=- 2.356194490
    SF_BaseX[7]=-0.000
    SF_BaseY[7]=-3987.200
    SF_Angle[7]=- 1.570796327
    SF_BaseX[8]=2638.357
    SF_BaseY[8]=-2894.357
    SF_Angle[8]=- 0.785398163
    SF_BaseX[4]=3731.200
    SF_BaseY[4]=-256.000
    SF_Angle[4]=- 0.000000000
    SF_BaseX[5]=2638.357
    SF_BaseY[5]=2382.357
    SF_Angle[5]=0.785398163
    SF_BaseX[2]=0.000
    SF_BaseY[2]=3475.200
    SF_Angle[2]=1.570796327
    SF_BaseX[1]=-2638.357
    SF_BaseY[1]=2382.357
    SF_Angle[1]=2.356194490
    q=1
    while True:
        if q>8: break
        RemoveLocation(udg_colossal_point[q])
        udg_colossal_point[q]=Location(3080.*Cos(SF_Angle[F8_Slot[q]+1]),-256.+3080.*Sin(SF_Angle[F8_Slot[q]+1]))
        q=q+1
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
    TimerStart(CreateTimer(),1.20,False,F8_Start)
    startup=None
    t=None

def F8_RefreshShop(shop,page):
    if GetUnitTypeId(shop) == 'n00R':
        RemoveUnitFromStock(shop, 'hrdh')
        RemoveUnitFromStock(shop, 'n00Q')
        RemoveUnitFromStock(shop, 'uobs')
        RemoveUnitFromStock(shop, 'n00S')
        RemoveUnitFromStock(shop, 'h00R')
        RemoveUnitFromStock(shop, 'n005')
        RemoveUnitFromStock(shop, 'o00H')
        RemoveUnitFromStock(shop, 'o00A')
        RemoveUnitFromStock(shop, 'h000')
        RemoveUnitFromStock(shop, 'n006')
        RemoveUnitFromStock(shop, 'n00A')
        RemoveUnitFromStock(shop, 'n052')
        RemoveUnitFromStock(shop, 'o00K')
        RemoveUnitFromStock(shop, 'n011')
        RemoveUnitFromStock(shop, 'n00T')
        RemoveUnitFromStock(shop, 'n033')
        RemoveUnitFromStock(shop, 'h03B')
        RemoveUnitFromStock(shop, 'nws1')
        RemoveUnitFromStock(shop, 'n001')
        RemoveUnitFromStock(shop, 'ushd')
        RemoveUnitFromStock(shop, 'n03M')
        RemoveUnitFromStock(shop, 'h02U')
        if page == 0:
            AddUnitToStock(shop, 'hrdh', 1, 1)
            AddUnitToStock(shop, 'n00Q', 1, 1)
            AddUnitToStock(shop, 'uobs', 1, 1)
            AddUnitToStock(shop, 'n00S', 1, 1)
            AddUnitToStock(shop, 'h00R', 1, 1)
            AddUnitToStock(shop, 'n005', 1, 1)
            AddUnitToStock(shop, 'o00H', 1, 1)
            AddUnitToStock(shop, 'o00A', 1, 1)
            AddUnitToStock(shop, 'h000', 1, 1)
            AddUnitToStock(shop, 'n006', 1, 1)
            AddUnitToStock(shop, 'n00A', 1, 1)
        elif page == 1:
            AddUnitToStock(shop, 'n052', 1, 1)
            AddUnitToStock(shop, 'o00K', 1, 1)
            AddUnitToStock(shop, 'n011', 1, 1)
            AddUnitToStock(shop, 'n00T', 1, 1)
            AddUnitToStock(shop, 'n033', 1, 1)
            AddUnitToStock(shop, 'h03B', 1, 1)
            AddUnitToStock(shop, 'nws1', 1, 1)
            AddUnitToStock(shop, 'n001', 1, 1)
            AddUnitToStock(shop, 'ushd', 1, 1)
            AddUnitToStock(shop, 'n03M', 1, 1)
        AddUnitToStock(shop, 'h02U', 1, 1)
    elif GetUnitTypeId(shop) == 'n01Y':
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
        RemoveUnitFromStock(shop, 'h037')
        if page == 0:
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
        elif page == 1:
            AddItemToStock(shop, 'I015', 1, 1)
            AddItemToStock(shop, 'I04B', 1, 1)
            AddItemToStock(shop, 'I00S', 1, 1)
            AddItemToStock(shop, 'I00K', 1, 1)
            AddItemToStock(shop, 'I01I', 1, 1)
            AddItemToStock(shop, 'I01S', 1, 1)
        AddUnitToStock(shop, 'h037', 1, 1)
    SaveInteger(F8_Shops, GetHandleId(shop), 0, page)

def F8_ShopSale():
    shop=GetSellingUnit()
    sold=GetSoldUnit()
    pages=0
    page=None
    if GetUnitTypeId(shop)=='n00R' and GetUnitTypeId(sold)=='h02U':
        pages=2
    elif GetUnitTypeId(shop)=='n01Y' and GetUnitTypeId(sold)=='h037':
        pages=2
    if pages>0:
        page=ModuloInteger(LoadInteger(F8_Shops,GetHandleId(shop),0)+1,pages)
        F8_RefreshShop(shop,page)
        SelectUnitForPlayerSingle(shop,GetOwningPlayer(sold))
        RemoveUnit(sold)
    shop=None
    sold=None

def F8_UpdateBoard():
    row=1
    p=None
    while True:
        if row>8: break
        p=F8_Slot[row]+1
        MultiboardSetItemValueBJ(udg_multiboard_kills,1,row+1,GetPlayerName(Player(p-1)))
        MultiboardSetItemValueBJ(udg_multiboard_kills,2,row+1,I2S(udg_hero_kills[p])+"/"+I2S(udg_hero_deaths[p]))
        MultiboardSetItemValueBJ(udg_multiboard_kills,3,row+1,I2S(udg_unit_kills[p])+"/"+I2S(udg_unit_deaths[p]))
        MultiboardSetItemValueBJ(udg_multiboard_kills,4,row+1,I2S(udg_base_kills[p]))
        MultiboardSetItemValueBJ(udg_multiboard_kills,5,row+1,I2S(udg_KOTH_Team_Gold_Earned_Total[row]))
        row=row+1

def F8_InitVision():
    p=0
    vision=None
    FogEnable(True)
    FogMaskEnable(True)
    while True:
        if p>=24: break
        if p>=12:
            vision=CreateFogModifierRect(Player(p),FOG_OF_WAR_VISIBLE,GetPlayableMapRect(),False,False)
            FogModifierStart(vision)
        elif F8_Team[p]>0:
            vision=CreateFogModifierRadius(Player(p),FOG_OF_WAR_VISIBLE,0.,-256.,2220.,False,False)
            FogModifierStart(vision)
            vision=CreateFogModifierRadius(Player(p),FOG_OF_WAR_VISIBLE,SF_BaseX[p+1],SF_BaseY[p+1],1150.,False,False)
            FogModifierStart(vision)
        p=p+1
    F8_VisionTick()
    TimerStart(CreateTimer(),1.,True,F8_VisionTick)
    vision=None

def F8_VisionTick():
    global F8_Day,F8_VisionReady
    p=0
    k=None
    slot=None
    a=None
    extent=None
    hour=GetFloatGameState(GAME_STATE_TIME_OF_DAY)
    day=hour>=6. and hour<18.
    if F8_VisionReady and day==F8_Day:
        return
    F8_Day=day
    F8_VisionReady=True
    while True:
        if p>=24: break
        if F8_Team[p]>0:
            k=1
            while True:
                if k>8: break
                slot=F8_Slot[k]
                if slot!=p:
                    if F8_Entrance[p*8+k]!=None:
                        FogModifierStop(F8_Entrance[p*8+k])
                        DestroyFogModifier(F8_Entrance[p*8+k])
                    a=SF_Angle[slot+1]
                    if day:
                        extent=450.
                    else:
                        extent=160.
                    F8_Entrance[p*8+k]=CreateFogModifierRadius(Player(p),FOG_OF_WAR_VISIBLE,2320.*Cos(a),-256.+2320.*Sin(a),extent,False,False)
                    FogModifierStart(F8_Entrance[p*8+k])
                k=k+1
        p=p+1

def Trig_Multiboard_Update_Actions():
    victim=GetTriggerUnit()
    killer=GetKillingUnit()
    d=GetPlayerId(GetOwningPlayer(victim))+1
    k=GetPlayerId(GetOwningPlayer(killer))+1
    valid=killer!=None and k<=12 and F8_Participant[k] and IsUnitEnemy(victim,Player(k-1))
    if d<=12 and F8_Participant[d]:
        if IsUnitType(victim,UNIT_TYPE_HERO):
            udg_hero_deaths[d]=udg_hero_deaths[d]+1
            udg_hero_killstreak[d]=0
            if valid:
                udg_hero_kills[k]=udg_hero_kills[k]+1
                udg_hero_killstreak[k]=udg_hero_killstreak[k]+1
        elif victim==udg_base[d]:
            if valid:
                udg_base_kills[k]=udg_base_kills[k]+1
        elif not IsUnitType(victim,UNIT_TYPE_STRUCTURE):
            udg_unit_deaths[d]=udg_unit_deaths[d]+1
            if valid:
                udg_unit_kills[k]=udg_unit_kills[k]+1
    F8_UpdateBoard()
    victim=None
    killer=None

def Trig_KD_Actions():
    row=1
    p=None
    while True:
        if row>8: break
        p=F8_Slot[row]+1
        if F8_Participant[p]:
            DisplayTimedTextToPlayer(GetTriggerPlayer(),0.,0.,20.,GetPlayerName(Player(p-1))+" - Hero K/D: "+I2S(udg_hero_kills[p])+"/"+I2S(udg_hero_deaths[p])+" - Unit K/D: "+I2S(udg_unit_kills[p])+"/"+I2S(udg_unit_deaths[p]))
        row=row+1

def Trig_colossal_stats_Actions():
    udg_colossal_unit_type[1]='n04I'
    udg_colossal_unit_hp_base[1]=500
    udg_colossal_unit_mp_base[1]=400
    udg_colossal_unit_armor_type[1]=2
    udg_colossal_unit_armor[1]=3
    udg_colossal_unit_dmg_base[1]=30
    udg_colossal_unit_bounty_base[1]=20
    udg_colossal_unit_level[1]=3
    udg_colossal_unit_type[2]='n04B'
    udg_colossal_unit_hp_base[2]=500
    udg_colossal_unit_mp_base[2]=0
    udg_colossal_unit_armor_type[2]=2
    udg_colossal_unit_armor[2]=2
    udg_colossal_unit_dmg_base[2]=35
    udg_colossal_unit_bounty_base[2]=20
    udg_colossal_unit_level[2]=3
    udg_colossal_unit_type[3]='n04O'
    udg_colossal_unit_hp_base[3]=600
    udg_colossal_unit_mp_base[3]=0
    udg_colossal_unit_armor_type[3]=2
    udg_colossal_unit_armor[3]=3
    udg_colossal_unit_dmg_base[3]=35
    udg_colossal_unit_bounty_base[3]=20
    udg_colossal_unit_level[3]=3
    udg_colossal_unit_type[4]='n04L'
    udg_colossal_unit_hp_base[4]=600
    udg_colossal_unit_mp_base[4]=0
    udg_colossal_unit_armor_type[4]=2
    udg_colossal_unit_armor[4]=2
    udg_colossal_unit_dmg_base[4]=43
    udg_colossal_unit_bounty_base[4]=20
    udg_colossal_unit_level[4]=3
    udg_colossal_unit_type[5]='o012'
    udg_colossal_unit_hp_base[5]=1500
    udg_colossal_unit_mp_base[5]=0
    udg_colossal_unit_armor_type[5]=2
    udg_colossal_unit_armor[5]=5
    udg_colossal_unit_dmg_base[5]=35
    udg_colossal_unit_bounty_base[5]=20
    udg_colossal_unit_level[5]=3
    udg_colossal_unit_type[11]='n03I'
    udg_colossal_unit_hp_base[11]=1400
    udg_colossal_unit_mp_base[11]=0
    udg_colossal_unit_armor_type[11]=2
    udg_colossal_unit_armor[11]=4
    udg_colossal_unit_dmg_base[11]=50
    udg_colossal_unit_bounty_base[11]=45
    udg_colossal_unit_level[11]=8
    udg_colossal_unit_type[12]='n04D'
    udg_colossal_unit_hp_base[12]=1000
    udg_colossal_unit_mp_base[12]=300
    udg_colossal_unit_armor_type[12]=2
    udg_colossal_unit_armor[12]=2
    udg_colossal_unit_dmg_base[12]=47
    udg_colossal_unit_bounty_base[12]=32
    udg_colossal_unit_level[12]=3
    udg_colossal_unit_type[13]='n04M'
    udg_colossal_unit_hp_base[13]=900
    udg_colossal_unit_mp_base[13]=300
    udg_colossal_unit_armor_type[13]=2
    udg_colossal_unit_armor[13]=3
    udg_colossal_unit_dmg_base[13]=50
    udg_colossal_unit_bounty_base[13]=32
    udg_colossal_unit_level[13]=3
    udg_colossal_unit_type[14]='n04N'
    udg_colossal_unit_hp_base[14]=900
    udg_colossal_unit_mp_base[14]=0
    udg_colossal_unit_armor_type[14]=2
    udg_colossal_unit_armor[14]=3
    udg_colossal_unit_dmg_base[14]=48
    udg_colossal_unit_bounty_base[14]=32
    udg_colossal_unit_level[14]=2
    udg_colossal_unit_type[15]='n04N'
    udg_colossal_unit_hp_base[15]=900
    udg_colossal_unit_mp_base[15]=0
    udg_colossal_unit_armor_type[15]=2
    udg_colossal_unit_armor[15]=3
    udg_colossal_unit_dmg_base[15]=48
    udg_colossal_unit_bounty_base[15]=32
    udg_colossal_unit_level[15]=3
    udg_colossal_unit_type[21]='n04G'
    udg_colossal_unit_hp_base[21]=800
    udg_colossal_unit_mp_base[21]=0
    udg_colossal_unit_armor_type[21]=2
    udg_colossal_unit_armor[21]=2
    udg_colossal_unit_dmg_base[21]=50
    udg_colossal_unit_bounty_base[21]=45
    udg_colossal_unit_level[21]=7
    udg_colossal_unit_type[22]='n050'
    udg_colossal_unit_hp_base[22]=700
    udg_colossal_unit_mp_base[22]=600
    udg_colossal_unit_armor_type[22]=2
    udg_colossal_unit_armor[22]=3
    udg_colossal_unit_dmg_base[22]=35
    udg_colossal_unit_bounty_base[22]=32
    udg_colossal_unit_level[22]=3
    udg_colossal_unit_type[23]='n051'
    udg_colossal_unit_hp_base[23]=750
    udg_colossal_unit_mp_base[23]=600
    udg_colossal_unit_armor_type[23]=2
    udg_colossal_unit_armor[23]=3
    udg_colossal_unit_dmg_base[23]=35
    udg_colossal_unit_bounty_base[23]=32
    udg_colossal_unit_level[23]=3
    udg_colossal_unit_type[24]='n04Z'
    udg_colossal_unit_hp_base[24]=750
    udg_colossal_unit_mp_base[24]=600
    udg_colossal_unit_armor_type[24]=2
    udg_colossal_unit_armor[24]=3
    udg_colossal_unit_dmg_base[24]=35
    udg_colossal_unit_bounty_base[24]=32
    udg_colossal_unit_level[24]=3
    udg_colossal_unit_type[25]='e014'
    udg_colossal_unit_hp_base[25]=1500
    udg_colossal_unit_mp_base[25]=0
    udg_colossal_unit_armor_type[25]=2
    udg_colossal_unit_armor[25]=3
    udg_colossal_unit_dmg_base[25]=75
    udg_colossal_unit_bounty_base[25]=40
    udg_colossal_unit_level[25]=5
    udg_colossal_unit_type[31]='o00Z'
    udg_colossal_unit_hp_base[31]=750
    udg_colossal_unit_mp_base[31]=0
    udg_colossal_unit_armor_type[31]=2
    udg_colossal_unit_armor[31]=1
    udg_colossal_unit_dmg_base[31]=50
    udg_colossal_unit_bounty_base[31]=40
    udg_colossal_unit_level[31]=3
    udg_colossal_unit_type[32]='n04J'
    udg_colossal_unit_hp_base[32]=900
    udg_colossal_unit_mp_base[32]=0
    udg_unit_armor_type[32]=2
    udg_colossal_unit_armor[32]=3
    udg_colossal_unit_dmg_base[32]=50
    udg_colossal_unit_bounty_base[32]=35
    udg_colossal_unit_level[32]=3
    udg_colossal_unit_type[33]='u00M'
    udg_colossal_unit_hp_base[33]=800
    udg_colossal_unit_mp_base[33]=0
    udg_colossal_unit_armor_type[33]=2
    udg_colossal_unit_armor[33]=2
    udg_colossal_unit_dmg_base[33]=50
    udg_colossal_unit_bounty_base[33]=32
    udg_colossal_unit_level[33]=3
    udg_colossal_unit_type[34]='e015'
    udg_colossal_unit_hp_base[34]=900
    udg_colossal_unit_mp_base[34]=0
    udg_colossal_unit_armor_type[34]=2
    udg_colossal_unit_armor[34]=1
    udg_colossal_unit_dmg_base[34]=50
    udg_colossal_unit_bounty_base[34]=32
    udg_colossal_unit_level[34]=3
    udg_colossal_unit_type[35]='n04Y'
    udg_colossal_unit_hp_base[35]=700
    udg_colossal_unit_mp_base[35]=300
    udg_colossal_unit_armor_type[35]=7
    udg_colossal_unit_armor[35]=1
    udg_colossal_unit_dmg_base[35]=25
    udg_colossal_unit_bounty_base[35]=32
    udg_colossal_unit_level[35]=3
    udg_colossal_unit_type[41]='n047'
    udg_colossal_unit_hp_base[41]=1500
    udg_colossal_unit_mp_base[41]=500
    udg_colossal_unit_armor_type[41]=3
    udg_colossal_unit_armor[41]=5
    udg_colossal_unit_dmg_base[41]=75
    udg_colossal_unit_bounty_base[41]=75
    udg_colossal_unit_level[41]=8
    udg_colossal_unit_type[51]='n04F'
    udg_colossal_unit_hp_base[51]=1600
    udg_colossal_unit_mp_base[51]=0
    udg_colossal_unit_armor_type[51]=3
    udg_colossal_unit_armor[51]=4
    udg_colossal_unit_dmg_base[51]=75
    udg_colossal_unit_bounty_base[51]=70
    udg_colossal_unit_level[51]=7
    udg_colossal_unit_type[61]='n048'
    udg_colossal_unit_hp_base[61]=1200
    udg_colossal_unit_mp_base[61]=0
    udg_colossal_unit_armor_type[61]=2
    udg_colossal_unit_armor[61]=4
    udg_colossal_unit_dmg_base[61]=70
    udg_colossal_unit_bounty_base[61]=75
    udg_colossal_unit_level[61]=5
    udg_colossal_unit_type[101]='n04E'
    udg_colossal_unit_hp_base[101]=2500
    udg_colossal_unit_mp_base[101]=2000
    udg_colossal_unit_armor_type[101]=3
    udg_colossal_unit_armor[101]=6
    udg_colossal_unit_dmg_base[101]=125
    udg_colossal_unit_bounty_base[101]=85
    udg_colossal_unit_level[101]=9
    udg_colossal_unit_type[102]='n04C'
    udg_colossal_unit_hp_base[102]=2500
    udg_colossal_unit_mp_base[102]=2000
    udg_colossal_unit_armor_type[102]=3
    udg_colossal_unit_armor[102]=6
    udg_colossal_unit_dmg_base[102]=130
    udg_colossal_unit_bounty_base[102]=85
    udg_colossal_unit_level[102]=9
    udg_colossal_unit_id[1]=101
    udg_colossal_unit_id[2]=102
    udg_colossal_unit_id[3]=1
    udg_colossal_unit_id[4]=2
    udg_colossal_unit_id[5]=3
    udg_colossal_unit_id[6]=4
    udg_colossal_unit_id[7]=5
    udg_colossal_unit_id[8]=11
    udg_colossal_unit_id[9]=12
    udg_colossal_unit_id[10]=13
    udg_colossal_unit_id[11]=14
    udg_colossal_unit_id[12]=15
    udg_colossal_unit_id[13]=21
    udg_colossal_unit_id[14]=22
    udg_colossal_unit_id[15]=23
    udg_colossal_unit_id[16]=24
    udg_colossal_unit_id[17]=25
    udg_colossal_unit_id[18]=31
    udg_colossal_unit_id[19]=32
    udg_colossal_unit_id[20]=33
    udg_colossal_unit_id[21]=34
    udg_colossal_unit_id[22]=35
    udg_colossal_unit_id[23]=41
    udg_colossal_unit_id[24]=51
    udg_colossal_unit_id[25]=61
    udg_colossal_number_of_units[1]=1
    udg_colossal_number_of_units[2]=1
    udg_colossal_number_of_units[3]=5
    udg_colossal_number_of_units[4]=5
    udg_colossal_number_of_units[5]=5
    udg_colossal_number_of_units[6]=5
    udg_colossal_number_of_units[7]=5
    udg_colossal_number_of_units[8]=1
    udg_colossal_number_of_units[9]=1
    udg_colossal_number_of_units[10]=1
    udg_colossal_number_of_units[11]=1
    udg_colossal_number_of_units[12]=1
    udg_colossal_number_of_units[13]=1
    udg_colossal_number_of_units[14]=1
    udg_colossal_number_of_units[15]=1
    udg_colossal_number_of_units[16]=1
    udg_colossal_number_of_units[17]=1
    udg_colossal_number_of_units[18]=1
    udg_colossal_number_of_units[19]=1
    udg_colossal_number_of_units[20]=1
    udg_colossal_number_of_units[21]=1
    udg_colossal_number_of_units[22]=1
    udg_colossal_number_of_units[23]=1
    udg_colossal_number_of_units[24]=1
    udg_colossal_number_of_units[25]=1
    udg_colossal_min_wave[1]=0
    udg_colossal_min_wave[2]=0
    udg_colossal_min_wave[3]=0
    udg_colossal_min_wave[4]=0
    udg_colossal_min_wave[5]=0
    udg_colossal_min_wave[6]=0
    udg_colossal_min_wave[7]=0
    udg_colossal_min_wave[8]=0
    udg_colossal_min_wave[9]=0
    udg_colossal_min_wave[10]=0
    udg_colossal_min_wave[11]=0
    udg_colossal_min_wave[12]=0
    udg_colossal_min_wave[13]=0
    udg_colossal_min_wave[14]=0
    udg_colossal_min_wave[15]=0
    udg_colossal_min_wave[16]=0
    udg_colossal_min_wave[17]=0
    udg_colossal_min_wave[18]=0
    udg_colossal_min_wave[19]=0
    udg_colossal_min_wave[20]=0
    udg_colossal_min_wave[21]=0
    udg_colossal_min_wave[22]=0
    udg_colossal_min_wave[23]=2
    udg_colossal_min_wave[24]=3
    udg_colossal_min_wave[25]=4

def Trig_colossal_spawn_Actions():
    global udg_colossal_wave,udg_colossal_wave_id,udg_timer_window_colossal
    k=0
    p=None
    entry=None
    n=None
    offset=None
    camp=None
    big=1
    a=None
    x=None
    y=None
    DestroyTimerDialogBJ(udg_timer_window_colossal)
    if ModuloInteger(udg_colossal_wave,2)==0:
        big=2
    while True:
        if k>=4: break
        a=I2R(k)*bj_PI/2.+bj_PI/4.
        F8_SpawnColo(big,480.*Cos(a),-256.+480.*Sin(a))
        k=k+1
    k=1
    while True:
        if k>8: break
        p=F8_Slot[k]+1
        if udg_player_active[p]:
            a=SF_Angle[p]
            entry=3
            offset=0
            camp=0
            while True:
                if entry>22: break
                if ModuloInteger(udg_colossal_unit_id[entry]-udg_colossal_wave_id,10)==0 and udg_colossal_wave>=udg_colossal_min_wave[entry]:
                    n=0
                    while True:
                        if n>=udg_colossal_number_of_units[entry]: break
                        x=(3080.+I2R(offset//3)*112.)*Cos(a)-I2R(ModuloInteger(offset,3)-1)*112.*Sin(a)
                        y=-256.+(3080.+I2R(offset//3)*112.)*Sin(a)+I2R(ModuloInteger(offset,3)-1)*112.*Cos(a)
                        F8_SpawnColo(entry,x,y)
                        offset=offset+1
                        n=n+1
                    F8_SpawnColo(entry,2580.*Cos(a)-I2R(camp)*160.*Sin(a),-256.+2580.*Sin(a)+I2R(camp)*160.*Cos(a))
                    camp=camp+1
                entry=entry+1
        k=k+1
    if ( Trig_colossal_spawn_Func028C() ):
        udg_colossal_wave=( udg_colossal_wave + 1 )
        udg_colossal_wave_id=( udg_colossal_wave_id + 1 )
        if ( Trig_colossal_spawn_Func028Func005C() ):
            udg_colossal_wave_id=1
        else:
            DoNothing()
        StartTimerBJ(udg_timer_colossal, False, udg_t_colossal_reoccuring)
        CreateTimerDialogBJ(udg_timer_colossal, ( "Colossal Wave #" + ( I2S(udg_colossal_wave) + ( " / " + I2S(udg_colossal_max_wave) ) ) ))
        udg_timer_window_colossal=GetLastCreatedTimerDialogBJ()
        TimerDialogDisplayBJ(True, udg_timer_window_colossal)
    else:
        DoNothing()

def SoloFootsAltarStockAddPage(altar,page):
    altarKey=GetHandleId(altar)
    slot=1
    heroIndex=None
    if SF_HeroCount[GetPlayerId(GetOwningPlayer(altar)) + 1] >= 2:
        return
    while True:
        if slot > 11: break
        heroIndex=LoadInteger(GST_Hash, altarKey, ( page * 100 ) + slot)
        if heroIndex != 0:
            SetPlayerUnitAvailableBJ(udg_hero_type[heroIndex], True, GetOwningPlayer(altar))
            AddUnitToStockBJ(udg_hero_type[heroIndex], altar, 1, 1)
        slot=slot + 1
    if page == 1:
        AddUnitToStockBJ('hPgN', altar, 1, 1)
    else:
        AddUnitToStockBJ('hPgN', altar, 1, 1)