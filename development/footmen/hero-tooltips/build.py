"""Compact, rank-specific tooltips for Guardian, Orianna and Gragus in 799X."""
from pathlib import Path
import sys,shutil,re,json,hashlib
R=Path(__file__).resolve().parent;W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,functions
import objdata
base=R/'base.w3x';source=W/'799x-backport/release/FF799X_Rx_GuardianLantern_v30.w3x'
if not base.exists():shutil.copy2(source,base)
O=R/'src';O.mkdir(exist_ok=True);(R/'audit').mkdir(exist_ok=True)
h=c.c_void_p();assert storm.SFileOpenArchive(str(base),0,0x100,c.byref(h))
for name in ['war3map.j','war3map.w3a','war3map.w3u','war3mapSkin.w3u','war3map.wts']:(O/name).write_bytes(read_storm(h,name))
assert storm.SFileCloseArchive(h)
original=(O/'war3map.j').read_text(encoding='utf-8-sig');s=original
d=objdata.load(str(O/'war3map.w3a'));es={e['newId']:e for t in d['tables'] for e in t}
gold=lambda label:'|cffffcc00'+label+'|r'
cyan=lambda value:'|cff80dfff'+str(value)+'|r'
green=lambda value:'|cff80ff80'+str(value)+'|r'
def fmt(n):return format(n,'.4f').rstrip('0').rstrip('.') if isinstance(n,float) else str(n)
def prop(e,k,level=0):return next(m['value'] for m in e['mods'] if m['id']==k and m['level']==level)
def line(label,value):return gold(label+':')+' '+str(value)
def stats(e,rank):
 mana=prop(e,'amcs',rank);cd=prop(e,'acdn',rank)
 return line('Mana',cyan(fmt(mana)))+'   '+line('Cooldown',cyan(fmt(cd)+' sec'))
def field(e,k,v,level=0):
 e['mods']=[m for m in e['mods'] if (m['id'],m['level'])!=(k,level)]
 e['mods'].append(dict(id=k,type=3,level=level,ptr=0,value=v,end=e['newId'].encode().hex()))
move=[60,90,120,160,200,225];pulse=[75,100,125,185,225,500]
attackradius=[259.875,281.53125,303.1875,346.5,389.8125,433.125]
protectdamage=[30,50,75,100,125,150];protectheal=[100,150,200,250,300,400]
barreldamage=[80,120,180,240,300,550];slamdamage=[75,100,125,175,200,225]
duration=[3,3,3.5,4,5,5];expiry=[.5,.7,1,1.25,1.5,1.75]
texts={};research={};titles={}
ids=['A0DL','AFg1','ATfd','AZd1','AOz1','AOz2','AOz3','AOz4','AGr1','AGr2','AGr3','AGr4']
for uid in ids:
 e=es[uid];ranks=prop(e,'alev');name=prop(e,'anam');hotkey=prop(e,'ahky');learnkey=prop(e,'arhk')
 for rank in range(1,ranks+1):
  k=rank-1
  if uid=='A0DL':
   body='Fire an orb that marks and damages enemies. Marked enemies are stunned when it bursts.'
   details=[line('Damage',cyan(30+10*k)+' magic'),line('Stun',cyan(fmt(.5+.25*k)+' sec')),line('Travel',cyan(str(700+100*k))),line('Radius',cyan(280))]
  elif uid=='AFg1':
   body='Place up to '+cyan(5)+' barriers in 4 seconds. Each blocks movement and stuns nearby enemies on expiry.'
   details=[line('Field duration',cyan(fmt(float(duration[k]))+' sec')),line('Expiry stun',cyan(fmt(float(expiry[k]))+' sec')),line('Cost',cyan('25 mana per field')),line('Recovery',cyan('30 sec after burst'))]
  elif uid=='ATfd':
   body='Throw a lantern that shields nearby allied heroes and pulls one allied hero to you safely.'
   details=[line('Shield',green(str(100+40*k))+' for 4 sec'),line('Lantern',cyan(str(6+k)+' sec')),
    gold('Guardian:')+' Enemies entering the lantern and heroes crossed by a passenger are stunned '+cyan('0.5 sec')+'.',
    gold('Chain:')+' Other allies heal '+green('10 + 20/sec')+' and are slowed '+cyan('20% for 1 sec')+' on entry.']
  elif uid=='AZd1':
   body='Toggle a moving dome. It restores allies and slows and burns enemies.'
   details=[line('Allies',green('100 HP + 10 mana/sec')),line('Enemies',cyan('60% slow; up to 20 mana burn/sec')+' and equal magic damage'),
    line('Bolts',green(str(25+5*k)+' heal')+' / '+cyan(str(25+5*k)+' damage')+' every 0.75 sec, plus mana and brief speed effects'),
    line('Ramp',cyan('+5% power/sec, up to 2x')),
    line('Drain',cyan('30 mana/sec, +5/sec over time (max 130)')),line('Radius',cyan(600)),
    'Stops at 5 mana. Cooldown starts when turned off.']
  elif uid=='AOz1':
   body='Send the ball to a point, damaging and slowing enemies it crosses.'
   details=[line('Damage',cyan(move[k])+' magic'),line('Slow',cyan('25% for 2 sec')),line('Cast range',cyan(1000))]
  elif uid=='AOz2':
   body='The ball emits a fast pulse that damages and slows enemies.'
   details=[line('Damage',cyan(pulse[k])+' magic'),line('Radius',cyan('~'+str(round(attackradius[k])))),line('Slow',cyan('25% for 2 sec'))]
  elif uid=='AOz3':
   body='Send the ball to an ally. It damages enemies on the way and heals allies on arrival.'
   details=[line('Travel damage',cyan(protectdamage[k])+' magic and '+cyan('25% slow for 2 sec')),line('Arrival heal',green(protectheal[k])+' in 200 radius'),line('Speed',green('+10%')+' for 5 sec on target; 2 sec on nearby allies'),line('Cast range',cyan(1000))]
  elif uid=='AOz4':
   body='After a short windup, pull nearby ground enemies toward the ball.'
   details=[line('Damage',cyan([200,275,400][k])+' magic'),line('Radius',cyan('~'+str(round([264.6875,317.625,370.5625][k])))),line('Windup',cyan('0.5 sec'))]
  elif uid=='AGr1':
   body='Roll a barrel to a point. Press '+gold('Z')+' again to detonate it early.'
   details=[line('Damage',cyan(barreldamage[k])+' magic'),line('Radius',cyan(260)),line('Slow',cyan('25% for 2 sec')),'Explodes 2 seconds after arrival if left alone.']
  elif uid=='AGr2':
   body='Drink to fortify yourself for '+cyan('5 sec')+'.'
   details=[line('Armor',green('+'+str(5+2*k))),line('Magic reduction',green(str(10+5*k)+'%')),line('Healing',green(str(20+10*k)+' HP/sec'))]
  elif uid=='AGr3':
   body='Charge forward, damaging and stunning ground enemies on impact.'
   details=[line('Damage',cyan(slamdamage[k])+' magic'),line('Stun',cyan('0.6 sec')),line('Impact radius',cyan(220)),line('Charge range',cyan(600)),'Blocked terrain stops the charge.']
  else:
   body='Throw an explosive cask that damages, stuns and knocks back ground enemies.'
   details=[line('Damage',cyan([200,300,400][k])+' magic'),line('Stun',cyan('0.6 sec')),line('Radius',cyan(430)),line('Knockback',cyan('up to 400'))]
  costs=stats(e,rank) if uid not in ['AFg1','AZd1'] else (line('Cooldown',cyan('5 sec after shutdown')) if uid=='AZd1' else '')
  text=body+'|n|n'+'|n'.join(details)+(('|n|n'+costs) if costs else '')
  required=prop(e,'arlv')+(rank-1)*prop(e,'alsk')
  learn=gold('Requires hero level '+str(required))+'|n|n'+text
  title=name+' ['+gold(hotkey)+'] - Level '+str(rank)
  learn_title='Learn '+name+' ['+gold(learnkey)+'] - Level '+str(rank)
  texts[uid,rank]=text;research[uid,rank]=learn;titles[uid,rank]=(title,learn_title)
  field(e,'aub1',text,rank);field(e,'atp1',title,rank)
 field(e,'arut',research[uid,1]);field(e,'aret',titles[uid,1][1])
# The recast button is a separate ability and has its own help text.
e=es['AGr8'];det='Detonate the active barrel immediately.|n|n'+line('Radius',cyan(260))+'   '+line('Slow',cyan('25% for 2 sec'))
field(e,'aub1',det,1)
(O/'war3map.w3a').write_bytes(objdata.dump(d))
# Research tooltips from OM_Init and TFP_Init override object data; install all
# rank-specific active and research descriptions after those initializers run.
calls=['function FF_CompactHeroTooltips_Init takes nothing returns nothing']
def jstr(v):return '"'+v.replace('\\','\\\\').replace('"','\\"')+'"'
for uid in ids:
 for rank in range(1,prop(es[uid],'alev')+1):
  calls.append("    call BlzSetAbilityExtendedTooltip('"+uid+"', "+jstr(texts[uid,rank])+', '+str(rank-1)+')')
  calls.append("    call BlzSetAbilityTooltip('"+uid+"', "+jstr(titles[uid,rank][0])+', '+str(rank-1)+')')
  calls.append("    call BlzSetAbilityResearchExtendedTooltip('"+uid+"', "+jstr(research[uid,rank])+', '+str(rank-1)+')')
  calls.append("    call BlzSetAbilityResearchTooltip('"+uid+"', "+jstr(titles[uid,rank][1])+', '+str(rank-1)+')')
calls.append("    call BlzSetAbilityExtendedTooltip('AGr8', "+jstr(det)+', 0)')
calls.append('endfunction')
s=s.replace('function InitTrig_FF_Runtime takes','\n'.join(calls)+'\n\nfunction InitTrig_FF_Runtime takes',1)
f=functions(s)['InitTrig_FF_Runtime'];assert '    call TFP_Init()' in f;s=s.replace(f,f.replace('    call TFP_Init()','    call TFP_Init()\n    call FF_CompactHeroTooltips_Init()',1),1)
s=s.replace('FF799X - Guardian Lantern v30','FF799X - Hero Tooltips v31')
(O/'war3map.j').write_text(s,encoding='utf8')
# Hero-selection descriptions are separate from the spell help shown in the command card.
hero_desc={'H043':'Control fights with barriers, a rescue lantern and a protective dome.',
 'HOr1':'Command the ball to damage enemies, heal allies and pull foes together.',
 'HGr1':'Roll explosive barrels, fortify yourself and charge into enemies.'}
for name in ['war3map.w3u','war3mapSkin.w3u']:
 obj=objdata.load(str(O/name));modified=[]
 for t in obj['tables']:
  for e in t:
   if e['newId'] in hero_desc:
    # Only replace existing custom hero text; do not add entries to unrelated skins.
    for mod in e['mods']:
     if mod['id']=='utub':mod['value']=gold('Abilities')+'|n'+hero_desc[e['newId']];modified.append(e['newId'])
 (O/name).write_bytes(objdata.dump(obj))
p=O/'war3map.wts';raw=p.read_bytes();assert b'FF799X - Guardian Lantern v30' in raw;p.write_bytes(raw.replace(b'FF799X - Guardian Lantern v30',b'FF799X - Hero Tooltips v31'))
bf,sf=functions(original),functions(s);changed=[n for n in bf if bf[n]!=sf[n]]
assert changed==['InitTrig_FF_Runtime'],changed
(R/'changes.json').write_text(json.dumps(dict(base=str(base),base_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),changed_functions=changed,added_functions=sorted(sf.keys()-bf.keys()),skills=ids),indent=2))
(R/'audit/tooltip-preview.txt').write_text('\n\n'.join(uid+' rank '+str(rank)+'\n'+v.replace('|n','\n') for (uid,rank),v in texts.items()),encoding='utf8')
print('Prepared',len(texts),'rank-specific active and research descriptions, plus barrel recast and hero selection text.')
