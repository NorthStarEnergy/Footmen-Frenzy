from pathlib import Path
import sys,struct,re,json,ctypes as c,shutil,subprocess,hashlib,io
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),str(W/'.audit-deps'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive,mpyq
B=R/'base';O=R/'src'
for folder in [B,O,R/'release']:folder.mkdir(parents=True,exist_ok=True)
shutil.copyfile(W/'ffa-v10/release/Solo_Foots_8P_FFA_v10.w3x',R/'baseline.w3x')
archive.extract(R/'baseline.w3x',B)
donor=Path(r'C:\Users\User\OneDrive\Documents\Warcraft III\Maps\Test\FF799X_Rx_Stalker_v71.w3x')
blob=donor.read_bytes();mpq=mpyq.MPQArchive(io.BytesIO(blob[512:] if blob[:4]==b'HM3W' else blob),listfile=False)
ds=mpq.read_file('war3map.j').decode('utf-8-sig');(R/'donor.j').write_text(ds)
s=(B/'war3map.j').read_text();pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
def put(n,t):
 global s
 s=s.replace(funcs(s)[n],t)
df=funcs(ds)
track={'FF_st_Slot','FF_st_OnSpell','FF_st_TmDrop','FF_st_OnDeath','FF_st_TmExpire'}
selected={n for n in df if n.startswith(('zoom_','DPS_')) or n=='InitTrig_Camera_Zoom'}|track
for n,f in list(funcs(s).items()):
 if n.startswith('zoom_') or n=='InitTrig_Camera_Zoom':s=s.replace(f,'')
gbend=re.search(r'^endglobals',s,re.M).start()
globalsblock=s[:gbend];globalsblock='\n'.join(line for line in globalsblock.splitlines() if not re.search(r'\bzoom_\w+',line))+'\n';s=globalsblock+s[gbend:]
for n in selected:s+='\n'+df[n]+'\n'
# Self-contained stat counters: no telemetry exporter or observer substitution dependency.
put('FF_st_Slot','''function FF_st_Slot takes player p returns integer
    local integer pn=GetPlayerId(p)+1
    if pn>=1 and pn<=12 then
        if F8_Team[pn-1]>0 and F8_Participant[pn] then
            return pn
        endif
    endif
    return 0
endfunction''')
f=funcs(s)['FF_st_OnDeath'];a=f.index('    // Denies:');b=f.index('    set victim = null',a);put('FF_st_OnDeath',f[:a]+f[b:])
# Import only the globals referenced by the actual imported UI/tracking functions.
def globals_of(t):
 out={}
 for line in t[t.index('globals')+7:re.search(r'^endglobals',t,re.M).start()].splitlines():
  m=re.match(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)\s*(?:=.*)?$',line.split('//')[0])
  if m:out[m[1]]=line
 return out
dg=globals_of(ds);sg=globals_of(s);refs=set(re.findall(r'\b\w+\b','\n'.join(funcs(s)[n] for n in selected)))
needed=(refs&dg.keys())-sg.keys()
assert all(n.startswith(('zoom_','DPS_','FF_st_','FF_ST_')) or n=='FF_gameTimer' for n in needed),needed
s=re.sub(r'^endglobals',lambda m:'\n'.join(dg[n] for n in sorted(needed))+'\nendglobals',s,count=1,flags=re.M)
s=re.sub(r'\bFF_gameTimer\b','DPS_Clock',s)
# Exactly eight visible rows, in the same order as the FFA/King scoreboard.
f=funcs(s)['DPS_Create'].replace('0.650, 0.393','0.650, 0.295').replace('    local integer s = 1','    local integer s')
f=f.replace('        exitwhen s > 12','        exitwhen row >= 8\n        set s=F8_Slot[row+1]+1')
f=f.replace('0.072 + I2R(row) * 0.022 + I2R(row / 3) * 0.003','0.072 + I2R(row) * 0.024')
f=f.replace('        set s = s + 1','')
f=f.replace('    set f = DPS_Text("DPS_Player"','    set f = DPS_Text("DPS_Title",0.026,0.016,0.52,"|cffffcc00Player stats|r   K/D: units   HK/HD: heroes")\n    set f = DPS_Text("DPS_Player"')
put('DPS_Create',f)
f=funcs(s)['DPS_Refresh'].replace('    local integer s = 1','    local integer s\n    local integer row=1').replace('        exitwhen s > 12','        exitwhen row > 8\n        set s=F8_Slot[row]+1').replace('        set s = s + 1','        set row=row+1')
f=f.replace('    loop\n','    call FF_st_TmExpire()\n    loop\n',1);put('DPS_Refresh',f)
# Resolve assists for every roster slot, allowing kingdom allies but never observers.
f=funcs(s)['DPS_OnDeath'].replace('if s != ks and IsPlayerAlly','if F8_Team[s-1]>0 and F8_Participant[s] and s != ks and IsPlayerAlly')
put('DPS_OnDeath',f)
# A monotonic timer is independent of the startup mode-selection clock reset.
f=funcs(s)['DPS_Init'].replace('    set DPS_Damage = InitHashtable()','    set DPS_Damage = InitHashtable()\n    set DPS_Clock=CreateTimer()\n    call TimerStart(DPS_Clock,1000000.,false,null)')
f=f.replace('    set DPS_Timer = CreateTimer()', '''    call TriggerAddAction(t, function FF_st_OnDeath)
    set t=CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SPELL_EFFECT)
    call TriggerAddAction(t,function FF_st_OnSpell)
    set DPS_Timer = CreateTimer()''')
put('DPS_Init',f)
main=funcs(s)['main'].replace('    call InitCustomTriggers()','    call DPS_Init()\n    call InitCustomTriggers()');put('main',main)
# Count hill captures at ownership assignment, separately from King-mode base captures.
f=funcs(s)['Trig_KOTH_Hill_Dies_Actions'].replace('        set udg_KOTH_Player=GetOwningPlayer(GetKillingUnitBJ())','''        set udg_KOTH_Player=GetOwningPlayer(GetKillingUnitBJ())
        if FF_st_Slot(udg_KOTH_Player)>0 then
            set DPS_Caps[GetConvertedPlayerId(udg_KOTH_Player)]=DPS_Caps[GetConvertedPlayerId(udg_KOTH_Player)]+1
        endif''');put('Trig_KOTH_Hill_Dies_Actions',f)
# Camera restores also refresh the slider and numeric label once frames exist.
f=funcs(s)['zoom__RestoreFromFile'].replace('        call zoom__Zoom(cameraDistance , false)','''        set cameraDistance=zoom__Zoom(cameraDistance , false)
        if zoom__slider!=null then
            call BlzFrameSetValue(zoom__slider,I2R(cameraDistance))
            call zoom__UpdateSliderLabel(cameraDistance)
        endif''');put('zoom__RestoreFromFile',f)
# Copy the actual donor's TOC/FDF payloads and register all of them in the import table.
assets=['MiniFootsUI.toc','MiniFootsUI.fdf',r'war3mapImported\templates.toc']
for name in assets:
 data=mpq.read_file(name);assert data is not None,name
 out=O/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
imp=(B/'war3map.imp').read_bytes();ver,count=struct.unpack_from('<II',imp);at=8;registered=set()
while at<len(imp):
 end=imp.index(0,at+1);registered.add(imp[at+1:end].decode().lower());at=end+1
new=[p for p in assets if p.lower() not in registered]
(O/'war3map.imp').write_bytes(struct.pack('<II',ver,count+len(new))+imp[8:]+b''.join(bytes([13])+p.encode()+b'\0' for p in new))
title='Solo Foots 8P FFA + King v11';s=re.sub(r'call SetMapName\("[^\"]+"\)',f'call SetMapName("{title}")',s)
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
exec((R/'shops.py').read_text())
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):]
tail=tail[:tail.index('# Terrain-derived BLP1 minimaps')]+tail[tail.index('work=Path('):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v11.w3x')
tail=tail.replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','ui_functions=len(selected),')
report={'donor':str(donor),'donor_sha256':hashlib.sha256(blob).hexdigest(),'ui_assets':assets};exec(tail)
