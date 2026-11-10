from pathlib import Path
import sys,copy,struct,json,shutil,subprocess,hashlib,ast
from PIL import Image
R=Path(__file__).resolve().parent;W=R.parent;O=R/'src';B=R/'base'
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c,archive,entries,functions,objdata
base=W/'dark-matter-icon-v68/FF799X_Rx_Veigar_Classic_v68_DarkMatterIcon.w3x'
assets={}
def save(name,data):
 p=O/name.replace('\\','/');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);assets[name]=p
for name in ['GuardianPentagonDome','GuardianPylon']:
 assets['war3mapImported\\'+name+'.mdx']=O/(name+'.mdx')
for folder,prefix in [('CommandButtons','BTN'),('CommandButtonsDisabled','DISBTN')]:
 old='ReplaceableTextures\\'+folder+'\\'+prefix+'GuardianForceField.blp'
 new='ReplaceableTextures\\'+folder+'\\'+prefix+'GuardianGuardianShield.blp'
 save(new,(B/old.replace('\\','/')).read_bytes())
tree=ast.parse((W/'799x-backport/make_magic_textures.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='blp'],type_ignores=[]),'<blp>','exec'))
for label in ['ForceField','Lantern']:
 im=Image.open(R/('ForceField-selected.png' if label=='ForceField' else label+'.png')).convert('RGB')
 for disabled in [False,True]:
  template=Image.open(W/'799x-backport/tools/button-manager/Button Manager/standard'/('bm_disbtn.tga' if disabled else 'bm_btn.tga')).convert('RGB')
  mult=Image.new('RGB',template.size);over=Image.new('RGB',template.size)
  mult.putdata([(b[0],)*3 if b[0]==b[1]==b[2] else (0,0,0) for b in template.getdata()])
  over.putdata([(0,0,0) if b[0]==b[1]==b[2] else b for b in template.getdata()])
  mult=mult.resize(im.size,Image.Resampling.BILINEAR);over=over.resize(im.size,Image.Resampling.BILINEAR)
  out=Image.new('RGBA',im.size);out.putdata([tuple(min(255,round(a[i]*m[i]/255)+b[i]) for i in range(3))+(255,) for a,m,b in zip(im.getdata(),mult.getdata(),over.getdata())])
  name=('DISBTN' if disabled else 'BTN')+'Guardian'+label
  data=bytearray(blp(out));struct.pack_into('<I',data,24,1)
  save('ReplaceableTextures\\'+('CommandButtonsDisabled' if disabled else 'CommandButtons')+'\\'+name+'.blp',data)
  out.save(R/(name+'.png'))
original=(B/'war3map.j').read_bytes().decode('latin1')
changes=[('war3mapImported\\\\HiveForceShield.mdx','war3mapImported\\\\GuardianPentagonDome.mdx'),
('    set l = CreateUnit(p, TFP_FFDP_UNIT_LANTERN, cx, cy, bj_RADTODEG * Atan2(ty - cy, tx - cx))',"    if GetUnitTypeId(c) == 'H043' then\n        set l = CreateUnit(p, 'hGpy', cx, cy, bj_RADTODEG * Atan2(ty - cy, tx - cx))\n    else\n        set l = CreateUnit(p, TFP_FFDP_UNIT_LANTERN, cx, cy, bj_RADTODEG * Atan2(ty - cy, tx - cx))\n    endif")]
def patch(text):
 for a,b in changes:text=text.replace(a,b)
 return text
for a,b in changes:assert original.count(a)==1,(a,original.count(a))
script=patch(original);save('war3map.j',script.encode('latin1'))
wct=(B/'war3map.wct').read_bytes();pos=wct.index(0,8)+1;prefix=wct[:pos];chunks=[];counts=[0]*len(changes)
while pos<len(wct):
 n=struct.unpack_from('<I',wct,pos)[0];pos+=4;data=wct[pos:pos+n];pos+=n
 text=data.decode('latin1');counts=[x+text.count(a) for x,(a,b) in zip(counts,changes)];data=patch(text).encode('latin1');chunks.append(struct.pack('<I',len(data))+data)
assert pos==len(wct) and counts==[1,1],counts
save('war3map.wct',prefix+b''.join(chunks))
units=objdata.load(str(B/'war3map.w3u'));allunits={e['newId']:e for t in units['tables'] for e in t};assert 'hGpy' not in allunits
new=copy.deepcopy(allunits['htf4']);new['newId']='hGpy'
for m in new['mods']:
 m['end']=b'hGpy'.hex()
 if m['id']=='umdl':m['value']='war3mapImported\\GuardianPylon.mdx'
 if m['id'] in ['unam','unsf']:m['value']='Psionic Pylon'
 if m['id']=='uico':m['value']='ReplaceableTextures\\CommandButtons\\BTNGuardianLantern.blp'
units['tables'][1].append(new);save('war3map.w3u',objdata.dump(units))
imp=(B/'war3map.imp').read_bytes();ver,count=struct.unpack_from('<II',imp);add=['war3mapImported\\GuardianPentagonDome.mdx','war3mapImported\\GuardianPylon.mdx'];save('war3map.imp',struct.pack('<II',ver,count+len(add))+imp[8:]+b''.join(b'\x0d'+n.encode()+b'\0' for n in add))
work=Path.home()/'Documents/Codex/2026-10-28/thi/work'
result=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(O/'war3map.j')],capture_output=True,text=True)
(R/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout+result.stderr
before,after=functions(original),functions(script);changed=[k for k in before if before[k]!=after[k]];assert len(changed)==2,changed
out=R/'FF799X_Rx_Veigar_GuardianVisuals_v68.w3x';shutil.copy2(base,out)
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n,p in assets.items():assert storm.SFileAddFileEx(h,str(p),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h);assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n,p in assets.items():assert read_storm(h,n)==p.read_bytes(),n
assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(out);old,now=entries(a),entries(b);allowed=set()
for n in list(assets)+['(listfile)','(attributes)','(signature)']:
 for ar in [a,b]:
  e=ar.get_hash_table_entry(n)
  if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(now.get(k)==v for k,v in old.items() if k not in allowed)
assert all(k in old or k in allowed for k in now)
report={'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'changed_members':list(assets),'changed_functions':changed,'editor_changes':counts,'unrelated_members_preserved':sum(k not in allowed for k in old),'jass_compiled':True,'engine_tested':False}
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
