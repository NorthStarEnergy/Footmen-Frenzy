from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent
WORK=Path('C:/Users/User/Documents/Codex/2026-10-28/thi/work')
def run(args,log):
    r=subprocess.run(list(map(str,args)),cwd=R,capture_output=True,text=True,errors='replace',timeout=90)
    output=r.stdout+r.stderr;(R/log).write_text(output)
    print(log+': '+str(r.returncode)+'\n'+output[-3500:])
    assert r.returncode==0,log
    return output
assert 'Parse successful:' in run([WORK/'jasshelper/pjass.exe',WORK/'common.j',WORK/'Blizzard.j',R/'src/war3map.j'],'compiler.log')
run([WORK/'jasshelper/clijasshelper.exe','--scriptonly',WORK/'common.j',WORK/'Blizzard.j',R/'editor-validation.j',R/'editor-compiled.j'],'jasshelper.log')
assert 'Parse successful:' in run([WORK/'jasshelper/pjass.exe',WORK/'common.j',WORK/'Blizzard.j',R/'editor-compiled.j'],'editor-compiler.log')
