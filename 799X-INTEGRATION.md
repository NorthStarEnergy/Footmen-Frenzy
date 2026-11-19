# Current 799X integration

The current test is **Reforged Footmen Frenzy v7.9.9X-rc3.w3x**. Both installed 799X copies have SHA256 `d6cc5f8245e0a5f28ebe7e991741c1e2c5381a9b16a0f4cf31118f656eadd5e5`. RC2 is archived in both channels. RC3 parents Profile and zoom controls directly to the native game UI to restore world clicks.

RC2 replaces the Items toolbar with Profile, removes item ownership and XP catch-up, and gives each hero picker a personal tavern. The RC2 preparation and regression checks live under `projects/799x/features/rc2`. Start subsequent work from the complete installed RC3 or its verified successor.

The Items catalog was introduced in **Reforged_Footmen_Frenzy_v7.9.9X-T44.w3x**.

T44 SHA256: `457be6407ac92bdd0b17d01bc4e19f1ba3bf36f1746d02cea232073e685ee0a7`

This combines the other agent's T43 boots/amulet work with the toolbar and the 225-entry Items catalog. It preserves the T42 balance and earlier draft fixes. There were two different T43 outputs; use hashes, not only version names, when merging.

The [catalog integration workflow](projects/799x/features/items-catalog/README.md) and [T44 delivery record](projects/799x/features/items-catalog/integration.json) describe the historical Items feature removed in RC2.

Warcraft was not opened for screenshots or live testing after the user requested that it remain untouched.
