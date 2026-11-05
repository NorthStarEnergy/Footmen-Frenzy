import re

def patch(s):
    def edit(name,old,new):
        nonlocal s
        before=re.search(r'^function '+name+r' takes .*?^endfunction',s,re.M|re.S)[0]
        assert old in before,(name,old)
        s=s.replace(before,before.replace(old,new),1)
    before=re.search(r'^function OM_FollowCarrier takes .*?^endfunction',s,re.M|re.S)[0]
    edit('OM_FollowCarrier',before,'''function OM_FollowCarrier takes integer i returns nothing
    local unit u = OM_Carrier[i]
    call SetUnitX(OM_Ball[i], GetUnitX(u))
    call SetUnitY(OM_Ball[i], GetUnitY(u))
    call SetUnitFlyHeight(OM_Ball[i], GetUnitFlyHeight(u) + 260.0, 0.0)
    set u = null
endfunction''')
    for old in ['EnchantressOrb.mdx','EnchantressOrbBlue.mdx']:
        edit('OM_UpdateBallVisual',old,'DenseOrb.mdx')
    start='    if OM_State[i] == 0 and OM_Carrier[i] == OM_Hero[i] then'
    before=re.search(r'^function OM_UpdateBallVisual takes .*?^endfunction',s,re.M|re.S)[0]
    a=before.index(start);b=before.index('    call SaveReal(OM_Hash, key, -110, size)',a)
    edit('OM_UpdateBallVisual',before[a:b],'')
    edit('OM_EmitTrail','EnchantressTrail.mdx','DenseOrb.mdx')
    edit('FS_ClearFortitude','    call BlzSetUnitArmor(FS_U[i], BlzGetUnitArmor(FS_U[i]) - FS_Armor[i])\n','')
    edit('FS_OnCast','                call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + FS_Armor[i])', '''                call UnitAddAbility(u, 'AGf1')
                call SetUnitAbilityLevel(u, 'AGf1', level)
                call BlzUnitHideAbility(u, 'AGf1', true)''')
    edit('FS_OnCast','"DrunkenRageBuff.mdx"',r'"Abilities\\Spells\\Human\\InnerFire\\InnerFireTarget.mdl"')
    return s
