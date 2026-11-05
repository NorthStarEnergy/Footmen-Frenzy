from pathlib import Path
import sys,struct,re,json,ctypes as c,shutil,subprocess,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive
B=R/'base';O=R/'src'
for d in [B,O,R/'release']:d.mkdir(exist_ok=True)
shutil.copyfile(W/'ffa-v16/release/Solo_Foots_8P_FFA_v16.w3x',R/'baseline.w3x');archive.extract(R/'baseline.w3x',B)
s=(B/'war3map.j').read_text();pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
q=Obj(B/'war3map.w3q',True);old=next(m[4] for m in q.find('R009')['mods'] if m[0]==b'gglb');assert old==300
q.set('R009','gglb',250);q.save(O/'war3map.w3q')
title='Solo Foots 8P FFA + King v17';s=re.sub(r'call SetMapName\("[^\"]+"\)',f'call SetMapName("{title}")',s)
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):];tail=tail[:tail.index('# Terrain-derived BLP1 minimaps')]+tail[tail.index('work=Path('):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v17.w3x').replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','')
report={'overdrive_research_old':old,'overdrive_research_new':250};exec(tail)
q=Obj(R/'roundtrip/war3map.w3q',True);assert next(m[4] for m in q.find('R009')['mods'] if m[0]==b'gglb')==250
assert funcs((R/'roundtrip/war3map.j').read_text())['Trig_BASE__Overdrive_Start_Actions']==funcs((B/'war3map.j').read_text())['Trig_BASE__Overdrive_Start_Actions']
