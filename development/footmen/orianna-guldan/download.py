from pathlib import Path
import urllib.request,re,zipfile,io
r=Path(__file__).resolve().parent
url='https://www.hiveworkshop.com/threads/guldan.295598/'
html=urllib.request.urlopen(url).read().decode()
links=re.findall(r'href="([^"]*resources/guldan\.73923/download[^\"]*)"',html)
assert links
url=links[0].replace('&amp;','&')
if url.startswith('/'):url='https://www.hiveworkshop.com'+url
raw=urllib.request.urlopen(url).read();z=zipfile.ZipFile(io.BytesIO(raw))
(r/'assets/Guldan.zip').write_bytes(raw)
for n in z.namelist():
 if n.lower().endswith(('.mdx','.blp','.txt')):
  (r/'assets'/Path(n).name).write_bytes(z.read(n))
print(z.namelist())
