integer OP_Phase = 0
    integer OP_Hand = 0
    integer OP_Button = -1
    integer OP_Turn = -1
    integer OP_Street = 0
    integer OP_Bet = 0
    integer OP_MinRaise = 10
    integer OP_Pot = 0
    integer OP_Clock = 8
    integer OP_ScoreCursor = 0
    integer OP_Seats = 0
    integer OP_Rest = -1
    boolean OP_Revealed = false
    boolean array OP_Dealt
    boolean array OP_Live
    boolean array OP_Leaving
    integer array OP_Faced
    integer array OP_Score
    integer array OP_Award
    integer array OP_Page
    integer array OP_Board
    framehandle array OP_PageButton
    timer OP_ScoreTimer = null
    string OP_Note = "Take a seat. The first hand starts when two players buy in."
    integer array BJ_Page
    integer BJ_ShoeSize = 104
