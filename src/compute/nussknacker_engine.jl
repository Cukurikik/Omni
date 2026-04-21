# ===========================================================================
# OMNI COMPUTE LAYER — NUSSKNACKER REAL-TIME STREAM RULES ENGINE
# ===========================================================================
# Source Paradigm : TouK/nussknacker
# Domain Layer   : Compute (SIMD vector ops, numerical computing, HPC)
# Language        : Julia
# Function        : Real-time event stream processing with typed scenario
#                   definitions, filter/split/aggregate nodes, CEP window
#                   evaluation, and typed expression language — all compiled
#                   for HPC throughput
# ===========================================================================

module OmniNussknacker

using Dates

export ScenarioNode, FilterNode, SplitNode, AggregateNode, SinkNode
export Scenario, EventRecord, EvaluationContext
export evaluate_scenario, aggregate_window

# ---- Event Record ----------------------------------------------------------

"""
    EventRecord

A single event entering the stream processing engine.
Fields map to common event schemas (timestamp, type, payload key-values).
"""
struct EventRecord
    id::String
    event_type::String
    timestamp::DateTime
    payload::Dict{String, Any}
end

# ---- Scenario Graph Nodes --------------------------------------------------

"""Abstract base for all scenario graph nodes."""
abstract type ScenarioNode end

"""Filter node: evaluates a predicate on each event."""
struct FilterNode <: ScenarioNode
    id::String
    expression::Function   # (EventRecord) -> Bool
    next_true::Union{ScenarioNode, Nothing}
    next_false::Union{ScenarioNode, Nothing}
end

"""Split node: routes events to multiple branches."""
struct SplitNode <: ScenarioNode
    id::String
    branches::Vector{Pair{String, ScenarioNode}}  # label => next node
end

"""Aggregate node: collects events within a time window and computes stats."""
mutable struct AggregateNode <: ScenarioNode
    id::String
    window_seconds::Int
    field_name::String        # which payload field to aggregate
    agg_fn::Symbol            # :sum, :mean, :count, :max, :min
    buffer::Vector{Float64}
    window_start::DateTime
    next::Union{ScenarioNode, Nothing}
end

"""Sink node: outputs the processed event (terminal)."""
struct SinkNode <: ScenarioNode
    id::String
    output_topic::String
end

# ---- Evaluation Context ----------------------------------------------------

"""Holds mutable state during scenario execution."""
mutable struct EvaluationContext
    events_processed::Int
    events_filtered::Int
    events_output::Int
    errors::Vector{String}
end

EvaluationContext() = EvaluationContext(0, 0, 0, String[])

# ---- Core Engine -----------------------------------------------------------

"""
    evaluate_node(node, event, ctx)

Recursively evaluate a single node in the scenario graph.
Returns the final output event (or nothing if filtered).
"""
function evaluate_node(node::FilterNode, event::EventRecord, ctx::EvaluationContext)
    ctx.events_processed += 1
    try
        if node.expression(event)
            if !isnothing(node.next_true)
                return evaluate_node(node.next_true, event, ctx)
            end
            return event
        else
            ctx.events_filtered += 1
            if !isnothing(node.next_false)
                return evaluate_node(node.next_false, event, ctx)
            end
            return nothing
        end
    catch e
        push!(ctx.errors, "Filter $(node.id): $(sprint(showerror, e))")
        return nothing
    end
end

function evaluate_node(node::AggregateNode, event::EventRecord, ctx::EvaluationContext)
    ctx.events_processed += 1
    val = get(event.payload, node.field_name, 0.0)
    push!(node.buffer, Float64(val))

    elapsed = Dates.value(event.timestamp - node.window_start) / 1000  # seconds
    if elapsed >= node.window_seconds
        result = aggregate_window(node)
        node.buffer = Float64[]
        node.window_start = event.timestamp
        println("[NUSSKNACKER-OMNI-JL] Window flush: $(node.agg_fn)($(node.field_name)) = $result")

        if !isnothing(node.next)
            return evaluate_node(node.next, event, ctx)
        end
        return event
    end

    return nothing  # window still open
end

function evaluate_node(node::SinkNode, event::EventRecord, ctx::EvaluationContext)
    ctx.events_output += 1
    println("[NUSSKNACKER-OMNI-JL] Sink '$(node.output_topic)': event $(event.id)")
    return event
end

"""Compute the aggregate statistic for a completed window."""
function aggregate_window(node::AggregateNode)::Float64
    buf = node.buffer
    isempty(buf) && return 0.0
    if node.agg_fn == :sum
        return sum(buf)
    elseif node.agg_fn == :mean
        return sum(buf) / length(buf)
    elseif node.agg_fn == :count
        return Float64(length(buf))
    elseif node.agg_fn == :max
        return maximum(buf)
    elseif node.agg_fn == :min
        return minimum(buf)
    else
        return 0.0
    end
end

"""
    evaluate_scenario(root_node, events)

Run an entire stream of events through a scenario graph.
Returns the EvaluationContext with execution statistics.
"""
function evaluate_scenario(root::ScenarioNode, events::Vector{EventRecord})
    ctx = EvaluationContext()
    println("[NUSSKNACKER-OMNI-JL] Evaluating scenario with $(length(events)) event(s)...")

    for event in events
        evaluate_node(root, event, ctx)
    end

    println("[NUSSKNACKER-OMNI-JL] Scenario complete:")
    println("  Processed : $(ctx.events_processed)")
    println("  Filtered  : $(ctx.events_filtered)")
    println("  Output    : $(ctx.events_output)")
    println("  Errors    : $(length(ctx.errors))")

    return ctx
end

end # module

# ---- FFI Test Harness (commented) ------------------------------------------
# using .OmniNussknacker
# sink = SinkNode("sink-1", "alerts-topic")
# filter = FilterNode("filter-temp", e -> get(e.payload, "temperature", 0) > 80.0, sink, nothing)
# events = [
#     EventRecord("e1", "sensor", now(), Dict("temperature" => 75.0)),
#     EventRecord("e2", "sensor", now(), Dict("temperature" => 95.0)),
#     EventRecord("e3", "sensor", now(), Dict("temperature" => 42.0)),
# ]
# evaluate_scenario(filter, events)
