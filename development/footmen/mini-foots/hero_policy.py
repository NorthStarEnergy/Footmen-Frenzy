"""Executed by Mini Foots build_source after hero ports; keeps test heroes unavailable."""
hero_types=dict((int(i),uid) for i,uid in re.findall(r"set udg_hero_type\[(\d+)\]='(....)'",s))
category_fn=re.search(r'function Trig_set_hero_stats_Actions takes .*?\nendfunction',s,re.S).group()
categories=dict((int(i),int(c)) for i,c in re.findall(r'set udg_hero_category\[(\d+)\]=(\d+)',category_fn))
allowed={uid for i,uid in hero_types.items() if i<=93 and categories.get(i,0)>0}
allowed.update({'HOr1','HGr1'})
units=objdata.load(str(O/'war3map.w3u'))
hero_ids={e['newId'] if e['newId']!='\0'*4 else e['oldId'] for tab in units['tables'] for e in tab if e['oldId'][0].isupper()}
blocked=(hero_ids-allowed)|{'HTf1','HMu1','HDk1','U00F','H00U','H02W','test'}
blocked.discard('H0R0') # Random-pick purchase token, not a playable test hero.
tech_blocked={uid for i,uid in hero_types.items() if uid in blocked}|{'HTf1','HMu1','HDk1','U00F','H00U','H02W','test'}
assert not {'HOr1','HGr1'} & blocked
condition=' or '.join("id == '"+uid+"'" for uid in sorted(blocked))
helpers='''function MF_HeroDisabled takes integer id returns boolean
    return CONDITION
endfunction

function MF_StockUnit takes unit shop, integer id, integer current, integer maximum returns nothing
    if not MF_HeroDisabled(id) then
        call AddUnitToStock(shop, id, current, maximum)
    endif
endfunction

function MF_StockUnitBJ takes integer id, unit shop, integer current, integer maximum returns nothing
    call MF_StockUnit(shop, id, current, maximum)
endfunction

'''.replace('CONDITION',condition)
s=s.replace('call AddUnitToStockBJ(', 'call MF_StockUnitBJ(').replace('call AddUnitToStock(', 'call MF_StockUnit(')
pos=re.search(r'^function ',s,re.M).start();s=s[:pos]+helpers+s[pos:]
needle='    local integer c = FFR_Category(index)'
assert needle in s
s=s.replace(needle,needle+'\n    if MF_HeroDisabled(udg_hero_type[index]) then\n        return false\n    endif',1)
for i,uid in hero_types.items():
 if uid in blocked:
  s=re.sub(r'(set udg_hero_category\['+str(i)+r'\]=)\d+',r'\g<1>0',s)
needle="        call SetPlayerTechMaxAllowed(Player(i), 'Rhme', 5)"
assert needle in s
s=s.replace(needle,needle+'\n'+'\n'.join("        call SetPlayerTechMaxAllowed(Player(i), '"+uid+"', 0)" for uid in sorted(tech_blocked)),1)
s=re.sub(r'function Trig_spawn_killa_Actions takes .*?\nendfunction','function Trig_spawn_killa_Actions takes nothing returns nothing\n    // Test-only hero disabled in Mini Foots.\nendfunction',s,flags=re.S)
for tab in units['tables']:
 for e in tab:
  for m in e['mods']:
   if m['id'] in ('useu','utra') and isinstance(m['value'],str):
    m['value']=','.join(uid for uid in m['value'].split(',') if uid not in blocked)
(O/'war3map.w3u').write_bytes(objdata.dump(units))
(R/'hero-policy.json').write_text(json.dumps({'allowed_roster':sorted(allowed),'disabled_hero_ids':sorted(blocked),'exceptions':['HOr1','HGr1']},indent=2))
