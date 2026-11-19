"""Instrument a private copy for a Warcraft client smoke test. Never install the probe."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

from prepare import Archive, ROOT, functions, once


def make_probe(release):
    work = release.parents[2] / "probe" / uuid.uuid4().hex[:8]
    work.mkdir(parents=True)
    config = json.loads((ROOT / "tools.local.json").read_text())
    with Archive(config["stormlib"], release) as archive:
        source = archive.read("war3map.j").decode().replace("\r\n", "\n")
    # Redirect both sides of FileIO and the match's preload exports for this run.
    for native in ("Preloader", "PreloadGenEnd"):
        source = source.replace(native + "(", native + '("SoloRC7_QA\\\\' + work.name + '\\\\"+')
    probe = r'''
function SoloProbeFlag takes boolean b returns integer
    if b then
        return 1
    endif
    return 0
endfunction

function SoloProbeLog takes string phase returns nothing
    call PreloadGenClear()
    call PreloadGenStart()
    call Preload("phase="+phase)
    call Preload("heroLevel="+I2S(GetHeroLevel(probeHero))+" xp="+I2S(GetHeroXP(probeHero)))
    call Preload("victimLevel="+I2S(GetUnitLevel(probeTarget))+" dead="+I2S(SoloProbeFlag(IsUnitType(probeTarget,UNIT_TYPE_DEAD))))
    call Preload("walletReady="+I2S(SoloProbeFlag(CAS_ready[1]))+" wallet="+I2S(CAS_gold[1])+" casinoFrame="+I2S(GetHandleId(CAS_root[1]))+" pokerFrame="+I2S(GetHandleId(PK_Dialog[0])))
    call Preload("blackjackRound="+I2S(BJ_round[1])+" blackjackBet="+I2S(BJ_bet[12]))
    call Preload("tavern="+GetUnitName(DraftShop[1])+" x="+R2S(GetUnitX(DraftShop[1]))+" y="+R2S(GetUnitY(DraftShop[1])))
    call PreloadGenEnd("SoloRC7_QA\\RUN_ID\\"+phase+".txt")
endfunction

function SoloProbeFinish takes nothing returns nothing
    call SoloProbeLog("finished")
    call DestroyTimer(GetExpiredTimer())
endfunction

function SoloProbeRun takes nothing returns nothing
    local player p = Player(0)
    set probeHero = CreateUnit(p,'Hpal',2650.,900.,0.)
    set probeTarget = CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE),'h060',2700.,900.,180.)
    call SetUnitInvulnerable(probeTarget,false)
    call BlzSetUnitIntegerField(probeTarget,UNIT_IF_LEVEL,33)
    call SetPlayerHandicapXP(p,1.)
    call SetUnitState(probeTarget,UNIT_STATE_LIFE,1.)
    call SoloProbeLog("before")
    call UnitDamageTarget(probeHero,probeTarget,10000.,true,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
    call BJ_Wager(1)
    call TimerStart(CreateTimer(),5.,false,function SoloProbeFinish)
    call DestroyTimer(GetExpiredTimer())
    set p = null
endfunction
'''
    probe = probe.replace("RUN_ID", work.name)
    source = once(source, "\nendglobals\n", "\nunit probeHero = null\nunit probeTarget = null\nendglobals\n")
    main = functions(source)["main"]
    main_with_timer = once(main, "\nendfunction", '\n    call SoloProbeLog("init")\n    call TimerStart(CreateTimer(),8.,false,function SoloProbeRun)\nendfunction')
    source = once(source, main, probe + "\n" + main_with_timer)
    script = work / "war3map.j"
    script.write_bytes(source.replace("\n", "\r\n").encode())
    subprocess.run([config["pjass"], config["common_j"], config["blizzard_j"], str(script)], check=True)
    target = work / "SoloRC7Probe.w3x"
    shutil.copyfile(release, target)
    with Archive(config["stormlib"], target, writable=True) as archive:
        archive.add("war3map.j", script)
    with Archive(config["stormlib"], target) as archive:
        assert archive.read("war3map.j") == script.read_bytes()
    return target


if __name__ == "__main__":
    print(make_probe(Path(sys.argv[1]).resolve()))
