# SF_Test1.7_v16

- Raised the player zoom limit from 4000 to 4800.
- The zoom system now sets `CAMERA_FIELD_FARZ` to 10000 so distant terrain is not clipped into black rectangles.
- Moved the black terrain-fog transition from 3000-10000 to 8000-10000 so the full playable area remains clear at wide zoom.
- Both JASS parsers pass.
- Source and packed-script SHA256: `C4B017AFFA840291F9D1155CAD70BEFDD2C863CB0A6FDA3C95B784020CB0E0AA`.
- Release and delivered-map SHA256: `10CFECC69413D0E81FA9DA51461118D2ED972B472BBB68C67D4D86B44DFD019C`.
- All 1,203 non-script files are byte-identical to v15.
- In-game visual testing is required at `-zoom 4800`, both from a base and from map center.
