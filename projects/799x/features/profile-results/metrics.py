"""Single schema for the in-game score pages and additive partner records."""
NATIVE = [
    ("trained", "Units trained", "UNITS_TRAINED"), ("killed", "Units killed", "UNITS_KILLED"),
    ("built", "Structures built", "STRUCT_BUILT"), ("razed", "Structures razed", "STRUCT_RAZED"),
    ("tech", "Tech percentage", "TECH_PERCENT"), ("food_cap", "Peak food produced", "FOOD_MAXPROD"),
    ("food_used", "Peak food used", "FOOD_MAXUSED"), ("hero_kills", "Heroes killed", "HEROES_KILLED"),
    ("items", "Items gained", "ITEMS_GAINED"), ("mercs", "Mercenaries hired", "MERCS_HIRED"),
    ("mined", "Gold mined", "GOLD_MINED_TOTAL"), ("gold_upkeep", "Gold mined with upkeep", "GOLD_MINED_UPKEEP"),
    ("gold_lost", "Gold lost to upkeep", "GOLD_LOST_UPKEEP"), ("gold_tax", "Gold lost to tax", "GOLD_LOST_TAX"),
    ("given", "Gold given (all trades)", "GOLD_GIVEN"), ("received", "Gold received (all trades)", "GOLD_RECEIVED"),
    ("lumber", "Lumber harvested", "LUMBER_TOTAL"), ("lumber_lost", "Lumber lost to upkeep", "LUMBER_LOST_UPKEEP"),
    ("lumber_tax", "Lumber lost to tax", "LUMBER_LOST_TAX"), ("lumber_given", "Lumber given", "LUMBER_GIVEN"),
    ("lumber_received", "Lumber received", "LUMBER_RECEIVED"), ("unit_score", "Unit score", "UNIT_TOTAL"),
    ("hero_score", "Hero score", "HERO_TOTAL"), ("resource_score", "Resource score", "RESOURCE_TOTAL"),
    ("score", "Total score", "TOTAL")
]
METRICS = [(key, label, "GetPlayerScore(Player(s-1), PLAYER_SCORE_" + native + ")" +
            {"given": " + FF_st_poolOut[s]", "received": " + FF_st_poolIn[s]"}.get(key, ""))
           for key, label, native in NATIVE]
METRICS += [
    ("level", "Highest hero level", "IMaxBJ(FF_st_heroLvl[s], GetHeroLevel(udg_herO[s]))"),
    ("kills", "Unit kills", "udg_unit_kills[s]"), ("deaths", "Unit deaths", "udg_unit_deaths[s]"),
    ("assists", "Assists", "DPS_Assists[s]"), ("h_kills", "Hero kills", "udg_hero_kills[s]"),
    ("h_deaths", "Hero deaths", "udg_hero_deaths[s]"), ("caps", "Hill captures", "DPS_Caps[s]"),
    ("buildings", "Buildings destroyed", "DPS_Buildings[s]"), ("transmutes", "Transmutes landed", "FF_st_tmHits[s]"),
    ("damage", "Damage dealt", "FF_st_dmg[s*3+FF_ST_DMG_OUT] + FF_st_dmg[s*3+FF_ST_DMG_BLD]"),
    ("building_dmg", "Structure damage", "FF_st_dmg[s*3+FF_ST_DMG_BLD]"),
    ("damage_in", "Damage taken", "FF_st_dmg[s*3+FF_ST_DMG_IN]"),
    ("gold_out", "Gold used (includes trades)", "PF_recordedCost[s]"),
    ("pool_out", "Gold pooled", "FF_st_poolOut[s]"), ("pool_in", "Pooled gold received", "FF_st_poolIn[s]"),
    ("sent_n", "Transfers sent", "PF_sent[s]"), ("received_n", "Transfers received", "PF_received[s]"),
    ("avg_sent", "Average per transfer sent", "PF_Average(FF_st_poolOut[s], PF_sent[s])"),
    ("avg_recv", "Average per transfer received", "PF_Average(FF_st_poolIn[s], PF_received[s])"),
    ("inherit_out", "Inheritance given", "FF_st_inhOut[s]"), ("inherit_in", "Inheritance received", "FF_st_inhIn[s]"),
    ("hill_gold", "Hill gold", "FF_st_kothGold[s]"), ("denies", "Own units denied", "FF_st_denyOwn[s]"),
    ("ally_denies", "Allied units denied", "FF_st_denyAlly[s]"), ("tm_casts", "Transmutes cast", "FF_st_tmCasts[s]"),
    ("tm_denied", "Transmutes denied", "FF_st_tmDenied[s]"), ("tm_saves", "Transmute saves", "FF_st_tmSaves[s]"),
    ("creeps", "Creeps hired", "FF_st_creeps[s]"), ("creep_gold", "Gold spent on creeps", "FF_st_creepGold[s]"),
    ("atk", "Attack upgrade", "FF_st_Tech(s, 'Rhme')"), ("def", "Defense upgrade", "FF_st_Tech(s, 'Rhar')"),
    ("race_level", "Race upgrade", "FF_st_RaceLevel(s)"), ("team_research", "Team research", "FF_st_teamRes[s]"),
    ("heroes_used", "Heroes fielded", "PF_heroCount[s]"), ("hero_xp", "Hero experience", "PF_heroXP[s]"),
    ("bets", "Casino stakes placed", "PF_wagers[s]"), ("staked", "Casino gold staked", "PF_staked[s]"),
    ("returns", "Casino gold returned", "PF_returned[s]"), ("net", "Casino net (incl. open stakes)", "PF_returned[s]-PF_staked[s]"),
    ("wallet", "Account gold", "WalletPublic[s-1]"), ("earned", "Match award (account gold)", "PF_rewards[s]"), ("escrow", "Casino gold in play", "CAS_escrow[s]"),
    ("loan", "Loan principal owed", "LoanPrincipal[s]"), ("interest", "Loan fees owed", "LoanFee[s]")
]

BOARDS = [
    [("level","Level"),("score","Score"),("kills","Kills"),("damage","Damage"),("gold_out","Gold used")],
    [("unit_score","Unit score"),("hero_score","Hero score"),("resource_score","Resources"),("score","Total"),("h_kills","Hero kills")],
    [("pool_out","Pooled"),("pool_in","Received"),("sent_n","Sends"),("avg_sent","Avg sent"),("avg_recv","Avg recv")],
    [("trained","Trained"),("built","Built"),("razed","Razed"),("items","Items"),("mercs","Hired")],
    [("mined","Gold mined"),("given","Given"),("received","Received"),("lumber","Lumber"),("gold_lost","Upkeep")],
    [("deaths","Deaths"),("assists","Assists"),("h_deaths","Hero deaths"),("caps","Hill caps"),("damage_in","Dmg taken")],
    [("tech","Tech %"),("food_cap","Peak supply"),("food_used","Food used"),("killed","Units killed"),("hero_kills","Heroes killed")],
    [("gold_upkeep","With upkeep"),("gold_tax","Gold tax"),("lumber_lost","Wood upkeep"),("lumber_tax","Wood tax"),("lumber_given","Wood given")],
    [("lumber_received","Wood recv."),("pool_out","Pooled"),("pool_in","Received"),("hill_gold","Hill gold"),("gold_out","Gold used")],
    [("heroes_used","Heroes used"),("hero_xp","Hero XP"),("level","Level"),("items","Items gained"),("mercs","Mercenaries")]
]

for index, game in enumerate(["Poker", "Blackjack", "Predictions", "Challenges"]):
    for suffix, label, variable in [("stakes", "stakes", "PF_gameBets"), ("gold", "gold staked", "PF_gameStake"), ("paid", "gold returned", "PF_gameReturn")]:
        METRICS.append((game.lower()+"_"+suffix,game+" "+label,f"{variable}[s*4+{index}]"))

def schema():
    ids = {key: i for i, (key, _, _) in enumerate(METRICS)}
    init = [f'    set PF_metrics = {len(METRICS)}']
    cases = []
    for i, (key, label, expression) in enumerate(METRICS):
        init += [f'    set PF_label[{i}] = "{label}"', f'    set PF_key[{i}] = "{key}"']
        cases += [f'    {"if" if i == 0 else "elseif"} k == {i} then', f'        return {expression}']
    for page, columns in enumerate(BOARDS):
        for col, (key, title) in enumerate(columns):
            ix = page * 5 + col
            init += [f'    set PF_columns[{ix}] = {ids[key]}', f'    set PF_columnTitle[{ix}] = "{title}"']
    return ('function PF_Schema takes nothing returns nothing\n' + '\n'.join(init) +
            '\nendfunction\n\nfunction PF_Live takes integer s, integer k returns integer\n' +
            '\n'.join(cases) + '\n    endif\n    return 0\nendfunction\n')
