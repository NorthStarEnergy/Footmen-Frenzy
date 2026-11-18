from pathlib import Path
import sys,json,re,struct,hashlib
root=Path(r'C:\Users\User\Documents\GitHub\Footmen Frenzy')
s=root/'projects/ffa/src'; donor=root/'projects/799x/src'
sys.path.insert(0,str(root/'tools'));from map_archive import Archive
sys.path.insert(0,r'C:\Users\User\Documents\Codex\2026-10-28\thi\work');from objectio import Obj
with Archive(json.loads((root/'tools.local.json').read_text())['stormlib'],Path.home()/'Documents/Warcraft III/Maps/Tests/FFA Foots/Solo_Foots_8P_FFA_v19.w3x') as a:
 for f in ['war3map.j','war3map.wct','war3mapUnits.doo','war3map.w3u','war3mapMisc.txt']:assert a.read(f)==(s/f).read_bytes(),f
don=(donor/'war3map.j').read_text()
def block(t,i):return re.search(r'(?m)^set udg_spawn_unit\['+str(i)+r'\].*?^set udg_unit_level\['+str(i)+r'\]=\d+',t,re.S|re.M)[0]
def patch(t):
 for i in [17,23,27,44]:t=t.replace(block(t,i),block(don,i))
 for a,b in [("'ohun'","'ogru'"),("'nskf'","'ugho'"),('Headhunter','Grunt'),('Burning Archer','Ghoul'),('udg_spawnTimer, true, 5.416667','udg_spawnTimer, true, 4.875'),('udg_spawnTimer, true, 6.666667','udg_spawnTimer, true, 6.00'),('gg_trg_five, 5.00','gg_trg_five, 4.50'),('gg_trg_ten, 7.50','gg_trg_ten, 6.75'),('amount*95','amount*70'),('udg_exp_sys_high_Foot=31','udg_exp_sys_high_Foot=30'),('udg_exp_sys_high_Foot=32','udg_exp_sys_high_Foot=31')]:t=t.replace(a,b)
 t=re.sub(r'(?m)^set (udg_unit_bounty_base\[\d+\]=)(\d+)',lambda m:'set '+m[1]+str(round(int(m[2])*.75)),t)
 t=re.sub(r'(?m)^ *call StartTimerBJ\(udg_timer_BountyIncrease, false, 2200.00\)\r?\n','',t)
 return t
def decoded(p):return p.read_bytes().decode()
j=s/'war3map.j';old=decoded(j);new=patch(old.replace('\r\n','\n'));nl='\r\n' if '\r\n' in old else '\n'
w=s/'war3map.wct';raw=w.read_bytes();p=raw.index(0,4)+1;n=struct.unpack_from('<I',raw,p)[0];editor=patch(raw[p+4:p+4+n].decode().replace('\r\n','\n')).encode()
for i in range(51):assert block(editor.decode(),i)==block(new,i)
o=Obj(s/'war3map.w3u');d=Obj(donor/'war3map.w3u')
for uid in ['ugho','ogru']:
 for k,typ,l,c,v,_ in d.find(uid)['mods']:o.set(uid,k.decode(),v,typ,l,c)
o.save(s/'war3map.w3u');j.write_bytes(new.replace('\n',nl).encode());w.write_bytes(raw[:p]+struct.pack('<I',len(editor))+editor+raw[p+4+n:])
p=s/'war3mapMisc.txt';p.write_bytes(p.read_bytes().replace(b'GrantNormalXP=25,38,57,85',b'GrantNormalXP=19,29,43,64'))
p=s/'war3map.wts';t=decoded(p);t=re.sub(r'(Spawned Units:\|r |Auto-Spawn: |Toggle )(Burning Archer|Headhunter)',lambda m:m[1]+{'Burning Archer':'Ghoul','Headhunter':'Grunt'}[m[2]],t);p.write_bytes(t.encode())
rows=json.loads((root/'development/solo/ffa-v17/unit-reference.json').read_text());rows.sort(key=lambda r:(r['index']>25,r['race']!='Shared',r['race'],r['tier'],r['index']))
report=['# Eight-player FFA: v19 to v20','Ordinary base troops, then same-tier swap bases. Each interval is seconds per wave; a double wave produces twice as many troops. Gold is per unmodified troop kill. Damage is the primary attack before mitigation.','', '| Base | Unit | Seconds v19 → v20 | HP | Armor | Damage | Attack sec | Range | Unit level | Gold v19 → v20 |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in rows:
 i=r['index']; b=block(new,i);f={k:float(v) for k,v in re.findall(r'udg_unit_(\w+)\[\d+\]=([\d.]+)',b)};g=lambda k:f[k];name={17:'Burning Archer → Ghoul',44:'Burning Archer → Ghoul',23:'Headhunter → Grunt',27:'Headhunter → Grunt'}.get(i,r['name']);a=r['spawn_interval'];report.append(f"| {r['race']} {r['tier'] or ''} ({r['base_id']}) | {name} | {a:g} → {a*.9:.2f} | {g('HP'):g} | {g('armor'):g} | {g('att_base')+g('att_num_dice'):g}–{g('att_base')+g('att_num_dice')*g('att_dice_sides'):g} | {g('att_CD'):g} | {g('range'):g} | {g('level'):g} | {r['bounty']} → {g('bounty_base')+g('bounty_num_dice'):g}–{g('bounty_base')+g('bounty_num_dice')*g('bounty_dice_sides'):g} |")
Path('FFA-v20-tempo.md').write_text('\n'.join(report)+'\n',encoding='utf8')
