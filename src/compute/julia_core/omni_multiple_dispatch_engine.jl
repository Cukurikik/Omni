# ===========================================================================
# OMNI MULTIPLE DISPATCH ENGINE (SEMESTER 3 — BATCH 38.6)
# ===========================================================================
# Absorbed From  : Julia's built-in multiple dispatch + MethodTable
# Logic Inherited: Julia / Compute Layer (Multi-Method Dispatch System)
# ===========================================================================
#
# By studying Julia's dispatch system, Mother learned:
#   1. Methods dispatch on ALL argument types, not just the first
#   2. Type hierarchies enable specialization and fallback
#   3. Parametric types (Array{T}) enable generic specialization
#   4. Multiple dispatch eliminates visitor pattern and type switches
#   5. Method ambiguity detection prevents runtime errors

module OmniMultipleDispatchEngine

export MultiDispatcher, defmethod, invoke, methods_for, diagnostics

"""
    MethodSignature

Represents the type signature of a registered method.
"""
struct MethodSignature
    types::Tuple{Vararg{Type}}
    priority::Int
end

"""
    RegisteredMethod

A method implementation with its signature and metadata.
"""
struct RegisteredMethod
    signature::MethodSignature
    func::Function
    name::String
    doc::String
    call_count::Ref{Int}
end

"""
    MultiDispatcher

A custom multiple dispatch table that selects methods based on
all argument types. Demonstrates Julia's core dispatch mechanism.
"""
mutable struct MultiDispatcher
    name::String
    methods::Vector{RegisteredMethod}
    total_dispatches::Int
    total_ambiguities::Int
    total_fallbacks::Int
    cache::Dict{UInt64, RegisteredMethod}  # Dispatch cache

    function MultiDispatcher(name::String)
        new(name, RegisteredMethod[], 0, 0, 0, Dict{UInt64, RegisteredMethod}())
    end
end

"""
    type_distance(actual::Type, expected::Type) -> Int

Calculate the distance in the type hierarchy between actual and expected.
Returns -1 if actual is not a subtype of expected.
"""
function type_distance(actual::Type, expected::Type)::Int
    if actual === expected
        return 0
    end
    if !(actual <: expected)
        return -1
    end

    # Walk up the type hierarchy
    dist = 0
    current = actual
    while current !== expected && current !== Any
        current = supertype(current)
        dist += 1
        if current === expected
            return dist
        end
    end

    return current === expected ? dist : -1
end

"""
    match_score(args, signature) -> Int

Calculate how well the argument types match a method signature.
Returns -1 for no match, 0 for exact match, higher for looser match.
"""
function match_score(args::Tuple, sig::MethodSignature)::Int
    if length(args) != length(sig.types)
        return -1
    end

    total_distance = 0
    for (actual, expected) in zip(map(typeof, args), sig.types)
        d = type_distance(actual, expected)
        if d < 0
            return -1  # No match
        end
        total_distance += d
    end

    return total_distance
end

"""
    defmethod(dispatcher, types, func; name="", doc="", priority=0)

Register a method implementation for the given argument types.
"""
function defmethod(
    dispatcher::MultiDispatcher,
    types::Tuple{Vararg{Type}},
    func::Function;
    name::String = "",
    doc::String = "",
    priority::Int = 0
)
    sig = MethodSignature(types, priority)
    method = RegisteredMethod(sig, func, name, doc, Ref(0))
    push!(dispatcher.methods, method)

    # Invalidate dispatch cache
    empty!(dispatcher.cache)

    return dispatcher
end

"""
    invoke(dispatcher, args...) -> Any

Dispatch to the best-matching method for the given arguments.
Uses most-specific-type-wins rule (smallest total type distance).
"""
function invoke(dispatcher::MultiDispatcher, args...)
    dispatcher.total_dispatches += 1

    # Check cache first
    cache_key = hash(map(typeof, args))
    if haskey(dispatcher.cache, cache_key)
        method = dispatcher.cache[cache_key]
        method.call_count[] += 1
        return method.func(args...)
    end

    # Find all matching methods
    candidates = Tuple{Int, Int, RegisteredMethod}[]  # (score, priority, method)

    for method in dispatcher.methods
        score = match_score(args, method.signature)
        if score >= 0
            push!(candidates, (score, method.signature.priority, method))
        end
    end

    if isempty(candidates)
        types_str = join(map(string ∘ typeof, args), ", ")
        error("No method found for $(dispatcher.name)($(types_str))")
    end

    # Sort by score (ascending = more specific first), then by priority (descending)
    sort!(candidates, by = c -> (c[1], -c[2]))

    # Check for ambiguity (multiple methods with same best score)
    if length(candidates) > 1 && candidates[1][1] == candidates[2][1] &&
       candidates[1][2] == candidates[2][2]
        dispatcher.total_ambiguities += 1
    end

    best = candidates[1][3]
    best.call_count[] += 1

    # Cache the result
    dispatcher.cache[cache_key] = best

    return best.func(args...)
end

"""
    methods_for(dispatcher, types...) -> Vector{RegisteredMethod}

List all methods that match the given types.
"""
function methods_for(dispatcher::MultiDispatcher, types::Type...)
    matching = RegisteredMethod[]
    for method in dispatcher.methods
        if length(method.signature.types) == length(types)
            all_match = all(
                types[i] <: method.signature.types[i]
                for i in 1:length(types)
            )
            if all_match
                push!(matching, method)
            end
        end
    end
    return matching
end

"""
    diagnostics(dispatcher) -> Dict{String, Any}

Return engine diagnostics.
"""
function diagnostics(dispatcher::MultiDispatcher)
    method_info = [
        Dict(
            "name" => m.name,
            "types" => string(m.signature.types),
            "priority" => m.signature.priority,
            "calls" => m.call_count[]
        )
        for m in dispatcher.methods
    ]

    return Dict{String, Any}(
        "engine" => "OmniMultipleDispatchEngine",
        "layer" => "Julia Compute",
        "dispatcher_name" => dispatcher.name,
        "total_methods" => length(dispatcher.methods),
        "total_dispatches" => dispatcher.total_dispatches,
        "total_ambiguities" => dispatcher.total_ambiguities,
        "cache_size" => length(dispatcher.cache),
        "methods" => method_info,
        "learned_logic" => [
            "multiple-dispatch-all-args",
            "type-hierarchy-distance",
            "most-specific-wins-rule",
            "parametric-type-matching",
            "dispatch-cache-hash-key",
            "ambiguity-detection",
            "priority-based-tiebreak",
            "subtype-operator-check"
        ]
    )
end

end # module
