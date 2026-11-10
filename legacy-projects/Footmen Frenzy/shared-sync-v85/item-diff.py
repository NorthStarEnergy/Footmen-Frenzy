"""Execute actual final JASS bodies with mocked natives; no engine claims."""
from pathlib import Path
from collections import defaultdict
import sys,re,ast,json,math
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W/'hero-polish'))
from archive_helpers import functions as split_functions,storm,read_storm,c
# Load the reusable translator definitions only (never run its historical test setup).
env={}
for node in ast.parse((W/'799x-backport/check_runtime.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ['expression','translate']:exec(compile(ast.Module(body=[node],type_ignores=[]),'translator','exec'),env)
env['re']=re
scripts={}
paths={'old':W/'consolidated-v84/release/FF799X_Rx_Consolidated_v84_TEST.w3x','main':R/'release/FF799X_Rx_Shared_Fixes_v85_TEST.w3x','solo':R/'release/Solo_Foots_v1.8_4P_SHARED_FIXES_UPDATE09.w3x'}
for name,path in paths.items():
 h=c.c_void_p();assert storm.SFileOpenArchive(str(path),0,256,c.byref(h));scripts[name]=read_storm(h,'war3map.j').decode('utf-8-sig').replace('\r','');assert storm.SFileCloseArchive(h)
fs={k:split_functions(v) for k,v in scripts.items()};checks=[];cases=0

def code(variant,names,generator=False):
 env['functions']=fs[variant];text='\n\n'.join(env['translate'](n) for n in names)
 text=re.sub(r'\bfunction\s+(\w+)',r'\1',text)
 lines=text.splitlines();result=[]
 for i,line in enumerate(lines):
  result.append(line)
  if line.rstrip().endswith(':') and i+1<len(lines) and len(lines[i+1])-len(lines[i+1].lstrip())<=len(line)-len(line.lstrip()):result.append(' '*(len(line)-len(line.lstrip())+4)+'pass')
 text='\n'.join(result)
 if generator:text=re.sub(r'TriggerSleepAction\s*\(\s*([\d.]+)\s*\)',r'(yield \1)',text)
 return text

def check(label,condition):
 assert condition,label
 checks.append(label)
noop=lambda *a:None
# Differential validation of all original 799X item-cap/hero-block rules.
rawcodes=sorted(set(re.findall(r"'(.{4})'",'\n'.join(f for n,f in fs['old'].items() if n.startswith('Trig_ITEM_limits')))))
heroes=rawcodes+['H043','HVg1','HMu1','HGr1','HOr1','HTf1','hfoo']

def item_env(v):
 state={};e={};exec(code(v,[n for n in fs[v] if n.startswith(('Trig_ITEM_limits','ItemLimit_'))]),e)
 def slot(u,i):return state['inventory'][i-1] if i<=len(state['inventory']) else None
 def drop(it,u=None):
  if it is not None and it in state['inventory']:state['removed'].append(it[0]);state['inventory'].remove(it)
 def item(t):return next((it for it in state['inventory'] if it[0]==t),None)
 e.update(GetTriggerUnit=lambda:1,GetManipulatedItem=lambda:state['picked'],GetItemTypeId=lambda i:i[0] if i else '',GetTriggerPlayer=lambda:0,GetConvertedPlayerId=lambda p:p+1,ConvertedPlayer=lambda p:p-1,GetUnitTypeId=lambda u:state['hero'],UnitItemInSlotBJ=slot,UnitItemInSlot=lambda u,i:slot(u,i+1),GetItemOfTypeFromUnitBJ=lambda u,t:item(t),GetItemName=lambda i:i[0] if i else '',GetUnitName=lambda u:state['hero'],UnitRemoveItemSwapped=drop,UnitRemoveItem=lambda u,it:drop(it),RemoveItem=drop,DisplayTextToForce=lambda force,msg:state['messages'].append(msg),DisplayTextToPlayer=lambda p,x,y,msg:state['messages'].append(msg),GetForceOfPlayer=lambda p:p,DestroyForce=noop,DoNothing=noop,I2S=str)
 def run(t,h,count):
  state.update(inventory=[(t,i) for i in range(count)],picked=(t,0),hero=h,removed=[],messages=[])
  e['Trig_ITEM_limits_Actions']()
  return list(state['removed']),list(state['messages'])
 return run
old,new=item_env('old'),item_env('main')
for t in rawcodes+['zzzz']:
 for h in heroes:
  for count in range(1,7):
   a,b=old(t,h,count),new(t,h,count)
   if a!=b and count==2 and h==heroes[0]:print(t,h,a,b)
   cases+=1


