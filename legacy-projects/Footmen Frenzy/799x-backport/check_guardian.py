from pathlib import Path
import ast,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'mini-foots/tools'))
import objdata
ROOT=Path(__file__).resolve().parent
s=(ROOT/'src/war3map.j').read_text()
functions={m[1]:m[0] for m in re.finditer(r'(?ms)^function (\w+)\b.*?^endfunction',s)}
tree=ast.parse((ROOT/'check_runtime.py').read_text())
ns=dict(re=re,functions=functions)
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'harness','exec'),ns)
state={};timers={};cooldowns={};now=0.;expired=None;serial=100
GFB_Data={}
def CreateTimer():
 global serial
 serial+=1;return serial
def TimerStart(t,delay,repeat,fn):timers[t]=(now+delay,fn)
def Save(h,k,c,v):h[k,c]=v
def Flush(h,k):
 for key in list(h):
  if key[0]==k:del h[key]
def advance(dt):
 global now,expired
 end=now+dt
 while timers and min(t[0] for t in timers.values())<=end:
  expired=min(timers,key=lambda k:timers[k][0]);now,fn=timers.pop(expired);fn()
 now=end
ns.update(GFB_Data=GFB_Data,CreateTimer=CreateTimer,TimerStart=TimerStart,GetHandleId=lambda x:x,GetExpiredTimer=lambda:expired,LoadUnitHandle=lambda h,k,c:h.get((k,c)),LoadInteger=lambda h,k,c:h.get((k,c),0),LoadTimerHandle=lambda h,k,c:h.get((k,c)),SaveTimerHandle=Save,SaveUnitHandle=Save,SaveInteger=Save,FlushChildHashtable=Flush,DestroyTimer=lambda t:timers.pop(t,None),PauseTimer=lambda t:timers.pop(t,None),BlzStartUnitAbilityCooldown=lambda u,a,d:cooldowns.__setitem__(u,now+d))
for n in ['GFB_End','GFB_Ready','GFB_Cast']:exec(ns['translate'](n).replace('function ', ''),ns)
# Exhaust the burst quickly; no old window timer may reset recovery later.
for i in range(5):
 ns['GFB_Cast'](1);advance(0)
 assert abs(cooldowns[1]-now-(.1 if i<4 else 30.))<1e-6
 advance(.15)
end=cooldowns[1];advance(4);assert cooldowns[1]==end and not timers and not GFB_Data
# Independent caster windows; partial bursts enter recovery when their window ends.
ns['GFB_Cast'](1);advance(1);ns['GFB_Cast'](2);advance(3)
assert abs(cooldowns[1]-now-30)<1e-6
assert GFB_Data[2,0]==4
advance(1);assert abs(cooldowns[2]-now-30)<1e-6 and not GFB_Data
# A later fresh burst gets five casts again.
advance(31);ns['GFB_Cast'](1);advance(0);assert GFB_Data[1,0]==4

def objects(ext):return {e['newId']:e for t in objdata.load(str(ROOT/'src'/('war3map.'+ext)))['tables'] for e in t}
a=objects('w3a');u=objects('w3u')
def val(e,k,l=0):return next(m['value'] for m in e['mods'] if m['id']==k and m.get('level',0)==l)
assert val(u['H043'],'uhab')=='A0DL,AFg1,ATfd,AZd1'
assert val(u['H043'],'uabi')=='AInv'
assert val(a['AZd1'],'arlv')==6 and val(a['AZd1'],'alev')==3
for rank in range(1,7):
 assert val(a['AFg1'],'Ncl6',rank)=='forceofnature'
 assert val(a['AFg1'],'Ncl6',rank)!=val(a['ATfd'],'Ncl6',rank)
 assert val(a['AFg1'],'amcs',rank)==25
assert 'GetSpellTargetLoc()' in functions['Trig_Guardian_Force_Field_Cast_Actions']
assert 'p, 72.0, PATHING_TYPE_ANY' in functions['GFW_Create']
assert '72.0, PATHING_TYPE_ANY' in functions['Trig_Guardian_Force_Field_Loop_Actions']
assert '), 0.675)' in functions['GFW_Create']
assert "id == 'H043'" not in functions['MF_HeroDisabled']
assert 'set udg_hero_category[72]=1' in s
print('Guardian burst exhaustion, timeout, concurrent casters, fresh burst, spell slots, orders, targeting and footprint checks passed')

# Visual lifecycle tests execute the actual translated JASS helpers.
fx={};tracked=set();visual_data={};dead=set();enum=[7];fxid=[0]
def addfx(model,u,point):
 fxid[0]+=1;fx[fxid[0]]=(model,u);return fxid[0]
ns.update(GDV_Data=visual_data,GDV_Units=tracked,GDV_Step=1,GD_Count=1,LoadEffectHandle=lambda h,k,c:h.get((k,c)),SaveEffectHandle=Save,AddSpecialEffectTarget=addfx,DestroyEffect=lambda e:fx.pop(e,None),BlzSetSpecialEffectColor=lambda *a:None,GroupAddUnit=lambda g,u:g.add(u),GroupRemoveUnit=lambda g,u:g.discard(u),GetEnumUnit=lambda:enum[0],GetUnitTypeId=lambda u:0 if u in dead else 1,GetWidgetLife=lambda u:0 if u in dead else 100,RemoveSavedHandle=lambda h,k,c:h.pop((k,c),None),RemoveSavedInteger=lambda h,k,c:h.pop((k,c),None))
ns.update(GDB_Clear=lambda caster:None,LoadLightningHandle=lambda h,k,c:h.get((k,c)),DestroyLightning=lambda b:None,RemoveSavedReal=lambda h,k,c:h.pop((k,c),None))
for n in ['GDV_Mark','GDV_Pulse','GDV_CleanupUnit','GDV_Stop']:exec(ns['translate'](n).replace('function ',''),ns)
ns['GDV_Mark'](7,True);first=visual_data[7,0]
ns['GDV_Mark'](7,True);assert visual_data[7,0]==first and len(fx)==1
ns['GDV_Mark'](7,False);assert len(fx)==2 # opposing overlapping domes coexist
ns['GDV_CleanupUnit']();assert len(fx)==2
ns['GDV_Step']=2;ns['GDV_Mark'](7,True);ns['GDV_CleanupUnit']();assert len(fx)==1 and (7,4) not in visual_data
ns['GDV_Pulse'](7,True);count=fxid[0];ns['GDV_Pulse'](7,True);assert fxid[0]==count
ns['GDV_Step']=18;ns['GDV_Pulse'](7,True);assert fxid[0]==count+1
ns['GDV_Step']=19;ns['GDV_CleanupUnit']();assert not fx and not tracked and not visual_data
ns['GDV_Mark'](7,True);dead.add(7);ns['GDV_CleanupUnit']();assert not fx and not tracked
# Stop destroys only orbit effects, leaving coverage to the aggregate cleanup.
dead.clear();ns['GDV_Mark'](7,True)
for slot in range(10,13):visual_data[7,slot]=addfx('orbit',7,'origin')
ns['GDV_Stop'](7);assert len(fx)==1
ns['GD_Count']=0;ns['GDV_CleanupUnit']();assert not fx and not tracked and not visual_data
# Combat implementation is byte-identical after removing added visual calls.
before=(ROOT/'audit/v18-before-guardian/war3map.j').read_text()
original=re.search(r'(?ms)^function GD_Tick .*?^endfunction',before)[0]
updated=functions['GD_Tick']
updated=re.sub(r'(?m)^.*(?:call GDV_|set GDV_Step|call ForGroup\(GDV_Units).*\n','',updated)
updated=updated.replace('                        if GetWidgetLife(u) < GetUnitState(u, UNIT_STATE_MAX_LIFE) or GetUnitState(u, UNIT_STATE_MANA) < GetUnitState(u, UNIT_STATE_MAX_MANA) then\n                        endif\n','')
assert updated==original
print('Guardian shield effects: reuse, overlap, exit, death, expiry, pulse throttling, orbit cleanup and unchanged combat checks passed')
# Projection tethers reuse three handles, follow caster and fade softly.
import math
beams={};beamid=[0];colors={}
def addbeam(kind,visible,*coords):
 assert kind=='DRAM';beamid[0]+=1;beams[beamid[0]]=coords;return beamid[0]
ns.update(Sin=math.sin,Cos=math.cos,I2R=float,R2I=int,GD_PERIOD=.05,GD_Loc=0,GetLocationZ=lambda loc:50.,GetUnitFlyHeight=lambda u:20.,LoadReal=lambda h,k,c:h.get((k,c),0.),SaveReal=Save,SaveLightningHandle=Save,AddLightningEx=addbeam,MoveLightningEx=lambda b,visible,*coords:beams.__setitem__(b,coords),SetLightningColor=lambda b,*rgba:colors.__setitem__(b,rgba),DestroyLightning=lambda b:beams.pop(b,None))
exec(ns['translate']('GDV_Project').replace('function ',''),ns)
ns['GDV_Step']=20;ns['GDV_Project'](7,100.,200.)
assert len(beams)==3
first=list(beams.values());alpha=[v[3] for v in colors.values()]
assert all(0<=a<=.55 for a in alpha)
for coords in first:
 assert coords[:3]==(100.,200.,170.)
 dx=coords[3]-100;dy=coords[4]-200;dz=coords[5]-(50.-41.)
 assert abs(dx*dx+dy*dy+dz*dz-600**2)<1e-5
ns['GDV_Project'](7,350.,400.)
assert len(beams)==3 and beamid[0]==3
assert all(c[:3]==(350.,400.,170.) for c in beams.values())
ns['GDV_Step']=60;ns['GDV_Project'](7,350.,400.)
assert beamid[0]==3 and list(beams.values())!=first
ns['GDV_Project'](8,0.,0.);assert len(beams)==6
ns['GDV_Stop'](7);assert len(beams)==3 and not any(k[0]==7 for k in visual_data)
ns['GDV_Stop'](8);assert not beams and not visual_data
print('Projection checks passed: soft alpha, shell endpoints, moving chest origin, handle reuse, endpoint variation, independent casters and cleanup')
