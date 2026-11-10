"""Resolve real item command-button artwork, preserving map overrides before CASC defaults."""
import audit_core as c
import io,json,hashlib,base64,struct
from PIL import Image,ImageDraw

dist=c.PROJECT/'item-wiki/dist'
data=json.loads((dist/'data.json').read_text(encoding='utf-8'))
extracted=c.ROOT/'icon-extraction/files'
report=[]
def decode(raw):
 # Pillow's BLP1 palette decoder uses palette alpha, but Warcraft stores
 # alpha in a separate per-mipmap bit plane. Read that plane explicitly.
 if raw[:4]==b'BLP1' and struct.unpack_from('<I',raw,4)[0]==1:
  _,depth,w,h,encoding,_=struct.unpack_from('<6I',raw,4)
  assert encoding in (4,5) and depth in (0,1,4,8)
  offset=struct.unpack_from('<I',raw,28)[0];count=w*h
  indices=raw[offset:offset+count];alpha=raw[offset+count:]
  pixels=[]
  for i,index in enumerate(indices):
   b,g,r,_=raw[156+index*4:160+index*4]
   a=255 if depth==0 else ((alpha[i*depth//8]>>(i*depth%8))&((1<<depth)-1))*255//((1<<depth)-1)
   pixels.append((r,g,b,a))
  im=Image.new('RGBA',(w,h));im.putdata(pixels);return im
 return Image.open(io.BytesIO(raw)).convert('RGBA')
for item in data['items']:
 uid=item['id'];art,field_source=c.val('item',uid,'iico')
 assert art,(uid,'missing item icon field')
 art=art.split(',')[0].strip('"');candidates=[]
 local=extracted/art.replace('\\','/')
 if local.exists():candidates.append((local.read_bytes(),'map:'+art))
 else:
  try:
   raw=c.archive(art)
   if raw:candidates.append((raw,'map:'+art))
  except Exception:pass
 for path in [art,art.rsplit('.',1)[0]+'.dds',art.rsplit('.',1)[0]+'.tga']:
  raw=c.gd.game_read('war3.w3mod:'+path)
  if raw:candidates.append((raw,'game:'+path))
 errors=[];decoded=None
 for raw,source in candidates:
  try:
   decoded=decode(raw);break
  except Exception as e:errors.append(str(e))
 assert decoded is not None,(uid,art,errors)
 filename=f'icons/{uid}.png';decoded.save(dist/filename)
 item['icon']=filename
 item['iconSource']={'path':art,'field':'iico','fieldSource':field_source,'assetSource':source,'sha256':hashlib.sha256(raw).hexdigest(),'dimensions':list(decoded.size)}
 if item['category']=='Spell purchase':
  note='Icon: this map inherits the Greater Mana Potion shop icon for this spell token. Its spell artwork is assigned to the model field (ifil), not the icon field (iico); the wiki displays the actual item icon.'
  if note not in item['details']:item['details'].append(note)
 report.append(dict(id=uid,**item['iconSource']))
data['meta']['icons']='All 222 entries use actual item iico artwork, extracted from the audited map first and Warcraft III SD game assets second. DDS replacements are decoded to PNG; no substitute art.'
(dist/'data.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
(dist/'data.js').write_text('window.WIKI_DATA = '+json.dumps(data)+';',encoding='utf-8')
(c.ROOT/'wiki-icon-provenance.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
# Rebuild the standalone file without repacking or modifying any map/source objects.
embedded=json.loads(json.dumps(data))
for item in embedded['items']:item['icon']='data:image/png;base64,'+base64.b64encode((dist/item['icon']).read_bytes()).decode()
html=(dist/'index.html').read_text(encoding='utf-8').replace('<link rel="stylesheet" href="styles.css">','<style>'+(dist/'styles.css').read_text(encoding='utf-8')+'</style>')
html=html.replace('<script defer src="data.js"></script>','').replace('<script defer src="app.js"></script>','')
html=html.replace('</body>','<script>window.WIKI_DATA='+json.dumps(embedded).replace('</','<\\/')+';</script><script>'+(dist/'app.js').read_text(encoding='utf-8')+'</script></body>')
map_name=data['meta']['patchedMap'];html=html.replace('href="'+map_name+'"','href="../release/'+map_name+'"')
for file in ['complete-list.md','data.json','validation.json']:html=html.replace('href="'+file+'"','href="dist/'+file+'"')
(c.PROJECT/'item-wiki/Footmen-Frenzy-799X-Item-Wiki.html').write_text(html,encoding='utf-8')
sheet=Image.new('RGB',(800,((len(report)+9)//10)*100),'#182020');draw=ImageDraw.Draw(sheet)
for n,item in enumerate(data['items']):
 im=Image.open(dist/item['icon']).convert('RGBA');im.thumbnail((64,64))
 x=(n%10)*80;y=(n//10)*100;sheet.paste(im,(x+8,y),im);draw.text((x+8,y+68),item['id'],fill='white')
sheet.save(c.ROOT/'wiki-icons-contact-sheet.png')
print(json.dumps(dict(icons=len(report),mapAssets=sum(x['assetSource'].startswith('map:') for x in report),gameAssets=sum(x['assetSource'].startswith('game:') for x in report),uniqueAssets=len(set(x['sha256'] for x in report))),indent=2))
