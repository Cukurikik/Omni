module Omni.Optimization.ToolRetrieval

// Omni Tool Retrieval Opt (F#)
// Functional optimization for tool recall scoring calculations.

type ToolScore = { ToolName: string; RecallK: float }

type OmniResult<'T, 'E> = 
    | Ok of 'T
    | Err of 'E

let evaluateRecall (relevantTools: string list) (retrievedTools: string list) : OmniResult<float, string> =
    if List.isEmpty relevantTools then
        Err "Relevant tools list cannot be empty"
    else
        let matches = 
            retrievedTools 
            |> List.filter (fun t -> List.contains t relevantTools)
            |> List.length
        
        let recall = float matches / float (List.length relevantTools)
        Ok recall

let optimizeScores (scores: ToolScore list) : ToolScore list =
    scores 
    |> List.sortByDescending (fun s -> s.RecallK)
