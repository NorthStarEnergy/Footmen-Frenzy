from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent
s=(W/'veigar-ultimate-v83/build.py').read_text()
s=s.replace('veigar-stacks-v82/release/FF799X_Rx_Veigar_Stacks_v82_TEST.w3x','veigar-ultimate-v83/release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x').replace("W/'veigar-stacks-v82/verification.json'","W/'veigar-ultimate-v83/verification.json'")
a=s.index('helper=');b=s.index('# Patch the authoritative',a)
s=s[:a]+'''DONOR=Path('C:/Users/User/Documents/Warcraft III/Maps/Test/FF799X_Rx_Ghoul_Grunt_Buff_v69.w3x')
GUARDIAN=W/'guardian-visuals-v68/FF799X_Rx_Veigar_GuardianVisuals_v68.w3x'
DARK=W/'dark-matter-icon-v68/FF799X_Rx_Veigar_Classic_v68_DarkMatterIcon.w3x'
def read_map(path,name):
 h=c.c_void_p(); assert storm.SFileOpenArchive(str(path),0,256,c.byref(h))
 data=read_storm(h,name); assert storm.SFileCloseArchive(h); return data
assert digest(DONOR.read_bytes())=='3a7fa707aacf1ccaee6e17683758f6a2f59cb5fa04c8baad39b9508c9e0363ca'
for folder,path in [('guardian-visuals-v68',GUARDIAN),('dark-matter-icon-v68',DARK)]:
 assert digest(path.read_bytes())==json.loads((W/folder/'verification.json').read_text())['sha256']
df=functions(norm(read_map(DONOR,'war3map.j'))); gf=functions(norm(read_map(GUARDIAN,'war3map.j')))
replacements={n:df[n] for n in ['FFGS_InitSettings','Trig_set_spawn_variables_Actions']}
replacements.update({n:gf[n] for n in ['TFP_FFDP_OnCast','GD_Cast']})
def patch(s):
 fs=functions(s)
 for name,new in replacements.items():
  if name in fs:s=s.replace(fs[name],new,1)
 return s
''' +s[b:]
s=s.replace('and edited==1','and edited>=1')
s=s.replace("list(replacements)+['VG82_UpdateCounter']","list(replacements)")
a=s.index('# Update the object data');b=s.index('headers=[',a)
s=s[:a]+'''# Merge the installed unit buff fields onto v83, preserving all newer objects.
import objdata, copy
for label,path in [('base',BASE),('installed',DONOR),('guardian',GUARDIAN)]:
 (R/(label+'.w3u')).write_bytes(read_map(path,'war3map.w3u'))
data=objdata.load(str(R/'base.w3u'));donor=objdata.load(str(R/'installed.w3u'));guard=objdata.load(str(R/'guardian.w3u'))
records=lambda d:{(e['oldId'],e['newId']):e for tab in d['tables'] for e in tab}
drec=records(donor); changes=[]
for key,e in records(data).items():
 if key[0] in ['ogru','ugho'] and key[1]=='\\0'*4:
  dm={m['id']:m for m in drec[key]['mods']}
  for m in e['mods']:
   if m['id'] in ['udef','ua1b','uhpm']:
    changes.append([key[0],m['id'],m['value'],dm[m['id']]['value']]);m.update(copy.deepcopy(dm[m['id']]))
assert len(changes)==6
pylons=[e for tab in guard['tables'] for e in tab if e['newId']=='hGpy'];assert len(pylons)==1
assert not any(e['newId']=='hGpy' for tab in data['tables'] for e in tab)
data['tables'][1].append(copy.deepcopy(pylons[0]));(O/'war3map.w3u').write_bytes(objdata.dump(data))
assets=[]
for folder,path,key in [('guardian-visuals-v68',GUARDIAN,'changed_members'),('dark-matter-icon-v68',DARK,'replaced_members')]:
 for n in json.loads((W/folder/'verification.json').read_text())[key]:
  if n.endswith(('.blp','.mdx')):
   dest=O/n.replace('\\\\','/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(read_map(path,n));assets.append(n)
imp=original['war3map.imp'];version,count=struct.unpack_from('<II',imp);p=8;existing=[]
for _ in range(count):
 flag=imp[p];p+=1;end=imp.index(0,p);name=imp[p:end].decode('latin1');p=end+1
 existing.append(name if flag in [10,13] else 'war3mapImported\\\\'+name)
assert p==len(imp)
added=[n for n in assets if n not in existing]
(O/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(added))+imp[8:]+b''.join(b'\\x0d'+n.encode()+b'\\0' for n in added))
wts=read_map(BASE,'war3map.wts')
wts,n=re.subn(rb'(STRING 1\\s*\\{\\s*)[^\\r\\n]+',lambda m:m[1]+b'Footmen Frenzy 799X v84 - Consolidated Test',wts,count=1);assert n==1
(O/'war3map.wts').write_bytes(wts)
(R/'merge-changes.json').write_text(json.dumps({'functions':list(replacements),'unit_fields':changes,'new_unit':'hGpy','assets':assets,'imports_added':added},indent=2))
''' +s[b:]
s=s.replace('v83 ultimate stacks from Z kills','v84 consolidated latest 799X')
a=s.index("(O/'FF_MAINTENANCE.md').write_bytes");b=s.index('out=',a)
s=s[:a]+'''(O/'FF_MAINTENANCE.md').write_bytes(original['FF_MAINTENANCE.md']+b'\\n\\nv84: Consolidated v83 with installed v68 spawn intervals/v69 Ghoul-Grunt buffs and completed Guardian dome/pylon/icon and Dark Matter icon branches. All v83 gameplay retained except the two explicitly merged spawn settings functions. Solo four-player variant and explicitly excluded casino/profile prototypes remain separate. Runtime/editor/archive checks passed; engine playtest pending.\\n')
'''+s[b:]
s=s.replace("out=R/'release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x'","out=R/'release/FF799X_Rx_Consolidated_v84_TEST.w3x'")
s=s.replace('Build permanent ultimate damage from Z kills on verified v82.','Consolidate verified latest 799X branches without dropping v83 content.')
(R/'build.py').write_text(s)
