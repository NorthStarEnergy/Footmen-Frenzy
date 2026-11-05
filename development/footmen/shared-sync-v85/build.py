"""Bidirectional shared-fix port; recipient balance, objects and modes are preserved."""
from pathlib import Path
import sys,re,json,struct,hashlib,subprocess,shutil
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,functions,storm,read_storm,c
MAIN=W/'consolidated-v84/release/FF799X_Rx_Consolidated_v84_TEST.w3x'
SOLO=Path('C:/Users/User/Documents/Warcraft III/Maps/Solo Foots/Solo Tests/Solo_Foots_v1.8_4P_799X_UPDATE08.w3x')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(MAIN.read_bytes())=='e3d36689259eb7d00d8585d45425590b72ac5d8f411c6cd6c056fb11ff5c44b9'
assert sha(SOLO.read_bytes())=='7529c5a174b2ee98fc5e0b90bdd20276a0ec14f0850501962907722a28415300'
def read(path,name):
 h=c.c_void_p();assert storm.SFileOpenArchive(str(path),0,256,c.byref(h));b=read_storm(h,name);assert storm.SFileCloseArchive(h);return b
norm=lambda b:b.decode('utf-8-sig').replace('\r','')
ms,ss=norm(read(MAIN,'war3map.j')),norm(read(SOLO,'war3map.j'));mf,sf=functions(ms),functions(ss)
def globals_of(s):
 g=re.search(r'(?ms)^globals\b(.*?)^endglobals',s)[1]
 return {m[1]:line for line in g.splitlines() if (m:=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)\b',line))}
mg,sg=globals_of(ms),globals_of(ss)
replacements={};added={};notes={}
def donor(name,reason):
 text=sf[name]
 for a,b in [('SoloFootsDisplayMessageToForce','DisplayTextToForce'),('SoloFootsDisplayMessageToPlayer','DisplayTextToPlayer'),('SoloFootsDisplayTimedMessageToForce','DisplayTimedTextToForce')]:text=text.replace(a,b)
 replacements[name]=text;notes[name]=reason
# Shared resource ownership, idle polling and per-cast cleanup improvements.
for name in [
 'Trig_HERO_Throw_Glaive_Loop_Func001Func001Func016Func001Func002C','Trig_HERO_Throw_Glaive_Loop_Func001Func001Func016Func001C','Trig_HERO_Throw_Glaive_Loop_Actions',
 'Trig_HERO_Prison_Actions','Trig_HERO_Prison_Func029A','Trig_HERO_Prison_Wall_countdown_Actions',
 'Trig_HERO_Thor_Powerhit_Actions','Trig_Staff_of_the_River_OnHit_Actions',
 'Trig_HERO_Architect_tower_build_Actions','Trig_HERO_Architect_tower_countdown_Actions','Trig_HERO_Blooddancer_Bloodrush_periodic_Actions',
 'Trig_ITEM_Wall_Actions','Trig_ITEM_Wall_countdown_Actions','Trig_ITEM_Purge_the_Dead_Actions',
 'Trig_HERO_Pandero_Preserve_Actions','Trig_HERO_Hook_Loop_Finish','Trig_HERO_break_loop_if_tp_Actions',
 'Trig_HERO_Myrmidon_Sinkhole_start_Actions','Trig_HERO_Myrmidon_Sinkhole_suck_Actions','Trig_HERO_Myrmidon_Sinkhole_end_Actions','InitTrig_HERO_Myrmidon_Sinkhole_suck',
 'Trig_page_system_Actions','Trig_limit_amount_of_creeps_Actions','Trig_ITEM_limits_Actions','Trig_ITEM_combo_limits_Actions',
 'Trig_ITEM_Scroll_of_Invisibility_Actions','Trig_ITEM_Scroll_of_AntiMagic_Actions','Trig_ITEM_Scroll_of_Inner_Fire_Actions','Trig_ITEM_Rune_of_Inner_Fire_Actions','Trig_ITEM_Scroll_of_Illusion_Actions']:
 donor(name,'Solo resource ownership / equivalent lookup / idle-loop improvement')
for i in range(1,5):
 for prefix in ['Trig_block_from_shop_t','Trig_kill_blink_shop_t']:donor(prefix+str(i)+'_Actions','Coordinate-based shop handling; recipient conditions and registrations retained')
# Preserve 799X-specific shop selector and observer-substitution ownership before cap accounting.
n='Trig_page_system_Actions';special="""    if GetUnitTypeId(udg_temp_unit) == 'u01C' then
        call SetUnitOwner(udg_temp_unit, Player(PLAYER_NEUTRAL_PASSIVE), false)
        call SelectUnitForPlayerSingle(udg_temp_unit, udg_temp_player)
        return
    endif
"""
replacements[n]=replacements[n].replace('    set target=SF_PageTargetForSelector',special+'    set target=SF_PageTargetForSelector')
n='Trig_limit_amount_of_creeps_Actions';replacements[n]=replacements[n].replace('    set udg_temp_unit=GetSoldUnit()','    set udg_temp_unit=GetSoldUnit()\n    call SoloSub_ReownToSlot(udg_temp_unit)')
# Merge only ownership corrections when donor and recipient balance differs.
def patch(name,old,new,reason,count=1):
 f=replacements.get(name,mf[name]);assert f.count(old)==count,(name,old,f.count(old));replacements[name]=f.replace(old,new);notes[name]=reason
patch('Trig_Cripple_Wave_Actions','RemoveLocation(udg_QS_Point[0])','RemoveLocation(udg_QS_Point_Copy[0])','Free Cripple Wave locations instead of Searing Bullet locations')
patch('Trig_Cripple_Wave_Actions','RemoveLocation(udg_QS_Point[1])','RemoveLocation(udg_QS_Point_Copy[1])','Free Cripple Wave locations instead of Searing Bullet locations')
n='Trig_Staff_of_the_River_Actions'
patch(n,'returns nothing\n','returns nothing\n    local location jungleCastOrigin\n','Release nested cast-origin allocation')
patch(n,'    set udg_MissileStart=PolarProjectionBJ(GetUnitLoc(GetTriggerUnit()), 150.00, udg_Jungle_Angle)','    set jungleCastOrigin=GetUnitLoc(GetTriggerUnit())\n    set udg_MissileStart=PolarProjectionBJ(jungleCastOrigin, 150.00, udg_Jungle_Angle)\n    call RemoveLocation(jungleCastOrigin)\n    set jungleCastOrigin=null','Release nested cast-origin allocation')
patch('Trig_Mirror_Image_Finish_Actions','set udg_MissileFinish=udg_MIC_Point[udg_MIC_Loop]','set udg_MissileFinish=OffsetLocation(udg_MIC_Point[udg_MIC_Loop], 0, 0)','Missile consumes a copied endpoint, not a persistent array location')
patch('Trig_ITEM_Forked_Fury_NEW_Actions',"            call BlzStartUnitAbilityCooldown(udg_temp_unit, 'A0HZ', 10.00)","            call BlzStartUnitAbilityCooldown(udg_temp_unit, 'A0HZ', 10.00)\n            call RemoveLocation(udg_temp_point)",'Release proc origin; retain 799X A0HZ and 10-second cooldown')
n='Trig_HERO_Hook_Loop_Actions'
patch(n,'call ForGroupBJ(GetRandomSubGroup(1, udg_hook_target_group[udg_X]), function Trig_HERO_Hook_Loop_Func001Func001Func003Func005Func005Func005A)','set udg_hook_target[udg_X]=GroupPickRandomUnit(udg_hook_target_group[udg_X])','Avoid temporary random subgroup; preserve recipient hook speed and radius')
patch(n,'call DestroyGroup(udg_hook_target_group[udg_X])','call DestroyGroup(udg_hook_target_group[udg_X])\n                    set udg_hook_target_group[udg_X]=null','Clear released hook group')
for n in ['Trig_ITEM_packhorse_pickup_Actions','Trig_ITEM_packhorse_buy_Actions','Trig_ITEM_Illusion_Actions']:
 f=mf[n];f,cnt=re.subn(r'DisplayTextToForce\(GetForceOfPlayer\((GetOwningPlayer\(udg_temp_unit\)|ConvertedPlayer\(udg_temp_playernumber\))\),',r'ItemLimit_WarnOwner(\1,',f);assert cnt>0
 replacements[n]=f;notes[n]='Send owner warning without allocating a leaking force; preserve recipient item restrictions'
# Preserve the recipient's correct two-copy warning rather than importing Solo's stale 1x text.
n='Trig_ITEM_limits_Actions'
replacements[n]=replacements[n].replace('"|cffff0000Only 1x |r"','"|cffff0000Only " + I2S(maxCopies) + "x |r"')
def non_destructive_limit(body):
 pattern=r"(?ms)^            if itemTypeId == 'I009' then.*?^            else\n(.*?)^            endif\n"
 body,count=re.subn(pattern,lambda m:''.join(line[4:]+'\n' for line in m[1].splitlines()),body);assert count==1
 return body
replacements[n]=non_destructive_limit(replacements[n])
# Resolve only missing function dependencies; never overwrite another existing subsystem implicitly.
def clean(s):return re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*','',s)
while True:
 body='\n'.join(replacements.values())+'\n'+'\n'.join(added.values())
 refs=set(re.findall(r'\b(\w+)\s*\(',clean(body)))|set(re.findall(r'\bfunction\s+(\w+)',clean(body)))
 missing=(refs & sf.keys())-mf.keys()-added.keys()
 if not missing:break
 for n in sorted(missing):
  assert not n.startswith('SoloFootsDisplay'),n
  text=sf[n].replace('SoloFootsDisplayMessageToForce','DisplayTextToForce').replace('SoloFootsDisplayMessageToPlayer','DisplayTextToPlayer')
  added[n]=text
# Retain the 799X-specific inventory policy while adopting Solo's lookup implementation.
added['ItemLimit_MaxCopies']=added['ItemLimit_MaxCopies'].replace('    return 0\nendfunction', "    if itemTypeId == 'nspi' or itemTypeId == 'I03C' then\n        return 1\n    endif\n    return 0\nendfunction")
n='ItemLimit_HeroTypeBlocked'
f=added[n]
f=f.replace("    elseif itemTypeId == 'desc' then", "    elseif itemTypeId == 'nspi' then\n        return heroTypeId == 'O003'\n    elseif itemTypeId == 'desc' then")
for item,extra in [('desc',["E00Z"]),('I01H',["E00U","E00Z","N01L"])]:
 pattern=r"(elseif itemTypeId == '"+item+r"' then[^\n]*\n        return [^\n]+)"
 f,count=re.subn(pattern,lambda m:m[1]+''.join(" or heroTypeId == '"+x+"'" for x in extra),f);assert count==1
added[n]=f
replacements['Trig_ITEM_limits_Actions']=replacements['Trig_ITEM_limits_Actions'].replace("set udg_temp_item_type='modt'","set udg_temp_item_type='nspi'")
# Add the exact donor globals referenced by these bodies, excluding locals and existing globals.
body=clean('\n'.join(replacements.values())+'\n'+'\n'.join(added.values()))
newglobals={n:line for n,line in sg.items() if n not in mg and re.search(r'\b'+n+r'\b',body)}
assert set(newglobals)<= {'sf_page_target_type','sf_glaive_x','sf_glaive_y','sf_sinkhole_enum_group'},newglobals
# Shared improvements from 799X to Solo, with Solo's bounty dice preserved.
solo_replacements={'Trig_HERO_Jaina_Ulti_Actions':mf['Trig_HERO_Jaina_Ulti_Actions'],'Trig_HERO_Alchemist_Chemical_Rage_Bounty_Actions':mf['Trig_HERO_Alchemist_Chemical_Rage_Bounty_Actions']}
solo_added={'FFR9_ApplyAlchemistBounty':mf['FFR9_ApplyAlchemistBounty'].replace('UNIT_IF_GOLD_BOUNTY_AWARDED_NUMBER_OF_DICE, 0','UNIT_IF_GOLD_BOUNTY_AWARDED_NUMBER_OF_DICE, 8').replace('UNIT_IF_GOLD_BOUNTY_AWARDED_SIDES_PER_DIE, 0','UNIT_IF_GOLD_BOUNTY_AWARDED_SIDES_PER_DIE, 3')}
solo_replacements['Trig_ITEM_limits_Actions']=non_destructive_limit(sf['Trig_ITEM_limits_Actions']).replace('"|cffff0000Only 1x |r"','"|cffff0000Only " + I2S(maxCopies) + "x |r"')
solo_replacements['config']=sf['config'].replace('Solo Foots v1.8 4P - 799X Update 08','Solo Foots v1.8 4P - Shared Fixes Update 09')
# Imported helpers must precede their callers, using native dependency ordering.
def ordered(fs):
 result=[];done=set();active=set()
 def visit(n):
  if n in done:return
  assert n not in active,n
  active.add(n);text=clean(fs[n]);refs=set(re.findall(r'\b(\w+)\s*\(',text))|set(re.findall(r'\bfunction\s+(\w+)',text))
  for dep in fs:
   if dep in refs and dep!=n:visit(dep)
  active.remove(n);done.add(n);result.append(fs[n])
 for n in fs:visit(n)
 return '\n\n'.join(result)
helpers=ordered(added)
def patch_text(text,reps,adds='',globals_added=None,insert=False):
 fs=functions(text)
 for n,f in reps.items():
  if n in fs:text=text.replace(fs[n],f,1)
 if globals_added and re.search(r'(?m)^endglobals',text):text=re.sub(r'(?m)^endglobals',lambda _:'\n'.join(globals_added.values())+'\nendglobals',text,count=1)
 if insert and adds:
  pos=re.search(r'(?m)^[ \t]*function ',text).start();text=text[:pos]+adds+'\n\n'+text[pos:]
 return text
reports=[]
for label,base,script,reps,adds,globs,title,filename in [
 ('799x',MAIN,ms,replacements,helpers,newglobals,'Footmen Frenzy 799X v85 - Shared Fixes Test','FF799X_Rx_Shared_Fixes_v85_TEST.w3x'),
 ('solo',SOLO,ss,solo_replacements,ordered(solo_added),{},'Solo Foots v1.8 4P - Shared Fixes Update 09','Solo_Foots_v1.8_4P_SHARED_FIXES_UPDATE09.w3x')]:
 O=R/label/'src';O.mkdir(parents=True,exist_ok=True)
 updated=patch_text(script,reps,adds,globs,True)
 assert functions(updated).keys()==functions(script).keys() | (added.keys() if label=='799x' else solo_added.keys())
 (O/'war3map.j').write_text(updated,encoding='utf8')
 if label=='799x':
  w=read(base,'war3map.wct');p=w.index(0,8)+1;prefix=w[:p];chunks=[];inserted=False
  while p<len(w):
   size=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+size];p+=size
   text=norm(b.rstrip(b'\0'));insert='function VG82_UpdateCounter' in text
   result=patch_text(text,reps,adds,globs,insert)
   if insert:assert not inserted;inserted=True
   chunks.append(result.encode()+(b'\0' if b.endswith(b'\0') else b'') if result!=text else b)
  assert p==len(w) and inserted
  (O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
  editor='\n'.join(norm(b.rstrip(b'\0')) for b in chunks);ef=functions(editor);uf=functions(updated)
  for n in reps.keys()|added.keys():assert ef[n]==uf[n],n
  header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1]
  known=globals_of('globals\n'+header+'\nendglobals');extras=[line for n,line in globals_of(updated).items() if n not in known]
  regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:ef.get(m[1],m[0]),updated)
  regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
  (R/label/'editor-validation.j').write_text(regen,encoding='utf8')
  headers=[b.rstrip(b'\0') for b in chunks if re.search(rb'(?m)^globals\b',b)];runtime=[b.rstrip(b'\0') for b in chunks if b'function VG82_UpdateCounter' in b];assert len(headers)==len(runtime)==1
  snap=O/'source_roundtrip';snap.mkdir(exist_ok=True);(snap/'globals.j').write_bytes(headers[0]);(snap/'FF_Runtime.j').write_bytes(runtime[0])
  manifest=json.loads(norm(read(base,'FF_SOURCE_MANIFEST.json')));manifest.update(compiled_source_sha256=sha((O/'war3map.j').read_bytes()),globals_sha256=sha(headers[0]),runtime_sha256=sha(runtime[0]),runtime_functions=len(ef),source_map_sha256=sha(base.read_bytes()),revision='v85 shared Solo fixes',engine_playtest=False)
  (O/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
  (O/'FF_MAINTENANCE.md').write_bytes(read(base,'FF_MAINTENANCE.md')+b'\n\nv85: Shared Solo leak/ownership, lookup and idle-loop fixes; preserve 799X balance, modes, roster, observer substitutions and v84 content. See shared-sync-v85 manifest. Engine test pending.\n')
 else:
  (O/'SF_SHARED_FIXES_MANIFEST.json').write_text(json.dumps({'revision':'UPDATE09','runtime_authoritative':True,'editor_source_not_authoritative':True,'base_sha256':sha(base.read_bytes()),'script_sha256':sha((O/'war3map.j').read_bytes()),'changed_functions':list(reps),'added_functions':list(solo_added),'preserved':'All object data, players, modes, terrain, economy rules and balance. Alchemist bounty retains Solo 8x3 dice.'},indent=2))
 wts=read(base,'war3map.wts');wts,n=re.subn(rb'(STRING 1\s*\{\s*)[^\r\n]+',lambda m:m[1]+title.encode(),wts,count=1);assert n==1
 (O/'war3map.wts').write_bytes(wts)
 # Compilers are required before packaging any candidate.
 tool=Path('C:/Users/User/Documents/Codex/2026-10-28/thi/work')
 def run(args,name,success):
  result=subprocess.run(list(map(str,args)),capture_output=True,text=True,errors='replace',cwd=R/label,timeout=90)
  (R/label/name).write_text(result.stdout+result.stderr);assert result.returncode==0 and success in result.stdout+result.stderr,(result.stdout+result.stderr)[-5000:]
 run([tool/'jasshelper/pjass.exe',tool/'common.j',tool/'Blizzard.j',O/'war3map.j'],'compiler.log','Parse successful:')
 if label=='799x':
  run([tool/'jasshelper/clijasshelper.exe','--scriptonly',tool/'common.j',tool/'Blizzard.j',R/label/'editor-validation.j',R/label/'editor-compiled.j'],'jasshelper.log','Success!')
  run([tool/'jasshelper/pjass.exe',tool/'common.j',tool/'Blizzard.j',R/label/'editor-compiled.j'],'editor-compiler.log','Parse successful:')
 dest=R/'release'/filename;dest.parent.mkdir(exist_ok=True);shutil.copy2(base,dest)
 h=c.c_void_p();assert storm.SFileOpenArchive(str(dest),0,0,c.byref(h))
 payloads={str(p.relative_to(O)).replace('/','\\'):p for p in O.rglob('*') if p.is_file()}
 for n,p in payloads.items():assert storm.SFileAddFileEx(h,str(p),n.encode(),0x80000200,2,2),n
 storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint]
 if archive(base).get_hash_table_entry('(attributes)'):assert storm.SFileRemoveFile(h,b'(attributes)',0)
 assert storm.SFileCloseArchive(h)
 a,z=archive(base),archive(dest);ae,ze=entries(a),entries(z);allowed=set()
 for n in list(payloads)+['(attributes)','(listfile)','(signature)']:
  for ar in [a,z]:
   e=ar.get_hash_table_entry(n)
   if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
 assert all(ze.get(k)==v for k,v in ae.items() if k not in allowed)
 assert all(k in ae or k in allowed for k in ze)
 for n,p in payloads.items():assert read(dest,n)==p.read_bytes(),n
 bf,af=functions(script),functions(updated);changed=[n for n in bf if bf[n]!=af[n]]
 assert set(changed)==set(reps)
 report={'variant':label,'output':str(dest),'sha256':sha(dest.read_bytes()),'base':str(base),'base_sha256':sha(base.read_bytes()),'changed_functions':changed,'added_functions':list(af.keys()-bf.keys()),'added_globals':list(globs),'preserved_functions':len(bf)-len(changed),'unrelated_archive_entries_preserved':sum(k not in allowed for k in ae),'runtime_compiled':True,'editor_compiled':label=='799x','engine_playtested':False}
 (R/label/'verification.json').write_text(json.dumps(report,indent=2));dest.with_suffix('.sha256').write_text(report['sha256']+'  '+filename+'\n');reports.append(report)
(R/'migration.json').write_text(json.dumps({'maps':reports,'799x_change_reasons':notes},indent=2));print(json.dumps(reports,indent=2))

