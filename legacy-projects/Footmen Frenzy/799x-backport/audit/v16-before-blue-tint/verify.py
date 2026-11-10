"""Validate every archive member, including files absent from the MPQ listfile."""
from pathlib import Path
import sys, re, struct, hashlib, wave, io, json
ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT.parent / 'mini-foots/tools')]
from mpyq import MPQArchive
import objdata
BASE = Path(r'C:\Users\User\Documents\Warcraft III\Maps\Test\Archive\FF799X_Rx_HeroTavern_v1.w3x')
RELEASE = ROOT / 'release/FF799X_Rx_Orianna_v16.w3x'
base = MPQArchive(str(BASE), listfile=False)
release = MPQArchive(str(RELEASE), listfile=False)
checks = []
def check(name, condition):
    assert condition, name
    checks.append(name)
def entries(archive):
    result = {}
    original = archive.get_hash_table_entry
    for entry in archive.hash_table:
        if entry.block_table_index >= len(archive.block_table): continue
        archive.get_hash_table_entry = lambda _, entry=entry: entry
        key = (entry.hash_a, entry.hash_b, entry.locale, entry.platform)
        try:
            result[key] = archive.read_file('ignored')
        except (RuntimeError, NotImplementedError):
            # Legacy PKWARE/encrypted entries: require byte-exact compressed preservation.
            block = archive.block_table[entry.block_table_index]
            archive.file.seek(block.offset + archive.header['offset'])
            result[key] = (block.flags, block.size, archive.file.read(block.archived_size))
    archive.get_hash_table_entry = original
    return result
before, after = entries(base), entries(release)
allowed = set()
for path in (ROOT / 'src').rglob('*'):
    if not path.is_file(): continue
    name = str(path.relative_to(ROOT / 'src')).replace('/', '\\')
    check('Packaged '+name, release.read_file(name) == path.read_bytes())
    entry = base.get_hash_table_entry(name)
    if entry: allowed.add((entry.hash_a,entry.hash_b,entry.locale,entry.platform))
for name in ['(listfile)', '(attributes)', '(signature)']:
    entry = base.get_hash_table_entry(name)
    if entry: allowed.add((entry.hash_a,entry.hash_b,entry.locale,entry.platform))
preserved = 0
for key, data in before.items():
    if key not in allowed:
        check('Preserved archive entry '+str(key), key in after and after[key] == data)
        preserved += 1

source = (ROOT / 'src/war3map.j').read_text(encoding='utf-8-sig')
orianna = source[source.index('// Orianna balance'):source.index('// Standalone spell runtime.')]
for path in set(re.findall(r'"([^"\n]+\.(?:mdl|mdx|wav))"', orianna)):
    path = path.replace('\\\\','\\')
    if path.lower().startswith('spells\\orianna'):
        check('Runtime asset '+path, release.read_file(path) is not None)
for path in (ROOT / 'src/Spells/Orianna/Feedback').glob('*.wav'):
    with wave.open(io.BytesIO(release.read_file(str(path.relative_to(ROOT/'src')))), 'rb') as wav:
        check('Mono PCM '+path.name, (wav.getnchannels(),wav.getsampwidth(),wav.getframerate()) == (1,2,22050))
        samples = struct.unpack('<'+'h'*wav.getnframes(),wav.readframes(wav.getnframes()))
        check('Audible samples '+path.name, max(map(abs,samples)) > 2000)
for name in ['OrbLightningX.mdx','OrbLightX.mdx']:
    data = release.read_file('war3mapImported\\'+name); at=4
    check('MDX '+name,data[:4]==b'MDLX')
    while at < len(data):
        tag=data[at:at+4]; size=struct.unpack_from('<I',data,at+4)[0]
        if tag==b'TEXS':
            for pos in range(at+8,at+8+size,268):
                texture=data[pos+4:pos+264].split(b'\0')[0].decode()
                raw=release.read_file(texture)
                check('Self-contained texture '+texture, raw is not None and raw[:4]==b'BLP1')
        at += 8+size
    check('Complete model '+name,at==len(data))

def objects(filename, folder):
    obj=objdata.load(str(folder/filename))
    check('Object roundtrip '+str(folder/filename),objdata.dump(obj)==(folder/filename).read_bytes())
    return {e['newId'] if e['newId']!='\0'*4 else e['oldId']:e for table in obj['tables'] for e in table}
lich_stats=json.loads((ROOT/'lich-stats.json').read_text())
for filename, permitted in [('war3map.w3u',{'HOr1','hor1','hor2'}),('war3map.w3a',{'AOz1','AOz2','AOz3','AOz4','AOz5','AOz7','AGf1','AGr2'}),('war3map.w3h',{'BOr4','BOr5'})]:
    old=objects(filename,ROOT.parent/'mini-foots/base/files');new=objects(filename,ROOT/'src')
    if filename=='war3map.w3u':
        disabled=set(json.loads((ROOT/'hero-policy.json').read_text())['disabled_hero_ids'])
        for e in old.values():
            for m in e['mods']:
                if m['id'] in ('useu','utra') and isinstance(m['value'],str):m['value']=','.join(x for x in m['value'].split(',') if x not in disabled)
    check('Object scope '+filename, all(old[k]==new[k] for k in old if k not in permitted) and set(new)-set(old)<=permitted)
    for k in permitted & old.keys():
        previous={(m['id'],m.get('level',0)):m for m in old[k]['mods']}
        current={(m['id'],m.get('level',0)):m for m in new[k]['mods']}
        fields={'HOr1':{'umdl','usnd','uico','ussi','ucpt','ucbs'}|set(lich_stats['fields']),'hor1':{'umxp','umxr','umdl'},'hor2':{'umxp','umxr','umdl'},'AOz1':{'aani'},'AOz3':{'aani'},'AOz2':{'aare','aub1','arut','aani'},'AOz4':{'aare','aub1','arut','aani'},'AOz5':{'abuf'},'AOz7':{'atat'},'AGf1':{'aare','atar','adur','ahdu'},'AGr2':{'Ncl6'},'BOr4':{'ftat','fta0','ftac'}}[k]
        check('Only permitted fields '+k, all(current[key]==value for key,value in previous.items() if key[0] not in fields))
        if k=='HOr1':
            check('Orianna uses downloaded Enchantress model',current['umdl',0]['value']==r'Models\OriannaEnchantress\BlackLegionEnchantressV2.mdx')
            check('Orianna uses native Sorceress voice',current['usnd',0]['value']=='Sorceress')
            check('Sorceress portrait icon',current['uico',0]['value']==r'ReplaceableTextures\CommandButtons\BTNSorceress.blp')
            check('Cast point matches spell release',abs(current['ucpt',0]['value']-.5)<.001 and abs(current['ucbs',0]['value']-1.033)<.001)
            for field,expected in lich_stats['fields'].items():
                value=current[field,0]['value']
                check('Lich stats / Necromancer projectile '+field,abs(value-expected['value'])<.0001 if isinstance(value,(float,int)) else value==expected['value'])
        if k=='AOz7':
            check('No inherited Endurance Aura target art',current['atat',0]['value']=='')
        if k in ('AOz1','AOz2','AOz3','AOz4'):
            check('Enchantress animation '+k,current['aani',0]['value']==('stand,channel' if k=='AOz4' else 'spell,attack'))
        if k in ('AOz2','AOz4'):
            radii = [207.9,225.225,242.55,277.2,311.85,346.5] if k=='AOz2' else [211.75,254.1,296.45]
            for level,radius in enumerate(radii,1):
                check('Reduced object radius '+k+' '+str(level),abs(current['aare',level]['value']-radius)<.001)
                check('Updated spell tooltip '+k+' '+str(level),'Radius: '+format(radius,'g')+'.' in current['aub1',level]['value'])
            if k=='AOz2':
                check('Pulse description matches timing',all('Expands in 0.25 seconds' in m['value'] for m in new[k]['mods'] if m['id'] in ('aub1','arut')))
check('Protect has no bird model', 'PriestMissile' not in orianna and 'SpiritOfVengeanceMissile' not in orianna)
check('Protect speed art is native scroll effect', r'Abilities\\Spells\\Items\\AIsp\\SpeedTarget.mdl' in orianna)
check('Protect heal art is native priest effect', r'Abilities\\Spells\\Human\\Heal\\HealTarget.mdl' in orianna)
manifest=json.loads((ROOT/'manifest.json').read_text())
for stat in lich_stats['runtime']:
    values=[float(re.search(r'set udg_hero_'+stat+r'\['+str(index)+r'\]=([0-9.]+)',source)[1]) for index in [10,92]]
    check('Lich runtime attributes and growth '+stat,values[0]==values[1])
functions=lambda s:{m[1]:m[0] for m in re.finditer(r'^function (\w+) takes .*?^endfunction',s,re.M|re.S)}
old=functions((ROOT.parent/'mini-foots/base/files/war3map.j').read_text(encoding='utf-8-sig'));new=functions(source)
check('Runtime function scope', {n for n in old if old[n]!=new[n]}==set(manifest['changed_functions']))
check('Added function scope',set(new)-set(old)==set(manifest['added_functions']))
report={'passed':True,'checks':len(checks),'preserved_archive_members':preserved,'base_members':len(before),'release_members':len(after),'sha256':hashlib.sha256(RELEASE.read_bytes()).hexdigest(),'live_gameplay':'Not tested','check_names':checks}
(ROOT/'audit/verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='check_names'},indent=2))
