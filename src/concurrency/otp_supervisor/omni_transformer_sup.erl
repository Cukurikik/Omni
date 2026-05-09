%% @omni-layer Concurrency | @omni-lang Erlang | @omni-batch 18 | @omni-semester 16
%% @omni-description Erlang OTP supervisor for transformer inference workers
%% with automatic restart, circuit breaker, and telemetry.

-module(omni_transformer_sup).
-behaviour(supervisor).

-export([start_link/0, init/1, start_worker/2, stop_worker/1, get_workers/0]).

start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

init([]) ->
    SupFlags = #{
        strategy => one_for_one,
        intensity => 10,
        period => 60
    },
    Children = [
        #{
            id => omni_inference_dispatcher,
            start => {omni_inference_dispatcher, start_link, []},
            restart => permanent,
            shutdown => 5000,
            type => worker
        },
        #{
            id => omni_model_registry,
            start => {omni_model_registry, start_link, []},
            restart => permanent,
            shutdown => 5000,
            type => worker
        },
        #{
            id => omni_metrics_collector,
            start => {omni_metrics_collector, start_link, []},
            restart => permanent,
            shutdown => 5000,
            type => worker
        }
    ],
    {ok, {SupFlags, Children}}.

start_worker(ModelId, Config) ->
    ChildSpec = #{
        id => {omni_inference_worker, ModelId},
        start => {omni_inference_worker, start_link, [ModelId, Config]},
        restart => transient,
        shutdown => 10000,
        type => worker
    },
    supervisor:start_child(?MODULE, ChildSpec).

stop_worker(ModelId) ->
    supervisor:terminate_child(?MODULE, {omni_inference_worker, ModelId}),
    supervisor:delete_child(?MODULE, {omni_inference_worker, ModelId}).

get_workers() ->
    Children = supervisor:which_children(?MODULE),
    [{Id, Pid, Type, Modules} || {Id, Pid, Type, Modules} <- Children, is_pid(Pid)].
