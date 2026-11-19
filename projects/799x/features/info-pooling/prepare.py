"""Apply the Info and pooling UI to the 799X script and editor source."""
from pathlib import Path

POOLING = Path(__file__).with_name('pooling.j')


def patch_globals(data):
    newline = b'\r\n' if b'\r\n' in data else b'\n'
    declare = [
        *(f'framehandle FFPool{name}' for name in
          ('Panel', 'Title', 'Recipient', 'ReserveButton', 'CloseButton')),
        'boolean array FFPoolOpen',
        'integer array FFPoolTarget',
        'integer array FFPoolReserve',
    ]
    anchor = b'    framehandle DPS_PageButton'
    if data.count(anchor) != 1:
        raise ValueError('Missing unique 799X Info globals anchor')
    prefix = b''.join(b'    ' + line.encode() + newline for line in declare)
    return data.replace(anchor, prefix + anchor, 1)


def patch_functions(data):
    newline = b'\r\n' if b'\r\n' in data else b'\n'
    script = data.replace(b'\r\n', b'\n')
    start = script.index(b'function F3_SendAllGold_Callback ')
    end = script.index(b'function Trig_Clear_Text_Setup_Actions ', start)
    pool = POOLING.read_bytes().replace(b'\r\n', b'\n').rstrip()
    script = script[:start] + pool + b'\n\n\n' + script[end:]

    edits = (
        (b'            call BlzTriggerRegisterPlayerKeyEvent(t, Player(i), OSKEY_F2, 0, false)\n', b''),
        (b'call F3_SendAllGold_Init()', b'call FFPoolInit()'),
        (b'DPS_Button, "Profile"', b'DPS_Button, "Info"'),
        (b'DPS_PageButton, "My Profile"', b'DPS_PageButton, "Profile"'),
        (b'DPS_PageButton, FRAMEPOINT_TOPRIGHT, DPS_Panel, FRAMEPOINT_TOPRIGHT, -0.060',
         b'DPS_PageButton, FRAMEPOINT_TOPLEFT, DPS_Panel, FRAMEPOINT_TOPLEFT, 0.050'),
        (b'DPS_PageButton, 0.084, 0.022', b'DPS_PageButton, 0.110, 0.026'),
        (b'"Skins", 0.305', b'"Skins", 0.170'),
        (b'"Hotkeys", 0.050', b'"Hotkeys", 0.290'),
        (b'CatalogCasino,FRAMEPOINT_TOPLEFT,DPS_Panel,FRAMEPOINT_TOPLEFT,0.420,-0.018',
         b'CatalogCasino,FRAMEPOINT_TOPLEFT,DPS_Panel,FRAMEPOINT_TOPLEFT,0.410,-0.018'),
        (b'spellKeysToggle, 0.073, 0.022', b'spellKeysToggle, 0.110, 0.026'),
        (b'F3|r: send gold above that reserve to that target.',
         b'F3|r: open pooling settings. X, F3 or F2 saves and closes.'),
        (b'BlzFrameSetVisible(CatalogCasino,PK_Eligible(GetPlayerId(GetLocalPlayer())))',
         b'BlzFrameSetVisible(CatalogCasino,true)'),
        (b'BlzFrameSetVisible(CatalogCasino, PK_Eligible(p))',
         b'BlzFrameSetVisible(CatalogCasino, true)'),
        (b'CatalogKind == 0 and PK_Eligible(GetPlayerId(GetLocalPlayer()))',
         b'CatalogKind == 0'),
        (b'CatalogKind == 0 and PK_Eligible(s-1)', b'CatalogKind == 0'),
        (b'call TriggerExecute(CasinoOpen)\n        endif\n        set f',
         b'call TriggerExecute(CasinoOpen)\n'
         b'        else\n'
         b'            call DisplayTimedTextToPlayer(GetTriggerPlayer(), 0, 0, 3.0, '
         b'"Casino is unavailable for this player.")\n'
         b'        endif\n        set f'),
    )
    for old, new in edits:
        if old not in script:
            raise ValueError(f'Missing 799X Info source anchor {old!r}')
        script = script.replace(old, new)
    return script.replace(b'\n', newline)
