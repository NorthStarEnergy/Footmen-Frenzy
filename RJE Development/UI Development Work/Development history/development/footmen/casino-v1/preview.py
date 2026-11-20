"""Offline layout preview from actual mocked JASS frame positions and shipped BLP art."""
from pathlib import Path
import copy
import json
import re
import runpy
import struct
from PIL import Image,ImageDraw,ImageFont
from make_panel import main as make_panel

ROOT = Path(__file__).resolve().parent
make_panel()
h = runpy.run_path(str(ROOT/'test_casino.py'))
env,call,reset,frames = (h[k] for k in ('ENV','call','reset','frames'))
poker_frames = copy.deepcopy(frames)
poker_root = h['poker']['PK_Dialog'][0]
reset()
frames.clear()
call('CAS_BuildPlayer',1)
call('CAS_BuildPlayer',2)
call('BJ_Wager',1)
call('BJ_Deal',1)
env['BJ_phase'][1] = 2
env['BJ_turn'][1] = 13
env['BJ_clock'][1] = 20
env['BJ_reveal'][1] = False
env['BJ_dealerCount'][1] = 2
env['BJ_dealerCard'][22] = 7
env['BJ_dealerCard'][23] = 12
h['cards'](12,[12,5])
env['BJ_state'][12] = 1
env['CAS_note'][1] = ''
env['CAS_view'][1] = 1
call('CAS_Render',1)
blackjack = copy.deepcopy(frames)
for player,amount,target in [(1,300,1),(2,150,1),(3,100,2),(4,50,4),(5,200,3),(6,100,3)]:
    env['CAS_amount'][player] = amount
    call('MK_Buy',player,1,target)
env['CAS_amount'][1] = 50
env['MK_tab'][1] = 1
env['MK_pick'][1] = 1
env['CAS_seconds'] = 99
env['CAS_note'][1] = ''
env['CAS_view'][1] = 2
call('CAS_Render',1)
bets = copy.deepcopy(frames)
env['DU_opponent'][1] = 2
env['DU_pick'][1] = 1
call('DU_Offer',1)
env['CAS_view'][1] = 3
call('CAS_Render',1)
duels = copy.deepcopy(frames)
env['CAS_view'][1] = 4
call('CAS_Render',1)
rules = copy.deepcopy(frames)

W,H = 1400,960
FONT = 'C:/Windows/Fonts/segoeui.ttf'
BOLD = str(ROOT/'art/CasinoUI/Bold.ttf')
def font(n,bold=False):
    return ImageFont.truetype(BOLD if bold else FONT,max(10,round(n)))

def texture(path):
    base = ROOT/'art' if path.startswith('CasinoUI') else ROOT.parent/'observer-poker/src'
    raw = (base/path.replace('\\','/')).read_bytes()
    w,h = struct.unpack_from('<II',raw,12)
    offset = struct.unpack_from('<I',raw,28)[0]
    indices = raw[offset:offset+w*h]
    alpha = raw[offset+w*h:offset+2*w*h]
    palette = raw[156:1180]
    return Image.frombytes('RGBA',(w,h),b''.join(bytes((palette[c*4+2],palette[c*4+1],palette[c*4],a)) for c,a in zip(indices,alpha)))

ART = {p.name:texture('PokerUI\\'+p.name) for p in (ROOT.parent/'observer-poker/src/PokerUI').glob('*.blp')}
ART.update({p.name:texture('CasinoUI\\'+p.name) for p in (ROOT/'art/CasinoUI').glob('*.blp')})
def xy(x,y):
    return round(x/.70*W),round(y/.48*H)

def visible(frame,data):
    return data[frame].get('visible',True) and (data[frame]['parent'] not in data or visible(data[frame]['parent'],data))

def text_runs(value):
    color = '#fff6dd'
    for part in re.split(r'(\|c[0-9a-fA-F]{8}|\|r|\|n)',value):
        if part.startswith('|c'):
            color = '#'+part[4:]
        elif part == '|r':
            color = '#fff6dd'
        elif part == '|n':
            yield '\n',color
        else:
            yield part,color

def render(data,title,root=None):
    root = root or env['CAS_root'][1]
    im = ART[data[root].get('texture','PokerUI\\table.blp').split('\\')[-1]].resize((W,H),Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(im)
    def inside(frame):
        return frame == root or (data[frame]['parent'] in data and inside(data[frame]['parent']))
    def geometry(frame):
        if frame == root:
            return 0,0,W,H
        f = data[frame]
        if 'allpoints' in f:
            return geometry(f['allpoints'])
        point = f.get('point')
        if not point:
            return 0,0,0,0
        px,py,_,_ = geometry(f['parent'])
        x,y = xy(point[-2],-point[-1])
        width,height = xy(*f.get('size',(0.1,0.02)))
        return px+x,py+y,width,height
    for frame,f in data.items():
        if frame == root or not inside(frame) or not visible(frame,data):
            continue
        x,y,width,height = geometry(frame)
        if f['kind'] == 'BACKDROP':
            path = f.get('texture','')
            if path.startswith(('PokerUI','CasinoUI')):
                asset = ART[path.split('\\')[-1]].resize((width,height),Image.Resampling.LANCZOS)
                im.alpha_composite(asset,(x,y))
                draw = ImageDraw.Draw(im)
            else:
                color = f.get('color',(255,30,55,49))[1:]
                draw.rectangle((x,y,x+width,y+height),fill=color)
        elif f['kind'] == 'GLUETEXTBUTTON':
            enabled = f.get('enabled',True)
            draw.rounded_rectangle((x,y,x+width,y+height),7,fill='#244b49' if enabled else '#233632',outline='#9d8e65' if enabled else '#4b5b50',width=2)
            draw.text((x+width/2,y+height/2),f.get('text',''),font=font(20,True),fill='#fff3d5' if enabled else '#81958d',anchor='mm')
        elif f['kind'] == 'TEXT':
            height_units = f.get('font',('',0.011,0))[1]
            ft = font(height_units*2000*f.get('scale',1),True)
            if f.get('align') == (3,4):
                color = f.get('textcolor',(255,255,250,240))[1:]
                draw.text((x+width/2,y+height/2),f.get('text',''),font=ft,fill=color,anchor='mm')
                continue
            cx,cy = x,y
            for run,color in text_runs(str(f.get('text',''))):
                if run == '\n':
                    cx,cy = x,cy+round(ft.size*1.25)
                    continue
                for word in re.split(r'(\s+)',run):
                    length = draw.textlength(word,font=ft)
                    if cx+length > x+width and cx > x:
                        cx,cy = x,cy+round(ft.size*1.25)
                    draw.text((cx,cy),word,font=ft,fill=color)
                    cx += length
    # Clearly separate the approximation from an engine screenshot.
    draw.text((W-22,H-12),'OFFLINE LAYOUT PREVIEW',font=font(13),fill='#8da79e',anchor='rd')
    im.save(ROOT/(title+'.png'))
    return im

previews = {}
for name,data in [('blackjack-preview',blackjack),('betting-preview',bets),('challenges-preview',duels),('rules-preview',rules)]:
    previews[name] = render(data,name)
previews['poker-preview'] = render(poker_frames,'poker-preview',poker_root)
overview = Image.new('RGB',(1800,660),'#101d29')
overview_draw = ImageDraw.Draw(overview)
for x,title,name in [(12,'BLACKJACK','blackjack-preview'),(912,'MATCH BETTING','betting-preview')]:
    overview_draw.text((x+8,12),title,font=font(20,True),fill='#e7cb88')
    overview.paste(previews[name].convert('RGB').resize((875,600),Image.Resampling.LANCZOS),(x,48))
overview.save(ROOT/'casino-preview.png')
print('Rendered four previews from actual JASS frame layouts.')
