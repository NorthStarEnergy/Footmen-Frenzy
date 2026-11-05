from archive_helpers import *
from checks import run
R=Path(__file__).resolve().parent;W=R.parent
for variant in ['799x','mini','solo']:
 V=R/variant;O=V/'src';m=json.loads((V/'changes.json').read_text());base=Path(m['base']);output=R/'release'/m['filename'];output.parent.mkdir(exist_ok=True)
 run(V,variant)
 s=(O/'war3map.j').read_text(encoding='utf8');scripts=[O/'war3map.j']
 if variant=='solo':
  code=(W/'six-player-ffa/editor_source.py').read_text().replace("R=Path(__file__).parent;O=R/'src'","R=Path("+repr(str(V))+");O=R/'src'").replace('Solo Foots 6 Player FFA v1 source','Solo Foots 6 Player FFA v3 source')
  code=code.replace("(O/'war3map.j').read_text()", "(O/'war3map.j').read_text(encoding='utf8')").replace('.write_text(wrapper)', ".write_text(wrapper,encoding='utf8')")
  exec(compile(code,'editor_source.py','exec'),{'__file__':str(W/'six-player-ffa/editor_source.py')});scripts.append(V/'editor-validation.j')
 for script in scripts:
  result=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(script)],capture_output=True,text=True)
  (V/'audit'/(script.name+'.compiler.log')).write_text(result.stdout+result.stderr)
  assert result.returncode==0,result.stdout+result.stderr
 original=archive(base);h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
 originalscript=read_storm(h,'war3map.j').decode('utf-8-sig');bf,sf=functions(originalscript),functions(s)
 for n in bf:
  if n not in m['changed_functions']:assert bf[n].replace('\r\n','\n')==sf[n],n
 changed=[]
 for file in sorted(O.rglob('*')):
  if file.is_file():
   name=str(file.relative_to(O)).replace('/','\\')
   if not original.get_hash_table_entry(name) or read_storm(h,name)!=file.read_bytes():changed.append((name,file))
 # No unrelated payloads may enter this incremental update.
 allowed={'war3map.j','war3map.w3u','war3map.w3a','war3mapSkin.w3u','war3map.wts','war3map.w3i','war3map.wct','war3map.wtg'}|{'Spells\\Orianna\\Feedback\\'+n+'.blp' for n in ['AttackGround','ProtectGround','ShockGround','ShockImpact','MoveGround']}
 assert all(name in allowed for name,f in changed),[n for n,f in changed if n not in allowed]
 for filename in ['war3map.w3u','war3map.w3a','war3mapSkin.w3u']:
  old=V/'audit'/filename;old.write_bytes(read_storm(h,filename))
  before=objdata.load(str(old));after=objdata.load(str(O/filename));assert objdata.dump(after)==(O/filename).read_bytes()
  key=lambda e:e['newId'] if e['newId']!='\0'*4 else e['oldId']
  new={key(e):e for t in after['tables'] for e in t}
  for t in before['tables']:
   for e in t:
    if key(e) not in ['HGr1','AGr2','AOz2','AOz4']:assert new[key(e)]==e,key(e)
 assert storm.SFileCloseArchive(h)
 shutil.copy2(base,output);assert storm.SFileOpenArchive(str(output),0,0,c.byref(h))
 for name,file in changed:assert storm.SFileAddFileEx(h,str(file),name.encode(),0x80000200,2,2),name
 assert storm.SFileCloseArchive(h)
 raw=output.read_bytes()
 if raw[:4]==b'HM3W':
  end=raw.index(0,8);header=b'HM3W'+raw[4:8]+m['title'].encode()+b'\0'+raw[end+1:end+9]
  output.write_bytes(header+bytes(512-len(header))+raw[512:])
 result=archive(output);before,after=entries(original),entries(result);skip=set()
 assert storm.SFileOpenArchive(str(output),0,0x100,c.byref(h))
 for name,file in changed:
  assert read_storm(h,name)==file.read_bytes(),name
  e=original.get_hash_table_entry(name)
  if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
 assert storm.SFileCloseArchive(h)
 for name in ['(listfile)','(attributes)','(signature)']:
  e=original.get_hash_table_entry(name)
  if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
 for k,data in before.items():
  if k not in skip:assert after.get(k)==data,k
 digest=hashlib.sha256(output.read_bytes()).hexdigest();output.with_suffix('.sha256').write_text(digest+'  '+output.name+'\n')
 report=dict(passed=True,output=str(output),sha256=digest,changed_payloads=[n for n,f in changed],preserved_archive_entries=len(before.keys()-skip),preserved_functions=len(bf)-len(m['changed_functions']),engine_test='Pending')
 (V/'verification.json').write_text(json.dumps(report,indent=2));print(variant,report,flush=True)
