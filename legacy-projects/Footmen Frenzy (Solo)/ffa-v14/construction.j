function F14_IsTower takes integer id returns boolean
    return TOWER_TYPES
endfunction

function F14_Grass takes real x,real y returns boolean
    local integer tile=GetTerrainType(x,y)
    return tile=='Yhdg' or tile=='Ygsb'
endfunction

function F14_OwnBase takes integer pn,real x,real y returns boolean
    local real dx=x-SF_BaseX[pn]
    local real dy=y-SF_BaseY[pn]
    local real d=dx*dx+dy*dy
    local integer row=1
    local integer other
    if F8_Team[pn-1]==0 or not udg_player_active[pn] or d>2102500. or x*x+(y+256.)*(y+256.)<7290000. then
        return false
    endif
    loop
        exitwhen row>8
        set other=F8_Slot[row]+1
        set dx=x-SF_BaseX[other]
        set dy=y-SF_BaseY[other]
        if other!=pn and dx*dx+dy*dy<d then
            return false
        endif
        set row=row+1
    endloop
    return F14_Grass(x,y) and F14_Grass(x-64.,y-64.) and F14_Grass(x+64.,y-64.) and F14_Grass(x-64.,y+64.) and F14_Grass(x+64.,y+64.)
endfunction

function F14_Construct takes nothing returns nothing
    local unit tower=GetConstructingStructure()
    local player owner=GetOwningPlayer(tower)
    local integer pn=GetPlayerId(owner)+1
    local group g
    local unit u
    local integer count=0
    local boolean valid
    if GetUnitTypeId(tower)!='hwtw' then
        set tower=null
        set owner=null
        return
    endif
    set valid=F14_OwnBase(pn,GetUnitX(tower),GetUnitY(tower))
    set g=CreateGroup()
    call GroupEnumUnitsOfPlayer(g,owner,null)
    loop
        set u=FirstOfGroup(g)
        exitwhen u==null
        call GroupRemoveUnit(g,u)
        if F14_IsTower(GetUnitTypeId(u)) and not IsUnitType(u,UNIT_TYPE_DEAD) then
            set count=count+1
        endif
    endloop
    call DestroyGroup(g)
    if not valid or count>4 then
        call RemoveUnit(tower)
        call AdjustPlayerStateBJ(250,owner,PLAYER_STATE_RESOURCE_GOLD)
        call DisplayTextToPlayer(owner,0.,0.,"Scout Towers require grass inside your own base. Maximum four living towers, including upgrades and construction. 250 gold refunded.")
    endif
    set u=null
    set g=null
    set tower=null
    set owner=null
endfunction

function F14_Init takes nothing returns nothing
    local trigger t=CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_CONSTRUCT_START)
    call TriggerAddAction(t,function F14_Construct)
    set t=null
endfunction

