// Omni AutoAgents Data Transform (PowerQuery M)
// Business/Analysis Layer: Strict ETL logic for agent trajectory data.

let
    OmniTransform = (SourceData as table) as table =>
    let
        // Ensure strictly bounded structure
        FilteredRows = Table.SelectRows(SourceData, each [AgentState] <> null and [AgentState] <> ""),
        AddedIndex = Table.AddIndexColumn(FilteredRows, "OmniStepID", 1, 1, Int64.Type),
        CleanedData = Table.TransformColumnTypes(AddedIndex,{{"AgentState", type text}})
    in
        CleanedData
in
    OmniTransform
