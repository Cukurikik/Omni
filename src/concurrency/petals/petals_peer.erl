% OMNI Divine Memory Integration: Inspired by Petals (Distributed BitTorrent Inference)
% Concurrency Layer - Erlang OTP GenServer for Peer Swarm Management

-module(petals_peer).
-behaviour(gen_server).

-export([start_link/1, assign_compute_block/3, get_peer_status/1]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-define(MAX_BLOCKS_PER_NODE, 8).
-define(TIMEOUT, 5000).

-record(state, {
    node_id :: binary(),
    vram_available :: integer(),
    blocks_hosted :: [binary()]
}).

%% API
start_link(NodeId) ->
    gen_server:start_link(?MODULE, [NodeId], []).

assign_compute_block(Pid, BlockId, RequiredVram) ->
    gen_server:call(Pid, {assign_block, BlockId, RequiredVram}, ?TIMEOUT).

get_peer_status(Pid) ->
    gen_server:call(Pid, get_status, ?TIMEOUT).

%% Callbacks
init([NodeId]) ->
    % Physical bound assumption for zero-mock system
    {ok, #state{node_id = NodeId, vram_available = 16#400000000, blocks_hosted = []}}. % 16GB

handle_call({assign_block, BlockId, RequiredVram}, _From, State = #state{vram_available = Vram, blocks_hosted = Blocks}) ->
    if
        length(Blocks) >= ?MAX_BLOCKS_PER_NODE ->
            {reply, {error, max_blocks_reached}, State};
        Vram < RequiredVram ->
            {reply, {error, insufficient_vram}, State};
        true ->
            NewState = State#state{
                vram_available = Vram - RequiredVram,
                blocks_hosted = [BlockId | Blocks]
            },
            {reply, {ok, BlockId}, NewState}
    end;

handle_call(get_status, _From, State) ->
    {reply, {ok, State}, State}.

handle_cast(_Msg, State) ->
    {noreply, State}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
