from pathlib import Path
import ctypes as c,re,struct,functools
O=Path(__file__).resolve().parent
lib=c.WinDLL(r'C:\Users\User\Documents\Codex\2026-10-20\brin\outputs\Google Drive Files\Old PC\Desktop\FF Map stuff\Map Archive\Testfoots\War3ModelEditor-v1.08\CascLib.dll',use_last_error=True);H=c.c_void_p;D=c.c_uint32
for n,args in [('CascOpenStorage',[c.c_char_p,D,c.POINTER(H)]),('CascOpenFile',[H,c.c_char_p,D,D,c.POINTER(H)]),('CascReadFile',[H,H,D,c.POINTER(D)]),('CascCloseFile',[H]),('CascCloseStorage',[H])]:
 f=getattr(lib,n);f.argtypes=args;f.restype=c.c_bool
lib.CascGetFileSize.argtypes=[H,c.POINTER(D)];lib.CascGetFileSize.restype=D
storage=H();assert lib.CascOpenStorage(b'C:/Program Files (x86)/Warcraft III',2,c.byref(storage))
@functools.lru_cache(maxsize=4096)
def game_read(name):
 f=H()
 if not lib.CascOpenFile(storage,name.encode('utf-8'),2,0,c.byref(f)):return None
 try:
  size=lib.CascGetFileSize(f,None)
  assert size<64000000
  buf=c.create_string_buffer(size);nr=D();assert lib.CascReadFile(f,buf,size,c.byref(nr));return buf.raw[:nr.value]
 finally:lib.CascCloseFile(f)
def ini(data):
 rows={};section=None
 for line in data.decode('utf-8-sig',errors='replace').splitlines():
  line=line.strip()
  if line.startswith('[') and line.endswith(']'):section=line[1:-1];rows.setdefault(section,{})
  elif section and '=' in line and not line.startswith('//'):
   k,v=line.split('=',1);rows[section][k]=v.strip('"')
 return rows
def slk(data):
 cells={};x=y=0
 for line in data.decode('utf-8-sig',errors='replace').splitlines():
  if not line.startswith('C;'):continue
  for part in re.findall(r'(?:[^;"\n]|"(?:[^"]|"")*")+',line)[1:]:
   if part.startswith('X'):x=int(part[1:])
   elif part.startswith('Y'):y=int(part[1:])
   elif part.startswith('K'):cells[x,y]=part[1:].strip('"')
 hdr={x:v for (x,y),v in cells.items() if y==1};rows={}
 for (x,y),v in cells.items():
  if y>1:rows.setdefault(y,{})[hdr.get(x,str(x))]=v
 return {r.get(hdr[1]):r for r in rows.values()}
def chunks(data):
 assert data[:4]==b'MDLX';at=4;result={}
 while at<len(data):
  tag=data[at:at+4].decode('ascii');size=struct.unpack_from('<I',data,at+4)[0];assert at+8+size<=len(data),(tag,size,len(data));result[tag]=data[at+8:at+8+size];at+=8+size
 assert at==len(data);return result
if __name__=='__main__':
 dest=O/'game-data';dest.mkdir(exist_ok=True)
 for file in ['units\\unitskin.txt','units\\unitui.slk','units\\itemdata.slk','units\\itemfunc.txt','units\\itemskin.txt','units\\unitmetadata.slk']:
  for prefix in ['war3.w3mod:','war3.w3mod:_balance\\custom_v1.w3mod:','war3.w3mod:_hd.w3mod:']:
   data=game_read(prefix+file)
   if data:
    (dest/(prefix+file).replace(':','_').replace('\\','_')).write_bytes(data)
    if file=='units\\unitskin.txt':print(prefix,ini(data).get('Udea'))
