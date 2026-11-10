# Building Solo Foots

## Do not open the map in World Editor

`war3map.wtg` and `war3map.wct` no longer describe the script the map actually runs.
Every custom system lives only in the compiled `war3map.j`:

| system | references in `war3map.wtg` / `war3map.wct` |
| --- | --- |
| `SF_PageTargetForSelector` | 0 |
| `SoloFootsSpawnEarlyWave` | 0 |
| `SoloFootsMassSpawnTick` | 0 |

If the map is opened in World Editor and saved, WE regenerates `war3map.j` from the
trigger source and every one of those systems is silently destroyed. There is no warning
and the map still builds — it just quietly loses its gameplay.

Either treat `src/war3map.j` as authoritative and never round-trip the map, or budget the
work to rebuild the custom systems as GUI triggers so the two representations agree again.
Right now the first is in force.

## Source of truth

| file | contents |
| --- | --- |
| `src/war3map.j` | gameplay script |
| `src/war3map.w3u` | custom unit object data |
| `src/war3map.w3t` | custom item object data |
| `src/war3map.wts` | trigger strings, including the lobby map name |

`src/war3map.w3u` and `src/war3map.w3t` are **generated**, not hand-edited. Both patch
scripts read the clean `roundtrip/SF_Test1.7_v73/files/` baseline and write into `src/`,
so they can be re-run at any time and always produce the same bytes:

```bash
python tools/PatchPageSelectorUnits.py
python tools/PatchRodItems.py
```

## Packing

`tools/MpqAdd` replaces a file inside an existing map. Its `--replace` mode removes the
old entry but does not add the new one, so a replacement is two steps:

```bash
MpqAdd --replace in.w3x payload war3map.w3u stage.w3x
MpqAdd stage.w3x payload war3map.w3u out.w3x
```

## Verification gate

Run all of these before delivering a build. The first two are the ones that matter — a
map can pass the JASS parser and still black-screen before the loading bar if the object
tables are malformed.

1. Object tables parse to the last byte: `w3u`, `w3t`, `w3a`, `w3h`, `w3q`, `w3b`, `w3d`.
   Both patch scripts do this internally; `PatchPageSelectorUnits.py` exposes it as `check()`.
2. Extract the packed map and diff it file-by-file against the previous build. Only the
   files you meant to change should differ.
3. `tools/bin/JassParseCheck/JassParseCheck.exe src/war3map.j`
4. Load it in Warcraft III and play a game.

## Object data format

A `.w3u` / `.w3t` / `.w3a` modification is:

```
id(4)  type(4)  [level(4) data(4) — w3a/w3d/w3q only]  value(4 or cstring)  end-marker(4)
```

The trailing **end-of-modification marker** is the part that is easy to miss. Omitting it
when walking the list desynchronises the cursor; omitting it when writing a modification
leaves the record 4 bytes short. Either one corrupts the table, and Warcraft III parses
object data *before* it draws the loading screen — so the symptom is a black screen after
the lobby countdown with no error message. This cost builds v73 through v80.
