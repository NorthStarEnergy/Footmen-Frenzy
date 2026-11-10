"""Read and patch Warcraft III archives using the existing local StormLib."""
from pathlib import Path
import ctypes as c
import shutil

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r'C:\Users\User\Documents\Warcraft III\Maps\Foots FFA\Solo_Foots_v1.8_8P_Compact_FFA_v3.w3x')
DLL = Path(r'C:\Users\User\Documents\Codex\2026-10-28\thi\work\stormlib\x64\StormLib.dll')
s = c.WinDLL(str(DLL))
s.SFileOpenArchive.argtypes = [c.c_wchar_p,c.c_uint,c.c_uint,c.POINTER(c.c_void_p)]
s.SFileOpenFileEx.argtypes = [c.c_void_p,c.c_char_p,c.c_uint,c.POINTER(c.c_void_p)]
s.SFileGetFileSize.argtypes = [c.c_void_p,c.c_void_p]
s.SFileReadFile.argtypes = [c.c_void_p,c.c_void_p,c.c_uint,c.POINTER(c.c_uint),c.c_void_p]
s.SFileCloseFile.argtypes = [c.c_void_p]
s.SFileCloseArchive.argtypes = [c.c_void_p]
s.SFileAddFileEx.argtypes = [c.c_void_p,c.c_wchar_p,c.c_char_p,c.c_uint,c.c_uint,c.c_uint]

def extract(path, directory):
    handle=c.c_void_p()
    assert s.SFileOpenArchive(str(path),0,0x100,c.byref(handle))
    def read(name):
        file=c.c_void_p()
        assert s.SFileOpenFileEx(handle,name.encode(),0,c.byref(file)),name
        data=c.create_string_buffer(s.SFileGetFileSize(file,None)); count=c.c_uint()
        assert s.SFileReadFile(file,data,len(data),c.byref(count),None)
        s.SFileCloseFile(file)
        return data.raw
    names=read('(listfile)').decode().splitlines()
    for name in names:
        path=directory/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(read(name))
    assert s.SFileCloseArchive(handle)
    return names

def pack(output):
    output.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(SOURCE,output)
    handle=c.c_void_p()
    assert s.SFileOpenArchive(str(output),0,0,c.byref(handle))
    for path in sorted((ROOT/'src').rglob('*')):
        if path.is_file():
            name=str(path.relative_to(ROOT/'src')).replace('/','\\')
            assert s.SFileAddFileEx(handle,str(path),name.encode(),0x80000200,2,2),name
    assert s.SFileCloseArchive(handle)

if __name__=='__main__':
    print('Extracted',len(extract(SOURCE,ROOT/'base')),'files from',SOURCE)
