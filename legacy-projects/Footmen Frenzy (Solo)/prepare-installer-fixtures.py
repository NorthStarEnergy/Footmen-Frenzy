from pathlib import Path
import json,re,hashlib
out=Path('legacy-installer-migration').resolve();cases=[]
for idx,p in enumerate((out/'updated').rglob('*.ps1')):
 rel=p.relative_to(out/'updated');tree=out/'fixtures'/str(idx)/'project';script=tree/rel;script.parent.mkdir(parents=True)
 s=p.read_text(encoding='utf-8-sig').replace(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\Legacy-TestDelivery.ps1',str(out/'Legacy-TestDelivery.ps1'))
 script.write_text(s,encoding='utf-8-sig')
 def seed(path):
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(('fixture '+str(path)).encode());h=hashlib.sha256(path.read_bytes()).hexdigest();path.with_suffix('.sha256').write_text(h);return h
 for name in ('799x-backport','mini-foots','six-player-ffa'):(tree/name/'release').mkdir(parents=True,exist_ok=True)
 (script.parent/'audit').mkdir(exist_ok=True)
 for match in re.findall(r"release\\([^'\n]+\.w3x)",s):seed(script.parent/'release'/match)
 # Hero sync copies fixed verified release names.
 if rel.parts[0]=='hero-sync':
  for name in ('Mini Foots v9.w3x','Solo Foots 6 Player FFA v2.w3x'):seed(script.parent/'release'/name)
 variants={'hero-sync':['mini','solo'],'hero-polish':['799x','mini','solo']}.get(rel.parts[0],[''])
 for variant in variants:
  folder=script.parent/variant;folder.mkdir(exist_ok=True)
  output=folder/'release'/('Verified_'+(variant or '799X')+'.w3x');h=seed(output)
  (folder/'verification.json').write_text(json.dumps({'output':str(output),'sha256':h,'passed':True}))
 families=['799X']
 if rel.parts[0]=='hero-sync':families=['Mini Foots','FFA Foots']
 elif rel.parts[0]=='hero-polish':families=['799X','Mini Foots','FFA Foots']
 elif rel.parts[0]=='six-player-ffa':families=['FFA Foots']
 cases.append({'script':str(script),'maps':str(tree.parent/'Maps'),'families':families,'name':str(rel)})
(out/'cases.json').write_text(json.dumps(cases,indent=2))
print(len(cases),'isolated installer cases prepared')
