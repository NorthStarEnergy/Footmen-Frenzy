from pathlib import Path
import sys,json,re
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c,functions
import objdata
base=W/'veigar-ultimate-v83/release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x';out=R/'release/FF799X_Rx_Consolidated_v84_TEST.w3x'
def read(p,n):
 h=c.c_void_p();assert storm.SFileOpenArchive(str(p),0,256,c.byref(h));b=read_storm(h,n);assert storm.SFileCloseArchive(h);return b
f=functions(read(out,'war3map.j').decode('utf-8-sig').replace('\r',''));b=functions(read(base,'war3map.j').decode('utf-8-sig').replace('\r',''))
changes=json.loads((R/'merge-changes.json').read_text());assert set(f)==set(b)
assert {n for n in b if b[n]!=f[n]}==set(changes['functions'])
# Every body from the last ten builds exists; differences are recorded rather than hidden.
coverage=[]
for folder in ['veigar-range-v74','spawn-level-v75','colo-xp-v76','colo-curve-v77','level10-catchup-v78','colo-lag-v79','fed-rewards-v80','veigar-visuals-v81','veigar-stacks-v82','veigar-ultimate-v83']:
 candidates=list((W/folder/'release').glob('*.w3x'));assert len(candidates)==1,(folder,candidates)
 old=functions(read(candidates[0],'war3map.j').decode('utf-8-sig').replace('\r',''))
 missing=set(old)-set(f);assert not missing,(folder,missing)
 coverage.append({'branch':folder,'all_functions_retained':True,'identical_functions':sum(old[n]==f[n] for n in old),'changed_in_later_revisions':[n for n in old if old[n]!=f[n]]})
# Exact field-level delta, no other hero/unit object edits.
records=lambda d:{(e['oldId'],e['newId'],m['id'],m.get('level',0),m.get('ptr',0)):m for tab in d['tables'] for e in tab for m in e['mods']}
a=records(objdata.load(str(R/'base.w3u')));z=records(objdata.load(str(R/'src/war3map.w3u')))
changed=[k for k in a if a[k]!=z.get(k)];assert len(changed)==6
assert all(k[0] in ['ogru','ugho'] and k[2] in ['udef','ua1b','uhpm'] for k in changed)
assert all(k[1]=='hGpy' for k in z.keys()-a.keys())
# All preexisting abilities, buffs, terrain and roster stay intact.
for n in ['war3map.w3a','war3map.w3h','war3map.w3e','war3map.w3i','war3map.w3t','war3map.w3q','war3map.doo','war3mapUnits.doo']:
 assert read(base,n)==read(out,n),n
# New pylon and dome references resolve to included assets.
for n in changes['assets']:assert read(out,n)==(R/'src'/n.replace('\\','/')).read_bytes(),n
assert "'hGpy'" in f['TFP_FFDP_OnCast'] and 'GuardianPentagonDome.mdx' in f['GD_Cast']
assert not any(n.startswith(('CAS_','ObsCasino','ObsDraft','FFPS_','FGA_')) for n in f)
report={'function_count':len(f),'v83_functions_unchanged':len(f)-4,'missing_predecessor_functions':0,'recent_builds':coverage,'unit_field_changes':6,'new_units':['hGpy'],'imported_assets_verified':len(changes['assets']),'unchanged_objects_terrain_roster':True,'casino_profile_prototypes_excluded':True,'engine_playtested':False}
(R/'coverage.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='recent_builds'},indent=2))
