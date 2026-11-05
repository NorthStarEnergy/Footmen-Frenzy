# Footmen Frenzy v50: size and content audit

Scope: `FF799X_Rx_TF_Guardian_WC3Icons_v50.w3x`, SHA-256 `b2ae4e62182c33fedd285c20d8f8f16ae503b7289ef3d6fc0568ea8ec279d3c2`. This is a read-only analysis of the release; no gameplay assets or map content were removed.

## What is core

Keep the map script (`war3map.j`), map terrain and placement data, map configuration and pathing, object and skin data, string table, import table, and resources reachable from them. This includes heroes and their spells, items, units, buildings, upgrades, modes, UI, sounds, models and models' textures. The imported hero and spell systems are scripted; deleting object records merely because a tavern or ability currently appears disabled can break another mode, a scripted dummy, a summoned unit, an upgrade, or a future selection path. Standard-game replacement paths can be implicitly loaded even if their path is not written in the script. Research/disabled button variants and portraits may also load by naming convention.

## Size measurements

The file is 58,679,435 bytes (55.96 MiB). Its 1,361 active archive entries total 26,496,109 stored bytes (25.27 MiB). This difference suggests archive layout/free space is worth investigating, but it is not a verified saving: alignment, tables, unknown entries, MPQ constraints, and file structure must be accounted for. Of the 1,361 archive entries, 1,333 could be named with the available import table, listfile, and workspace file inventories; 28 entries remain unnamed. Known entries include approximately 11.63 MiB of BLP textures and 7.73 MiB of MDX models (stored sizes). Their sum excludes unnamed files and is not the full archive size.

A non-destructive StormLib compaction trial on a copy returned failure (error 10007); the trial file did not shrink. No compacted build was validated. Do not ship or treat the estimated gap as savings until every archive entry is identified and a compaction/rebuild preserves all entries and passes a real game load. Prior v39 cleanup reported a larger output despite deleting assets, illustrating that uncompressed bytes or removed files do not guarantee a smaller map.

## Candidate categories

The automated literal-reference scan found 842 imports with no direct string reference, totaling 7,021,546 stored bytes (6.70 MiB). This is an upper-bound review queue, not a safe deletion list or expected net saving. The scan checks raw script, object, model and other named file bytes but cannot prove absence of implicit, runtime-constructed, game-engine or unnamed-entry dependencies. In particular, do not remove a disabled icon because the scan misses its implicit BTN-to-DISBTN mapping, or a portrait because it is not referenced by name. Several portraits in the raw scan need such special handling.

The best first review is obsolete source or preview images rather than gameplay models: the seven unreferenced PNG imports together occupy 596,708 stored bytes (0.57 MiB), led by `war3mapImported\warstomp.PNG` (230,079 bytes), `war3mapImported\healspray.PNG` (224,583), and `war3mapImported\Windwalk.PNG` (97,409). Confirm none are used through a runtime-generated path, imported UI, editor workflow, or unknown asset before testing removal. The old `BTNLoadedDice.tga` and `DISBTNLoadedDice.tga` are candidates after the newer BLP dice buttons were introduced; together they occupy 20,706 stored bytes, but verify the current ability and disabled-button resolution and all other references before deleting them.

There are 108 MDX files with no literal reference (1,567,929 stored bytes) and 717 BLP files with no literal reference (4,613,802 stored bytes); these numbers include implicit portraits, textures, standard-path overrides and buttons, so require dependency-graph investigation. Some models may be deliberately unused variants; classify them only after tracing their object records, model texture paths, portrait companions, and script references. Do not bulk-delete this group.

Three Frost Eruption MP3 imports have no literal reference and total 146,108 stored bytes. Check Warcraft sound metadata and editor-trigger dependencies before removal. Five import-table entries could not be read as archive files: four `.flac` paths and a doubled `war3mapImported\\war3mapImported\\PASTreantHide.blp` path. These may be stale records, stock assets, or path resolution issues; investigate before changing the import list.

## Object inventory

The base unit object table contains 139 modified standard units and 608 custom units. The ability table has 362 modified standard abilities and 1,535 custom abilities. Item data contains 85 modified standard items and 230 custom items. Buff data has 132 custom entries; upgrade data has 8 modified and 28 custom entries. These counts are not counts of unused objects. Object records are highly compressed compared with their decoded size; cleanup may simplify maintenance but deleting them is unlikely to save as much as reducing large imported art or safely reclaiming archive space.

## Recommended sequence

1. Establish a complete file-name inventory for all 28 unnamed archive entries and determine the reason compaction returned error 10007. Preserve the original and compare every archive entry after any trial.
2. Build a dependency graph covering direct object and trigger references, map placements, spawned rawcodes, model-to-texture links, implicit portraits, active/disabled button pairs, and engine overrides. Include every mode and test/debug path.
3. Review the PNGs, old dice TGAs and other confirmed obsolete source files as the first removal batch. Build a separate map, update its import table, measure the actual resulting file size, compare all unrelated archive payloads, and test game loading and affected heroes/UI.
4. Review unused-looking model families and their exclusive textures together. Keep shared textures and implicit portraits. Repeat the measured build and in-game checks for each coherent group.
5. Only then consider unused spells/units/items or restoring modified game objects to defaults, and only after checking rawcode references, generated trigger data, inheritance, summons, and mode-specific uses.

`imports.csv` contains the full review queue, stored and raw byte sizes, and literal reference sources; `archive-files.json` lists named archive entries. `summary.json` contains aggregate counts and largest entries. The numbers are based on the v50 release and must be regenerated for later versions. No gameplay or visual validation has been performed for removal candidates.
