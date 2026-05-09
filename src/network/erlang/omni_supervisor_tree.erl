%% OMNI Network — Erlang Supervision Tree
%% Fault-tolerant architecture for the OMNI cluster nodes

-module(omni_supervisor_tree).
-behaviour(supervisor).

-export([start_link/0, init/1]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    %% Supervisor specifications
    SupFlags = #{strategy => one_for_one,
                 intensity => 10,
                 period => 60},

    %% Child specifications
    InferenceNode = #{id => omni_inference_worker,
                      start => {omni_inference_worker, start_link, []},
                      restart => permanent,
                      shutdown => 5000,
                      type => worker,
                      modules => [omni_inference_worker]},

    TelemetryNode = #{id => omni_telemetry_reporter,
                      start => {omni_telemetry_reporter, start_link, []},
                      restart => transient,
                      shutdown => 2000,
                      type => worker,
                      modules => [omni_telemetry_reporter]},

    %% If a worker crashes, Erlang supervisor automatically restarts it
    {ok, {SupFlags, [InferenceNode, TelemetryNode]}}.
