import zlib

path = r'C:\SCADA\H2O-Oshawa-SPlus-VM.tar.gz'
decoder = zlib.decompressobj(31)
offset = 0
with open(path, 'rb') as source:
    while chunk := source.read(1024 * 1024):
        try:
            decoder.decompress(chunk)
        except zlib.error as exc:
            print(f'Gzip error near compressed byte {offset}, part {offset // 524288000:03}: {exc}')
            raise SystemExit(1)
        offset += len(chunk)
print(f'Bytes read: {offset}; gzip stream complete: {decoder.eof}; trailing bytes: {len(decoder.unused_data)}')
raise SystemExit(0 if decoder.eof else 1)
