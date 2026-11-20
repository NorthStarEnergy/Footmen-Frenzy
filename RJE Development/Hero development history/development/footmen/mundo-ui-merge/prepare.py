"""Merge only the Mundo branch delta into the UI repair agent's completed map."""
from pathlib import Path
import sys,re,struct,json,hashlib,copy,subprocess,tempfile,shutil
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
BASE=Path(sys.argv[1]).resolve()
ANCESTOR=W/'combined-v68/release/FF799X_Rx_Veigar_Classic_v68.w3x'
DONOR=W/'mundo-cloud-ramp/release/FF799X_Rx_Mundo_Cloud_Ramp_Test.w3x'
O=R/'src';O.mkdir(exist_ok=True)
names=['war3map.j','war3map.wct','war3map.w3a','war3map.w3u','war3map.w3h','war3map.imp','FF_MAINTENANCE.md']
def readmap(p):
    h=c.c_void_p();assert storm.SFileOpenArchive(str(p),0,0x100,c.byref(h))
    d={n:read_storm(h,n) for n in names};assert storm.SFileCloseArchive(h);return d
old,ours,target=map(readmap,[ANCESTOR,DONOR,BASE])
norm=lambda b:b.decode('utf-8-sig').replace('\r','')
of=functions(norm(old['war3map.j']));nf=functions(norm(ours['war3map.j']))
changed=[n for n in of if of[n]!=nf[n]];added=[n for n in nf if n not in of]
audit=dict(ancestor=str(ANCESTOR),donor=str(DONOR),base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),changed_functions=changed,new_functions=added,object_changes={})
def merge_function(name,current):
    if current==of[name]:return nf[name]
    if current==nf[name]:return current
    with tempfile.TemporaryDirectory(prefix='mundo-merge-') as temp:
        paths=[Path(temp)/n for n in ['target.j','ancestor.j','mundo.j']]
        for p,s in zip(paths,[current,of[name],nf[name]]):p.write_text(s+'\n',encoding='utf8')
        result=subprocess.run(['git','merge-file','-p',*map(str,paths)],capture_output=True,text=True)
        if result.returncode!=0:
            (R/(name+'-conflict.txt')).write_text(result.stdout+'\n'+result.stderr)
            raise AssertionError('Resolve overlapping edits in '+name)
        return result.stdout.rstrip('\n')
def patch(s):
    fs=functions(s)
    for n in changed:
        if n in fs:s=s.replace(fs[n],merge_function(n,fs[n]),1)
    # Place new functions before their next ancestor function, preserving declaration order.
    group=[]
    for n in nf:
        if n in added:group.append(n)
        else:
            if group and n in fs:
                pending=[]
                for a in group:
                    if a in fs:assert fs[a]==nf[a],('Conflicting added function',a)
                    else:pending.append(nf[a])
                if pending:
                    anchor=functions(s)[n];s=s.replace(anchor,'\n\n'.join(pending)+'\n\n'+anchor,1)
            group=[]
    if re.search(r'^globals\b',s,re.M) and 'hashtable MW_Hash' not in s:
        s=s.replace('\nendglobals','\nhashtable MW_Hash = null\nendglobals',1)
    return s
runtime=patch(norm(target['war3map.j']));(O/'war3map.j').write_text(runtime,encoding='utf8')
tf=functions(norm(target['war3map.j']));rf=functions(runtime)
assert all(rf[n]==f for n,f in tf.items() if n not in changed and n not in added)
audit['changed_functions']=[n for n in tf if tf[n]!=rf[n]]
audit['new_functions']=[n for n in rf if n not in tf]
w=target['war3map.wct'];p=w.index(0,8)+1;prefix=w[:p];chunks=[]
while p<len(w):
    size=struct.unpack_from('<I',w,p)[0];p+=4;b=w[p:p+size];p+=size
    s=patch(norm(b.rstrip(b'\0')))
    chunks.append(s.encode('utf8')+(b'\0' if b.endswith(b'\0') else b''))
assert p==len(w)
(O/'war3map.wct').write_bytes(prefix+b''.join(struct.pack('<I',len(b))+b for b in chunks))
editor='\n'.join(norm(b.rstrip(b'\0')) for b in chunks);ef=functions(editor)
for n in changed+added:assert ef[n]==rf[n],('Runtime/editor mismatch',n)
header=re.search(r'(?ms)^globals\b(.*?)^endglobals',editor)[1];packed=re.search(r'(?ms)^globals\b(.*?)^endglobals',runtime)[1]
gnames=lambda s:set(re.findall(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',s,re.M))
sources=gnames(header);extras=[]
for line in packed.splitlines():
    m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
    if m and m[1] not in sources and not line.lstrip().startswith('//'):extras.append(line)
regen=re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:ef.get(m[1],m[0]),runtime)
regen=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+header+'\n'+'\n'.join(extras)+'\nendglobals',regen,count=1)
(R/'editor-validation.j').write_text(regen,encoding='utf8')
for name in ['war3map.w3a','war3map.w3u','war3map.w3h']:
    parsed=[]
    for prefix,data in [('ancestor',old),('mundo',ours),('before',target)]:
        path=R/(prefix+'-'+name);path.write_bytes(data[name]);d=objdata.load(str(path));assert objdata.dump(d)==data[name];parsed.append(d)
    a,b,d=parsed;changes=[]
    for table in range(2):
        key=lambda e:(e['oldId'],e['newId'])
        am={key(e):e for e in a['tables'][table]};bm={key(e):e for e in b['tables'][table]};dm={key(e):e for e in d['tables'][table]}
        assert am.keys()<=bm.keys(),'Mundo removed an ancestor object'
        for k,be in bm.items():
            if k not in am:
                if k in dm:assert dm[k]==be,('New object collision',k)
                else:d['tables'][table].append(copy.deepcopy(be));changes.append(dict(object=k,added=True))
                continue
            if am[k]==be:continue
            assert k in dm,('Target lost required object',k)
            ae,de=am[k],dm[k]
            mk=lambda m:(m['id'],m.get('level'),m.get('ptr'))
            av={mk(m):m for m in ae['mods']};bv={mk(m):m for m in be['mods']};dv={mk(m):m for m in de['mods']}
            for field in av.keys()|bv.keys():
                if av.get(field)==bv.get(field):continue
                assert dv.get(field) in [av.get(field),bv.get(field)],('Object field conflict',k,field)
                de['mods']=[m for m in de['mods'] if mk(m)!=field]
                if field in bv:de['mods'].append(copy.deepcopy(bv[field]))
                changes.append(dict(object=k,field=field))
    (O/name).write_bytes(objdata.dump(d));audit['object_changes'][name]=changes
cloudmanifest=json.loads((W/'mundo-cloud-ramp/changes.json').read_text());imports=cloudmanifest['imports']
imp=target['war3map.imp'];version,count=struct.unpack_from('<II',imp);addimports=[n for n in imports if n.encode()+b'\0' not in imp]
(O/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(addimports))+imp[8:]+b''.join(b'\r'+n.encode()+b'\0' for n in addimports))
for n in imports:
    p=Path(n.replace('\\','/'));(O/p).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/'mundo-cloud-ramp/src'/p,O/p)
maintenance=ours['FF_MAINTENANCE.md'][len(old['FF_MAINTENANCE.md']):]
assert ours['FF_MAINTENANCE.md'].startswith(old['FF_MAINTENANCE.md'])
(O/'FF_MAINTENANCE.md').write_bytes(target['FF_MAINTENANCE.md']+maintenance+b'\nMundo merged onto UI label repair; UI repair archive members preserved and validated.\n')
audit['imports']=imports
(R/'changes.json').write_text(json.dumps(audit,indent=2))
print(json.dumps(audit,indent=2))
