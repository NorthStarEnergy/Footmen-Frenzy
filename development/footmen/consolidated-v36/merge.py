from pathlib import Path
import sys, re, json, copy, difflib, hashlib
R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
TF=Path('C:/Users/User/Documents/Codex/2026-10-29/i/outputs/FF799X_Rx_Twisted_Fate_v33.w3x')
BASE=W/'guardian-lantern/release/FF799X_Rx_GuardianLantern_v30.w3x'
NAMES=['war3map.j','war3map.w3a','war3map.w3u','war3map.wts','war3map.imp']
snapshots={}; manifests={}
def snapshot(label,path):
    p=R/'inputs'/label;p.mkdir(parents=True,exist_ok=True)
    h=c.c_void_p();assert storm.SFileOpenArchive(str(path),0,0x100,c.byref(h))
    for n in NAMES:(p/n).write_bytes(read_storm(h,n))
    storm.SFileCloseArchive(h)
    snapshots[label]=p;manifests[label]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    return p
snapshot('tf',TF);snapshot('v30',BASE)
snapshot('tooltips',W/'hero-tooltips/release/FF799X_Rx_HeroTooltips_v31.w3x')
snapshot('gas',W/'mundo-gas/release/FF799X_Rx_Mundo_v32.w3x')
snapshot('requiem',W/'requiem-fix/release/FF799X_Rx_RequiemFix_v33.w3x')
snapshot('guldan',W/'orianna-guldan/release/FF799X_Rx_OriannaGuldan_v34.w3x')
snapshot('rename',W/'799x-backport/release/FF799X_Rx_Guldan_v35.w3x')
snapshot('veigar',W/'veigar-prototype/release/FF799X_Rx_Veigar_v33.w3x')
(R/'inputs.json').write_text(json.dumps(manifests,indent=2))
s=(snapshots['tf']/'war3map.j').read_text(encoding='utf-8-sig')
objects={ext:objdata.load(str(snapshots['tf']/('war3map.'+ext))) for ext in ['w3a','w3u']}
log=[]
def merge_text(old,new,current,label):
    if current==old:return new
    if current==new:return current
    # Apply each donor edit only when its original context is still present uniquely.
    a,b=old.splitlines(True),new.splitlines(True)
    for tag,i,j,k,l in reversed(difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()):
        if tag=='equal':continue
        before=''.join(a[i:j]);after=''.join(b[k:l])
        if before and current.count(before)==1:current=current.replace(before,after,1);continue
        for width in range(1,8):
            left=''.join(a[max(0,i-width):i]);right=''.join(a[j:j+width])
            target=left+before+right
            if target and current.count(target)==1:
                current=current.replace(target,left+after+right,1);break
        else:raise AssertionError(('merge conflict',label,before[:180],after[:180]))
    return current
def apply_script(parent,donor):
    global s
    old=(snapshots[parent]/'war3map.j').read_text(encoding='utf-8-sig');new=(snapshots[donor]/'war3map.j').read_text(encoding='utf-8-sig')
    of,nf,cf=functions(old),functions(new),functions(s)
    # Insert each new function ahead of the next existing donor function, preserving dependency order.
    order=list(nf)
    for n in order:
        if n in of:continue
        assert n not in cf,n
        anchor=next((x for x in order[order.index(n)+1:] if x in cf),None)
        assert anchor
        s=s.replace(cf[anchor],nf[n]+'\n\n'+cf[anchor],1);cf=functions(s)
        log.append([donor,'new_function',n])
    for n in of:
        if of[n]==nf[n]:continue
        if donor=='requiem' and n=='DK_OnCast':
            assert "call DR_Start(source, level)" in cf[n] and 'DK_New(4, source)' not in cf[n]
            log.append([donor,'superseded','DK_OnCast: Ascension replaces Requiem; no channel restart path'])
            continue
        s=s.replace(cf[n],merge_text(of[n],nf[n],cf[n],donor+':'+n),1)
        log.append([donor,'changed_function',n])
    og=old[:old.index('\nendglobals')];ng=new[:new.index('\nendglobals')]
    added=[x for x in ng.splitlines() if x.strip() and x not in og.splitlines()]
    if added:s=s.replace('\nendglobals','\n'+'\n'.join(added)+'\nendglobals',1)
def objkey(e):return e['newId'] if e['newId']!='\0'*4 else e['oldId']
def modkey(m):return (m['id'],m.get('level',0),m.get('ptr',0))
def apply_objects(parent,donor):
    for ext,current in objects.items():
        old=objdata.load(str(snapshots[parent]/('war3map.'+ext)));new=objdata.load(str(snapshots[donor]/('war3map.'+ext)))
        for ti in range(2):
            om={objkey(e):e for e in old['tables'][ti]};nm={objkey(e):e for e in new['tables'][ti]};cm={objkey(e):e for e in current['tables'][ti]}
            for key,e in nm.items():
                if donor=='requiem' and key=='ADk4':
                    log.append([donor,'superseded','ADk4: retain Ascension object rather than Requiem channel'])
                    continue
                if key not in om:
                    assert key not in cm;current['tables'][ti].append(copy.deepcopy(e));log.append([donor,ext,'new',key]);continue
                if e==om[key]:continue
                target=cm[key];oldmods={modkey(m):m for m in om[key]['mods']};newmods={modkey(m):m for m in e['mods']};curmods={modkey(m):m for m in target['mods']}
                for k in oldmods.keys()|newmods.keys():
                    if oldmods.get(k)==newmods.get(k):continue
                    assert curmods.get(k) in (oldmods.get(k),newmods.get(k)),('object conflict',donor,ext,key,k)
                    target['mods']=[m for m in target['mods'] if modkey(m)!=k]
                    if k in newmods:target['mods'].append(copy.deepcopy(newmods[k]))
                log.append([donor,ext,'changed',key])
apply_script('v30','tooltips');apply_objects('v30','tooltips')
apply_script('gas','requiem');apply_objects('gas','requiem')
apply_script('requiem','guldan');apply_objects('requiem','guldan')
apply_script('guldan','rename');apply_objects('guldan','rename')
apply_script('gas','veigar');apply_objects('gas','veigar')
O=R/'src';O.mkdir(exist_ok=True)
(O/'war3map.j').write_text(s,encoding='utf8')
for ext,d in objects.items():(O/('war3map.'+ext)).write_bytes(objdata.dump(d))
text=(snapshots['tf']/'war3map.wts').read_text(encoding='utf-8-sig')
prior=(snapshots['guldan']/'war3map.wts').read_text(encoding='utf-8-sig')
renamed=(snapshots['rename']/'war3map.wts').read_text(encoding='utf-8-sig')
def strings(t):return {m[1]:m[0] for m in re.finditer(r'(?ms)^STRING (\d+)[^\n]*\n(?://[^\n]*\n)*\{\n.*?^\}',t)}
ps,ns,ts=strings(prior),strings(renamed),strings(text)
for key,value in ns.items():
    if value==ps.get(key) or key=='1':continue
    assert ts[key]==ps[key],('string conflict',key)
    text=text.replace(ts[key],value,1);log.append(['rename','string',key])
(O/'war3map.wts').write_text(text,encoding='utf8')
(O/'war3map.imp').write_bytes((snapshots['guldan']/'war3map.imp').read_bytes())
(R/'merge-log.json').write_text(json.dumps(log,indent=2))
print('Merged',len(log),'recorded branch changes.')
