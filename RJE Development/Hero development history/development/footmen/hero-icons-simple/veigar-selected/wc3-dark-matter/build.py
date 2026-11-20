from pathlib import Path
import ast,struct,json,shutil,zipfile
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;W=R.parents[2]
source=Path('C:/Users/User/.codex/generated_images/01a18bda-8628-77c2-a7cd-a7838e94d9a3/exec-a74bce1d-0cf7-46dc-b1f4-2f6188a2177b.png')
shutil.copy2(source,R/'Dark-Matter-clean.png')
tree=ast.parse((W/'799x-backport/make_magic_textures.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='blp'],type_ignores=[]),'<blp>','exec'))
im=Image.open(source).convert('RGB').resize((64,64),Image.Resampling.LANCZOS)
standard=W/'799x-backport/tools/button-manager/Button Manager/standard'
preview=Image.new('RGB',(320,190),'#191c23');draw=ImageDraw.Draw(preview)
files=[]
for i,disabled in enumerate([False,True]):
 template=Image.open(standard/('bm_disbtn.tga' if disabled else 'bm_btn.tga')).convert('RGB')
 out=Image.new('RGBA',(64,64));out.putdata([tuple(round(v*b[0]/255) for v in a)+(255,) if b[0]==b[1]==b[2] else b+(255,) for a,b in zip(im.getdata(),template.getdata())])
 name=('DISBTN' if disabled else 'BTN')+'VeigarW'
 path=R/'ReplaceableTextures'/('CommandButtonsDisabled' if disabled else 'CommandButtons')/(name+'.blp');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blp(out))
 decoded=Image.open(path).convert('RGBA');assert decoded.size==(64,64) and decoded.getchannel('A').getextrema()==(255,255)
 data=path.read_bytes();offsets=struct.unpack_from('<16I',data,28);sizes=struct.unpack_from('<16I',data,92)
 assert list(sizes[:7])==[8192,2048,512,128,32,8,2]
 assert all(o+s<=len(data) for o,s in zip(offsets,sizes))
 decoded.save(R/(name+'.png'));preview.paste(decoded.resize((128,128),Image.Resampling.LANCZOS),(16+i*160,12))
 draw.text((16+i*160,145),'Disabled' if disabled else 'Enabled',fill='white');files.append(path)
preview.save(R/'preview.png')
with zipfile.ZipFile(R/'Veigar-Dark-Matter-WC3.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.relative_to(R))
(R/'README.txt').write_text('Dark Matter: 64x64 opaque paletted BLP1, seven mip levels. Standard Button Manager BTN/DISBTN borders. Import using the paths inside the ZIP, matching existing v68 BTNVeigarW references. Not installed in map. Artwork cleanup used built-in image_gen to remove the download overlay; remaining formatting uses the established local button pipeline.\n')
print('Verified enabled and disabled BLP1 files with all seven mip levels.')


