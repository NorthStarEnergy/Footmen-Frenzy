from PIL import Image,ImageEnhance,ImageDraw
art=O/'artwork';art.mkdir(exist_ok=True)
sources={'Q':'exec-cc8fbdd8-a46d-48a3-b22d-597c74162365.png','W':'exec-e3e3dfb5-cfff-4920-8ec9-e518e06cf63c.png','E':'exec-b5ae50bb-17b8-4830-a45b-d8d3bd469f7c.png','R':'exec-8044195e-402f-4f08-987c-095f9a713d9d.png','Hero':'exec-ca36d3f3-c818-419f-aeb9-6470dc1ad957.png'}
generated=Path(r'C:\Users\Ryan1\.codex\generated_images\01a18bc7-b2ab-7fe1-90b5-76996f3b49a7')
def encode(im,path):
 im=im.convert('RGB');pal=im.quantize(colors=256);rgb=pal.getpalette();palette=b''.join(bytes((rgb[i+2],rgb[i+1],rgb[i],255)) for i in range(0,768,3))
 levels=[im.resize((z,z),Image.Resampling.LANCZOS).quantize(palette=pal,dither=Image.Dither.NONE).tobytes() for z in [64,32,16,8,4,2,1]]
 offsets=[];pos=1180
 for data in levels:offsets.append(pos);pos+=len(data)
 data=b'BLP1'+struct.pack('<6I',1,0,64,64,5,1)+struct.pack('<16I',*(offsets+[0]*9))+struct.pack('<16I',*([len(z) for z in levels]+[0]*9))+palette+b''.join(levels)
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 check=Image.open(path);check.load();assert check.size==(64,64)
 return check.convert('RGB')
def bordered(source,disabled=False,passive=False):
 im=Image.new('RGB',(64,64),'black');im.paste(source.resize((56,56),Image.Resampling.LANCZOS),(4,4));d=ImageDraw.Draw(im)
 # WC3-sized square beveled button rim; opaque corners prevent green missing icons.
 colors=[(12,12,16),(170,172,180),(88,90,103),(34,32,47)] if not passive else [(8,8,12),(80,72,98),(42,36,60),(16,14,24)]
 for n,c in enumerate(colors):
  d.line([(n,63-n),(n,n),(63-n,n)],fill=c)
  d.line([(63-n,n),(63-n,63-n),(n,63-n)],fill=tuple(int(v*.45) for v in c))
 if disabled:im=ImageEnhance.Color(im).enhance(.3);im=ImageEnhance.Brightness(im).enhance(.28)
 return im
preview=Image.new('RGB',(600,300),(19,17,25));d=ImageDraw.Draw(preview)
for i,(name,filename) in enumerate(sources.items()):
 shutil.copy2(generated/filename,art/(name+'.png'));im=Image.open(art/(name+'.png')).convert('RGB')
 for disabled in [False,True]:
  path=icons[name] if not disabled else icons[name].replace('CommandButtons\\BTN','CommandButtonsDisabled\\DISBTN')
  decoded=encode(bordered(im,disabled),E/path)
  preview.paste(decoded.resize((96,96),Image.Resampling.NEAREST),(i*120+12,30+int(disabled)*130))
 d.text((i*120+12,8),name,fill='white')
im=Image.open(art/'Hero.png').convert('RGB')
encode(bordered(im,passive=True),E/'ReplaceableTextures/PassiveButtons/PASVeigarHero.blp')
encode(bordered(im,disabled=True,passive=True),E/'ReplaceableTextures/CommandButtonsDisabled/DISPASVeigarHero.blp')
preview.save(O/'ICON_PREVIEW.png')
