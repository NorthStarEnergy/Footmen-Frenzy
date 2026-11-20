from pathlib import Path
import sys,re,json,copy,hashlib,struct,ast
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;W=R.parent;O=R/'src'
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
base=W/'799x-backport/release/FF799X_Rx_Consolidated_Clean_v39.w3x'
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for n in ['war3map.j','war3map.w3a','war3map.wts','war3map.imp']:(O/n).write_bytes(read_storm(h,n))
assert storm.SFileCloseArchive(h)
s=(O/'war3map.j').read_text(encoding='utf-8-sig');original=s
def replace(n,new):
 global s
 s=s.replace(functions(s)[n],new,1)
def edit(n,old,new):
 f=functions(s)[n];assert old in f,(n,old);replace(n,f.replace(old,new,1))
s=s.replace('\nendglobals','\ninteger array MDV_Code\nboolean array MDV_Used\nendglobals',1)
anchor=functions(s)['MD_Clear'];s=s.replace(anchor,(R/'visuals.j').read_text()+'\n\n'+anchor,1)
edit('MD_Clear','    call FlushChildHashtable(MD_Hash, h)','    call MDV_Clear(u)\n    call FlushChildHashtable(MD_Hash, h)')
edit('MD_Start','    call SaveUnitHandle(MD_Hash, h, 1, v)','    call SaveReal(MD_Hash, h, 26, 35.0+15.0*rank)\n    call SaveUnitHandle(MD_Hash, h, 1, v)')
edit('MD_Tick','            call SaveBoolean(MD_Hash, h, 5, true)','            call SaveBoolean(MD_Hash, h, 5, true)\n            call MDV_Update(u, v)')
edit('MD_OnDamage','        set amount = RMinBJ', '''        if HaveSavedReal(MD_Hash, GetHandleId(u), 25) and MU_Now > LoadReal(MD_Hash, GetHandleId(u), 25) and GetEventDamage() > 0.0 then
            call SaveReal(MD_Hash, GetHandleId(u), 26, GetEventDamage()/(MU_Now-LoadReal(MD_Hash, GetHandleId(u), 25)))
        endif
        call SaveReal(MD_Hash, GetHandleId(u), 25, MU_Now)
        set amount = RMinBJ''')
edit('MU_Clear',"    call UnitRemoveAbility(u, 'AMqh')","    call MQ_ClearLoaded(u)\n    call UnitRemoveAbility(u, 'AMqh')")
edit('MQ_Free','    call PauseTimer(t)', '''    call DestroyEffect(LoadEffectHandle(MQ_Hash, i, 13))
    call DestroyLightning(LoadLightningHandle(MQ_Hash, i, 14))
    call DestroyTextTag(LoadTextTagHandle(MQ_Hash, i, 15))
    call PauseTimer(t)''')
edit('MQ_GroundTick',"        call BlzEndUnitAbilityCooldown(u, 'AMu1')",'''        if LoadBoolean(MQ_Hash, i, 11) then
            call MQ_LoadBloodied(u)
        endif
        call BlzEndUnitAbilityCooldown(u, 'AMu1')''')
edit('MQ_GroundTick','        call SaveReal(MQ_Hash, i, 4, life)', '''        call BlzSetSpecialEffectZ(LoadEffectHandle(MQ_Hash, i, 3), DK_GroundZ(x, y)+55.0+12.0*Sin(life*6.0))
        call MoveLightningEx(LoadLightningHandle(MQ_Hash, i, 14), true, GetUnitX(u), GetUnitY(u), DK_GroundZ(GetUnitX(u), GetUnitY(u))+60.0, x, y, DK_GroundZ(x, y)+45.0)
        call SetTextTagVisibility(LoadTextTagHandle(MQ_Hash, i, 15), IsVisibleToPlayer(x, y, GetLocalPlayer()))
        if LoadBoolean(MQ_Hash, i, 11) then
            call SetTextTagText(LoadTextTagHandle(MQ_Hash, i, 15), "BLOODIED +50% | PICK UP " + I2S(R2I(life+0.99)), 0.018)
        else
            call SetTextTagText(LoadTextTagHandle(MQ_Hash, i, 15), "PICK UP CLEAVER " + I2S(R2I(life+0.99)), 0.018)
        endif
        call SaveReal(MQ_Hash, i, 4, life)''')
edit('MQ_Land','    local effect fx','    local effect fx\n    local effect ring\n    local lightning beam\n    local texttag label')
edit('MQ_Land','call BlzSetSpecialEffectScale(fx, 2.0)','call BlzSetSpecialEffectScale(fx, 3.5)')
edit('MQ_Land','DK_GroundZ(x, y)+20.0','DK_GroundZ(x, y)+55.0')
edit('MQ_Land','        call SaveEffectHandle(MQ_Hash, i, 3, fx)',r'''        call SaveEffectHandle(MQ_Hash, i, 3, fx)
        set ring = AddSpecialEffect("buildings\\other\\CircleOfPower\\CircleOfPower.mdl", x, y)
        call BlzSetSpecialEffectScale(ring, 0.65)
        set beam = AddLightningEx("TFLN", true, GetUnitX(u), GetUnitY(u), DK_GroundZ(GetUnitX(u), GetUnitY(u))+60.0, x, y, DK_GroundZ(x, y)+45.0)
        set label = CreateTextTag()
        call SetTextTagPos(label, x-85.0, y, 100.0)
        call SetTextTagPermanent(label, true)
        call SetTextTagVisibility(label, IsVisibleToPlayer(x, y, GetLocalPlayer()))
        if LoadBoolean(MQ_Hash, i, 11) then
            call BlzSetSpecialEffectColor(fx, 255, 65, 45)
            call BlzSetSpecialEffectColor(ring, 255, 40, 25)
            call SetLightningColor(beam, 1.0, 0.15, 0.1, 0.85)
            call SetTextTagColor(label, 255, 80, 50, 255)
            call SetTextTagText(label, "BLOODIED +50% | PICK UP 3", 0.018)
        else
            call BlzSetSpecialEffectColor(ring, 255, 210, 70)
            call SetLightningColor(beam, 1.0, 0.8, 0.2, 0.65)
            call SetTextTagColor(label, 255, 220, 90, 255)
            call SetTextTagText(label, "PICK UP CLEAVER 3", 0.018)
        endif
        call SaveEffectHandle(MQ_Hash, i, 13, ring)
        call SaveLightningHandle(MQ_Hash, i, 14, beam)
        call SaveTextTagHandle(MQ_Hash, i, 15, label)''')
edit('MQ_Land','    set fx = null','    set ring = null\n    set beam = null\n    set label = null\n    set fx = null')
edit('MU_OnCleaverHit','    set udg_MissileDestroy = true','''    if LoadBoolean(MQ_Hash, i, 12) then
        set damage = damage * 1.5
        set refund = refund * 1.5
    endif
    call SaveBoolean(MQ_Hash, i, 11, true)
    set udg_MissileDestroy = true''')
edit('MU_Launch','    call SaveInteger(MU_Hash, GetHandleId(u), 20, i)', '''    call SaveBoolean(MQ_Hash, i, 12, LoadBoolean(MU_Hash, GetHandleId(u), 60))
    call MQ_ClearLoaded(u)
    call SaveInteger(MU_Hash, GetHandleId(u), 20, i)''')
edit('MU_Launch','    set udg_MissileScale = 2.0','    set udg_MissileScale = 3.0')
# Object fields and standard WC3 active/disabled icon borders.
a=objdata.load(str(O/'war3map.w3a'));es={e['newId']:e for t in a['tables'] for e in t}
def field(e,key,val,lv=0,ptr=0):
 e['mods']=[m for m in e['mods'] if (m['id'],m.get('level',0))!=(key,lv)]
 e['mods'].append(dict(id=key,type=3 if isinstance(val,str) else 0 if isinstance(val,int) else 1,level=lv,ptr=ptr,value=val,end=e['newId'].encode().hex()))
for code,name in [('AMu1','Cleaver'),('AMu3','Maul')]:
 for key in ['aart','arar']:field(es[code],key,'ReplaceableTextures\\CommandButtons\\BTNMundo'+name+'.blp')
extra='|n|cffff6655Bloodied Cleaver:|r hitting a unit bloodies the dropped blade. Retrieve it to load your next throw with +50% impact damage and +50% impact healing. One charge, consumed on throw; successful hit-and-pickup cycles refresh it without stacking. A missed throw breaks the chain. Red weapon glow means loaded.'
for m in es['AMu1']['mods']:
 if m['id'] in ['aub1','arut']:m['value']+=extra
f=functions(s)['MU_Init'];f=re.sub(r'(call BlzSetAbilityResearchExtendedTooltip\(\x27AMu1\x27, ")(.*?)(", \d\))',lambda m:m[1]+m[2]+extra+m[3],f);replace('MU_Init',f)
meal_tip='|nWhile digesting, the D slot displays the swallowed unit icon and an estimated remaining-time cooldown. A pulsing chest effect marks an active meal.'
for m in es['AMu3']['mods']:
 if m['id'] in ['aub1','arut']:m['value']+=meal_tip
f=functions(s)['MU_Init'];f=re.sub(r'(call BlzSetAbilityResearchExtendedTooltip\(\x27AMu3\x27, ")(.*?)(", \d\))',lambda m:m[1]+m[2]+meal_tip+m[3],f);replace('MU_Init',f)
codes=[]
for i in range(256):
 code=f'mD{i:02X}';assert code not in es
 e=dict(oldId='ANcl',newId=code,flags=1,extra=0,mods=[])
 for k,v in [('anam','Digestion indicator'),('aher',0),('alev',1),('abpx',2),('abpy',1),('ahky','D'),('aart','ReplaceableTextures\\CommandButtons\\BTNMundoMaul.blp'),('aani',''),('arac','other')]:field(e,k,v)
 for k,v,p in [('Ncl1',0.,1),('Ncl2',0,2),('Ncl3',1,3),('Ncl4',0.,4),('Ncl5',0,5),('Ncl6','wispharvest',6)]:field(e,k,v,1,p)
 for k,v in [('amcs',0),('acdn',3600.),('atp1','Digesting'),('aub1','Meal status'),('aran',0.),('adur',0.),('ahdu',0.)]:field(e,k,v,1)
 a['tables'][1].append(e);codes.append(code)
edit('MD_Init','    call MD_InitTypes()','\n'.join(f"    set MDV_Code[{i+1}] = '{code}'" for i,code in enumerate(codes))+'\n    call MD_InitTypes()')
(O/'war3map.w3a').write_bytes(objdata.dump(a));(O/'war3map.j').write_text(s,encoding='utf8')
p=O/'war3map.wts';p.write_bytes(p.read_bytes().replace(b'Consolidated Clean v39',b'Consolidated Mundo v40'))
tree=ast.parse((W/'799x-backport/make_magic_textures.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='blp'],type_ignores=[]),'<blp>','exec'))
templates=W/'799x-backport/tools/button-manager/Button Manager/standard';imports=[]
preview=Image.new('RGB',(384,220),'#17191d');draw=ImageDraw.Draw(preview)
for index,name in enumerate(['Cleaver','Maul']):
 art=Image.open(R/'assets'/f'{name}.png').convert('RGBA').resize((64,64),Image.Resampling.LANCZOS)
 for disabled in [False,True]:
  template=Image.open(templates/('bm_disbtn.tga' if disabled else 'bm_btn.tga')).convert('RGB')
  rendered=Image.new('RGBA',(64,64));rendered.putdata([tuple(round(c*b[0]/255) for c in p[:3])+(255,) if b[0]==b[1]==b[2] else b+(255,) for p,b in zip(art.getdata(),template.getdata())])
  folder='CommandButtonsDisabled' if disabled else 'CommandButtons';prefix='DISBTN' if disabled else 'BTN'
  n=f'ReplaceableTextures/{folder}/{prefix}Mundo{name}.blp';p=O/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blp(rendered));imports.append(n.replace('/','\\'))
  if not disabled:preview.paste(rendered.resize((192,192),Image.Resampling.NEAREST),(index*192,0))
 draw.text((index*192+12,199),name,fill='white')
preview.save(R/'assets/icons-preview.png')
imp=O/'war3map.imp';raw=imp.read_bytes();ver,count=struct.unpack_from('<II',raw);imp.write_bytes(struct.pack('<II',ver,count+len(imports))+raw[8:]+b''.join(b'\x0d'+n.encode()+b'\0' for n in imports))
af=functions(s);bf=functions(original)
metadata=dict(base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),changed_functions=[n for n in bf if bf[n]!=af[n]],added_functions=sorted(af.keys()-bf.keys()),added_abilities=codes,imports=imports)
(R/'changes.json').write_text(json.dumps(metadata,indent=2));print('Prepared Mundo v40',len(metadata['changed_functions']),'changed functions; 256 independent digestion slots.')


