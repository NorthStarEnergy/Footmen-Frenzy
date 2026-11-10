from pathlib import Path
import struct,sys
sys.path.insert(0,str(Path(__file__).parent/'tools'))
from objdata import Reader
r=Reader((Path(__file__).parent/'base/files/war3map.w3i').read_bytes())
print('header', [r.i32() for _ in range(7)])
print('strings',[r.cstr() for _ in range(4)])
print('bounds',[r.f32() for _ in range(8)],[r.i32() for _ in range(4)])
print('dimsflags', [r.i32() for _ in range(3)],r.raw(1))
print('loading',r.i32(),[r.cstr() for _ in range(4)])
print('game',r.i32(),[r.cstr() for _ in range(4)])
print('fog',r.i32(),[r.f32() for _ in range(3)],r.raw(4))
print('environment',r.raw(4),r.cstr(),r.raw(1),r.raw(4))
print('newfields', [r.i32() for _ in range(3)])
print('players offset',r.o,'count',r.i32())
for _ in range(24):
 print('p',r.o,[r.i32() for _ in range(4)],r.cstr(),[r.f32() for _ in range(2)],[r.i32() for _ in range(4)])
print('forces',r.o,r.i32())
