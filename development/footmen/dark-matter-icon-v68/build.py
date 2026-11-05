from pathlib import Path
import sys, ast, struct, shutil, json, hashlib
from PIL import Image
R=Path(__file__).resolve().parent; W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive, entries, storm, read_storm, c
source=W/'hero-icons-simple/veigar-selected/C-Dark-Matter.png'
im=Image.open(source).convert('RGB')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original_sha=sha(source)
tree=ast.parse((W/'799x-backport/make_magic_textures.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='blp'],type_ignores=[]),'<blp>','exec'))
standard=W/'799x-backport/tools/button-manager/Button Manager/standard'
assets={}
for disabled in [False,True]:
    template=Image.open(standard/('bm_disbtn.tga' if disabled else 'bm_btn.tga')).convert('RGB')
    # Scale only the border template, never the selected artwork.
    mult=Image.new('RGB',template.size); overlay=Image.new('RGB',template.size)
    mult.putdata([(b[0],)*3 if b[0]==b[1]==b[2] else (0,0,0) for b in template.getdata()])
    overlay.putdata([(0,0,0) if b[0]==b[1]==b[2] else b for b in template.getdata()])
    mult=mult.resize(im.size,Image.Resampling.BILINEAR)
    overlay=overlay.resize(im.size,Image.Resampling.BILINEAR)
    out=Image.new('RGBA',im.size)
    out.putdata([tuple(min(255,round(a[i]*m[i]/255)+b[i]) for i in range(3))+(255,) for a,m,b in zip(im.getdata(),mult.getdata(),overlay.getdata())])
    name=('DISBTN' if disabled else 'BTN')+'VeigarW'
    out.save(R/(name+'.png'))
    member='ReplaceableTextures\\'+('CommandButtonsDisabled' if disabled else 'CommandButtons')+'\\'+name+'.blp'
    path=R/(name+'.blp'); data=bytearray(blp(out)); struct.pack_into('<I',data,24,1); path.write_bytes(data)
    decoded=Image.open(path); assert decoded.size==im.size
    offsets=struct.unpack_from('<16I',data,28); sizes=struct.unpack_from('<16I',data,92)
    assert all(o+s<=len(data) for o,s in zip(offsets,sizes))
    assert sizes[0]==im.width*im.height*2
    assets[member]=path
base=W/'combined-v68/release/FF799X_Rx_Veigar_Classic_v68.w3x'
dest=R/'FF799X_Rx_Veigar_Classic_v68_DarkMatterIcon.w3x'
shutil.copy2(base,dest)
h=c.c_void_p(); assert storm.SFileOpenArchive(str(dest),0,0,c.byref(h))
for member,path in assets.items(): assert storm.SFileAddFileEx(h,str(path),member.encode(),0x80000200,2,2)
assert storm.SFileCloseArchive(h)
assert storm.SFileOpenArchive(str(dest),0,0x100,c.byref(h))
for member,path in assets.items(): assert read_storm(h,member)==path.read_bytes()
objects=read_storm(h,'war3map.w3a')
assert b'AVgw' in objects and b'ReplaceableTextures\\CommandButtons\\BTNVeigarW.blp' in objects
assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(dest); old,new=entries(a),entries(b); allowed=set()
for name in list(assets)+['(listfile)','(attributes)','(signature)']:
    for ar in [a,b]:
        e=ar.get_hash_table_entry(name)
        if e: allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert all(new.get(k)==v for k,v in old.items() if k not in allowed)
assert all(k in old or k in allowed for k in new)
assert sha(source)==original_sha
report={'output':str(dest),'sha256':sha(dest),'artwork_dimensions':im.size,'source_sha256':original_sha,'replaced_members':list(assets),'unrelated_entries_preserved':sum(k not in allowed for k in old),'engine_tested':False}
(R/'verification.json').write_text(json.dumps(report,indent=2))
(R/'README.txt').write_text('Veigar Dark Matter (AVgw): standard BTN and DISBTN borders over the selected artwork at original dimensions. Only the two existing icon payloads are replaced; gameplay and spell bindings are unchanged. Full-resolution PNG button masters are included. BLP1 uses 256-color encoding and full mipmaps. Archive readback and unrelated member preservation verified; not tested in the game. Modern Warcraft III required for textures above the old 512-pixel limit. Format reference: https://www.hiveworkshop.com/threads/blp-specifications-wc3.279306/\n')
print(json.dumps(report,indent=2))
