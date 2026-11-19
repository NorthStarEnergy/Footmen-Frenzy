// BEGIN ITEMS CATALOG RUNTIME
// Gameplay handles are created only during synchronized hydration, never in click callbacks.
function IC_Plain takes string s returns string
    local string out = ""
    local integer i = 0
    local string c
    loop
        exitwhen i >= StringLength(s)
        set c = SubString(s, i, i+2)
        if c == "|c" or c == "|C" then
            set i = i + 10
        elseif c == "|r" or c == "|R" then
            set i = i + 2
        elseif c == "|n" or c == "|N" then
            set out = out + "\n"
            set i = i + 2
        else
            set c = SubString(s, i, i+1)
            if c != "\r" then
                set out = out + c
            endif
            set i = i + 1
        endif
    endloop
    return out
endfunction

function IC_Number takes real value returns string
    if value == I2R(R2I(value)) then
        return I2S(R2I(value))
    endif
    return R2SW(value, 0, 2)
endfunction

function IC_Matches takes string text, string query returns boolean
    local integer i = 0
    local integer n = StringLength(query)
    set text = StringCase(text, false)
    loop
        exitwhen i+n > StringLength(text)
        if SubString(text, i, i+n) == query then
            return true
        endif
        set i = i + 1
    endloop
    return n == 0
endfunction

function IC_Short takes string s returns string
    if StringLength(s) > 24 then
        return SubString(s, 0, 21) + "..."
    endif
    return s
endfunction

function IC_Cost takes integer idx returns string
    local string value = I2S(IC_Gold[idx]) + " gold"
    if IC_Lumber[idx] > 0 then
        set value = value + " / " + I2S(IC_Lumber[idx]) + " lumber"
    endif
    return value
endfunction

// Wrap by words before pagination, so long tooltips cannot run below the panel.
function IC_Paginate takes string text returns string
    local integer i = 0
    local integer column = 0
    local integer row = 0
    local string word = ""
    local string out = ""
    local string c
    set text = IC_Plain(text) + "\n"
    loop
        exitwhen i >= StringLength(text)
        set c = SubString(text,i,i+1)
        if c == " " or c == "\n" then
            if column > 0 and column + StringLength(word) > 88 then
                if row/12 == IC_TextPage then
                    set out = out + "\n"
                endif
                set row = row + 1
                set column = 0
            endif
            if row/12 == IC_TextPage then
                set out = out + word
                if c == " " then
                    set out = out + " "
                endif
            endif
            set column = column + StringLength(word) + 1
            set word = ""
            if c == "\n" then
                if row/12 == IC_TextPage then
                    set out = out + "\n"
                endif
                set row = row + 1
                set column = 0
            endif
        else
            set word = word + c
        endif
        set i = i + 1
    endloop
    set IC_TextPages = IMaxBJ(1,(row+11)/12)
    return out
endfunction

function IC_SetTile takes integer slot, integer idx returns nothing
    set IC_TileItem[slot] = idx
    call BlzFrameSetVisible(IC_Tile[slot], idx > 0)
    if idx > 0 then
        call BlzFrameSetTexture(IC_TileArt[slot], IC_Icon[idx], 0, true)
        call BlzFrameSetText(IC_TileLabel[slot], IC_Short(IC_Name[idx]) + "\n|cffffcc00" + I2S(IC_Gold[idx]) + "g|r")
    endif
endfunction

function IC_Render takes nothing returns nothing
    local integer i = 0
    local integer j
    local integer section
    local integer count = 0
    local integer idx
    local integer pages
    local string text
    call BlzFrameSetVisible(IC_Browse, IC_Selected == 0)
    call BlzFrameSetVisible(IC_Detail, IC_Selected > 0)
    call BlzFrameSetText(IC_Back, "Shops")
    if IC_Selected == 0 then
        loop
            exitwhen i == 24
            call IC_SetTile(i, 0)
            set i = i + 1
        endloop
        set i = 0
        loop
            exitwhen i == 2
            call BlzFrameSetVisible(IC_SectionArt[i], IC_Query == "")
            call BlzFrameSetVisible(IC_SectionTitle[i], IC_Query == "")
            set i = i + 1
        endloop
        if IC_Query == "" then
            set pages = (IC_Sections+1)/2
            set IC_Page = IMinBJ(IC_Page, pages-1)
            set i = 0
            loop
                exitwhen i == 2
                set section = IC_Page*2+i+1
                call BlzFrameSetVisible(IC_SectionArt[i], section <= IC_Sections)
                call BlzFrameSetVisible(IC_SectionTitle[i], section <= IC_Sections)
                if section <= IC_Sections then
                    call BlzFrameSetTexture(IC_SectionArt[i],IC_SectionIcon[section],0,true)
                    call BlzFrameSetText(IC_SectionTitle[i],IC_SectionName[section])
                    set j = 0
                    loop
                        exitwhen j >= IC_SectionCount[section]
                        call IC_SetTile(i*12+j,IC_Stock[IC_SectionStart[section]+j])
                        set j = j + 1
                    endloop
                endif
                set i = i + 1
            endloop
            call BlzFrameSetText(IC_Footer,"Shops " + I2S(IC_Page+1) + " / " + I2S(pages) + "   |   Click an item to inspect it")
        else
            set i = 1
            loop
                exitwhen i > IC_Count
                if IC_Matches(IC_Name[i],IC_Query) or IC_Matches(IC_Location[i],IC_Query) then
                    if count/24 == IC_Page then
                        call IC_SetTile(ModuloInteger(count,24),i)
                    endif
                    set count = count + 1
                endif
                set i = i + 1
            endloop
            set pages = IMaxBJ(1,(count+23)/24)
            call BlzFrameSetText(IC_Footer,I2S(count) + " matches   |   Page " + I2S(IC_Page+1) + " / " + I2S(pages))
        endif
        call BlzFrameSetEnable(IC_Previous, IC_Page > 0)
        call BlzFrameSetEnable(IC_Next, IC_Page+1 < pages)
    else
        set idx = IC_Selected
        call BlzFrameSetText(IC_Back, "Back")
        call BlzFrameSetTexture(IC_DetailIcon, IC_Icon[idx], 0, true)
        call BlzFrameSetText(IC_DetailName, IC_Name[idx])
        call BlzFrameSetText(IC_DetailCost, IC_Cost(idx) + "   |   " + IC_Location[idx])
        set i = 0
        loop
            exitwhen i == 8
            call BlzFrameSetVisible(IC_Link[i],false)
            set IC_LinkItem[i] = 0
            set i = i + 1
        endloop
        call BlzFrameSetText(IC_TabButton[0], "Overview")
        call BlzFrameSetText(IC_TabButton[1], "Abilities")
        call BlzFrameSetText(IC_TabButton[2], "Recipe")
        if IC_Tab == 0 then
            call BlzFrameSetText(IC_TabButton[0], "|cffffcc00Overview|r")
            set text = IC_Description[idx]
            if IC_Note[idx] != "" then
                set text = text + "\n\n" + IC_Note[idx]
            endif
            call BlzFrameSetText(IC_Body, IC_Paginate(text))
        elseif IC_Tab == 1 then
            call BlzFrameSetText(IC_TabButton[1], "|cffffcc00Abilities|r")
            call BlzFrameSetText(IC_Body, IC_Paginate(IC_Stats[idx]))
        else
            call BlzFrameSetText(IC_TabButton[2], "|cffffcc00Recipe|r")
            set IC_TextPages = 1
            set section = IC_Recipe[idx]
            if section == 0 then
                call BlzFrameSetText(IC_Body,"This item is bought directly or granted as a starting item.\nSee Overview for its effects and restrictions.")
            else
                call BlzFrameSetText(IC_Body,"Combine the components below. Click any icon for its details.\nTotal acquisition cost: " + I2S(IC_Total[idx]) + " gold.  Result is shown last.")
                set i = 0
                loop
                    exitwhen i >= IC_IngredientCount[section]+1 or i == 8
                    if i == IC_IngredientCount[section] then
                        set j = IC_Result[section]
                    else
                        set j = IC_Ingredients[section*8+i]
                    endif
                    set IC_LinkItem[i] = j
                    call BlzFrameSetTexture(IC_LinkArt[i],IC_Icon[j],0,true)
                    if i == IC_IngredientCount[section] then
                        call BlzFrameSetText(IC_LinkLabel[i],"|cffffcc00Result|r\n"+IC_Short(IC_Name[j]))
                    else
                        call BlzFrameSetText(IC_LinkLabel[i],IC_Short(IC_Name[j])+"\n|cffffcc00"+IC_Cost(j)+"|r")
                    endif
                    call BlzFrameSetVisible(IC_Link[i],true)
                    set i = i + 1
                endloop
            endif
        endif
        call BlzFrameSetText(IC_Footer,"Page " + I2S(IC_TextPage+1) + " / " + I2S(IC_TextPages))
        call BlzFrameSetEnable(IC_Previous,IC_TextPage > 0)
        call BlzFrameSetEnable(IC_Next,IC_TextPage+1 < IC_TextPages)
    endif
    if not IC_Ready then
        call BlzFrameSetText(IC_Footer,"Loading item details " + I2S(IC_LoadIndex-1) + " / " + I2S(IC_Count))
    endif
endfunction

function IC_Select takes integer idx returns nothing
    if idx > 0 then
        if IC_HistoryCount < 32 then
            set IC_History[IC_HistoryCount] = IC_Selected
            set IC_HistoryCount = IC_HistoryCount + 1
        endif
        set IC_Selected = idx
        set IC_Tab = 0
        set IC_TextPage = 0
    endif
endfunction

function IC_Click takes nothing returns nothing
    local framehandle f = BlzGetTriggerFrame()
    local integer i = 0
    if GetLocalPlayer() == GetTriggerPlayer() then
        call BlzFrameSetEnable(f,false)
        call BlzFrameSetEnable(f,true)
        call BlzFrameSetFocus(f,false)
        if f == IC_Close then
            set FFUI_ItemsOpen = false
            call BlzFrameSetVisible(FFUI_Items,false)
        elseif f == IC_Search or f == IC_SearchButton then
            set IC_Query = StringCase(IC_Plain(BlzFrameGetText(IC_Search)),false)
            set IC_Selected = 0
            set IC_HistoryCount = 0
            set IC_Page = 0
            set IC_TextPage = 0
        elseif f == IC_Back then
            if IC_Selected > 0 and IC_HistoryCount > 0 then
                set IC_HistoryCount = IC_HistoryCount - 1
                set IC_Selected = IC_History[IC_HistoryCount]
            else
                set IC_Selected = 0
                set IC_Query = ""
                set IC_Page = 0
                call BlzFrameSetText(IC_Search,"")
            endif
            set IC_Tab = 0
            set IC_TextPage = 0
        elseif f == IC_Previous or f == IC_Next then
            if IC_Selected > 0 then
                if f == IC_Previous then
                    set IC_TextPage = IMaxBJ(0,IC_TextPage-1)
                else
                    set IC_TextPage = IMinBJ(IC_TextPages-1,IC_TextPage+1)
                endif
            elseif f == IC_Previous then
                set IC_Page = IMaxBJ(0,IC_Page-1)
            else
                set IC_Page = IC_Page+1
            endif
        else
            loop
                exitwhen i == 3
                if f == IC_TabButton[i] then
                    set IC_Tab = i
                    set IC_TextPage = 0
                endif
                set i = i + 1
            endloop
            set i = 0
            loop
                exitwhen i == 24
                if f == IC_Tile[i] then
                    call IC_Select(IC_TileItem[i])
                endif
                set i = i + 1
            endloop
            set i = 0
            loop
                exitwhen i == 8
                if f == IC_Link[i] then
                    call IC_Select(IC_LinkItem[i])
                endif
                set i = i + 1
            endloop
        endif
        call IC_Render()
    endif
    set f = null
endfunction

function IC_ReadAbility takes ability a returns string
    local integer id = BlzGetAbilityId(a)
    local integer count = LoadInteger(IC_Data,id,-1)
    local integer i = 0
    local integer field
    local real value
    local string label
    local string out = IC_Plain(GetObjectName(id)) + "\n"
    loop
        exitwhen i >= count
        set field = LoadInteger(IC_Data,id,i*4)
        if LoadInteger(IC_Data,id,i*4+1) == 1 then
            set value = I2R(BlzGetAbilityIntegerLevelField(a,ConvertAbilityIntegerLevelField(field),0))
        else
            set value = BlzGetAbilityRealLevelField(a,ConvertAbilityRealLevelField(field),0)
        endif
        if value != 0 then
            set label = LoadStr(IC_Data,id,i*4+2)
            if field == 'Uau2' and not BlzGetAbilityBooleanLevelField(a,ConvertAbilityBooleanLevelField('Uau3'),0) then
                set out = out + "Health regeneration per second: " + IC_Number(value) + "\n"
            elseif field == 'Hab1' and not BlzGetAbilityBooleanLevelField(a,ConvertAbilityBooleanLevelField('Hab2'),0) then
                set out = out + "Mana regeneration per second: " + IC_Number(value) + "\n"
            elseif LoadBoolean(IC_Data,id,i*4+3) then
                set out = out + label + ": " + IC_Number(value*100) + "%\n"
            else
                set out = out + label + ": " + IC_Number(value) + "\n"
            endif
        endif
        set i = i + 1
    endloop
    if count == 0 then
        set out = out + IC_Plain(BlzGetAbilityExtendedTooltip(id,0)) + "\n"
    endif
    return out
endfunction

function IC_Hydrate takes nothing returns nothing
    local integer stop = IMinBJ(IC_LoadIndex+2,IC_Count+1)
    local integer i
    local item sample
    local ability a
    local string text
    loop
        exitwhen IC_LoadIndex >= stop
        set i = IC_LoadIndex
        set sample = CreateItem(IC_Id[i],0,0)
        call SetItemVisible(sample,false)
        set IC_Name[i] = IC_Plain(GetItemName(sample))
        set IC_Icon[i] = BlzGetItemIconPath(sample)
        set text = BlzGetItemExtendedTooltip(sample)
        if text == "" or text == null then
            set text = BlzGetItemDescription(sample)
        endif
        if text != "" and text != null and not IC_Matches(text,"<") then
            set IC_Description[i] = text
        endif
        if IC_Spell[i] != 0 then
            set text = BlzGetAbilityExtendedTooltip(IC_Spell[i],0)
            if text != "" and text != null and not IC_Matches(text,"<") then
                set IC_Description[i] = "Teaches " + IC_Name[i] + ".\n\n" + text
            endif
        else
            set text = ""
            set i = 0
            loop
                set a = BlzGetItemAbilityByIndex(sample,i)
                exitwhen a == null or i >= 16
                set text = text + IC_ReadAbility(a) + "\n"
                set i = i + 1
            endloop
            if text != "" then
                set IC_Stats[IC_LoadIndex] = text + "\nValues shown are for level 1. See Overview for scripted effects and restrictions."
            endif
        endif
        call RemoveItem(sample)
        set IC_LoadIndex = IC_LoadIndex + 1
    endloop
    if IC_LoadIndex > IC_Count then
        set IC_Ready = true
        call PauseTimer(IC_LoadTimer)
        call DestroyTimer(IC_LoadTimer)
        set IC_LoadTimer = null
    endif
    // This updates presentation only; each client keeps its own open page.
    if FFUI_ItemsOpen and not FFUI_Hidden then
        call IC_Render()
    endif
    set sample = null
    set a = null
endfunction

function IC_Label takes framehandle parent, real x, real y, real w, real h, string text returns framehandle
    local framehandle f = BlzCreateFrameByType("TEXT","",parent,"",0)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,parent,FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetText(f,text)
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_LEFT)
    call BlzFrameSetScale(f,0.85)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function IC_Button takes framehandle parent, trigger click, real x, real y, real w, real h, string text returns framehandle
    local framehandle f = BlzCreateFrame("ScriptDialogButton",parent,0,0)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,parent,FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetSize(f,w,h)
    call BlzFrameSetText(f,text)
    call BlzTriggerRegisterFrameEvent(click,f,FRAMEEVENT_CONTROL_CLICK)
    return f
endfunction

function IC_Art takes framehandle parent, real x, real y, real size returns framehandle
    local framehandle f = BlzCreateFrameByType("BACKDROP","",parent,"",0)
    call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,parent,FRAMEPOINT_TOPLEFT,x,-y)
    call BlzFrameSetSize(f,size,size)
    call BlzFrameSetEnable(f,false)
    return f
endfunction

function IC_Init takes nothing returns nothing
    local trigger click = CreateTrigger()
    local integer i = 0
    local real x
    local real y
    call IC_LoadData()
    call BlzFrameSetSize(FFUI_Items,0.740,0.400)
    call BlzFrameClearAllPoints(FFUI_Items)
    call BlzFrameSetAbsPoint(FFUI_Items,FRAMEPOINT_TOPLEFT,0.030,0.575)
    set IC_Header = IC_Label(FFUI_Items,0.020,0.018,0.160,0.025,"|cffffcc00Items|r")
    call BlzFrameSetScale(IC_Header,1.25)
    set IC_Search = BlzCreateFrame("EscMenuEditBoxTemplate",FFUI_Items,0,0)
    call BlzFrameSetPoint(IC_Search,FRAMEPOINT_TOPLEFT,FFUI_Items,FRAMEPOINT_TOPLEFT,0.285,-0.014)
    call BlzFrameSetSize(IC_Search,0.190,0.028)
    call BlzFrameSetText(IC_Search,"")
    call BlzTriggerRegisterFrameEvent(click,IC_Search,FRAMEEVENT_EDITBOX_ENTER)
    set IC_SearchButton = IC_Button(FFUI_Items,click,0.480,0.014,0.075,0.028,"Search")
    set IC_Back = IC_Button(FFUI_Items,click,0.559,0.014,0.075,0.028,"Shops")
    set IC_Close = IC_Button(FFUI_Items,click,0.638,0.014,0.080,0.028,"Close")
    set IC_Browse = BlzCreateFrameByType("FRAME","",FFUI_Items,"",0)
    call BlzFrameSetAllPoints(IC_Browse,FFUI_Items)
    set IC_Detail = BlzCreateFrameByType("FRAME","",FFUI_Items,"",0)
    call BlzFrameSetAllPoints(IC_Detail,FFUI_Items)
    loop
        exitwhen i == 2
        set IC_SectionArt[i] = IC_Art(IC_Browse,0.022,0.052+i*0.153,0.038)
        set IC_SectionTitle[i] = IC_Label(IC_Browse,0.070,0.062+i*0.153,0.610,0.026,"")
        call BlzFrameSetScale(IC_SectionTitle[i],1.0)
        set i = i + 1
    endloop
    set i = 0
    loop
        exitwhen i == 24
        set x = 0.022+ModuloInteger(i,6)*0.116
        set y = 0.097+(ModuloInteger(i,12)/6)*0.052+(i/12)*0.153
        set IC_Tile[i] = IC_Button(IC_Browse,click,x,y,0.112,0.049,"")
        set IC_TileArt[i] = IC_Art(IC_Tile[i],0.004,0.006,0.032)
        set IC_TileLabel[i] = IC_Label(IC_Tile[i],0.040,0.006,0.068,0.040,"")
        call BlzFrameSetScale(IC_TileLabel[i],0.65)
        set i = i + 1
    endloop
    set IC_DetailIcon = IC_Art(IC_Detail,0.025,0.060,0.060)
    set IC_DetailName = IC_Label(IC_Detail,0.100,0.062,0.600,0.028,"")
    call BlzFrameSetScale(IC_DetailName,1.15)
    set IC_DetailCost = IC_Label(IC_Detail,0.100,0.095,0.600,0.030,"")
    set IC_TabButton[0] = IC_Button(IC_Detail,click,0.025,0.132,0.125,0.027,"Overview")
    set IC_TabButton[1] = IC_Button(IC_Detail,click,0.156,0.132,0.125,0.027,"Abilities")
    set IC_TabButton[2] = IC_Button(IC_Detail,click,0.287,0.132,0.125,0.027,"Recipe")
    set IC_Body = IC_Label(IC_Detail,0.025,0.173,0.685,0.174,"")
    set i = 0
    loop
        exitwhen i == 8
        set x = 0.025+ModuloInteger(i,4)*0.174
        set y = 0.225+(i/4)*0.060
        set IC_Link[i] = IC_Button(IC_Detail,click,x,y,0.167,0.054,"")
        set IC_LinkArt[i] = IC_Art(IC_Link[i],0.005,0.008,0.035)
        set IC_LinkLabel[i] = IC_Label(IC_Link[i],0.045,0.008,0.118,0.040,"")
        call BlzFrameSetScale(IC_LinkLabel[i],0.75)
        set i = i + 1
    endloop
    set IC_Previous = IC_Button(FFUI_Items,click,0.020,0.359,0.083,0.027,"Previous")
    set IC_Next = IC_Button(FFUI_Items,click,0.637,0.359,0.083,0.027,"Next")
    set IC_Footer = IC_Label(FFUI_Items,0.113,0.367,0.510,0.020,"")
    call BlzFrameSetTextAlignment(IC_Footer,TEXT_JUSTIFY_TOP,TEXT_JUSTIFY_CENTER)
    call TriggerAddAction(click,function IC_Click)
    call IC_Render()
    set IC_LoadTimer = CreateTimer()
    call TimerStart(IC_LoadTimer,0.03,true,function IC_Hydrate)
    set click = null
endfunction
// END ITEMS CATALOG RUNTIME
