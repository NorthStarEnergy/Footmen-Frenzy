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
