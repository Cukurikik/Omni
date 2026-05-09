-module(omni_tcp_acceptor).
-behaviour(gen_server).

-export([start_link/1, init/1, handle_call/3, handle_cast/2, handle_info/2]).

-record(state, {lsock}).

start_link(Port) ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [Port], []).

init([Port]) ->
    {ok, LSock} = gen_tcp:listen(Port, [{active, once}, {packet, line}, {reuseaddr, true}]),
    error_logger:info_msg("OMNI Erlang TCP Acceptor listening on ~p~n", [Port]),
    spawn_link(fun() -> accept(LSock) end),
    {ok, #state{lsock = LSock}}.

accept(LSock) ->
    {ok, CSock} = gen_tcp:accept(LSock),
    spawn_link(fun() -> accept(LSock) end),
    handle_client(CSock).

handle_client(CSock) ->
    receive
        {tcp, CSock, Data} ->
            gen_tcp:send(CSock, ["OMNI ACK: ", Data]),
            inet:setopts(CSock, [{active, once}]),
            handle_client(CSock);
        {tcp_closed, CSock} ->
            ok
    end.

handle_call(_Req, _From, State) -> {reply, ok, State}.
handle_cast(_Msg, State) -> {noreply, State}.
handle_info(_Info, State) -> {noreply, State}.
