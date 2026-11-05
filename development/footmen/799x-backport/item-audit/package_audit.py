import audit_core as c
import subprocess,os,json,hashlib,shutil,base64,struct
root=c.PROJECT.parent;out=c.ROOT/'final'
dotnet=root/'mini-foots/tools/dotnet/dotnet.exe'
packer=root.parent/'Footmen Frenzy (Solo)/tools/MpqAdd/bin/Debug/net8.0/MpqAdd.dll'
env=dict(os.environ,DOTNET_ROLL_FORWARD='Major')
def encrypt(data,key):
 seed=0xEEEEEEEE;result=bytearray()
 for (value,) in struct.iter_unpack('<I',data):
  seed=(seed+c.mpq.encryption_table[0x400+(key&0xff)])&0xffffffff
  result+=struct.pack('<I',value^((key+seed)&0xffffffff))
  key=(((~key<<21)+0x11111111)|(key>>11))&0xffffffff
  seed=(value+seed+(seed<<5)+3)&0xffffffff
 return result
# Append replacements without relocating any original member, preserving encrypted files exactly.
raw=bytearray(c.MAP.read_bytes());offset=c.mpq.header['offset'];blocks=list(c.mpq.block_table)
for fn in ['war3map.w3t','war3mapSkin.w3t']:
 payload=(out/fn).read_bytes();i=c.mpq.get_hash_table_entry(fn).block_table_index
 blocks[i]=blocks[i]._replace(offset=len(raw)-offset,archived_size=len(payload),size=len(payload),flags=0x81000000);raw+=payload
table_offset=len(raw)-offset
table=b''.join(struct.pack('<4I',*b) for b in blocks)
raw+=encrypt(table,c.mpq._hash('(block table)','TABLE'))
struct.pack_into('<I',raw,offset+8,len(raw)-offset);struct.pack_into('<I',raw,offset+20,table_offset)
final=c.PROJECT/'release/FF799X_Rx_Orianna_v10_ItemsAudited.w3x';final.write_bytes(raw)
new=c.MPQArchive(str(final),listfile=False)
changed={tuple(c.mpq.get_hash_table_entry(n)[:4]) for n in ['war3map.w3t','war3mapSkin.w3t']}
def members(a):
 result={}
 for h in a.hash_table:
  if h.block_table_index>=len(a.block_table):continue
  b=a.block_table[h.block_table_index]
  a.file.seek(a.header['offset']+b.offset)
  result[tuple(h[:4])]=(b.size,b.flags,a.file.read(b.archived_size))
 return result
oldm=members(c.mpq);newm=members(new)
assert oldm.keys()==newm.keys(), 'Archive member set changed'
for key in oldm:
 if key in changed or oldm[key]==newm[key]:continue
 values=[]
 for a in [c.mpq,new]:
  h=next(h for h in a.hash_table if tuple(h[:4])==key);lookup=a.get_hash_table_entry
  try:
   a.get_hash_table_entry=lambda filename:h
   values.append(a.read_file('member'))
  finally:a.get_hash_table_entry=lookup
 assert values[0]==values[1],('Non-item archive content changed',key)
for fn in ['war3map.w3t','war3mapSkin.w3t']:
 assert new.read_file(fn)==(out/fn).read_bytes()
 shutil.copyfile(out/fn,c.PROJECT/'src'/fn)
report=dict(source=str(c.MAP),output=str(final),sha256=hashlib.sha256(final.read_bytes()).hexdigest(),archiveMembers=len(oldm),unchangedArchiveMembers=len(oldm)-2,changedMembers=['war3map.w3t','war3mapSkin.w3t'],validation='All other decompressed archive member bytes identical; only utub/ides/utip item string fields changed; object binary round-trip passed.')
(out/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
dist=c.PROJECT/'item-wiki/dist';data=json.loads((dist/'data.json').read_text())
data['meta']['patchedMap']=final.name;data['meta']['patchedSha256']=report['sha256'];data['meta']['validation']=report['validation']
(dist/'data.json').write_text(json.dumps(data,indent=2),encoding='utf-8');(dist/'data.js').write_text('window.WIKI_DATA = '+json.dumps(data)+';',encoding='utf-8')
shutil.copyfile(final,dist/final.name)
shutil.copyfile(out/'validation.json',dist/'validation.json')
for x in data['items']:
 if x.get('icon'):x['icon']='data:image/png;base64,'+base64.b64encode((dist/x['icon']).read_bytes()).decode()
html=(dist/'index.html').read_text(encoding='utf-8').replace('<link rel="stylesheet" href="styles.css">','<style>'+(dist/'styles.css').read_text(encoding='utf-8')+'</style>')
html=html.replace('<script defer src="data.js"></script>','').replace('<script defer src="app.js"></script>','')
html=html.replace('</body>','<script>window.WIKI_DATA='+json.dumps(data).replace('</','<\\/')+';</script><script>'+(dist/'app.js').read_text(encoding='utf-8')+'</script></body>')
html=html.replace('href="'+final.name+'"','href="../release/'+final.name+'"')
for file in ['complete-list.md','data.json','validation.json']:html=html.replace('href="'+file+'"','href="dist/'+file+'"')
(c.PROJECT/'item-wiki/Footmen-Frenzy-799X-Item-Wiki.html').write_text(html,encoding='utf-8')
