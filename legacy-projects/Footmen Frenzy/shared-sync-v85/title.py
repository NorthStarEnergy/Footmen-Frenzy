from pathlib import Path
p=Path('shared-sync-v85/build.py');s=p.read_text();anchor='# Imported helpers must precede their callers, using native dependency ordering.'
s=s.replace(anchor,'''solo_replacements['config']=sf['config'].replace('Solo Foots v1.8 4P - 799X Update 08','Solo Foots v1.8 4P - Shared Fixes Update 09')
'''+anchor);p.write_text(s)
