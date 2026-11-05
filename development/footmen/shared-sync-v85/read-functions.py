exec(compile(open('shared-sync-v85/inspect.py',encoding='utf8').read().split('selected=')[0],'setup','exec'))
for n in ['FFR9_ApplyAlchemistBounty','Trig_HERO_Death_Wards_Actions','ItemLimit_MaxCopies','ItemLimit_HeroTypeBlocked','ItemLimit_HeroRejectMessage','ItemLimit_WarnOwner','SF_ShopBlockPush','SF_ShopKillBlinkPunish','CreepLimit_MaxAllowed','Trig_AFK_Host_Timer_Expires_Actions','Trig_Staff_of_Sanctuary_Func009C','Trig_Staff_of_Sanctuary_Func008C']:
 if n.startswith(('Item','SF_','Creep')):print(s.get(n,n))
 elif n.startswith('Trig_AFK'):print(m[n]);print(s[n])
 elif n.startswith('Trig_Staff'):print(m.get(n,n));print(s.get(n,n))
 else:print(m.get(n,n))
