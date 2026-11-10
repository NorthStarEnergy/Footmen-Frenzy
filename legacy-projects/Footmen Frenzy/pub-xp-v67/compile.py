from pathlib import Path
import subprocess
import sys

R = Path(__file__).resolve().parent
WORK = Path('C:/Users/User/Documents/Codex/2026-10-28/thi/work')
COMMON = WORK / 'common.j'
BLIZZARD = WORK / 'Blizzard.j'
PJASS = WORK / 'jasshelper/pjass.exe'
CLI = WORK / 'jasshelper/clijasshelper.exe'

def run(args, log):
    result = subprocess.run([str(a) for a in args], cwd=R, capture_output=True, text=True, errors='replace', timeout=90)
    output = result.stdout + result.stderr
    (R / log).write_text(output)
    print(log + ': exit ' + str(result.returncode))
    print('\n'.join(output.splitlines()[:18]))
    if result.returncode != 0:
        sys.exit(result.returncode)
    return output

out = run([PJASS, COMMON, BLIZZARD, R / 'src/war3map.j'], 'compiler.log')
assert 'Parse successful:' in out and 'Parse failed' not in out
# --scriptonly validates the editor's authoritative source without touching an
# installed map. All compiler working files live in this test-build folder.
run([CLI, '--scriptonly', COMMON, BLIZZARD, R / 'editor-validation.j', R / 'editor-compiled.j'], 'jasshelper.log')
assert (R / 'editor-compiled.j').is_file()
out = run([PJASS, COMMON, BLIZZARD, R / 'editor-compiled.j'], 'editor-compiler.log')
assert 'Parse successful:' in out and 'Parse failed' not in out
