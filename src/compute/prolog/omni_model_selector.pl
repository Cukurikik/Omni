% OMNI Compute Layer — Prolog Reasoning Engine for Model Selection
% Logic-based model recommendation and constraint satisfaction.

:- module(omni_model_selector, [
    select_model/3,
    best_model_for_task/2,
    model_fits_constraints/2,
    explain_selection/2
]).

% Model knowledge base
% model(Name, Architecture, Parameters, ContextLen, Tasks, Latency_ms, Accuracy)
model(omni_tiny, causal_lm, 125000000, 2048, [text_gen, chat], 10, 0.82).
model(omni_small, causal_lm, 350000000, 4096, [text_gen, chat, code], 25, 0.87).
model(omni_base, causal_lm, 1300000000, 4096, [text_gen, chat, code, reasoning], 50, 0.91).
model(omni_7b, causal_lm, 7000000000, 8192, [text_gen, chat, code, reasoning, math], 100, 0.94).
model(omni_13b, causal_lm, 13000000000, 8192, [text_gen, chat, code, reasoning, math, analysis], 200, 0.96).
model(omni_vit_base, vision_transformer, 86000000, 0, [image_class, object_detect], 15, 0.89).
model(omni_bert_base, encoder, 110000000, 512, [classification, ner, sentiment], 8, 0.90).
model(omni_t5_base, encoder_decoder, 220000000, 512, [translation, summarization, qa], 30, 0.88).

% Hardware constraints
% gpu(Name, VRAM_MB, FLOPS_TFLOPS)
gpu(a100, 80000, 312).
gpu(a10, 24000, 125).
gpu(t4, 16000, 65).
gpu(cpu_only, 0, 1).

% Select model given task and constraints
select_model(Task, Constraints, SelectedModel) :-
    model(SelectedModel, _, _, _, Tasks, _, _),
    member(Task, Tasks),
    model_fits_constraints(SelectedModel, Constraints).

% Check if model fits within constraints
model_fits_constraints(ModelName, Constraints) :-
    model(ModelName, _, Params, _, _, Latency, _),
    member(max_params(MaxParams), Constraints),
    Params =< MaxParams,
    member(max_latency(MaxLatency), Constraints),
    Latency =< MaxLatency.

model_fits_constraints(ModelName, Constraints) :-
    model(ModelName, _, Params, _, _, Latency, _),
    \+ member(max_params(_), Constraints),
    \+ member(max_latency(_), Constraints).

% Find best model for a given task (by accuracy)
best_model_for_task(Task, BestModel) :-
    findall(Acc-Model, (
        model(Model, _, _, _, Tasks, _, Acc),
        member(Task, Tasks)
    ), Models),
    sort(0, @>=, Models, [_-BestModel|_]).

% GPU compatibility check
model_fits_gpu(ModelName, GPUName) :-
    model(ModelName, _, Params, _, _, _, _),
    gpu(GPUName, VRAM, _),
    RequiredVRAM is Params * 2 / 1000000,  % ~2 bytes per param in FP16
    RequiredVRAM =< VRAM.

% Explain why a model was selected
explain_selection(ModelName, Explanation) :-
    model(ModelName, Arch, Params, CtxLen, Tasks, Latency, Accuracy),
    format(atom(Explanation),
        "Selected ~w: ~w architecture, ~w params, ~w context, ~wms latency, ~w accuracy. Supports: ~w",
        [ModelName, Arch, Params, CtxLen, Latency, Accuracy, Tasks]).

% Rule: Recommend model for production deployment
production_ready(ModelName) :-
    model(ModelName, _, _, _, _, _, Accuracy),
    Accuracy >= 0.90.

% Rule: Cost-optimized selection
cost_optimal(Task, Model) :-
    findall(Params-M, (
        model(M, _, Params, _, Tasks, _, Acc),
        member(Task, Tasks),
        Acc >= 0.85
    ), Models),
    sort(0, @=<, Models, [_-Model|_]).
