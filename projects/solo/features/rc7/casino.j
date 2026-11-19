function SoloCasinoOpen takes nothing returns nothing
    set CasinoLauncherSlot = GetPlayerId(GetTriggerPlayer()) + 1
    call CasinoFromStats()
endfunction

function SoloCasinoInit takes nothing returns nothing
    local trigger sync = CreateTrigger()
    local integer i = 0
    set WalletAccount = GetPlayerName(GetLocalPlayer())
    loop
        exitwhen i >= 24
        set LoanIdentity[i+1] = StringHash(GetPlayerName(Player(i)))
        call BlzTriggerRegisterPlayerSyncEvent(sync,Player(i),"FFWallet1",false)
        call BlzTriggerRegisterPlayerSyncEvent(sync,Player(i),"FFWalletNew",false)
        set i = i+1
    endloop
    call TriggerAddAction(sync,function WalletReceive)
    call TriggerAddAction(SoloCasinoLaunch,function SoloCasinoOpen)
    call TimerStart(CreateTimer(),0.,false,function WalletLoad)
    call PK_Init()
    call CAS_Init()
    set sync = null
endfunction

function SoloCasinoSettle takes nothing returns nothing
    set CAS_winner = PF_winSide
    call TriggerExecute(CAS_matchEvent)
    call WalletAward(0,PF_winSide)
endfunction
