from pathlib import Path
import sys,json,shutil,hashlib
sys.path.insert(0,'tools')
from map_archive import Archive
root=Path('.'); work=root/'build/799x-ui-t43'; project=work/'projects/799x'; src=project/'src'
src.mkdir(parents=True,exist_ok=True); (project/'release').mkdir(exist_ok=True); (work/'tools').mkdir(exist_ok=True)
for f in ['Build-Map.ps1','tools.local.json']: shutil.copy2(root/f,work/f)
for f in ['build_map.py','map_archive.py','Install-Wc3Map.ps1']: shutil.copy2(root/'tools'/f,work/'tools'/f)
old=Path.home()/'Documents/Warcraft III/Maps/Tests/799X/Reforged_Footmen_Frenzy_v7.9.9X-T42.w3x'
shutil.copy2(old,project/'release'/old.name)
meta=dict(map_type='799X',branch='Footmen-Frenzy-12p',release=old.name,sha256=hashlib.sha256(old.read_bytes()).hexdigest())
(project/'project.json').write_text(json.dumps(meta,indent=2))
cfg=json.loads((root/'tools.local.json').read_text())
with Archive(cfg['stormlib'],old) as a:
 for name in ['war3map.j','war3map.wts','war3map.w3i']: (src/name).write_bytes(a.read(name))
s=(src/'war3map.j').read_bytes().decode(); nl='\r\n' if '\r\n' in s else '\n';s=s.replace('\r\n','\n')
s=s.replace('globals\n','''globals
    framehandle FFUI_Root = null
    framehandle FFUI_Toggle = null
    framehandle FFUI_Items = null
    framehandle FFUI_ItemsButton = null
    boolean FFUI_Hidden = false
    boolean FFUI_ItemsOpen = false
''',1)
helper='''
// All custom controls share a parent; hiding it also hides refreshed children.
function FFUI_GetRoot takes nothing returns framehandle
    if FFUI_Root == null then
        set FFUI_Root = BlzCreateFrameByType("FRAME", "FFUI_Root", BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0), "", 0)
        call BlzFrameSetAllPoints(FFUI_Root, BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0))
    endif
    return FFUI_Root
endfunction
'''
s=s.replace('\nendglobals\n','\nendglobals\n'+helper,1)
# Reparent every custom frame created directly under the game UI.
import re
s,n=re.subn(r'(local framehandle (?:ui|gameUI)\s*=\s*)BlzGetOriginFrame\(ORIGIN_FRAME_GAME_UI, 0\)',r'\1FFUI_GetRoot()',s)
assert n==2,n
s=s.replace('"FFSlotKey",ui,','"FFSlotKey",ui,')
s=s.replace('FRAMEPOINT_TOP, -0.039, 0.004','FRAMEPOINT_TOP, -0.039, -0.004')
s=s.replace('FRAMEPOINT_TOP, 0.039, 0.004','FRAMEPOINT_TOP, 0.037, -0.004')
# Opening either existing page closes Items.
s=s.replace('        set DPS_Open[p] = not DPS_Open[p]','        set FFUI_ItemsOpen = false\n        call BlzFrameSetVisible(FFUI_Items, false)\n        set DPS_Open[p] = not DPS_Open[p]',1)
s=s.replace('            set spellKeysOpen = clicked == spellKeysToggle and not spellKeysOpen','            set FFUI_ItemsOpen = false\n            if FFUI_Items != null then\n                call BlzFrameSetVisible(FFUI_Items, false)\n            endif\n            set spellKeysOpen = clicked == spellKeysToggle and not spellKeysOpen',1)
new='''function FFUI_Click takes nothing returns nothing
    local framehandle clicked = BlzGetTriggerFrame()
    if GetLocalPlayer() == GetTriggerPlayer() then
        if clicked == FFUI_Toggle then
            set FFUI_Hidden = not FFUI_Hidden
            set spellKeysEditing = -1
            call BlzFrameSetVisible(FFUI_Root, not FFUI_Hidden)
            if FFUI_Hidden then
                call BlzFrameSetText(FFUI_Toggle, "|cff00ff00X|r")
            else
                call BlzFrameSetText(FFUI_Toggle, "|cffff0000X|r")
            endif
        else
            set FFUI_ItemsOpen = clicked == FFUI_ItemsButton and not FFUI_ItemsOpen
            set DPS_Open[GetPlayerId(GetLocalPlayer())] = false
            call BlzFrameSetVisible(DPS_Panel, false)
            set spellKeysOpen = false
            set spellKeysEditing = -1
            call SpellKeysRefresh()
            call BlzFrameSetVisible(FFUI_Items, FFUI_ItemsOpen)
        endif
        call BlzFrameSetEnable(clicked, false)
        call BlzFrameSetEnable(clicked, true)
        call BlzFrameSetFocus(clicked, false)
    endif
    set clicked = null
endfunction

function FFUI_Create takes nothing returns nothing
    local trigger click = CreateTrigger()
    local framehandle f
    set FFUI_ItemsButton = BlzCreateFrame("ScriptDialogButton", FFUI_Root, 0, 0)
    call BlzFrameSetSize(FFUI_ItemsButton, 0.073, 0.028)
    call BlzFrameSetPoint(FFUI_ItemsButton, FRAMEPOINT_LEFT, spellKeysToggle, FRAMEPOINT_RIGHT, 0.003, 0)
    call BlzFrameSetText(FFUI_ItemsButton, "Items")
    call BlzFrameSetLevel(FFUI_ItemsButton, 20)
    set FFUI_Toggle = BlzCreateFrame("ScriptDialogButton", BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0), 0, 0)
    call BlzFrameSetSize(FFUI_Toggle, 0.028, 0.028)
    call BlzFrameSetPoint(FFUI_Toggle, FRAMEPOINT_BOTTOM, BlzGetOriginFrame(ORIGIN_FRAME_MINIMAP, 0), FRAMEPOINT_TOP, 0.1665, -0.004)
    call BlzFrameSetText(FFUI_Toggle, "|cffff0000X|r")
    call BlzFrameSetLevel(FFUI_Toggle, 22)
    set FFUI_Items = BlzCreateFrame("EscMenuBackdrop", FFUI_Root, 0, 0)
    call BlzFrameSetSize(FFUI_Items, 0.414, 0.300)
    call BlzFrameSetAbsPoint(FFUI_Items, FRAMEPOINT_CENTER, 0.400, 0.348)
    call BlzFrameSetLevel(FFUI_Items, 21)
    set f = BlzCreateFrameByType("TEXT", "FFUI_ItemsTitle", FFUI_Items, "", 0)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPLEFT, FFUI_Items, FRAMEPOINT_TOPLEFT, 0.020, -0.018)
    call BlzFrameSetText(f, "|cffffcc00Items|r")
    set f = BlzCreateFrame("ScriptDialogButton", FFUI_Items, 0, 0)
    call BlzFrameSetSize(f, 0.061, 0.025)
    call BlzFrameSetPoint(f, FRAMEPOINT_TOPRIGHT, FFUI_Items, FRAMEPOINT_TOPRIGHT, -0.018, -0.013)
    call BlzFrameSetText(f, "Close")
    call BlzTriggerRegisterFrameEvent(click, f, FRAMEEVENT_CONTROL_CLICK)
    call BlzTriggerRegisterFrameEvent(click, FFUI_ItemsButton, FRAMEEVENT_CONTROL_CLICK)
    call BlzTriggerRegisterFrameEvent(click, FFUI_Toggle, FRAMEEVENT_CONTROL_CLICK)
    call TriggerAddAction(click, function FFUI_Click)
    call BlzFrameSetVisible(FFUI_Items, false)
    set f = null
    set click = null
endfunction

'''
s=s.replace('function DPS_Create takes',new+'function DPS_Create takes',1)
# SpellKeys init precedes DPS_Create in runtime; create new toolbar after Stats.
start=s.index('function DPS_Create takes');end=s.index('endfunction',start)
s=s[:end]+'    call FFUI_Create()\n'+s[end:]
s=s.replace('7.9.9X-T42','7.9.9X-T43')
(src/'war3map.j').write_bytes(s.replace('\n',nl).encode())
for name in ['war3map.wts','war3map.w3i']:
 p=src/name;p.write_bytes(p.read_bytes().replace(b'7.9.9X-T42',b'7.9.9X-T43'))
print('Prepared T43 from full T42 baseline; custom roots:',n)


