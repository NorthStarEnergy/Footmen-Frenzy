# Warcraft III build and installation rules

Every new validated test map MUST be installed as the final build step, without routine confirmation. A build is not complete until installation and verification succeed.

Use this project's Install-Wc3Map.ps1, which delegates to the shared checked installer:

```powershell
& 'C:\Users\User\Documents\ChatGPT\Footmen Frenzy\Install-Wc3Map.ps1' -Source 'absolute path to new map.w3x' -MapType '799X'
```

MapType is 799X for 799X builds, Mini Foots for Mini builds, Solo Foots for four-player Solo, and FFA Foots for the eight-player FFA branch. Do not infer Solo from an FFA filename containing Solo. Use a new family name for a genuinely new map type.

The sole installation root is C:\Users\User\Documents\Warcraft III\Maps. Never install into OneDrive or singular Maps\Test.

For every new test:
- Install into Maps\Tests\[map type], retaining its versioned filename.
- Keep exactly ONE active .w3x/.w3m file directly inside that folder.
- Move all previous active tests into that folder's Test Archives subfolder; preserve them without overwriting or deleting.
- Synchronize the new test into Maps\[map type], archiving the previous main-folder map under Maps\Archive\[map type]. The current test and main copies must have the same filename and SHA256.
- Verify the active-file count, checksums, and preservation of the previous test before reporting completion.
- If installation fails, resolve it or explicitly report the map as not installed.

Maps\Foots is reserved for deployed real-game maps. A test build does not authorize promotion there.

These instructions apply to every build subdirectory, including 799x-backport, shared-sync-v85, mini-foots, and future version directories. Older README paths and historical Install*.ps1 scripts that copy to OneDrive, Maps\Test, or bypass rollover are obsolete for installation. Use the shared installer instead of those installation steps, after the relevant build validation passes. Do not rerun an old build merely to install a newer map.

## Canonical GitHub workspace (November 5, 2026)

All four current map projects now live in `C:\Users\User\Documents\GitHub\Footmen Frenzy` (NorthStarEnergy/Footmen-Frenzy). Read that repository's AGENTS.md and README.md before new development. Use projects/799x, projects/solo, projects/mini, and projects/ffa and the repository Build-Map.ps1 entry point. This older working tree is retained as a migration backup and for historical dependencies. Its shared installer entry point forwards through to the repository's canonical installer.
