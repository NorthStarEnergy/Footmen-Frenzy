from pathlib import Path
import sys,json,difflib
W=Path.cwd();sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import *
def read(p,n):
 h=c.c_void_p();assert storm.SFileOpenArchive(str(p),0,256,c.byref(h));b=read_storm(h,n);storm.SFileCloseArchive(h);return b
installed=Path('C:/Users/User/Documents/Warcraft III/Maps/Test/FF799X_Rx_Ghoul_Grunt_Buff_v69.w3x')
a=archive(W/'pub-xp-v67/release/FF799X_Rx_Pub_XP_v67.w3x');b=archive(installed);ae,be=entries(a),entries(b)
lookup={}
for n in ['war3map.j','war3map.wct','war3map.wtg','war3map.w3u','war3mapSkin.w3u','war3map.wts','war3map.w3i','FF_MAINTENANCE.md','FF_SOURCE_MANIFEST.json','(attributes)','(listfile)']:
 e=b.get_hash_table_entry(n)
 if e:lookup[(e.hash_a,e.hash_b,e.locale,e.platform)]=n
print('installed changes',[lookup.get(k,str(k)) for k in be if be[k]!=ae.get(k)])
G=W/'guardian-visuals-v68/FF799X_Rx_Veigar_GuardianVisuals_v68.w3x';V=W/'veigar-ultimate-v83/release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x'
f=functions(read(V,'war3map.j').decode('utf-8-sig').replace('\r',''));g=functions(read(G,'war3map.j').decode('utf-8-sig').replace('\r',''))
for n in ['TFP_FFDP_OnCast','GD_Cast']:
 print(''.join(difflib.unified_diff(f[n].splitlines(True),g[n].splitlines(True),fromfile='v83',tofile='guardian-donor')))
for n in json.loads((W/'guardian-visuals-v68/verification.json').read_text())['changed_members']:
 if n.endswith(('.blp','.mdx')):print(n,'same' if archive(V).get_hash_table_entry(n) and read(V,n)==read(G,n) else 'MISSING/DIFFERENT')
for n in json.loads((W/'dark-matter-icon-v68/verification.json').read_text())['replaced_members']:
 print(n,'same' if read(V,n)==read(W/'dark-matter-icon-v68/FF799X_Rx_Veigar_Classic_v68_DarkMatterIcon.w3x',n) else 'DIFFERENT')

