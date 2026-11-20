from pathlib import Path
exec((Path(__file__).resolve().parent/'build.py').read_text())
# Rebuild base first, then apply TF changes in the same validated object model.
import struct
before_tf=s
s=s.replace('TFP_wildCards___OFFSET_ANGLE=30.', 'TFP_wildCards___OFFSET_ANGLE=18.')
s=s.replace('TFP_wildCards___PROJECTILE_SPEED=700.', 'TFP_wildCards___PROJECTILE_SPEED=1400.')
s=s.replace('TFP_wildCards___ENUM_RADIUS=125. / 2.', 'TFP_wildCards___ENUM_RADIUS=32.')
linehit='''function TF45_LineHit takes real x, real y, real ax, real ay, real bx, real by returns boolean
    local real dx=bx-ax
    local real dy=by-ay
    local real t=0.
    if dx*dx+dy*dy>0. then
        set t=RMaxBJ(0.,RMinBJ(1.,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
    endif
    set dx=x-ax-t*dx
    set dy=y-ay-t*dy
    return dx*dx+dy*dy<=TFP_wildCards___ENUM_RADIUS*TFP_wildCards___ENUM_RADIUS
endfunction'''
f=functions(s)['TFP_wildCards___p'].replace('        local real uX','        local real oldX\n        local real oldY\n        local real uX')
anchor='                set uX=GetUnitX('
f=f.replace(anchor,'                set oldX=GetUnitX(TFP_s___wildCards___cardDat_cards[TFP_s__wildCards___cardDat_cards[tempDat]+tripleLooper])\n                set oldY=GetUnitY(TFP_s___wildCards___cardDat_cards[TFP_s__wildCards___cardDat_cards[tempDat]+tripleLooper])\n'+anchor)
f=f.replace('TFP_wildCards___grp, uX, uY, TFP_wildCards___ENUM_RADIUS, null','TFP_wildCards___grp, (oldX+uX)*.5, (oldY+uY)*.5, TFP_wildCards___ENUM_RADIUS+TFP_wildCards___PROJECTILE_SPEED*TFP_tfConsts_FPS*.5, null')
f=f.replace('if IsUnitEnemy(FoG,','if TF45_LineHit(GetUnitX(FoG),GetUnitY(FoG),oldX,oldY,uX,uY) and IsUnitEnemy(FoG,')
replace('TFP_wildCards___p',linehit+'\n\n'+f)
for name in ['TFP_wildCards___setCardRandHue','TF33_Cast']:
 f=functions(s)[name].replace('1.5,1.5,1.5','0.85,0.85,0.85').replace('1.5, 1.5, 1.5','0.85, 0.85, 0.85')
 if name=='TF33_Cast':
  f=f.replace('            call TF33_Tint(orb,color)', '            call TF33_Tint(orb,color)\n            call SaveEffectHandle(TF33_H,GetHandleId(t),6,AddSpecialEffectTarget("Abilities\\\\Spells\\\\Undead\\\\DeathCoil\\\\DeathCoilMissile.mdl",orb,"origin"))\n            call BlzSetSpecialEffectScale(LoadEffectHandle(TF33_H,GetHandleId(t),6),.25)')
 replace(name,f)
f=functions(s)['TF33_Flight'].replace('        call RemoveUnit(orb)','        call DestroyEffect(LoadEffectHandle(TF33_H,h,6))\n        call RemoveUnit(orb)')
f=f.replace('        call SetUnitX(orb,','        call SetUnitFacing(orb,Atan2(dy,dx)*bj_RADTODEG)\n        call SetUnitX(orb,')
replace('TF33_Flight',f)
replace('TF33_SelectTick',functions(s)['TF33_SelectTick'].replace('or ticks>=120','or (not LoadBoolean(TF33_H,h,5) and ticks>=120) or (LoadBoolean(TF33_H,h,5) and ticks>=200)'))
# Replace passive income; track life streak from spawning, before skill learning.
dice=functions((R/'dice.j').read_text())
replace('TF33_IncomeHero', '\n\n'.join(dice[n] for n in ['TF45_Odds','TF45_Track','TF33_IncomeHero','TF45_Enter','TF45_Existing','TF45_Death','TF45_ShareLoss','TF45_Roll','TF45_DiceInit']))
replace('TF33_Init',functions(s)['TF33_Init'].replace('    set t=null','    call TF45_DiceInit()\n    set t=null'))
s=s.replace('hashtable TF33_G=InitHashtable()', 'hashtable TF33_G=InitHashtable()\n    hashtable TF45_Gate=InitHashtable()')
assert 'hashtable TF45_Gate=' in s
replace('TFP_destiny___i',(R/'gate.j').read_text()+'\n'+functions(s)['TFP_destiny___i'].replace('        set t=null','        call TF45_GateInit()\n        set t=null'))

def cardtext(t):
 return t.replace('homing orb','homing card').replace('orbs','cards').replace('orb','card').replace('then six seconds to throw','then ten seconds to throw')
for idx in (a,skin):
 for code in ['ATf1','ATf2','ATf3','ATf4','ATf5','ATf6','ATf7','ATf8']:
  if code in idx:
   for m in idx[code]['mods']:
    if m['id'] in ['aub1','arut','atp1','aret']:m['value']=cardtext(m['value'])
 if 'ATfc' in idx:
  put(idx['ATfc'],'aani','spell',3,0)
  put(idx['ATfc'],'atp1','Gate [|cffffcc00V|r]',3,1)
  put(idx['ATfc'],'aub1','Channel for 2 seconds to teleport. Swirling gateways mark your departure and intended destination before arrival. Range: 5500. One Gate per Destiny.',3,1)
  for k in ['asat','aaea']:put(idx['ATfc'],k,'',3,0)
for n in ['war3map.w3u','war3mapSkin.w3u']:
 idx=index(objects[n])
 if 'htf1' in idx:
  put(idx['htf1'],'umdl','war3mapImported\\TFCard.mdx',3);put(idx['htf1'],'usca',1.,1)
 if 'HTf1' in idx:
  put(idx['HTf1'],'utub','Ranged card master. Wild Cards fires three fast piercing cards. Pick a Card cycles, locks, then throws a homing card. Loaded Dice wagers 50 gold; survival and hero kills improve the odds. Destiny reveals heroes and enables Gate. Cast Z/X/C/V; learn Q/W/E/R.',3)

tip='Roll once every 60 sec. Requires 50 gold: win to gain 50 gold, lose to distribute 50 gold evenly among opposing players with a living, non-illusion hero. If none qualify, the 50 gold is lost. Win chance starts at 50%, gains up to 10 percentage points proportionally over 15 minutes alive, plus 2 points per enemy hero kill (maximum 5 kills / 10 points). Maximum: 70%. Death resets all luck. No mana cost.'
for idx in (a,skin):
 if 'ATfg' not in idx:continue
 e=idx['ATfg'];e['oldId']='ANcl';e['mods']=[m for m in e['mods'] if not m['id'].startswith('Hbh')]
 for k,v,t in [('anam','Loaded Dice',3),('ahky','C',3),('aart','ReplaceableTextures\\CommandButtons\\BTNLoadedDice.blp',3),('arar','ReplaceableTextures\\CommandButtons\\BTNLoadedDice.blp',3),('aret','Learn Loaded Dice [E]',3),('arut',tip,3),('acat','',3),('atat','',3),('aeat','',3),('aani','spell',3)]:put(e,k,v,t,0)
 for lv in range(1,7):
  for k,v,t,p in [('Ncl1',0.,2,1),('Ncl2',0,0,2),('Ncl3',1,0,3),('Ncl4',0.,2,4),('Ncl5',0,0,5),('Ncl6','farsight',3,6),('acdn',60.,1,0),('amcs',0,0,0),('aran',0.,2,0),('atp1',f'Loaded Dice [|cffffcc00C|r] - Level {lv}',3,0),('aub1',tip,3,0)]:put(e,k,v,t,lv,p)
# Runtime research descriptions override object data.
s=re.sub(r'(BlzSetAbilityResearchTooltip\(\'ATfg\', ")[^"]*(", \d\))',lambda m:m[1]+'Learn Loaded Dice [E]'+m[2],s)
s=re.sub(r'(BlzSetAbilityResearchExtendedTooltip\(\'ATfg\', ")[^"]*(", \d\))',lambda m:m[1]+tip+m[2],s)
s='\n'.join(cardtext(line) if 'BlzSetAbilityResearch' in line and "'ATf2'" in line else line for line in s.split('\n'))
(S/'war3map.j').write_text(s,encoding='utf8')
for n,o in objects.items():
 data=objdata.dump(o);validate(data,n.endswith('.w3a'));(S/n).write_bytes(data)
(S/'war3map.wts').write_bytes((S/'war3map.wts').read_bytes().replace(b'Consolidated Mundo Polish v45',b'Mundo and Twisted Fate v45a'))
assets=[str(p.relative_to(S)).replace('/', '\\') for folder in ['war3mapImported','ReplaceableTextures'] for p in (S/folder).rglob('*') if p.is_file()]
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h));imp=read_storm(h,'war3map.imp');assert storm.SFileCloseArchive(h)
version,count=struct.unpack_from('<II',imp);data=imp[8:]
for name in assets:
 assert name.encode()+b'\0' not in data
 data+=b'\r'+name.encode()+b'\0'
(S/'war3map.imp').write_bytes(struct.pack('<II',version,count+len(assets))+data)
bf,af=functions(before_tf),functions(s)
report['payloads']+=assets+['war3map.imp'];report['tf_functions']=[n for n in bf if bf[n]!=af[n]];report['tf_added']=sorted(af.keys()-bf.keys())
report['dice']={'cooldown':60,'minimum_gold':50,'win':50,'loss':-50,'base_percent':50,'alive_cap_seconds':900,'alive_bonus_percent':10,'kill_bonus_percent':2,'kill_cap':5,'death_resets':True}
(R/'changes.json').write_text(json.dumps(report,indent=2));print('TF patch applied:',len(assets),'assets; Loaded Dice active C.')


