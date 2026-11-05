from pathlib import Path
import sys,json,hashlib,shutil,re,struct
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions,archive,entries
import objdata
manifest=json.loads((R/'inputs.json').read_text())
for name,info in manifest.items():
    assert hashlib.sha256(Path(info['path']).read_bytes()).hexdigest()==info['sha256'],('Input changed during merge',name)
base=Path(manifest['tf']['path']);s=(R/'src/war3map.j').read_text();final=functions(s)
old=functions((R/'inputs/tf/war3map.j').read_text())
allowed={'MF_InitHeroPolicy','MF_HeroDisabled','OM_WindupFX','OM_OnCastAnimation','DK_Free','DK_EndRequiem','MU_OnCast','MU_TickHero','MU_Init','FFGS_CountLivingOfType','FFR7_ApplyMassSpeed','FFGS_SpawnForPlayer','Trig_set_hero_stats_Actions','Trig_keep_footy_in_base_Conditions','Trig_Mass_START_Actions','InitTrig_FF_Runtime','main'}
changed={n for n in old if final[n]!=old[n]};assert changed==allowed,changed^allowed
assert not old.keys()-final.keys()
# All TF runtime, cleaver/Devour, Guardian/Gragus gameplay, UI and map functions
# outside the explicit integration list must remain byte-for-byte identical.
branch_checks={}
for donor,prefixes in [('tf',('TF33_','MQ_','MD_','DR_')),('veigar',('VG_',)),('tooltips',('FF_CompactHeroTooltips_',))]:
    fs=functions((R/'inputs'/donor/'war3map.j').read_text());names=[n for n in fs if n.startswith(prefixes)]
    assert names
    for n in names:assert final[n]==fs[n],(donor,n)
    branch_checks[donor]=len(names)
guldan=functions((R/'inputs/guldan/war3map.j').read_text())
for n in ['OM_WindupFX','OM_OnCastAnimation']:assert final[n]==guldan[n],n
assert 'call DR_Start(source, level)' in final['DK_OnCast']
assert "call MD_Start(u, GetSpellTargetUnit(), rank)" in final['MU_OnCast']
assert 'call MU_Fling' not in final['MU_OnCast']
assert 'call MU_GasSpawn(u, rank)' in final['MU_OnCast']+final['MU_TickHero']
assert 'call FS_Hit(u, target' not in final['MU_TickHero'] # No double poison damage.
assert "or id == 'HMu1'" not in final['MF_HeroDisabled']
assert 'PauseUnit' not in final['DK_Free']
assert 'i == 0 or DK_Kind[i] != 4' in final['DK_EndRequiem']
def objs(path):return {e['newId'] if e['newId']!='\0'*4 else e['oldId']:e for t in objdata.load(str(path))['tables'] for e in t}
scope={'w3a':{'A0DL','AOz1','AOz2','AOz3','AOz4','AGr1','AGr2','AGr3','AGr4','AGr8','AZd1','ATfd','AFg1','AMu2'},'w3u':{'HOr1','HGr1'}}
object_report={}
for ext,allowed_ids in scope.items():
    before=objs(R/'inputs/tf'/('war3map.'+ext));after=objs(R/'src'/('war3map.'+ext))
    modified={k for k in before if before[k]!=after[k]}
    assert modified<=allowed_ids,(ext,modified-allowed_ids)
    added=after.keys()-before.keys()
    assert added==({'AVge','AVgw','AVgs','AMug'} if ext=='w3a' else {'HVg1'}),(ext,added)
    object_report[ext]={'modified':sorted(modified),'added':sorted(added),'preserved':len(before)-len(modified)}
    if ext=='w3a':
        for k in ['ATfg','AMu1','AMu3','AMu4','AMdc','ADk1','ADk4']:assert after[k]==before[k],k
    data=objdata.load(str(R/'src'/('war3map.'+ext)));assert objdata.dump(data)==(R/'src'/('war3map.'+ext)).read_bytes()
checks=json.loads((R/'checks.json').read_text());assert checks['mass_checks']>=45 and sum(checks['hero_checks'].values())>=168
assert 'Parse successful:' in (R/'compiler.log').read_text() and 'error' not in (R/'compiler.log').read_text().lower()
# Read the new model payloads from their verified donor archive.
h=c.c_void_p();assert storm.SFileOpenArchive(manifest['guldan']['path'],0,0x100,c.byref(h))
assets={}
for i,name in enumerate(['Models\\OriannaGuldan\\Guldan.mdx','Guldan.blp']):
    p=R/'src'/('guldan-'+str(i)+Path(name).suffix);p.write_bytes(read_storm(h,name));assets[name]=p
assert storm.SFileCloseArchive(h)
def imports(data):
    out=[];pos=8;count=struct.unpack_from('<I',data,4)[0]
    for _ in range(count):
        flag=data[pos];pos+=1;end=data.index(0,pos);out.append((flag,data[pos:end]));pos=end+1
    return out
assert set(imports((R/'inputs/tf/war3map.imp').read_bytes()))<=set(imports((R/'src/war3map.imp').read_bytes()))
files={n:R/'src'/n for n in ['war3map.j','war3map.w3a','war3map.w3u','war3map.wts','war3map.imp']};files.update(assets)
release=R/'release';release.mkdir(exist_ok=True);out=release/'FF799X_Rx_Consolidated_InstaMass_v36.w3x';shutil.copy2(base,out)
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for name,path in files.items():assert storm.SFileAddFileEx(h,str(path),name.encode(),0x80000200,2,2),name
assert storm.SFileCloseArchive(h)
before,after=archive(base),archive(out);be,ae=entries(before),entries(after);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for name,path in files.items():
    assert read_storm(h,name)==path.read_bytes(),name
    e=before.get_hash_table_entry(name)
    if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
# Verify actual packed terrain pathing at every initial maximum-count formation position.
wpm=read_storm(h,'war3map.wpm');w3e=read_storm(h,'war3map.w3e')
offset=13
for _ in range(2):n=struct.unpack_from('<I',w3e,offset)[0];offset+=4+4*n
tw,th,x0,y0=struct.unpack_from('<IIff',w3e,offset);pw,ph=struct.unpack_from('<II',wpm,8)
for pn in range(12):
    for n in range(63):
        along=(pn%3*7+n%7)*48;depth=n//7*32
        x=(128+along+depth)*(-1 if pn//3 in [0,3] else 1)
        y=-256+(1088-along+depth)*(-1 if pn//3 in [2,3] else 1)
        ix=int((x-x0)/32);iy=int((y-y0)/32)
        assert not wpm[16+iy*pw+ix]&2,(pn,n,'unwalkable')
assert storm.SFileCloseArchive(h)
for name in ['(listfile)','(attributes)','(signature)']:
    e=before.get_hash_table_entry(name)
    if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for key,value in be.items():
    if key not in skip:assert ae.get(key)==value,key
digest=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(digest+'  '+out.name+'\n')
report=dict(output=str(out),sha256=digest,inputs=manifest,preserved_archive_entries=len(be.keys()-skip),preserved_existing_functions=len(old)-len(changed),changed_functions=sorted(changed),added_functions=sorted(final.keys()-old.keys()),exact_branch_function_checks=branch_checks,object_checks=object_report,behavior_checks=checks['mass_checks']+sum(checks['hero_checks'].values()),walkable_formation_positions=756,compiler='passed',live_test='Pending Warcraft III playtest',resolutions=['Mundo Devour and Undying supersede Fling and Sadism; gas trail and rank colors integrated with newer kit.','Demon Ascension supersedes Dread Requiem; applicable legacy cleanup/duplicate-completion fixes retained.','Pub mass staging port retains 90-second countdown and normal 12-player spawn counts.'])
(R/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['output','sha256','preserved_archive_entries','preserved_existing_functions','behavior_checks','walkable_formation_positions']},indent=2))
