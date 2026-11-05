import re
def patch(s):
 old=re.search(r'^function FS_OnCast takes .*?^endfunction',s,re.M|re.S)[0]
 new=old.replace('call SetUnitAnimationByIndex(u, 9)','call SetUnitAnimationByIndex(u, 12)')
 new=new.replace('        if a == FS_Q or a == FS_R then','        if a == FS_Q or a == FS_R then\n            call SetUnitAnimationByIndex(u, 11)\n            call QueueUnitAnimation(u, "stand")')
 new=new.replace('        elseif a == FS_E and dist > 1.0 then','        elseif a == FS_E and dist > 1.0 then\n            call SetUnitAnimationByIndex(u, 9)\n            call QueueUnitAnimation(u, "stand")')
 assert new!=old and 'SetUnitAnimationByIndex(u, 12)' in new
 return s.replace(old,new)
