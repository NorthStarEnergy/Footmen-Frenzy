# 799X Items catalog

The delivered combined build is `Reforged_Footmen_Frenzy_v7.9.9X-T44.w3x`.
See `integration.json` for its SHA256, baseline identity, and checks.

It includes the latest T43 boots/amulet changes, T42 balance changes, the Stats / Hotkeys / Items toolbar, and the global red/green UI toggle. Two different T43 builds existed during development; filenames alone are not sufficient to identify a baseline.

## Player interface

- 225 entries, grouped into 18 shop/category groups and 23 displayed sections.
- Existing shop artwork above each section; clickable item icons below it.
- Search by item or shop name, paged browsing, and a Back history.
- Overview, Abilities, and Recipe detail tabs. Long descriptions are paginated.
- All 17 live recipes link to ingredients and the crafted result and show total acquisition cost.
- The current amulet/boots substitution rule is included.
- Custom Hero spell purchases and starting/alternative components are included.
- The global hide/show button preserves the current catalog page.
- The catalog is informational; it never buys an item or changes inventory.

Actual shop screenshots have deliberately not been captured. Shop header textures can be replaced later through `IC_SectionIcon` / generated shop metadata. The original item and shop artwork remains in the map/game archives.

## Integrating another agent's version

Always start from the newest complete 799X map and verify its hash. Do not replace its script with the root checkout's historical v85 source, or with the earlier toolbar-only T43 script.

From the repository root, using the locally configured Python executable:

```powershell
python tools/build_799x_items_catalog.py --baseline '<current-map.w3x>' --workspace build/items-catalog/<new-stage> --name 'Reforged_Footmen_Frenzy_v7.9.9X-T<next>.w3x'
python tools/test_799x_items_catalog.py build/items-catalog/<new-stage>
& ./build/items-catalog/<new-stage>/Build-Map.ps1 -Project 799x -Name 'Reforged_Footmen_Frenzy_v7.9.9X-T<next>.w3x' -Python '<python.exe>'
```

`build_799x_items_catalog.py` applies the toolbar when absent and replaces only the marked catalog blocks when already present. It regenerates stock, recipes, descriptions, prices, and native ability-field descriptors from the new baseline. Unexpected integration anchors or unknown tooltip references fail preparation rather than silently discarding changes.

The staged `Build-Map.ps1` checks the installed baseline's filename **and** SHA256 immediately before installation. If another agent delivered a newer map, regenerate on that map with a new output version. Keep the failed stage as evidence; do not bypass the guard.

Use the resulting complete map as the baseline for subsequent agents. Preserve all other gameplay functions and object files. Current release binaries and images belong in Git LFS if committing; `build/` and `tools.local.json` remain untracked. No GitHub publication is performed by these tools.

## Source layout

- `globals.j`: catalog-only state and frame handles.
- `runtime.j`: rendering, navigation, native item reads, and event handlers.
- `tools/custom_ui_toolbar.py`: additive toolbar integration.
- `tools/build_799x_items_catalog.py`: current-map data extraction and isolated preparation.
- `tools/test_799x_items_catalog.py`: source-executed JASS behavior tests with mocked natives.
- `build/items-catalog/final/projects/799x/src`: exact editable payloads used for the delivered T44.

The catalog reads native names, icons, tooltips, and attached ability fields during synchronized initialization, two temporary items per timer tick. Every sample item is immediately hidden and removed. Click handlers are local presentation only and allocate no gameplay handles. Raw custom spell hotkeys are suppressed while the catalog is open so search input cannot issue spells.

Tooltip references are expanded before embedding; native text replaces the fallback only when it has no unresolved editor references. A small set of unchanged inherited prices uses the retained item audit; standard `bspd` boots use Blizzard's [published base cost](https://classic.battle.net/war3/neutral/buildings.shtml). Generated verification records enumerate these fallbacks for review. Dormant shops and undefined stock rawcode `I032` are excluded.

## Validation and limits

JASS compilation, archive roundtrip checks, untouched-entry checks, all-item reachability, search/empty states, recipe navigation, local-player isolation, no handles allocated by clicks, long-text pagination, percentage formatting, sample cleanup, and reapplication of the feature passed. Both installed copies have the same SHA256; the previous T43 is preserved in both archives.

No live Warcraft rendering or multiplayer test was performed, per the request not to open the game. The behavior harness validates JASS control flow against mocked native functions; it does not prove engine rendering, native tooltip expansion, or multiplayer behavior.
