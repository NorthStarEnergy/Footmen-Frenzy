from pathlib import Path
import sys, re, json, hashlib, subprocess, shutil, copy, struct
O=Path(__file__).resolve().parent; P=O.parents[1]; B=O/'baseline'; E=O/'edited'; E.mkdir(exist_ok=True)
SRC=Path(r'C:\Users\Ryan1\Transfer\FF799X_Rx_Pub_XP_v67.w3x'); OUT=O/'FF799X_Rx_Veigar_Classic_v68.w3x'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=(O/'baseline.sha256').read_text().strip(); assert sha(SRC)==expected
sys.path.insert(0,str(P/'tools'));import objdata_fieldmerge as obj
MPQ=P/'tools/external/mpqcli-bin/mpqcli.exe'
def run(args,log):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,encoding='utf8',errors='replace');(O/log).write_text(r.stdout+r.stderr,encoding='utf8');assert r.returncode==0,(log,(r.stdout+r.stderr)[-1800:]);return r.stdout
def tool(n,*a):return run([next((P/'tools'/n/'bin/Release').glob('*/'+n+'.exe')),*a],n+'.log')
def put(e,k,v,level=0,pointer=0,typ=None):
 typ=typ if typ is not None else (3 if isinstance(v,str) else 0 if isinstance(v,int) else 1)
 found=[m for m in e.mods() if m.modid==k and m.level==level]
 if found:found[0].value=v;found[0].vartype=typ
 else:e.sets[0][1].append(obj.Mod(k,typ,level,pointer,v,e.newid.encode('latin1')))
def entry(t,k):return next(e for tab in t for e in tab if e.key()==k)
icons={k:'ReplaceableTextures\\CommandButtons\\BTNVeigar'+k+'.blp' for k in ['Q','W','E','R','Hero']}
v,t,l=obj.parse(str(B/'war3map.w3u'));assert obj.roundtrip_ok(str(B/'war3map.w3u'))
hero=entry(t,'HVg1')
for k,a in dict(unam='Veigar',upro='The Tiny Master of Evil',utip='Summon Veigar',utpr='Revive Veigar',uawt='Revive Veigar',uhab='AVgq,AVgw,AVge,AVgr',uabi='AInv,AVgp',ustr=15,ustp=1.5,uagi=16,uagp=1.5,uint=20,uinp=3.0,upra='INT',uhpm=100,uhpr=0.25,umpm=150,umpi=150,umpr=1.0,umvs=270,umdl='units\\undead\\HeroLich\\HeroLich.mdl',usca=0.8,ussc=0.8,uico=icons['Hero'],ussi=icons['Hero'],usnd='HeroLich',ua1b=0,ua1d=2,ua1s=4,ua1c=2.1,ua1r=600,ua1t='hero',ua1w='missile',udef=0,ugol=0,ulum=0,ufor=0,ureq='',urqc=0,urq1='',urq2='',usst=0,usrg=3600,usma=3,ubba=250,ubpx=3,ubpy=1,ucpt=0.25,ucbs=0.35).items():put(hero,k,a)
put(hero,'utub','|cff808080Category:|r Hero Killer|n|nA slow, fragile Intelligence mage. Baleful Strike farms permanent Intelligence; Event Horizon catches enemies for Dark Matter. Primordial Burst punishes high-Intelligence heroes.|n|nSTR 15 +1.5/lvl | AGI 16 +1.5/lvl | INT 20 +3/lvl|nMovement: 270. Low base health. Equilibrium restores up to 2 extra mana/sec as mana falls.')
(E/'war3map.w3u').write_bytes(obj.serialise(v,t,l))
v,t,l=obj.parse(str(B/'war3map.w3a'));assert obj.roundtrip_ok(str(B/'war3map.w3a'))
template=copy.deepcopy(entry(t,'AVgw'))
for raw in ['AVgq','AVgr','AVgp']:
 assert not any(e.key()==raw for tab in t for e in tab)
 e=copy.deepcopy(template);e.newid=raw
 for m in e.mods():m.endtoken=raw.encode()
 t[1].append(e)
specs={
 'AVgq':('Baleful Strike','Q',6,0,'thunderbolt',1,[7,7,6.5,6,5.5,5],[60,65,70,75,80,90]),
 'AVgw':('Dark Matter','W',6,1,'flamestrike',2,[12,12,11.5,11,10.5,10],[80,90,100,110,125,140]),
 'AVge':('Event Horizon','E',6,2,'cloudoffog',2,[22,21,20,19,18,17],[80,85,90,95,100,110]),
 'AVgr':('Primordial Burst','R',3,3,'fingerofdeath',1,[100,85,70],[150,200,250])}
tooltips={}
for raw,(name,key,ranks,x,order,target,cd,mana) in specs.items():
 e=entry(t,raw);e.sets[0][1][:]=[m for m in e.mods() if m.level==0]
 for k,a in dict(anam=name,ahky=key,arhk=key,aart=icons[key],arar=icons[key],alev=ranks,aher=1,aite=0,abpx=x,abpy=2,arpx=x,arpy=0,alsk=5 if key=='R' else 3,arlv=6 if key=='R' else 1,areq='',aret='Learn '+name+' [|cffffcc00'+key+'|r]').items():put(e,k,a)
 descriptions=[]
 for rank in range(1,ranks+1):
  if key=='Q':desc=f'Targeted bolt: {80+70*rank} + 0.6 x Intelligence magic damage. Last hits grant +1 permanent Intelligence. While learned, enemy hero kills by Veigar grant +{rank} Intelligence (stacks with the last-hit bonus). Illusions, summoned units and buildings grant none.'
  elif key=='W':desc=f'After 1.25 seconds, a dark meteor deals {100+90*rank} + 1.0 x Intelligence magic damage in a 225 radius. Damage snapshots when cast.'
  elif key=='E':desc=f'Instantly creates a pentagonal cage for 3 seconds, 300 radius to its corners. Touching or crossing an edge stuns for {1.25+0.25*rank:g} seconds, once per cage. Units inside can move freely. Deals no damage.'
  else:desc=f'Blasts an enemy hero for {250+300*rank} + 1.2 x your Intelligence + 0.8 x target Intelligence magic damage. Classic anti-mage burst; damage does not depend on missing health.'
  desc+=f'|n|nExcludes buildings and magic-immune targets.|nMana: {mana[rank-1]} | Cooldown: {cd[rank-1]:g} sec | Range: {650 if key=="R" else 700 if key=="Q" else 900}.'
  descriptions.append(desc)
  vals=dict(atp1=f'{name} [|cffffcc00{key}|r] - Rank {rank}',aub1=desc,amcs=mana[rank-1],acdn=float(cd[rank-1]),aran=float(650 if key=='R' else 700 if key=='Q' else 900),aare=float(300 if key=='E' else 225 if key=='W' else 0),adur=0.0,ahdu=0.0,atar='air,ground,enemy,hero,vulnerable' if key=='R' else 'air,ground,enemy,vulnerable' if key=='Q' else '',Ncl1=0.0,Ncl2=target,Ncl3=1,Ncl4=0.0,Ncl5=0,Ncl6=order)
  for k,a in vals.items():put(e,k,a,rank,int(k[-1]) if k.startswith('Ncl') else 0)
 put(e,'arut','|n|n'.join(f'|cffffcc00Rank {i+1}|r: '+d for i,d in enumerate(descriptions)))
 tooltips[raw]=descriptions
# Actual passive icon uses a zero-bonus native attribute ability, not a clickable Channel.
p=entry(t,'AVgp');p.oldid='Aamk';p.sets[0][1][:]=[]
for k,a in dict(anam='Equilibrium',aher=0,alev=1,aart='ReplaceableTextures\\PassiveButtons\\PASVeigarHero.blp',abpx=0,abpy=1,areq='').items():put(p,k,a)
for k,a in dict(atp1='Equilibrium',aub1='Restores extra mana each second based on missing mana: +1 mana/sec at 50% missing, up to +2 mana/sec when empty. Always active while alive. This Warcraft adaptation adds to normal regeneration.',Istr=0,Iagi=0,Iint=0).items():put(p,k,a,1)
stun=entry(t,'AVgs');put(stun,'alev',6)
original=[copy.deepcopy(m) for m in stun.mods() if m.level==1]
for rank in range(1,7):
 for m in original:put(stun,m.modid,m.value,rank,m.pointer,m.vartype)
 put(stun,'adur',1.25+0.25*rank,rank);put(stun,'ahdu',1.25+0.25*rank,rank)
(E/'war3map.w3a').write_bytes(obj.serialise(v,t,l));(O/'tooltips.json').write_text(json.dumps(tooltips,indent=2))
s=(B/'war3map.j').read_text(encoding='utf-8-sig');original=s
def replace(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
replace('    set udg_total_hero_count=96',"    set udg_hero_type[97]='HVg1'\n    set udg_total_hero_count=97")
stats='\n'.join(f'    set udg_hero_{k}[97]={a}' for k,a in dict(category=6,STR_base=15,STR_inc=1.5,AGI_base=16,AGI_inc=1.5,INT_base=20,INT_inc=3.0,move_base=270,turnrate=0.6).items())
replace('    set udg_hero_turnrate[96]=0.6','    set udg_hero_turnrate[96]=0.6\n'+stats)
needle="    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'HTf1', GetRectCenterX(gg_rct_EXILE) + 192.0, GetRectCenterY(gg_rct_EXILE), 270.0)"
replace(needle,needle+"\n    call CreateUnit(Player(PLAYER_NEUTRAL_PASSIVE), 'HVg1', GetRectCenterX(gg_rct_EXILE) + 320.0, GetRectCenterY(gg_rct_EXILE), 270.0)")
replace("                call UnitAddAbility(dummy, 'AVgs')","                call UnitAddAbility(dummy, 'AVgs')\n                call SetUnitAbilityLevel(dummy, 'AVgs', LoadInteger(VG_Hash, h, 11))")
replace('call UnitDamageTarget(caster, u, 300.0, false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)','call UnitDamageTarget(caster, u, LoadReal(VG_Hash, h, 10), false, false, ATTACK_TYPE_NORMAL, DAMAGE_TYPE_MAGIC, WEAPON_TYPE_WHOKNOWS)')
replace('    call SaveReal(VG_Hash, h, 3, 0.0)','    call SaveReal(VG_Hash, h, 3, 0.0)\n    call SaveReal(VG_Hash, h, 10, 100.0 + 90.0 * GetUnitAbilityLevel(GetTriggerUnit(), \'AVgw\') + GetHeroInt(GetTriggerUnit(), true))\n    call SaveInteger(VG_Hash, h, 11, GetUnitAbilityLevel(GetTriggerUnit(), \'AVge\'))')
replace('function VG_Init takes nothing returns nothing',(O/'classic.j').read_text()+'\nfunction VG_Init takes nothing returns nothing')
replace('    local trigger cast = CreateTrigger()\n    local trigger chat = CreateTrigger()','    local trigger cast = CreateTrigger()\n    local trigger chat = CreateTrigger()\n    local trigger kills = CreateTrigger()')
replace('    call TriggerAddAction(cast, function VG_Cast)','    call TriggerAddAction(cast, function VG_Cast)\n    call TriggerAddAction(cast, function VG_ClassicCast)\n    call TriggerRegisterAnyUnitEventBJ(kills, EVENT_PLAYER_UNIT_DEATH)\n    call TriggerAddAction(kills, function VG_ClassicKill)\n    call TimerStart(CreateTimer(), 1.0, true, function VG_Equilibrium)\n    set kills = null')
# Preserve chat access but use the normal debug recruit path, avoiding a second free hero in public games.
a=s.index('function VG_Summon takes');z=s.index('\nendfunction',a)+len('\nendfunction')
s=s[:a]+'''function VG_Summon takes nothing returns nothing
    local player p = GetTriggerPlayer()
    local integer id = GetPlayerId(p)
    local unit u = udg_herO[id + 1]
    if GetUnitTypeId(u) == 'HVg1' then
        call SelectUnitForPlayerSingle(u, p)
    elseif udg_mode_debugmode then
        set u = VG_Hero[id]
        if GetUnitTypeId(u) == 0 then
            set u = CreateUnit(p, 'HVg1', GetStartLocationX(GetPlayerStartLocation(p)), GetStartLocationY(GetPlayerStartLocation(p)), 270.0)
            set VG_Hero[id] = u
            call FF_TestExtraHero(u)
        elseif GetWidgetLife(u) <= 0.405 then
            call ReviveHero(u, GetStartLocationX(GetPlayerStartLocation(p)), GetStartLocationY(GetPlayerStartLocation(p)), true)
        endif
        call SelectUnitForPlayerSingle(u, p)
        call DisplayTimedTextToPlayer(p, 0.0, 0.0, 12.0, "Veigar: learn Q/W/E/R using hero skill points. Equilibrium is always active.")
    else
        call DisplayTimedTextToPlayer(p, 0.0, 0.0, 12.0, "Veigar is in the Hero Killer selection pool. In Debug, recruit him from All Heroes.")
    endif
    set p = null
    set u = null
endfunction'''+s[z:]
(E/'war3map.j').write_text(s,encoding='utf8')
misc=(B/'war3mapMisc.txt').read_text();misc=misc.replace('HMu1,HTf1','HMu1,HTf1,HVg1');assert misc!=(B/'war3mapMisc.txt').read_text();(E/'war3mapMisc.txt').write_text(misc)
shutil.copyfile(B/'war3map.imp',E/'war3map.imp')
run([sys.executable,P/'tools/prepare_editor_runtime.py',E,O/'recovered-source'],'recover-source.log')
notes='v68: Classic Veigar complete. User stats STR/AGI/INT 15/16/20, gains 1.5/1.5/3. Hero Killer roster 97; Lich model; Q last-hit INT, W scaled meteor, E ranked stun, R target-INT burst, Equilibrium. Custom bordered BLP icons. Static-validated candidate; engine playtest pending.'
(O/'maintenance.txt').write_text(notes)
tool('EditorSourceSync','write',B/'war3map.wtg',B/'war3map.wct',O/'recovered-source/globals.j',O/'recovered-source/FF_Runtime.j',O/'maintenance.txt',E)
(E/'FF_MAINTENANCE.md').write_text((B/'FF_MAINTENANCE.md').read_text(encoding='utf-8-sig')+'\n\n'+notes,encoding='utf8')
manifest=json.loads((O/'recovered-source/FF_SOURCE_MANIFEST.json').read_text());manifest.pop('baseline_checks',None);manifest.update(source_map_sha256=expected,revision='v68 classic Veigar',engine_playtest=False);(E/'FF_SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
wts=(B/'war3map.wts').read_bytes();wts,n=re.subn(rb'(STRING 1\s*\{\s*)[^\r\n]+',lambda m:m[1]+b'Footmen Frenzy 799X Veigar Classic v68',wts,count=1);assert n==1;(E/'war3map.wts').write_bytes(wts)
# Deterministic asset-format conversion and border compositing, using generated artwork.
exec((O/'icons.py').read_text(),globals())
assets=[str(f.relative_to(E)) for f in E.rglob('*.blp')]
imp=(B/'war3map.imp').read_bytes();ver,count=struct.unpack_from('<II',imp);(E/'war3map.imp').write_bytes(struct.pack('<II',ver,count+len(assets))+imp[8:]+b''.join(b'\r'+p.encode()+b'\0' for p in assets))
tool('JassCheck',E/'war3map.j')
J=Path(r'C:\Users\Ryan1\Documents\Warcraft III\JassHelper');compiler=Path(r'C:\Program Files\Warcraft III\_retail_\x86_64\JassHelper\pjass.exe')
run([compiler,J/'common.j',J/'Blizzard.j',E/'war3map.j'],'pjass.log')
run([compiler,J/'common.j',J/'Blizzard.j',O/'recovered-source/editor_regeneration_input.j'],'editor-pjass.log')
members=[str(f.relative_to(E)) for f in E.rglob('*') if f.is_file()]
shutil.copy2(SRC,OUT)
for i,n in enumerate(members):run([MPQ,'add',OUT,E/n,'-p',n,'-w'],'pack-last.log')
V=O/'verified';V.mkdir(exist_ok=True)
for n in members:
 run([MPQ,'extract',OUT,'-o',V,'-f',n,'-k'],'extract-last.log');assert (E/n).read_bytes()==(V/n).read_bytes(),n
tool('EditorSourceSync','export',V/'war3map.wtg',V/'war3map.wct',O/'verified-source')
run([sys.executable,P/'tools/check_editor_runtime.py','--globals',O/'verified-source/globals.j','--runtime',O/'verified-source/FF_Runtime.j','--script',V/'war3map.j','--report',O/'source-verification.json'],'source-check.log')
assert sha(SRC)==expected
from check_editor_runtime import parse_source
a=parse_source(original);b=parse_source(s)
(O/'verification.json').write_text(json.dumps(dict(passed=True,source_sha256=expected,output_sha256=sha(OUT),changed_members=members,changed_functions=[n for n in a.functions if a.functions[n]!=b.functions[n]],new_functions=sorted(set(b.functions)-set(a.functions)),engine_tested=False),indent=2))
print(OUT)

