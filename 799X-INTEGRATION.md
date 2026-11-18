# Current 799X integration

The current test is **Reforged Footmen Frenzy v7.9.9X-T45 - Official Test - RJE.w3x**. Both installed 799X copies use the same title in Warcraft. T44 is archived.

The Items catalog was introduced in **Reforged_Footmen_Frenzy_v7.9.9X-T44.w3x**.

T44 SHA256: `457be6407ac92bdd0b17d01bc4e19f1ba3bf36f1746d02cea232073e685ee0a7`

This combines the other agent's T43 boots/amulet work with the toolbar and the 225-entry Items catalog. It preserves the T42 balance and earlier draft fixes. There were two different T43 outputs; use hashes, not only version names, when merging.

Other agents should start from the current complete installed map, or from any subsequently delivered newer map that retains this feature. Do not overwrite it with a stale T43 or the root checkout's historical v85 source.

See [the integration workflow](projects/799x/features/items-catalog/README.md) and [the delivery record](projects/799x/features/items-catalog/integration.json). The reusable generator can apply or refresh the catalog against another agent's latest complete map, and the staged installer rejects a changed baseline.

Warcraft was not opened for screenshots or live testing after the user requested that it remain untouched.
