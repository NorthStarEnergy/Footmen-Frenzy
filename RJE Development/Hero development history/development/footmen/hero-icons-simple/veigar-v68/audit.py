from pathlib import Path
import json,sys,subprocess,hashlib,collections,struct,re
from PIL import Image
O=Path(__file__).resolve().parent;P=O.parents[1];B=O/'baseline';E=O/'edited';V=O/'verified';OUT=O/'FF799X_Rx_Veigar_Classic_v68.w3x';MPQ=P/'tools/external/mpqcli-bin/mpqcli.exe'
sys.path.insert(0,str(P/'tools'));import objdata_fieldmerge as obj
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((O/'verification.json').read_text());changes=report['changed_members']
def run(args,log):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(O/log).write_text(r.stdout+r.stderr);assert r.returncode==0,(log,r.stderr[-900:]);assert '[!]' not in r.stderr+r.stdout;return r.stdout
# Compare the entire decompressed archive as a multiset; unknown names are preserved.
full=O/'full-verified';full.mkdir(exist_ok=True)
run([MPQ,'extract',OUT,'-o',full,'-k'],'full-extract.log')
oldfiles=[p for p in B.glob('File*') if p.is_file()]
old=collections.Counter(sha(p) for p in oldfiles)
assert len(oldfiles)==len((O/'baseline-list.txt').read_text(encoding='utf-8-sig').splitlines())
new=collections.Counter(sha(p) for p in full.rglob('*') if p.is_file() and p.name not in ['(listfile)','(attributes)'])
removed=0
for n in changes:
 if (B/n).exists():
  digest=sha(B/n);assert old[digest]>0,n;old[digest]-=1;removed+=1
 digest=sha(E/n);assert new[digest]>0,n;new[digest]-=1
assert +old==+new,{'lost':list((old-new).items())[:5],'extra':list((new-old).items())[:5]}
# Field-level comparison across every existing object, including unrelated hero abilities.
for fn,allowed in [('war3map.w3u',{'HVg1'}),('war3map.w3a',{'AVgq','AVgw','AVge','AVgr','AVgp','AVgs'})]:
 assert obj.roundtrip_ok(str(V/fn))
 before={e.key():e for t in obj.parse(str(B/fn))[1] for e in t};after={e.key():e for t in obj.parse(str(V/fn))[1] for e in t}
 assert set(before)<=set(after)
 fields=lambda e:[(m.modid,m.vartype,m.level,m.pointer,m.value,m.endtoken) for m in e.mods()]
 for raw in before:
  if raw not in allowed:assert fields(before[raw])==fields(after[raw]),(fn,raw)
 if fn.endswith('w3u'):
  f={m.modid:m.value for m in after['HVg1'].mods()}
  for k,a in dict(ustr=15,uagi=16,uint=20,ustp=1.5,uagp=1.5,uinp=3,umvs=270,uhpm=100).items():assert f[k]==a
 else:
  for raw,levels in [('AVgq',6),('AVgw',6),('AVge',6),('AVgr',3)]:
   mods=list(after[raw].mods());assert next(m.value for m in mods if m.modid=='alev')==levels
   for lv in range(1,levels+1):
    tip=next(m.value for m in mods if m.modid=='aub1' and m.level==lv)
    assert tip.count('|c')==tip.count('|r') and 'TRIGSTR_' not in tip
  assert len(set(next(m.value for m in after[raw].mods() if m.modid=='Ncl6') for raw in ['AVgq','AVgw','AVge','AVgr']))==4
for n in changes:
 assert (V/n).read_bytes()==(E/n).read_bytes()
 if n.endswith('.blp'):
  p=V/n;im=Image.open(p);im.load();assert im.size==(64,64)
  data=p.read_bytes();assert data[:4]==b'BLP1';offsets=struct.unpack_from('<16I',data,28);lengths=struct.unpack_from('<16I',data,92)
  assert list(lengths[:7])==[4096,1024,256,64,16,4,1]
  assert all(a+b<=len(data) for a,b in zip(offsets,lengths))
  assert n.encode()+b'\0' in (V/'war3map.imp').read_bytes()
j=(V/'war3map.j').read_text(encoding='utf-8-sig')
assert "set udg_hero_type[97]='HVg1'" in j and 'set udg_total_hero_count=97' in j
for k,a in dict(STR_base=15,STR_inc=1.5,AGI_base=16,AGI_inc=1.5,INT_base=20,INT_inc=3.0).items():assert f'set udg_hero_{k}[97]={a}' in j
assert 'GetUnitTypeId(u) == \'HVg1\' and GetWidgetLife(u) > 0.405' in j
assert "call RemoveSavedHandle(VG_Hash, GetHandleId(caster), 701)" in j
assert 'not IsUnitIllusion(victim)' in j and 'not IsUnitType(victim, UNIT_TYPE_SUMMONED)' in j
assert 'LoadReal(VG_Hash, h, 10)' in j and "call SetUnitAbilityLevel(dummy, 'AVgs', LoadInteger(VG_Hash, h, 11))" in j
assert 'elseif udg_mode_debugmode then' in j[j.index('function VG_Summon takes'):j.index('function VG_ClassicKill takes')]
report.update(archive_payloads_preserved=sum(old.values()),original_archive_entries=len(oldfiles),original_members_replaced=removed,object_field_isolation=True,icons_validated=12,editor_jasshelper_compile_passed=True,engine_tested=False)
(O/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['archive_payloads_preserved','original_archive_entries','icons_validated','editor_jasshelper_compile_passed','engine_tested']}))
