from pathlib import Path
import re,json,sys,shutil
R=Path(__file__).parent;O=R
src=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\mini-foots')
sys.path.insert(0,str(src/'tools'));import objdata
shutil.copyfile(src/'src/war3map.w3u',O/'war3map.w3u')
s=(O/'war3map.j').read_text(encoding='utf8')
exec((R/'hero_policy.py').read_text(encoding='utf8'))
(O/'war3map.j').write_text(s,encoding='utf8',newline='\n')
b=(O/'build_source.py').read_text(encoding='utf8')
b=b.replace("exec((R/'port_orianna.py').read_text(encoding='utf-8'))","exec((R/'port_orianna.py').read_text(encoding='utf-8'))\nexec((R/'hero_policy.py').read_text(encoding='utf-8'))")
(O/'build_source.py').write_text(b,encoding='utf8')
print((R/'hero-policy.json').read_text(encoding='utf8'))

