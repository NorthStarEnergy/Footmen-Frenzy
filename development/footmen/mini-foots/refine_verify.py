from pathlib import Path
p=Path('mini-foots/verify.py');s=p.read_text().replace('total=[0,0];rem=[0,1]','total=[0,0];rem=[0,1];baseline=0').replace(' for n in waves:\n',' for n in waves:\n  baseline+=n\n').replace("sum(total)==sum(waves[:waves.index(n)+1])*3 if False else True",'sum(total)==baseline*3');p.write_text(s)
