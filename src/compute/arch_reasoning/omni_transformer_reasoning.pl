%% @omni-layer Compute | @omni-lang Prolog | @omni-batch 18 | @omni-semester 16
%% @omni-description Prolog transformer architecture reasoning engine:
%% model selection logic, architecture validation, and constraint reasoning.

:- module(omni_transformer_reasoning, [
    select_model/3,
    validate_architecture/2,
    optimal_config/3,
    compute_flops/4
]).

%% Model database: model(Id, Type, DModel, NHeads, NLayers, ParamsM)
model(tempo, timeseries, 768, 12, 6, 125).
model(hiformer, segmentation, 256, 8, 4, 85).
model(video_cls, video, 768, 12, 12, 300).
model(bert_ner, ner, 768, 12, 12, 110).
model(long_text, classification, 768, 12, 12, 110).

%% Task-model compatibility
compatible(timeseries, tempo).
compatible(segmentation, hiformer).
compatible(video, video_cls).
compatible(ner, bert_ner).
compatible(classification, long_text).
compatible(classification, bert_ner).

%% Select best model for task with constraints
select_model(Task, MaxParamsM, ModelId) :-
    compatible(Task, ModelId),
    model(ModelId, _, _, _, _, Params),
    Params =< MaxParamsM.

%% Validate transformer architecture
validate_architecture(DModel, NHeads) :-
    DModel > 0,
    NHeads > 0,
    DModel mod NHeads =:= 0,
    HeadDim is DModel // NHeads,
    HeadDim >= 16,
    HeadDim =< 256.

%% Compute FLOPs for attention
compute_flops(SeqLen, DModel, NHeads, FLOPs) :-
    HeadDim is DModel // NHeads,
    QKFlops is 2 * SeqLen * SeqLen * HeadDim * NHeads,
    AVFlops is 2 * SeqLen * SeqLen * HeadDim * NHeads,
    FFNFlops is 2 * SeqLen * DModel * 4 * DModel,
    FLOPs is QKFlops + AVFlops + FFNFlops.

%% Find optimal config given constraints
optimal_config(MaxFlops, SeqLen, config(DModel, NHeads, NLayers)) :-
    member(DModel, [256, 512, 768, 1024]),
    member(NHeads, [4, 8, 12, 16]),
    member(NLayers, [2, 4, 6, 8, 12]),
    validate_architecture(DModel, NHeads),
    compute_flops(SeqLen, DModel, NHeads, LayerFlops),
    TotalFlops is LayerFlops * NLayers,
    TotalFlops =< MaxFlops.

%% Reasoning about attention patterns
attention_type(full, SeqLen) :- SeqLen =< 2048.
attention_type(linear, SeqLen) :- SeqLen > 2048, SeqLen =< 16384.
attention_type(sparse, SeqLen) :- SeqLen > 16384.

recommend_attention(SeqLen, Type, Reason) :-
    attention_type(Type, SeqLen),
    (Type = full -> Reason = 'Standard O(n^2) attention suitable for short sequences' ;
     Type = linear -> Reason = 'Linear attention recommended for medium sequences' ;
     Type = sparse -> Reason = 'Sparse/local attention required for very long sequences').
