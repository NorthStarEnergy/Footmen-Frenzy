from pathlib import Path
import sys,struct,re,json,ctypes as c,shutil,subprocess,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'ffa-v4/tools'),r'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\six-player-ffa']
from objectio import Obj
import archive
B=R/'base';O=R/'src'
for folder in [B,O,R/'release']:folder.mkdir(parents=True,exist_ok=True)
shutil.copyfile(W/'ffa-v11/release/Solo_Foots_8P_FFA_v11.w3x',R/'baseline.w3x')
archive.extract(R/'baseline.w3x',B)
s=(B/'war3map.j').read_text();pat=r'^[ \t]*function (\w+)\b.*?^[ \t]*endfunction'
def funcs(t):return {m[1]:m[0] for m in re.finditer(pat,t,re.M|re.S)}
def put(n,t):
 global s
 s=s.replace(funcs(s)[n],t)
oldpages=json.loads((W/'ffa-v8/shop-pages.json').read_text())
# Ten stock positions, Next at (2,2), Select Buyer at (3,2).
pages={k:[sum(v,[])[i:i+10] for i in range(0,len(sum(v,[])),10)] for k,v in oldpages.items()}
(R/'shop-pages.json').write_text(json.dumps(pages,indent=2))
objects=Obj(B/'war3map.w3u');skin=Obj(B/'war3mapSkin.w3u')
items=Obj(B/'war3map.w3t');itemskin=Obj(B/'war3mapSkin.w3t')
for token in ['h02U','h037']:
 for table in [objects,skin]:
  for key,val in dict(unam='Next page',utip='Next page',utub='Show the next shop page. The last page returns to the first. Bring a buyer within range to use this shop.',uhot='N',ubpx=2,ubpy=2,uico=r'ReplaceableTextures\CommandButtons\BTNReplay-SpeedUp.blp').items():table.set(token,key,val)
 for key,val in dict(ugol=0,ulum=0,ufoo=0,usst=0,usrg=1,usma=1,ussc=0,ureq='',urqa='',upgr='').items():objects.set(token,key,val)
for family,table,skintable in [('creeps',objects,skin),('recipes',items,itemskin)]:
 for page in pages[family]:
  for index,kind in enumerate(page):
   for t in [table,skintable]:
    t.set(kind,'ubpx',index%4);t.set(kind,'ubpy',index//4)
for table,name in [(objects,'war3map.w3u'),(skin,'war3mapSkin.w3u'),(items,'war3map.w3t'),(itemskin,'war3mapSkin.w3t')]:table.save(O/name)

lines=['function F8_RefreshShop takes unit shop,integer page returns nothing']
for index,(kind,family,token,native) in enumerate([('n00R','creeps','h02U','Unit'),('n01Y','recipes','h037','Item')]):
 lines.append(('    if' if index==0 else '    elseif')+f" GetUnitTypeId(shop)=='{kind}' then")
 lines.append(f"        call RemoveUnitFromStock(shop,'{token}')")
 for id in sum(pages[family],[]):lines.append(f"        call Remove{native}FromStock(shop,'{id}')")
 # Add the navigation control first; never let stock fill its slot.
 lines.append(f"        call AddUnitToStock(shop,'{token}',1,1)")
 for p,stock in enumerate(pages[family]):
  lines.append(('        if' if p==0 else '        elseif')+f' page=={p} then')
  for id in stock:lines.append(f"            call Add{native}ToStock(shop,'{id}',1,1)")
 lines.append('        endif')
lines+=['    endif','    call SaveInteger(F8_Shops,GetHandleId(shop),0,page)','endfunction']
put('F8_RefreshShop','\n'.join(lines))
s+='''
function F8_FinishShopPage takes nothing returns nothing
    local timer t=GetExpiredTimer()
    local integer key=GetHandleId(t)
    local unit shop=LoadUnitHandle(F8_Shops,key,0)
    local player buyer=LoadPlayerHandle(F8_Shops,key,1)
    call F8_RefreshShop(shop,LoadInteger(F8_Shops,GetHandleId(shop),0))
    call SelectUnitForPlayerSingle(shop,buyer)
    call RemoveSavedHandle(F8_Shops,GetHandleId(shop),1)
    call FlushChildHashtable(F8_Shops,key)
    call DestroyTimer(t)
    set t=null
    set shop=null
    set buyer=null
endfunction

function F8_KeepRecipeStock takes nothing returns boolean
    return GetUnitTypeId(GetSellingUnit())!='n01Y'
endfunction

function F8_InitShops takes nothing returns nothing
    local group g=CreateGroup()
    local trigger t=CreateTrigger()
    set F8_Shops=InitHashtable()
    call GroupEnumUnitsInRect(g,GetPlayableMapRect(),null)
    call ForGroup(g,function F8_ShopInitEnum)
    call DestroyGroup(g)
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SELL)
    call TriggerAddAction(t,function F8_ShopSale)
    // Keep Warcraft's marketplace cleanup for other shops, but let recipe stock replenish.
    call TriggerAddCondition(bj_stockItemPurchased,Condition(function F8_KeepRecipeStock))
    set g=null
    set t=null
endfunction
'''
put('F8_ShopSale','''function F8_ShopSale takes nothing returns nothing
    local unit shop=GetSellingUnit()
    local unit sold=GetSoldUnit()
    local player buyer=GetOwningPlayer(sold)
    local integer pages=0
    local integer key=GetHandleId(shop)
    local timer t
    if GetUnitTypeId(shop)=='n00R' and GetUnitTypeId(sold)=='h02U' then
        set pages=3
    elseif GetUnitTypeId(shop)=='n01Y' and GetUnitTypeId(sold)=='h037' then
        set pages=2
    endif
    if pages>0 then
        call SaveInteger(F8_Shops,key,0,ModuloInteger(LoadInteger(F8_Shops,key,0)+1,pages))
        call RemoveUnit(sold)
        // Finish after Warcraft consumes the sold stock, not inside that transaction.
        set t=LoadTimerHandle(F8_Shops,key,1)
        if t==null then
            set t=CreateTimer()
            call SaveTimerHandle(F8_Shops,key,1,t)
            call SaveUnitHandle(F8_Shops,GetHandleId(t),0,shop)
            call TimerStart(t,0.,false,function F8_FinishShopPage)
        endif
        call SavePlayerHandle(F8_Shops,GetHandleId(t),1,buyer)
    endif
    set t=null
    set shop=null
    set sold=null
    set buyer=null
endfunction''')
# Populate before mode choice so selecting a shop at startup never yields an empty card.
f=funcs(s)['F8_Start'];start=f.index('    set F8_Shops=');end=f.index('    loop',start)
f=f[:start]+f[end:];f=f.replace('    local group g=CreateGroup()\n','').replace('    local trigger t=CreateTrigger()\n','').replace('    set g=null\n','').replace('    set t=null\n','');put('F8_Start',f)
put('SF_Initialize',funcs(s)['SF_Initialize'].replace('    set F8_Slot[1]=0','    call F8_InitShops()\n    set F8_Slot[1]=0'))
# The old pub timer must not inject an off-page turtle/troll into a full command card.
put('Trig_Add_Creeps_To_Pub_Mode_Actions','''function Trig_Add_Creeps_To_Pub_Mode_Actions takes nothing returns nothing
    // Turtle and troll are already included in the paged creep pool.
endfunction''')
# Navigation tokens are controls, not purchases subject to creep limits/bounties.
put('Trig_limit_amount_of_creeps_Actions',funcs(s)['Trig_limit_amount_of_creeps_Actions'].replace('    set udg_temp_unit=GetSoldUnit()',"    if GetUnitTypeId(GetSoldUnit())=='h02U' or GetUnitTypeId(GetSoldUnit())=='h037' or GetUnitTypeId(GetSoldUnit())=='hPgN' then\n        return\n    endif\n    set udg_temp_unit=GetSoldUnit()"))
title='Solo Foots 8P FFA + King v12';s=re.sub(r'call SetMapName\("[^\"]+"\)',f'call SetMapName("{title}")',s)
info=(B/'war3map.w3i').read_bytes();end=info.index(0,28);(O/'war3map.w3i').write_bytes(info[:28]+title.encode()+info[end:])
pipeline=(W/'ffa-v7/build.py').read_text();tail=pipeline[pipeline.index('# Order declarations before their callers'):]
tail=tail[:tail.index('# Terrain-derived BLP1 minimaps')]+tail[tail.index('work=Path('):]
tail=tail.replace('Solo_Foots_8P_FFA_v7.w3x','Solo_Foots_8P_FFA_v12.w3x').replace('hero_functions=len(selected),base_shift=96,tower_widening_each=64,cliff_tip_min_radius=2220,','')
report={'shop_pages':pages,'maximum_purchases_per_page':10};exec(tail)
