import re
def patch(s):
 helpers=r'''function FS_BarrelPresentation takes effect fx, unit caster, boolean ultimate returns nothing
    local sound yell = null
    local string voice = "Units\\Creeps\\PandarenBrewmaster\\PandarenBrewmasterWarcry1.wav"
    if ultimate then
        call BlzSetSpecialEffectScale(fx, 1.45)
        call BlzSetSpecialEffectColor(fx, 255, 55, 35)
        set yell = CreateSound(voice, false, true, true, 0, 0, "HeroAcksEAX")
        call SetSoundDuration(yell, GetSoundFileDuration(voice))
        call SetSoundChannel(yell, 0)
        call SetSoundVolume(yell, 120)
        call SetSoundDistances(yell, 400.0, 2200.0)
        call SetSoundDistanceCutoff(yell, 2400.0)
        call AttachSoundToUnit(yell, caster)
        call StartSound(yell)
        call KillSoundWhenDone(yell)
    else
        call BlzSetSpecialEffectScale(fx, 1.15)
    endif
    set yell = null
endfunction

function FS_UltimateBurst takes real x, real y returns nothing
    local effect fx = AddSpecialEffect("Objects\\Spawnmodels\\Other\\NeutralBuildingExplosion\\NeutralBuildingExplosion.mdl", x, y)
    call BlzSetSpecialEffectScale(fx, 1.30)
    call BlzSetSpecialEffectColor(fx, 255, 70, 35)
    call DestroyEffect(fx)
    set fx = null
endfunction

'''
 pos=s.index('function FS_Tick takes');s=s[:pos]+helpers+s[pos:]
 needle='                set FS_FX[i] = AddSpecialEffect(FS_BARREL, GetUnitX(u), GetUnitY(u))'
 assert s.count(needle)==1;s=s.replace(needle,needle+'\n                call FS_BarrelPresentation(FS_FX[i], u, a == FS_R)')
 needle='                                call FS_Area(u, owner, x, y, 430.0, amount, 3)'
 assert s.count(needle)==1;s=s.replace(needle,'                                call FS_UltimateBurst(x, y)\n'+needle)
 return s
