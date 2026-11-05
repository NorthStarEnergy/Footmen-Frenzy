from pathlib import Path
import re,runpy,collections,json
R=Path(__file__).resolve().parent
base=runpy.run_path(str(R/'verify_king.py'))
World=base['World'];players=base['players'];slots=base['slots'];s=(R/'roundtrip/war3map.j').read_text()
helper=(R.parent/'ffa-v4/verify_behavior.py').read_text();exec(helper[helper.index('def translate('):helper.index("translated='")])
names=set(re.findall(r'^function ((?:DPS_|zoom_|FF_st_)\w+) ',s,re.M))
code='\n\n'.join(translate(n) for n in sorted(names));(R/'ui-translated.py').write_text(code)
class UI(World):
 def __init__(self,king=True):
  super().__init__(king=king);e=self.e;self.frames=[];self.mutations=[];self.chatregs=[];self.saved={};self.hash={};self.camera={p:2500 for p in range(24)}
  for typ,name,value in re.findall(r'^\s*(?:constant )?(\w+)\s+((?:DPS_|zoom_|FF_ST_|FF_st_)\w+)\s*=\s*([^\n]+)',s,re.M):
   value=value.strip()
   if re.fullmatch(r'-?[\d.]+',value):e[name]=float(value) if '.' in value else int(value)
   elif value=='null':e[name]=None
   elif value in ['true','false']:e[name]=value=='true'
   elif value.startswith('"'):e[name]=value[1:-1]
  e.update(localplayer=0,now=0.,GetLocalPlayer=lambda:e['localplayer'],GetHandleId=id,
   BlzCreateFrame=lambda name,parent,*a:self.frame(name,parent),
   BlzCreateFrameByType=lambda kind,name,parent,inherit,context:self.frame(name,parent,kind,context),
   BlzGetOriginFrame=lambda kind,index:kind,BlzGetFrameByName=lambda *a:'multiboard',
   BlzLoadTOCFile=lambda name:True,BlzGetTriggerFrameValue=lambda:e['value'],
   BlzFrameSetText=lambda f,v:self.setframe(f,'text',v),BlzFrameSetVisible=lambda f,v:self.setframe(f,'visible',v),
   BlzFrameSetEnable=lambda f,v:self.setframe(f,'enabled',v),BlzFrameSetValue=lambda f,v:self.setframe(f,'value',v),
   BlzFrameSetTexture=lambda f,v,*a:self.setframe(f,'texture',v),BlzFrameSetSize=lambda f,w,h:self.setframe(f,'size',(w,h)),
   GetCameraField=lambda field:self.camera[e['localplayer']] if field=='distance' else 10000.,
   SetCameraField=lambda field,value,duration:self.camera.__setitem__(e['localplayer'],value) if field=='distance' else None,
   TriggerRegisterPlayerChatEvent=lambda *a:self.chatregs.append(a),
   s__File_open=lambda name:e['localplayer'],s__File_close=lambda file:None,
   s__File_write=lambda file,text:self.saved.__setitem__(file,text),s__File_readEx=lambda file,*a:self.saved.get(file,''),
   R2I=int,S2I=lambda text:int(text) if re.fullmatch(r'-?\d+',text.strip()) else 0,SubString=lambda text,a,b:text[a:b],StringLength=len,
   GetEventDamageSource=lambda:e['source'],GetEventDamage=lambda:e['damage'],GetSpellAbilityId=lambda:e['spell'],GetSpellTargetUnit=lambda:e['target'],
   SaveReal=lambda h,key,child,val:self.hash.__setitem__((key,child),val),HaveSavedReal=lambda h,key,child:(key,child) in self.hash,
   LoadReal=lambda h,key,child:self.hash.get((key,child),0.),FlushChildHashtable=self.flush,
   TimerGetElapsed=lambda t:e['now'],IsPlayerAlly=lambda p,q:p==q or self.alliances.get((p,q,'passive'),False),
   GetHeroLevel=lambda u:u.get('level',1),BlzGetAbilityIcon=lambda kind:'icon/'+kind,
   CAMERA_FIELD_TARGET_DISTANCE='distance',CAMERA_FIELD_FARZ='far',PLAYER_SLOT_STATE_EMPTY='empty')
  for called in set(re.findall(r'\b(\w+)\(',code)):
   if called not in e and called not in names:e[called]=lambda *a:None
  for token in set(re.findall(r'\b(?:FRAMEPOINT|FRAMEEVENT|ORIGIN_FRAME|TEXT_JUSTIFY|EVENT_PLAYER_UNIT)_[A-Z_]+\b',code)):e[token]=token
  exec(code,e)
 def frame(self,name,parent,kind=None,context=0):
  f=dict(name=name,parent=parent,kind=kind,context=context);self.frames.append(f);return f
 def setframe(self,f,key,value):
  assert isinstance(f,dict),('Invalid frame',f,key,value)
  f[key]=value;self.mutations.append((id(f),key,value))
 def flush(self,h,key):
  for k in list(self.hash):
   if k[0]==key:del self.hash[k]

u=UI();e=u.e;e['DPS_Create']()
assert len([f for f in u.frames if f['name']=='DPS_HeroIcon'])==8
assert len([f for f in u.frames if f['name']=='DPS_Name'])==8
assert e['DPS_Button']['text']=='Stats' and not e['DPS_Panel']['visible']
for i,pn in enumerate(players):
 e['udg_unit_kills'][pn]=100+i;e['udg_unit_deaths'][pn]=200+i;e['udg_hero_kills'][pn]=i
 e['udg_hero_deaths'][pn]=10+i;e['DPS_Assists'][pn]=20+i;e['DPS_Caps'][pn]=30+i;e['DPS_Buildings'][pn]=40+i;e['FF_st_tmHits'][pn]=50+i
 e['udg_herO'][pn]=u.unit(pn-1,'H001');e['udg_herO'][pn]['level']=i+1
e['DPS_Refresh']()
for i,pn in enumerate(players):
 assert e['DPS_Cell'][pn*10+1]['text']==str(100+i)
 assert e['DPS_Cell'][pn*10+3]['text']==str(20+i)
 assert e['DPS_Cell'][pn*10+5]['text']==str(30+i)
 assert e['DPS_Cell'][pn*10+7]['text']==str(50+i)
 assert e['DPS_Cell'][pn*10+8]['text']==str(i+1)
for pn in players:
 e['localplayer']=pn-1;e['triggerplayer']=pn-1;before=len(u.frames)
 e['DPS_Toggle']();assert e['DPS_Open'][pn-1] and e['DPS_Panel']['visible']
 e['DPS_Toggle']();assert not e['DPS_Open'][pn-1] and not e['DPS_Panel']['visible']
 assert len(u.frames)==before
 e['triggerplayer']=(pn+2)%12;before=len(u.mutations);e['DPS_Toggle']();assert len(u.mutations)==before

# Zoom creates the imported slider/lock, clamps 1400-6000, persists locally and never changes game vision.
e['localplayer']=0;e['zoom_Init']();e['zoom__CreateSlider']()
assert e['zoom__slider']['name']=='MiniFootsZoomSlider' and len(u.chatregs)==96
assert set(a[1] for a in u.chatregs)==set(range(24))
for p in slots+[12,23]:
 e['localplayer']=p;e['triggerplayer']=p;e['value']=6500
 others={q:u.camera[q] for q in range(24) if q!=p};before=len(u.fog)
 e['zoom__handleSegment']();assert u.camera[p]==6000 and u.saved[p]=='6000' and e['zoom__sliderLabel']['text']=='6000'
 e['zoom__handleLockButton']();e['value']=2000;e['zoom__handleSegment']();assert u.camera[p]==6000
 e['zoom__handleLockButton']();e['value']=1000;e['zoom__handleSegment']();assert u.camera[p]==1400
 e['chat']='-z 3300';e['zoom__handleChatCommand']();assert u.camera[p]==3300 and u.saved[p]=='3300'
 u.camera[p]=2000;e['zoom__RestoreFromFile']();assert u.camera[p]==3300 and e['zoom__slider']['value']==3300
 assert all(u.camera[q]==v for q,v in others.items()) and len(u.fog)==before
 e['triggerplayer']=(p+1)%24;before=len(u.mutations);e['value']=4000;e['zoom__handleSegment']();assert len(u.mutations)==before
u.saved.clear();e['localplayer']=0;u.camera[0]=2500;e['zoom__RestoreFromFile']();assert u.camera[0]==2500

# Assists require recent damage by a current ally; all eight players can contribute.
for pn in players:
 u=UI();e=u.e;k=next(p for p in players if p!=pn);v=next(p for p in players if p not in [pn,k])
 e['SKCapture'](pn,k);target=u.unit(v-1,'H001');contributor=u.unit(pn-1,'hfoo');killer=u.unit(k-1,'hfoo')
 e.update(dead=target,source=contributor,damage=20.,now=5.);e['DPS_OnDamage']()
 e.update(killer=killer,now=14.);e['DPS_OnDeath']();assert e['DPS_Assists'][pn]==1 and not u.hash
 e.update(now=20.);e['DPS_OnDamage']();e.update(now=31.);e['DPS_OnDeath']();assert e['DPS_Assists'][pn]==1
 e['dead']=u.unit(v-1,'base');e['DPS_OnDeath']();assert e['DPS_Buildings'][k]==1
 e['dead']['illusion']=True;e['DPS_OnDeath']();assert e['DPS_Buildings'][k]==1
 e['source']=u.unit(12,'hfoo');e['dead']=target;e['DPS_OnDamage']();assert not u.hash

# Transmute counters use the donor's successful-target-death tracking and discard expired casts.
for pn in players:
 u=UI();e=u.e;caster=u.unit(pn-1,'H001');target=u.unit(27,'creep')
 e.update(dead=caster,target=target,spell='ANtm',now=1.);e['FF_st_OnSpell']();assert e['FF_st_tmN']==1
 e.update(dead=target,killer=caster,now=2.);e['FF_st_OnDeath']();assert e['FF_st_tmHits'][pn]==1 and e['FF_st_tmN']==0
 e.update(dead=caster,now=3.);e['FF_st_OnSpell']();e['now']=10.;e['FF_st_TmExpire']();assert e['FF_st_tmN']==0 and e['FF_st_tmTarget'][0] is None

# Frame creation remains synchronized. UI handlers contain no gameplay/unit/force mutations.
for name in ['DPS_Toggle','zoom__handleSegment','zoom__handleLockButton']:
 f=re.search(r'^function '+name+r'\b.*?^endfunction',s,re.M|re.S)[0]
 assert 'GetLocalPlayer()' in f
 assert not re.search(r'call (CreateUnit|SetUnit|SetPlayerAlliance|ForceAddPlayer|AdjustPlayerState)',f)
main=re.search(r'^function main\b.*?^endfunction',s,re.M|re.S)[0]
assert main.index('call DPS_Init()')<main.index('call InitCustomTriggers()')
for name in ['MiniFootsUI.fdf','MiniFootsUI.toc',r'war3mapImported\templates.toc']:
 assert (R/'roundtrip'/name).read_bytes()==(R/'src'/name).read_bytes()
print('PASS: eight stats rows/counters/icons; local open/close; 24-player zoom commands, clamp/lock/cache and camera isolation; eight-slot assists/buildings/transmutes; frame asset packaging and pre-capture death-handler ordering.')
