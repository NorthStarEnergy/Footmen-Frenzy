# Hero hiring v65

Built from v64 (SHA256 35097d7a8639a1ea6cbff0b75a32b871be4478e7550277c1b9dd187a7dca15f2), preserving v63 startup dialogs and v64 Mundo cloud changes.

The new dialog startup deletes the h01G/h03Y selector units. Those owned units also supplied nearby patrons for neutral tavern hiring. AP taverns use Ane2 with an 800-unit activation radius; SD/Carry taverns use A05T with a 200-unit radius. The combat bases are outside the hero plaza. One player slot also lacked a placed selector.

At shared game start, after selection mode creates its taverns, FFHire_Prepare creates food-free, invulnerable, transparent, nonblocking h01G buyers for every active slot 1–12. Vote abilities are removed. AP gets one buyer in the plaza center (within 173 units of all nine taverns). SD gets buyers at its own team's main and carry taverns, plus the optional second carry tavern. Other teams' shops stay outside their 200-unit activation range. Buyers stay present rather than using ShowUnit(false) or Locust. AR retains direct assignment. FFHire_Ready prevents duplicate initialization.

All existing function bodies except the shared Start_game hook are unchanged from v64. No unit/ability objects, hero limits, stock restrictions, mode menu sequencing, or starting gold changed. Editor WCT globals/functions and runtime JASS both updated. Internal title, description and loading screen show v65.

Validation: runtime pjass passed; regenerated authoritative WCT source compiled with JassHelper and compiled output passed pjass. Checks cover all 12 slots, AP shop reach, SD team isolation, and routes for Pub, Pro, Custom 4K, Private AP/SD/AR, Debug and AFK Pub fallback. Packed modified files re-extract identically and 1,357 unaffected archive payloads are preserved.

Output: FF799X_Rx_Hero_Hiring_v65.w3x
SHA256: 3ae78df2a3f080c6705a624b452dac778841c96dcccb737192343797813f68da

Live Warcraft mode-by-mode playtesting remains pending. An existing match cannot load these changes; start v65 from the Test folder. Previous unresolved v63 item I032 is unchanged.

Reproducible local build files: prepare.py, hiring.j, verify.py, pack.py in this folder on the User PC. The shared release includes reports and this handoff; supporting archive tools live in that PC's Footmen Frenzy workspace.
