import sys,struct,shutil,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import archive,entries,storm,read_storm,c
base=R/'base.w3x';stage=R/'stage.w3x';shutil.copy2(base,stage)
for log in ['compiler.log']:
 s=(R/log).read_text();assert 'Parse successful:' in s and 'Parse failed' not in s
h=c.c_void_p();assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h))
changed=[]
for f in (R/'src').iterdir():
 assert storm.SFileAddFileEx(h,str(f),f.name.encode(),0x80000200,2,2);changed.append(f.name)
assert storm.SFileCloseArchive(h)
a=archive(stage);hashes=list(a.hash_table);blocks=list(a.block_table);attrs=a.get_hash_table_entry('(attributes)')
if attrs:
 idx=next(i for i,e in enumerate(hashes) if e==attrs);hashes[idx]=hashes[idx]._replace(block_table_index=0xfffffffe)
live={e.block_table_index for e in hashes if e.block_table_index<len(blocks)}
assert not any(blocks[i].flags&0x10000 for i in live),'unexpected encrypted payload'
out=R/'release/FF799X_Rx_Mundo_Cloud_v64.w3x';out.parent.mkdir(exist_ok=True);data=stage.read_bytes();assert data[:4]==b'MPQ\x1a'
def encrypt(data,key):
 seed1=key;seed2=0xEEEEEEEE;result=bytearray()
 for (v,) in struct.iter_unpack('<I',data):
  seed2=(seed2+a.encryption_table[0x400+(seed1&255)])&0xffffffff;result+=struct.pack('<I',(v^(seed1+seed2))&0xffffffff);seed1=(((~seed1<<21)+0x11111111)|(seed1>>11))&0xffffffff;seed2=(v+seed2+(seed2<<5)+3)&0xffffffff
 return result
with out.open('wb') as f:
 f.write(b'\0'*32)
 for i in sorted(live,key=lambda i:blocks[i].offset):
  b=blocks[i];off=f.tell();f.write(data[b.offset:b.offset+b.archived_size]);blocks[i]=b._replace(offset=off)
 hp=f.tell();f.write(encrypt(b''.join(struct.pack('<2I2HI',*e) for e in hashes),a._hash('(hash table)','TABLE')))
 bp=f.tell();f.write(encrypt(b''.join(struct.pack('<4I',*e) for e in blocks),a._hash('(block table)','TABLE')));total=f.tell();f.seek(0);f.write(struct.pack('<4s2I2H4I',b'MPQ\x1a',32,total,0,a.header['sector_size_shift'],hp,bp,len(hashes),len(blocks)))
old=archive(base);before=entries(old);after=entries(archive(out));skip=set()
for n in changed+['(attributes)','(listfile)','(signature)']:
 e=old.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in before.items():
 if k not in skip:assert after.get(k)==v,('changed unexpected payload',k)
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in changed:assert read_storm(h,n)==(R/'src'/n).read_bytes()
storm.SFileCloseArchive(h)
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report={'output':str(out),'sha256':sha,'before_bytes':base.stat().st_size,'after_bytes':out.stat().st_size,'saved_bytes':base.stat().st_size-out.stat().st_size,'removed_functions':0,'removed_objects':0,'preserved_payloads':len(before.keys()-skip),'runtime_jass':'passed','editor_function_body_syntax':'changed functions match runtime; independent editor compilation not performed','editor_save_and_live_game_test':'pending','changed_files':changed}
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
