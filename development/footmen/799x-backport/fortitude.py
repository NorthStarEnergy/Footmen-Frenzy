"""Immediate item armor; targeted, rank-correct cosmetic buff replaces self aura."""
import re,copy
def patch(s):
 old="""                call UnitAddAbility(u, 'AGf1')
                call SetUnitAbilityLevel(u, 'AGf1', level)
                call BlzUnitHideAbility(u, 'AGf1', true)"""
 new="""                // One fixed-rank item modifier: immediate armor, no aura polling.
                call UnitAddAbility(u, 'GF01' + level - 1)
                call BlzUnitHideAbility(u, 'GF01' + level - 1, true)
                // Set the display spell rank before issuing its only order.
                set fortDummy = CreateUnit(owner, 'hor3', GetUnitX(u), GetUnitY(u), 0.0)
                call UnitAddAbility(fortDummy, 'GFbf')
                call SetUnitAbilityLevel(fortDummy, 'GFbf', level)
                call IssueTargetOrder(fortDummy, "innerfire", u)
                call UnitApplyTimedLife(fortDummy, 'BTLF', 1.0)
                set fortDummy = null"""
 assert old in s;s=s.replace(old,new)
 s=s.replace('function FS_OnCast takes nothing returns nothing','function FS_OnCast takes nothing returns nothing\n    local unit fortDummy = null')
 needle="        call UnitRemoveAbility(FS_U[i], 'BGf1' + rank - 1)"
 assert needle in s;s=s.replace(needle,needle+"\n        call UnitRemoveAbility(FS_U[i], 'GF01' + rank - 1)")
 return s
def objects(data):
 ids={e['newId'] for t in data['tables'] for e in t};assert not ids & {'GFbf',*[f'GF0{i}' for i in range(1,7)]}
 def entry(base,uid,rows):
  e={'oldId':base,'newId':uid,'flags':1,'extra':0,'mods':[]}
  for field,typ,level,ptr,value in rows:e['mods'].append(dict(id=field,type=typ,level=level,ptr=ptr,value=value,end=uid.encode().hex()))
  data['tables'][1].append(e)
 common=[('aher',0,0,0,0),('areq',3,0,0,''),('aart',3,0,0,''),('alev',0,0,0,1)]
 for rank in range(1,7):entry('AId1',f'GF0{rank}',common+[('anam',3,0,0,f'Fortitude armor {rank}'),('Idef',0,1,1,3+2*rank)])
 rows=[r for r in common if r[0]!='alev']+[('alev',0,0,0,6),('anam',3,0,0,'Fortitude buff display'),('aite',0,0,0,0),('atat',3,0,0,'')]
 for rank in range(1,7):
  rows += [('Inf1',1,rank,1,0.0),('Inf2',0,rank,2,0),('Inf3',1,rank,3,0.0),('Inf4',1,rank,4,0.0),('abuf',3,rank,0,f'BGf{rank}'),('adur',1,rank,0,5.0),('ahdu',1,rank,0,5.0),('amcs',0,rank,0,0),('acdn',1,rank,0,0.0),('aran',1,rank,0,99999.0),('atar',3,rank,0,'friend,ground,air,organic,mechanical,invulnerable,vulnerable'),('acas',1,rank,0,0.0)]
 entry('Ainf','GFbf',rows)
 return data
