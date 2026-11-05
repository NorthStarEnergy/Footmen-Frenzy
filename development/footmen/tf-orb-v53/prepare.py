from pathlib import Path
import sys
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W/'hero-polish'));from archive_helpers import storm,read_storm,c,functions
base=W/'tf-lock-v52/release/FF799X_Rx_TF_Guardian_OrbLock_v52.w3x';h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h));s=read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r\n','\n');assert storm.SFileCloseArchive(h)
def edit(name,a,b):
 global s
 f=functions(s)[name];assert a in f,(name,a);s=s.replace(f,f.replace(a,b,1),1)
s=s.replace('constant real TFP_wildCards___PROJECTILE_SPEED=1400.','constant real TFP_wildCards___PROJECTILE_SPEED=1100.',1)
edit('TFP_wildCards___setCardRandHue','SetUnitScale(u,1.0,1.0,1.0)','SetUnitScale(u,2.0,2.0,2.0)')
edit('TF33_Cast',"set orb=CreateUnit(GetOwningPlayer(c),'htf1',GetUnitX(c),GetUnitY(c),0.)\n            call SetUnitScale(orb,0.85,0.85,0.85)","set orb=CreateUnit(GetOwningPlayer(c),'htf1',GetUnitX(c),GetUnitY(c),0.)\n            call SetUnitScale(orb,2.0,2.0,2.0)")
edit('TF33_Flight','distance<=36.','distance<=33.');edit('TF33_Flight','+36.*dx/distance','+33.*dx/distance');edit('TF33_Flight','+36.*dy/distance','+33.*dy/distance')
edit('TF33_Impact','    local real heal=30.+20.*rank','    local real heal=30.+20.*rank\n    local sound healSound\n    local effect healFx')
edit('TF33_Impact','''            call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Human\\\\HolyBolt\\\\HolyBoltSpecialArt.mdl",c,"origin"))''','''            set healSound=CreateSound("Spells\\\\Orianna\\\\Feedback\\\\Heal.wav",false,true,true,0,0,"SpellsEAX")
            call SetSoundDuration(healSound,700)
            call SetSoundChannel(healSound,0)
            call SetSoundVolume(healSound,127)
            call SetSoundDistances(healSound,300.,2400.)
            call SetSoundDistanceCutoff(healSound,2600.)
            call AttachSoundToUnit(healSound,c)
            call StartSound(healSound)
            call KillSoundWhenDone(healSound)''')
edit('TF33_Impact','''                    call DestroyEffect(AddSpecialEffectTarget("Abilities\\\\Spells\\\\Items\\\\AIhe\\\\AIheTarget.mdl",u,"origin"))''','''                    set healFx=AddSpecialEffectTarget("Abilities\\\\Spells\\\\Orc\\\\HealingWave\\\\HealingWaveTarget.mdl",u,"origin")
                    call BlzSetSpecialEffectColor(healFx,65,255,100)
                    call BlzSetSpecialEffectScale(healFx,1.2)
                    call DestroyEffect(healFx)''')
edit('TF33_Impact','    set g=null\n    set u=null','    set g=null\n    set u=null\n    set healSound=null\n    set healFx=null')
(R/'src/war3map.j').write_text(s,encoding='utf8');print('Prepared green healing visuals, audio, and 1100 speed projectiles')
