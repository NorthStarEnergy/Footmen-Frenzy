from pathlib import Path
import struct,sys
sys.path.insert(0,str(Path(__file__).parent/'tools'))
from objdata import Reader
r=Reader((Path(__file__).parent/'base/files/war3map.w3i').read_bytes());r.o=r.d.index(struct.pack('<6i',24,0,1,1,64,1));print('start',r.o,r.i32())
for i in range(24):
 print(r.o,[r.i32() for _ in range(5)],r.cstr(),[r.f32() for _ in range(2)],[r.i32() for _ in range(4)])
n=r.i32();print('force',n)
for i in range(n):print(r.i32(),r.i32(),r.cstr())
print('end',r.o,'tail',r.d[r.o:].hex())
