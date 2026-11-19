function PF_Color takes integer s returns string
    local integer id = GetHandleId(GetPlayerColor(Player(s-1)))
    if id < 10 then
        return "ReplaceableTextures\\TeamColor\\TeamColor0"+I2S(id)+".blp"
    endif
    return "ReplaceableTextures\\TeamColor\\TeamColor"+I2S(id)+".blp"
endfunction
