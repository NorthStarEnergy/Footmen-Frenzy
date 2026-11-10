# Latest map audit — November 4, 2026

The newest 799X map directly in Documents/Warcraft III/Maps/Test is FF799X_Rx_Ghoul_Grunt_Buff_v69.w3x (October 30). SHA-256: 3a7fa707aacf1ccaee6e17683758f6a2f59cb5fa04c8baad39b9508c9e0363ca. The folder also has Spawn_Rates_v68 and Pub_XP_v67. There is no installed v83 in that folder.

The latest build from this chat is veigar-ultimate-v83/release/FF799X_Rx_Veigar_Ultimate_v83_TEST.w3x. It remains outside the game Test folder. It includes Z stacking and Z-kill-based V stacking; the installed v69 does not. Direct script comparison also confirms the installed map lacks the newer Lux, Stalker, Soul Hook, Mundo cleaver-wound, catch-up and fed-reward helper implementations.

The branches have diverged in both directions. Compared with the common v67 source, installed v69 changes FFGS_InitSettings and Trig_set_spawn_variables_Actions, and six unit object fields. V83 lacks those spawn-interval edits and Ghoul/Grunt buffs:

| Unit | Installed v69 HP / armor / base damage | v83 HP / armor / base damage |
|---|---|---|
| Ghoul | 750 / 2 / 16 | 675 / 1 / 14 |
| Grunt | 900 / 3 / 27 | 800 / 2 / 24 |

Solo Tests/Solo_Foots_v1.8_4P_799X_UPDATE08.w3x is a separate four-player branch, SHA-256 7529c5a174b2ee98fc5e0b90bdd20276a0ec14f0850501962907722a28415300. Its script has separate Solo camera, mass preload/release, spawn, tavern, altar and other implementations. Their presence does not mean all are appropriate to transplant into 799X; different function names alone do not prove an equivalent feature is absent. No comprehensive semantic merge of Solo work is established.

Conclusion: there is no verified single map containing every latest change. Files are preserved, but work remains split across installed Test, v83 and Solo branches. Merely copying v83 into Test would not resolve the missing installed spawn/balance edits. No maps were changed or installed by this audit.

Evidence: report.json contains artifact hashes, function differences and unit field comparisons; differences.txt contains the exact installed/v83 spawn/balance diffs and recent build lineage. This is an archive/source audit, not a gameplay test or a claim to have exhaustively classified every historical branch change.
