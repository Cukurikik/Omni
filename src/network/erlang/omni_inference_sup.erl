%% OMNI Network — Erlang OTP Supervisor for Inference Workers
%% Fault-tolerant worker pool with health monitoring.

-module(omni_inference_sup).
-behaviour(supervisor).

-export([start_link/1, init/1, start_worker/1, get_stats/0]).

-define(MAX_RESTART, 10).
-define(MAX_TIME, 60).

start_link(Config) ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, Config).

init(Config) ->
    NumWorkers = maps:get(num_workers, Config, 4),
    ModelId = maps:get(model_id, Config, <<"omni-7b">>),
    Endpoint = maps:get(endpoint, Config, <<"http://localhost:9090">>),

    WorkerSpecs = [
        #{
            id => list_to_atom("inference_worker_" ++ integer_to_list(N)),
            start => {omni_inference_worker, start_link, [
                #{id => N, model_id => ModelId, endpoint => Endpoint}
            ]},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [omni_inference_worker]
        }
        || N <- lists:seq(1, NumWorkers)
    ],

    HealthMonitor = #{
        id => omni_health_monitor,
        start => {omni_health_monitor, start_link, [Config]},
        restart => permanent,
        shutdown => 5000,
        type => worker,
        modules => [omni_health_monitor]
    },

    MetricsCollector = #{
        id => omni_metrics,
        start => {omni_metrics_collector, start_link, [Config]},
        restart => permanent,
        shutdown => 5000,
        type => worker,
        modules => [omni_metrics_collector]
    },

    AllSpecs = [HealthMonitor, MetricsCollector | WorkerSpecs],

    SupFlags = #{
        strategy => one_for_one,
        intensity => ?MAX_RESTART,
        period => ?MAX_TIME
    },

    {ok, {SupFlags, AllSpecs}}.

start_worker(Config) ->
    Id = maps:get(id, Config),
    ChildSpec = #{
        id => list_to_atom("inference_worker_" ++ integer_to_list(Id)),
        start => {omni_inference_worker, start_link, [Config]},
        restart => permanent,
        shutdown => 5000,
        type => worker,
        modules => [omni_inference_worker]
    },
    supervisor:start_child(?MODULE, ChildSpec).

get_stats() ->
    Children = supervisor:which_children(?MODULE),
    Active = length([C || {_, Pid, _, _} = C <- Children, is_pid(Pid)]),
    Total = length(Children),
    #{
        active_workers => Active,
        total_children => Total,
        restart_intensity => ?MAX_RESTART
    }.
