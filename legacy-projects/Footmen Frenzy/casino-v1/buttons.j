// Shared colored buttons. Explicit children make fills/font consistent in-game.
// 0 grey, 1 red, 2 green, 3 light green, 4 blue, 5 gold, 6 disabled.
function CUI_Text takes framehandle f, string label returns nothing
    call BlzFrameSetText(BlzFrameGetChild(f,1),label)
endfunction

function CUI_Paint takes framehandle f, integer tone, boolean enabled returns nothing
    local integer color = BlzConvertColor(255,255,250,240)
    call BlzFrameSetEnable(f,enabled)
    if not enabled then
        set tone = 6
        set color = BlzConvertColor(255,145,158,170)
    elseif tone == 3 or tone == 5 then
        set color = BlzConvertColor(255,16,36,27)
    endif
    call BlzFrameSetTexture(BlzFrameGetChild(f,0),"CasinoUI\\button"+I2S(tone)+".blp",0,true)
    call BlzFrameSetTextColor(BlzFrameGetChild(f,1),color)
endfunction

function CUI_Create takes framehandle parent, integer context, real x, real y, real w, real h, string label, integer tone returns framehandle
    local framehandle f = BlzCreateFrameByType("GLUEBUTTON","CasinoAction",parent,"",context)
    local framehandle bg = BlzCreateFrameByType("BACKDROP","CasinoActionFill",f,"",context)
    local framehandle text = BlzCreateFrameByType("TEXT","CasinoActionLabel",f,"",context)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,parent,FRAMEPOINT_TOPLEFT,x,y)
    call BlzFrameSetAllPoints(bg,f)
    call BlzFrameSetAllPoints(text,f)
    call BlzFrameSetFont(text,"CasinoUI\\Bold.ttf",0.0125,0)
    call BlzFrameSetTextAlignment(text,TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_CENTER)
    call BlzFrameSetLevel(bg,0)
    call BlzFrameSetLevel(text,1)
    call BlzFrameSetText(text,label)
    call CUI_Paint(f,tone,true)
    set bg = null
    set text = null
    return f
endfunction
