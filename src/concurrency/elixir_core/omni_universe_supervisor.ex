defmodule Omni.Concurrency.UniverseSupervisor do
  @moduledoc """
  OMNI Framework - Universe Supervisor
  The ultimate top-level supervisor for the entire BEAM concurrency tree.
  Ensures the ecosystem remains fault-tolerant and alive permanently.
  """
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {Omni.Concurrency.MaestStreamWorker, []},
      {Omni.Concurrency.ZkRollupSequencer, []},
      {Omni.Concurrency.EasyLMJobSupervisor, []}
      # Additional polyglot worker bridges would be supervised here
    ]

    # OneForOne ensures independent recovery of nodes
    Supervisor.init(children, strategy: :one_for_one, max_restarts: 100, max_seconds: 1)
  end
end
