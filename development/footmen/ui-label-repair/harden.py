from pathlib import Path
for p in [Path('taverns-v66/prepare.py'),Path('pub-xp-v67/prepare.py')]:
 s=p.read_text();old="(O/'war3map.wts').write_text(wts,encoding='utf-8')" if p.parts[0]=='taverns-v66' else "(O / 'war3map.wts').write_text(wts, encoding='utf-8')"
 new="(O / 'war3map.wts').write_bytes(re.sub(r'\\r+\\n', '\\n', wts).replace('\\n', '\\r\\n').encode('utf-8'))"
 assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
p=Path('ui-label-repair/repair.py');s=p.read_text();old=" names=[x['path'] for x in json.loads((W/'size-audit-v50/archive-files.json').read_text())]";new=old+'''
 imp=read_storm(h,'war3map.imp');version,count=struct.unpack_from('<II',imp);pos=8
 for _ in range(count):
  flag=imp[pos];pos+=1;end=imp.index(0,pos);name=imp[pos:end].decode('latin1');pos=end+1
  names.append(name if flag in (10,13) else 'war3mapImported\\\\'+name)
 names=list(dict.fromkeys(names))
''';assert old in s;p.write_text(s.replace(old,new))
