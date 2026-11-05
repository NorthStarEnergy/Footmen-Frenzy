from pathlib import Path
import sys, shutil, re, json, hashlib, subprocess
R = Path(__file__).resolve().parent
W = R.parent
sys.path[:0] = [str(W/'hero-polish'), str(W/'mini-foots/tools')]
from archive_helpers import storm, read_storm, c, functions, archive, entries, work
import objdata

base = W/'799x-backport/release/FF799X_Rx_HeroTooltips_v31.w3x'
outdir = R/'src'; outdir.mkdir(exist_ok=True)
(R/'audit').mkdir(exist_ok=True)
names = ['war3map.j', 'war3map.w3a', 'war3map.w3u', 'war3map.wts']
h = c.c_void_p(); assert storm.SFileOpenArchive(str(base), 0, 0x100, c.byref(h))
for name in names: (outdir/name).write_bytes(read_storm(h, name))
assert storm.SFileCloseArchive(h)
s = (outdir/'war3map.j').read_text(encoding='utf-8-sig')
original = s
def edit(name, old, new):
 global s
 f = functions(s)[name]; assert old in f, (name, old)
 s = s.replace(f, f.replace(old, new, 1), 1)
s = s.replace('function MU_OnCast takes nothing returns nothing', (R/'abilities.j').read_text()+'\nfunction MU_OnCast takes nothing returns nothing', 1)
edit('MF_InitHeroPolicy', "        call SetPlayerTechMaxAllowed(Player(i), 'HMu1', 0)\n", '')
edit('MF_HeroDisabled', " or id == 'HMu1'", '')
assert 'set udg_hero_category[95]=0' in s
s = s.replace('set udg_hero_category[95]=0', 'set udg_hero_category[95]=15', 1)
edit('MU_OnCast', '''            call UnitAddAbility(u, 'AMur')
            call SetUnitAbilityLevel(u, 'AMur', rank)
            call BlzUnitHideAbility(u, 'AMur', true)
            call SaveEffectHandle(MU_Hash, h, 6, AddSpecialEffectTarget("Abilities\\\\Spells\\\\NightElf\\\\Immolation\\\\ImmolationTarget.mdl", u, "chest"))''', '''            call SaveReal(MU_Hash, h, 20, MU_Now)
            call MU_GasSpawn(u, rank)''')
edit('MU_OnCast', '''            call MU_EOff(u)
            call SaveReal(MU_Hash, h, 2, MU_Now + 5.0)
            call SaveEffectHandle(MU_Hash, h, 7, AddSpecialEffectTarget("Abilities\\\\Spells\\\\Orc\\\\Bloodlust\\\\BloodlustTarget.mdl", u, "hand,right"))
            call MU_RefreshE(u)''', '''            if not MU_Fling(u, GetSpellTargetUnit(), rank) then
                call MU_Heal(u, 25.0 + 8.0 * (rank - 1))
                call BlzEndUnitAbilityCooldown(u, spell)
            endif''')
f = functions(s)['MU_TickHero']
start = f.index("                call SetUnitAbilityLevel(u, 'AMur', rank)")
end = f.index('            endif', start)
# The first endif is inside the enemy filter; replace through DestroyGroup instead.
end = f.index('                call DestroyGroup(targets)', start) + len('                call DestroyGroup(targets)')
f2 = f[:start]+'''                if LoadReal(MU_Hash, h, 20) <= MU_Now then
                    call MU_GasSpawn(u, rank)
                    call SaveReal(MU_Hash, h, 20, MU_Now + 0.5)
                endif'''+f[end:]
f2 = re.sub(r'        if FS_Alive\(u\) and LoadReal\(MU_Hash, h, 2\).*?        endif\n', '', f2, flags=re.S)
s = s.replace(f, f2, 1)
# Remove the old runtime research tooltip overrides and replace them with rank-specific text.
f = functions(s)['MU_Init']
f2 = re.sub(r'^.*BlzSetAbilityResearch(?:Extended)?Tooltip\(\x27AMu[23]\x27.*\n', '', f, flags=re.M)
assert f2 != f
s = s.replace(f, f2, 1)
d = objdata.load(str(outdir/'war3map.w3a'))
es = {e['newId']:e for table in d['tables'] for e in table}
def field(e, key, value, level=0, typ=3, ptr=0):
 e['mods'] = [m for m in e['mods'] if (m['id'],m['level']) != (key,level)]
 e['mods'].append(dict(id=key,type=typ,level=level,ptr=ptr,value=value,end=e['newId'].encode().hex()))
def gold(t): return '|cffffcc00'+str(t)+'|r'
def cyan(t): return '|cff80dfff'+str(t)+'|r'
calls=[]
for uid, name, key, learn, icon in [('AMu2','Toxic Trail','X','W','BTNPlagueCloud'),('AMu3','Fling','C','E','BTNBash')]:
 e=es[uid]
 for k in ('anam','aart','arar'): field(e,k,name if k=='anam' else 'ReplaceableTextures\\CommandButtons\\'+icon+'.blp')
 for rank in range(1,7):
  if uid=='AMu2':
   body='Toggle a trail of disease clouds that poison nearby enemies.'
   info=gold('Poison:')+' '+cyan(str(35+15*(rank-1))+' damage/sec')+' for 2 sec|n'+gold('Cloud:')+' '+cyan('250 radius, 3 sec')+'|n'+gold('Health drain:')+' '+cyan(str(8+4*rank)+'/sec')+'|nStops before it would kill Mundo.'
  else:
   body='Throw an enemy over Mundo, landing behind him.'
   info=gold('Damage:')+' '+cyan(str(50+30*(rank-1))+' magic')+'|n'+gold('Health cost:')+' '+cyan(25+8*(rank-1))+'|n'+gold('Range:')+' '+cyan(250)+'   '+gold('Cooldown:')+' '+cyan('7 sec')
   field(e,'Ncl2',1,rank,0,2);field(e,'Ncl6','acidbomb',rank,3,6)
   field(e,'aran',250.0,rank,1);field(e,'atar','ground,enemy,organic,vulnerable',rank)
  text=body+'|n|n'+info
  title=name+' ['+gold(key)+'] - Level '+str(rank)
  research='Learn '+name+' ['+gold(learn)+'] - Level '+str(rank)
  ext=gold('Requires hero level '+str(1+3*(rank-1)))+'|n|n'+text
  field(e,'atp1',title,rank);field(e,'aub1',text,rank)
  if rank==1:field(e,'aret',research);field(e,'arut',ext)
  for func,val in [('BlzSetAbilityResearchTooltip',research),('BlzSetAbilityResearchExtendedTooltip',ext)]:
   calls.append("    call %s('%s', \"%s\", %d)"%(func,uid,val,rank-1))
f=functions(s)['MU_Init']; s=s.replace(f,f.replace('    set MU_Hash = InitHashtable()', '\n'.join(calls)+'\n    set MU_Hash = InitHashtable()',1),1)
# Aap2 is Warcraft III's Disease Cloud aura. The invisible temporary cloud applies its native poison buff.
cloud=dict(oldId='Aap2',newId='AMug',flags=1,extra=0,mods=[])
field(cloud,'anam','Mundo Toxic Trail Cloud');field(cloud,'alev',6,0,0)
for rank in range(1,7):
 field(cloud,'aare',250.0,rank,1)
 field(cloud,'Apl1',2.0,rank,1,1)
 field(cloud,'Apl2',float(35+15*(rank-1)),rank,1,2)
 field(cloud,'atar','ground,enemy,organic,vulnerable',rank)
assert 'AMug' not in es
d['tables'][1].append(cloud)
(outdir/'war3map.w3a').write_bytes(objdata.dump(d))
u=objdata.load(str(outdir/'war3map.w3u'))
hero=next(e for t in u['tables'] for e in t if e['newId']=='HMu1')
next(m for m in hero['mods'] if m['id']=='utub')['value']='|cff808080Category:|r Carry Tier|n|nA health-powered tank. Throw infected cleavers, leave a toxic trail, and fling enemies behind you. Sadism restores health and grants speed. Adrenaline Rush restores 0.3% maximum health each second.'
(outdir/'war3map.w3u').write_bytes(objdata.dump(u))
s=s.replace('FF799X - Hero Tooltips v31','FF799X - Mundo v32')
(outdir/'war3map.j').write_text(s,encoding='utf8')
p=outdir/'war3map.wts'; raw=p.read_bytes(); assert b'FF799X - Hero Tooltips v31' in raw;p.write_bytes(raw.replace(b'FF799X - Hero Tooltips v31',b'FF799X - Mundo v32'))
run=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(outdir/'war3map.j')],capture_output=True,text=True)
(R/'audit/compiler.log').write_text(run.stdout+run.stderr)
assert run.returncode==0,run.stdout+run.stderr
release=R/'release';release.mkdir(exist_ok=True);out=release/'FF799X_Rx_Mundo_v32.w3x';shutil.copy2(base,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for name in names: assert storm.SFileAddFileEx(h,str(outdir/name),name.encode(),0x80000200,2,2),name
assert storm.SFileCloseArchive(h)
before=archive(base);after=archive(out); oldentries,newentries=entries(before),entries(after);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name in names:
 assert read_storm(h,name)==(outdir/name).read_bytes()
 e=before.get_hash_table_entry(name);skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert storm.SFileCloseArchive(h)
for name in ['(listfile)','(attributes)','(signature)']:
 e=before.get_hash_table_entry(name)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in oldentries.items():
 if k not in skip:assert newentries.get(k)==v,k
digest=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(digest+'  '+out.name+'\n')
new_functions=functions(s)
report=dict(output=str(out),sha256=digest,preserved_archive_entries=len(oldentries.keys()-skip),changed_functions=[n for n,f in functions(original).items() if new_functions[n]!=f],live_test='Pending')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
