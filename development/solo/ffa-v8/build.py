from pathlib import Path
import sys,re,struct,math,json,copy,io,ctypes as c,shutil,subprocess,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),str(W/'.audit-deps'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
import archive,mpyq
from objectio import Obj
B=R/'base';O=R/'src';D=R/'donor';archive.extract(R/'baseline.w3x',B)
s=(B/'war3map.j').read_text();ds=(D/'war3map.j').read_text(encoding='utf-8-sig')
pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
def put(n,t):
 global s
 s=s.replace(funcs(s)[n],t)
def body(n,t):put(n,funcs(s)[n].splitlines()[0]+'\n'+t.strip()+'\nendfunction')
def add(t):
 global s
 s+='\n'+t+'\n'
def globals_of(t):
 out={}
 for line in t[t.index('globals')+7:re.search(r'^endglobals',t,re.M).start()].splitlines():
  m=re.match(r'^\s*(?:constant\s+)?\w+\s+(?:array\s+)?(\w+)\s*(?:=.*)?$',line.split('//')[0])
  if m:out[m[1]]=line
 return out
roster=[0,4,7,11,1,3,6,9]
extra='''integer array F8_Slot
integer array F8_Team
boolean array F8_Participant
fogmodifier array F8_Entrance
boolean F8_Day=false
boolean F8_VisionReady=false
hashtable F8_Shops=null
'''
s=re.sub(r'^endglobals',lambda m:extra+'endglobals',s,count=1,flags=re.M)

# Import the installed 799X v71 Gragus/Orianna/Guardian code and dependency assets.
df=funcs(ds);sf=funcs(s);selected={n for n in df if n.startswith(('OM_','FS_','GD_','GDV_','GDB_','GFW_','GFB_','GTW_','TFP_FFDP_')) or n in ['TFP_InitTrig_FFDP_DarkPassage','FF_HeroTooltips_Init','Trig_HERO_Guardian_Purification_Nova_Actions','Trig_HERO_Guardian_Purification_Nova_Explode_Actions'] or 'Guardian_Force_Field' in n}
while True:
 text='\n'.join(df[n] for n in selected);more=(set(re.findall(r'\b\w+\b',text))&df.keys())-sf.keys()-selected
 if not more:break
 selected|=more
dg=globals_of(ds);sg=globals_of(s);needed=set(re.findall(r'\b\w+\b',text))&dg.keys()
while True:
 more=(set(re.findall(r'\b\w+\b','\n'.join(dg[n] for n in needed)))&dg.keys())-needed
 if not more:break
 needed|=more
for n in needed&sg.keys():
 if n.startswith(('OM_','FS_','GD_','GDV_','GDB_','GFW_','GFB_','GTW_','TFP_FFDP_')):s=s.replace(sg[n],dg[n],1)
s=re.sub(r'^endglobals',lambda m:'\n'.join(dg[n] for n in needed if n not in sg)+'\nendglobals',s,count=1,flags=re.M)
for n in selected:
 if n in sf:put(n,df[n])
 else:add(df[n])
add(df['MF_SetAttackRange'])
s=re.sub(r'call BlzSetUnitWeaponRealFieldBJ\(([^,\n]+), UNIT_WEAPON_RF_ATTACK_RANGE, 1, ([^\n]+)\)',r'call MF_SetAttackRange(\1, \2)',s)
donorfile=Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\stalker-v71\release\FF799X_Rx_Stalker_v71.w3x');data=donorfile.read_bytes();da=mpyq.MPQArchive(io.BytesIO(data[512:] if data[:4]==b'HM3W' else data),listfile=False)
tables={};donortables={};index={}
for ext,levelled in [('w3u',False),('w3a',True),('w3h',False)]:
 tables[ext]=Obj(B/('war3map.'+ext),levelled);donortables[ext]=Obj(D/('war3map.'+ext),levelled)
 for i,tab in enumerate(donortables[ext].tables):
  for ob in tab:index[(ob['new'] if ob['new']!=bytes(4) else ob['old']).decode()]=(ext,i,ob)
ids=set(json.loads((Path(r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\hero-sync\solo\migration.json')).read_text())['objects'])
ids|=set(re.findall(r"'(.{4})'",text+'\n'.join(dg[n] for n in needed)))&index.keys()
while True:
 more={v for id in ids if id in index for mod in index[id][2]['mods'] if isinstance(mod[4],str) for v in mod[4].split(',') if v in index}-ids
 if not more:break
 ids|=more
wts={int(m[1]):m[2] for m in re.finditer(r'STRING (\d+)[^\{]*\{\s*\n(.*?)\n\}',(D/'war3map.wts').read_text(encoding='utf-8-sig'),re.S)}
assets=set(x.replace('\\\\','\\') for x in re.findall(r'"([^"\n]+\.(?:mdx|mdl|blp|wav))"',text+'\n'.join(dg[n] for n in needed),re.I))
for id in ids:
 if id not in index:continue
 ext,i,record=index[id];record=copy.deepcopy(record)
 for mod in record['mods']:
  if isinstance(mod[4],str):
   mod[4]=re.sub(r'TRIGSTR_(\d+)',lambda m:wts.get(int(m[1]),m[0]),mod[4]);assets.update(v for v in mod[4].split(',') if re.search(r'\.(mdx|mdl|blp|wav)$',v,re.I))
 for tab in tables[ext].tables:tab[:]=[o for o in tab if (o['new'] if o['new']!=bytes(4) else o['old']).decode()!=id]
 tables[ext].tables[i].append(record)
checked=set();packaged=[]
dh=c.c_void_p();assert archive.s.SFileOpenArchive(str(donorfile),0,0x100,c.byref(dh))
def donor_read(name):
 try:return da.read_file(name)
 except RuntimeError:
  fh=c.c_void_p()
  assert archive.s.SFileOpenFileEx(dh,name.encode(),0,c.byref(fh)),name
  size=archive.s.SFileGetFileSize(fh,None)
  assert size>=0,(name,size)
  buf=c.create_string_buffer(size);got=c.c_uint()
  assert archive.s.SFileReadFile(fh,buf,size,c.byref(got),None),name
  archive.s.SFileCloseFile(fh)
  return buf.raw
while assets:
 name=assets.pop().strip().replace('\\\\','\\')
 if name.lower() in checked:continue
 checked.add(name.lower());blob=donor_read(name)
 if blob is None and name.lower().endswith('.mdl'):name=name[:-4]+'.mdx';blob=donor_read(name)
 if blob is None:continue
 out=O/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob);packaged.append(name)
 if blob[:4]==b'MDLX':
  at=4
  while at+8<=len(blob):
   tag=blob[at:at+4];size=struct.unpack_from('<I',blob,at+4)[0]
   if tag==b'TEXS':
    for q in range(at+8,at+8+size,268):
     texture=blob[q+4:q+264].split(b'\0')[0].decode()
     if texture:assets.add(texture)
   at+=8+size

objects=tables['w3u'];skin=Obj(B/'war3mapSkin.w3u');donorskin=Obj(D/'war3mapSkin.w3u')
for id in ['HGr1','HOr1','H043']:
 ob=donorskin.find(id)
 if ob:
  for tab in skin.tables:tab[:]=[o for o in tab if (o['new'] if o['new']!=bytes(4) else o['old']).decode()!=id]
  skin.tables[1].append(copy.deepcopy(ob))
# Use the authored 799X building presentation, with correct real-valued scale fields.
for id,model in [('nFHT',r'buildings\other\Tavern\Tavern.mdl'),('hhou',r'buildings\human\AltarofKings\AltarofKings.mdl')]:
 for table in [objects,skin]:
  table.set(id,'umdl',model);table.set(id,'upor',model);table.set(id,'usca',0.85,typ=1)
  for key in ['uclr','uclg','uclb']:table.set(id,key,255)
 objects.set(id,'uabi','Asud,Avul' if id=='nFHT' else 'Asud,Abds')
# Remove standard tier-based second-hero prerequisites; the altar unlock and two-hero limit remain authoritative.
heroids=set(re.findall(r"set udg_hero_type\[\d+\]\s*=\s*'(....)'",s))
for id in heroids:
 for key in ['ureq','urqa','urq1','urq2','urq3','urq4','urq5','urq6','urq7','urq8','urq9']:objects.set(id,key,'')
 objects.set(id,'usma',1);objects.set(id,'usst',0);objects.set(id,'usrg',0)
def props(id):return {m[0].decode():m[4] for m in objects.find(id)['mods']}
creepids=['n00R','n02U','n03L'];tokens={'h02U','h02V','h03O','h03P','h037','h038'}
creeps=[[v for v in props(id).get('useu','').split(',') if v and v not in tokens] for id in creepids]
unique=list(dict.fromkeys(v for page in creeps for v in page));creeps=[unique[:11],unique[11:]]
recipes=[props(id)['usei'].split(',') for id in ['n01Y','n02Z']]
for id in ['n00R','n01Y']:
 objects.set(id,'useu','');objects.set(id,'usei','');objects.set(id,'uabi','Asud,Asid,Aneu,Avul,Apit')
for id in ['h02U','h037']:
 objects.set(id,'unam','Next page');objects.set(id,'utip','Next page');objects.set(id,'ubpx',3);objects.set(id,'ubpy',2);objects.set(id,'ugol',0);objects.set(id,'ulum',0);objects.set(id,'ufoo',0)
for ext,table in tables.items():table.save(O/('war3map.'+ext))
skin.save(O/'war3mapSkin.w3u')

# One physical shop per stock family. Page buttons always reselect the same shop.
pagecode='''function F8_RefreshShop takes unit shop,integer page returns nothing
    if GetUnitTypeId(shop) == 'n00R' then
CREEPCLEAR
        call RemoveUnitFromStock(shop, 'h02U')
CREEPPAGES
        call AddUnitToStock(shop, 'h02U', 1, 1)
    elseif GetUnitTypeId(shop) == 'n01Y' then
RECIPECLEAR
        call RemoveUnitFromStock(shop, 'h037')
RECIPEPAGES
        call AddUnitToStock(shop, 'h037', 1, 1)
    endif
    call SaveInteger(F8_Shops, GetHandleId(shop), 0, page)
endfunction'''
for prefix,pages,native in [('CREEP',creeps,'Unit'),('RECIPE',recipes,'Item')]:
 pagecode=pagecode.replace(prefix+'CLEAR','\n'.join(f"        call Remove{native}FromStock(shop, '{id}')" for page in pages for id in page))
 lines=[]
 for i,page in enumerate(pages):
  lines.append(('        if' if i==0 else '        elseif')+f' page == {i} then')
  lines.extend(f"            call Add{native}ToStock(shop, '{id}', 1, 1)" for id in page)
 lines.append('        endif');pagecode=pagecode.replace(prefix+'PAGES','\n'.join(lines))
add(pagecode)
add('''function F8_ShopSale takes nothing returns nothing
    local unit shop=GetSellingUnit()
    local unit sold=GetSoldUnit()
    local integer pages=0
    local integer page
    if GetUnitTypeId(shop)=='n00R' and GetUnitTypeId(sold)=='h02U' then
        set pages=2
    elseif GetUnitTypeId(shop)=='n01Y' and GetUnitTypeId(sold)=='h037' then
        set pages=2
    endif
    if pages>0 then
        set page=ModuloInteger(LoadInteger(F8_Shops,GetHandleId(shop),0)+1,pages)
        call F8_RefreshShop(shop,page)
        call SelectUnitForPlayerSingle(shop,GetOwningPlayer(sold))
        call RemoveUnit(sold)
    endif
    set shop=null
    set sold=null
endfunction''')
sale=funcs(s)['SF_OnSale'];sale=re.sub(r"    if GetUnitTypeId\(shop\) == 'n01Y'.*?    elseif p <= 12",'    if p <= 12',sale,flags=re.S);put('SF_OnSale',sale)
condition=funcs(s)['Trig_page_system_Conditions'].replace("GetUnitTypeId(GetSellingUnit()) == 'n01Y'","GetUnitTypeId(GetSellingUnit()) == 'n01Y' or GetUnitTypeId(GetSellingUnit()) == 'n00R'");put('Trig_page_system_Conditions',condition)

# Remove obsolete quadrant vision; all permanent vision is built from the FFA roster.
for name,fn in list(funcs(s).items()):
 if 'CreateFogModifier' in fn:
  fn=re.sub(r'^.*call CreateFogModifier[^\n]*\n','',fn,flags=re.M)
  fn=re.sub(r'^.*(?:set .*GetLastCreatedFogModifier|call DestroyFogModifier\(GetLastCreatedFogModifier)[^\n]*\n','',fn,flags=re.M);put(name,fn)
add('''function F8_VisionTick takes nothing returns nothing
    local integer p=0
    local integer k
    local integer slot
    local real a
    local real extent
    local real hour=GetFloatGameState(GAME_STATE_TIME_OF_DAY)
    local boolean day=hour>=6. and hour<18.
    if F8_VisionReady and day==F8_Day then
        return
    endif
    set F8_Day=day
    set F8_VisionReady=true
    loop
        exitwhen p>=24
        if F8_Team[p]>0 then
            set k=1
            loop
                exitwhen k>8
                set slot=F8_Slot[k]
                if slot!=p then
                    if F8_Entrance[p*8+k]!=null then
                        call FogModifierStop(F8_Entrance[p*8+k])
                        call DestroyFogModifier(F8_Entrance[p*8+k])
                    endif
                    set a=SF_Angle[slot+1]
                    if day then
                        set extent=450.
                    else
                        set extent=160.
                    endif
                    set F8_Entrance[p*8+k]=CreateFogModifierRadius(Player(p),FOG_OF_WAR_VISIBLE,2320.*Cos(a),-256.+2320.*Sin(a),extent,false,false)
                    call FogModifierStart(F8_Entrance[p*8+k])
                endif
                set k=k+1
            endloop
        endif
        set p=p+1
    endloop
endfunction
function F8_InitVision takes nothing returns nothing
    local integer p=0
    local fogmodifier vision
    call FogEnable(true)
    call FogMaskEnable(true)
    loop
        exitwhen p>=24
        if p>=12 then
            set vision=CreateFogModifierRect(Player(p),FOG_OF_WAR_VISIBLE,GetPlayableMapRect(),false,false)
            call FogModifierStart(vision)
        elseif F8_Team[p]>0 then
            set vision=CreateFogModifierRadius(Player(p),FOG_OF_WAR_VISIBLE,0.,-256.,2220.,false,false)
            call FogModifierStart(vision)
            set vision=CreateFogModifierRadius(Player(p),FOG_OF_WAR_VISIBLE,SF_BaseX[p+1],SF_BaseY[p+1],1150.,false,false)
            call FogModifierStart(vision)
        endif
        set p=p+1
    endloop
    call F8_VisionTick()
    call TimerStart(CreateTimer(),1.,true,function F8_VisionTick)
    set vision=null
endfunction''')
# Independent scoring and shared -kd output for all eight original participants.
body('Trig_reveal_Actions','return')
add('''function F8_UpdateBoard takes nothing returns nothing
    local integer row=1
    local integer p
    loop
        exitwhen row>8
        set p=F8_Slot[row]+1
        call MultiboardSetItemValueBJ(udg_multiboard_kills,1,row+1,GetPlayerName(Player(p-1)))
        call MultiboardSetItemValueBJ(udg_multiboard_kills,2,row+1,I2S(udg_hero_kills[p])+"/"+I2S(udg_hero_deaths[p]))
        call MultiboardSetItemValueBJ(udg_multiboard_kills,3,row+1,I2S(udg_unit_kills[p])+"/"+I2S(udg_unit_deaths[p]))
        call MultiboardSetItemValueBJ(udg_multiboard_kills,4,row+1,I2S(udg_base_kills[p]))
        call MultiboardSetItemValueBJ(udg_multiboard_kills,5,row+1,I2S(udg_KOTH_Team_Gold_Earned_Total[row]))
        set row=row+1
    endloop
endfunction''')
body('Trig_Multiboard_Create_with_KOTH_Actions','''local integer row=1
    if udg_multiboard_kills!=null then
        call DestroyMultiboard(udg_multiboard_kills)
    endif
    call CreateMultiboardBJ(5,9,"Eight Player FFA")
    set udg_multiboard_kills=GetLastCreatedMultiboard()
    call MultiboardSetItemsStyle(udg_multiboard_kills,true,false)
    call MultiboardSetItemValueBJ(udg_multiboard_kills,1,1,"Player")
    call MultiboardSetItemValueBJ(udg_multiboard_kills,2,1,"Hero K/D")
    call MultiboardSetItemValueBJ(udg_multiboard_kills,3,1,"Unit K/D")
    call MultiboardSetItemValueBJ(udg_multiboard_kills,4,1,"Bases")
    call MultiboardSetItemValueBJ(udg_multiboard_kills,5,1,"Hill gold")
    loop
        exitwhen row>9
        call MultiboardSetItemWidthBJ(udg_multiboard_kills,1,row,12.)
        call MultiboardSetItemWidthBJ(udg_multiboard_kills,2,row,5.)
        call MultiboardSetItemWidthBJ(udg_multiboard_kills,3,row,5.)
        call MultiboardSetItemWidthBJ(udg_multiboard_kills,4,row,3.)
        call MultiboardSetItemWidthBJ(udg_multiboard_kills,5,row,4.)
        set row=row+1
    endloop
    call F8_UpdateBoard()
    call MultiboardDisplay(udg_multiboard_kills,true)''')
body('Trig_Multiboard_Update_Conditions','return not IsUnitIllusion(GetTriggerUnit()) and GetUnitAbilityLevel(GetTriggerUnit(),\'Aloc\')==0')
body('Trig_Multiboard_Update_Actions','''local unit victim=GetTriggerUnit()
    local unit killer=GetKillingUnit()
    local integer d=GetPlayerId(GetOwningPlayer(victim))+1
    local integer k=GetPlayerId(GetOwningPlayer(killer))+1
    local boolean valid=killer!=null and k<=12 and F8_Participant[k] and IsUnitEnemy(victim,Player(k-1))
    if d<=12 and F8_Participant[d] then
        if IsUnitType(victim,UNIT_TYPE_HERO) then
            set udg_hero_deaths[d]=udg_hero_deaths[d]+1
            set udg_hero_killstreak[d]=0
            if valid then
                set udg_hero_kills[k]=udg_hero_kills[k]+1
                set udg_hero_killstreak[k]=udg_hero_killstreak[k]+1
            endif
        elseif victim==udg_base[d] then
            if valid then
                set udg_base_kills[k]=udg_base_kills[k]+1
            endif
        elseif not IsUnitType(victim,UNIT_TYPE_STRUCTURE) then
            set udg_unit_deaths[d]=udg_unit_deaths[d]+1
            if valid then
                set udg_unit_kills[k]=udg_unit_kills[k]+1
            endif
        endif
    endif
    call F8_UpdateBoard()
    set victim=null
    set killer=null''')
body('Trig_KD_Actions','''local integer row=1
    local integer p
    loop
        exitwhen row>8
        set p=F8_Slot[row]+1
        if F8_Participant[p] then
            call DisplayTimedTextToPlayer(GetTriggerPlayer(),0.,0.,20.,GetPlayerName(Player(p-1))+" - Hero K/D: "+I2S(udg_hero_kills[p])+"/"+I2S(udg_hero_deaths[p])+" - Unit K/D: "+I2S(udg_unit_kills[p])+"/"+I2S(udg_unit_deaths[p]))
        endif
        set row=row+1
    endloop''')
# The obsolete KOTH row writer used column four; periodic board update owns display now.
for name,fn in list(funcs(s).items()):
 if name not in ['F8_UpdateBoard','Trig_Multiboard_Create_with_KOTH_Actions'] and 'MultiboardSetItemValueBJ' in fn:
  fn=re.sub(r'^.*call MultiboardSetItemValueBJ[^\n]*\n','',fn,flags=re.M);put(name,fn)
# Preserve authored wave selection/scaling, but distribute camps for all eight slots.
oldspawn=funcs(s)['Trig_colossal_spawn_Actions']
statblock=oldspawn[oldspawn.index('    // calculate actual'):oldspawn.index('    call RemoveLocation(udg_temp_point)')]
spawnhelper='''function F8_SpawnColo takes integer entry,real x,real y returns nothing
    set udg_X_colo=entry
    set udg_spawned_colo=CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE),udg_colossal_unit_type[udg_colossal_unit_id[entry]],x,y,Atan2(-256.-y,-x)*bj_RADTODEG)
    set udg_colossal_aggro_range=300.
'''+statblock+'''    call SetUnitState(udg_spawned_colo,UNIT_STATE_LIFE,I2R(BlzGetUnitMaxHP(udg_spawned_colo)))
endfunction''';add(spawnhelper)
tail=oldspawn[oldspawn.index('    // start new timer'):oldspawn.rindex('endfunction')]
body('Trig_colossal_spawn_Actions','''local integer k=0
    local integer p
    local integer entry
    local integer n
    local integer offset
    local integer camp
    local integer big=1
    local real a
    local real x
    local real y
    call DestroyTimerDialogBJ(udg_timer_window_colossal)
    if ModuloInteger(udg_colossal_wave,2)==0 then
        set big=2
    endif
    loop
        exitwhen k>=4
        set a=I2R(k)*bj_PI/2.+bj_PI/4.
        call F8_SpawnColo(big,480.*Cos(a),-256.+480.*Sin(a))
        set k=k+1
    endloop
    set k=1
    loop
        exitwhen k>8
        set p=F8_Slot[k]+1
        if udg_player_active[p] then
            set a=SF_Angle[p]
            set entry=3
            set offset=0
            set camp=0
            loop
                exitwhen entry>22
                if ModuloInteger(udg_colossal_unit_id[entry]-udg_colossal_wave_id,10)==0 and udg_colossal_wave>=udg_colossal_min_wave[entry] then
                    set n=0
                    loop
                        exitwhen n>=udg_colossal_number_of_units[entry]
                        set x=(3080.+I2R(offset/3)*112.)*Cos(a)-I2R(ModuloInteger(offset,3)-1)*112.*Sin(a)
                        set y=-256.+(3080.+I2R(offset/3)*112.)*Sin(a)+I2R(ModuloInteger(offset,3)-1)*112.*Cos(a)
                        call F8_SpawnColo(entry,x,y)
                        set offset=offset+1
                        set n=n+1
                    endloop
                    call F8_SpawnColo(entry,2580.*Cos(a)-I2R(camp)*160.*Sin(a),-256.+2580.*Sin(a)+I2R(camp)*160.*Cos(a))
                    set camp=camp+1
                endif
                set entry=entry+1
            endloop
        endif
        set k=k+1
    endloop
'''+tail)
# The altar requires actual availability for each offered hero, not inherited race/tier restrictions.
altar=funcs(s)['SoloFootsAltarStockAddPage'].replace('            call AddUnitToStockBJ','            call SetPlayerUnitAvailableBJ(udg_hero_type[heroIndex], true, GetOwningPlayer(altar))\n            call AddUnitToStockBJ');put('SoloFootsAltarStockAddPage',altar)
altar=funcs(s)['SoloFootsAltarStockPopulate'].replace("    call UnitAddAbility(altar, 'Asud')","    call SetUnitScale(altar,.85,.85,.85)\n    call SetUnitVertexColor(altar,255,255,255,255)\n    call ShowUnit(altar,true)\n    call UnitAddAbility(altar, 'Asud')");put('SoloFootsAltarStockPopulate',altar)

# Initial roster is established before normal mode executes.
rosterinit='\n'.join(f'    set F8_Slot[{i}]={p}\n    set F8_Team[{p}]={i}\n    set udg_teamnumber[{p+1}]={i}\n    set F8_Participant[{p+1}]=udg_player_active[{p+1}]' for i,p in enumerate(roster,1))
rosterinit+='''
    set q=1
    loop
        exitwhen q>9
        if udg_team[q]!=null then
            call DestroyForce(udg_team[q])
        endif
        set udg_team[q]=CreateForce()
        if q<=8 then
            call ForceAddPlayer(udg_team[q],Player(F8_Slot[q]))
        endif
        set q=q+1
    endloop
    set q=12
    loop
        exitwhen q>=24
        call ForceAddPlayer(udg_team[9],Player(q))
        set udg_teamnumber[q+1]=9
        set q=q+1
    endloop
'''
init=funcs(s)['SF_Initialize'];at=init.index('    set SF_BaseX');init=init[:at]+rosterinit+'\n'+init[at:];put('SF_Initialize',init)
init=funcs(s)['SF_Initialize'].replace('    set SF_GameClock=CreateTimer()', '''    set q=1
    loop
        exitwhen q>8
        call RemoveLocation(udg_colossal_point[q])
        set udg_colossal_point[q]=Location(3080.*Cos(SF_Angle[F8_Slot[q]+1]),-256.+3080.*Sin(SF_Angle[F8_Slot[q]+1]))
        set q=q+1
    endloop
    set SF_GameClock=CreateTimer()''');put('SF_Initialize',init)
put('Trig_colossal_spawn_message_Actions',funcs(s)['Trig_colossal_spawn_message_Actions'].replace('exitwhen udg_X > 4','exitwhen udg_X > 8'))
put('Trig_KOTH_Update_Text_Actions',funcs(s)['Trig_KOTH_Update_Text_Actions'].replace('"Team " + I2S(udg_KOTH_Team_Number)','GetPlayerName(udg_KOTH_Player)'))
add('''function F8_ShopInitEnum takes nothing returns nothing
    local unit u=GetEnumUnit()
    local integer id=GetUnitTypeId(u)
    if id=='n00R' or id=='n01Y' then
        call F8_RefreshShop(u,0)
    endif
    if id=='nFHT' or id=='hhou' then
        call SetUnitScale(u,.85,.85,.85)
        call SetUnitVertexColor(u,255,255,255,255)
        call ShowUnit(u,true)
    endif
    set u=null
endfunction
function F8_Start takes nothing returns nothing
    local group g=CreateGroup()
    local trigger t=CreateTrigger()
    local integer p=0
    local integer q
    set F8_Shops=InitHashtable()
    call GroupEnumUnitsInRect(g,GetPlayableMapRect(),null)
    call ForGroup(g,function F8_ShopInitEnum)
    call DestroyGroup(g)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SELL)
    call TriggerAddAction(t,function F8_ShopSale)
    loop
        exitwhen p>=12
        set q=0
        loop
            exitwhen q>=12
            if p!=q then
                call SetPlayerAlliance(Player(p),Player(q),ALLIANCE_SHARED_VISION,false)
                call SetPlayerAlliance(Player(p),Player(q),ALLIANCE_SHARED_CONTROL,false)
            endif
            set q=q+1
        endloop
        set p=p+1
    endloop
    call F8_InitVision()
    call TimerStart(CreateTimer(),1.,true,function F8_UpdateBoard)
    call DestroyTimer(GetExpiredTimer())
    set g=null
    set t=null
endfunction''')
init=funcs(s)['SF_Initialize'].replace('    set startup=null','    call TimerStart(CreateTimer(),1.20,false,function F8_Start)\n    set startup=null');put('SF_Initialize',init)

# Ordered rear shop rows follow the 799X sequence, with adequate spacing and inward facing.
source=(W/'ffa-v4/build.py').read_text();exec(source[source.index('class Reader:'):source.index('shop_types=')])
ub=(B/'war3mapUnits.doo').read_bytes();units=placements(ub);records=[];layout=[]
order=['n012','n007','n00R','n01T','n01Y','n02N','n045','n046']
angles={p:float(re.search(r'set SF_Angle\['+str(p+1)+r'\]=([^\n]+)',s)[1].replace(' ','')) for p in roster}
def nearest(x,y):return min(roster,key=lambda p:abs(math.atan2(math.sin(math.atan2(y+256,x)-angles[p]),math.cos(math.atan2(y+256,x)-angles[p]))))
path=(B/'war3map.wpm').read_bytes();pw,ph=struct.unpack_from('<II',path,8)
def walk(x,y,clear=32):
 for dx,dy in [(0,0),(clear,0),(-clear,0),(0,clear),(0,-clear)]:
  i=int((x+dx+5120)/32);j=int((y+dy+5376)/32)
  if not (0<=i<pw and 0<=j<ph) or path[16+j*pw+i]&2:return False
 return True
def seat(x,y):
 choices=[(x+dx,y+dy) for dx in range(-256,257,32) for dy in range(-256,257,32) if walk(x+dx,y+dy)]
 assert choices,('no seat',x,y)
 return min(choices,key=lambda p:math.hypot(p[0]-x,p[1]-y))
midtemplates={u['kind']:u for u in units if u['kind'] in ['n01B','n004']}
for u in units:
 kind=u['kind'];x,y=u['x'],u['y'];a=angles.get(u['owner'],angles[nearest(x,y)]);rec=bytearray(ub[u['start']:u['end']])
 if kind in ['n02U','n03L','n02Z','n01B','n004']:continue
 if kind in order:
  a=angles[nearest(x,y)];lateral=(order.index(kind)-3.5)*192.;radial=4360.
  x,y=seat(radial*math.cos(a)-lateral*math.sin(a),-256+radial*math.sin(a)+lateral*math.cos(a))
 elif kind=='hwtw':
  oldt=-x*math.sin(a)+(y+256)*math.cos(a);t=640. if oldt>0 else -640.
  x,y=3640.*math.cos(a)-t*math.sin(a),-256+3640.*math.sin(a)+t*math.cos(a)
  assert walk(x,y),('tower',x,y)
 if kind in order or kind=='hwtw':struct.pack_into('<ff',rec,8,x,y);struct.pack_into('<f',rec,20,math.atan2(-256-y,-x))
 records.append(rec);layout.append(dict(kind=kind,old=[u['x'],u['y']],new=[x,y],owner=u['owner']))
for k in range(8):
 kind='n01B' if k%2==0 else 'n004';a=(k+.5)*math.pi/4;x,y=seat(2180*math.cos(a),-256+2180*math.sin(a));u=midtemplates[kind]
 rec=bytearray(ub[u['start']:u['end']]);struct.pack_into('<ff',rec,8,x,y);struct.pack_into('<f',rec,20,math.atan2(-256-y,-x));struct.pack_into('<I',rec,len(rec)-16,9000+k)
 records.append(rec);layout.append(dict(kind=kind,old=None,new=[x,y],owner=27))
head=bytearray(ub[:16]);struct.pack_into('<I',head,12,len(records));(O/'war3mapUnits.doo').write_bytes(head+b''.join(records))
creation=funcs(s)['CreateAllUnits']
creation=re.sub(r"^.*BlzCreateUnitWithSkin\([^\n]*'(?:n02U|n03L|n02Z|n01B|n004)'[^\n]*\n",'',creation,flags=re.M)
for ch in layout:
 if ch['old'] is None:continue
 if ch['old']==ch['new']:continue
 def repl(m):
  x=float(m[2].replace(' ',''));y=float(m[3].replace(' ',''))
  if math.hypot(x-ch['old'][0],y-ch['old'][1])>.03:return m[0]
  nx,ny=ch['new'];return m[1]+f'{nx:.3f}, {ny:.3f}, {math.degrees(math.atan2(-256-ny,-nx)):.3f}'+m[5]
 creation=re.sub(r"(BlzCreateUnitWithSkin\(Player\(\d+\), '"+ch['kind']+r"', )([\d. -]+), ([\d. -]+), ([\d. -]+)(, '....'\))",repl,creation)
for i,ch in enumerate([u for u in layout if u['old'] is None]):
 x,y=ch['new'];kind=ch['kind'];ref='gg_unit_n01B_0055' if i==0 else 'gg_unit_n004_0057' if i==1 else 'gg_unit_n01B_0056' if i==2 else 'gg_unit_n004_0058' if i==3 else 'u'
 creation=creation.replace('endfunction',f"    set {ref}=BlzCreateUnitWithSkin(Player(27), '{kind}', {x:.3f}, {y:.3f}, {math.degrees(math.atan2(-256-y,-x)):.3f}, '{kind}')\nendfunction")
put('CreateAllUnits',creation)
(R/'layout.json').write_text(json.dumps(layout,indent=2));(R/'shop-pages.json').write_text(json.dumps(dict(creeps=creeps,recipes=recipes),indent=2))
title='Solo Foots 8 Player FFA v8';s=re.sub(r'call SetMapName\("[^"]+"\)',f'call SetMapName("{title}")',s)
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
imp=(B/'war3map.imp').read_bytes();ver,count=struct.unpack_from('<II',imp);at=8;registered=set()
while at<len(imp):end=imp.index(0,at+1);registered.add(imp[at+1:end].decode().lower());at=end+1
new=sorted(set(p for p in packaged if p.lower() not in registered));(O/'war3map.imp').write_bytes(struct.pack('<II',ver,count+len(new))+imp[8:]+b''.join(bytes([13])+p.encode()+b'\0' for p in new))

# Reuse the v7 compiler, editor synchronization and archive verification pipeline.
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):]
tail=tail[:tail.index('# Terrain-derived BLP1 minimaps')]+tail[tail.index('work=Path('):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v8.w3x')
tail=tail.replace('report.update(output=',"report.update(output=").replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','hero_functions=len(selected),')
report={};exec(tail)
