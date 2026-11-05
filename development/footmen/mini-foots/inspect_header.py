from pathlib import Path
p=Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test\FF799X_Rx_HeroTavern_v1.w3x'); b=p.read_bytes();print(b[:100], b.find(b'MPQ\x1a'))
