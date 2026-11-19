hashtable PF_data = InitHashtable()
    hashtable PF_prices = InitHashtable()
    hashtable PF_final = InitHashtable()
    hashtable PF_local = InitHashtable()
    integer array PF_sent
    integer array PF_received
    integer array PF_logCount
    integer array PF_recordedCost
    integer array PF_wagers
    integer array PF_staked
    integer array PF_returned
    integer array PF_lastHero
    integer array PF_counts
    integer PF_metrics = 0
    string array PF_label
    string array PF_key
    string array PF_tabName
    integer array PF_columns
    string array PF_columnTitle
    boolean PF_frozen = false
    boolean PF_draw = false
    boolean PF_dirty = false
    integer PF_exportSlot = 0
    framehandle PF_root = null
    framehandle PF_title = null
    framehandle PF_subtitle = null
    framehandle PF_footer = null
    framehandle PF_back = null
    framehandle PF_continue = null
    framehandle PF_prev = null
    framehandle PF_next = null
    framehandle array PF_tab
    framehandle array PF_icon
    framehandle array PF_line
    framehandle array PF_value
    framehandle array PF_board
    framehandle array PF_band
    boolean PF_visible = false
    boolean PF_results = false
    integer PF_page = 0
    integer PF_section = 0
    integer PF_pages = 1
    integer array PF_careerCount
    boolean PF_careerReady = false
    integer PF_saveTick = 0
    integer PF_exportStart = 0
    integer PF_endSecond = 0
    integer PF_casinoFirst = 0
    integer PF_combatFirst = 0
    integer PF_poolOutMetric = 0
    integer PF_poolInMetric = 0
    integer PF_sentMetric = 0
    integer PF_receivedMetric = 0
    integer array PF_verdict
    string array PF_message
    framehandle array PF_portrait
    boolean PF_shown = false
    integer array PF_gameBets
    integer array PF_gameStake
    integer array PF_gameReturn
    integer array PF_hillSeconds
    integer array PF_priorEco
    string PF_lastEco = null
    hashtable PF_history = InitHashtable()
    integer array PF_historyN
    integer PF_sendKind = 0
    integer PF_sendIndex = 0
    integer array PF_heroCount
    integer array PF_heroXP
    integer PF_winSide = 0
    integer array PF_rewards
