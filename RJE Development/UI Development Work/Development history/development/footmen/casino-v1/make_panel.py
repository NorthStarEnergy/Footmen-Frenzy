"""Package a plain casino panel with the existing artwork's border palette."""
from pathlib import Path
import struct
from PIL import Image,ImageDraw

ROOT = Path(__file__).resolve().parent

def blp(image):
    width,height = image.size
    pal = image.convert('RGB').quantize(colors=256)
    colors = pal.getpalette()
    colors += [0]*(768-len(colors))
    palette = b''.join(bytes([colors[i+2],colors[i+1],colors[i],255]) for i in range(0,768,3))
    levels = []
    while True:
        levels.append(image.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).tobytes()+image.getchannel('A').tobytes())
        if image.size == (1,1):
            break
        image = image.resize((max(1,image.width//2),max(1,image.height//2)),Image.Resampling.LANCZOS)
    offsets = []
    at = 1180
    for level in levels:
        offsets.append(at)
        at += len(level)
    return b'BLP1'+struct.pack('<6I',1,8,width,height,5,0)+struct.pack('<16I',*(offsets+[0]*(16-len(offsets))))+struct.pack('<16I',*([len(level) for level in levels]+[0]*(16-len(levels))))+palette+b''.join(levels)

def main():
    image = Image.new('RGBA',(1024,1024))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((4,4,1019,1019),40,fill='#14232d',outline='#b19b64',width=4)
    draw.line((72,220,952,220),fill='#30454c',width=2)
    draw.line((72,812,952,812),fill='#30454c',width=2)
    out = ROOT/'art/CasinoUI/panel.blp'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(blp(image))
    colors = ['#455460','#b03c49','#24764b','#83c49a','#306a8a','#b5914e','#26333e']
    borders = ['#788996','#dc7983','#55ad7a','#b2e3c2','#6b9fbd','#e0c282','#455360']
    for tone,(color,border) in enumerate(zip(colors,borders)):
        button = Image.new('RGBA',(256,64))
        button_draw = ImageDraw.Draw(button)
        button_draw.rounded_rectangle((1,1,254,62),9,fill=color,outline=border,width=2)
        (out.parent/('button'+str(tone)+'.blp')).write_bytes(blp(button))

if __name__ == '__main__':
    main()
