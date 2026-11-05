from pathlib import Path
import sys,re,json,io,struct,hashlib,subprocess,ctypes as c,shutil,ast
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'799x-backport/tools'),str(W/'mini-foots/tools'),str(W/'799x-backport')]
from mpyq import MPQArchive
import objdata
def archive(path):
 raw=path.read_bytes();return MPQArchive(io.BytesIO(raw[512:] if raw[:4]==b'HM3W' else raw),listfile=False)
def entries(a):
 out={};original=a.get_hash_table_entry
 for e in a.hash_table:
  if e.block_table_index>=len(a.block_table):continue
  a.get_hash_table_entry=lambda _,e=e:e
  try:
   b=a.block_table[e.block_table_index]
   if b.archived_size==b.size and not b.flags & 0x10000:
    a.file.seek(b.offset+a.header['offset']);data=a.file.read(b.size)
   else:data=a.read_file('ignored')
  except (RuntimeError,NotImplementedError):
   b=a.block_table[e.block_table_index];a.file.seek(b.offset+a.header['offset']);data=(b.flags,b.size,a.file.read(b.archived_size))
  out[e.hash_a,e.hash_b,e.locale,e.platform]=data
 a.get_hash_table_entry=original;return out
def functions(s):return {m[1]:m[0] for m in re.finditer(r'(?ms)^[ \t]*function (\w+)\b.*?^[ \t]*endfunction',s)}
work=Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work')
donor=(R/'donor/base/war3map.j').read_text(encoding='utf-8-sig');df=functions(donor)
storm=c.WinDLL(str(work/'stormlib/x64/StormLib.dll'))
storm.SFileOpenArchive.argtypes=[c.c_wchar_p,c.c_uint,c.c_uint,c.POINTER(c.c_void_p)]
storm.SFileAddFileEx.argtypes=[c.c_void_p,c.c_wchar_p,c.c_char_p,c.c_uint,c.c_uint,c.c_uint]
storm.SFileCloseArchive.argtypes=[c.c_void_p]
storm.SFileOpenFileEx.argtypes=[c.c_void_p,c.c_char_p,c.c_uint,c.POINTER(c.c_void_p)]
storm.SFileGetFileSize.argtypes=[c.c_void_p,c.c_void_p]
storm.SFileReadFile.argtypes=[c.c_void_p,c.c_void_p,c.c_uint,c.POINTER(c.c_uint),c.c_void_p]
storm.SFileCloseFile.argtypes=[c.c_void_p]
def read_storm(h,name):
 f=c.c_void_p();assert storm.SFileOpenFileEx(h,name.encode(),0,c.byref(f)),name
 raw=c.create_string_buffer(storm.SFileGetFileSize(f,None));count=c.c_uint()
 assert storm.SFileReadFile(f,raw,len(raw),c.byref(count),None),name
 assert storm.SFileCloseFile(f);return raw.raw
for variant in ['mini','solo']:
 V=R/variant;O=V/'src';B=V/'base';m=json.loads((V/'migration.json').read_text());(V/'audit').mkdir(exist_ok=True)
 s=(O/'war3map.j').read_text(encoding='utf-8-sig');sf=functions(s);bf=functions((B/'war3map.j').read_text(encoding='utf-8-sig'));checks=[]
 def check(value,label):assert value,label;checks.append(label)
 for n in m['hero_functions']:check(sf[n]==df[n],'Donor hero function '+n)
 allowed=set(m['hero_functions'])|{'main','config','Trig_set_hero_stats_Actions','Trig_set_hero_numbers_Actions','MF_HeroDisabled','MF_Init'}
 for n in bf:
  if n not in allowed:
   expected=bf[n].replace('Mini Foots v8','Mini Foots v9') if variant=='mini' else bf[n].replace('Solo Foots 6 Player FFA v1','Solo Foots 6 Player FFA v2')
   check(sf[n]==expected,'Unrelated function preserved '+n)
 for ext in ['w3u','w3a','w3h']:
  old=objdata.load(str(B/('war3map.'+ext)));new=objdata.load(str(O/('war3map.'+ext)))
  check(objdata.dump(new)==(O/('war3map.'+ext)).read_bytes(),'Object roundtrip '+ext)
  key=lambda e:e['newId'] if e['newId']!='\0'*4 else e['oldId']
  ni={key(e):e for t in new['tables'] for e in t}
  for t in old['tables']:
   for e in t:
    if key(e) not in m['objects']:check(ni[key(e)]==e,'Unrelated object '+key(e))
 check('set udg_hero_category[72]=1' in s,'Guardian enabled')
 if variant=='mini':check("id == 'H043'" not in sf['MF_HeroDisabled'] and "'H043', 0)" not in sf['MF_Init'],'Guardian policy enabled')
 else:
  check('SetPlayers(6)' in sf['config'] and 'SetTeams(6)' in sf['config'],'Solo keeps six slots and teams')
  check('set udg_total_hero_count=93' in s and "set udg_hero_type[92]='HOr1'" in s and "set udg_hero_type[93]='HGr1'" in s,'Solo registers both new heroes')
 for harness in ['check_runtime.py','check_gragus.py','check_guardian.py','check_guardian_bolts.py']:
  code=(W/'799x-backport'/harness).read_text()
  code=code.replace('ROOT=Path(__file__).resolve().parent','ROOT=Path('+repr(str(V))+')')
  code=code.replace("(ROOT/'check_runtime.py')","(Path("+repr(str(W/'799x-backport'))+")/'check_runtime.py')")
  code=code.replace("(ROOT/'audit/v18-before-guardian/war3map.j')","(Path("+repr(str(W/'799x-backport'))+")/'audit/v18-before-guardian/war3map.j')")
  if variant=='solo':code=code.replace("assert \"id == 'H043'\" not in functions['MF_HeroDisabled']", "assert \"'H043'\" not in functions['SoloFootsIsNoMuteHeroType']")
  exec(compile(code,harness,'exec'),{'__file__':str(W/'799x-backport'/harness),'__name__':'__main__'})
  check(True,'Behavior harness '+harness)
 scripts=[O/'war3map.j']
 if variant=='solo':
  code=(W/'six-player-ffa/editor_source.py').read_text().replace("R=Path(__file__).parent;O=R/'src'","R=Path("+repr(str(V))+");O=R/'src'").replace('Solo Foots 6 Player FFA v1 source','Solo Foots 6 Player FFA v2 source')
  code=code.replace("(O/'war3map.j').read_text()", "(O/'war3map.j').read_text(encoding='utf8')").replace('.write_text(wrapper)', ".write_text(wrapper,encoding='utf8')")
  exec(compile(code,'editor_source.py','exec'),{'__file__':str(W/'six-player-ffa/editor_source.py')})
  scripts.append(V/'editor-validation.j')
 for script in scripts:
  run=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(script)],capture_output=True,text=True)
  (V/'audit'/(script.name+'.compiler.log')).write_text(run.stdout+run.stderr)
  check(run.returncode==0,'Compile '+str(script))
 output=R/'release'/(m['title']+'.w3x');output.parent.mkdir(exist_ok=True);shutil.copy2(m['base'],output)
 h=c.c_void_p();check(storm.SFileOpenArchive(str(output),0,0,c.byref(h)),'Open archive')
 for file in sorted(O.rglob('*')):
  if file.is_file():
   name=str(file.relative_to(O)).replace('/','\\')
   check(storm.SFileAddFileEx(h,str(file),name.encode(),0x80000200,2,2),'Pack '+name)
 check(storm.SFileCloseArchive(h),'Close archive')
 raw=output.read_bytes()
 if raw[:4]==b'HM3W':
  end=raw.index(0,8);tail=raw[end+1:end+9];header=b'HM3W'+raw[4:8]+m['title'].encode()+b'\0'+tail
  output.write_bytes(header+bytes(512-len(header))+raw[512:])
 base=archive(Path(m['base']));out=archive(output);before,after=entries(base),entries(out);allowed_entries=set()
 handle=c.c_void_p();assert storm.SFileOpenArchive(str(output),0,0x100,c.byref(handle))
 for file in O.rglob('*'):
  if file.is_file():
   name=str(file.relative_to(O)).replace('/','\\');check(read_storm(handle,name)==file.read_bytes(),'Packed bytes '+name)
   e=base.get_hash_table_entry(name)
   if e:allowed_entries.add((e.hash_a,e.hash_b,e.locale,e.platform))
 assert storm.SFileCloseArchive(handle)
 for name in ['(listfile)','(attributes)','(signature)']:
  e=base.get_hash_table_entry(name)
  if e:allowed_entries.add((e.hash_a,e.hash_b,e.locale,e.platform))
 preserved=0
 for k,data in before.items():
  if k not in allowed_entries:check(after.get(k)==data,'Untouched archive '+str(k));preserved+=1
 digest=hashlib.sha256(output.read_bytes()).hexdigest();output.with_suffix('.sha256').write_text(digest+'  '+output.name+'\n')
 report={'passed':len(checks),'preserved_archive_entries':preserved,'output':str(output),'sha256':digest,'engine_test':'Pending','checks':checks}
 (V/'verification.json').write_text(json.dumps(report,indent=2));print(variant,report['passed'],'checks;',preserved,'archive entries preserved;',digest,flush=True)
