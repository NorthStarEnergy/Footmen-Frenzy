# Adds recording mocks for the new visual/status natives to the prior behavior suite.
for name in ['MQ_ClearLoaded','MQ_LoadBloodied','MDV_Clear','MDV_Update']:
 exec(translate(name),env)
visual_base_setup=setup
def setup():
 visual_base_setup()
 noop=lambda *a:None
 def create(kind):
  counter[0]+=1;fx[counter[0]]=dict(kind=kind);return counter[0]
 for kind in ['LightningHandle','TextTagHandle']:
  env['Save'+kind]=lambda h,i,k,v:H.update({(h,i,k):v})
  env['Load'+kind]=lambda h,i,k:H.get((h,i,k),0)
 env.update(RemoveSavedBoolean=lambda h,i,k:H.pop((h,i,k),None),HaveSavedReal=lambda h,i,k:(h,i,k) in H,
  AddLightningEx=lambda *a:create('beam'),CreateTextTag=lambda:create('label'),
  DestroyLightning=lambda f:fx[f].update(destroyed=True) if f else None,DestroyTextTag=lambda f:fx[f].update(destroyed=True) if f else None,
  MoveLightningEx=noop,SetLightningColor=noop,SetTextTagPos=noop,SetTextTagPermanent=noop,SetTextTagVisibility=noop,SetTextTagColor=noop,SetTextTagText=noop,
  IsVisibleToPlayer=lambda *a:True,GetLocalPlayer=lambda:0,I2S=str,R2I=int,
  MDV_Code={i:f'mD{i-1:02X}' for i in range(1,257)},MDV_Used=defaultdict(bool),
  BlzGetAbilityIcon=lambda uid:'icon:'+str(uid),GetUnitName=lambda u:'Unit '+str(u),
  BlzSetAbilityIcon=lambda a,icon:event.setdefault('icons',{}).update({a:icon}),
  BlzSetAbilityTooltip=lambda a,text,lv:event.setdefault('titles',{}).update({a:text}),
  BlzSetAbilityExtendedTooltip=lambda a,text,lv:event.setdefault('tips',{}).update({a:text}),
  BlzSetUnitAbilityCooldown=lambda u,a,lv,t:event.setdefault('full_cd',{}).update({(u,a):t}),
  BlzStartUnitAbilityCooldown=lambda u,a,t:event.setdefault('remaining_cd',{}).update({(u,a):t}))

exec(translate('MU_FlingSafe'),env)
terrain_base_setup=setup
def setup():
 terrain_base_setup()
 env.update(bj_mapInitialPlayableArea=1,bj_PI=math.pi,I2R=float,IMinBJ=min,SquareRoot=math.sqrt,
  GetTerrainCliffLevel=lambda x,y:2,BlzGetUnitCollisionSize=lambda u:32.,
  GetRectMinX=lambda r:-10000.,GetRectMaxX=lambda r:10000.,
  GetRectMinY=lambda r:-10000.,GetRectMaxY=lambda r:10000.)
