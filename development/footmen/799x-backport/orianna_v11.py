"""Front-held solid orb, travel growth, and map-Lich attributes."""
from pathlib import Path
import re,json

def patch(script):
    def edit(name,old,new):
        nonlocal script
        before=re.search(r'^function '+name+r' takes .*?^endfunction',script,re.M|re.S)[0]
        assert old in before,(name,old)
        script=script.replace(before,before.replace(old,new),1)
    helper='''function OM_FollowCarrier takes integer i returns nothing
    local unit u = OM_Carrier[i]
    local real facing = GetUnitFacing(u) * 0.01745329252
    local real x = GetUnitX(u)
    local real y = GetUnitY(u)
    local real height = GetUnitFlyHeight(u) + 260.0
    if u == OM_Hero[i] then
        set x = x + 70.0 * Cos(facing)
        set y = y + 70.0 * Sin(facing)
        set height = GetUnitFlyHeight(u) + 145.0
    endif
    call SetUnitX(OM_Ball[i], x)
    call SetUnitY(OM_Ball[i], y)
    call SetUnitFlyHeight(OM_Ball[i], height + 5.0 * Sin(OM_Now * 3.0), 0.0)
    set u = null
endfunction

'''
    script=script.replace('function OM_Home takes',helper+'function OM_Home takes',1)
    edit('OM_Home', '''    call SetUnitX(OM_Ball[i], GetUnitX(OM_Hero[i]))
    call SetUnitY(OM_Ball[i], GetUnitY(OM_Hero[i]))
    call SetUnitFlyHeight(OM_Ball[i], GetUnitFlyHeight(OM_Hero[i])+220.0, 0.0)''','    call OM_FollowCarrier(i)')
    edit('OM_Tick', '''                    call SetUnitX(OM_Ball[i], GetUnitX(OM_Carrier[i]))
                    call SetUnitY(OM_Ball[i], GetUnitY(OM_Carrier[i]))
                    call SetUnitFlyHeight(OM_Ball[i], GetUnitFlyHeight(OM_Carrier[i])+220.0+12.0*Sin(OM_Now*3.0), 0.0)''','                    call OM_FollowCarrier(i)')
    edit('OM_UpdateBallVisual','    local real gesture = 0.0','''    local real gesture = 0.0
    local real size = 2.0
    local real startSize = LoadReal(OM_Hash, key, -111)''')
    edit('OM_UpdateBallVisual','BlzSetSpecialEffectAlpha(fx, 200)','BlzSetSpecialEffectAlpha(fx, 255)')
    edit('OM_UpdateBallVisual','    call BlzSetSpecialEffectScale(fx, 2.0 * (1.0 + 0.18 * gesture))','''    if OM_State[i] == 0 and OM_Carrier[i] == OM_Hero[i] then
        set size = 1.05
    elseif OM_State[i] == 1 or OM_State[i] == 2 then
        if startSize <= 0.0 then
            set startSize = 1.05
        endif
        set size = startSize + (2.0 - startSize) * RMinBJ(1.0, RMaxBJ(0.0, (OM_Now - LoadReal(OM_Hash, key, -109)) / 0.22))
    endif
    call SaveReal(OM_Hash, key, -110, size)
    call BlzSetSpecialEffectScale(fx, size * (1.0 + 0.18 * gesture))''')
    edit('OM_UpdateBallVisual','    // The control ball follows either carrier at their fly height + 220 units.','    // Front-held for Orianna; overhead for protected allies.')
    edit('OM_StartTravelFX','    call OM_StopTravelFX(i)','''    call SaveReal(OM_Hash, GetHandleId(OM_Ball[i]), -109, OM_Now)
    call SaveReal(OM_Hash, GetHandleId(OM_Ball[i]), -111, LoadReal(OM_Hash, GetHandleId(OM_Ball[i]), -110))
    call OM_StopTravelFX(i)''')
    edit('OM_Unregister','    call OM_ClearBallVisual(i)','''    call RemoveSavedReal(OM_Hash, GetHandleId(OM_Ball[i]), -109)
    call RemoveSavedReal(OM_Hash, GetHandleId(OM_Ball[i]), -110)
    call RemoveSavedReal(OM_Hash, GetHandleId(OM_Ball[i]), -111)
    call OM_ClearBallVisual(i)''')
    edit('OM_GroundRing',r'Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl',r'Abilities\\Spells\\Undead\\FrostNova\\FrostNovaTarget.mdl')
    edit('OM_GroundRing','radius/200.0','radius/140.0')
    edit('OM_GroundRing','    call RemoveLocation(ground)',r'''    call OM_CommandGround(4, x, y, radius, 0.0)
    set burst = AddSpecialEffect("Abilities\\Spells\\Other\\Monsoon\\MonsoonBoltTarget.mdl", x, y)
    call BlzSetSpecialEffectZ(burst, GetLocationZ(ground) + 40.0)
    call BlzSetSpecialEffectScale(burst, 1.2)
    call BlzSetSpecialEffectColor(burst, 120, 230, 255)
    call OM_KeepEffect(burst, 1.0)
    call RemoveLocation(ground)''')
    runtime=json.loads((Path(__file__).parent/'lich-stats.json').read_text())['runtime']
    for stat,value in runtime.items():
        name='Trig_set_hero_stats_Actions'
        old=re.search(r'set udg_hero_'+stat+r'\[92\]=[0-9.]+',script)[0]
        edit(name,old,'set udg_hero_'+stat+'[92]='+format(value,'g'))
    return script
