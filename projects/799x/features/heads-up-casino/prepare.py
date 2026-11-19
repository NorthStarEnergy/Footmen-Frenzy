"""Apply the casino and hero changes to the complete 799X RC35 SD Draft test."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import struct
import sys

FEATURE = Path(__file__).resolve().parent
ROOT = FEATURE.parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
from map_archive import Archive
from restore_rc6_item_text import dump, parse

TITLE = 'Reforged Footmen Frenzy v7.9.9X-rc36'
PARENT = '94dbd8c551a3d0d37c604b6b26094c38bf1d21ab0dc68f51685089de07aaa4b5'
EDGE_MODEL = r'war3mapImported\GuardianPentagonDome.mdx'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'Expected one occurrence of {old[:92]!r}, got {source.count(old)}')
    return source.replace(old, new)


def module(name):
    return (FEATURE / name).read_text(encoding='utf-8').strip() + '\n\n'


def region(source, first, after, replacement):
    start = source.index('function ' + first + ' takes')
    end = source.index('function ' + after + ' takes', start)
    return source[:start] + replacement + source[end:]


def patch_globals(source):
    new = '''    integer PK_Queue = 0
    integer array PK_Table
    integer array PK_Guest
    integer array PK_Default
    integer array PK_LastPot
    integer array PK_Version
    integer array PK_InputVersion
    boolean array PK_Ready
    string array PK_Feedback
    framehandle array PK_Input
    framehandle array PK_Prompt
    framehandle array PK_Alternate
    hashtable TF_PendingCard = InitHashtable()
    string array BJ_dealerAction
'''
    return once(source, '    integer array PokerBuyIn', new + '    integer array PokerBuyIn')


def poker(s):
    s = region(s, 'PK_Limit', 'PK_Pay', '')
    s = region(s, 'PK_End', 'PK_Texture', module('poker-table.j'))
    s = region(s, 'PK_Render', 'PK_Button', module('poker-panel.j'))
    s = once(s, 'or ModuloInteger(stake,2) != 0 or CAS_gold', 'or (game != 0 and ModuloInteger(stake,2) != 0) or CAS_gold')
    s = once(s, '    local trigger chat = CreateTrigger()\n    loop\n        exitwhen p >= 24',
             '    local trigger chat = CreateTrigger()\n    local trigger sync = CreateTrigger()\n    call TriggerAddAction(sync,function PK_Sync)\n    loop\n        exitwhen p >= 24')
    s = once(s, 'set click = CreateTrigger()\n            set PK_Fold', '''set click = CreateTrigger()
            set PK_Default[p] = 100
            set PK_Version[p] = 1
            set PK_Feedback[p] = ""
            set PK_Prompt[p] = PK_Label(p,0.454,0.081,0.225,0.023,0.96)
            set PK_Input[p] = BlzCreateFrame("EscMenuEditBoxTemplate",PK_Dialog[p],0,p)
            call BlzFrameSetSize(PK_Input[p],0.168,0.033)
            call BlzFrameSetPoint(PK_Input[p],FRAMEPOINT_TOPLEFT,PK_Dialog[p],FRAMEPOINT_TOPLEFT,0.454,-0.107)
            call BlzFrameSetTextSizeLimit(PK_Input[p],6)
            call BlzTriggerRegisterFrameEvent(click,PK_Input[p],FRAMEEVENT_EDITBOX_ENTER)
            call BlzTriggerRegisterPlayerSyncEvent(sync,Player(p),"FFPK35",false)
            set PK_Alternate[p] = PK_Button(p,click,0.285,-0.439,0.180,"Practice")
            set PK_Fold''')
    s = once(s, 'call TriggerRegisterPlayerChatEvent(chat,Player(p),"-poker",true)',
             'call TriggerRegisterPlayerChatEvent(chat,Player(p),"-poker",true)\n            call TriggerRegisterPlayerChatEvent(chat,Player(p),"-raise ",false)')
    s = once(s, '"Blinds 1/2. Set buy-in with -stake (max 300g), then Deal."', '""')
    # Allow space for opponent names and two labelled amounts beside each hand.
    for old, new in [
        ('0.105,0.090,0.085,0.017','0.025,0.086,0.231,0.023'),
        ('0.105,0.109,0.085,0.032,1.48','0.025,0.114,0.155,0.056,1.08'),
        ('0.105,0.314,0.085,0.017','0.025,0.308,0.231,0.023'),
        ('0.105,0.333,0.085,0.032,1.48','0.025,0.335,0.155,0.051,1.08'),
        ('0.532,0.205,0.134,0.038','0.537,0.197,0.139,0.048'),
        ('0.52,-0.439,0.155,"Next hand"','0.478,-0.439,0.197,"Find player"'),
        ('0.26,-0.439,0.12,"Raise"','0.26,-0.439,0.12,"Raise to"'),
        ('elseif PK_Started[s-1] and not PK_Hidden[s-1] then\n        return 300','elseif PK_Started[s-1] and not PK_Hidden[s-1] then\n        return 1500'),
        ('            set CAS_amount[s] = IMinBJ(300,CAS_amount[s])\n',''),
        ('        set amount = SubString(line,7,StringLength(line))', '''        set amount = SubString(line,7,StringLength(line))
        if PK_Started[s-1] and not PK_Hidden[s-1] then
            call PK_Submit(s-1,"b",amount)
            return
        endif'''),
    ]:
        s = once(s, old, new)
    i = s.index('        if i < 24 and PokerBuyIn[i] > 0 then')
    j = s.index('        if BJ_phase[i]',i)
    s = s[:i] + '''        if i < 24 and PK_Queue == i+1 then
            call PK_CancelQueue(i)
        elseif i < 24 and PK_Table[i] == i+1 then
            call PK_CloseTable(i,true)
        endif
''' + s[j:]
    s = s.replace('// Each eligible observer owns an independent heads-up practice table.', '// Heads-up human matchmaking and optional computer practice use the same rules.')
    return s


def blackjack(s):
    s = region(s, 'BJ_Value', 'BJ_Shuffle', module('blackjack.j'))
    s = region(s, 'BJ_DealerHit', 'BJ_Payout', '''function BJ_DealerHit takes integer t returns nothing
    local integer count = BJ_dealerCount[t]
    local integer before = BJ_CardSum(t,count,true)
    set BJ_dealerTotal[t] = before
    if count >= 2 and before >= 17 then
        return
    endif
    set BJ_dealerCard[t*22+count] = BJ_Draw(t)
    set BJ_dealerCount[t] = count+1
    set BJ_dealerTotal[t] = BJ_CardSum(t,count+1,true)
    if count >= 2 then
        set BJ_dealerAction[t] = "Hit on "+I2S(before)+"  /  now "+I2S(BJ_dealerTotal[t])
    endif
endfunction

''')
    s = once(s,'function BJ_Next takes integer t returns nothing\n    local integer h = t*12',
             'function BJ_Next takes integer t returns nothing\n    local integer h = t*12\n    local boolean compare = false')
    s = once(s, '        if BJ_state[h] == 1 then\n            set BJ_turn', '''        if BJ_state[h] == 2 and BJ_bet[h] > 0 then
            set compare = true
        endif
        if BJ_state[h] == 1 then
            set BJ_turn''')
    s = once(s, '    set BJ_phase[t] = 3', '''    if not compare then
        set BJ_dealerAction[t] = "No hands left to compare"
        call BJ_Finish(t,false)
        return
    endif
    set BJ_dealerAction[t] = "Hole card revealed"
    set BJ_phase[t] = 3''')
    s = once(s, '    set BJ_round[t] = BJ_round[t]+1', '    set BJ_dealerAction[t] = ""\n    set BJ_round[t] = BJ_round[t]+1')
    s = once(s, '    elseif BJ_dealerTotal[t] == 21 then\n        call BJ_Finish', '    elseif BJ_dealerTotal[t] == 21 then\n        set BJ_dealerAction[t] = "Blackjack"\n        call BJ_Finish')
    s = once(s,'                if BJ_dealerTotal[t] < 17 then','                if BJ_CardSum(t,BJ_dealerCount[t],true) < 17 then')
    s = once(s, '                else\n                    call BJ_Finish(t,false)', '''                else
                    if BJ_dealerTotal[t] > 21 then
                        set BJ_dealerAction[t] = "Bust on "+I2S(BJ_dealerTotal[t])
                    else
                        set BJ_dealerAction[t] = "Stands on "+I2S(BJ_dealerTotal[t])
                    endif
                    call BJ_Finish(t,false)''')
    s = once(s,'        set dealer = dealer+"  "+CUI_Value(I2S(BJ_dealerTotal[t]))','''        set dealer = dealer+"  "+CUI_Value(I2S(BJ_dealerTotal[t]))+"   /   "+BJ_dealerAction[t]
    elseif BJ_dealerCount[t] > 0 then
        set dealer = dealer+"   /   Shows "+PK_Card(BJ_dealerCard[t*22])+"   /   Hole card down"''')
    s = once(s,'"2 DECKS / PAYS 3:2"','"STANDS ON ALL 17s  /  3:2"')
    s = once(s,'    elseif BJ_bet[h] > 0 then\n        set phase = phase+"|nIN PLAY', '    elseif BJ_phase[t] == 4 then\n        set phase = phase+"|nLAST BET  "+CUI_Value(I2S(BJ_bet[h])+"g")\n    elseif BJ_bet[h] > 0 then\n        set phase = phase+"|nIN PLAY')
    s = once(s,'    if action == 1 then\n        call BJ_Hit(t,h)','''    if action == 1 then
        call BJ_Hit(t,h)
        set BJ_clock[t] = 20
        set CAS_note[s] = "Hit  /  drew "+PK_Card(BJ_card[h*22+BJ_count[h]-1])+"  /  total "+I2S(BJ_total[h])''')
    s = once(s,'    elseif action == 2 then\n        set BJ_state[h] = 2','    elseif action == 2 then\n        set CAS_note[s] = "Standing on "+I2S(BJ_total[h])\n        set BJ_state[h] = 2')
    s = once(s,'        set BJ_bet[h] = stake*2','        set CAS_note[s] = "Doubled  /  wager now "+I2S(stake*2)+"g"\n        set BJ_bet[h] = stake*2')
    s = once(s,'        set card = BJ_card[h*22+1]','        set CAS_note[s] = "Split  /  "+I2S(stake)+"g on each hand"\n        set card = BJ_card[h*22+1]')
    # Never reset another human's payout display during the results interval.
    s = once(s,'    if BJ_phase[t] == 4 then\n        call BJ_Reset(t)','    if BJ_phase[t] == 4 then\n        if t == 0 and BJ_clock[t] > 0 then\n            set CAS_note[s] = "Next round opens in "+I2S(BJ_clock[t])+"s."\n            return\n        endif\n        call BJ_Reset(t)')
    s = once(s,'    call CAS_ShowButton(s,11,BJ_phase[t] == 0 or BJ_phase[t] == 4', '    call CAS_ShowButton(s,11,BJ_phase[t] == 0 or (BJ_phase[t] == 4 and (t != 0 or BJ_clock[t] == 0))')
    s = once(s,'    set label = "BET "+CUI_Value','    set label = "SELECTED BET  "+CUI_Value')
    s = once(s,'    call BlzFrameSetText(CAS_status[s],label)','''    if CAS_view[s] == 1 then
        set label = label+"    /    ON TABLE  "+CUI_Value(I2S(BJ_bet[BJ_seat[s]*2]+BJ_bet[BJ_seat[s]*2+1])+"g")
    endif
    call BlzFrameSetText(CAS_status[s],label)''')
    s = once(s, '    call CAS_Render(s)\n    set f = null\nendfunction\n\nfunction CasinoFromStats', '''    if id >= 6 and id <= 10 then
        set CAS_note[s] = "Selected bet is now "+I2S(CAS_amount[s])+"g."
    elseif id >= 26 and id <= 31 and MK_pick[s] > 0 then
        set CAS_note[s] = "Selected "+MK_Label(MK_tab[s],MK_pick[s])+"  /  wager "+I2S(CAS_amount[s])+"g"
    elseif id == 34 then
        set CAS_note[s] = "Challenge opponent  /  "+CAS_Name(DU_opponent[s])
    elseif id == 35 then
        set CAS_note[s] = "Backing  /  "+MK_Label(5,DU_pick[s])
    endif
    call CAS_Render(s)
    set f = null
endfunction

function CasinoFromStats''')
    return s


def fate(s):
    s = once(s, '''function TF33_Cast takes nothing returns nothing
    local unit c=GetTriggerUnit()
    local unit v=GetSpellTargetUnit()
    local integer id=GetSpellAbilityId()''','function TF33_Cast takes unit c, unit v, integer id returns nothing')
    s = once(s, 'function TF45_Odds takes',module('fate-control.j')+'function TF45_Odds takes')
    s = once(s, '    call TriggerAddAction(t,function TF33_Cast)', '''    call TriggerAddAction(t,function TF_CardEffect)
    set t=CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SPELL_CHANNEL)
    call TriggerAddAction(t,function TF_CardChannel)
    set t=CreateTrigger()
    call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SPELL_ENDCAST)
    call TriggerAddAction(t,function TF_CardEnd)''')
    s = once(s, '    if not TFP_TF_Alive(c) or GetUnitAbilityLevel(c,','''    if HaveSavedInteger(TF_PendingCard,h,3) or HaveSavedInteger(TF_PendingCard,h,0) or LoadBoolean(TF_PendingCard,h,2) then
        return
    endif
    if not TFP_TF_Alive(c) or GetUnitAbilityLevel(c,''')
    s = once(s, 'GetEventDamage()>0.0 and LoadBoolean(TF33_H,h,5)', 'GetEventDamage()>0.0 and not HaveSavedInteger(TF_PendingCard,h,3) and not HaveSavedInteger(TF_PendingCard,h,0) and not LoadBoolean(TF_PendingCard,h,2) and LoadBoolean(TF33_H,h,5)')
    # The tracking card is cosmetic. An attached effect cannot enter unit order,
    # collision, selection, sale, hero tracking or AI systems.
    s = once(s, "        set orb=CreateUnit(GetOwningPlayer(c),'htf1',GetUnitX(c),GetUnitY(c),0.)\n        call SetUnitScale(orb,0.85,0.85,0.85)",r'''        call SaveEffectHandle(TF33_H,h,2,AddSpecialEffectTarget("war3mapImported\\TFPickedCard.mdx",c,"overhead"))''')
    s = once(s,'        call SaveUnitHandle(TF33_H,h,2,orb)\n','')
    s = once(s, '    call ShowUnit(LoadUnitHandle(TF33_H,h,2),false)\n    call RemoveUnit(LoadUnitHandle(TF33_H,h,2))','    call DestroyEffect(LoadEffectHandle(TF33_H,h,2))')
    s = once(s, '''    local unit orb=LoadUnitHandle(TF33_H,h,2)
    local integer ticks''','''    local effect orb=LoadEffectHandle(TF33_H,h,2)
    local integer color=LoadInteger(TF33_H,h,4)
    local integer ticks''')
    a=s.index('    call SetUnitX(orb,GetUnitX(c))')
    b=s.index('    set orb=null',a)
    s=s[:a]+'''    call BlzSetSpecialEffectScale(orb,scale)
    if color == 1 then
        call BlzSetSpecialEffectColor(orb,255,45,45)
    elseif color == 2 then
        call BlzSetSpecialEffectColor(orb,255,210,30)
    else
        call BlzSetSpecialEffectColor(orb,70,159,255)
    endif
'''+s[b:]
    s = once(s,'    call TriggerAddAction(t, function TF_ClearGuardOnEvent)','    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_HERO_LEVEL)\n    call TriggerRegisterAnyUnitEventBJ(t, EVENT_PLAYER_HERO_SKILL)\n    call TriggerAddAction(t, function TF_ClearGuardOnEvent)')
    s = once(s,'    if IsUnitInGroup(dead,TF33_Heroes) then','    call FlushChildHashtable(TF_PendingCard,GetHandleId(dead))\n    if IsUnitInGroup(dead,TF33_Heroes) then')
    return s


def guardian_text(s):
    return re.sub(r'(Enemies are slowed, lose mana and take \|cffff8979)(90|120|150)(\|r damage)',lambda m:m[1]+{'90':'67.5','120':'90','150':'112.5'}[m[2]]+m[3],s)


def runtime(s):
    s = fate(blackjack(poker(s)))
    s = once(s, 'set amount = 60.0 + 30.0 * rank','set amount = 45.0 + 22.5 * rank')
    s = s.replace('// Force Shield (Team colour), by ApeJI, imported unchanged.',"// Force Shield by ApeJI, with contrasting pentagon edges.")
    s = guardian_text(s)
    for slot in (10,40):
        for field,value in [('HP',725),('armor',0)]:
            s,count=re.subn(rf'(set udg_unit_{field}\[{slot}\]=)\d+',lambda m:m[1]+str(value),s)
            assert count==1
    return s


def recolor_model(data):
    # Material 1 belongs only to the polygon strips (geoset 2). The dome is material 0.
    output = bytearray(data)
    pos = 4
    found = set()
    while pos < len(output):
        tag, length = struct.unpack_from('<4sI',output,pos)
        start = pos+8
        end = start+length
        if tag == b'MTLS':
            material = start+struct.unpack_from('<I',output,start)[0]
            assert output[material+12:material+16] == b'LAYS'
            assert struct.unpack_from('<IIII',output,material+16) == (1,28,2,145)
            assert struct.unpack_from('<I',output,material+32)[0] == 4
            struct.pack_into('<f',output,material+44,0.90)
            found.add(tag)
        if tag == b'GEOA':
            i = start
            while i < end:
                size = struct.unpack_from('<I',output,i)[0]
                if struct.unpack_from('<I',output,i+24)[0] == 2:
                    assert size == 28
                    struct.pack_into('<fff',output,i+12,0.56,0.12,0.24)  # BGR, dark violet
                    found.add(tag)
                i += size
        pos = end
    assert found == {b'MTLS',b'GEOA'} and pos==len(output)
    return bytes(output)


def units(data):
    obj = parse(data)
    assert dump(obj)==data
    found=set()
    for rows in obj[1]:
        for hdr,mods in rows:
            ident=hdr[4:8]
            if ident in (b'n04X',b'o019'):
                for field,kind,value,_ in mods:
                    if field in (b'uhpm',b'udef'):
                        current=struct.unpack('<i',value)[0]
                        expected={b'n04X':(775,1),b'o019':(750,2)}[ident][field==b'udef']
                        assert current==expected and kind==0
                        found.add((ident,field))
                for mod in mods:
                    if mod[0] in (b'uhpm',b'udef'):
                        mod[2]=struct.pack('<i',struct.unpack('<i',mod[2])[0]-(50 if mod[0]==b'uhpm' else 1))
            if ident==b'HTf1':
                assert all(mod[0]!=b'ufle' for mod in mods)
                mods.append([b'ufle',0,bytes(4),bytes(4)])
    assert len(found)==4
    return dump(obj)


def abilities(data,script):
    obj=parse(data,True)
    for rows in obj[1]:
        for hdr,mods in rows:
            if hdr[4:8]==b'AZd1':
                for mod in mods:
                    if mod[0] in (b'arut',b'aub1'):
                        rank=max(1,struct.unpack_from('<i',mod[2])[0])
                        desc=re.search(r"BlzSetAbilityExtendedTooltip\('AZd1', \"([^\"]+)\", "+str(rank-1)+r'\)',script)[1]
                        mod[2]=mod[2][:8]+desc.encode()+b'\0'
    return dump(obj)


def prepare(baseline,stage):
    if sha(baseline.read_bytes()) != PARENT:
        raise ValueError('Expected complete RC35 Blackjack UI baseline')
    project=stage/'projects/799x'
    release=project/'release'
    release.mkdir(parents=True,exist_ok=True)
    if not (release/baseline.name).exists():
        shutil.copy2(baseline,release/baseline.name)
    (project/'project.json').write_text(json.dumps(dict(map_type='799X',release=baseline.name,sha256=PARENT,branch='Footmen-Frenzy-12p')))
    for n in ('Build-Map.ps1','tools.local.json','tools/build_map.py','tools/map_archive.py','tools/Install-Wc3Map.ps1'):
        dst=stage/n
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/n,dst)
    with Archive(json.loads((ROOT/'tools.local.json').read_text())['stormlib'],baseline) as archive:
        read=archive.read
        def script(name,patch):
            raw=read(name)
            text=patch(raw.decode().replace('\r\n','\n'))
            if b'\r\n' in raw:
                text=text.replace('\n','\r\n')
            return text.encode()
        j=script('war3map.j',lambda s:re.sub(r'call SetMapName\("[^"]+"\)',f'call SetMapName("{TITLE}")',runtime(patch_globals(s))))
        rname=r'source_roundtrip\FF_Runtime.j'
        gname=r'source_roundtrip\globals.j'
        # RC35 only published its new blackjack layout in the playable script.
        # Carry its three edited frame functions and frame array into the editor.
        def editor_runtime(source):
            parent=read('war3map.j').decode().replace('\r\n','\n')
            for name in ('CAS_BlackjackView','CAS_Render','CAS_BuildPlayer'):
                pattern=rf'(?ms)^function {name} takes .*?^endfunction'
                body=re.search(pattern,parent)[0]
                source,count=re.subn(pattern,lambda _:body,source)
                assert count==1
            return runtime(source)
        r=script(rname,editor_runtime)
        g=script(gname,lambda s:patch_globals(once(s,'    integer array PokerBuyIn','    framehandle array BJ_wagerLabel\n    integer array PokerBuyIn')))
        w=read('war3map.wct')
        def record(data):
            return struct.pack('<I',len(data)+1)+data+b'\0'
        for name,updated in [(rname,r),(gname,g)]:
            w=once(w,record(read(name)),record(updated))
        manifest=json.loads(read('FF_SOURCE_MANIFEST.json'))
        manifest.update(compiled_source_sha256=sha(j),runtime_sha256=sha(r),globals_sha256=sha(g),
                        runtime_functions=len(re.findall(rb'(?m)^function ',r)),source_map_sha256=PARENT,revision=TITLE,engine_playtest=False)
        info=read('war3map.w3i')
        old=info[28:info.index(0,28)]
        info=info[:28]+TITLE.encode()+info[28+len(old):]
        wts=read('war3map.wts')
        wts=re.sub(rb'(?m)^'+re.escape(old)+rb'(?=\r?$)',TITLE.encode(),wts)
        for k in (10714,17913,14371,14374):
            wts,n=re.subn(rb'(?ms)(^STRING '+str(k).encode()+rb'\s.*?^\{.*?^)\}',lambda m:m[0].replace(b'775',b'725').replace(b'Armor: 1',b'Armor: 0'),wts)
            assert n==1
        outputs={'war3map.j':j,'war3map.wts':wts,'war3map.wct':w,'war3map.w3i':info,rname:r,gname:g,
                 'war3map.w3u':units(read('war3map.w3u')),'war3map.w3a':abilities(read('war3map.w3a'),j.decode()),
                 EDGE_MODEL:recolor_model(read(EDGE_MODEL)), 'FF_SOURCE_MANIFEST.json':(json.dumps(manifest,indent=2)+'\n').encode()}
        for name,data in outputs.items():
            dst=project/'src'/name
            dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_bytes(data)


if __name__=='__main__':
    prepare(Path(sys.argv[1]),ROOT/'build/799x-rc36-casino')
