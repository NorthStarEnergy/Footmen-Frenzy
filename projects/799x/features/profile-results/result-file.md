# 799X match and Profile records

The map writes `ff_result.txt` in Warcraft III's CustomMapData directory on ordinary clients. The host-bot client uses `ff_result_<game token>.txt`. Each write replaces the current match snapshot. Read the last complete snapshot for a game and use its `gameend` record to recognize a final result. A repeated snapshot for the same game can carry late-arriving career history. The existing format-2 records, including roster, results, skills, usage and hill control, keep their meanings.

| Record | Contents |
| --- | --- |
| `casino,enabled=1,starting_wallet=1000` | RC29 casino configuration for the match. |
| `wallet,accountSlot,known=1,opening=N,balance=N,starting_grant=N` | Available Wallet balance at initial sync and at this snapshot. Opening includes the grant. A returning account has a zero grant even when opening is exactly 1,000. A pending or invalid Wallet on a participating slot emits only `known=0`. |
| `profile_owner,slot,name,accountSlot` | One-based slot, sanitized name and the associated casino account slot when a substitute is playing |
| `profile,slot,key=value,...` | Match totals, the Warcraft score categories, gameplay, transfers, account awards and casino activity. Merge all rows for each slot by key. The casino counters belong to the physical account slot. |
| `collection,slot,kind,rawcode=count,...` | Hero selections, item purchases, units fielded and appearances fielded in this match. The kinds are `hero`, `item`, `unit` and `skin`. |
| `build,slot,sequence,seconds,action,objectId,amount,otherSlot,balance` | Chronological journal. Sequence starts at one per slot. Object IDs use decimal Warcraft four-character codes. Zero means no object or counterparty. An amount of −1 means no quoted price. Balance is battlefield gold at the event. |
| `career,accountSlot,kind,id=total,...` | Cumulative values using the reporting client's saved history plus this match. Kinds 1–4 correspond to heroes, items, units and skins. IDs in career rows are decimal. |
| `career_pool,accountSlot,avg_pro_sent=N,avg_pro_received=N` | Average gold pooled and received per Pro match played, including games with zero transfers. These rows require the client's saved economy baseline. |

## Gold and career totals

`given` and `received` combine native resource trades with custom transfers. `pool_out` and `pool_in` are the custom transfers alone. Both the periodic `-pool` delivery and F3 use the amount actually transferred after reserves and applicable limits. `sent_n` and `received_n` count successful transfers. `avg_sent` and `avg_recv` use integer gold per successful transfer. For team averages, divide total pooled gold by the total number of transfers across that team.

`gold_out` counts observed battlefield gold debits, including outgoing transfers. Refunds are credits. A `gold_out` journal row records a balance change. Named purchase, completion and transfer rows explain activity and may describe that same gold. Use the debit total directly when totaling gold used. Casino stakes, returns, loans and match awards use the separate account wallet. Poker buy-ins, blackjack stakes (including doubles and splits), market predictions and player challenges each have their own stake count, gold staked and gold returned. Returns include refunded principal.

In kind 0 career rows, IDs 0–7 are games played, Pro games played, pooled gold sent, pooled gold received, outgoing transfers, incoming transfers, Pro gold sent and Pro gold received. IDs 8–15 are unit kills, unit deaths, assists, hero kills, hero deaths, hill captures, buildings destroyed and transmutes landed. Career totals are client-reported and may arrive after the match rows. A fresh installation begins a new collection history. RC22 reads the eight existing local combat totals. Use match rows when independently aggregating games.

The metric keys and human-readable labels are defined together in `metrics.py`. The wallet account and battlefield slot can differ when an observer substitutes for a player. Read the account's casino rows and the battlefield slot's gameplay rows in that case.
