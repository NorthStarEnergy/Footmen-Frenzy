from pathlib import Path
p=Path('shared-sync-v85/build.py');s=p.read_text()
anchor='# Resolve only missing function dependencies; never overwrite another existing subsystem implicitly.'
s=s.replace(anchor,'''# Preserve the recipient's correct two-copy warning rather than importing Solo's stale 1x text.
n='Trig_ITEM_limits_Actions'
replacements[n]=replacements[n].replace('"|cffff0000Only 1x |r"','"|cffff0000Only " + I2S(maxCopies) + "x |r"')
'''+anchor)
anchor='# Imported helpers must precede their callers, using native dependency ordering.'
s=s.replace(anchor,'''solo_replacements['Trig_ITEM_limits_Actions']=sf['Trig_ITEM_limits_Actions'].replace('"|cffff0000Only 1x |r"','"|cffff0000Only " + I2S(maxCopies) + "x |r"')
'''+anchor)
p.write_text(s)
