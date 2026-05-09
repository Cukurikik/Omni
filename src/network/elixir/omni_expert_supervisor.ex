defmodule OmniMoE.ExpertSupervisor do
  use Supervisor

  # OMNI MOTHER: Expert Node Supervisor
  # Monitors Expert tracking nodes and PiKV nodes, restarting on failure

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {OmniMoE.PiKVCacheNode, name: :pikv_cache},
      {OmniMoE.T2MIRTracker, []}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end
