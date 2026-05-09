defmodule Omni.Supervisor do
  use Supervisor

  @moduledoc """
  Omni Elixir Supervisor (Concurrency Layer)
  Supervision tree for managing distributed Transformer inference workers.
  Provides fault tolerance, automatic restarts, and actor-model scalability.
  """

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      # Dynamic supervisor for spawning inference actors on demand
      {DynamicSupervisor, name: Omni.InferenceWorkerSupervisor, strategy: :one_for_one},
      
      # Global registry for routing requests to specific workers
      {Registry, keys: :unique, name: Omni.WorkerRegistry},
      
      # Cluster heartbeat monitor
      {Omni.ClusterMonitor, []}
    ]

    # one_for_one: if a child crashes, only that child is restarted.
    # maximum 10 restarts in 5 seconds before giving up.
    Supervisor.init(children, strategy: :one_for_one, max_restarts: 10, max_seconds: 5)
  end

  @doc """
  Spawns a new Transformer inference worker dynamically.
  """
  def spawn_inference_worker(model_id, gpu_id) do
    child_spec = {Omni.InferenceWorker, {model_id, gpu_id}}
    DynamicSupervisor.start_child(Omni.InferenceWorkerSupervisor, child_spec)
  end
end
