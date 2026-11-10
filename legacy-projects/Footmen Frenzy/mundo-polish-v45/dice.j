function TF45_Odds takes unit u returns real
    local integer h=GetHandleId(u)
    return 50. + RMinBJ(10.,LoadReal(TF33_G,h,1)/90.) + 2.*I2R(IMinBJ(5,LoadInteger(TF33_G,h,2)))
endfunction

function TF45_Track takes unit u returns nothing
    if GetUnitTypeId(u)=='HTf1' and not IsUnitIllusion(u) then
        call GroupAddUnit(TF33_Heroes,u)
    endif
endfunction

function TF33_IncomeHero takes nothing returns nothing
    local unit u=GetEnumUnit()
    local integer h=GetHandleId(u)
    if GetUnitTypeId(u)==0 or IsUnitIllusion(u) then
        call GroupRemoveUnit(TF33_Heroes,u)
        call FlushChildHashtable(TF33_G,h)
    elseif TFP_TF_Alive(u) then
        call SaveReal(TF33_G,h,1,RMinBJ(900.,LoadReal(TF33_G,h,1)+1.))
    else
        call FlushChildHashtable(TF33_G,h)
    endif
    set u=null
endfunction

function TF45_Enter takes nothing returns nothing
    call TF45_Track(GetTriggerUnit())
endfunction

function TF45_Existing takes nothing returns nothing
    call TF45_Track(GetEnumUnit())
endfunction

function TF45_Death takes nothing returns nothing
    local unit dead=GetTriggerUnit()
    local unit killer=GetKillingUnit()
    local integer h=GetHandleId(killer)
    if IsUnitInGroup(dead,TF33_Heroes) then
        call FlushChildHashtable(TF33_G,GetHandleId(dead))
    endif
    if killer!=null and IsUnitInGroup(killer,TF33_Heroes) and TFP_TF_Alive(killer) and IsUnitType(dead,UNIT_TYPE_HERO) and not IsUnitIllusion(dead) and IsUnitEnemy(dead,GetOwningPlayer(killer)) then
        call SaveInteger(TF33_G,h,2,IMinBJ(5,LoadInteger(TF33_G,h,2)+1))
    endif
    set dead=null
    set killer=null
endfunction

function TF45_ShareLoss takes player loser returns nothing
    local force eligible=CreateForce()
    local group g=CreateGroup()
    local unit u
    local player p
    local integer i=0
    local integer count=0
    local integer remaining=50
    local integer share
    local integer start=GetRandomInt(0,11)
    loop
        exitwhen i>=12
        set p=Player(i)
        if p!=loser and IsPlayerEnemy(p,loser) and GetPlayerSlotState(p)==PLAYER_SLOT_STATE_PLAYING then
            call GroupEnumUnitsOfPlayer(g,p,null)
            loop
                set u=FirstOfGroup(g)
                exitwhen u==null
                call GroupRemoveUnit(g,u)
                if TFP_TF_Alive(u) and IsUnitType(u,UNIT_TYPE_HERO) and not IsUnitIllusion(u) then
                    call ForceAddPlayer(eligible,p)
                    set count=count+1
                    call GroupClear(g)
                endif
            endloop
        endif
        set i=i+1
    endloop
    set i=0
    loop
        exitwhen i>=12 or count==0
        set p=Player(ModuloInteger(start+i,12))
        if IsPlayerInForce(p,eligible) then
            set share=R2I(I2R(remaining)/I2R(count))
            call SetPlayerState(p,PLAYER_STATE_RESOURCE_GOLD,GetPlayerState(p,PLAYER_STATE_RESOURCE_GOLD)+share)
            call DisplayTextToPlayer(p,0.,0.,"|cffffcc00Loaded Dice: +"+I2S(share)+" gold from an enemy's lost roll.|r")
            set remaining=remaining-share
            set count=count-1
        endif
        set i=i+1
    endloop
    call DestroyGroup(g)
    call DestroyForce(eligible)
    set g=null
    set eligible=null
    set p=null
    set u=null
endfunction

function TF45_Roll takes nothing returns nothing
    local unit u=GetTriggerUnit()
    local player p=GetOwningPlayer(u)
    local integer gold=GetPlayerState(p,PLAYER_STATE_RESOURCE_GOLD)
    local real odds=TF45_Odds(u)
    if GetSpellAbilityId()=='ATfg' then
        if gold<50 or IsUnitIllusion(u) or not TFP_TF_Alive(u) then
            call BlzEndUnitAbilityCooldown(u,'ATfg')
            call DisplayTextToPlayer(p,0.,0.,"Loaded Dice requires at least 50 gold.")
        else
            call BlzStartUnitAbilityCooldown(u,'ATfg',60.)
            if GetRandomReal(0.,100.)<odds then
                call SetPlayerState(p,PLAYER_STATE_RESOURCE_GOLD,gold+50)
                call DisplayTextToPlayer(p,0.,0.,"|cffffcc00Loaded Dice: WIN +50 gold!|r ("+I2S(R2I(odds))+"% win chance)")
            else
                call SetPlayerState(p,PLAYER_STATE_RESOURCE_GOLD,gold-50)
                call TF45_ShareLoss(p)
                call DisplayTextToPlayer(p,0.,0.,"|cffff5555Loaded Dice: LOSS -50 gold.|r ("+I2S(R2I(odds))+"% win chance)")
            endif
        endif
    endif
    set u=null
    set p=null
endfunction

function TF45_DiceInit takes nothing returns nothing
    local trigger t=CreateTrigger()
    local region r=CreateRegion()
    local group g=CreateGroup()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_DEATH)
    call TriggerAddAction(t,function TF45_Death)
    set t=CreateTrigger()
    call RegionAddRect(r,bj_mapInitialPlayableArea)
    call TriggerRegisterEnterRegion(t,r,null)
    call TriggerAddAction(t,function TF45_Enter)
    set t=CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddAction(t,function TF45_Roll)
    call GroupEnumUnitsInRect(g,bj_mapInitialPlayableArea,null)
    call ForGroup(g,function TF45_Existing)
    call DestroyGroup(g)
    set g=null
    set r=null
    set t=null
endfunction
