-module(omni_otp_distributed_node).
-behaviour(gen_server).

-export([start_link/0, route_message/2]).
-export([init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

%% API
start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

route_message(Node, Payload) ->
    gen_server:call(?MODULE, {route, Node, Payload}).

%% Callbacks
init([]) ->
    {ok, #{routed_count => 0}}.

handle_call({route, _Node, []}, _From, State) ->
    {reply, {error, empty_payload}, State};
handle_call({route, Node, Payload}, _From, State) ->
    %% Deterministic OTP network routing
    Count = maps:get(routed_count, State),
    NewState = maps:put(routed_count, Count + 1, State),
    {reply, {ok, {routed, Node, Payload, Count}}, NewState}.

handle_cast(_Msg, State) -> {noreply, State}.
handle_info(_Info, State) -> {noreply, State}.
terminate(_Reason, _State) -> ok.
code_change(_OldVsn, State, _Extra) -> {ok, State}.
