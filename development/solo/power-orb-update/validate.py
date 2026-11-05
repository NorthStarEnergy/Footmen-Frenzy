from pathlib import Path
import sys,re,json,hashlib
W=Path(__file__).resolve().parent;R=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots')
sys.path.insert(0,str(W.parent/'.audit-deps'));import mpyq
a=mpyq.MPQArchive(str(W/'Mini Foots v8.w3x'),listfile=False)
S=W/'src';V=W/'roundtrip/files'
for f in S.rglob('*'):
 if f.is_file():
  rel=f.relative_to(S);b=a.read_file(str(rel));assert b==f.read_bytes(),str(rel)
  target=V/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
code=(W/'verify.py').read_text(encoding='utf8')
code=code.replace('R=Path(__file__).parent;',f'R=Path({str(R)!r});')
code=code.replace("S=R/'src';V=Path((R/'last-build.txt').read_text().strip())/'roundtrip/files'",f'S=Path({str(S)!r});V=Path({str(V)!r})')
code=code.replace("(R/'power_orb.py')",f"(Path({str(W)!r})/'power_orb.py')")
code=code.replace("release=R/'release/Mini Foots v8.w3x'",f"release=Path({str(W/'Mini Foots v8.w3x')!r})")
code=code.replace("(R/'verification.json')",f"(Path({str(W)!r})/'verification.json')")
exec(compile(code,'verify','exec'),{'__file__':str(W/'verify.py')})
old=(R/'src/war3map.j').read_text(encoding='utf8');new=(S/'war3map.j').read_text(encoding='utf8')
func=lambda s:{m[1]:m[0] for m in re.finditer(r'^function (\w+) takes .*?^endfunction',s,re.M|re.S)}
of,nf=func(old),func(new)
changed=[n for n in of if of[n]!=nf[n]]
assert set(changed)=={'OM_ClearBallVisual','OM_UpdateBallVisual','OM_BallLook','config'},changed
print('Only expected functions changed:',changed)
