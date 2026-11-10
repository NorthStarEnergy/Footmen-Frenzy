"""Apply Button Manager 1.8.2 standard templates using its documented shading rules."""
from pathlib import Path
import ast,struct,json
from PIL import Image,ImageEnhance,ImageDraw
ROOT=Path(__file__).resolve().parent
tree=ast.parse((ROOT/'make_magic_textures.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='blp'],type_ignores=[]),'<blp>','exec'))

def build_icons(out):
    originals=ROOT/'icon-sources/existing';originals.mkdir(exist_ok=True)
    names=['RxOriannaMove','RxOriannaAttackRed','RxOriannaProtect','RxOriannaShockwave','RxGragasBarrel','RxGragasFortitude','RxGragasSlam','RxGragasCask']
    standard=ROOT/'tools/button-manager/Button Manager/standard'
    templates={False:Image.open(standard/'bm_btn.tga').convert('RGB'),True:Image.open(standard/'bm_disbtn.tga').convert('RGB')}
    preview=Image.new('RGB',(4*192,3*220),'#17191d');draw=ImageDraw.Draw(preview)
    rows=[]
    for name in names:
        p=originals/(name+'.png')
        if not p.exists():
            Image.open(out/'ReplaceableTextures/CommandButtons'/('BTN'+name+'.blp')).convert('RGBA').save(p)
        image=Image.open(p).convert("RGBA").resize((64,64),Image.Resampling.LANCZOS)
        rows.append((name,image))
    for name in ['TimeWarp','ForceField','Lantern','GuardianShield']:
        image=Image.open(ROOT/'icon-sources'/(name+'.png')).convert('RGBA')
        # Remove the generated frame completely before applying the actual WC3 border.
        w,h=image.size
        image=image.crop((round(w*.10),round(h*.10),round(w*.90),round(h*.90)))
        rows.append(('Guardian'+name,image.resize((64,64),Image.Resampling.LANCZOS)))
    for index,(name,image) in enumerate(rows):
        image.putalpha(255)
        for disabled in [False,True]:
            folder='CommandButtonsDisabled' if disabled else 'CommandButtons'
            p=out/'ReplaceableTextures'/folder/(('DISBTN' if disabled else 'BTN')+name+'.blp')
            p.parent.mkdir(parents=True,exist_ok=True)
            rendered=Image.new('RGBA',(64,64))
            pixels=[]
            for source,border in zip(image.getdata(),templates[disabled].getdata()):
                if border[0]==border[1]==border[2]:
                    pixels.append(tuple(round(c*border[0]/255) for c in source[:3])+(255,))
                else:
                    pixels.append(border+(255,))
            rendered.putdata(pixels)
            if not disabled: active=rendered.copy()
            p.write_bytes(blp(rendered))
            assert Image.open(p).convert('RGBA').getchannel('A').getextrema()==(255,255)
        x=(index%4)*192;y=(index//4)*220
        preview.paste(active.resize((192,192),Image.Resampling.NEAREST),(x,y));draw.text((x,y+195),name,fill='white')
    preview.save(ROOT/'audit/ability-buttons-wc3-default.png')
    (ROOT/'icon-sources/border-provenance.txt').write_text('Standard bm_btn.tga and bm_disbtn.tga from Shadow Daemon Button Manager v1.8.2, downloaded from https://www.hiveworkshop.com/threads/button-manager-v1-8-2.116280/ . Applied documented equal-RGB shading rule; default Shading=100. Guardian custom frames cropped away. Opaque BLP1 with mipmaps.\n')
