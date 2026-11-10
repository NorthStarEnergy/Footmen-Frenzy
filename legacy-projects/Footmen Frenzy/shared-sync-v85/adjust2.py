from pathlib import Path
p=Path('shared-sync-v85/build.py');s=p.read_text()
anchor='# Resolve only missing function dependencies; never overwrite another existing subsystem implicitly.'
s=s.replace(anchor,'''def non_destructive_limit(body):
 pattern=r"(?ms)^            if itemTypeId == 'I009' then.*?^            else\\n(.*?)^            endif\\n"
 body,count=re.subn(pattern,lambda m:''.join(line[4:]+'\\n' for line in m[1].splitlines()),body);assert count==1
 return body
replacements[n]=non_destructive_limit(replacements[n])
'''+anchor)
s=s.replace("solo_replacements['Trig_ITEM_limits_Actions']=sf['Trig_ITEM_limits_Actions'].replace", "solo_replacements['Trig_ITEM_limits_Actions']=non_destructive_limit(sf['Trig_ITEM_limits_Actions']).replace")
p.write_text(s)
