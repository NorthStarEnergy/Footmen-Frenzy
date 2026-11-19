function PF_AlignNumber takes framehandle f returns nothing
    call BlzFrameSetTextAlignment(f,TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_RIGHT)
    call BlzFrameSetFont(f,"CasinoUI\\Bold.ttf",0.013,0)
endfunction

function PF_CreateProfile takes trigger t returns nothing
    local integer i = 0
    local real y
    local framehandle f
    set PF_sectionTitle = PF_Text(-0.182,0.084,0.54,0.040,0.022)
    call BlzFrameSetFont(PF_sectionTitle,"CasinoUI\\Bold.ttf",0.021,0)
    set PF_col[0] = PF_Text(-0.174,0.131,0.306,0.023,0.011)
    set PF_col[1] = PF_Text(0.136,0.131,0.106,0.023,0.011)
    set PF_col[2] = PF_Text(0.249,0.131,0.108,0.023,0.011)
    loop
        exitwhen i >= 3
        call BlzFrameSetTextColor(PF_col[i],BlzConvertColor(255,232,202,146))
        if i > 0 then
            call BlzFrameSetTextAlignment(PF_col[i],TEXT_JUSTIFY_MIDDLE,TEXT_JUSTIFY_RIGHT)
        endif
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 11
        set PF_menu[i] = PF_Button(t,-0.366,0.091+I2R(i)*0.041,0.158)
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 9
        set y = 0.162+I2R(i)*0.042
        set f = BlzCreateFrameByType("BACKDROP","",PF_root,"",i)
        call BlzFrameSetPoint(f,FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.182,-y)
        call BlzFrameSetSize(f,0.548,0.038)
        call BlzFrameSetTexture(f,"ReplaceableTextures\\TeamColor\\TeamColor08.blp",0,true)
        call BlzFrameSetVertexColor(f,BlzConvertColor(80,149,147,135))
        set PF_stripe[i] = f
        set PF_icon[i] = BlzCreateFrameByType("BACKDROP","",PF_root,"",i)
        call BlzFrameSetPoint(PF_icon[i],FRAMEPOINT_TOPLEFT,PF_root,FRAMEPOINT_TOP,-0.174,-y-0.006)
        call BlzFrameSetSize(PF_icon[i],0.026,0.026)
        set PF_line[i] = PF_Text(-0.174,y,0.306,0.038,0.013)
        set PF_value[i] = PF_Text(0.136,y,0.106,0.038,0.013)
        set PF_extra[i] = PF_Text(0.249,y,0.108,0.038,0.013)
        call PF_AlignNumber(PF_value[i])
        call PF_AlignNumber(PF_extra[i])
        call BlzFrameSetTextColor(PF_extra[i],BlzConvertColor(255,232,218,190))
        set i = i+1
    endloop
    set f = null
endfunction

function PF_RenderNavigation takes nothing returns nothing
    local integer i = 0
    local integer section
    loop
        exitwhen i >= 6
        call BlzFrameSetVisible(PF_tab[i],PF_results)
        if PF_results then
            call BlzFrameSetText(PF_tab[i],PF_tabName[10+i])
            call BlzFrameSetEnable(PF_tab[i],i != PF_section)
        endif
        set i = i+1
    endloop
    set i = 0
    loop
        exitwhen i >= 11
        call BlzFrameSetVisible(PF_menu[i],not PF_results)
        if not PF_results then
            set section = PF_menuOrder[i]
            if section == PF_section then
                call BlzFrameSetText(PF_menu[i],"|cffffd784>  "+PF_sectionName[section]+"|r")
            else
                call BlzFrameSetText(PF_menu[i],PF_sectionName[section])
            endif
        endif
        set i = i+1
    endloop
    call BlzFrameSetVisible(PF_sectionTitle,not PF_results)
    set i = 0
    loop
        exitwhen i >= 3
        call BlzFrameSetVisible(PF_col[i],not PF_results)
        set i = i+1
    endloop
endfunction
