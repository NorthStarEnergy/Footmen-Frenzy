from pathlib import Path
import sys,re,json,hashlib,shutil,difflib
O=Path(__file__).parent
R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots')
sys.path[:0]=[str(O.parent/'.audit-deps'),str(R/'tools')]
import mpyq,objdata
V=O/'final-roundtrip/files';old=O/'old-roundtrip/files'
a=mpyq.MPQArchive(str(O/'Mini Foots v7.w3x'),listfile=False)
S=O/'validation-src';shutil.copytree(R/'src',S,dirs_exist_ok=True)
for name in ['war3map.j','war3map.wts','war3map.w3i','war3map.w3u']:shutil.copyfile(O/name,S/name)
for f in S.rglob('*'):
 if f.is_file():
  rel=f.relative_to(S);data=a.read_file(str(rel).replace('/','\\'));assert data==f.read_bytes(),rel
  target=V/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
# The established Mini regression suite, using the staged sources and final archive.
code=(O/'verify.py').read_text()
code=code.replace("R=Path(__file__).parent;",'R=Path('+repr(str(R))+');')
code=code.replace("S=R/'src';V=Path((R/'last-build.txt').read_text().strip())/'roundtrip/files'",'S=Path('+repr(str(S))+');V=Path('+repr(str(V))+')')
code=code.replace("release=R/'release/Mini Foots v7.w3x'",'release=Path('+repr(str(O/'Mini Foots v7.w3x'))+')')
code=code.replace("(R/'verification.json')","(Path("+repr(str(O))+ ")/'regression-verification.json')")
exec(compile(code,'mini-regressions','exec'),{'__file__':str(O/'verify.py')})
# Confirm donor functions against the latest actual packed 799X test, not only source.
donor_path=Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test\FF799X_Rx_Orianna_v13.w3x')
donor=mpyq.MPQArchive(str(donor_path),listfile=False)
ds=donor.read_file('war3map.j').decode('utf-8-sig');s=(S/'war3map.j').read_text(encoding='utf8')
funcs=lambda text:{m[1]:m[0] for m in re.finditer(r'^function (\w+) takes .*?^endfunction',text,re.M|re.S)}
sf,df=funcs(s),funcs(ds)
checked=[n for n in df if n.startswith(('OM_','FS_','GPS_','GTW_','zoom'))]
assert all(sf.get(n)==df[n] for n in checked)
diffs={n:list(difflib.unified_diff(df[n].splitlines(),sf[n].splitlines())) for n in df if n.startswith('DPS_') and sf.get(n)!=df[n]}
(O/'ui-differences.json').write_text(json.dumps(diffs,indent=2))
policy=json.loads((O/'hero-policy.json').read_text());disabled=set(policy['disabled_hero_ids'])
assert {'HTf1','HMu1','HDk1','U00F','H00U','H02W','test'}<=disabled
assert not {'HOr1','HGr1','H0R0'} & disabled
assert 'MF_HeroDisabled(udg_hero_type[index])' in sf['FFR_Allowed']
assert s.count('call AddUnitToStock(')==1 and 'call AddUnitToStockBJ(' not in s
assert 'call AddUnitToStock(' in sf['MF_StockUnit']
coords=json.loads((O/'positions.json').read_text())['restored']
found=[]
for i in range(12):
 for m in re.finditer(r"BlzCreateUnitWithSkin\((p|Player\((\d+)\)), 'hwtw', ([^,]+), ([^,]+),",sf['CreateBuildingsForPlayer'+str(i)]):
  found.append({'owner':i if m[1]=='p' else int(m[2]),'x':float(m[3].replace(' ','')),'y':float(m[4].replace(' ',''))})
assert found==coords
report={'status':'PASS','donor':str(donor_path),'donor_sha256':hashlib.sha256(donor_path.read_bytes()).hexdigest(),'matching_hero_and_zoom_functions':len(checked),'stats_panel_adaptations':list(diffs),'tower_count':len(found),'hero_policy':policy,'engine_test':'pending','sha256':hashlib.sha256((O/'Mini Foots v7.w3x').read_bytes()).hexdigest()}
(O/'verification.json').write_text(json.dumps(report,indent=2));print('FINAL POLICY, TOWERS AND DONOR CHECKS PASS',len(checked))

