// ==== globals (2645-2664) ====
constant string zoom__gFileName= "FFR_Zoom.txt"
integer zoom__gMinDistance= 1400
integer zoom__gMaxDistance= 6000
framehandle zoom__sliderLabel= null
framehandle zoom__lockButton= null
boolean array zoom__sliderLocked
// Vertical zoom column: lock button on top, north-south track below it, readout at the bottom.
// EscMenuSliderTemplate is horizontal-only, so the track is a backdrop groove plus a stack of
// invisible click areas, with a backdrop thumb marking the current level.
framehandle zoom__track= null
framehandle zoom__thumb= null
framehandle array zoom__segment
constant integer zoom__gSegmentCount= 20
constant real zoom__gColumnX= 0.143
constant real zoom__gTrackBottom= 0.07475
constant real zoom__gTrackSpan= 0.0855
constant real zoom__gSegmentHeight= 0.0045
// Map fog is black and ends at 5000, so anything beyond that renders as a black screen.
constant real zoom__gFogZStart= 3000.00
constant real zoom__gFogZEnd= 5000.00

// ==== zoom scope (16092-16361) ====

//===========================================================================

// The map's terrain fog is opaque black from 5000 units out, so at high zoom levels the whole
// visible world sits inside the fog and the screen goes black. Push the fog plane (and the far
// clip plane behind it) out with the camera, leaving the close-up look untouched.
// only call ApplyFog from local context!
function zoom__ApplyFog takes integer cameraDistance returns nothing
    local real distance= I2R(cameraDistance)
    local real zStart= zoom__gFogZStart
    local real zEnd= zoom__gFogZEnd
    local real farZ= 10000.00
    if ( distance * 1.20 > zStart ) then
        set zStart=distance * 1.20
    endif
    if ( distance * 2.20 > zEnd ) then
        set zEnd=distance * 2.20
    endif
    if ( zEnd + 2000.00 > farZ ) then
        set farZ=zEnd + 2000.00
    endif
    call SetCameraField(CAMERA_FIELD_FARZ, farZ, 0.00)
    call SetTerrainFogEx(0, zStart, zEnd, 0.50, 0.00, 0.00, 0.00)
endfunction

// only call Zoom from local context!
function zoom__Zoom takes integer cameraDistance,boolean withMessaging returns integer
    local boolean wasValid= false
    local integer previousCameraDistance= R2I(GetCameraField(CAMERA_FIELD_TARGET_DISTANCE))
    if ( previousCameraDistance == cameraDistance ) then
        if ( withMessaging ) then
            call DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "Already at target zoom level")
        endif
    else

        if ( cameraDistance > zoom__gMaxDistance ) then
            set cameraDistance=zoom__gMaxDistance
        elseif ( cameraDistance < zoom__gMinDistance ) then
            set cameraDistance=zoom__gMinDistance
        else
            set wasValid=true
        endif

        if ( withMessaging and not ( wasValid ) ) then
            call DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "Valid zoom range: " + I2S(zoom__gMinDistance) + " up to " + I2S(zoom__gMaxDistance))
        endif
    
        if ( withMessaging ) then
            call DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "New zoom level: " + I2S(cameraDistance))
        endif
        call SetCameraField(CAMERA_FIELD_TARGET_DISTANCE, cameraDistance, 0.00)
    endif
    call zoom__ApplyFog(cameraDistance)
    return cameraDistance
endfunction

function zoom__UpdateSliderLabel takes integer cameraDistance returns nothing
    call BlzFrameSetText(zoom__sliderLabel, I2S(cameraDistance))
endfunction

// Bottom of the track is the closest zoom, top is the farthest.
function zoom__DistanceToFraction takes integer cameraDistance returns real
    local real span= I2R(zoom__gMaxDistance - zoom__gMinDistance)
    local real fraction
    if ( span <= 0.00 ) then
        return 0.00
    endif
    set fraction=I2R(cameraDistance - zoom__gMinDistance) / span
    if ( fraction < 0.00 ) then
        set fraction=0.00
    elseif ( fraction > 1.00 ) then
        set fraction=1.00
    endif
    return fraction
endfunction

function zoom__UpdateThumb takes integer cameraDistance returns nothing
    call BlzFrameSetAbsPoint(zoom__thumb, FRAMEPOINT_CENTER, zoom__gColumnX, zoom__gTrackBottom + zoom__DistanceToFraction(cameraDistance) * zoom__gTrackSpan)
endfunction

function zoom__UpdateLockButton takes player p returns nothing
    local integer playerId= GetPlayerId(p)
    local integer i= 0
    if ( GetLocalPlayer() == p ) then
        loop
        exitwhen i >= zoom__gSegmentCount
            call BlzFrameSetEnable(zoom__segment[i], not zoom__sliderLocked[playerId])
            set i=i + 1
        endloop
        if ( zoom__sliderLocked[playerId] ) then
            // 0xFFFF3030 red X, greyed-out thumb.
            call BlzFrameSetText(zoom__lockButton, "|cffff3030X|r")
            call BlzFrameSetVertexColor(zoom__thumb, -8355712)
        else
            // 0xFFFFCC00 gold thumb.
            call BlzFrameSetText(zoom__lockButton, "|cffffffffX|r")
            call BlzFrameSetVertexColor(zoom__thumb, -13312)
        endif
    endif
endfunction

function zoom__handleLockButton takes nothing returns nothing
    local player p= GetTriggerPlayer()
    local integer playerId= GetPlayerId(p)
    set zoom__sliderLocked[playerId]=not zoom__sliderLocked[playerId]
    call zoom__UpdateLockButton(p)
    if ( zoom__sliderLocked[playerId] ) then
        call DisplayTextToPlayer(p, 0, 0, "Zoom slider locked. Click the X again to unlock it.")
    else
        call DisplayTextToPlayer(p, 0, 0, "Zoom slider unlocked.")
    endif
    set p=null
endfunction

function zoom__Save takes integer cameraDistance returns nothing
    local integer file= s__File_open(zoom__gFileName)
    call s__File_write(file,I2S(cameraDistance))
    call s__File_close(file)
endfunction

// Frame events are local UI events. Camera, frame, and file-cache writes remain local here.
// Segment 0 is the top of the track (farthest zoom), the last segment is the bottom (closest).
function zoom__handleSegment takes nothing returns nothing
    local player p= GetTriggerPlayer()
    local integer playerId= GetPlayerId(p)
    local framehandle clicked= BlzGetTriggerFrame()
    local integer i= 0
    local integer cameraDistance
    if ( GetLocalPlayer() == p and not zoom__sliderLocked[playerId] ) then
        loop
            exitwhen i >= zoom__gSegmentCount
            if ( zoom__segment[i] == clicked ) then
                set cameraDistance=zoom__gMaxDistance - R2I(I2R(zoom__gMaxDistance - zoom__gMinDistance) * I2R(i) / I2R(zoom__gSegmentCount - 1) + 0.50)
                set cameraDistance=zoom__Zoom(cameraDistance , false)
                call zoom__UpdateSliderLabel(cameraDistance)
                call zoom__UpdateThumb(cameraDistance)
                call zoom__Save(cameraDistance)
                exitwhen true
            endif
            set i=i + 1
        endloop
    endif
    set clicked=null
    set p=null
endfunction

function zoom__CreateSlider takes nothing returns nothing
    local framehandle gameUI= BlzGetOriginFrame(ORIGIN_FRAME_GAME_UI, 0)
    local trigger segmentTrigger= CreateTrigger()
    local trigger lockTrigger= CreateTrigger()
    local integer cameraDistance= R2I(GetCameraField(CAMERA_FIELD_TARGET_DISTANCE))
    local integer i= 0
    // Stack (top-to-bottom): X lock button, north-south track, zoom readout.
    // Positioned directly left of the ping/formation/creep/colors buttons.
    set zoom__lockButton=BlzCreateFrameByType("GLUETEXTBUTTON", "SoloFootsZoomLock", gameUI, "ScriptDialogButton", 0)
    call BlzFrameSetAbsPoint(zoom__lockButton, FRAMEPOINT_CENTER, zoom__gColumnX, 0.1740)
    call BlzFrameSetSize(zoom__lockButton, 0.016, 0.016)
    call BlzFrameSetText(zoom__lockButton, "|cffffffffX|r")
    set zoom__track=BlzCreateFrameByType("BACKDROP", "SoloFootsZoomTrack", gameUI, "", 0)
    call BlzFrameSetTexture(zoom__track, "Black32.blp", 0, true)
    call BlzFrameSetAbsPoint(zoom__track, FRAMEPOINT_CENTER, zoom__gColumnX, zoom__gTrackBottom + zoom__gTrackSpan / 2.00)
    call BlzFrameSetSize(zoom__track, 0.006, zoom__gTrackSpan + zoom__gSegmentHeight)
    set zoom__thumb=BlzCreateFrameByType("BACKDROP", "SoloFootsZoomThumb", gameUI, "", 0)
    call BlzFrameSetTexture(zoom__thumb, "Black32.blp", 0, true)
    call BlzFrameSetSize(zoom__thumb, 0.014, 0.004)
    call BlzFrameSetVertexColor(zoom__thumb, -13312)
    loop
        exitwhen i >= zoom__gSegmentCount
        // Invisible click areas laid over the track; clicking one jumps to that zoom level.
        set zoom__segment[i]=BlzCreateFrameByType("GLUEBUTTON", "SoloFootsZoomSegment", gameUI, "", i)
        call BlzFrameSetAbsPoint(zoom__segment[i], FRAMEPOINT_CENTER, zoom__gColumnX, zoom__gTrackBottom + zoom__gTrackSpan - I2R(i) * zoom__gSegmentHeight)
        call BlzFrameSetSize(zoom__segment[i], 0.020, zoom__gSegmentHeight)
        call BlzTriggerRegisterFrameEvent(segmentTrigger, zoom__segment[i], FRAMEEVENT_CONTROL_CLICK)
        set i=i + 1
    endloop
    set zoom__sliderLabel=BlzCreateFrameByType("TEXT", "SoloFootsZoomLabel", gameUI, "", 0)
    call BlzFrameSetAbsPoint(zoom__sliderLabel, FRAMEPOINT_CENTER, zoom__gColumnX, 0.0620)
    call BlzFrameSetTextAlignment(zoom__sliderLabel, TEXT_JUSTIFY_MIDDLE, TEXT_JUSTIFY_CENTER)
    call BlzFrameSetScale(zoom__sliderLabel, 0.65)
    call TriggerAddAction(segmentTrigger, function zoom__handleSegment)
    call BlzTriggerRegisterFrameEvent(lockTrigger, zoom__lockButton, FRAMEEVENT_CONTROL_CLICK)
    call TriggerAddAction(lockTrigger, function zoom__handleLockButton)
    call zoom__UpdateSliderLabel(cameraDistance)
    call zoom__UpdateThumb(cameraDistance)
    set gameUI=null
    set segmentTrigger=null
    set lockTrigger=null
endfunction

//===========================================================================

// only call RestoreFromFile from local context!
function zoom__RestoreFromFile takes nothing returns nothing
    local integer file= s__File_open(zoom__gFileName)
    local string input= (s__File_readEx((file),false)) // INLINED!!
    local integer cameraDistance= S2I(SubString(input, 0, 4))
    call s__File_close(file)
    call zoom__Zoom(cameraDistance , false)
endfunction

//===========================================================================

function zoom__handleChatCommand takes nothing returns nothing
    local string commandText= GetEventPlayerChatString()
    local string cameraDistanceStr
    local integer cameraDistance= 0
    if ( SubString(commandText, 0, 3) == "-z " ) then
        set cameraDistanceStr=SubString(commandText, 3, StringLength(commandText))
    else
        set cameraDistanceStr=SubString(commandText, 6, StringLength(commandText))
    endif
    if ( GetLocalPlayer() == GetTriggerPlayer() ) then
        if ( cameraDistanceStr != " " ) then
            set cameraDistance=S2I(cameraDistanceStr)
        endif
        if ( cameraDistance == 0 ) then
            call DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "Invalid zoom command usage. Example: \"-z 2500\" or \"-zoom 2500\"")
        else
            set cameraDistance=zoom__Zoom(cameraDistance , true)
            call zoom__UpdateThumb(cameraDistance)
            call zoom__UpdateSliderLabel(cameraDistance)
            call zoom__Save(cameraDistance)
        endif
    endif
endfunction

function zoom__handleInfoChatCommand takes nothing returns nothing
    if ( GetLocalPlayer() == GetTriggerPlayer() ) then
        call DisplayTextToPlayer(GetLocalPlayer(), 0, 0, "Current zoom level: " + I2S(R2I(GetCameraField(CAMERA_FIELD_TARGET_DISTANCE))))
    endif
endfunction

function zoom_RestoreFromCacheForPlayer takes player p returns nothing
    if ( GetLocalPlayer() == p ) then
        call zoom__RestoreFromFile()
    endif
endfunction

function zoom_RestoreForAllPlayersFromCache takes nothing returns nothing
    local integer i= 0
    loop
    exitwhen i >= 24
        if ( GetPlayerSlotState(Player(i)) == PLAYER_SLOT_STATE_PLAYING ) then
            if ( GetLocalPlayer() == Player(i) ) then
                call zoom__RestoreFromFile()
            endif
        endif
        set i=i + 1
    endloop
endfunction

function zoom_Init takes nothing returns nothing
    local integer i= 0
    local trigger setTrigger= CreateTrigger()
    local trigger infoTrigger= CreateTrigger()
    loop
    exitwhen i >= 24
        call TriggerRegisterPlayerChatEvent(setTrigger, Player(i), "-zoom ", false)
        call TriggerRegisterPlayerChatEvent(setTrigger, Player(i), "-z ", false)
        call TriggerRegisterPlayerChatEvent(infoTrigger, Player(i), "-zoom", true)
        call TriggerRegisterPlayerChatEvent(infoTrigger, Player(i), "-z", true)
        set i=i + 1
    endloop
    call TriggerAddAction(setTrigger, function zoom__handleChatCommand)
    call TriggerAddAction(infoTrigger, function zoom__handleInfoChatCommand)
    call zoom_RestoreForAllPlayersFromCache()
    call zoom__CreateSlider()
endfunction

// scope zoom ends
