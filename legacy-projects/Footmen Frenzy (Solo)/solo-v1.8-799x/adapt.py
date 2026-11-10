from pathlib import Path
p=Path('../Footmen Frenzy/hero-sync/build.py');s=p.read_text()
s=s.replace("R=Path(__file__).resolve().parent; W=R.parent", "R=Path(__file__).resolve().parent; W=R.parent.parent/'Footmen Frenzy'")
s=s.replace("DONOR=W/'799x-backport/release/FF799X_Rx_WC3Icons_v25.w3x'", "DONOR=W/'fed-rewards-v80/release/FF799X_Rx_Fed_Rewards_v80_TEST.w3x'")
s=s.replace("D=R/'donor/base'", "D=R/'donor'")
s=s.replace("configs={'mini':(R/'mini/base-v8.w3x','Mini Foots v9','Mini Foots v8'), 'solo':(R/'solo/base-v1.w3x','Solo Foots 6 Player FFA v2','Solo Foots 6 Player FFA v1')}", "configs={'solo':(Path(r'C:/Users/User/Documents/Warcraft III/Maps/Solo Foots/GPT/Solo_Foots_v1.8_4P_PRELOAD_TEST07/Solo_Foots_v1.8_4P_PRELOAD_TEST07.w3x'),'Solo Foots v1.8 4P - 799X Update 08','Solo Foots v1.8')}")
s=s.replace("B=R/variant/'base';O=R/variant/'src'", "B=R/'base';O=R/'src'")
s=s.replace("(B/'war3map.j').read_text(encoding='utf-8-sig')", "(B/'war3map.j').read_text(encoding='cp1252')")
a=s.index(' selected={');z=s.index(' while True:',a)
s=s[:a]+" selected={n for n in df if n.startswith(('OM_','FS_')) or n=='FF_HeroTooltips_Init'}\n"+s[z:]
s=s.replace("['OM_Init','FS_Init','GD_Init','GTW_Init','TFP_InitTrig_FFDP_DarkPassage']", "['OM_Init','FS_Init','SF08_HeroTooltips_Init']")
s=s.replace("s=s.replace('    call SF_Initialize()',init+'\\n    call SF_Initialize()',1)", "s=s.replace('    call SoloFootsMassPreload()',init+'\\n    call SoloFootsMassPreload()',1)")
s=s.replace('for idx in [72,92]:','for idx in [92]:')
s=s.replace(" ids={'H043','HOr1','HGr1','hor1','hor2','hor3','hgr1','A0DL','AFg1','AZd1','AZd2','AFFD','ATfd','AGbs','AGbn','BGbs','BGbn'}", " ids={'HOr1','HGr1','hor1','hor2','hor3','hgr1'}")
s=s.replace("('AOz','AGr','AGf','BOr','BGr','GF0')) or k=='GFbf'", "('AOz','AGr','AGf','BOr','BGr'))")
a=s.index(' # All 12 active');z=s.index(' packaged=set()',a)
s=s[:a]+s[z:]
s=s.replace("if key(e) in {'H043','HOr1','HGr1'}:", "if key(e) in {'HOr1','HGr1'}:")
s=s.replace("(R/variant/'migration.json')", "(R/'migration.json')")
# Insert hero-specific runtime tooltip subset before ordering functions.
a=s.index(' # Stable dependency')
s=s[:a]+''' # Keep only the imported heroes' runtime tooltip overrides.
 tips=df['FF_CompactHeroTooltips_Init'].splitlines()
 tips=[line for line in tips[1:-1] if re.search(r"'(?:AOz|AGr|AGf)[^']*'",line)]
 tooltip='function SF08_HeroTooltips_Init takes nothing returns nothing\\n'+'\\n'.join(tips)+'\\nendfunction\\n'
 s=s.replace('function main takes',tooltip+'\\nfunction main takes',1)
'''+s[a:]
# Title only in config/lobby, never global byte substitution of prefix.
s=s.replace("s=s.replace(oldtitle,title).replace('Solo Foots v1.8 - 6 Player FFA v1','Solo Foots v1.8 - 6 Player FFA v2')", "s=re.sub(r'(call SetMapName\\(\\\")[^\\\"]*(\\\"\\))',lambda m:m[1]+title+m[2],s)")
s=s.replace("raw=(B/name).read_bytes().replace(oldtitle.encode(),title.encode()).replace(b'Solo Foots v1.8 - 6 Player FFA v1',b'Solo Foots v1.8 - 6 Player FFA v2');(O/name).write_bytes(raw)", "raw=(B/name).read_bytes();(O/name).write_bytes(raw)")
Path('solo-v1.8-799x/build.py').write_text(s)

