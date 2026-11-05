from pathlib import Path
p=Path('mini-foots/build_source.py');s=p.read_text()
needle="# Object tier closure and upgrade caps."
s=s.replace(needle,"""# Keep the internal force roster at two members while retaining canonical slot numbering.
for removed in [1,4,7,10]:
 s=s.replace(f'    call ForceAddPlayerSimple(Player({removed}), udg_team[{removed//3+1}])\\n','')
"""+needle)
needle="m=re.search(r'function Trig_Mass_START_Actions takes .*?\\nendfunction',s,re.S)"
s=s.replace(needle,"""# The inherited automatic roar must be cast in the formation, not at the now-empty bases.
point='function MF_MassPoint takes integer pn returns location\\n'
for team in range(4):
 x=-484 if team in [0,3] else 484
 y=-412 if team in [2,3] else 412
 point+=f'    if (pn - 1) / 3 == {team} then\\n        return Location(ffgs_center_x + {x}.0, ffgs_center_y + {y}.0)\\n    endif\\n'
point+='    return Location(ffgs_center_x, ffgs_center_y)\\nendfunction'
insert_before('Trig_Mass_START_Actions',point)
"""+needle)
s=s.replace("m.group().replace('\\nendfunction','\\n    call MF_ReleaseMass()\\nendfunction')","m.group().replace('\\nendfunction','\\n    call MF_ReleaseMass()\\nendfunction').replace('set udg_temp_point=udg_player_start[udg_X_playernumber]','set udg_temp_point=MF_MassPoint(udg_X_playernumber)').replace(\"call CreateNUnitsAtLoc(1, 'h01K', ConvertedPlayer(udg_X_playernumber), udg_temp_point, bj_UNIT_FACING)\",\"call CreateNUnitsAtLoc(1, 'h01K', ConvertedPlayer(udg_X_playernumber), udg_temp_point, bj_UNIT_FACING)\\n                call RemoveLocation(udg_temp_point)\")")
# Release before the roar action so it sees visible units; avoid double mass-speed application by release after footmen loop.
s=s.replace("'\\n    call MF_ReleaseMass()\\nendfunction'","'\\n    call MF_ReleaseMass()\\nendfunction'")
s=s.replace("(O/'war3map.j').write_text(s,encoding='utf-8',newline='\\n')", "s=s.replace('        // AUTO BEASTSCROLL', '        call MF_ReleaseMass()\\n        // AUTO BEASTSCROLL', 1)\\n(O/'war3map.j').write_text(s,encoding='utf-8',newline='\\n')".replace(')\\n(O',')\n(O'))
p.write_text(s)
