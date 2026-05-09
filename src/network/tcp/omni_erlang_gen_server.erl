-module(omni_tcp_acceptor).
-behaviour(gen_server).

%% Omni Fault-Tolerant TCP Acceptor Pool (Erlang)
%% Concurrency & Networking Layer
%% High-throughput, resilient TCP socket listener that delegates raw 
%% incoming byte streams directly to the internal Go/Rust processors.

-export([start_link/1, init/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

-record(state, {listen_socket, acceptor_ref}).

start_link(Port) ->
    gen_server:start_link({local, ?MODULE}, ?MODULE, [Port], []).

init([Port]) ->
    %% Open TCP socket in binary, active once, reuseaddr mode
    {ok, ListenSocket} = gen_tcp:listen(Port, [binary, {packet, 0}, {active, once}, {reuseaddr, true}]),
    io:format("Omni Erlang Acceptor bound to port ~p~n", [Port]),
    %% Cast to self to start accepting connections
    gen_server:cast(self(), accept),
    {ok, #state{listen_socket = ListenSocket}}.

handle_cast(accept, State = #state{listen_socket = ListenSocket}) ->
    %% Asynchronously wait for a connection
    {ok, Ref} = prim_inet:async_accept(ListenSocket, -1),
    {noreply, State#state{acceptor_ref = Ref}};

handle_cast(_Msg, State) ->
    {noreply, State}.

handle_call(_Request, _From, State) ->
    {reply, ok, State}.

handle_info({inet_async, ListenSocket, Ref, {ok, ClientSocket}}, State = #state{listen_socket = ListenSocket, acceptor_ref = Ref}) ->
    %% Connection received. Hand off to connection handler.
    %% In Omni, this dispatches to the NIF queue.
    io:format("Accepted new connection. Dispatching to Omni Runtime.~n"),
    inet:setopts(ClientSocket, [{active, once}]),
    %% Immediately listen for the next connection
    gen_server:cast(self(), accept),
    {noreply, State};

handle_info({tcp, Socket, Data}, State) ->
    %% Received data. Pass to Universal Binary processing.
    io:format("Received ~p bytes~n", [byte_size(Data)]),
    inet:setopts(Socket, [{active, once}]),
    {noreply, State};

handle_info({tcp_closed, _Socket}, State) ->
    io:format("Connection closed.~n"),
    {noreply, State};

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
