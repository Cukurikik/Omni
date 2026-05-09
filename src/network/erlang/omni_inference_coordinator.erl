%% OMNI Concurrency Layer — Erlang Distributed Inference Coordinator
%% Coordinates transformer inference across Erlang cluster nodes.

-module(omni_inference_coordinator).
-behaviour(gen_server).

-export([start_link/1, infer/2, get_stats/0, add_node/1, remove_node/1]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2]).

-record(state, {
    nodes = [] :: [node()],
    current_idx = 0 :: non_neg_integer(),
    total_requests = 0 :: non_neg_integer(),
    total_latency_us = 0 :: non_neg_integer(),
    error_count = 0 :: non_neg_integer()
}).

-record(infer_request, {
    id :: binary(),
    text :: binary(),
    max_tokens = 256 :: pos_integer(),
    temperature = 0.7 :: float()
}).

%% API
start_link(Opts) ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, Opts, []).

infer(Text, Opts) ->
    Request = #infer_request{
        id = generate_request_id(),
        text = Text,
        max_tokens = proplists:get_value(max_tokens, Opts, 256),
        temperature = proplists:get_value(temperature, Opts, 0.7)
    },
    gen_server:call(?MODULE, {infer, Request}, 30000).

get_stats() ->
    gen_server:call(?MODULE, get_stats).

add_node(Node) ->
    gen_server:cast(?MODULE, {add_node, Node}).

remove_node(Node) ->
    gen_server:cast(?MODULE, {remove_node, Node}).

%% Callbacks
init(Opts) ->
    Nodes = proplists:get_value(nodes, Opts, [node()]),
    net_kernel:monitor_nodes(true),
    error_logger:info_msg("OMNI Inference Coordinator started with ~p nodes~n", [length(Nodes)]),
    {ok, #state{nodes = Nodes}}.

handle_call({infer, Request}, _From, #state{nodes = []} = State) ->
    {reply, {error, no_nodes_available}, State#state{error_count = State#state.error_count + 1}};

handle_call({infer, Request}, _From, State) ->
    StartTime = erlang:monotonic_time(microsecond),
    Node = select_node(State),

    Result = try
        rpc:call(Node, omni_inference_worker, process, [Request], 25000)
    catch
        _:Reason ->
            error_logger:warning_msg("Inference failed on ~p: ~p~n", [Node, Reason]),
            {error, {inference_failed, Reason}}
    end,

    Latency = erlang:monotonic_time(microsecond) - StartTime,
    NewState = State#state{
        current_idx = (State#state.current_idx + 1) rem length(State#state.nodes),
        total_requests = State#state.total_requests + 1,
        total_latency_us = State#state.total_latency_us + Latency
    },
    {reply, Result, NewState};

handle_call(get_stats, _From, State) ->
    AvgLatency = case State#state.total_requests of
        0 -> 0.0;
        N -> State#state.total_latency_us / N / 1000.0  % Convert to ms
    end,
    Stats = #{
        nodes => State#state.nodes,
        total_requests => State#state.total_requests,
        avg_latency_ms => AvgLatency,
        error_count => State#state.error_count
    },
    {reply, Stats, State}.

handle_cast({add_node, Node}, State) ->
    case lists:member(Node, State#state.nodes) of
        true -> {noreply, State};
        false ->
            error_logger:info_msg("Added node: ~p~n", [Node]),
            {noreply, State#state{nodes = [Node | State#state.nodes]}}
    end;

handle_cast({remove_node, Node}, State) ->
    {noreply, State#state{nodes = lists:delete(Node, State#state.nodes)}}.

handle_info({nodedown, Node}, State) ->
    error_logger:warning_msg("Node down: ~p~n", [Node]),
    {noreply, State#state{nodes = lists:delete(Node, State#state.nodes)}};

handle_info({nodeup, Node}, State) ->
    error_logger:info_msg("Node up: ~p~n", [Node]),
    {noreply, State};

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

%% Internal
select_node(#state{nodes = Nodes, current_idx = Idx}) ->
    lists:nth((Idx rem length(Nodes)) + 1, Nodes).

generate_request_id() ->
    Bytes = crypto:strong_rand_bytes(16),
    binary:encode_hex(Bytes).
