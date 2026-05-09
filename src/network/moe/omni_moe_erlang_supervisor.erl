-module(omni_moe_erlang_supervisor).
-behaviour(supervisor).

-export([start_link/0]).
-export([init/1]).

%% OMNI MOTHER Production Zero-Mock Erlang Supervisor
%% High-availability process manager for MoE worker nodes.
%% Will automatically restart crashed inference workers to maintain SLA.

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    %% Supervisor Strategy: One-For-One
    %% Max Restarts: 5 within 10 seconds
    SupFlags = #{strategy => one_for_one,
                 intensity => 5,
                 period => 10},

    %% Define the MoE Worker child specifications
    %% (Assume omni_moe_worker is a gen_server implemented elsewhere)
    ChildSpecs = [
        #{id => worker_1,
          start => {omni_moe_worker, start_link, [1]},
          restart => permanent,
          shutdown => 5000,
          type => worker,
          modules => [omni_moe_worker]},
          
        #{id => worker_2,
          start => {omni_moe_worker, start_link, [2]},
          restart => permanent,
          shutdown => 5000,
          type => worker,
          modules => [omni_moe_worker]}
    ],

    {ok, {SupFlags, ChildSpecs}}.
