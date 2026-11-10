from pathlib import Path
import sys,struct
sys.path.insert(0,str(Path(__file__).parent/'tools'))
from objdata import Reader
r=Reader((Path(__file__).parent/'base/files/war3mapUnits.doo').read_bytes())
print(r.raw(4),r.i32(),r.i32());n=r.i32();print(n)
for k in range(n):
 start=r.o;id=r.raw(4).decode();variation=r.i32();pos=[r.f32() for _ in range(3)];r.raw(16);skin=r.raw(4);flags=r.raw(1);owner=r.i32();r.raw(2);r.raw(8);table=r.i32();sets=r.i32()
 assert 0<=sets<100,(k,r.o,sets)
 for _ in range(sets):r.raw(8*r.i32())
 r.raw(24)
 inv=r.i32();assert 0<=inv<100,(k,id,r.o,inv)
 r.raw(inv*8);abilities=r.i32();assert 0<=abilities<100,(k,id,r.o,abilities)
 r.raw(abilities*12);mode=r.i32()
 if mode==0:r.raw(4)
 elif mode==1:r.raw(8)
 elif mode==2:r.raw(8*r.i32())
 else:raise Exception(k,id,r.o,mode)
 r.raw(12)
 if k<4 or id in ['hwtw','n003','sloc']:print(k,start,r.o,id,owner,pos)
print('end',r.o,len(r.d));assert r.o==len(r.d)
