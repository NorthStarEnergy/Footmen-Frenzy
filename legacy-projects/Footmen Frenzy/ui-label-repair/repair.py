from pathlib import Path
import sys,re,json,hashlib,shutil,io
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'hero-polish'))
from archive_helpers import *
R=Path(__file__).resolve().parent;W=R.parent
DONOR=W/'tf-orb-v53/release/FF799X_Rx_TF_Guardian_HealOrbs_v53.w3x'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def repair(base,tag):
 out=R/'release'/('FF799X_Rx_'+tag+'_UI_Labels_Icons_Fixed.w3x');out.parent.mkdir(exist_ok=True)
 src=R/tag;src.mkdir(exist_ok=True);h=c.c_void_p();dh=c.c_void_p()
 assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h));assert storm.SFileOpenArchive(str(DONOR),0,0x100,c.byref(dh))
 names=[x['path'] for x in json.loads((W/'size-audit-v50/archive-files.json').read_text())]
 imp=read_storm(h,'war3map.imp');version,count=struct.unpack_from('<II',imp);pos=8
 for _ in range(count):
  flag=imp[pos];pos+=1;end=imp.index(0,pos);name=imp[pos:end].decode('latin1');pos=end+1
  names.append(name if flag in (10,13) else 'war3mapImported\\'+name)
 names=list(dict.fromkeys(names))

 changes={};restored=[];readable={}
 for n in names:
  if n.startswith('('):continue
  try:b=read_storm(h,n)
  except (AssertionError,ValueError):
   if not archive(base).get_hash_table_entry(n):continue
   b=read_storm(dh,n);changes[n]=b;restored.append(n);continue
  readable[n]=hashlib.sha256(b).hexdigest()
  if n.lower().endswith(('.wts','.fdf','.toc','.txt','.slk')) and b'\r\r' in b:
   fixed=re.sub(rb'\r{2,}\n',b'\r\n',b)
   assert fixed!=b and re.sub(rb'\r+\n',b'\n',fixed)==re.sub(rb'\r+\n',b'\n',b)
   changes[n]=fixed
 assert 'war3map.wts' in changes
 oldwts=read_storm(h,'war3map.wts');newwts=changes['war3map.wts']
 for n,b in changes.items():
  if n.endswith('.blp'):
   assert b[:4] in [b'BLP1',b'BLP2'];assert struct.unpack_from('<II',b,12)==(64,64)
  if n.endswith('.mdx'):assert b[:4]==b'MDLX'
 storm.SFileCloseArchive(h);storm.SFileCloseArchive(dh)
 shutil.copy2(base,out);assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
 for n,b in changes.items():
  f=src/n.replace('\\','/');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
  assert storm.SFileAddFileEx(h,str(f),n.encode(),0x80000200,2,2),n
 assert storm.SFileCloseArchive(h)
 before,after=archive(base),archive(out);be,ae=entries(before),entries(after);allowed=set()
 for n in list(changes)+['(listfile)','(attributes)','(signature)']:
  for a in [before,after]:
   e=a.get_hash_table_entry(n)
   if e:allowed.add((e.hash_a,e.hash_b,e.locale,e.platform))
 assert all(ae.get(k)==v for k,v in be.items() if k not in allowed)
 assert all(k in be or k in allowed for k in ae)
 assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
 for n,digest in readable.items():
  b=read_storm(h,n)
  if n not in changes:assert hashlib.sha256(b).hexdigest()==digest,n
 for n,b in changes.items():assert read_storm(h,n)==b,n
 assert b'\r\r' not in read_storm(h,'war3map.wts')
 assert read_storm(h,'war3map.j')==before.read_file('war3map.j')
 assert read_storm(h,'war3map.wct')==before.read_file('war3map.wct')
 storm.SFileCloseArchive(h)
 records=re.findall(rb'STRING (\d+)',newwts);assert len(records)==len(set(records))
 report={'base':str(base),'base_sha256':sha(base),'output':str(out),'sha256':sha(out),'restored_assets':restored,'changed_payloads':list(changes),'repaired_string_line_endings':len(re.findall(rb'\r{2,}\n',oldwts)),'string_records_preserved':len(records),'readable_payloads_reverified':len(readable)+len(restored),'unchanged_archive_entries':sum(k not in allowed for k in be),'runtime_and_editor_scripts_byte_identical':True,'engine_playtested':False}
 (R/(tag+'-verification.json')).write_text(json.dumps(report,indent=2));out.with_suffix('.sha256').write_text(sha(out)+'  '+out.name+'\n');print(json.dumps(report,indent=2));return report
if __name__=='__main__':
 if len(sys.argv)>1:repair(Path(sys.argv[1]).resolve(),sys.argv[2])
 else:
  repair(W/'pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x','v67')
  repair(W/'stalker-v71/release/FF799X_Rx_Stalker_v71.w3x','v71')
