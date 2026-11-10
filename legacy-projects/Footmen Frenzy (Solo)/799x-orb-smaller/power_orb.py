# Power Orb by Kitabatake: https://www.hiveworkshop.com/threads/power-orb.48602/
import re,shutil
def apply_power_orb(s):
    s=s.replace(r"Spells\\Orianna\\Feedback\\DenseOrb.mdx",r"Spells\\Orianna\\Feedback\\Power_Orb.mdx",2)
    s=s.replace("    local real size = 2.0", "    local real size = 0.60")
    s=s.replace("        // Native missile death animations must not leave a second orb behind.\n        call BlzSetSpecialEffectAlpha(fx, 0)\n        call BlzSetSpecialEffectPosition(fx, 0.0, 0.0, -10000.0)", "        // Power Orb has a finite 1.4-second Death sequence; DestroyEffect plays it here.")
    s=s.replace("    if LoadBoolean(OM_Hash, key, -103) != protect then\n        call OM_ClearBallVisual(i)\n    endif", "    // Keep one persistent orb across shield changes; only its tint changes.")
    return s
if 's' in globals():
    s=apply_power_orb(s)
    target=O/'Spells/Orianna/Feedback/Power_Orb.mdx'
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(R/'assets/Power_Orb.mdx',target)
