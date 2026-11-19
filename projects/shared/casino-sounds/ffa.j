function FFA_CasinoOpen takes nothing returns nothing
    set CasinoLauncherSlot = GetPlayerId(GetTriggerPlayer())+1
    call CasinoFromStats()
endfunction

function FFA_CasinoInit takes nothing returns nothing
    local trigger sync = CreateTrigger()
    local integer p = 0
    set WalletAccount = GetPlayerName(GetLocalPlayer())
    loop
        exitwhen p >= 24
        set LoanIdentity[p+1] = StringHash(GetPlayerName(Player(p)))
        call BlzTriggerRegisterPlayerSyncEvent(sync,Player(p),"FFWallet1",false)
        set p = p+1
    endloop
    call TriggerAddAction(sync,function WalletReceive)
    call TriggerAddAction(FFA_CasinoLaunch,function FFA_CasinoOpen)
    call TimerStart(CreateTimer(),0.,false,function WalletLoad)
    call PK_Init()
    call CAS_Init()
    set sync = null
endfunction

function FFA_CasinoFinish takes nothing returns nothing
    local trigger batch
    if CAS_ended then
        return
    endif
    call CAS_EndMatch()
    // Flush every ticket before the victory dialog can end the session.
    set batch = CreateTrigger()
    call TriggerAddAction(batch,function MK_PayBatch)
    loop
        exitwhen MK_scan > MK_n
        call TriggerExecute(batch)
    endloop
    call DestroyTrigger(batch)
    call WalletAward(-CAS_winner,0)
    set batch = null
endfunction
