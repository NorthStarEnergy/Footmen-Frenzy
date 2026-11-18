    // BEGIN ITEMS CATALOG GLOBALS
    hashtable IC_Data = InitHashtable()
    integer IC_Count = 0
    integer IC_Sections = 0
    integer IC_LoadIndex = 1
    integer IC_Selected = 0
    integer IC_Tab = 0
    integer IC_Page = 0
    integer IC_TextPage = 0
    integer IC_TextPages = 1
    integer IC_HistoryCount = 0
    integer array IC_History
    integer array IC_Id
    integer array IC_Gold
    integer array IC_Lumber
    integer array IC_Total
    integer array IC_Recipe
    integer array IC_Result
    integer array IC_Ingredients
    integer array IC_IngredientCount
    integer array IC_Spell
    integer array IC_SectionStart
    integer array IC_SectionCount
    integer array IC_Stock
    integer array IC_TileItem
    string array IC_Name
    string array IC_Icon
    string array IC_Description
    string array IC_Stats
    string array IC_Location
    string array IC_Note
    string array IC_SectionName
    string array IC_SectionIcon
    string IC_Query = ""
    boolean IC_Ready = false
    framehandle IC_Header
    framehandle IC_Search
    framehandle IC_SearchButton
    framehandle IC_Back
    framehandle IC_Close
    framehandle IC_Previous
    framehandle IC_Next
    framehandle IC_Footer
    framehandle IC_Browse
    framehandle IC_Detail
    framehandle IC_DetailIcon
    framehandle IC_DetailName
    framehandle IC_DetailCost
    framehandle IC_Body
    framehandle array IC_TabButton
    framehandle array IC_SectionArt
    framehandle array IC_SectionTitle
    framehandle array IC_Tile
    framehandle array IC_TileArt
    framehandle array IC_TileLabel
    framehandle array IC_Link
    framehandle array IC_LinkArt
    framehandle array IC_LinkLabel
    integer array IC_LinkItem
    timer IC_LoadTimer = null
    // END ITEMS CATALOG GLOBALS
