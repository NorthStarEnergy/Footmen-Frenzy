"""Visual-only dome feedback; combat numbers and eligibility remain unchanged."""
from pathlib import Path

def patch(s):
    s=s.replace('    integer GD_Count = 0', '    hashtable GDV_Data = InitHashtable()\n    group GDV_Units = CreateGroup()\n    integer GDV_Step = 0\n    integer GD_Count = 0',1)
    start=s.index('function GD_Stop ')
    s=s[:start]+Path(__file__).with_suffix('.j').read_text()+'\n'+s[start:]
    s=s.replace('    call UnitRemoveAbility(GD_Caster[i], GD_SLOW)', '    call GDV_Stop(GD_Caster[i])\n    call UnitRemoveAbility(GD_Caster[i], GD_SLOW)',1)
    start=s.index('function GD_Tick ');end=s.index('function GD_Cast ',start)
    block=s[start:end]
    block=block.replace('    loop\n', '    set GDV_Step = GDV_Step + 1\n    loop\n',1)
    block=block.replace('            call GroupEnumUnitsInRange(GD_Enum', '            call GDV_Dome(i, x, y)\n            call GroupEnumUnitsInRange(GD_Enum',1)
    needle='                    if IsUnitAlly(u, GetOwningPlayer(caster)) then'
    block=block.replace(needle,needle+'\n                        call GDV_Mark(u, true)\n                        if GetWidgetLife(u) < GetUnitState(u, UNIT_STATE_MAX_LIFE) or GetUnitState(u, UNIT_STATE_MANA) < GetUnitState(u, UNIT_STATE_MAX_MANA) then\n                            call GDV_Pulse(u, true)\n                        endif')
    block=block.replace('                        set burned =', '                        call GDV_Mark(u, false)\n                        set burned =',1)
    block=block.replace('                        if burned > 0.0 then', '                        if burned > 0.0 then\n                            call GDV_Pulse(u, false)',1)
    block=block.replace('    if GD_Count == 0 then','    call ForGroup(GDV_Units, function GDV_CleanupUnit)\n    if GD_Count == 0 then',1)
    return s[:start]+block+s[end:]
