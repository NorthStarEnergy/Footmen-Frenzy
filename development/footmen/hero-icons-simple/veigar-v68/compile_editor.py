from pathlib import Path
import re,sys,subprocess
sys.path.insert(0,'tools')
from check_editor_runtime import parse_source
O=Path(__file__).resolve().parent;V=O/'verified'
read=lambda p:p.read_text(encoding='utf-8-sig')
C=Path(r'C:\Program Files\Warcraft III\_retail_\x86_64\JassHelper');J=Path(r'C:\Users\Ryan1\Documents\Warcraft III\JassHelper')
def run(args,log):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 (O/log).write_text(r.stdout+r.stderr)
 assert r.returncode==0,r.stdout+r.stderr
# Regenerate every authoritative function from final exported WCT before compilation.
regenerated=read(V/'war3map.j')
source_functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',read(O/'verified-source/FF_Runtime.j'))}
regenerated=re.sub(r'(?ms)^function (\w+)\b.*?^endfunction',lambda m:source_functions.get(m[1],m[0]),regenerated)
header=read(O/'verified-source/globals.j')
source_decls=re.search(r'(?ms)^globals\b(.*?)^endglobals',header)[1]
packed_decls=re.search(r'(?ms)^globals\b(.*?)^endglobals',regenerated)[1]
source_names=set(parse_source(header).globals)
extra=[]
for line in packed_decls.splitlines():
    m=re.match(r'\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)',line)
    if m and m[1] not in source_names and not line.lstrip().startswith('//'):extra.append(line)
regenerated=re.sub(r'(?ms)^globals\b.*?^endglobals',lambda _:'globals\n'+source_decls+'\n'+'\n'.join(extra)+'\nendglobals',regenerated,count=1)
(O/'regenerated.j').write_text(regenerated,encoding='utf8')
run([C/'jasshelper.exe','--scriptonly',J/'common.j',J/'Blizzard.j',O/'regenerated.j',O/'compiled.j'],'compiler.log')
run([C/'pjass.exe',J/'common.j',J/'Blizzard.j',O/'compiled.j'],'compiler.log')
