    // One physical arena. State 0 is free, 1 is an invitation, 2 is a fight.
    integer AR_state = 0
    integer array AR_seat
    integer array AR_pick
    integer AR_until = 0
    integer AR_stake = 0
    integer array AR_held
    integer AR_offer = 0
    integer AR_shownOffer = 0 // Local UI value, sent with the Accept click.
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
    // Read and used only by the local camera UI.
    real AR_oldLeft
    real AR_oldBottom
    real AR_oldRight
    real AR_oldTop
    real AR_oldX
    real AR_oldY
    real AR_oldZoom
