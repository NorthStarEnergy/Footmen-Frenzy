def F8_UpdateBoard():
    row=1
    p=None
    if SKEnabled:
        SKBoard()
        return
    while True:
        if row>8: break
        p=F8_Slot[row]+1
        MultiboardSetItemValueBJ(udg_multiboard_kills,1,row+1,GetPlayerName(Player(p-1)))
        MultiboardSetItemValueBJ(udg_multiboard_kills,2,row+1,I2S(udg_hero_kills[p])+"/"+I2S(udg_hero_deaths[p]))
        MultiboardSetItemValueBJ(udg_multiboard_kills,3,row+1,I2S(udg_unit_kills[p])+"/"+I2S(udg_unit_deaths[p]))
        MultiboardSetItemValueBJ(udg_multiboard_kills,4,row+1,I2S(udg_base_kills[p]))
        MultiboardSetItemValueBJ(udg_multiboard_kills,5,row+1,I2S(udg_KOTH_Team_Gold_Earned_Total[row]))
        row=row+1

def S8Player(row):
    return F8_Slot[row]+1

def S8Team(pn):
    if pn<1 or pn>12:
        return 9
    if F8_Team[pn-1]==0:
        return 9
    return F8_Team[pn-1]

def SF_Initialize():
    global SF_Deadline,SF_GameClock
    p=1
    q=None
    t=CreateTrigger()
    startup=CreateTimer()
    F8_InitShops()
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
    SF_TavernX[1]=-2489.016
    SF_TavernY[1]=3454.896
    SF_TavernX[5]=3710.896
    SF_TavernY[5]=2233.016
    SF_TavernX[8]=2489.016
    SF_TavernY[8]=-3966.896
    SF_TavernX[12]=-3710.896
    SF_TavernY[12]=-2745.016
    SF_TavernX[2]=864.000
    SF_TavernY[2]=4128.000
    SF_TavernX[4]=4384.000
    SF_TavernY[4]=-1120.000
    SF_TavernX[7]=-864.000
    SF_TavernY[7]=-4640.000
    SF_TavernX[10]=-4384.000
    SF_TavernY[10]=608.000
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
    TimerStart(startup, 1.10, False, SKOpenMode)
    startup=None
    t=None

def SF_RevealEliminated(pn):
    if pn<1 or pn>12:
        return
    if udg_player_active[pn] or F8_Team[pn-1]==0:
        return
    if SF_EliminatedVision[pn]==None:
        SF_EliminatedVision[pn]=CreateFogModifierRect(Player(pn-1),FOG_OF_WAR_VISIBLE,GetPlayableMapRect(),False,False)
        FogModifierStart(SF_EliminatedVision[pn])

def SKActive(pn):
    if pn<1 or pn>12:
        return False
    return F8_Team[pn-1]>0 and udg_player_active[pn]

def SKBoard():
    i=1
    pn=None
    king=None
    status=None
    if udg_multiboard_kills == None:
        return
    MultiboardSetTitleText(udg_multiboard_kills, "King Mode - Kingdom totals")
    while True:
        if i > 8: break
        pn=S8Player(i)
        king=SKKing[pn]
        if SKActive(pn):
            status="King"
            if king!=pn:
                status="Vassal: ready"
            if SKDefected[pn]:
                status="Used"
            MultiboardSetItemValueBJ(udg_multiboard_kills, 2, i+1, GetPlayerName(Player(king-1)))
            MultiboardSetItemValueBJ(udg_multiboard_kills, 3, i+1, I2S(SKTroopKills[king]))
            MultiboardSetItemValueBJ(udg_multiboard_kills, 4, i+1, I2S(SKHeroKills[king]))
            MultiboardSetItemValueBJ(udg_multiboard_kills, 5, i+1, I2S(SKCaptures[king]))
        else:
            status="Left"
            MultiboardSetItemValueBJ(udg_multiboard_kills,3,i+1,"-")
            MultiboardSetItemValueBJ(udg_multiboard_kills,4,i+1,"-")
            MultiboardSetItemValueBJ(udg_multiboard_kills,5,i+1,"-")
            MultiboardSetItemValueBJ(udg_multiboard_kills, 2, i+1, "-")
        MultiboardSetItemValueBJ(udg_multiboard_kills, 1, i+1, GetPlayerName(Player(pn-1)))
        MultiboardSetItemValueBJ(udg_multiboard_kills, 6, i+1, status)
        MultiboardSetItemValueBJ(udg_multiboard_kills,7,i+1,I2S(udg_KOTH_Team_Gold_Earned_Total[S8Team(king)]))
        i=i+1

def SKCapture(victim,attacker):
    oldKing=SKKing[victim]
    newKing=SKKing[attacker]
    i=1
    if not SKActive(victim) or not SKActive(attacker) or oldKing == newKing or SoloFoots_EndGameStarted:
        return
    if victim == oldKing:
        while True:
            if i > 8: break
            if SKActive(S8Player(i)) and SKKing[S8Player(i)] == oldKing:
                SKKing[S8Player(i)]=newKing
            i=i+1
        SKMergeScore(oldKing, newKing)
    else:
        SKKing[victim]=newKing
    SKCaptures[newKing]=SKCaptures[newKing]+1
    SKSync()
    DisplayTextToForce(udg_all_players, "King Mode: " + GetPlayerName(Player(attacker-1)) + " captured " + GetPlayerName(Player(victim-1)) + " for King " + GetPlayerName(Player(newKing-1)) + ".")
    DisplayTextToPlayer(Player(victim-1), 0.0, 0.0, "Your base will rebuild in 3 seconds. Keep playing for your kingdom. Use -defect once to become independent.")
    SKCheckVictory()
    SKBoard()

def SKCheckVictory():
    global SKPendingKing,SKWinAt,SKWinner,SoloFoots_EndGameStarted
    king=None
    i=1
    pn=None
    if not SKReady or SoloFoots_EndGameStarted or SKInitialPlayers < 2:
        return
    SKNormalize()
    king=SKUnifiedKing()
    if king == 0:
        if SKPendingKing != 0:
            DisplayTextToForce(udg_all_players, "King Mode: the takeover has been broken. The battle continues!")
        SKPendingKing=0
        SKWinAt=0
    elif SKPendingKing != king:
        SKPendingKing=king
        SKWinAt=SKClock+20
        DisplayTextToForce(udg_all_players, "King Mode: " + GetPlayerName(Player(king-1)) + " controls every active player. Victory in 20 seconds unless someone uses -defect!")
    elif SKClock >= SKWinAt:
        SKWinner=king
        SoloFoots_EndGameStarted=True
        DisplayTextToForce(udg_all_players, "King Mode: " + GetPlayerName(Player(king-1)) + " has conquered the map! Their kingdom wins!")
        while True:
            if i > 8: break
            pn=S8Player(i)
            if SKActive(pn) and SKKing[pn] == king:
                CustomVictoryBJ(Player(pn-1), True, True)
            i=i+1

def SKChooseMode(kingMode):
    global SKEnabled,SKModeChosen
    if SKModeChosen:
        return
    SKModeChosen=True
    PauseTimer(SKModeTimeout)
    if SKModeHost!=None:
        DialogDisplay(SKModeHost,SKModeDialog,False)
    SKEnabled=kingMode
    TimerStart(SF_GameClock,86400.,False,None)
    if kingMode:
        SKInit()
    else:
        DisplayTextToForce(udg_all_players,"Normal FFA selected. Each player fights independently.")
    TimerStart(CreateTimer(),.01,False,SF_StartBaseSelection)

def SKClearAttack():
    u=GetEnumUnit()
    pn=GetPlayerId(GetOwningPlayer(u))+1
    if GetUnitCurrentOrder(u) == OrderId("attack") or GetUnitCurrentOrder(u) == OrderId("attackground"):
        IssueImmediateOrder(u, "stop")
        if not IsUnitType(u, UNIT_TYPE_HERO) and not IsUnitType(u, UNIT_TYPE_STRUCTURE) and udg_autosend[pn]:
            IssuePointOrder(u, "attack", 0.0, -256.0)
    u=None

def SKCommand():
    pn=GetPlayerId(GetTriggerPlayer())+1
    king=None
    if GetEventPlayerChatString() == "-defect":
        SKDefect(pn)
    elif SKActive(pn):
        king=SKKing[pn]
        DisplayTextToPlayer(Player(pn-1), 0.0, 0.0, "King Mode | King: " + GetPlayerName(Player(king-1)) + " | Kingdom unit kills: " + I2S(SKTroopKills[king]) + " | Hero kills: " + I2S(SKHeroKills[king]) + " | Captures: " + I2S(SKCaptures[king]) + ". Use -defect once while captured.")

def SKCreateBoard():
    global udg_multiboard_kills
    row=1
    col=None
    if udg_multiboard_kills!=None:
        DestroyMultiboard(udg_multiboard_kills)
    CreateMultiboardBJ(7, 9, "King Mode")
    udg_multiboard_kills=GetLastCreatedMultiboard()
    MultiboardSetItemValueBJ(udg_multiboard_kills, 1, 1, "Player")
    MultiboardSetItemValueBJ(udg_multiboard_kills, 2, 1, "King")
    MultiboardSetItemValueBJ(udg_multiboard_kills, 3, 1, "Units")
    MultiboardSetItemValueBJ(udg_multiboard_kills, 4, 1, "Heroes")
    MultiboardSetItemValueBJ(udg_multiboard_kills, 5, 1, "Captures")
    MultiboardSetItemValueBJ(udg_multiboard_kills, 6, 1, "Defect")
    while True:
        if row > 9: break
        col=1
        while True:
            if col > 7: break
            MultiboardSetItemStyleBJ(udg_multiboard_kills, col, row, True, False)
            MultiboardSetItemWidthBJ(udg_multiboard_kills, col, row, 4.0)
            if col <= 2:
                MultiboardSetItemWidthBJ(udg_multiboard_kills, col, row, 10.0)
            col=col+1
        row=row+1
    MultiboardSetItemValueBJ(udg_multiboard_kills,7,1,"Hill gold")
    SKBoard()
    MultiboardDisplay(udg_multiboard_kills,True)

def SKCreditKill():
    pn=GetPlayerId(GetOwningPlayer(GetKillingUnit()))+1
    dead=GetDyingUnit()
    if SKReady and not SoloFoots_EndGameStarted and SKActive(pn) and GetKillingUnit() != None and not IsUnitIllusion(dead) and GetUnitAbilityLevel(dead, 'Aloc')==0 and IsUnitEnemy(dead, Player(pn-1)):
        if IsUnitType(dead, UNIT_TYPE_HERO):
            SKHeroKills[SKKing[pn]]=SKHeroKills[SKKing[pn]]+1
        elif not IsUnitType(dead, UNIT_TYPE_STRUCTURE):
            SKTroopKills[SKKing[pn]]=SKTroopKills[SKKing[pn]]+1
    dead=None

def SKDefect(pn):
    if not SKReady or not SKActive(pn) or SoloFoots_EndGameStarted:
        return
    if SKKing[pn] == pn:
        DisplayTextToPlayer(Player(pn-1), 0.0, 0.0, "You are already an independent king. Your defection has not been used.")
        return
    if SKDefected[pn]:
        DisplayTextToPlayer(Player(pn-1), 0.0, 0.0, "You have already used your one defection this game.")
        return
    SKDefected[pn]=True
    SKKing[pn]=pn
    SKProtectUntil[pn]=SKClock+10
    if udg_base[pn] != None:
        SetUnitInvulnerable(udg_base[pn], True)
    SKSync()
    DisplayTextToForce(udg_all_players, "King Mode: " + GetPlayerName(Player(pn-1)) + " has defected and is independent! Their base has 10 seconds of protection.")
    SKCheckVictory()
    SKBoard()

def SKHillIncome():
    global udg_KOTH_Gold_Remaining,udg_KOTH_Team,udg_KOTH_Team_Number
    owner=GetPlayerId(udg_KOTH_Player)+1
    king=None
    row=1
    pn=None
    count=0
    payout=None
    each=None
    remainder=None
    if not SKActive(owner):
        TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
        return
    king=SKKing[owner]
    while True:
        if row>8: break
        pn=S8Player(row)
        if SKActive(pn) and SKKing[pn]==king:
            count=count+1
        row=row+1
    if count==0:
        PauseTimer(udg_KOTH_Income_Timer)
        return
    payout=IMinBJ(udg_KOTH_Gold_Rewarded,udg_KOTH_Gold_Remaining)
    each=payout//count
    remainder=ModuloInteger(payout,count)
    row=1
    while True:
        if row>8: break
        pn=S8Player(row)
        if SKActive(pn) and SKKing[pn]==king:
            AdjustPlayerStateBJ(each,Player(pn-1),PLAYER_STATE_RESOURCE_GOLD)
        row=row+1
    AdjustPlayerStateBJ(remainder,Player(king-1),PLAYER_STATE_RESOURCE_GOLD)
    udg_KOTH_Team_Number=S8Team(king)
    udg_KOTH_Team=udg_team[udg_KOTH_Team_Number]
    udg_KOTH_Gold_Remaining=udg_KOTH_Gold_Remaining-payout
    udg_KOTH_Team_Gold_Earned_Reset[udg_KOTH_Team_Number]=udg_KOTH_Team_Gold_Earned_Reset[udg_KOTH_Team_Number]+payout
    udg_KOTH_Team_Gold_Earned_Total[udg_KOTH_Team_Number]=udg_KOTH_Team_Gold_Earned_Total[udg_KOTH_Team_Number]+payout
    if udg_KOTH_Gold_Remaining<=0:
        TriggerExecute(gg_trg_KOTH_Gold_Depleted)
    elif udg_KOTH_Team_Gold_Earned_Reset[udg_KOTH_Team_Number]>=udg_KOTH_Gold_Reset_Amount:
        udg_KOTH_Team_Gold_Earned_Reset[udg_KOTH_Team_Number]=0
        TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
        TriggerExecute(gg_trg_KOTH_Reset_Hill)
    TriggerExecute(gg_trg_KOTH_Update_Text)
    SKBoard()

def SKInit():
    global SKInitialPlayers,SKReady,SKTimer
    i=1
    pn=None
    commands=None
    if SKReady:
        return
    SKReady=True
    commands=CreateTrigger()
    while True:
        if i > 8: break
        pn=S8Player(i)
        SKKing[pn]=pn
        if SKActive(pn):
            SKInitialPlayers=SKInitialPlayers+1
        TriggerRegisterPlayerChatEvent(commands, Player(pn-1), "-defect", True)
        TriggerRegisterPlayerChatEvent(commands, Player(pn-1), "-king", True)
        i=i+1
    TriggerAddAction(commands, SKCommand)
    SKSync()
    SKTimer=CreateTimer()
    TimerStart(SKTimer, 1.0, True, SKTick)
    DisplayTextToForce(udg_all_players, "King Mode: capture bases to grow your kingdom. Capturing a king captures their kingdom. Captured players keep control and may use -defect once. Allied kills and captures belong to their king. Use -king for status.")
    commands=None

def SKMergeScore(oldKing,newKing):
    udg_KOTH_Team_Gold_Earned_Total[S8Team(newKing)]=udg_KOTH_Team_Gold_Earned_Total[S8Team(newKing)]+udg_KOTH_Team_Gold_Earned_Total[S8Team(oldKing)]
    udg_KOTH_Team_Gold_Earned_Total[S8Team(oldKing)]=0
    SKTroopKills[newKing]=SKTroopKills[newKing]+SKTroopKills[oldKing]
    SKHeroKills[newKing]=SKHeroKills[newKing]+SKHeroKills[oldKing]
    SKCaptures[newKing]=SKCaptures[newKing]+SKCaptures[oldKing]
    SKTroopKills[oldKing]=0
    SKHeroKills[oldKing]=0
    SKCaptures[oldKing]=0

def SKModeClicked():
    if GetTriggerPlayer()!=SKModeHost or SKModeChosen:
        return
    if GetClickedButton()==SKModeButton:
        SKChooseMode(True)
    elif GetClickedButton()==SKFfaButton:
        SKChooseMode(False)

def SKModeDefault():
    SKChooseMode(False)

def SKNormalize():
    i=1
    j=None
    pn=None
    oldKing=None
    successor=None
    changed=False
    while True:
        if i > 8: break
        pn=S8Player(i)
        if SKActive(pn) and not SKActive(SKKing[pn]):
            oldKing=SKKing[pn]
            successor=pn
            j=1
            while True:
                if j > 8: break
                if SKActive(S8Player(j)) and SKKing[S8Player(j)] == oldKing:
                    SKKing[S8Player(j)]=successor
                j=j+1
            SKMergeScore(oldKing, successor)
            changed=True
            DisplayTextToForce(udg_all_players, "King Mode: " + GetPlayerName(Player(successor-1)) + " succeeds the departed king.")
        i=i+1
    if changed:
        SKSync()

def SKOnBaseDeath():
    dead=GetDyingUnit()
    killer=GetKillingUnit()
    victim=GetPlayerId(GetOwningPlayer(dead))+1
    attacker=0
    if not SKReady or not SKActive(victim) or dead != udg_base[victim] or SKRespawnIn[victim] > 0 or SoloFoots_EndGameStarted:
        dead=None
        killer=None
        return
    SKBaseType[victim]=GetUnitTypeId(dead)
    SKBaseHP[victim]=BlzGetUnitMaxHP(dead)
    SKBaseMP[victim]=BlzGetUnitMaxMana(dead)
    SKBaseX[victim]=GetUnitX(dead)
    SKBaseY[victim]=GetUnitY(dead)
    SKBaseFacing[victim]=GetUnitFacing(dead)
    SKProduction[victim]=udg_unit_production[victim]
    udg_unit_production[victim]=False
    SKRespawnIn[victim]=3
    udg_base[victim]=None
    if killer != None:
        attacker=GetPlayerId(GetOwningPlayer(killer))+1
    if SKActive(attacker) and SKKing[attacker] != SKKing[victim]:
        SKCapture(victim, attacker)
    else:
        DisplayTextToPlayer(Player(victim-1), 0.0, 0.0, "King Mode: your base will rebuild. A neutral or allied kill does not capture you.")
    dead=None
    killer=None

def SKOpenMode():
    global SKFfaButton,SKModeButton,SKModeDialog,SKModeHost,SKModeTimeout
    row=1
    pn=None
    t=CreateTrigger()
    DestroyTimer(GetExpiredTimer())
    SKModeDialog=DialogCreate()
    SKModeTimeout=CreateTimer()
    while True:
        if row>8 or SKModeHost!=None: break
        pn=S8Player(row)
        if SKActive(pn) and GetPlayerController(Player(pn-1))==MAP_CONTROL_USER and GetPlayerSlotState(Player(pn-1))==PLAYER_SLOT_STATE_PLAYING:
            SKModeHost=Player(pn-1)
        row=row+1
    if SKModeHost==None:
        SKChooseMode(False)
    else:
        DialogSetMessage(SKModeDialog,"Choose game mode (FFA in 20 seconds)")
        SKFfaButton=DialogAddButton(SKModeDialog,"Normal FFA",70)
        SKModeButton=DialogAddButton(SKModeDialog,"King Mode - capture and defect",75)
        TriggerRegisterDialogEvent(t,SKModeDialog)
        TriggerAddAction(t,SKModeClicked)
        DialogDisplay(SKModeHost,SKModeDialog,True)
        DisplayTextToForce(udg_all_players,GetPlayerName(SKModeHost)+" is choosing Normal FFA or King Mode.")
        TimerStart(SKModeTimeout,20.,False,SKModeDefault)
    t=None

def SKRespawnTick():
    i=1
    pn=None
    b=None
    while True:
        if i > 8: break
        pn=S8Player(i)
        if SKActive(pn):
            if SKRespawnIn[pn] > 0:
                SKRespawnIn[pn]=SKRespawnIn[pn]-1
                if SKRespawnIn[pn] == 0:
                    b=CreateUnit(Player(pn-1), SKBaseType[pn], SKBaseX[pn], SKBaseY[pn], SKBaseFacing[pn])
                    udg_base[pn]=b
                    BlzSetUnitMaxHP(b, SKBaseHP[pn])
                    BlzSetUnitMaxMana(b, SKBaseMP[pn])
                    SetUnitState(b, UNIT_STATE_LIFE, I2R(SKBaseHP[pn]))
                    SetUnitState(b, UNIT_STATE_MANA, I2R(SKBaseMP[pn]))
                    SKRestoreBaseControls(pn)
                    if GetPlayerTechCountSimple('R009', Player(pn-1)) == 1:
                        UnitAddAbility(b, 'A082')
                        BlzStartUnitAbilityCooldown(b, 'A082', TimerGetRemaining(udg_timer_overdrive_CD[pn]))
                    if SKProtectUntil[pn] < SKClock+8:
                        SKProtectUntil[pn]=SKClock+8
                    SetUnitInvulnerable(b, True)
                    udg_unit_production[pn]=SKProduction[pn]
            if SKProtectUntil[pn] > 0 and SKClock >= SKProtectUntil[pn]:
                if udg_base[pn] != None:
                    SetUnitInvulnerable(udg_base[pn], False)
                SKProtectUntil[pn]=0
        else:
            SKRespawnIn[pn]=0
        i=i+1
    b=None

def SKRestoreBaseControls(pn):
    b=udg_base[pn]
    UnitRemoveAbility(b,'A0FS')
    UnitRemoveAbility(b,'A0FR')
    if SKProduction[pn]:
        UnitAddAbility(b,'A0FR')
    else:
        UnitAddAbility(b,'A0FS')
    UnitRemoveAbility(b,'A06X')
    UnitRemoveAbility(b,'A06Y')
    if udg_autosend[pn]:
        UnitAddAbility(b,'A06Y')
    else:
        UnitAddAbility(b,'A06X')
    b=None

def SKSync():
    global udg_KOTH_Team,udg_KOTH_Team_Number
    i=1
    j=None
    pn=None
    other=None
    hillOwner=None
    allied=None
    g=None
    visionKey=None
    while True:
        if i > 8: break
        ForceClear(udg_team[i])
        i=i+1
    i=1
    while True:
        if i > 8: break
        pn=S8Player(i)
        if SKActive(pn):
            ForceAddPlayer(udg_team[S8Team(SKKing[pn])], Player(pn-1))
        if SKActive(pn) and udg_autopoolto[pn]>0:
            if not SKActive(udg_autopoolto[pn]) or SKKing[udg_autopoolto[pn]]!=SKKing[pn]:
                udg_autopoolto[pn]=0
        j=1
        while True:
            if j > 8: break
            other=S8Player(j)
            if pn != other:
                allied=SKActive(pn) and SKActive(other) and SKKing[pn] == SKKing[other]
                visionKey=pn*16+other
                if SKBaseVision[visionKey]!=None:
                    FogModifierStop(SKBaseVision[visionKey])
                    DestroyFogModifier(SKBaseVision[visionKey])
                    SKBaseVision[visionKey]=None
                if allied:
                    SKBaseVision[visionKey]=CreateFogModifierRadius(Player(pn-1),FOG_OF_WAR_VISIBLE,SF_BaseX[other],SF_BaseY[other],1500.,False,False)
                    FogModifierStart(SKBaseVision[visionKey])
                SetPlayerAlliance(Player(pn-1), Player(other-1), ALLIANCE_PASSIVE, allied)
                SetPlayerAlliance(Player(pn-1), Player(other-1), ALLIANCE_HELP_REQUEST, allied)
                SetPlayerAlliance(Player(pn-1), Player(other-1), ALLIANCE_HELP_RESPONSE, allied)
                SetPlayerAlliance(Player(pn-1), Player(other-1), ALLIANCE_SHARED_XP, allied)
                SetPlayerAlliance(Player(pn-1), Player(other-1), ALLIANCE_SHARED_VISION, allied)
                SetPlayerAlliance(Player(pn-1), Player(other-1), ALLIANCE_SHARED_CONTROL, False)
                SetPlayerAlliance(Player(pn-1), Player(other-1), ALLIANCE_SHARED_ADVANCED_CONTROL, False)
            j=j+1
        if SKActive(pn):
            g=CreateGroup()
            GroupEnumUnitsOfPlayer(g, Player(pn-1), None)
            ForGroup(g, SKClearAttack)
            DestroyGroup(g)
        i=i+1
    if udg_mode_koth:
        hillOwner=GetPlayerId(udg_KOTH_Player)+1
        if SKActive(hillOwner):
            udg_KOTH_Team_Number=S8Team(SKKing[hillOwner])
            udg_KOTH_Team=udg_team[udg_KOTH_Team_Number]
        elif hillOwner <= 12:
            TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
            TriggerExecute(gg_trg_KOTH_Reset_Hill)
    g=None

def SKTick():
    global SKClock
    if SoloFoots_EndGameStarted:
        PauseTimer(SKTimer)
        return
    SKClock=SKClock+1
    SKRespawnTick()
    SKNormalize()
    SKCheckVictory()
    SKBoard()

def SKUnifiedKing():
    i=1
    king=0
    pn=None
    while True:
        if i > 8: break
        pn=S8Player(i)
        if SKActive(pn):
            if king == 0:
                king=SKKing[pn]
            elif king != SKKing[pn]:
                return 0
        i=i+1
    return king

def Trig_END_Actions():
    winner=SoloFootsFindWinner()
    if SKEnabled:
        SKCheckVictory()
        return
    if winner == 0 or not SoloFootsPrepareEndGame():
        return
    DisplayTextToForce(GetPlayersAll(), GetPlayerName(Player(winner - 1)) + " wins!")
    CustomVictoryBJ(Player(winner - 1), True, True)

def Trig_KD_Actions():
    row=1
    p=None
    while True:
        if row>8: break
        p=F8_Slot[row]+1
        if F8_Participant[p]:
            DisplayTimedTextToPlayer(GetTriggerPlayer(),0.,0.,20.,GetPlayerName(Player(p-1))+" - Hero K/D: "+I2S(udg_hero_kills[p])+"/"+I2S(udg_hero_deaths[p])+" - Unit K/D: "+I2S(udg_unit_kills[p])+"/"+I2S(udg_unit_deaths[p]))
        row=row+1

def Trig_Multiboard_Create_with_KOTH_Actions():
    global udg_multiboard_kills
    row=1
    if SKEnabled:
        SKCreateBoard()
        return
    if udg_multiboard_kills!=None:
        DestroyMultiboard(udg_multiboard_kills)
    CreateMultiboardBJ(5,9,"Eight Player FFA")
    udg_multiboard_kills=GetLastCreatedMultiboard()
    MultiboardSetItemsStyle(udg_multiboard_kills,True,False)
    MultiboardSetItemValueBJ(udg_multiboard_kills,1,1,"Player")
    MultiboardSetItemValueBJ(udg_multiboard_kills,2,1,"Hero K/D")
    MultiboardSetItemValueBJ(udg_multiboard_kills,3,1,"Unit K/D")
    MultiboardSetItemValueBJ(udg_multiboard_kills,4,1,"Bases")
    MultiboardSetItemValueBJ(udg_multiboard_kills,5,1,"Hill gold")
    while True:
        if row>9: break
        MultiboardSetItemWidthBJ(udg_multiboard_kills,1,row,12.)
        MultiboardSetItemWidthBJ(udg_multiboard_kills,2,row,5.)
        MultiboardSetItemWidthBJ(udg_multiboard_kills,3,row,5.)
        MultiboardSetItemWidthBJ(udg_multiboard_kills,4,row,3.)
        MultiboardSetItemWidthBJ(udg_multiboard_kills,5,row,4.)
        row=row+1
    F8_UpdateBoard()
    MultiboardDisplay(udg_multiboard_kills,True)

def Trig_Multiboard_Update_Actions():
    victim=GetTriggerUnit()
    killer=GetKillingUnit()
    d=GetPlayerId(GetOwningPlayer(victim))+1
    k=GetPlayerId(GetOwningPlayer(killer))+1
    valid=killer!=None and k<=12 and F8_Participant[k] and IsUnitEnemy(victim,Player(k-1))
    if SKEnabled:
        SKCreditKill()
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

def Trig_player_destroyed_Actions():
    global SafeRemoval_GraceTicks,SoloFoots_FinalEliminationWasLeave,SoloFoots_FinalStrikePlayer,SoloFoots_LastEliminatedPlayerNumber,udg_temp_playernumber,udg_unitgroup_kill
    defeatedPlayer=GetOwningPlayer(GetDyingUnit())
    playerNumber=GetConvertedPlayerId(defeatedPlayer)
    if SKEnabled:
        SKOnBaseDeath()
        defeatedPlayer=None
        return
    if playerNumber > 12 or not udg_player_active[playerNumber]:
        defeatedPlayer=None
        return
    udg_temp_playernumber=playerNumber
    if GetKillingUnitBJ() != None:
        SoloFootsDisplayMessageToForce(udg_all_players , ( GetPlayerName(defeatedPlayer) + " has been destroyed by " + GetPlayerName(GetOwningPlayer(GetKillingUnitBJ())) ))
    else:
        SoloFootsDisplayMessageToForce(udg_all_players , ( GetPlayerName(defeatedPlayer) + " has been destroyed." ))
    if udg_mode_koth and udg_KOTH_Team_Number == udg_teamnumber[playerNumber]:
        TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
        TriggerExecute(gg_trg_KOTH_Reset_Hill)
    SoloFoots_LastEliminatedPlayerNumber=playerNumber
    if GetKillingUnitBJ() != None:
        SoloFoots_FinalStrikePlayer=GetOwningPlayer(GetKillingUnitBJ())
    else:
        SoloFoots_FinalStrikePlayer=None
    SoloFoots_FinalEliminationWasLeave=False
    udg_player_active[playerNumber]=False
    SF_RevealEliminated(playerNumber)
    ForceRemovePlayerSimple(defeatedPlayer, udg_Active_PlayGroup)
    SafeRemoval_GraceTicks=0
    EnableTrigger(gg_trg_Kill_units_of_inactive_player)
    EnableTrigger(gg_trg_Visibility)
    ConditionalTriggerExecute(gg_trg_Visibility)
    ConditionalTriggerExecute(gg_trg_END)
    udg_unitgroup_kill=GetUnitsOfPlayerMatching(defeatedPlayer, Condition(Trig_player_destroyed_Func010Func010002002))
    ForGroupBJ(udg_unitgroup_kill, Trig_player_destroyed_Func010Func011002)
    DestroyGroup(udg_unitgroup_kill)
    EnableTrigger(gg_trg_check_if_team_active)
    defeatedPlayer=None

def Trig_player_leaves_Actions():
    global SafeRemoval_GraceTicks,SoloFoots_FinalEliminationWasLeave,SoloFoots_FinalStrikePlayer,SoloFoots_LastEliminatedPlayerNumber,udg_temp_player,udg_temp_playernumber
    leaver=GetTriggerPlayer()
    playerNumber=GetConvertedPlayerId(leaver)
    if playerNumber > 12 or not udg_player_active[playerNumber]:
        leaver=None
        return
    udg_temp_player=leaver
    udg_temp_playernumber=playerNumber
    udg_autopoolto[playerNumber]=0
    if udg_mode_koth and udg_KOTH_Player==Player(playerNumber-1):
        TriggerExecute(gg_trg_KOTH_Set_Neutral_Hill)
        TriggerExecute(gg_trg_KOTH_Reset_Hill)
    SoloFootsDisplayMessageToForce(udg_all_players , ( GetPlayerName(leaver) + " has left the game..." ))
    MultiboardDisplayBJ(False, GetLastCreatedMultiboard())
    MultiboardDisplayBJ(True, GetLastCreatedMultiboard())
    SoloFoots_LastEliminatedPlayerNumber=playerNumber
    SoloFoots_FinalStrikePlayer=None
    SoloFoots_FinalEliminationWasLeave=True
    udg_player_active[playerNumber]=False
    if SKEnabled:
        SKRespawnIn[playerNumber]=0
        SKNormalize()
        SKSync()
        SKCheckVictory()
    ForceRemovePlayerSimple(leaver, udg_Active_PlayGroup)
    SafeRemoval_GraceTicks=0
    EnableTrigger(gg_trg_Kill_units_of_inactive_player)
    EnableTrigger(gg_trg_Visibility)
    ConditionalTriggerExecute(gg_trg_Visibility)
    ConditionalTriggerExecute(gg_trg_END)
    EnableTrigger(gg_trg_check_if_team_active)
    leaver=None