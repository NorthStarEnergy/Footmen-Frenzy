from pathlib import Path
p=Path('solo-v1.8-799x/build.py');s=p.read_text();s=s.replace("import objdata", "import objdata\nsys.path.insert(0,str(W/'hero-polish'))\nfrom archive_helpers import storm,read_storm,c\ndef read_asset(path):\n h=c.c_void_p();assert storm.SFileOpenArchive(str(DONOR),0,256,c.byref(h))\n try:return read_storm(h,path)\n finally:storm.SFileCloseArchive(h)")
s=s.replace('raw=da.read_file(path);out=O/path','raw=read_asset(path);out=O/path')
p.write_text(s)
