from pathlib import Path
p=Path('shared-sync-v85/build.py');s=p.read_text();anchor='# Add the exact donor globals referenced by these bodies, excluding locals and existing globals.'
s=s.replace(anchor,'''# Retain the 799X-specific inventory policy while adopting Solo's lookup implementation.
added['ItemLimit_MaxCopies']=added['ItemLimit_MaxCopies'].replace('    return 0\\nendfunction', "    if itemTypeId == 'nspi' then\\n        return 1\\n    endif\\n    return 0\\nendfunction")
n='ItemLimit_HeroTypeBlocked'
f=added[n]
f=f.replace("    elseif itemTypeId == 'desc' then", "    elseif itemTypeId == 'nspi' then\\n        return heroTypeId == 'O003'\\n    elseif itemTypeId == 'desc' then")
for item,extra in [('desc',["E00Z"]),('I01H',["E00U","E00Z","N01L"])]:
 pattern=r"(elseif itemTypeId == '"+item+r"' then[^\\n]*\\n        return [^\\n]+)"
 f,count=re.subn(pattern,lambda m:m[1]+''.join(" or heroTypeId == '"+x+"'" for x in extra),f);assert count==1
added[n]=f
replacements['Trig_ITEM_limits_Actions']=replacements['Trig_ITEM_limits_Actions'].replace("set udg_temp_item_type='modt'","set udg_temp_item_type='nspi'")
'''+anchor);p.write_text(s)
