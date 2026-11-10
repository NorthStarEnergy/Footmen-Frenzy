# Footmen Frenzy project instructions

Work autonomously; do not ask for routine confirmation. Preserve user changes and previous map builds.

This repository owns all four map projects. Read README.md and the selected projects/<project>/project.json. Use repository-relative paths; do not depend on the former ChatGPT working folders or OneDrive. Historical scripts in development are reference material; the current build entry point is Build-Map.ps1.

Every new validated test build MUST finish by using Build-Map.ps1, which builds, checks, and installs, or tools/Install-Wc3Map.ps1 for an already validated output. Do not report completion before delivery succeeds. Map families: 799x -> 799X; solo -> Solo Foots; mini -> Mini Foots; ffa -> FFA Foots. An FFA filename containing Solo does not change its family.

Use local Documents/Warcraft III/Maps/Tests/<family>. Keep exactly ONE active map directly inside each family folder; previous tests belong in its Test Archives. Update Maps/<family> to the same filename and SHA256, archiving the previous main copy under Maps/Archive/<family>. Verify both copies and the old test's preservation. Never install into OneDrive or Maps/Test. Maps/Foots is reserved for separately authorized live deployments.

Keep current releases and binary assets in Git LFS. Do not commit tools.local.json, credentials, build outputs, downloaded tools, or old binary caches. Retain the complete baseline map to preserve protected/unnamed archive entries. Compile changed JASS and perform archive roundtrip checks. Report whether live game testing was performed; static checks are not gameplay verification.

For new or revised ability tooltips, use coral red (#FF8979) only for damage values and green (#86E99D) for healing values. Keep all other text white. Omit "magic" from damage descriptions and preserve targeting restrictions.
