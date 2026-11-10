"""Capture original feedback and self-contained orb textures from local sources."""
from pathlib import Path
import io, sys, struct, math, random, wave, json
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT.parent / 'mini-foots/tools')]
from mpyq import MPQArchive
from game_data import game_read, chunks
from PIL import Image

BASE_MAP = Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test\Archive\FF799X_Rx_HeroTavern_v1.w3x')
archive = MPQArchive(str(BASE_MAP), listfile=False)
assets = ROOT / 'assets'
feedback = assets / 'Spells/Orianna/Feedback'
feedback.mkdir(parents=True, exist_ok=True)
for name in ['Move.wav', 'Attack.wav', 'Shockwave.wav', 'AttackRing.mdx', 'ShockwaveRing.mdx', 'AttackRingColor.blp', 'ShockwaveRingColor.blp']:
    data = archive.read_file('Spells\\Orianna\\Feedback\\' + name)
    assert data, name
    (feedback / name).write_bytes(data)

def blp(image):
    """Warcraft-compatible paletted BLP1, separate 8-bit alpha, full mip chain."""
    image = image.convert('RGBA')
    width, height = image.size
    palette_image = image.convert('RGB').quantize(colors=256)
    colors = palette_image.getpalette()
    colors += [0] * (768 - len(colors))
    palette = b''.join(bytes([colors[i+2], colors[i+1], colors[i], 255]) for i in range(0,768,3))
    levels = []
    while True:
        indices = image.convert('RGB').quantize(palette=palette_image, dither=Image.Dither.NONE).tobytes()
        levels.append(indices + image.getchannel('A').tobytes())
        if image.size == (1, 1): break
        image = image.resize((max(1, image.width // 2), max(1, image.height // 2)), Image.Resampling.LANCZOS)
    offsets = []; at = 1180
    for level in levels:
        offsets.append(at); at += len(level)
    result = b'BLP1' + struct.pack('<6I', 1, 8, width, height, 5, 0)
    result += struct.pack('<16I', *(offsets + [0] * (16-len(offsets))))
    result += struct.pack('<16I', *([len(v) for v in levels] + [0] * (16-len(levels))))
    result += palette + b''.join(levels)
    assert len(result) == at
    return result

(feedback / 'ProtectRingColor.blp').write_bytes(blp(Image.new('RGBA', (4, 4), (80, 255, 150, 255))))
textures = {}
for filename in ['OrbLightningX.mdx', 'OrbLightX.mdx']:
    data = chunks((ROOT.parent / 'mini-foots/base/files/war3mapImported' / filename).read_bytes())['TEXS']
    for at in range(0, len(data), 268):
        original = data[at+4:at+264].split(b'\0')[0].decode()
        if original in textures: continue
        source = game_read('war3.w3mod:' + original)
        if not source: source = game_read('war3.w3mod:' + original[:-4] + '.dds')
        assert source, original
        name = original.split('\\')[-1]
        destination = assets / 'Spells/Orianna/BallTextures' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(blp(Image.open(io.BytesIO(source))))
        textures[original] = 'Spells\\Orianna\\BallTextures\\' + name
(assets / 'orb-textures.json').write_text(json.dumps(textures, indent=2))

# Original short mono PCM cues; distinct envelopes/pitches for each command phase.
for name, duration, frequency, seed in [('Protect', .6, 520, 10), ('Heal', .7, 880, 11), ('Arrival', .3, 440, 12), ('Windup', .5, 110, 13), ('Return', .4, 700, 14)]:
    rate = 22050; rng = random.Random(seed); samples = []
    for i in range(round(duration*rate)):
        t = i/rate; p = t/duration
        envelope = min(1, t/.015) * ((p+.15)*.8 if name == 'Windup' else (1-p)**2)
        envelope *= min(1, (duration-t)/.015)
        sweep = 1 if name in ('Windup', 'Heal') else -.4
        phase = 2*math.pi*frequency*(t+sweep*t*t/(2*duration))
        tone = .42*math.sin(phase)+.16*math.sin(1.5*phase)+.05*rng.uniform(-1,1)
        samples.append(round(30000*envelope*tone))
    with wave.open(str(feedback / (name+'.wav')), 'wb') as wav:
        wav.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        wav.writeframes(struct.pack('<'+'h'*len(samples), *samples))
print('Captured seven existing feedback assets, ten orb textures and five new cues.')
