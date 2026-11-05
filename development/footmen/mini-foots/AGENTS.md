# Mini Foots test delivery

Follow the parent AGENTS.md installation requirements. Every new validated Mini Foots test build MUST finish by calling this directory's Install-TestMap.ps1 -Source 'absolute path to the new map.w3x'. Do not ask for routine confirmation.

This fixes the family to Mini Foots, installs into local Maps\Tests\Mini Foots, moves the previous test into its Test Archives, and updates Maps\Mini Foots with the same new map. Verify one active test and matching main/test SHA256 hashes. Never use the historical OneDrive or direct-copy installation steps in old READMEs or Install scripts.
