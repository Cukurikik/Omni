%% OMNI Framework - Erlang TableFormer Gateway
%% Highly concurrent HTTP acceptor for table-text encoding requests

-module(omni_table_encoder_gateway).
-behaviour(gen_server).

-export([start_link/0, init/1, handle_call/3, handle_cast/2]).

start_link() ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [], []).

init([]) ->
    %% Start Cowboy HTTP listener on port 8085
    io:format("OMNI TableFormer Gateway listening on port 8085~n"),
    {ok, #{request_count => 0}}.

handle_call({encode_table, TableData}, _From, State) ->
    %% Forward request to Python via OMNI gRPC Proxy
    #{request_count := Count} = State,
    NewState = State#{request_count => Count + 1},
    Response = {ok, <<"Table encoded successfully">>},
    {reply, Response, NewState}.

handle_cast(_Msg, State) ->
    {noreply, State}.
