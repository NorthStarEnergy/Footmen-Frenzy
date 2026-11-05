"""Port the 799X hero runtime, objects and assets without changing Mini rules."""
import copy, shutil, struct
from pathlib import Path
donor=R/'audit/heroes-799x-v13'
ds=(donor/'war3map.j').read_text(encoding='utf-8-sig')
pat=r'^function (\w+) takes .*?^endfunction'
def funcs(text): return {m[1]:m[0] for m in re.finditer(pat,text,re.M|re.S)}
def region(text):
    matches=[m for m in re.finditer(pat,text,re.M|re.S) if m[1].startswith('OM_')]
    return matches[0].start(),matches[-1].end()
a,b=region(s); da,db=region(ds); block=ds[da:db]
# Preserve unrelated hero tooltip functions embedded among Orianna functions.
for m in re.finditer(pat,s[a:b],re.M|re.S):
    if not m[1].startswith('OM_'):
        block,n=re.subn(r'^function '+m[1]+r' takes .*?^endfunction',lambda _:m[0],block,flags=re.M|re.S)
        assert n==1,m[1]
s=s[:a]+block+s[b:]
assert 'location OM_VisualGround' not in s
s=s.replace('    hashtable OM_Hash = InitHashtable()', '    location OM_VisualGround = Location(0.0, 0.0)\n    hashtable OM_Hash = InitHashtable()',1)
for name in ['FS_ClearFortitude','FS_OnCast']:
    sf,df=funcs(s),funcs(ds);s=s.replace(sf[name],df[name],1)
# Only replace Orianna tooltip and roster-stat lines, preserving all other heroes.
sf,df=funcs(s),funcs(ds)
for name,pattern in [('FF_HeroTooltips_Init',r'^.*(?:\x27AOz2\x27|\x27AOz4\x27).*$'),('Trig_set_hero_stats_Actions',r'^.*set udg_hero_\w+\[92\]=.*$')]:
    old,new=sf[name],df[name]
    oldlines=re.findall(pattern,old,re.M);newlines=re.findall(pattern,new,re.M)
    assert len(oldlines)==len(newlines) and oldlines,name
    for before,after in zip(oldlines,newlines):old=old.replace(before,after,1)
    s=s.replace(sf[name],old,1)
for ext,ids in [('w3u',{'HOr1','hor1','hor2'}),('w3a',{'AOz1','AOz2','AOz3','AOz4','AOz5','AOz7','AGf1','AGr2'}),('w3h',{'BOr4','BOr5'})]:
    target=objdata.load(str(O/('war3map.'+ext)));source=objdata.load(str(donor/('war3map.'+ext)))
    key=lambda e:e['newId'] if e['newId']!='\0'*4 else e['oldId']
    seen=set()
    for ti,table in enumerate(source['tables']):
        for e in table:
            if key(e) in ids:
                target['tables'][ti]=[old for old in target['tables'][ti] if key(old)!=key(e)]
                target['tables'][ti].append(copy.deepcopy(e));seen.add(key(e))
    assert seen==ids,(ext,ids-seen)
    (O/('war3map.'+ext)).write_bytes(objdata.dump(target))
assets=[]
for f in donor.rglob('*'):
    rel=f.relative_to(donor); path=str(rel).replace('/','\\')
    if f.is_file() and ('Orianna' in path or 'Gragas' in path or path in ('war3mapImported\\OrbLightningX.mdx','war3mapImported\\OrbLightX.mdx')):
        out=O/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,out)
        if f.suffix.lower() in ('.mdx','.blp','.wav'):assets.append(path)
imp=(O/'war3map.imp').read_bytes();version,count=struct.unpack_from('<ii',imp);at=8;paths=set()
for _ in range(count):
    end=imp.index(b'\0',at+1);paths.add(imp[at+1:end].decode().lower());at=end+1
new=[]
for path in assets:
    if path.lower() not in paths: paths.add(path.lower());new.append(path)
(O/'war3map.imp').write_bytes(struct.pack('<ii',version,count+len(new))+imp[8:]+b''.join(b'\r'+p.encode()+b'\0' for p in new))
