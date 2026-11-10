from pathlib import Path
import sys, subprocess, shutil, hashlib, json
R=Path(__file__).resolve().parent; W=R.parent
sys.path[:0]=[str(W/'hero-polish'),str(W/'mini-foots/tools')]
from archive_helpers import storm,read_storm,c,archive,entries,functions
p=R/'src/war3map.j'; s=(W/'tf-destiny-v46/src/war3map.j').read_text(encoding='utf-8-sig'); before=s
def edit(n,a,b):
 global s
 f=functions(s)[n]; assert a in f,(n,a); s=s.replace(f,f.replace(a,b,1),1)
s=s.replace('group array TFP_LinkInside','hashtable GL_Armor = InitHashtable()\nlocation GTW_HeightLoc = Location(0.0, 0.0)\ngroup array TFP_LinkInside',1)
helper='''function GL_ArmorExpire takes nothing returns nothing
    local timer t = GetExpiredTimer()
    local integer k = GetHandleId(t)
    local unit u = LoadUnitHandle(GL_Armor, k, 0)
    local real amount = LoadReal(GL_Armor, k, 1)
    if u != null and GetUnitTypeId(u) != 0 then
        call BlzSetUnitArmor(u, BlzGetUnitArmor(u) - amount)
        call RemoveSavedHandle(GL_Armor, GetHandleId(u), 0)
    endif
    call FlushChildHashtable(GL_Armor, k)
    call DestroyTimer(t)
    set u = null
    set t = null
endfunction

function GL_ArmorApply takes unit u, real amount returns nothing
    local integer k = GetHandleId(u)
    local timer t = LoadTimerHandle(GL_Armor, k, 0)
    local real old = 0.0
    if t == null then
        set t = CreateTimer()
        call SaveTimerHandle(GL_Armor, k, 0, t)
        call SaveUnitHandle(GL_Armor, GetHandleId(t), 0, u)
    else
        set old = LoadReal(GL_Armor, GetHandleId(t), 1)
    endif
    call BlzSetUnitArmor(u, BlzGetUnitArmor(u) + amount - old)
    call SaveReal(GL_Armor, GetHandleId(t), 1, amount)
    call TimerStart(t, 2.0, false, function GL_ArmorExpire)
    set t = null
endfunction

'''
s=s.replace('function TFP_LinkGround takes',helper+'function TFP_LinkGround takes',1)
edit('TFP_LinkEffect',"'ALTc'","'AGbn'")
edit('TFP_LinkGround','        if u != TFP_FFDP_Caster[i] and GetWidgetLife(u)', '''        if TFP_LinkEnemy(u, TFP_FFDP_Owner[i]) and TFP_LinkDistanceSquared(ux, uy, ax, ay, bx, by) <= 65.0 * 65.0 then
            call GL_ArmorApply(u, -3.0)
            if not IsUnitInGroup(u, TFP_LinkInside[i]) then
                call TFP_LinkEffect(i, u, false)
            endif
            call GroupAddUnit(TFP_LinkNext, u)
        endif
        if u != TFP_FFDP_Caster[i] and GetWidgetLife(u)''')
edit('TFP_LinkGround','            call GroupAddUnit(TFP_LinkNext, u)\n            if not IsUnitInGroup(u, TFP_LinkInside[i]) then\n                call SetWidgetLife', '            call GroupAddUnit(TFP_LinkNext, u)\n            call GL_ArmorApply(u, 3.0)\n            if not IsUnitInGroup(u, TFP_LinkInside[i]) then\n                call SetWidgetLife')
edit('TFP_LinkGround','''                if not IsUnitType(u, UNIT_TYPE_MAGIC_IMMUNE) and not BlzIsUnitInvulnerable(u) then
                    call TFP_LinkEffect(i, u, false)
                endif
''','')
edit('TFP_FFDP_Tick','''                set x = GetUnitX(TFP_FFDP_Rider[i])
                set y = GetUnitY(TFP_FFDP_Rider[i])''','''                if GetUnitTypeId(TFP_FFDP_Caster[i]) == 'H043' then
                    call GL_ArmorApply(TFP_FFDP_Rider[i], 3.0)
                    call SetWidgetLife(TFP_FFDP_Rider[i], RMinBJ(GetUnitState(TFP_FFDP_Rider[i], UNIT_STATE_MAX_LIFE), GetWidgetLife(TFP_FFDP_Rider[i]) + 40.0 * TFP_FFDP_TICK))
                endif
                set x = GetUnitX(TFP_FFDP_Rider[i])
                set y = GetUnitY(TFP_FFDP_Rider[i])''')
edit('GFW_Create','0.70875','1.25');edit('GFW_Create','55, 105, 255','120, 200, 255');edit('GFW_Create','3.0)','1.0)')
edit('GTW_Cast','    local real dy\n','    local real dy\n    local real distance\n')
edit('GTW_Cast','    set GTW_Count = GTW_Count + 1','    set distance = RMaxBJ(200.0, RMinBJ(600.0 + 100.0 * I2R(GetUnitAbilityLevel(u, \'A0DL\')), SquareRoot(dx * dx + dy * dy)))\n    set GTW_Count = GTW_Count + 1')
edit('GTW_Cast',"    set GTW_Left[i] = 600.0 + 100.0 * I2R(GetUnitAbilityLevel(u, 'A0DL'))",'    set GTW_Left[i] = distance')
edit('GTW_Cast','    call BlzSetSpecialEffectScale(GTW_FX[i], 4.0)','    call BlzSetSpecialEffectScale(GTW_FX[i], 4.0)\n    call MoveLocation(GTW_HeightLoc, GTW_X[i], GTW_Y[i])\n    call BlzSetSpecialEffectZ(GTW_FX[i], GetLocationZ(GTW_HeightLoc) + 200.0)')
edit('GTW_Tick','            call BlzSetSpecialEffectY(GTW_FX[i], GTW_Y[i])','            call BlzSetSpecialEffectY(GTW_FX[i], GTW_Y[i])\n            call MoveLocation(GTW_HeightLoc, GTW_X[i], GTW_Y[i])\n            call BlzSetSpecialEffectZ(GTW_FX[i], GetLocationZ(GTW_HeightLoc) + 200.0)')
edit('GTW_Explode','Abilities\\\\Spells\\\\Human\\\\Thunderclap\\\\ThunderClapCaster.mdl','Abilities\\\\Spells\\\\Other\\\\Doom\\\\DoomDeath.mdl')
edit('GDV_Dome','    call GDB_Visual(GD_Caster[i])','    call GDB_Visual(GD_Caster[i])\n    call GDV_Project(GD_Caster[i], x, y)')
edit('GDB_Hit','1.0 + RMinBJ(1.0, GD_Left[LoadInteger(GD_Data, GetHandleId(caster), 0)] * 0.05)','1.5')
edit('GD_Tick','(30.0 + RMinBJ(100.0, 5.0 * GD_Left[i]))','30.0');edit('GD_Tick','set power = 1.0 + RMinBJ(1.0, GD_Left[i] * 0.05)','set power = 1.5');edit('GD_Tick','set GD_Left[i] = GD_Left[i] + GD_PERIOD','set GD_Left[i] = 0.0')
p.write_text(s,encoding='utf8')
work=Path.home()/'Documents/Codex/2026-10-28/thi/work'
r=subprocess.run([str(work/'jasshelper/pjass.exe'),str(work/'common.j'),str(work/'Blizzard.j'),str(p)],capture_output=True,text=True);(R/'compiler.log').write_text(r.stdout+r.stderr); print(r.stdout+r.stderr);assert r.returncode==0
base=W/'tf-destiny-v46/release/FF799X_Rx_TF_Destiny_v46.w3x';out=R/'release/FF799X_Rx_Guardian_v47.w3x';shutil.copy2(base,out)
h=c.c_void_p();assert storm.SFileOpenArchive(str(out),0,0,c.byref(h));assert storm.SFileAddFileEx(h,str(p),b'war3map.j',0x80000200,2,2);assert storm.SFileCloseArchive(h)
assert storm.SFileOpenArchive(str(out),0,0x100,c.byref(h));assert read_storm(h,'war3map.j')==p.read_bytes();assert storm.SFileCloseArchive(h)
a,b=archive(base),archive(out);old,new=entries(a),entries(b);skip=set()
for name in ['war3map.j','(listfile)','(attributes)','(signature)']:
 e=a.get_hash_table_entry(name)
 if e:skip.add((e.hash_a,e.hash_b,e.locale,e.platform))
for k,v in old.items():
 if k not in skip:assert new.get(k)==v
sha=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.sha256').write_text(sha+'  '+out.name+'\n');print(json.dumps({'output':str(out),'sha256':sha,'preserved':len(old.keys()-skip)},indent=2))

