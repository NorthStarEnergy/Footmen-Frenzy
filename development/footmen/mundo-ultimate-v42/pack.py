from pathlib import Path
import sys,json,hashlib,shutil
R=Path(__file__).resolve().parent;W=R.parent;S=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions,archive,entries
import objdata
from validate_objdata import validate
change=json.loads((R/'changes.json').read_text());paths={k:Path(v) for k,v in change['base_maps'].items()}
for k,p in paths.items():assert hashlib.sha256(p.read_bytes()).hexdigest()==change['base_hashes'][k],k+' changed since preparation'
assert json.loads((R/'checks.json').read_text())['passed']>=160
log=(R/'compiler.log').read_text();assert 'Parse successful' in log and 'error' not in log.lower()
ability_data=objdata.load(str(S/'war3map.w3a'))
ability_index={e['newId']:e for t in ability_data['tables'] for e in t}
for i in range(256):
 e=ability_index[f'mD{i:02X}']
 assert (e['flags'],e['extra'])==(1,0), 'Invalid v3 digestion indicator record'
out=R/'release/FF799X_Rx_Consolidated_Undying_v42a.w3x';out.parent.mkdir(exist_ok=True);assert not out.exists()
shutil.copy2(paths['item'],out)
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n in change['payloads']:assert storm.SFileAddFileEx(h,str(S/n),n.encode(),0x80000200,2,2),n
assert storm.SFileCloseArchive(h)
item,outmpq=archive(paths['item']),archive(out);ie,oe=entries(item),entries(outmpq);skip=set()
for n in change['payloads']+['(listfile)','(attributes)','(signature)']:
 e=item.get_hash_table_entry(n)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in ie.items():
 if k not in skip:assert oe.get(k)==v,('Unrelated item-branch payload changed',k)
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in change['payloads']:assert read_storm(h,n)==(S/n).read_bytes(),n
assert storm.SFileCloseArchive(h)
def read(path,n):
 h=c.c_void_p();assert storm.SFileOpenArchive(str(path),0,0x100,c.byref(h));v=read_storm(h,n);assert storm.SFileCloseArchive(h);return v
for n in ['war3map.w3u','war3mapSkin.w3u']:assert read(out,n)==read(paths['unit'],n)
for n in ['war3map.w3u','war3mapSkin.w3u','war3map.w3a','war3mapSkin.w3a','war3map.w3t','war3mapSkin.w3t']:
 validate(read(out,n), n.endswith('.w3a'))
norm=lambda b:b.decode('utf-8-sig').replace('\r\n','\n')
merged=functions(norm(read(out,'war3map.j')));donor=functions(norm(read(paths['unit'],'war3map.j')));old=functions(norm(read(paths['item'],'war3map.j')))
for n in change['unit_functions']:assert merged[n]==donor[n],n
for n in old:
 if n not in change['unit_functions']:assert merged[n]==old[n],n
assert read(out,'war3map.w3t')==read(paths['item'],'war3map.w3t')
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report=dict(output=str(out),sha256=sha,base=str(paths['item']),unit_balance_donor=str(paths['unit']),unit_functions=change['unit_functions'],preserved_item_payloads=len(ie.keys()-skip),behavior_checks=160,compiler='passed',live_test='pending')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
