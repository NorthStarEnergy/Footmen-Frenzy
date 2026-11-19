"""Refresh the native learn menu from the selected hero's acquired ranks."""
import re
import struct

SETTER = re.compile(rb"""call BlzSetAbilityResearch(Extended)?Tooltip\('(.{4})', ("[^\r\n]*"), (\d+)\)""")
ANCHOR = b"function FF_CompactHeroTooltips_Init takes nothing returns nothing"


def object_research_ranks(ability, fields):
    """Build learn text from the ranks of a skill defined in the object data."""
    name = re.sub(rb'\|c[0-9a-fA-F]{8}|\|r', b'', fields[b'aret', 0])
    maximum = int.from_bytes(fields[b'alev', 0], 'little')
    first = int.from_bytes(fields[b'arlv', 0], 'little')
    skip = int.from_bytes(fields[b'alsk', 0], 'little')
    damage = {
        b'AVgq': rb'(?<=Deals )[^.]+?(?= as damage)|\+\d+(?= permanent| instead)',
        b'AVgw': rb'(?<=deals )\d+(?= damage)|\d+%(?= more)',
        b'AVgr': rb'(?<= for )\d[^|]+?(?= damage\.)',
    }.get(ability)

    def quote(value):
        return b'"' + value.replace(b'\\', b'\\\\').replace(b'"', b'\\"') + b'"'

    ranks = {}
    for rank in range(maximum):
        description = fields[b'aub1', rank + 1].replace(b'magic damage', b'damage')
        if damage:
            description = re.sub(damage, rb'|cffff8979\g<0>|r', description)
        ranks[rank] = {
            b'': quote(name + f' - Level {rank + 1}'.encode()),
            b'Extended': quote(
                f'Requires hero level {first + rank * skip}|n'.encode()
                + description
            ),
        }
    return ranks


def functions(script, object_ranks=None):
    ranks = {}
    # Some older builds also initialize legacy text. The compact table owns
    # the current wording wherever both initializers describe the same spell.
    compact = script.split(ANCHOR, 1)[1].split(b"endfunction", 1)[0]
    for source in (script, compact):
        for extended, ability, value, index in SETTER.findall(source):
            ranks.setdefault(ability, {}).setdefault(int(index), {})[extended] = value
    for ability, levels in (object_ranks or {}).items():
        if ability not in ranks:
            ranks[ability] = levels
    lines = []
    abilities = []
    for ability, levels in ranks.items():
        if len(levels) < 2:
            continue
        assert sorted(levels) == list(range(len(levels)))
        name = ability.decode()
        abilities.append(name)
        lines.extend([f"function FF_LearnTip_{name} takes unit hero returns nothing",
                      f"    local integer rank = GetUnitAbilityLevel(hero, '{name}')"])
        for rank, fields in sorted(levels.items()):
            compare = '>=' if rank == len(levels) - 1 else '=='
            lines.append(f"    {'elseif' if rank else 'if'} rank {compare} {rank} then")
            for field in (b'', b'Extended'):
                value = fields[field].decode('utf-8')
                lines.append(f"        call BlzSetAbilityResearch{field.decode()}Tooltip('{name}', {value}, 0)")
        lines.extend(["    endif", "endfunction", ""])
    lines += ["function FF_LearnTip_Refresh takes nothing returns nothing",
              "    local unit hero = GetTriggerUnit()",
              "    if IsUnitType(hero, UNIT_TYPE_HERO) and IsUnitSelected(hero, GetLocalPlayer()) then"]
    lines += [f"        call FF_LearnTip_{name}(hero)" for name in abilities]
    lines += ["    endif", "    set hero = null", "endfunction", "",
              "function FF_LearnTip_Init takes nothing returns nothing",
              "    local trigger refresh = CreateTrigger()",
              "    call TriggerRegisterAnyUnitEventBJ(refresh, EVENT_PLAYER_UNIT_SELECTED)",
              "    call TriggerRegisterAnyUnitEventBJ(refresh, EVENT_PLAYER_HERO_SKILL)",
              "    call TriggerAddAction(refresh, function FF_LearnTip_Refresh)",
              "    set refresh = null", "endfunction", ""]
    return "\n".join(lines).encode(), len(abilities)


def patch(source, generated, anchor=ANCHOR):
    start = source.index(anchor)
    end = source.index(b'endfunction', start)
    nl = b'\r\n' if b'\r\n' in source[start:end] else b'\n'
    return (source[:start] + generated.replace(b'\n', nl) + nl +
            source[start:end] + b'    call FF_LearnTip_Init()' + nl + source[end:])


def patch_editor(wct, generated):
    for anchor in (ANCHOR, b'function FF_HeroTooltips_Init takes nothing returns nothing'):
        if anchor in wct:
            pos = wct.index(anchor)
            end = wct.index(b'\0', pos) + 1
            for start in range(pos, 3, -1):
                if struct.unpack_from('<I', wct, start-4)[0] == end-start:
                    block = wct[start:end]
                    updated = patch(block, generated, anchor)
                    return wct[:start-4] + struct.pack('<I', len(updated)) + updated + wct[end:]
            raise ValueError('Missing length-prefixed trigger record')
    return wct
