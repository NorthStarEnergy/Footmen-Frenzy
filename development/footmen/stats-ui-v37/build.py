from pathlib import Path
import sys,json,shutil,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import storm,read_storm,c,functions,archive,entries
base=W/'799x-backport/release/FF799X_Rx_Consolidated_InstaMass_v36.w3x'
O=R/'src';O.mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
original=read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r\n','\n')
wts=read_storm(h,'war3map.wts');assert storm.SFileCloseArchive(h)
s=original;f=functions(s)['DPS_Create']
new=f.replace('BlzFrameSetSize(DPS_Button, 0.0625, 0.020)','BlzFrameSetSize(DPS_Button, 0.075, 0.028)').replace('FRAMEPOINT_TOP, 0.0, 0.002)','FRAMEPOINT_TOP, 0.0, 0.004)').replace('FRAMEPOINT_TOPLEFT, 0.075, 0.510)','FRAMEPOINT_TOPLEFT, 0.075, 0.580)')
assert new!=f and new.count('0.075, 0.028')==1 and new.count('0.075, 0.580')==1
s=s.replace(f,new,1)
updated=functions(s)
assert [n for n,v in functions(original).items() if updated[n]!=v]==['DPS_Create']
(O/'war3map.j').write_text(s,encoding='utf8')
assert b'Consolidated InstaMass v36' in wts
(O/'war3map.wts').write_bytes(wts.replace(b'Consolidated InstaMass v36',b'Consolidated Stats UI v37'))
if '--pack' not in sys.argv:
    print('Prepared: Stats button 0.075 x 0.028; panel top 0.580, bottom 0.187.');sys.exit()
log=(R/'compiler.log').read_text();assert 'Parse successful' in log and 'error' not in log.lower()
release=R/'release';release.mkdir(exist_ok=True);out=release/'FF799X_Rx_Consolidated_StatsUI_v37.w3x';shutil.copy2(base,out)
names=['war3map.j','war3map.wts'];assert storm.SFileOpenArchive(str(out),0,0,c.byref(h))
for n in names:assert storm.SFileAddFileEx(h,str(O/n),n.encode(),0x80000200,2,2)
assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(out);ae,be=entries(a),entries(b);skip=set()
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h))
for n in names:
    assert read_storm(h,n)==(O/n).read_bytes()
    e=a.get_hash_table_entry(n);skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
assert storm.SFileCloseArchive(h)
for n in ['(listfile)','(attributes)','(signature)']:
    e=a.get_hash_table_entry(n)
    if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in ae.items():
    if k not in skip:assert be[k]==v,k
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n')
report=dict(output=str(out),sha256=sha,base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),changed_functions=['DPS_Create'],preserved_archive_entries=len(ae.keys()-skip),button_before=[.0625,.020],button_after=[.075,.028],panel_top_before=.510,panel_top_after=.580,panel_bottom_after=.187,close_button='unchanged',compiler='passed',live_visual_test='pending')
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
