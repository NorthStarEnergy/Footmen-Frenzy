import pathlib,struct,re
class Obj:
 def __init__(self,path,levels=False):
  self.path=pathlib.Path(path);self.b=self.path.read_bytes();self.o=0;self.levels=levels;self.ver=self.get('I');self.tables=[]
  for t in range(2):
   table=[]
   for _ in range(self.get('I')):
    old,new=self.get('4s4s');extra=[self.get('I') for _ in range(self.get('I'))] if self.ver>=3 else [];mods=[]
    for j in range(self.get('I')):
     key,typ=self.get('4sI');level,col=self.get('II') if levels else (0,0);v=self.z() if typ==3 else self.get('i' if typ==0 else 'f');end=self.get('4s');mods.append([key,typ,level,col,v,end])
    table.append(dict(old=old,new=new,extra=extra,mods=mods))
   self.tables.append(table)
  assert self.o==len(self.b),(str(path),self.o,len(self.b))
 def get(self,f):
  x=struct.unpack_from('<'+f,self.b,self.o);self.o+=struct.calcsize('<'+f);return x[0] if len(x)==1 else x
 def z(self):
  e=self.b.index(0,self.o);s=self.b[self.o:e].decode();self.o=e+1;return s
 def find(self,id):
  for t in self.tables:
   for x in t:
    if (x['new'] if x['new']!=b'\0'*4 else x['old'])==id.encode():return x
 def set(self,id,key,value,typ=None,level=0,col=0):
  x=self.find(id)
  if x is None:x=dict(old=id.encode(),new=b'\0'*4,extra=[0],mods=[]);self.tables[0].append(x)
  typ=typ if typ is not None else 3 if isinstance(value,str) else 2 if isinstance(value,float) else 0
  m=next((m for m in x['mods'] if m[0]==key.encode() and m[2]==level and m[3]==col),None)
  if m:m[1]=typ;m[4]=value
  else:x['mods'].append([key.encode(),typ,level,col,value,x['new']])
 def save(self,path):
  b=struct.pack('<I',self.ver)
  for table in self.tables:
   b+=struct.pack('<I',len(table))
   for x in table:
    b+=x['old']+x['new']
    if self.ver>=3:b+=struct.pack('<I',len(x['extra']))+b''.join(struct.pack('<I',v) for v in x['extra'])
    b+=struct.pack('<I',len(x['mods']))
    for k,t,l,c,v,e in x['mods']:
     b+=k+struct.pack('<I',t)+(struct.pack('<II',l,c) if self.levels else b'')+(v.encode()+b'\0' if t==3 else struct.pack('<i' if t==0 else '<f',v))+e
  pathlib.Path(path).write_bytes(b)
if __name__=='__main__':
 for folder in ['extracted','reference4p']:
  for file,ids,levels in [('war3map.w3u',['h000','hhou','h02U','h02V'],False),('war3map.w3a',['ANre','Aneu'],True)]:
   ob=Obj('work/'+folder+'/'+file,levels)
   for id in ids:print(folder,id,ob.find(id))
