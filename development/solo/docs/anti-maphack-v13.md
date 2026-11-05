# Silent anti-maphack telemetry — SF_Test1.7_v13

## Review result

The Pass 23 design was accepted after a source-level review, but it was not copied unchanged. Its synchronization model is sound: client-local fog and camera values are read only by the probe sender, serialized through `BlzSendSyncData`, and evaluated only after synchronized receipt. The response remains telemetry-only and never renames, handicaps, removes, defeats, or otherwise alters a player.

## Solo Foots adaptations

- Changed the zoom rule from the source map's 4500 clamp to Solo Foots' actual 4000 clamp.
- Uses 4700 as the anomaly threshold, preserving Pass 23's 700-unit tolerance.
- Requires consecutive anomalous zoom samples; a normal reading resets the watch counter.
- Exempts level-90 administrators from zoom scoring because Solo Foots' authorized `-cam 1` command applies a legitimate 10067-distance video camera.
- Runs zoom evaluation even with one or two responders. Fog, bounds, and far-Z consensus still abstain below three responders because no safe majority exists.
- Excludes units with the Locust ability from fogged-target order scoring so scripted spell-dummy orders do not pollute the log.

## Detection layers

### Fog and camera synchronization probe

Every 11 seconds, after four warm-up ticks, each client reports fog state, fog-mask state, four camera bounds, target distance, and far-Z. Fog, bounds, and far-Z outliers are scored only when at least three clients respond and a strict majority agrees. Missing replies are scored only when at least two other clients prove the round succeeded.

### Fogged-target orders

A targeted order against a living, visible-model, non-structure enemy that `IsUnitVisible` says the issuing player cannot see adds a telemetry hit. Structures remain exempt because remembered building shadows are legitimately clickable. Unselectable Locust spell dummies are also exempt.

## Output and access

- Detections are written as MMD `custom AMH` records.
- Administrators at level 90 or higher can type `-mhlog` for the current score table.
- No public message or automated punishment exists.
- The existing fake-shop protection remains a separate system.

## Static verification

- JASS parser: OK, 8,850 top-level declarations.
- Anti-maphack functions: 17.
- Client-local fog/camera reads: seven kinds, all confined to `AntiMH_ProbeSend`.
- `BlzSendSyncData` calls per probe: one.
- `GetLocalPlayer` references inside the subsystem: zero.
- Gameplay-response calls inside the subsystem: zero.
- Source/round-trip script SHA256: `1270C497A4535EBA95E122167D70042236A6D9850EB293A4C4057A4E9623A076` (exact match).
- Map SHA256: `477467228DDB9C0C0B7411031F6A1219FF076DC651D37B47896974637770D6EF`.
- Unit object data remains unchanged: `B0F8043E9D18088AD264B64F4AAAA0FFCD813EAB6288CE915A1FCCB2CA1C332E`.

## First live-game checks

1. In a clean three- or four-player lobby, wait through the 44-second warm-up and several probe rounds; `-mhlog` should show nothing scored.
2. In a one-player test, verify ordinary `-zoom 4000` does not score.
3. As an authorized admin, apply `-cam 1`, wait for several rounds, and verify it does not score a zoom hit.
4. Review any order hits to identify a non-Locust scripted order that needs a narrow exemption before considering any response policy.
5. Confirm KOTH, Colossals, spawning, shop visibility, and page navigation still behave as in v12.

Render-only maphacks can still report honest native values or spoof a known payload. This system is evidence collection, not proof, and logs should be reviewed across several real games before any automated action is considered.
