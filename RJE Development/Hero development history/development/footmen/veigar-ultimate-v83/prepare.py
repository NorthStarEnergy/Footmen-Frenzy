from pathlib import Path
R=Path(__file__).resolve().parent; W=R.parent
s=(W/'veigar-stacks-v82/build.py').read_text()
s=s.replace('veigar-visuals-v81/release/FF799X_Rx_Veigar_Visuals_v81_TEST.w3x','veigar-stacks-v82/release/FF799X_Rx_Veigar_Stacks_v82_TEST.w3x').replace("W/'veigar-visuals-v81/verification.json'","W/'veigar-stacks-v82/verification.json'")
a=s.index('replacements=');b=s.index('# Patch the authoritative',a)
s=s[:a]+'''replacements={'VG_ClassicKill':[], 'VG_ClassicCast':[], 'VG82_UpdateCounter':[]}
def patch(s):
 fs=functions(s)
 if 'VG_ClassicCast' not in fs:return s
 old=fs['VG_ClassicKill']
 new=old.replace('        call VG82_UpdateCounter(u)', '        if LoadUnitHandle(VG_Hash, GetHandleId(u), 701) == victim then\\n            call SaveInteger(VG_Hash, GetHandleId(u), 703, LoadInteger(VG_Hash, GetHandleId(u), 703) + gain)\\n        endif\\n        call VG82_UpdateCounter(u)')
 s=s.replace(old,new,1)
 old=fs['VG_ClassicCast']
 damage='            call UnitDamageTarget(caster, target, damage, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)'
 new=old.replace(damage,'            call SaveUnitHandle(VG_Hash, GetHandleId(caster), 701, target)\\n'+damage+'\\n            call RemoveSavedHandle(VG_Hash, GetHandleId(caster), 701)',1)
 new=new.replace(' + 0.8 * enemyInt',' + 0.8 * enemyInt + I2R(LoadInteger(VG_Hash, GetHandleId(caster), 703))')
 s=s.replace(old,new,1)
 s=s.replace(fs['VG82_UpdateCounter'],helper,1)
 return s
''' +s[b:]
s=s.replace("set(after)-set(before)=={'VG82_UpdateCounter'}","set(after)==set(before)")
a=s.index('  if entry[\'newId\']==\'AVgq\':');b=s.index("(O/'war3map.w3a')",a)
s=s[:a]+'''  if entry['newId']=='AVgr':
   for m in entry['mods']:
    if m['id'] in ['ahky','arhk']:m['value']='V'
    if m['id'] in ['atp1','aret']:m['value']=m['value'].replace('|cffffcc00R|r','|cffffcc00V|r')
    if m['id'] in ['aub1','arut']:
     m['value']+='|n|nBaleful Strike (Z) kills permanently add +1 ultimate damage per enemy unit or +5 per enemy hero. Other kills do not add ultimate stacks. Stacks persist through death and ability upgrades. The live bonus appears on this ability.'
''' +s[b:]
s=s.replace('v82 permanent Veigar Z damage stacks','v83 ultimate stacks from Z kills')
a=s.index("(O/'FF_MAINTENANCE.md').write_bytes");b=s.index('out=',a)
s=s[:a]+'''(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\\n\\nv83: V ultimate gains separate permanent +1 damage per Z unit kill / +5 per Z hero kill. Other kill sources do not grant V stacks. Existing Z stacks retained. V tooltip counter and V hotkey added. Engine test pending.\\n')
'''+s[b:]
s=s.replace("out=R/'release/FF799X_Rx_Veigar_Stacks_v82_TEST.w3x'","out=R/'release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x'")
s=s.replace("added_functions=['VG82_UpdateCounter']","added_functions=[]")
s=s.replace('Build permanent Veigar Z damage stacks on the verified v81 map.','Build permanent ultimate damage from Z kills on verified v82.')
(R/'build.py').write_text(s)
h=(W/'veigar-stacks-v82/stack-counter.j').read_text()
h=h.replace('    set a = null', '''    set a = BlzGetUnitAbility(u, 'AVgr')
    set stacks = LoadInteger(VG_Hash, GetHandleId(u), 703)
    set i = 0
    if a != null then
        loop
            exitwhen i >= 3
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL, i, "Primordial Burst [|cffffcc00V|r] - |cff80dfff+" + I2S(stacks) + " damage|r")
            call BlzSetAbilityStringLevelField(a, ABILITY_SLF_TOOLTIP_NORMAL_EXTENDED, i, "Deals " + I2S(550 + 300 * i) + " + 120% Intelligence + 80% target Intelligence + |cff80dfff" + I2S(stacks) + " permanent bonus|r magic damage to an enemy hero.|n|nKills with Baleful Strike (Z) permanently grant +1 ultimate damage per enemy unit, or +5 per enemy hero. Other kill sources do not grant ultimate stacks. Illusions and structures do not count.|nStacks never reset, including on death.|n|nCurrent permanent bonus: |cff80dfff+" + I2S(stacks) + " damage|r")
            set i = i + 1
        endloop
    endif
    set a = null''')
(R/'stack-counter.j').write_text(h)
