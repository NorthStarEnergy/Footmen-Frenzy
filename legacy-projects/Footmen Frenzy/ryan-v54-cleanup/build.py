import sys,struct,shutil,json,hashlib,ctypes
from pathlib import Path
R=Path('ryan-v54-cleanup').resolve();W=R.parent;sys.path.insert(0,str(W/'hero-polish'));from archive_helpers import storm,read_storm,c,archive,entries
base=R/'source/FF799X_Rx_UI_Startup_v54.w3x';a=archive(base);before=entries(a)
names=['war3mapImported\\warstomp.PNG','war3mapImported\\healspray.PNG','war3mapImported\\Windwalk.PNG','war3mapImported\\Wight.png','war3mapImported\\WightScythe.png','war3mapImported\\WightSpirits.png','war3mapImported\\BTNHeroTrollGodSlayer.png','ReplaceableTextures\\CommandButtons\\BTNLoadedDice.tga','ReplaceableTextures\\CommandButtonsDisabled\\DISBTNLoadedDice.tga']
ignore=set()
for n in names+['war3map.imp','(listfile)','(attributes)','(signature)']:
 e=a.get_hash_table_entry(n)
 if n in names:assert e,n
 if e:ignore.add((e.hash_a,e.hash_b,e.locale,e.platform))
for name in names:
 leaf=name.split('\\')[-1].encode().lower()
 assert not any(leaf in v.lower() for k,v in before.items() if k not in ignore and isinstance(v,bytes)),name
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h));imp=read_storm(h,'war3map.imp');assert storm.SFileCloseArchive(h)
v,count=struct.unpack_from('<II',imp);pos=8;keep=[];removed=[]
for _ in range(count):
 start=pos;flag=imp[pos];pos+=1;end=imp.index(0,pos);path=imp[pos:end].decode('latin1');pos=end+1;full=path if flag in (10,13) else 'war3mapImported\\'+path
 if full.lower() in {n.lower() for n in names}:removed.append(full)
 else:keep.append(imp[start:pos])
assert len(removed)==len(names),(removed,names)
newimp=struct.pack('<II',v,len(keep))+b''.join(keep);(R/'src/war3map.imp').write_bytes(newimp)
stage=R/'stage.w3x';shutil.copy2(base,stage);storm.SFileRemoveFile.argtypes=[c.c_void_p,c.c_char_p,c.c_uint];storm.SFileRemoveFile.restype=c.c_bool
h=c.c_void_p();assert storm.SFileOpenArchive(str(stage),0,0,c.byref(h))
for n in names:assert storm.SFileRemoveFile(h,n.encode(),0),n
assert storm.SFileAddFileEx(h,str(R/'src/war3map.imp'),b'war3map.imp',0x80000200,2,2);assert storm.SFileCloseArchive(h)
# Repack compressed blocks byte-for-byte. The only encrypted block is optional
# StormLib attributes metadata, whose fixed key depends on its old position.
# Exclude it; keep all other hash entries, including unnamed files.
a=archive(stage);attrs=a.get_hash_table_entry('(attributes)');assert attrs and a.block_table[attrs.block_table_index].flags & 0x10000
live={e.block_table_index for e in a.hash_table if e.block_table_index<len(a.block_table)};encrypted=[i for i in live if a.block_table[i].flags & 0x10000];assert encrypted==[attrs.block_table_index],encrypted
hashes=list(a.hash_table);idx=next(i for i,e in enumerate(hashes) if e==attrs);hashes[idx]=hashes[idx]._replace(block_table_index=0xfffffffe)
blocks=list(a.block_table);out=R/'release/FF799X_Rx_UI_Startup_Clean_v55.w3x';data=stage.read_bytes();header=a.header;assert data[:4]==b'MPQ\x1a' and header['format_version']==0
with out.open('wb') as f:
 f.write(b'\0'*32)
 for i in sorted(live-{attrs.block_table_index},key=lambda j:blocks[j].offset):
  b=blocks[i];blob=data[b.offset:b.offset+b.archived_size];assert len(blob)==b.archived_size;off=f.tell();f.write(blob);blocks[i]=b._replace(offset=off)
 blocks[attrs.block_table_index]=blocks[attrs.block_table_index]._replace(offset=0,archived_size=0,size=0,flags=0)
 def encrypt(data,key):
  seed1=key;seed2=0xEEEEEEEE;out=bytearray()
  for (v,) in struct.iter_unpack('<I',data):
   seed2=(seed2+a.encryption_table[0x400+(seed1&255)])&0xffffffff;out+=struct.pack('<I',(v^(seed1+seed2))&0xffffffff);seed1=(((~seed1<<21)+0x11111111)|(seed1>>11))&0xffffffff;seed2=(v+seed2+(seed2<<5)+3)&0xffffffff
  return out
 hashpos=f.tell();ht=b''.join(struct.pack('<2I2HI',*e) for e in hashes);f.write(encrypt(ht,a._hash('(hash table)','TABLE')))
 blockpos=f.tell();bt=b''.join(struct.pack('<4I',*e) for e in blocks);f.write(encrypt(bt,a._hash('(block table)','TABLE')));total=f.tell();f.seek(0);f.write(struct.pack('<4s2I2H4I',b'MPQ\x1a',32,total,0,header['sector_size_shift'],hashpos,blockpos,len(hashes),len(blocks)))
# Verify the entire pre-existing payload set, including unnamed compressed blocks.
z=archive(out);after=entries(z);skipped=set()
for n in names+['war3map.imp','(listfile)','(attributes)','(signature)']:
 e=archive(base).get_hash_table_entry(n)
 if e:skipped.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in before.items():
 if k not in skipped:assert after.get(k)==v,('payload changed',k)
for n in names:assert z.get_hash_table_entry(n) is None,n
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h));assert read_storm(h,'war3map.imp')==newimp;assert read_storm(h,'war3map.j')==read_storm(h,'war3map.j');assert storm.SFileCloseArchive(h)
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n');report={'base':str(base),'output':str(out),'sha256':sha,'before_bytes':base.stat().st_size,'after_bytes':out.stat().st_size,'saved_bytes':base.stat().st_size-out.stat().st_size,'removed_imports':removed,'excluded_metadata':'optional MPQ (attributes) metadata, encrypted with offset-dependent key','verified_preserved_payloads':len(before.keys()-skipped),'live_game_test':'pending'};(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
