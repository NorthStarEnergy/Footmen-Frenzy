    hashtable DK_Hash = null
    timer DK_Timer = null
    real DK_Now = 0.0
    integer DK_High = 0
    integer array DK_Kind
    unit array DK_Source
    unit array DK_Target
    player array DK_Owner
    effect array DK_FX
    group array DK_Hit
    group array DK_Pulled
    real array DK_X
    real array DK_Y
    real array DK_DX
    real array DK_DY
    real array DK_Left
    real array DK_End
    real array DK_Damage
    integer array DK_Stacks
    integer array DK_Parent
    boolean array DK_Return
hashtable MU_Hash = null
unit array MU_Hero
integer MU_Count = 0
timer MU_Timer = null
trigger MU_CleaverHit = null
real MU_Now = 0.0
unit array FF_DebugFate
hashtable MQ_Hash = InitHashtable()
trigger MQ_FinishTrigger = CreateTrigger()
trigger MQ_RemoveTrigger = CreateTrigger()
hashtable MD_Hash = InitHashtable()
hashtable MD_Types = InitHashtable()
    hashtable VG_Hash = null
    hashtable VG_PrevX = null
    hashtable VG_PrevY = null
    unit array VG_Hero
hashtable MM_Hash=InitHashtable()
integer array MDV_Code
boolean array MDV_Used
hashtable MW_Hash = null
    boolean DPS_ProfileLoaded = false
    integer array DPS_Prior
    string DPS_ProfilePath
    string DPS_LastPayload
hashtable PF_data = InitHashtable()
    hashtable PF_final = InitHashtable()
    hashtable PF_local = InitHashtable()
    integer array PF_sent
    integer array PF_received
    integer array PF_logCount
    integer array PF_recordedCost
    integer array PF_lastHero
    integer array PF_counts
    integer PF_metrics = 0
    string array PF_label
    string array PF_key
    string array PF_tabName
    integer array PF_columns
    string array PF_columnTitle
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
    integer array PF_hillSeconds
    integer array PF_priorEco
    string PF_lastEco = null
    hashtable PF_history = InitHashtable()
    integer array PF_historyN
    integer PF_sendKind = 0
    integer PF_sendIndex = 0
    integer array PF_heroCount
    integer array PF_heroXP
    string WalletAccount
    string WalletPath
    integer WalletBalance = -1
    integer array WalletPublic
    string WalletSyncPrefix = "FFWallet1"
    integer array WalletOpening
    integer array WalletStartingGrant
    boolean array WalletKnown
    boolean WalletSettled = false
    integer array WalletPlayedSlot
    framehandle array BJ_wagerLabel
    boolean array CasinoPlayed
    integer array NS_Selected
    integer array NS_Dealt
    framehandle array NS_Selector
    boolean array NS_BoardRank
    integer PK_Seed = 81731
    integer array PK_Deck
    integer array PK_Cards
    integer array PK_Stack
    integer array PK_Paid
    integer array PK_Total
    integer array PK_Street
    integer array PK_Turn
    integer array PK_Dealer
    integer array PK_Hand
    integer array PK_LastRaise
    integer array PK_Actions
    integer array PK_Clock
    integer array PK_Wait
    boolean array PK_Started
    boolean array PK_Hidden
    boolean array PK_Acted
    boolean array PK_Reveal
    string array PK_Note
    framehandle array PK_Dialog
    framehandle array PK_Text
    framehandle array PK_Title
    framehandle array PK_HumanLabel
    framehandle array PK_HumanStack
    framehandle array PK_BotStack
    framehandle array PK_BotLabel
    framehandle array PK_PotLabel
    framehandle array PK_Status
    framehandle array PK_CallLabel
    framehandle array PK_Face
    framehandle array PK_HumanChips
    framehandle array PK_BotChips
    framehandle array PK_PotChips
    framehandle array PK_HumanDealer
    framehandle array PK_BotDealer
    framehandle array PK_Fold
    framehandle array PK_Call
    framehandle array PK_Raise
    framehandle array PK_Allin
    framehandle array PK_Next
    framehandle array PK_Hide
    integer array PK_Count
    integer array PK_Sort
    integer array PK_Eval
    sound CAS_winSound = null
    sound CAS_lossSound = null
    integer CAS_seed = 71983
    integer CAS_bank = 1000000
    integer CAS_liability = 0
    integer CAS_seconds = 0
    integer CAS_winner = 0
    trigger CAS_baseEvent = null
    trigger CAS_matchEvent = null
    boolean CAS_warned = false
    boolean CAS_closed = false
    boolean CAS_ended = false
    integer CAS_buildSlot = 0
    integer array CAS_escrow
    integer array CAS_returnDue
    integer array CAS_profitDue
    integer array CAS_view
    integer array CAS_amount
    string array CAS_note
    framehandle array CAS_root
    framehandle array CAS_title
    framehandle array CAS_balance
    framehandle array CAS_status
    framehandle array CAS_footer
    framehandle array CAS_button
    framehandle array CAS_content
    framehandle array CAS_card
    framehandle array CAS_felt
    framehandle array CAS_chip
    framehandle array CAS_seatTotal
    framehandle array CAS_row
    framehandle array CAS_bar
    framehandle array CAS_track
    integer array BJ_table
    integer array BJ_seat
    integer array BJ_owner
    integer array BJ_phase
    integer array BJ_clock
    integer array BJ_round
    integer array BJ_turn
    integer array BJ_shoe
    integer array BJ_pos
    boolean array BJ_error
    integer array BJ_card
    integer array BJ_count
    integer array BJ_total
    integer array BJ_aces
    integer array BJ_state
    integer array BJ_bet
    integer array BJ_reserve
    boolean array BJ_split
    integer array BJ_dealerCard
    integer array BJ_dealerCount
    integer array BJ_dealerTotal
    integer array BJ_dealerAces
    boolean array BJ_reveal
    string array BJ_result
    integer MK_n = 0
    boolean MK_ffa = false
    timer MK_payTimer = null
    integer MK_scan = 1
    integer array MK_prior
    integer array MK_quoteTotal
    integer array MK_ownedStake
    integer array MK_ownedReturn
    integer array MK_player
    integer array MK_market
    integer array MK_target
    integer array MK_stake
    integer array MK_return
    integer array MK_reserve
    boolean array MK_paid
    integer array MK_pool
    integer array MK_volume
    boolean array MK_done
    integer array MK_winner
    boolean array MK_baseScored
    integer array MK_tab
    integer array MK_pick
    integer array MK_page
    integer DU_n = 0
    integer array DU_from
    integer array DU_to
    integer array DU_target
    boolean array DU_ffa
    integer array DU_stake
    integer array DU_state
    integer array DU_expire
    integer array DU_outgoing
    integer array DU_incoming
    integer array DU_active
    integer array DU_opponent
    integer array DU_pick
    integer array CAS_gold
    boolean array CAS_ready
    integer array CasinoLastView
    integer array LoanLent
    integer array LoanOutstanding
    integer array LoanInterest
    integer array LoanLender
    integer array LoanPrincipal
    integer array LoanFee
    integer array LoanPendingPrincipal
    integer array LoanPendingFee
    integer array LoanIdentity
    integer array CreditMode
    integer array CreditRate
    integer array CreditPeriod
    integer array CreditElapsed
    integer array CreditFraction
    integer array CreditHold
    integer array CreditOwner
    integer array CreditAmount
    integer array CreditOfferMode
    integer array CreditOfferRate
    integer array CreditOfferPeriod
    integer array CreditTarget
    integer array CreditFee
    integer array CreditGeneration
    integer array CreditSeen
    integer array CreditSelected
    integer array CreditDraftMode
    integer array CreditDraftRate
    integer array CreditDraftPeriod
    boolean array CreditRequest
    boolean array CreditDraftRequest
    string LoanLocalRecord
    integer PK_Queue = 0
    integer array PK_Table
    integer array PK_Guest
    integer array PK_Default
    integer array PK_LastPot
    integer array PK_Version
    integer array PK_InputVersion
    boolean array PK_Ready
    string array PK_Feedback
    framehandle array PK_Input
    framehandle array PK_Prompt
    framehandle array PK_Alternate
    string array BJ_dealerAction
    integer CasinoLauncherSlot = 0
    trigger CasinoOpen = null
    integer array PF_wagers
    integer array PF_staked
    integer array PF_returned
    integer array PF_gameBets
    integer array PF_gameStake
    integer array PF_gameReturn
    integer array PF_rewards
    integer array AR_pick
    integer AR_until = 0
    player array AR_owner
    unit array AR_hero
    unit array AR_foot
    item array AR_scroll
    fogmodifier array AR_vision
    rect AR_floor = null
    timer AR_clock = null
    trigger AR_orders = null
    trigger AR_damage = null
    trigger AR_deaths = null
    integer array AR_roster
    integer array AR_skill
    player array AR_flagFrom
    player array AR_flagTo
    alliancetype array AR_flagType
    boolean array AR_flagBefore
    integer AR_flagCount = 0
    real AR_oldLeft
    real AR_oldBottom
    real AR_oldRight
    real AR_oldTop
    real AR_oldX
    real AR_oldY
    real AR_oldZoom
    trigger SoloCasinoLaunch = CreateTrigger()
    integer array BJWatchHost
    integer array BJWatchPage
    framehandle array BJWatchEye
    framehandle array BJWatchHistory
    string array BJWatchLast
    string array BJWatchPrevious
    string array BJWatchOlder
    integer CasinoWalletRetries = 0
    framehandle array PK_Lower
    framehandle array PK_Higher
    framehandle CasinoMenuButton = null