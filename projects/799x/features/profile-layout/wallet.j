function HUD_WalletValue takes nothing returns string
    if WalletBalance >= 0 then
        return I2S(WalletBalance)
    elseif HUD_walletRead then
        return "Unavailable"
    endif
    return "Loading"
endfunction

function HUD_ShowWallet takes nothing returns nothing
    if HUD_wallet != null then
        call BlzFrameSetText(HUD_wallet,HUD_WalletValue())
    endif
endfunction
