import sys,struct,re,json,csv
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src';S.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c,archive,entries,functions,objdata
base=W/'ryan-v54-cleanup/release/FF799X_Rx_UI_Startup_Clean_v55.w3x';a=archive(base);h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
script=read_storm(h,'war3map.j').decode('latin1');wct=read_storm(h,'war3map.wct');jfs=functions(script);print('Read runtime',len(jfs),flush=True)
pos=wct.index(0,8)+1;prefix=wct[:pos];chunks=[]
while pos<len(wct):
 n=struct.unpack_from('<I',wct,pos)[0];pos+=4;assert pos+n<=len(wct);chunks.append(wct[pos:pos+n]);pos+=n
assert pos==len(wct)
ed='\n'.join(x.rstrip(b'\0').decode('latin1') for x in chunks);efs=functions(ed)
print('Read editor chunks',len(chunks),len(efs),flush=True)
audit=json.loads((W/'ryan-v54-cleanup/audit/summary.json').read_text());remove=set(audit['unreachable_functions'])&efs.keys()
def strip(s,ns):
 return re.sub(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',lambda m:'' if m[1] in ns else m[0],s)
# Retain functions referenced by globals, editor wrappers, and any retained code.
while True:
 rest=strip(script,remove)+'\n'+strip(ed,remove);used=set(re.findall(r'\b[A-Za-z_]\w*\b',rest));keep=remove&used
 if not keep:break
 remove-=keep
print('Selected removal',len(remove),flush=True)
newscript=strip(script,remove);newchunks=[]
for chunk in chunks:
 txt=chunk.rstrip(b'\0').decode('latin1');newchunks.append(strip(txt,remove).encode('latin1')+(b'\0' if chunk.endswith(b'\0') else b''))
newwct=prefix+b''.join(struct.pack('<I',len(x))+x for x in newchunks)
nf=functions(newscript);ef=functions('\n'.join(x.decode('latin1') for x in newchunks))
assert all(n not in nf and n not in ef for n in remove)
assert all(nf[n]==b for n,b in jfs.items() if n not in remove)
(S/'war3map.j').write_bytes(newscript.encode('latin1'));(S/'war3map.wct').write_bytes(newwct)
# Conservative object removal: direct and integer/raw binary references, plus computed ID families.
data=entries(a);blobs=[v for v in data.values() if isinstance(v,bytes)];unknown=sum(not isinstance(v,bytes) for v in data.values())
objects={};rawobjs={}
for ext in ['w3u','w3t','w3a','w3h','w3q','w3b','w3d']:
 n='war3map.'+ext;rawobjs[n]=read_storm(h,n);f=R/n;f.write_bytes(rawobjs[n]);objects[n]=objdata.load(str(f));assert objdata.dump(objects[n])==rawobjs[n]
storm.SFileCloseArchive(h)
# Scan remaining archive files; object tables are handled per record below.
other=[b for b in blobs if b not in rawobjs.values()]
dynamic=set(re.findall(r"'([A-Za-z0-9]{4})'\s*[+-]",script))
dynamic_prefixes={x[:2] for x in dynamic}
deleted=[];held=[]
for candidate in audit['object_candidates']:
 ident=candidate['id'];raw=ident.encode('latin1');num=int.from_bytes(raw,'big');patterns=[raw,raw[::-1],str(num).encode(),hex(num)[2:].encode()]
 reason=None
 if ident[:2] in dynamic_prefixes:reason='computed rawcode family'
 if not reason and any(any(p in b for p in patterns) for b in other):reason='archive reference or metadata mention'
 if not reason:
  for n,ob in objects.items():
   for ti,table in enumerate(ob['tables']):
    for e in table:
     eid=e['newId'] if ti else e['oldId']
     if eid==ident:continue
     if e['oldId']==ident or any((isinstance(m['value'],int) and m['value']==num) or (isinstance(m['value'],str) and (ident in m['value'] or ident[::-1] in m['value'])) for m in e['mods']):reason='object reference'
 if reason:held.append({'id':ident,'reason':reason});continue
 # Unknown compressed archive members prevent claiming full reference coverage;
 # remove only candidates with empty modifications (identical copies of base).
 match=[(n,e) for n,ob in objects.items() for e in ob['tables'][1] if e['newId']==ident]
 assert len(match)==1
 n,e=match[0]
 if unknown and e['mods']:held.append({'id':ident,'reason':'unreadable archive members; nonempty custom object retained'});continue
 objects[n]['tables'][1].remove(e);deleted.append({'id':ident,'kind':candidate['kind'],'parent':e['oldId']})
for n,ob in objects.items():
 raw=objdata.dump(ob)
 if raw!=rawobjs[n]:(S/n).write_bytes(raw)
# Editor syntax-check wrapper: use original generated map functions/declarations,
# and replace every shared runtime function with the edited authoritative source.
editorfunc=functions('\n'.join(x.decode('latin1') for x in newchunks))
wrapper=newscript
for n,b in functions(newscript).items():
 if n in editorfunc:wrapper=wrapper.replace(b,editorfunc[n])
(R/'editor-validation.j').write_bytes(wrapper.encode('latin1'))
report={'base':str(base),'removed_functions':sorted(remove),'removed_objects':deleted,'retained_object_candidates':held,'computed_rawcode_bases':sorted(dynamic),'unreadable_archive_members':unknown,'runtime_bytes_saved':len(script)-len(newscript),'editor_bytes_saved':len(wct)-len(newwct),'wct_chunks':len(chunks),'changed_files':[f.name for f in S.iterdir()]}
(R/'changes.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['removed_functions','retained_object_candidates']},indent=2));print('Removed functions:',len(remove),'retained object candidates:',len(held))
