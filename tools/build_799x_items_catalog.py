"""Generate the Items catalog on top of an exact current 799X map.

Run from the repository root. Preparation never installs or overwrites an output.
Use the staged Build-Map.ps1 for compilation, archive checks, and delivery.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re
import shutil
import struct

from map_archive import Archive
from restore_rc6_item_text import strings, resolved
from custom_ui_toolbar import apply_toolbar

ROOT = Path(__file__).resolve().parents[1]
FEATURE = ROOT / 'projects/799x/features/items-catalog'
AUDIT = ROOT / 'development/footmen/799x-backport/item-audit'
WIKI = ROOT / 'development/footmen/799x-backport/item-wiki/dist/data.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(text):
    return re.sub(r'\|c[0-9a-fA-F]{8}|\|r', '', text or '').replace('|n', '\n').replace('\ufffd', "'")


def quoted(text):
    text=str(text)
    if len(text)>700:
        return ' + '.join(quoted(text[i:i+700]) for i in range(0,len(text),700))
    return '"' + text.replace('\\', '\\\\').replace('"', '\\"').replace('\r', '').replace('\n', '\\n') + '"'


def parse_objects(data, wts, extended=False):
    pos = 4
    version = struct.unpack_from('<i', data)[0]
    def integer():
        nonlocal pos
        value = struct.unpack_from('<i', data, pos)[0]
        pos += 4
        return value
    out = {}
    for _ in range(2):
        for _ in range(integer()):
            old, new = data[pos:pos+4], data[pos+4:pos+8]
            pos += 8
            if version >= 3:
                extra_count = integer()
                pos += extra_count*4
            uid = (old if new == bytes(4) else new).decode('ascii')
            row = {'parent': old.decode('ascii'), 'fields': {}}
            for _ in range(integer()):
                field = data[pos:pos+4].decode('ascii')
                pos += 4
                kind = integer()
                level = integer() if extended else 0
                if extended:
                    integer()
                if kind == 3:
                    end = data.index(0, pos)
                    value = resolved(data[pos:end+1], wts).rstrip(b'\0').decode('utf-8')
                    pos = end+1
                else:
                    value = struct.unpack_from('<f' if kind in (1, 2) else '<i', data, pos)[0]
                    pos += 4
                pos += 4
                row['fields'][field, level] = value
            out[uid] = row
    assert pos == len(data), (pos, len(data))
    return out


def merged_objects(archive, wts, ext):
    out = {}
    for name in ['war3mapSkin.'+ext, 'war3map.'+ext]:
        try:
            rows = parse_objects(archive.read(name), wts, ext == 'w3a')
        except KeyError:
            continue
        for uid, row in rows.items():
            out.setdefault(uid, {'parent': row['parent'], 'fields': {}})['fields'].update(row['fields'])
    return out


def functions(script):
    return {m[1]: m[0] for m in re.finditer(r'^function (\w+) takes .*?^endfunction', script, re.M | re.S)}


def collect(archive, common):
    wts = strings(archive.read('war3map.wts'))
    items = merged_objects(archive, wts, 'w3t')
    # Unmodified standard boots are accepted by the current amulet helper.
    # This is catalog fallback data only, never an object-data edit.
    # Vanilla gold cost: https://classic.battle.net/war3/neutral/buildings.shtml
    items.setdefault('bspd', {'parent':'bspd','fields':{('unam',0):'Boots of Speed',('igol',0):250,('iabi',0):'AIms'}})
    units = merged_objects(archive, wts, 'w3u')
    abilities = merged_objects(archive, wts, 'w3a')
    script = archive.read('war3map.j').decode('utf-8').replace('\r\n', '\n')
    old = json.loads(WIKI.read_text())
    historical = {i['id']: i for i in old['items']}
    icon_defaults = {i['id']: i['path'] for i in json.loads((AUDIT/'wiki-icon-provenance.json').read_text())}
    icon_defaults['bspd'] = r'ReplaceableTextures\CommandButtons\BTNBootsOfSpeed.blp'
    inherited_costs = {}

    def value(table, uid, field, default=None, level=0):
        row = table.get(uid, {})
        if (field, level) in row.get('fields', {}):
            return row['fields'][field, level]
        parent = row.get('parent', uid)
        if parent != uid:
            return value(table, parent, field, default, level)
        return default

    def price(uid):
        v = value(items, uid, 'igol')
        if v is None:
            base = items[uid]['parent']
            v = historical.get(base, historical.get(uid, {})).get('cost')
            assert v is not None, ('Missing inherited price', uid, base)
            inherited_costs[uid] = dict(parent=base, gold=int(v), source='retained vanilla cost from audited item data')
        return int(v)

    def name(uid):
        return plain(value(items, uid, 'unam', historical.get(uid, {}).get('name', uid)))

    model_icons = {
        'n004': r'ReplaceableTextures\CommandButtons\BTNMarketplace.blp',
        'n007': r'ReplaceableTextures\CommandButtons\BTNGoblinMerchant.blp',
        'n01B': r'ReplaceableTextures\CommandButtons\BTNBlacksmith.blp',
        'h001': r'ReplaceableTextures\CommandButtons\BTNArcaneObservatory.blp',
    }
    order = ['n000','n004','n01B','n007','n012','n01T','n02N','n045','n046','n01Y','n02Z','h001']
    placed = set(re.findall(r"(?:BlzCreateUnitWithSkin|CreateUnit)\(\s*\w+\s*,\s*'(.{4})'", script))
    shops = []
    excluded = []
    for uid in order:
        assert uid in placed, ('Shop is no longer placed', uid)
        stock = value(units, uid, 'usei', '').split(',')
        if uid == 'n007' and "AddItemToStock(u,'IGs1'" in script:
            stock.append('IGs1')
        for item in list(stock):
            if item not in items:
                excluded.append(dict(shop=uid, item=item, reason='undefined item rawcode'))
                stock.remove(item)
        title = plain(value(units, uid, 'unam', uid))
        if uid in ('n01Y', 'n02Z'):
            title += ' - ' + ('Page 1' if uid == 'n01Y' else 'Page 2')
        if uid == 'h001':
            title = 'Map information'
        art = value(units, uid, 'uico', model_icons.get(uid))
        assert art, ('Missing shop artwork', uid)
        shops.append(dict(id=uid, name=title, icon=art, items=list(dict.fromkeys(stock))))
    live = set(i for s in shops for i in s['items'])
    recipes = []
    alternatives = []
    amulet_body = functions(script).get('FF_AmuletComponent', '')
    if amulet_body:
        alternatives = re.findall(r"set component\s*=\s*GetItemOfTypeFromUnitBJ\(u,\s*'(.{4})'", amulet_body)
    for func, body in functions(script).items():
        ingredients = re.findall(r"RemoveItem\(GetItemOfTypeFromUnitBJ\(GetTriggerUnit\(\),\s*'(.{4})'\)\)", body)
        result = re.findall(r"UnitAddItemByIdSwapped\('(.{4})',\s*GetTriggerUnit\(\)\)", body)
        if 'FF_AmuletComponent(GetTriggerUnit())' in body:
            ingredients.insert(1, 'I001')
        if ingredients and len(result) == 1:
            recipe = next((i for i in ingredients if i in live and 'recipe' in name(i).lower()), None)
            if recipe:
                recipes.append(dict(id=recipe, ingredients=ingredients, result=result[0], function=func,
                                    alternatives=alternatives if 'FF_AmuletComponent(GetTriggerUnit())' in body else []))
    crafted = [r['result'] for r in recipes]
    shops.append(dict(id='crafted', name='Crafted items', icon=r'ReplaceableTextures\CommandButtons\BTNBlacksmith.blp', items=crafted))
    starting = ['I001'] + [i for i in alternatives if i != 'I001']
    shops.append(dict(id='starting',name='Starting items & recipe alternatives',icon=r'ReplaceableTextures\CommandButtons\BTNBootsOfSpeed.blp',items=starting))
    tokens = {}
    for m in re.finditer(r"set udg_FFCH_Item\[(\d+)\]\s*=\s*'(.{4})'", script):
        n, uid = m[1], m[2]
        def token_field(field, pattern):
            return re.search(r'set udg_FFCH_'+field+r'\['+n+r'\]\s*=\s*'+pattern, script)[1]
        tokens[uid] = dict(ability=token_field('Ability', "'(.{4})'"),slot=int(token_field('Slot', r'(\d+)')),
                           price=int(token_field('Price', r'(\d+)')),name=token_field('Name', '"([^"]+)"'))
    for slot in range(1,5):
        stock = [uid for uid,t in tokens.items() if t['slot']==slot]
        shops.append(dict(id='CH'+str(slot), name='Custom Hero - '+ 'ZXCV'[slot-1] +' spells',
                          icon=r'ReplaceableTextures\CommandButtons\BTNArcaneVault.blp', items=stock))
    all_ids = list(dict.fromkeys(i for s in shops for i in s['items']))
    for r in recipes:
        for uid in r['ingredients']:
            if uid not in all_ids:
                all_ids.append(uid)
    rows=[]
    recipe_for={r['id']:r for r in recipes}
    recipe_for.update({r['result']:r for r in recipes})
    for uid in all_ids:
        assert uid in items, ('Missing item',uid)
        h=historical.get(uid,{})
        desc=value(items,uid,'utub') or value(items,uid,'ides') or h.get('summary','')
        art=value(items,uid,'iico',icon_defaults.get(uid,icon_defaults.get(items[uid]['parent'])))
        assert art, ('No item icon',uid)
        gold=tokens[uid]['price'] if uid in tokens else price(uid)
        loc=[s['name'] for s in shops if uid in s['items']]
        note=''
        if uid in tokens:
            note='Custom Hero mode only. Buy within 45 seconds. One spell per slot and one copy per team; one Z area spell per team.'
        if uid in recipe_for and recipe_for[uid]['alternatives']:
            note='Uses the starting amulet. After owning an amulet upgrade, the recipe also accepts '+', '.join(name(i) for i in alternatives)+'. The total shown uses the free starting amulet.'
        if uid in crafted:
            note='Crafted item; not sold directly. Open Recipe for its components and total acquisition cost. '+note
        if uid == 'I001':
            note='Granted starting item; free recipe component.'
        rows.append(dict(id=uid,name=tokens.get(uid,{}).get('name',name(uid)),icon=art,cost=gold,
                         lumber=int(value(items,uid,'ilum',0)),description=desc,location='; '.join(loc) or 'Recipe component',
                         note=note,spell=tokens.get(uid,{}).get('ability'),recipe=recipe_for.get(uid)))

    # Native field types come from the configured common.j, labels from the audit.
    native={m[2]:(1 if m[1]=='Integer' else 2) for m in re.finditer(r"ConvertAbility(Integer|Real)LevelField\('(.{4})'\)",common)}
    defaults={}
    labels={}
    for item in old['items']:
        for a in item['abilities']:
            defaults[a['id']]=a
            for f in a['fields']:
                labels[f['raw']]=f['label']
    skip={'alev','arlv','alsk','aher','aite','arac','apri','abuf','aeff','areq','atar'}
    fraction={'Ivam','Uav1','Eev1','Isx1','Imrp','Oae1','Oae2','Hab1','Ear1'}
    relevant=set()
    for row in rows:
        attached=value(items,row['id'],'iabi')
        if attached is not None:
            relevant.update(a for a in attached.split(',') if len(a)==4)
        else:
            relevant.update(a['id'] for a in historical.get(row['id'],{}).get('abilities',[]))
        if row['spell']:
            relevant.add(row['spell'])
    specs={}
    for uid in relevant:
        a=defaults.get(uid,defaults.get(abilities.get(uid,{}).get('parent'),{}))
        fields={f['raw']:f['label'] for f in a.get('fields',[]) if f['level'] in (0,1)}
        for (field,level),v in abilities.get(uid,{}).get('fields',{}).items():
            if level in (0,1) and field in native and field in labels:
                fields[field]=labels[field]
        fields.update(acdn='Cooldown (seconds)',amcs='Mana cost',adur='Duration (seconds)',ahdu='Hero duration (seconds)',aare='Area of effect',aran='Cast range')
        selected=[]
        for field,label in fields.items():
            if field not in native or field in skip or label.startswith('WESTRING'):
                continue
            selected.append(dict(field=field,label=label,kind=native[field],percent=field in fraction or '(%)' in label or '% of' in label))
        specs[uid]=selected
    for row in rows:
        # Runtime native descriptions supersede these authored fallbacks.
        row['stats']='This item has no direct stat ability. See Overview for its recipe, information, or scripted effect.'
        if row['spell']:
            uid=row['spell']
            known=defaults.get(uid,{})
            inherited={(f['raw'],f['level']):f['value'] for f in known.get('fields',[])}
            fields=[]
            for spec in specs[uid]:
                field=spec['field']
                val=value(abilities,uid,field,inherited.get((field,1)),1)
                if val is None:
                    continue
                try:
                    val=float(val)
                except (TypeError,ValueError):
                    continue
                if val==0:
                    continue
                suffix=''
                if spec['percent']:
                    val*=100
                    suffix='%'
                fields.append(f"{spec['label']}: {val:g}{suffix}")
            row['stats']=row['name']+' (level 1)\n'+'\n'.join(fields)
    # Custom TEXT frames do not reliably expand editor <object,field> references.
    # Resolve the current map's references before embedding them; keep native text
    # at runtime only when it has no unresolved reference tokens.
    candidates=json.loads((AUDIT/'candidate-data.json').read_text())
    base_abilities={a['id']:a for i in candidates['items'] for a in i['abilities']}
    aliases={
        'A01M':{'A':'Iagi','B':'Iint','C':'Istr'}, 'AIrl':{'A':'irl1','B':'irl2'},
        'AIev':{'A':'Eev1'}, 'AIrn':{'A':'Imrp'}, 'Arel':{'A':'Ihpr'},
        'AIob':{'A':'Idam'}, 'AIsx':{'A':'Isx1'}, 'AIlb':{'A':'Idam'},
        'AIlp':{'C':'Prg3'}, 'AIav':{'A':'Uav1'}, 'AIcd':{'A':'Cac1'},
        'AIpb':{'A':'Idam'}, 'AIil':{'B':'Iilw'}, 'AIva':{'A':'Ivam'},
        'AIra':{'A':'Ihps'}, 'AIsl':{'A':'irl1'}, 'AIcb':{'A':'Idic','B':'Iarp'},
        'AIs2':{'A':'Isx1'}, 'A0A7':{'C':'Ams3'}, 'Aams':{'C':'Ams3'},
        'Asta':{'D':'Sta4'}, 'A014':{'A':'Osh1','C':'Osh3'},
        'A09G':{'A':'Osh1','C':'Osh3'}, 'Apo2':{'A':'Poi1'},
    }
    standard={'Dur1':'adur','HeroDur1':'ahdu','Cool1':'acdn','Area1':'aare'}
    resolutions={}
    def expand(match):
        token=match[1]
        uid,key,*flags=token.split(',')
        if key=='uses':
            val=value(items,uid,'iuse')
        else:
            field=standard.get(key)
            if key.startswith('Data'):
                field=aliases.get(uid,{}).get(key[4])
            val=value(abilities,uid,field,None,1) if field else None
            if val is None and field:
                val=next((f['value'] for f in defaults.get(uid,{}).get('fields',[]) if f['raw']==field and f['level']==1),None)
            if val is None:
                val=base_abilities.get(uid,{}).get('base_level_1',{}).get(key)
            if val is None and (uid,key)==('AIra','DataA1'):
                val=next(f['value'] for f in defaults['A0MM']['fields'] if f['raw']=='Ihps')
        assert val is not None,('Unresolved tooltip reference',token)
        number=float(val)*(100 if '%' in flags else 1)
        replacement=f'{number:.4f}'.rstrip('0').rstrip('.') if number%1 else str(int(number))
        resolutions[token]=replacement
        return replacement
    for row in rows:
        if row['spell']:
            row['description']='Teaches '+row['name']+'.\n\n'+row['stats']
        else:
            row['description']=re.sub(r'<([^>]+)>',expand,row['description'])
    costs={r['id']:r['cost'] for r in rows}
    for r in recipes:
        r['total']=sum(costs[i] for i in r['ingredients'])
    return dict(items=rows,shops=shops,recipes=recipes,specs=specs,excluded=excluded,inherited_costs=inherited_costs,tooltip_references=resolutions),script


def generate_data(data):
    lines=[]
    idx={row['id']:i for i,row in enumerate(data['items'],1)}
    rid={row['id']:i for i,row in enumerate(data['recipes'],1)}
    for i,row in enumerate(data['items'],1):
        lines += [f"    set IC_Id[{i}] = '{row['id']}'", f"    set IC_Gold[{i}] = {row['cost']}", f"    set IC_Lumber[{i}] = {row['lumber']}"]
        for var,key in [('Name','name'),('Icon','icon'),('Description','description'),('Stats','stats'),('Location','location'),('Note','note')]:
            lines.append(f'    set IC_{var}[{i}] = {quoted(row[key])}')
        if row['spell']:
            lines.append(f"    set IC_Spell[{i}] = '{row['spell']}'")
        if row['recipe']:
            lines += [f"    set IC_Recipe[{i}] = {rid[row['recipe']['id']]}",f"    set IC_Total[{i}] = {row['recipe']['total']}"]
    for n,r in enumerate(data['recipes'],1):
        assert len(r['ingredients']) <= 7
        lines += [f"    set IC_Result[{n}] = {idx[r['result']]}",f"    set IC_IngredientCount[{n}] = {len(r['ingredients'])}"]
        for j,uid in enumerate(r['ingredients']):
            lines.append(f'    set IC_Ingredients[{n*8+j}] = {idx[uid]}')
    section=0
    stock=0
    for shop in data['shops']:
        for start in range(0,len(shop['items']),12):
            section+=1
            title=shop['name']
            if len(shop['items'])>12:
                title += f" ({start//12+1}/{(len(shop['items'])+11)//12})"
            subset=shop['items'][start:start+12]
            lines += [f'    set IC_SectionName[{section}] = {quoted(title)}', f'    set IC_SectionIcon[{section}] = {quoted(shop["icon"])}',
                      f'    set IC_SectionStart[{section}] = {stock}',f'    set IC_SectionCount[{section}] = {len(subset)}']
            for uid in subset:
                lines.append(f'    set IC_Stock[{stock}] = {idx[uid]}')
                stock+=1
    for uid,fields in sorted(data['specs'].items()):
        for j,f in enumerate(fields):
            lines += [f"    call SaveInteger(IC_Data,'{uid}',{j*4},'{f['field']}')",f"    call SaveInteger(IC_Data,'{uid}',{j*4+1},{f['kind']})",
                      f"    call SaveStr(IC_Data,'{uid}',{j*4+2},{quoted(f['label'])})"]
            if f['percent']:
                lines.append(f"    call SaveBoolean(IC_Data,'{uid}',{j*4+3},true)")
        lines.append(f"    call SaveInteger(IC_Data,'{uid}',-1,{len(fields)})")
    assert stock<8192 and len(idx)<8192 and section<8192
    parts=[]
    # Each ExecuteFunc is a bounded initialization thread, below the VM operation limit.
    for start in range(0,len(lines),160):
        n=start//160
        parts.append(f'function IC_Data{n} takes nothing returns nothing\n'+'\n'.join(lines[start:start+160])+'\nendfunction\n')
    parts.append('function IC_LoadData takes nothing returns nothing\n'+f'    set IC_Count = {len(idx)}\n    set IC_Sections = {section}\n'+
                 ''.join(f'    call ExecuteFunc("IC_Data{n}")\n' for n in range(len(parts)))+'endfunction\n')
    data['sections']=section
    return '// BEGIN ITEMS CATALOG DATA\n'+'\n'.join(parts)+'// END ITEMS CATALOG DATA\n'


def integrate(script,data_code):
    script=apply_toolbar(script).replace('\r\n','\n')
    refresh='BEGIN ITEMS CATALOG' in script
    if refresh:
        for section in ['GLOBALS','DATA','RUNTIME']:
            script,n=re.subn(r'(?ms)^\s*// BEGIN ITEMS CATALOG '+section+r'.*?// END ITEMS CATALOG '+section+r'\n?', '', script)
            assert n==1,('Catalog markers changed; manual merge required',section)
    globals_text=(FEATURE/'globals.j').read_text()
    script=script.replace('globals\n','globals\n'+globals_text+'\n',1)
    runtime=(FEATURE/'runtime.j').read_text()
    script=script.replace('function FFUI_Click takes',data_code+'\n'+runtime+'\nfunction FFUI_Click takes',1)
    old='''    set f = BlzCreateFrameByType("TEXT", "FFUI_ItemsTitle", FFUI_Items, "", 0)'''
    if not refresh:
        start=script.index(old,script.index('function FFUI_Create takes'))
        end=script.index('    call BlzTriggerRegisterFrameEvent(click, FFUI_ItemsButton',start)
        script=script[:start]+'    call IC_Init()\n'+script[end:]
    else:
        assert functions(script)['FFUI_Create'].count('call IC_Init()')==1
    needle='            call BlzFrameSetVisible(FFUI_Items, FFUI_ItemsOpen)'
    assert script.count(needle)==1
    if not refresh:
        script=script.replace(needle,needle+'\n            if FFUI_ItemsOpen then\n                call IC_Render()\n            endif')
    # Raw keyboard triggers must not cast spells while the catalog's search box is used.
    body=functions(script)['SpellKeysInput']
    guarded=body.replace('if GetLocalPlayer() == p then','if GetLocalPlayer() == p and (not FFUI_ItemsOpen or FFUI_Hidden) then',1)
    assert guarded!=body or 'not FFUI_ItemsOpen or FFUI_Hidden' in body
    script=script.replace(body,guarded,1)
    return script


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',required=True,type=Path)
    parser.add_argument('--workspace',required=True,type=Path)
    parser.add_argument('--name',required=True)
    args=parser.parse_args()
    baseline=args.baseline.resolve()
    work=args.workspace.resolve()
    assert work.is_relative_to(ROOT/'build'),'Staging directory must be inside repository build/'
    work.mkdir(parents=True,exist_ok=False)
    config=json.loads((ROOT/'tools.local.json').read_text())
    common=Path(config['common_j']).read_text()
    project=work/'projects/799x'
    src=project/'src'
    release=project/'release'
    src.mkdir(parents=True)
    release.mkdir()
    shutil.copy2(baseline,release/baseline.name)
    with Archive(config['stormlib'],baseline) as archive:
        data,original=collect(archive,common)
        generated=generate_data(data)
        updated=integrate(original,generated)
        title_match=re.search(r'7\.9\.9X-T\d+',args.name)
        assert title_match
        title=title_match[0]
        updated=re.sub(r'7\.9\.9X-T\d+',title,updated)
        (src/'war3map.j').write_bytes(updated.encode('utf-8'))
        for name in ['war3map.wts','war3map.w3i']:
            raw=archive.read(name)
            (src/name).write_bytes(re.sub(rb'7\.9\.9X-T\d+',title.encode(),raw))
    before=functions(original)
    after=functions(updated)
    changed=[name for name in before if before[name]!=after.get(name)]
    allowed={'SpellKeysClick','SpellKeysInit','SpellKeysInput','DPS_Toggle','DPS_Create','FFUI_Click','FFUI_Create'}
    # The camera initializer is the only additional function whose parent is changed.
    allowed.update(name for name,body in before.items() if 'local framehandle gameUI= BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)' in body)
    allowed.update(name for name in before if name.startswith('IC_'))
    assert set(changed)<=allowed,('Unrelated functions changed',set(changed)-allowed)
    meta=dict(map_type='799X',branch='Footmen-Frenzy-12p',release=baseline.name,sha256=digest(baseline),source_payloads=3)
    (project/'project.json').write_text(json.dumps(meta,indent=2)+'\n')
    (project/'catalog-data.json').write_text(json.dumps(data,indent=2)+'\n')
    (project/'catalog-generated.j').write_text(generated)
    report=dict(baseline=str(baseline),baseline_sha256=digest(baseline),output=args.name,
                items=len(data['items']),shops=len(data['shops']),sections=data['sections'],recipes=len(data['recipes']),
                excluded=data['excluded'],inherited_costs=data['inherited_costs'],changed_existing_functions=changed,
                preserved_existing_functions=len(before)-len(changed),live_game_tested=False)
    (project/'catalog-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    shutil.copy2(ROOT/'Build-Map.ps1',work/'Build-Map.ps1')
    shutil.copy2(ROOT/'tools.local.json',work/'tools.local.json')
    (work/'tools').mkdir()
    for name in ['build_map.py','map_archive.py','Install-Wc3Map.ps1']:
        shutil.copy2(ROOT/'tools'/name,work/'tools'/name)
    # Preserve the 512-byte pre-MPQ header while updating its map-list title.
    builder=work/'tools/build_map.py'
    header_hook='''    with destination.open('r+b') as stream:
        header = stream.read(512)
        if header.startswith(b'HM3W'):
            end = header.index(b'\\0', 8)
            assert not any(header[end + 9:])
            updated = header[:8] + TITLE_BYTES + b'\\0' + header[end + 1:end + 9]
            assert len(updated) <= 512
            stream.seek(0)
            stream.write(updated.ljust(512, b'\\0'))
'''.replace('TITLE_BYTES',repr(('Reforged Footmen '+title+' - RJE').encode()))
    builder.write_text(builder.read_text().replace('    with Archive(dll, baseline) as before,',header_hook+'    with Archive(dll, baseline) as before,'))
    # A second agent may deliver while compilation is running. Fail before any
    # installation if either the filename OR bytes of the active baseline changed.
    entry=work/'Build-Map.ps1'
    guard='''$activeDirectory=Join-Path $MapsRoot 'Tests/799X'
$active=@(Get-ChildItem -LiteralPath $activeDirectory -File | Where-Object Extension -in @('.w3x','.w3m'))
if($active.Count -ne 1 -or $active[0].Name -ne $meta.release -or (Get-FileHash -LiteralPath $active[0].FullName).Hash -ne $meta.sha256){throw '799X changed during catalog work. Rebase the feature on the new active map before delivery.'}
'''
    anchor="& (Join-Path $PSScriptRoot 'tools\\Install-Wc3Map.ps1')"
    entry.write_text(entry.read_text().replace(anchor,guard+anchor))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
