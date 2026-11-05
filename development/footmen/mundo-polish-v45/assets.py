from pathlib import Path
import ast,struct
from PIL import Image,ImageEnhance
R=Path(__file__).resolve().parent; W=R.parent; S=R/'src'
code=ast.parse((W/'799x-backport/make_magic_textures.py').read_text())
exec(compile(ast.Module(body=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='blp'],type_ignores=[]),'blp','exec'))
out=S/'war3mapImported';out.mkdir(exist_ok=True)
(out/'TFWhite.blp').write_bytes(blp(Image.new('RGBA',(8,8),'white')))
im=Image.open(R/'assets/loaded-dice.png').convert('RGBA').resize((64,64),Image.Resampling.LANCZOS)
for name,frame,disabled in [('BTNLoadedDice','bm_btn',False),('DISBTNLoadedDice','bm_disbtn',True)]:
 icon=ImageEnhance.Brightness(im).enhance(.4) if disabled else im.copy()
 border=Image.open(W/f'799x-backport/tools/button-manager/Button Manager/standard/{frame}.tga').convert('RGBA')
 icon.alpha_composite(border)
 path=S/('ReplaceableTextures/CommandButtonsDisabled' if disabled else 'ReplaceableTextures/CommandButtons');path.mkdir(parents=True,exist_ok=True)
 (path/(name+'.blp')).write_bytes(blp(icon));icon.save(R/'assets'/f'{name}.png')
print('Mipmapped dice icons and model texture generated.')
