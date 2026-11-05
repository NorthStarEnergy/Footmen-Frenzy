import audit
from audit import R,W,base,data,normalized,norm,report,storm,read_storm,c,archive,entries
import json,re,struct,shutil,hashlib
def live_refs(path,removed):
    p=norm(path.encode());alt=p[:-4]+b'.mdl' if p.endswith(b'.mdx') else p
    return [n for n,b in normalized.items() if n!=path and n not in removed and not n.lower().endswith('credits.txt') and (p in b or alt in b)]
scope=lambda p:p.startswith(('Models\\OriannaEnchantress\\','Models\\OriannaLich\\','Spells\\Orianna\\')) or p in ['BarrelRollImpact.mdx','DrunkenRageDmgReduction.mdx','ExplosiveCask.mdx','RollingBarrelMissile.mdx']
remove={x['path'] for x in report if scope(x['path']) and not live_refs(x['path'],set())}
# Retain implicit *_Portrait companions whenever their primary model survives.
for p in list(remove):
    if p.lower().endswith('_portrait.mdx'):
        primary=p[:-13]+'.mdx'
        if any(n.lower()==primary.lower() and n not in remove for n in data):remove.remove(p)
model_remove=set(remove);dependencies=set()
for p in model_remove:
    raw=data[p];pos=4
    if raw[:4]!=b'MDLX':continue
    while pos+8<=len(raw):
        tag=raw[pos:pos+4];size=struct.unpack_from('<I',raw,pos+4)[0]
        if tag==b'TEXS':
            for off in range(pos+8,pos+8+size,268):
                tex=raw[off+4:off+264].split(b'\0')[0].decode('latin1')
                found=next((n for n in data if norm(n.encode())==norm(tex.encode())),None)
                if found:dependencies.add(found)
        pos+=8+size
for p in dependencies:
    if not live_refs(p,remove):remove.add(p)
assert len(model_remove)>0
for p in remove:assert not live_refs(p,remove),(p,live_refs(p,remove))
# No active object, script, current model or automatic portrait reference changes.
for p in ['Models\\OriannaGuldan\\Guldan.mdx','war3mapImported\\HeroAbomination.mdx','war3mapImported\\DemonKnight.mdx','InfernalGragas.mdx','InfernalGragas_Portrait.mdx','war3mapImported\\SuperLightningBall.mdx']:
    assert p not in remove
O=R/'src';O.mkdir(exist_ok=True)
imp=data['war3map.imp'];version,count=struct.unpack_from('<II',imp);pos=8;kept=[]
for _ in range(count):
    start=pos;flag=imp[pos];pos+=1;end=imp.index(0,pos);p=imp[pos:end].decode('latin1');pos=end+1
    name=p if flag in (10,13) else 'war3mapImported\\'+p
    if name.lower() not in {p.lower() for p in remove}:kept.append(imp[start:pos])
(O/'war3map.imp').write_bytes(struct.pack('<II',version,len(kept))+b''.join(kept))
wts=data['war3map.wts'];assert b'Consolidated Maul v38' in wts
(O/'war3map.wts').write_bytes(wts.replace(b'Consolidated Maul v38',b'Consolidated Clean v39'))
release=R/'release';release.mkdir(exist_ok=True);out=release/'FF799X_Rx_Consolidated_Clean_v39.w3x';shutil.copy2(base,out)
storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint]
storm.SFileCompactArchive.argtypes=[c.c_void_p,c.c_wchar_p,c.c_bool]
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for p in sorted(remove):assert storm.SFileRemoveFile(h,p.encode(),0),p
for p in ['war3map.imp','war3map.wts']:assert storm.SFileAddFileEx(h,str(O/p),p.encode(),0x80000200,2,2),p
assert storm.SFileCloseArchive(h)
# Compaction physically reclaims deleted model bytes, rather than merely hiding entries.
assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
listfile=R/'known-files.txt';listfile.write_text('\n'.join(n for n in data if not n.startswith('unnamed:') and n not in remove)+'\n',encoding='utf8')
assert storm.SFileCompactArchive(h,str(listfile),False)
assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(out);ae,be=entries(a),entries(b);skip=set()
for p in sorted(remove)+['war3map.imp','war3map.wts','(attributes)','(signature)','(listfile)']:
    e=a.get_hash_table_entry(p)
    if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for p in remove:assert b.get_hash_table_entry(p) is None,p
for k,v in ae.items():
    if k not in skip:assert be.get(k)==v,('Changed unrelated payload',k)
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
assert read_storm(h,'war3map.j')==data['war3map.j']
for n in ['war3map.imp','war3map.wts']:assert read_storm(h,n)==(O/n).read_bytes()
assert storm.SFileCloseArchive(h)
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
result=dict(output=str(out),sha256=sha,base=str(base),removed_models=sorted(model_remove),removed_exclusive_textures=sorted(remove-model_remove),retained_shared_textures=sorted(dependencies-remove),removed_uncompressed_bytes=sum(len(data[p]) for p in remove),previous_map_bytes=base.stat().st_size,map_bytes=out.stat().st_size,saved_map_bytes=base.stat().st_size-out.stat().st_size,preserved_archive_entries=len(ae.keys()-skip),gameplay_script='byte-identical to v38',live_test='not performed; asset reference and archive checks passed')
(R/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
