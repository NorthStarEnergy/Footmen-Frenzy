// Cosmetic only: Q/R damage remains synchronous in VG_ClassicCast.
function VG81_OrbImpact takes unit target, string model returns nothing
    local effect fx = AddSpecialEffectTarget(model, target, "chest")
    local timer t = CreateTimer()
    call BlzPlaySpecialEffect(fx, ANIM_TYPE_STAND)
    call SaveEffectHandle(VG_Hash, GetHandleId(t), 20, fx)
    call TimerStart(t, 0.30, false, function VG_ImpactCleanup)
    set fx = null
    set t = null
endfunction
