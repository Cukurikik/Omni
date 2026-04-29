# Omni Rephrase-and-Respond Evaluator (Julia)
# Ref: uclaml/Rephrase-and-Respond
module OmniRARJulia
function improvement_ratio(original_acc::Float64, rar_acc::Float64)
    delta = rar_acc - original_acc
    relative = delta / max(original_acc, 0.01)
    return (delta=round(delta, digits=4), relative=round(relative, digits=4))
end
function batch_accuracy(predictions::Vector{String}, answers::Vector{String})
    correct = sum(lowercase(strip(p)) == lowercase(strip(a)) for (p, a) in zip(predictions, answers))
    return correct / max(length(answers), 1)
end
end
