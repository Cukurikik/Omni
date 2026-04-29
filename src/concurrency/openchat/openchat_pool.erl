%% OMNI Divine Memory Integration: Inspired by openchat
%% Concurrency Layer - Erlang pool supervisor bounding WebSocket chat connections

-module(openchat_pool).
-behaviour(supervisor).

-export([start_link/0, init/1]).

-define(MAX_CHAT_CONNECTIONS, 50000). %% Physical bound on socket file descriptors

-record(omni_error, {code :: integer(), message :: string()}).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    %% Zero-mock constraint logic
    %% Ensure supervisor terminates if connection restart intensity implies systemic failure
    SupFlags = #{
        strategy => one_for_one,
        intensity => 10,
        period => 5
    },

    %% Single child spec representing the listener pool
    ChildSpecs = [
        #{
            id => chat_listener,
            start => {chat_listener, start_link, [?MAX_CHAT_CONNECTIONS]},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [chat_listener]
        }
    ],

    {ok, {SupFlags, ChildSpecs}}.
