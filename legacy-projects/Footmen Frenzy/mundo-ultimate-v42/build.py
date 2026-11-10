from pathlib import Path
import sys,re,struct,json,hashlib,shutil,ast,io
from PIL import Image
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions,archive,entries
import objdata
root=W/'799x-backport/release'
common=root/'FF799X_Rx_Consolidated_Clean_v39.w3x'
item=root/'FF799X_Rx_ItemBalance_v41.w3x'
unit=Path('C:/Users/User/Documents/Warcraft III/Maps/Test/FF799X_Rx_Unit_Balance_v41.w3x')
paths={'common':common,'item':item,'unit':unit}
def readmap(path,names):
 h=c.c_void_p();assert storm.SFileOpenArchive(str(path),0,0x100,c.byref(h))
 result={}
 for name in names:
  try:result[name]=read_storm(h,name)
  except AssertionError:pass
 assert storm.SFileCloseArchive(h);return result
names=['war3map.j','war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3mapSkin.w3a','war3map.wts','war3map.imp']
common_data,item_data,unit_data=[readmap(p,names) for p in paths.values()]
for n,d in item_data.items():(S/n).write_bytes(d)
norm=lambda b:b.decode('utf-8-sig').replace('\r\n','\n')
bs,is_,us=[norm(d['war3map.j']) for d in [common_data,item_data,unit_data]]
bf,inf,uf=[functions(s) for s in [bs,is_,us]]
assert not (bf.keys()-inf.keys()) and not (bf.keys()-uf.keys())
unit_functions={n for n in bf if bf[n]!=uf[n]}
item_functions={n for n in bf if bf[n]!=inf[n]}
assert not unit_functions & item_functions,unit_functions & item_functions
expected={'FFGS_ApplyUnit','FF_gr_Poll','FF_kl_OnDeath','FF_st_IsFeedUnit','Trig_GM_set_messages_Actions','Trig_Unit_Experience_System_Func004Func014C','Trig_set_base_Actions','Trig_set_spawn_variables_Actions','Trig_swap_execute_Actions'}
assert unit_functions==expected
# Verify the donor's entire script change is accounted for by these functions.
check=bs
for n in sorted(unit_functions):check=check.replace(bf[n],uf[n],1)
assert check==us,'Unit branch has changes outside the identified functions'
merged=is_
for n in sorted(unit_functions):
 assert inf[n]==bf[n]
 merged=merged.replace(inf[n],uf[n],1)
(S/'war3map.j').write_text(merged,encoding='utf8')
for n in ['war3map.w3u','war3mapSkin.w3u']:
 assert common_data[n]==item_data[n],n+' has independent edits and needs a three-way object merge'
 (S/n).write_bytes(unit_data[n])
# Ultimate ability: modify only the ordinary and hero-research art fields.
o=objdata.load(str(S/'war3map.w3a'));before=objdata.load(str(S/'war3map.w3a'))
index=lambda x:{(e['newId'] if e['newId']!='\0'*4 else e['oldId']):e for t in x['tables'] for e in t}
idx=index(o);idx0=index(before);ability=idx['AMu4']
icon=r'ReplaceableTextures\CommandButtons\BTNMundoUndying.blp'
for key in ['aart','arar']:
 matches=[m for m in ability['mods'] if m['id']==key and m.get('level',0)==0];assert len(matches)==1
 matches[0]['value']=icon
for uid in idx:
 if uid!='AMu4':assert idx[uid]==idx0[uid],uid
assert [m for m in ability['mods'] if m['id'] not in ('aart','arar')]==[m for m in idx0['AMu4']['mods'] if m['id'] not in ('aart','arar')]
# The legacy parser calls the v3 modification-set count 'flags' and the
# set flag 'extra'. v40 wrote zero sets but still serialized one set, which
# misaligns Warcraft's object reader. Serialize the existing set as (1, 0).
for i in range(256):
 indicator=idx[f'mD{i:02X}']
 assert indicator['oldId']=='ANcl' and indicator['extra']==0
 indicator['flags']=1
(S/'war3map.w3a').write_bytes(objdata.dump(o))
if 'war3mapSkin.w3a' in item_data:
 sk=index(objdata.load(str(S/'war3mapSkin.w3a')))
 assert 'AMu4' not in sk or not any(m['id'] in ('aart','arar') for m in sk['AMu4']['mods']),'Skin object would override the new icon'
# WC3 Button Manager 1.8.2 border templates and opaque mipmapped BLP1.
tree=ast.parse((W/'799x-backport/make_magic_textures.py').read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='blp'],type_ignores=[]),'<blp>','exec'))
art=Image.open(R/'assets/Undying.png').convert('RGBA').resize((64,64),Image.Resampling.LANCZOS)
template_dir=W/'799x-backport/tools/button-manager/Button Manager/standard';imports=[]
preview=Image.new('RGBA',(384,192))
for disabled in [False,True]:
 template=Image.open(template_dir/('bm_disbtn.tga' if disabled else 'bm_btn.tga')).convert('RGB')
 render=Image.new('RGBA',(64,64));render.putdata([tuple(round(c*b[0]/255) for c in p[:3])+(255,) if b[0]==b[1]==b[2] else b+(255,) for p,b in zip(art.getdata(),template.getdata())])
 folder='CommandButtonsDisabled' if disabled else 'CommandButtons';prefix='DISBTN' if disabled else 'BTN'
 path=f'ReplaceableTextures\\{folder}\\{prefix}MundoUndying.blp';out=S/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blp(render));imports.append(path)
 data=out.read_bytes();decoded=Image.open(io.BytesIO(data)).convert('RGBA')
 assert data[:4]==b'BLP1' and decoded.size==(64,64) and decoded.getchannel('A').getextrema()==(255,255)
 assert sum(x>0 for x in struct.unpack_from('<16I',data,28))==7
 preview.paste(render.resize((192,192),Image.Resampling.NEAREST),(192 if disabled else 0,0))
preview.save(R/'assets/icon-preview.png')
imp=S/'war3map.imp';raw=imp.read_bytes();ver,count=struct.unpack_from('<II',raw)
for path in imports:assert path.lower().encode() not in raw.lower()
imp.write_bytes(struct.pack('<II',ver,count+len(imports))+raw[8:]+b''.join(b'\x0d'+x.encode()+b'\0' for x in imports))
wts=S/'war3map.wts';raw=wts.read_bytes();assert b'Consolidated Mundo v40' in raw
wts.write_bytes(raw.replace(b'Consolidated Mundo v40',b'Consolidated Undying v42a'))
report=dict(base_maps={k:str(p) for k,p in paths.items()},base_hashes={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()},unit_functions=sorted(unit_functions),imports=imports,payloads=['war3map.j','war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3map.wts','war3map.imp']+imports)
(R/'changes.json').write_text(json.dumps(report,indent=2));print('Prepared v42 with unit/item branches merged and Undying icons.')
