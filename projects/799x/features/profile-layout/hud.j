function HUD_Text takes real x, real y, real width, real height, real size, string value returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","",HUD_root,"",0)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,HUD_root,FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetSize(f,width,height)
    call BlzFrameSetFont(f,"CasinoUI\\Bold.ttf",size,0)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetEnable(f,false)
    call BlzFrameSetText(f,value)
    return f
endfunction

function HUD_Refresh takes nothing returns nothing
    local integer width = BlzGetLocalClientWidth()
    local integer height = BlzGetLocalClientHeight()
    local integer slot = PF_MySlot()
    local real left = 0.012
    if width != HUD_width or height != HUD_height then
        if height > 0 then
            set left = left-RMaxBJ(0.0,(0.6*I2R(width)/I2R(height)-0.8)*0.5)
        endif
        call BlzFrameClearAllPoints(HUD_root)
        call BlzFrameSetAbsPoint(HUD_root,FRAMEPOINT_TOPLEFT,left,0.574)
        set HUD_width = width
        set HUD_height = height
    endif
    call HUD_ShowWallet()
    if slot <= 12 then
        call BlzFrameSetText(HUD_gold,I2S(GetPlayerState(Player(slot-1),PLAYER_STATE_RESOURCE_GOLD)))
    else
        call BlzFrameSetText(HUD_gold,"--")
    endif
endfunction

function HUD_Create takes nothing returns nothing
    local framehandle label
    set HUD_root = BlzCreateFrameByType("BACKDROP","FFBalanceHud",FFUI_GetRoot(),"",0)
    call BlzFrameSetSize(HUD_root,0.268,0.043)
    call BlzFrameSetTexture(HUD_root,"ReplaceableTextures\\TeamColor\\TeamColor00.blp",0,true)
    call BlzFrameSetVertexColor(HUD_root,BlzConvertColor(225,18,18,18))
    call BlzFrameSetLevel(HUD_root,110)
    set label = HUD_Text(0.010,0.002,0.121,0.013,0.0095,"WALLET")
    call BlzFrameSetTextColor(label,BlzConvertColor(255,255,215,132))
    set HUD_wallet = HUD_Text(0.010,0.014,0.121,0.027,0.019,"")
    set label = HUD_Text(0.144,0.002,0.117,0.013,0.0095,"MATCH GOLD")
    call BlzFrameSetTextColor(label,BlzConvertColor(255,255,215,132))
    set HUD_gold = HUD_Text(0.144,0.014,0.117,0.027,0.019,"")
    call HUD_Refresh()
    set label = null
endfunction
