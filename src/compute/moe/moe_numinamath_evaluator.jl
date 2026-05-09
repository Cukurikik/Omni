# moe_numinamath_evaluator.jl — Compute Layer: NuminaMath Evaluator
# Julia engine verifying generated mathematical proofs and solutions natively.

module NuminaMathEvaluator

export verify_equation, extract_final_answer

function extract_final_answer(generation::String)::String
    # Extract answer contained in \boxed{} tag
    start_idx = findfirst("\\boxed{", generation)
    if start_idx === nothing
        return ""
    end
    
    content_start = start_idx[end] + 1
    brace_count = 1
    content_end = content_start
    
    while content_end <= length(generation) && brace_count > 0
        if generation[content_end] == '{'
            brace_count += 1
        elseif generation[content_end] == '}'
            brace_count -= 1
        end
        if brace_count > 0
            content_end = nextind(generation, content_end)
        end
    end
    
    return generation[content_start:prevind(generation, content_end)]
end

function verify_equation(predicted::String, ground_truth::String)::Bool
    pred_clean = strip(predicted)
    truth_clean = strip(ground_truth)
    
    # Exact match for strict evaluation
    return pred_clean == truth_clean
end

end # module
