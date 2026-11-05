"""Incremental, asserted refinements shared by all three current maps."""
import re
def patch(s):
 def edit(name,old,new):
  nonlocal s
  f=re.search(r'^function '+name+r'\b.*?^endfunction',s,re.M|re.S)[0]
  assert old in f,(name,old)
  s=s.replace(f,f.replace(old,new),1)
 def replace(name,body):
  nonlocal s
  s,n=re.subn(r'^function '+name+r'\b.*?^endfunction',lambda m:body,s,flags=re.M|re.S);assert n==1
 edit('GFW_Create','), 0.675)', '), 0.70875)')
 edit('GFW_Create','p, 72.0, PATHING_TYPE_ANY','p, 75.6, PATHING_TYPE_ANY')
 edit('GFW_Create','call BlzSetSpecialEffectTimeScale', 'call BlzSetSpecialEffectColor(LoadEffectHandle(udg_Guardian_FF_Hash, instance, segment), 55, 105, 255)\n        call BlzSetSpecialEffectAlpha(LoadEffectHandle(udg_Guardian_FF_Hash, instance, segment), 255)\n        call BlzSetSpecialEffectTimeScale')
 edit('Trig_Guardian_Force_Field_Loop_Actions','72.0, PATHING_TYPE_ANY','75.6, PATHING_TYPE_ANY')
 s=s.replace('set udg_hero_turnrate[93]=0.6','set udg_hero_turnrate[93]=1.0')
 # A one-shot reapplication occurs after the engine completes its instant Channel order.
 # Never overwrite a new movement/attack order, pause a unit, or modify attack speed.
 animation='''function FS_DrinkDeferred takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer key = GetHandleId(t)
    local unit u = LoadUnitHandle(FS_Hash, key, 30)
    local integer order = GetUnitCurrentOrder(u)
    if FS_Alive(u) and not IsUnitPaused(u) and (order == 0 or order == OrderId("roar")) then
        call SetUnitAnimationByIndex(u, 12)
        call QueueUnitAnimation(u, "stand")
    endif
    call FlushChildHashtable(FS_Hash, key)
    call DestroyTimer(t)
    set u = null
    set t = null
endfunction

function FS_DrinkAnimation takes unit u returns nothing
    local timer t = CreateTimer()
    call SaveUnitHandle(FS_Hash, GetHandleId(t), 30, u)
    call TimerStart(t, 0.03125, false, function FS_DrinkDeferred)
    set t = null
endfunction

function FS_OnChannel takes nothing returns nothing
    if GetSpellAbilityId() == FS_W and GetUnitTypeId(GetTriggerUnit()) == 'HGr1' then
        call SetUnitAnimationByIndex(GetTriggerUnit(), 12)
    endif
endfunction

'''
 s=s.replace('function FS_OnCast takes',animation+'function FS_OnCast takes',1)
 edit('FS_OnCast','            call SetUnitAnimationByIndex(u, 12)\n            call QueueUnitAnimation(u, "stand")','            call FS_DrinkAnimation(u)')
 edit('FS_Init','    local trigger death = CreateTrigger()','    local trigger death = CreateTrigger()\n    local trigger channel = CreateTrigger()')
 edit('FS_Init','    set cast = null','    call TriggerRegisterAnyUnitEventBJ(channel, EVENT_PLAYER_UNIT_SPELL_CHANNEL)\n    call TriggerAddAction(channel, function FS_OnChannel)\n    set channel = null\n    set cast = null')
 f=re.search(r'^function OM_AttackRadius\b.*?^endfunction',s,re.M|re.S)[0]
 s=s.replace(f,re.sub(r'return ([\d.]+)',lambda m:'return '+format(float(m[1])*1.25,'.8g'),f),1)
 edit('OM_OnCast','* 0.4235','* 0.529375')
 edit('OM_Tick','600.0 * OM_TICK','750.0 * OM_TICK')
 # Ground material itself carries a wide feathered wavefront, with no opaque circle mesh.
 edit('OM_StartPulse','AttackRing.mdx','AttackGround.mdx')
 edit('OM_StartPulse','    call OM_CommandGround(2, x, y, OM_AttackRadius(level) * 0.96, 0.0)\n','')
 edit('OM_PulseTick','    call BlzSetSpecialEffectScale(fx, radius)','    call BlzSetSpecialEffectScale(fx, radius)\n    call BlzSetSpecialEffectAlpha(fx, R2I(230.0 - 70.0 * RMinBJ(1.0, elapsed / 0.25)))')
 edit('OM_ArrivalFX','OM_HASTE_RADIUS * 0.96','OM_HASTE_RADIUS')
 # Keep healing feedback, remove the old fixed ProtectRing completely.
 f=re.search(r'^function OM_ArrivalFX\b.*?^endfunction',s,re.M|re.S)[0]
 f2=re.sub(r'        set ground = Location.*?        call OM_KeepEffect\(fx, 1.5\)\n','',f,flags=re.S)
 f2=f2.replace('        call RemoveLocation(ground)\n','');s=s.replace(f,f2,1)
 edit('OM_CommandGroundTick','size * (0.94 + 0.06 * Sin(elapsed * 6.0))','size * RMinBJ(1.0, elapsed / 0.50)')
 edit('OM_CommandGroundTick','        set fade = RMinBJ(1.0, fade * 2.0)','        set fade = RMinBJ(1.0, RMaxBJ(0.0, (duration - elapsed) / 0.65))')
 edit('OM_CommandGround','    if kind == 2 or kind == 4 then','    if kind == 2 or kind == 3 or kind == 4 then')
 edit('OM_WindupFX','ShockwaveRing.mdx','ShockGround.mdx')
 edit('OM_UpdateShockGround','    if fx != null then','    local effect outer = LoadEffectHandle(OM_Hash, GetHandleId(OM_Ball[i]), -101)\n    if outer != null then\n        call BlzSetSpecialEffectScale(outer, OM_ShockRadius[i] * (0.25 + 0.75 * progress))\n        call BlzSetSpecialEffectAlpha(outer, R2I(110.0 * (1.0 - 0.55 * progress)))\n    endif\n    set outer = null\n    if fx != null then')
 # Impact gets a single expanding, soft-edged wave; retain its lightning/frost accents.
 f=re.search(r'^function OM_GroundRing\b.*?^endfunction',s,re.M|re.S)[0]
 f2=re.sub(r'    if ultimate then.*?    call OM_KeepEffect\(fx, 1.5\)\n','',f,flags=re.S)
 s=s.replace(f,f2,1)
 # Update only affected tooltip numbers; gameplay and object data use the same radii.
 f=re.search(r'^function FF_HeroTooltips_Init\b.*?^endfunction',s,re.M|re.S)[0]
 def tooltipline(m):
  line=m[0]
  if "'AOz2'" in line or "'AOz4'" in line:
   line=re.sub(r'(?i)(radius: )(\d+(?:\.\d+)?)',lambda q:q[1]+format(float(q[2])*1.25,'.8g'),line)
  return line
 s=s.replace(f,re.sub(r'^.*$',tooltipline,f,flags=re.M),1)
 return s

def objects(data):
 for table in data['tables']:
  for e in table:
   uid=e['newId']
   if uid=='HGr1':
    e['mods']=[m for m in e['mods'] if m['id'] not in ['umvr','uori']]
    e['mods'] += [dict(id='umvr',type=2,value=1.0,end=b'HGr1'.hex()),dict(id='uori',type=0,value=0,end=b'HGr1'.hex())]
   if uid=='AGr2':
    e['mods']=[m for m in e['mods'] if m['id']!='aani']
    e['mods'].append(dict(id='aani',type=3,level=0,ptr=0,value='spell,drink',end=b'AGr2'.hex()))
   if uid in ['AOz2','AOz4']:
    for m in e['mods']:
     if m['id']=='aare':m['value']*=1.25
     if m['id'] in ['aub1','arut']:
      m['value']=re.sub(r'(?i)(radius: )(\d+(?:\.\d+)?)',lambda q:q[1]+format(float(q[2])*1.25,'.8g'),m['value'])
 return data
