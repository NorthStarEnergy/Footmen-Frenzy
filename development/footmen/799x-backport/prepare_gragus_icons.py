from pathlib import Path
import ast,struct
from PIL import Image,ImageEnhance
ROOT=Path(__file__).resolve().parent
# Reuse the BLP encoder without running the ground texture generator.
tree=ast.parse((ROOT/'make_magic_textures.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='blp'],type_ignores=[]),'<blp>','exec'))
for name in ['Barrel','Fortitude','Slam','Cask']:
    source=ROOT.parent/'mini-foots/audit/pre-orianna-v3/files/ReplaceableTextures/CommandButtons'/('BTNRxGragas'+name+'.blp')
    if name in ['Fortitude','Slam']:source=ROOT.parent/'mini-foots/src/ReplaceableTextures/CommandButtons'/source.name
    im=Image.open(source).convert('RGBA');im.putalpha(255)
    for disabled in [False,True]:
        folder='CommandButtonsDisabled' if disabled else 'CommandButtons'
        filename=('DISBTN' if disabled else 'BTN')+'RxGragas'+name+'.blp'
        dest=ROOT/'assets/ReplaceableTextures'/folder/filename;dest.parent.mkdir(parents=True,exist_ok=True)
        out=ImageEnhance.Brightness(im).enhance(.4) if disabled else im
        dest.write_bytes(blp(out))
        assert Image.open(dest).size==(64,64) and dest.read_bytes()[:4]==b'BLP1'
print('Eight Gragus icons encoded as opaque BLP1 with mipmaps.')
