function NS_Name takes integer id returns string
    if id == 0 then
        return "Maya Chen II"
    elseif id == 1 then
        return "Elise Park"
    elseif id == 2 then
        return "Alex Morgan"
    elseif id == 3 then
        return "Miles Bennett"
    endif
    return "Ethan Cole"
endfunction

function NS_Equity takes integer n, integer bucket returns integer
    local string row
    if n == 3 then
        set row = "027043041054037037037037037037037037037037037037031051045063060066066076073081072082059059059059077077077077070076071071078085082082077077077077037058048048092096092092093093093093088088088088090090089091090090090090090090090090090090090090093095094096094094094094094094094094094094094094097097097097093095094094097099098098097097097097100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100"
    elseif n == 4 then
        set row = "018034028042030030030030030030030030030030030030023045032051057063061067073080075081052052052052028056034056068072066078078084073084072072072072030053036056092093092096091093094092082082082082089082089089082074081086080079076083088088088088088093088094084096082093080089086084089089089089093093093093090092090090095098096096093093093093081083087087100100100100100100100100098098098098100100100100100100100100100100100100100100100100"
    else
        set row = "011025017017017017017017017017017017004004004004015037026026052059054054072079078078009009009009026056043043066070067067078084083083021030022022020048034034091093091091088092091091016024018018091091091091086087086086086087087087042041043043086092089089084094087087084090089089038035039039090090090090090091090090096097097097044044046046052073071071100100099099097100098098046059063063100100099099099099098098097097097097075084085085"
    endif
    return S2I(SubString(row,bucket*3,bucket*3+3))
endfunction

function NS_Preflop takes integer first, integer second returns integer
    local integer a = ModuloInteger(first,13)+2
    local integer b = ModuloInteger(second,13)+2
    local integer value = (a+b-10)*100/24
    if a == b then
        return 48+(a-2)*43/10
    endif
    if first/13 == second/13 then
        set value = value+7
    endif
    if IAbsBJ(a-b) == 1 then
        set value = value+4
    endif
    if a == 14 or b == 14 then
        set value = value+4
    endif
    return IMinBJ(96,value)
endfunction

function NS_Postflop takes integer p, integer n returns integer
    local integer base = p*9
    local integer first = HousePK_Cards[base+2]
    local integer second = HousePK_Cards[base+3]
    local integer a = ModuloInteger(first,13)+2
    local integer b = ModuloInteger(second,13)+2
    local integer top = 0
    local integer matched = 0
    local integer pairGroup = 0
    local integer suitA = 1
    local integer suitB = 1
    local integer i = 1
    local integer j
    local integer card
    local integer r
    local integer boardIn
    local integer allInWindow
    local integer draw = 0
    local integer high = 0
    local integer score = HousePK_Score(p,1,n)
    loop
        exitwhen i > 14
        set NS_BoardRank[i] = false
        set i = i+1
    endloop
    if first/13 == second/13 then
        set suitA = 2
        set suitB = 2
    endif
    set i = 0
    loop
        exitwhen i >= n
        set card = HousePK_Cards[base+4+i]
        set r = ModuloInteger(card,13)+2
        set top = IMaxBJ(top,r)
        set NS_BoardRank[r] = true
        if card/13 == first/13 then
            set suitA = suitA+1
        endif
        if card/13 == second/13 then
            set suitB = suitB+1
        endif
        set i = i+1
    endloop
    if a == b or NS_BoardRank[a] then
        set matched = a
    endif
    if NS_BoardRank[b] then
        set matched = IMaxBJ(matched,b)
    endif
    if matched >= top then
        set pairGroup = 2
    elseif matched > 0 then
        set pairGroup = 1
    endif
    if n == 5 then
        if score == PK_Score5(HousePK_Cards[base+4],HousePK_Cards[base+5],HousePK_Cards[base+6],HousePK_Cards[base+7],HousePK_Cards[base+8]) then
            set pairGroup = 3
        endif
    elseif suitA == 4 or suitB == 4 then
        set draw = 1
    else
        set i = 1
        loop
            exitwhen i > 10 or draw == 1
            set j = i
            set boardIn = 0
            set allInWindow = 0
            loop
                exitwhen j >= i+5
                set r = j
                if j == 1 then
                    set r = 14
                endif
                if NS_BoardRank[r] then
                    set boardIn = boardIn+1
                    set allInWindow = allInWindow+1
                elseif a == r or b == r then
                    set allInWindow = allInWindow+1
                endif
                set j = j+1
            endloop
            if allInWindow == 4 and boardIn < 4 then
                set draw = 1
            endif
            set i = i+1
        endloop
    endif
    if IMaxBJ(a,b) >= 12 then
        set high = 1
    endif
    return NS_Equity(n,(score/759375)*16+pairGroup*4+draw*2+high)
endfunction

function NS_Move takes integer p, integer due, integer pot, integer blind, integer roll returns integer
    local integer id = NS_Dealt[p]
    local integer n = HousePK_BoardCount(p)
    local integer price = 100*due/IMaxBJ(1,pot+due)
    local integer value
    local integer pressure
    local integer defend
    local integer caution = 0
    local integer first = HousePK_Cards[p*9+2]
    local integer second = HousePK_Cards[p*9+3]
    if n == 0 then
        set value = NS_Preflop(first,second)
        if HousePK_Dealer[p] == 1 then
            set value = value+5
        endif
        set pressure = IMinBJ(88,IMaxBJ(0,(value-25)*2))
        set defend = 19+price/2
        if due > blind then
            set pressure = IMaxBJ(0,value-53)
            set defend = 25+price/2+IMinBJ(28,2*due/blind)
        endif
    else
        set value = NS_Postflop(p,n)
        set defend = price+6
        // A large bet represents a stronger range than a random pair of cards.
        if due > 0 then
            set defend = defend+price/3
        endif
        set pressure = IMinBJ(91,IMaxBJ(3,(value-39)*2))
        if due > 0 then
            set pressure = IMaxBJ(2,(value-56)*2)
        endif
    endif
    if id == 0 then
        // Maya flats more, including with some hands strong enough to reraise.
        set pressure = pressure-9
        set defend = defend-3
    elseif id == 1 then
        // Elise gives up marginal bluff catchers, particularly on the river.
        set caution = 3
        if n == 5 then
            set caution = 9
        endif
        set defend = defend+caution
    elseif id == 2 then
        // Alex pushes early edges and removes some speculative river bluffs.
        if n < 4 then
            set pressure = pressure+8
        elseif n == 5 and value < 50 then
            set pressure = 0
        endif
    elseif id == 3 then
        // Miles checks some big hands and rarely fires an empty bluff.
        if value >= 65 then
            set pressure = pressure-16
        elseif value < 45 then
            set pressure = 1
        endif
        set defend = defend-2
    else
        // Ethan's easier heads-up adaptation opens wide and overdefends small bets.
        if n == 0 then
            set pressure = pressure+17
            set defend = defend-13
        elseif price <= 28 then
            set defend = defend-10
        endif
    endif
    if due > 0 and value < defend and roll >= IMaxBJ(0,18-3*(defend-value)) then
        return 0
    endif
    if roll < pressure then
        return 2
    endif
    return 1
endfunction
