from pathlib import Path
p=Path('solo-v1.8-799x/build.py');s=p.read_text().replace("('AOz','AGr','AGf','BOr','BGr'))", "('AOz','AGr','AGf','BOr','BGr','GF0'))")
s=s.replace("raw=(B/name).read_bytes();(O/name).write_bytes(raw)", "raw=(B/name).read_bytes().replace(b'Solo Foots v1.8 4P PRELOAD TEST07',title.encode());(O/name).write_bytes(raw)")
p.write_text(s)
