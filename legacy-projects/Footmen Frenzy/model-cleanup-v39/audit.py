from pathlib import Path
import sys,json,re,struct
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries
import objdata
base=W/'799x-backport/release/FF799X_Rx_Consolidated_Maul_v38.w3x'
R.mkdir(exist_ok=True);h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
imp=read_storm(h,'war3map.imp');pos=8;names=set()
for _ in range(struct.unpack_from('<I',imp,4)[0]):
    flag=imp[pos];pos+=1;end=imp.index(0,pos);n=imp[pos:end].decode('latin1');pos=end+1
    names.add(n if flag in (10,13) else 'war3mapImported\\'+n)
for folder in [W/'mini-foots/base/files',W/'799x-backport/src']:
    names.update(str(p.relative_to(folder)).replace('/','\\') for p in folder.rglob('*') if p.is_file())
a=archive(base);data={};known={}
for n in sorted(names):
    e=a.get_hash_table_entry(n)
    if e:
        data[n]=read_storm(h,n);known[(e.hash_a,e.hash_b,e.locale,e.platform)]=n
for key,value in entries(a).items():
    if key not in known:
        meta=a.get_hash_table_entry('(attributes)')
        if meta and key==(meta.hash_a,meta.hash_b,meta.locale,meta.platform):continue
        assert isinstance(value,bytes),('Unscanned archive payload',key)
        data['unnamed:'+str(key)]=value
names=list(data)
assert storm.SFileCloseArchive(h)
def norm(b):return b.lower().replace(b'/',b'\\').replace(b'\\\\',b'\\')
normalized={n:norm(b) for n,b in data.items() if n.lower() not in ['(listfile)','war3map.imp']}
models=[n for n in names if n.lower().endswith(('.mdx','.mdl'))]
report=[]
for model in models:
    path=norm(model.encode());alt=path[:-4]+(b'.mdl' if path.endswith(b'.mdx') else b'.mdx')
    refs=[n for n,b in normalized.items() if n!=model and (path in b or alt in b)]
    report.append(dict(path=model,bytes=len(data[model]),references=refs))
(R/'models.json').write_text(json.dumps(report,indent=2))
for ext in ['war3map.w3u','war3mapSkin.w3u']:
    if ext not in data:continue
    p=R/ext;p.write_bytes(data[ext])
    for t in objdata.load(str(p))['tables']:
        for e in t:
            if e['newId'] in ['HOr1','hor1','hor2','HMu1','HGr1','HDk1','HTf1','H043','HVg1']:
                print(ext,e['newId'],[(m['id'],m['value']) for m in e['mods'] if m['id'] in ['umdl','unam','upro']])
print('Model inventory',len(models))
if __name__=='__main__':print(json.dumps([x for x in report if re.search('Models\\\\Orianna|Spells\\\\Orianna',x['path'],re.I)],indent=2))
