"""Small Windows StormLib adapter; no third-party Python packages required."""
import ctypes as c
from pathlib import Path, PureWindowsPath


class Archive:
    def __init__(self, dll, path, writable=False):
        self.lib = c.WinDLL(str(dll))
        signatures = {
            'SFileOpenArchive': [c.c_wchar_p, c.c_uint, c.c_uint, c.POINTER(c.c_void_p)],
            'SFileOpenFileEx': [c.c_void_p, c.c_char_p, c.c_uint, c.POINTER(c.c_void_p)],
            'SFileGetFileSize': [c.c_void_p, c.c_void_p],
            'SFileReadFile': [c.c_void_p, c.c_void_p, c.c_uint, c.POINTER(c.c_uint), c.c_void_p],
            'SFileCloseFile': [c.c_void_p], 'SFileCloseArchive': [c.c_void_p],
            'SFileAddFileEx': [c.c_void_p, c.c_wchar_p, c.c_char_p, c.c_uint, c.c_uint, c.c_uint],
        }
        for name, args in signatures.items():
            getattr(self.lib, name).argtypes = args
            getattr(self.lib, name).restype = c.c_bool
        self.lib.SFileGetFileSize.restype = c.c_uint
        self.handle = c.c_void_p()
        if not self.lib.SFileOpenArchive(str(Path(path).resolve()), 0, 0 if writable else 256, c.byref(self.handle)):
            raise RuntimeError(f'Cannot open map archive: {path}')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if not self.lib.SFileCloseArchive(self.handle):
            raise RuntimeError('Cannot close map archive')

    def read(self, name):
        handle = c.c_void_p()
        if not self.lib.SFileOpenFileEx(self.handle, name.encode('utf-8'), 0, c.byref(handle)):
            raise KeyError(name)
        try:
            size = self.lib.SFileGetFileSize(handle, None)
            if size == 0xFFFFFFFF:
                raise RuntimeError(f'Invalid entry size: {name}')
            data = c.create_string_buffer(size)
            count = c.c_uint()
            if size and (not self.lib.SFileReadFile(handle, data, size, c.byref(count), None) or count.value != size):
                raise RuntimeError(f'Incomplete read: {name}')
            return data.raw
        finally:
            self.lib.SFileCloseFile(handle)

    def names(self):
        try:
            return self.read('(listfile)').decode('utf-8-sig').splitlines()
        except KeyError:
            return []  # Protected maps can omit their internal filename list.

    def add(self, name, path):
        if not self.lib.SFileAddFileEx(self.handle, str(path.resolve()), name.encode('utf-8'), 0x80000200, 2, 2):
            raise RuntimeError(f'Cannot replace map entry: {name}')

    def extract(self, destination, candidates=()):
        count = 0
        for name in sorted(set(self.names()) | set(candidates)):
            if name.startswith('('):
                continue
            rel = PureWindowsPath(name)
            if rel.is_absolute() or rel.drive or '..' in rel.parts:
                raise ValueError(f'Unsafe archive entry: {name}')
            try:
                data = self.read(name)
            except KeyError:
                continue
            target = destination.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            count += 1
        return count
