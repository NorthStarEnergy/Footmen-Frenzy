from pathlib import Path
import sys,json,hashlib,re
O=Path(__file__).parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots')
sys.path.insert(0,str(O.parent/'.audit-deps'));import mpyq
a=mpyq.MPQArchive(str(R/'release/Mini Foots v6.w3x'),listfile=False)
b=mpyq.MPQArchive(str(O/'Mini Foots v7.w3x'),listfile=False)
changed=[];count=0
names={str(f.relative_to(O/'roundtrip/files')).replace('/','\\').encode() for f in (O/'roundtrip/files').rglob('*') if f.is_file()}
names.update(str(f.relative_to(R/'src')).replace('/','\\').encode() for f in (R/'src').rglob('*') if f.is_file())
for name in names:
 if name in [b'(listfile)',b'(attributes)']:continue
 av,bv=a.read_file(name),b.read_file(name)
 if av!=bv:changed.append(name.decode())
 count+=1
assert set(changed)=={'war3map.j','war3map.wts','war3map.w3i'},changed
for f in (R/'src').rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(R/'src');name=str(rel).replace('/','\\')
 data=b.read_file(name);expected=(O/rel).read_bytes() if name in changed else f.read_bytes()
 assert data==expected,name
 out=O/'roundtrip/files'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
s=b.read_file('war3map.j').decode('utf-8-sig');old=a.read_file('war3map.j').decode('utf-8-sig')
pattern=r"BlzCreateUnitWithSkin\((p|Player\(\d+\)), 'hwtw', [^\n]+?\)"
assert re.sub(pattern,'TOWER',s).replace('Mini Foots v7','Mini Foots v6')==re.sub(pattern,'TOWER',old)
assert len(re.findall(pattern,s))==16
report={'status':'PASS','compared_archive_files':count,'changed_files':changed,'tower_count':16,'only_script_changes':'tower coordinates and version name','sha256':hashlib.sha256((O/'Mini Foots v7.w3x').read_bytes()).hexdigest(),'engine_test':'not performed'}
(O/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

