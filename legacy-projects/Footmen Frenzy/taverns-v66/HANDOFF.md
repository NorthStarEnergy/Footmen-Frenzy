# v66 - Team Taverns

Map: FF799X_Rx_Team_Taverns_v66.w3x
Client name: Footmen Frenzy 799X v66 - Team Taverns
Based on v65 (which preserves the v63 startup sequence and v64 Mundo cloud repair).

- SD: real Tavern model for non-carry offers; Human Altar of Kings for carry offers, positioned near the inner front of each base.
- Completed teams' shops move into four ordered rows at the west plaza. An eligible SD/AR repick returns the team's altar/tavern to the base.
- Public offers and current picks are recorded in F9 (Quests) and -draft for all 24 player/observer slots. These records do not need world vision. Tracked tavern vision stops after drafting; archived shops have zero sight.
- Random Hero is available only at team Carry Altars. Three shared uses per team; full enabled roster including heroes offered in the draft. Invalid purchases do not consume a use. Existing SD category limits and carry locks remain. Random SD heroes retain bonus Boots of Speed.
- AP keeps all nine western taverns. Roster stock follows the authoritative hero count. All 91 enabled heroes are covered, with no shop exceeding 11 hero entries. The five pre-existing disabled roster entries remain disabled: H00K, O00G, N03J, U00F, HDk1.
- AR retains automatic initial assignment. During an eligible -repick, use the team's Random altar instead of receiving the old predetermined replacement.
- Attack range setters compensate for the engine's two-weapon-field delta behavior at eight army spawn/update call sites. Intended baseline footman range remains 110; range upgrades are preserved.
- Runtime and World Editor source are synchronized. The existing startup dialogs and Mundo functions are preserved.

Validation: runtime pjass, World Editor JassHelper regeneration + pjass, roster/quota/range checks, and MPQ payload preservation passed. 1,355 unaffected archive payloads preserved. No imported assets removed or replaced; the new building art uses Warcraft's built-in models.

In-game playtest is still required, especially base placement/pathing, SD/AP/debug hiring, three shared Random purchases, observer draft records, and range display/damage behavior. The running match was not interrupted.
