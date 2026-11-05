from pathlib import Path
import sys,struct,re,json,ctypes as c,shutil,subprocess,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive
B=R/'base';O=R/'src'
for d in [B,O,R/'release']:d.mkdir(exist_ok=True)
shutil.copyfile(W/'ffa-v12/release/Solo_Foots_8P_FFA_v12.w3x',R/'baseline.w3x');archive.extract(R/'baseline.w3x',B)
s=(B/'war3map.j').read_text();pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
def put(n,f):
 global s
 s=s.replace(funcs(s)[n],f)
changes=[]
for filename in ['war3map.w3a','war3mapSkin.w3a']:
 a=Obj(B/filename,True)
 for table in a.tables:
  for obj in table:
   # Native sustained area channels, including custom derivatives.
   if obj['old'] not in [b'AOeq',b'AUdd',b'ANvc',b'AHbz',b'ANrf',b'ANcs',b'ANhs']:continue
   for m in obj['mods']:
    if m[0]==b'aran' and m[4]>600:
     changes.append([filename,(obj['new'] if obj['new']!=bytes(4) else obj['old']).decode(),m[2],m[4],600]);m[4]=600.0
 a.save(O/filename)
f=funcs(s)['SKBoard'].replace('set status="King"','set status="King / Ready"').replace('set status="Vassal: ready"','set status="Vassal / Ready"').replace('set status="Used"','set status="King / Used"\n                if king!=pn then\n                    set status="Vassal / Used"\n                endif').replace('set status="Left"','set status="Eliminated"\n            if GetPlayerSlotState(Player(pn-1))!=PLAYER_SLOT_STATE_PLAYING then\n                set status="Left"\n            endif\n            if not F8_Participant[pn] then\n                set status="Empty"\n            endif')
put('SKBoard',f)
f=funcs(s)['SKCreateBoard'].replace('6, 1, "Defect"','6, 1, "Status / Defect"').replace('            set col=col+1','            if col==6 then\n                call MultiboardSetItemWidthBJ(udg_multiboard_kills,col,row,12.0)\n            endif\n            set col=col+1');put('SKCreateBoard',f)
f=funcs(s)['F8_UpdateBoard'].replace('    local integer p','    local integer p\n    local string label',1).replace('        call MultiboardSetItemValueBJ(udg_multiboard_kills,1,row+1,GetPlayerName(Player(p-1)))','''        set label=GetPlayerName(Player(p-1))
        if not udg_player_active[p] then
            set label=label+" [Dead]"
            if not F8_Participant[p] then
                set label="[Empty]"
            elseif GetPlayerSlotState(Player(p-1))!=PLAYER_SLOT_STATE_PLAYING then
                set label=GetPlayerName(Player(p-1))+" [Left]"
            endif
        endif
        call MultiboardSetItemValueBJ(udg_multiboard_kills,1,row+1,label)''');put('F8_UpdateBoard',f)
title='Solo Foots 8P FFA + King v13';s=re.sub(r'call SetMapName\("[^\"]+"\)',f'call SetMapName("{title}")',s)
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):];tail=tail[:tail.index('# Terrain-derived BLP1 minimaps')]+tail[tail.index('work=Path('):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v13.w3x').replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','')
report={'channel_range_changes':changes};exec(tail)
