from pathlib import Path
p=Path('solo-v1.8-799x/build.py');s=p.read_text()
s=s.replace("selected={n for n in df if n.startswith(('OM_','FS_')) or n=='FF_HeroTooltips_Init'}", "selected={n for n in df if n.startswith(('OM_','FS_')) or n in ['FF_HeroTooltips_Init','MF_SetAttackRange','Trig_HERO_Architect_Recruit_Actions','Trig_HERO_Architect_Recruit_Func014Func001Func013C','Trig_HERO_Architect_Recruit_Func014Func001Func013Func001C']}")
a=s.index(' # Keep only the imported')
s=s[:a]+''' # Preserve Solo message filtering in the imported Architect ownership fix.
 f=functions(s)['Trig_HERO_Architect_Recruit_Actions']
 s=s.replace(f,f.replace('call DisplayTextToForce(', 'call SoloFootsDisplayMessageToForce('),1)
 # Use the donor's effective-range setter for absolute range assignments.
 # Existing incremental range bonuses and the sniper's paired setters remain intact.
 s=re.sub(r'call BlzSetUnitWeaponRealField(?:BJ)?\\(([^,\\n]+), UNIT_WEAPON_RF_ATTACK_RANGE, 1, (udg_unit_range(?:_actual)?\\[[^\\n]+)\\)',r'call MF_SetAttackRange(\\1, \\2)',s)
'''+s[a:]
s=s.replace("raw=read_asset(path);out=O/path", """# Warcraft derives disabled-button and portrait paths at runtime.
  if path.lower().startswith('replaceabletextures\\\\commandbuttons\\\\btn'):
   assets.add(re.sub(r'(?i)CommandButtons\\\\BTN',lambda m:'CommandButtonsDisabled\\\\DISBTN',path))
  if path.lower().endswith('.mdx') and not path.lower().endswith('_portrait.mdx'):
   assets.add(path[:-4]+'_portrait.mdx')
  raw=read_asset(path);out=O/path""")
p.write_text(s)
